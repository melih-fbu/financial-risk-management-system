from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.risk.calculator import RiskCalculator

router = APIRouter()


class CompareMetalsRequest(BaseModel):
    initial_amount: float
    start_date: date
    end_date: date


@router.get("/customer-summary")
def get_customer_summary(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Customer.id.label("customer_id"),
            Customer.name.label("customer_name"),
            Customer.email.label("email"),
            func.coalesce(func.sum(Transaction.amount_try), 0).label("total_investment_try"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .outerjoin(Transaction, Transaction.customer_id == Customer.id)
        .group_by(Customer.id, Customer.name, Customer.email)
        .order_by(Customer.id.asc())
        .all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "email": row.email,
            "total_investment_try": float(row.total_investment_try or 0),
            "transaction_count": int(row.transaction_count or 0),
        }
        for row in rows
    ]


@router.get("/metal-performance")
def get_metal_performance(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Transaction.metal_type.label("metal_type"),
            func.coalesce(func.sum(Transaction.amount_try), 0).label("total_volume_try"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .group_by(Transaction.metal_type)
        .order_by(Transaction.metal_type.asc())
        .all()
    )

    return [
        {
            "metal_type": row.metal_type,
            "total_volume_try": float(row.total_volume_try or 0),
            "transaction_count": int(row.transaction_count or 0),
        }
        for row in rows
    ]


@router.get("/monthly-volume")
def get_monthly_volume(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.date_trunc("month", Transaction.date).label("month"),
            func.coalesce(func.sum(Transaction.amount_try), 0).label("total_volume_try"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .group_by(func.date_trunc("month", Transaction.date))
        .order_by(func.date_trunc("month", Transaction.date).asc())
        .all()
    )

    return [
        {
            "month": row.month.date().isoformat() if row.month else None,
            "total_volume_try": float(row.total_volume_try or 0),
            "transaction_count": int(row.transaction_count or 0),
        }
        for row in rows
    ]


@router.post("/compare-metals")
def compare_metals(request: CompareMetalsRequest, db: Session = Depends(get_db)):
    result = RiskCalculator.compare_metals(
        db=db,
        initial_amount=request.initial_amount,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/risk-summary/{customer_id}")
def get_risk_summary(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    summary = RiskCalculator.calculate_portfolio_risk(db, customer_id)
    summary["customer_name"] = customer.name
    summary["email"] = customer.email
    return summary
