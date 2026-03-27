from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class MetalPrice(Base):
    __tablename__ = "metal_prices"

    id         = Column(Integer, primary_key=True, index=True)
    metal_type = Column(String, nullable=False)  # "XAU" altın, "XAG" gümüş
    price_usd  = Column(Float, nullable=False)   # O günkü fiyat (dolar)
    price_try  = Column(Float, nullable=True)    # O günkü fiyat (TL)
    date       = Column(Date, nullable=False)    # Hangi gün
    created_at = Column(DateTime, default=func.now())  # Sisteme ne zaman girildi

class Portfolio(Base):
    __tablename__ = "portfolios"

    id          = Column(Integer, primary_key=True, index=True)
    user_name   = Column(String, nullable=False)   # Kimin portföyü
    metal_type  = Column(String, nullable=False)   # Hangi maden
    amount_try  = Column(Float, nullable=False)    # Ne kadar yatırıldı (TL)
    start_date  = Column(Date, nullable=False)     # Ne zaman yatırıldı
    created_at  = Column(DateTime, default=func.now())

class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id              = Column(Integer, primary_key=True, index=True)
    user_name       = Column(String, nullable=False)
    metal_type      = Column(String, nullable=False)   # Hangi maden simüle edildi
    initial_amount  = Column(Float, nullable=False)    # Başlangıç yatırımı
    final_amount    = Column(Float, nullable=True)     # Bitiş değeri
    profit_loss     = Column(Float, nullable=True)     # Kar / zarar
    var_95          = Column(Float, nullable=True)     # %95 VaR değeri
    start_date      = Column(Date, nullable=False)
    end_date        = Column(Date, nullable=False)
    created_at      = Column(DateTime, default=func.now())