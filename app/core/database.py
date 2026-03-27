from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import DATABASE_URL

# PostgreSQL'e bağlantı motoru oluştur
engine = create_engine(DATABASE_URL)

# Her istek için bir oturum (session) açar
SessionLocal = sessionmaker(bind=engine)

# Tüm tablolarımız bu sınıftan türeyecek
class Base(DeclarativeBase):
    pass

# API'de kullanmak için veritabanı oturumu açan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()