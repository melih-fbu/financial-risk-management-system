from fastapi import FastAPI
from app.core.config import APP_NAME
from app.api import metals

app = FastAPI(
    title=APP_NAME,
    description="Altın ve Gümüş Portföy Risk Analiz Sistemi",
    version="1.0.0"
)

app.include_router(metals.router, prefix="/metals", tags=["Metals"])

@app.get("/")
def root():
    return {
        "message": "Financial Risk Management API çalışıyor!",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "OK"}