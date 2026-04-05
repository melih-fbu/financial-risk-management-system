from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)  # Veritabanında şifreli saklanır
    phone = Column(String, nullable=True)   # Veritabanında şifreli saklanır
    created_at = Column(DateTime, default=func.now())
