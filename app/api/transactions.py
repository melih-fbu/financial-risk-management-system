from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction

router = APIRouter()


class TransactionCreate(BaseModel):
    customer_id: int
    metal_type: str
    amount_try: float
    transaction_type: str
    date: date


@router.get("")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc()).all()


@router.post("")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == transaction.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="İşlem için müşteri bulunamadı")

    transaction_type = transaction.transaction_type.upper()
    if transaction_type not in {"BUY", "SELL"}:
        raise HTTPException(status_code=400, detail="transaction_type sadece BUY veya SELL olabilir.")

    new_transaction = Transaction(
        customer_id=transaction.customer_id,
        metal_type=transaction.metal_type,
        amount_try=transaction.amount_try,
        transaction_type=transaction_type,
        date=transaction.date,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return {"message": "İşlem eklendi", "data": new_transaction}


@router.get("/customer/{customer_id}")
def get_transactions_by_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    return (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .all()
    )
