from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer

router = APIRouter()


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None


@router.get("")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.id.asc()).all()


@router.post("")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi ile kayıtlı müşteri zaten var.")

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return {"message": "Müşteri eklendi", "data": new_customer}


@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    return customer
