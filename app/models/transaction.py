from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    metal_type = Column(String, nullable=False)
    amount_try = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # BUY / SELL
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
