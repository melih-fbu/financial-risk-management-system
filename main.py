from fastapi import FastAPI
from app.core.config import APP_NAME

# FastAPI uygulamasını başlat
app = FastAPI(
     title="Financial Risk Management System",
    description="Altın ve Gümüş Portföy Risk Analiz Sistemi",
    version="1.0.0"
)

# Ana sayfa - API çalışıyor mu diye kontrol
@app.get("/")
def root():
    return {
        "message": "Financial Risk Management API çalışıyor!",
        "version": "1.0.0"
    }

# Sağlık kontrolü - sistem ayakta mı?
@app.get("/health")
def health_check():
    return {"status": "OK"}