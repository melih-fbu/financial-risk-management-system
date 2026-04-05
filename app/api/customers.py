from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.database import get_db
from app.core.security import decrypt_data, encrypt_data
from app.models.customer import Customer

router = APIRouter()


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None


def serialize_customer(customer: Customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "email": decrypt_data(customer.email),
        "phone": decrypt_data(customer.phone),
        "created_at": customer.created_at,
    }


@router.get("")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    serialized_customers = [serialize_customer(customer) for customer in customers]
    log_action(
        db,
        action="READ",
        entity_type="customer",
        entity_id=None,
        details={"count": len(serialized_customers), "operation": "list_customers"},
    )
    return serialized_customers


@router.post("")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing_customers = db.query(Customer).all()
    if any(decrypt_data(existing_customer.email) == customer.email for existing_customer in existing_customers):
        raise HTTPException(status_code=400, detail="Bu e-posta adresi ile kayıtlı müşteri zaten var.")

    new_customer = Customer(
        name=customer.name,
        email=encrypt_data(customer.email),
        phone=encrypt_data(customer.phone),
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    log_action(
        db,
        action="CREATE",
        entity_type="customer",
        entity_id=new_customer.id,
        details={"name": new_customer.name},
    )
    return {"message": "Müşteri eklendi", "data": serialize_customer(new_customer)}


@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    log_action(
        db,
        action="READ",
        entity_type="customer",
        entity_id=customer.id,
        details={"operation": "get_customer"},
    )
    return serialize_customer(customer)
