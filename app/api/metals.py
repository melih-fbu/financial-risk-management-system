from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# --- Veri şemaları ---
# Kullanıcıdan ne geleceğini tanımlıyoruz
class MetalPriceCreate(BaseModel):
    metal_type: str   # "XAU" veya "XAG"
    price_usd: float  # Dolar fiyatı
    price_try: float  # TL fiyatı
    date: date        # Hangi gün

class PortfolioCreate(BaseModel):
    user_name: str    # Kimin portföyü
    metal_type: str   # Hangi maden
    amount_try: float # Ne kadar TL yatırıldı
    start_date: date  # Ne zaman

# --- Endpointler ---
# Şimdilik veritabanı olmadan test verisiyle çalışıyoruz

@router.get("/prices")
def get_prices():
    # Gerçek veri gelince burası DB'den okuyacak
    return [
        {"metal_type": "XAU", "price_usd": 3100.0, "price_try": 99200.0, "date": "2025-03-01"},
        {"metal_type": "XAG", "price_usd": 34.5,   "price_try": 1104.0,  "date": "2025-03-01"},
    ]

@router.post("/prices")
def add_price(price: MetalPriceCreate):
    # Gerçek veri gelince burası DB'ye kaydedecek
    return {"message": "Fiyat eklendi", "data": price}

@router.post("/portfolio")
def create_portfolio(portfolio: PortfolioCreate):
    return {"message": "Portföy oluşturuldu", "data": portfolio}