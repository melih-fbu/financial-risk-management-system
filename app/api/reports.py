from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.forecast import MetalForecaster
from app.models.customer import Customer
from app.models.metals import MetalPrice
from app.models.transaction import Transaction
from app.risk.calculator import RiskCalculator
import pandas as pd

router = APIRouter()


class CompareMetalsRequest(BaseModel):
    initial_amount: float
    start_date: date
    end_date: date


class MonteCarloRequest(BaseModel):
    metal_type: str
    days: int = 30
    simulations: int = 1000


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


@router.get("/metal-analysis/{metal_type}")
def get_metal_analysis(metal_type: str, db: Session = Depends(get_db)):
    all_prices = (
        db.query(MetalPrice)
        .filter(MetalPrice.metal_type == metal_type)
        .order_by(MetalPrice.date.asc())
        .all()
    )
    price_series = pd.Series(
        [
            p.price_try if p.price_try else p.price_usd
            for p in all_prices
            if (p.price_try if p.price_try else p.price_usd) is not None
        ]
    )
    if len(price_series) < 2:
        raise HTTPException(status_code=400, detail="Analiz için yetersiz fiyat verisi var.")

    return {
        "metal_type": metal_type,
        "historical_var_95": RiskCalculator.calculate_historical_var(price_series, 0.95),
        "sharpe_ratio": RiskCalculator.calculate_sharpe_ratio(price_series),
        "max_drawdown": RiskCalculator.calculate_max_drawdown(price_series),
        "volatility": RiskCalculator.calculate_volatility(price_series),
        "data_points": int(len(price_series)),
    }


@router.post("/monte-carlo")
def run_monte_carlo(request: MonteCarloRequest, db: Session = Depends(get_db)):
    if request.days <= 0:
        raise HTTPException(status_code=400, detail="days değeri 0'dan büyük olmalıdır.")
    if request.simulations <= 0:
        raise HTTPException(status_code=400, detail="simulations değeri 0'dan büyük olmalıdır.")

    price_series = RiskCalculator._get_price_series(db, request.metal_type)
    if len(price_series) < 2:
        raise HTTPException(status_code=400, detail="Monte Carlo için yetersiz fiyat verisi var.")

    simulation_result = RiskCalculator.monte_carlo_simulation(
        price_series,
        days=request.days,
        simulations=request.simulations,
    )

    return {
        "metal_type": request.metal_type,
        "days": request.days,
        "simulations": request.simulations,
        **simulation_result,
    }


@router.get("/predict/{metal_type}")
def predict_metal_price(
    metal_type: str,
    days_ahead: int = Query(default=7, ge=1, le=60),
    db: Session = Depends(get_db),
):
    all_prices = (
        db.query(MetalPrice)
        .filter(MetalPrice.metal_type == metal_type)
        .order_by(MetalPrice.date.asc())
        .all()
    )
    price_series = pd.Series(
        [
            p.price_try if p.price_try else p.price_usd
            for p in all_prices
            if (p.price_try if p.price_try else p.price_usd) is not None
        ]
    )
    if len(price_series) < 6:
        raise HTTPException(status_code=400, detail="Tahmin için en az 6 fiyat verisi gereklidir.")

    prediction = MetalForecaster.predict_future_prices(price_series, days_ahead=days_ahead)
    return {
        "metal_type": metal_type,
        **prediction,
    }


@router.get("/signal/{metal_type}")
def get_signal_report(metal_type: str, db: Session = Depends(get_db)):
    price_series = RiskCalculator._get_price_series(db, metal_type)
    if len(price_series) < 20:
        raise HTTPException(status_code=400, detail="Sinyal üretmek için en az 20 fiyat verisi gereklidir.")

    return {
        "metal_type": metal_type,
        **MetalForecaster.calculate_risk_score(price_series),
        **MetalForecaster.classify_volatility(price_series),
        **MetalForecaster.generate_signal(price_series),
    }
