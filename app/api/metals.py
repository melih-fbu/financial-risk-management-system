from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.metals import MetalPrice, Portfolio, SimulationResult
from app.risk.calculator import RiskCalculator
import pandas as pd

router = APIRouter()

# --- Veri şemaları ---
# Kullanıcıdan gelecek verinin şekli
class MetalPriceCreate(BaseModel):
    metal_type: str   # "XAU" veya "XAG"
    price_usd: float  # Dolar fiyatı
    price_try: float  # TL fiyatı
    date: date        # Hangi gün

class PortfolioCreate(BaseModel):
    user_name: str    # Kimin portföyü
    metal_type: str   # Hangi maden
    amount_try: float # Ne kadar TL
    start_date: date  # Ne zaman yatırıldı

class SimulationRequest(BaseModel):
    user_name: str
    metal_type: str
    amount_try: float
    start_date: date

# --- Endpointler ---

# Tüm fiyatları listele
@router.get("/prices")
def get_prices(db: Session = Depends(get_db)):
    # Veritabanından tüm fiyatları çek
    prices = db.query(MetalPrice).all()
    return prices

# Yeni fiyat ekle
@router.post("/prices")
def add_price(price: MetalPriceCreate, db: Session = Depends(get_db)):
    # Gelen veriyi veritabanına kaydet
    new_price = MetalPrice(
        metal_type=price.metal_type,
        price_usd=price.price_usd,
        price_try=price.price_try,
        date=price.date
    )
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return {"message": "Fiyat eklendi", "data": new_price}

# Portföy oluştur
@router.post("/portfolio")
def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    new_portfolio = Portfolio(
        user_name=portfolio.user_name,
        metal_type=portfolio.metal_type,
        amount_try=portfolio.amount_try,
        start_date=portfolio.start_date
    )
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    return {"message": "Portföy oluşturuldu", "data": new_portfolio}

# Belirli bir madenin fiyatlarını getir
@router.get("/prices/{metal_type}")
def get_prices_by_metal(metal_type: str, db: Session = Depends(get_db)):
    prices = db.query(MetalPrice).filter(MetalPrice.metal_type == metal_type).all()
    if not prices:
        raise HTTPException(status_code=404, detail="Fiyat bulunamadı")
    return prices

# Portföy Simülasyonu
@router.post("/simulate")
def simulate_portfolio(request: SimulationRequest, db: Session = Depends(get_db)):
    """
    Geçmiş bir tarihte yapılan yatırımın bugünkü değerini simüle eder.
    """
    result = RiskCalculator.simulate_portfolio(
        db, 
        request.user_name, 
        request.metal_type, 
        request.amount_try, 
        request.start_date
    )
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result

# Tarihsel VaR Hesaplama
@router.get("/var/{metal_type}")
def get_metal_var(metal_type: str, db: Session = Depends(get_db)):
    """
    Belirli bir maden için %95 güven aralığında Historical VaR hesaplar.
    """
    all_prices = db.query(MetalPrice).filter(
        MetalPrice.metal_type == metal_type
    ).order_by(MetalPrice.date.asc()).all()
    
    if not all_prices or len(all_prices) < 2:
        raise HTTPException(status_code=400, detail="VaR hesaplamak için yetersiz veri var (en az 2 gün gerekli).")
        
    price_series = pd.Series([p.price_try for p in all_prices if p.price_try is not None])
    var_95 = RiskCalculator.calculate_historical_var(price_series, 0.95)
    
    return {
        "metal_type": metal_type,
        "confidence_level": 0.95,
        "historical_var_95": var_95,
        "data_points": len(price_series)
    }