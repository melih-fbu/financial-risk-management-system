from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers, metals, reports, transactions
from app.core.config import APP_NAME
from app.core.database import Base, engine
from app.models.audit import AuditLog
from app.models.customer import Customer
from app.models.metals import MetalPrice, Portfolio, SimulationResult
from app.models.transaction import Transaction

app = FastAPI(
    title=APP_NAME,
    description="Altın ve Gümüş Portföy Risk Analiz Sistemi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metals.router, prefix="/metals", tags=["Metals"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Financial Risk Management API çalışıyor!",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "OK"}
