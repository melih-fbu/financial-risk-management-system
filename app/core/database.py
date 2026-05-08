from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL tanımlı değil.")

# PostgreSQL bağlantı motoru
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Her istek için bir session açar
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
