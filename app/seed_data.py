from datetime import date, timedelta
import random

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.models.metals import MetalPrice


def generate_price_series(start_price: float, change_limit: float, generator: random.Random) -> float:
    daily_change = generator.uniform(-change_limit, change_limit)
    return round(start_price * (1 + daily_change), 2)


def main():
    load_dotenv()

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL .env dosyasında tanımlı olmalıdır.")

    engine = create_engine(DATABASE_URL)
    session_local = sessionmaker(bind=engine)
    db = session_local()

    start_date = date(2026, 1, 1)
    end_date = date(2026, 6, 30)
    generator = random.Random(42)

    current_xau_usd = 2000.0
    current_xau_try = 64000.0
    current_xag_usd = 23.0
    current_xag_try = 736.0

    inserted_count = 0

    try:
        current_date = start_date
        while current_date <= end_date:
            existing_records = {
                row.metal_type
                for row in db.query(MetalPrice.metal_type).filter(MetalPrice.date == current_date).all()
            }

            current_xau_usd = generate_price_series(current_xau_usd, 0.015, generator)
            current_xau_try = generate_price_series(current_xau_try, 0.015, generator)
            current_xag_usd = generate_price_series(current_xag_usd, 0.015, generator)
            current_xag_try = generate_price_series(current_xag_try, 0.015, generator)

            if "XAU" not in existing_records:
                db.add(
                    MetalPrice(
                        metal_type="XAU",
                        price_usd=current_xau_usd,
                        price_try=current_xau_try,
                        date=current_date,
                    )
                )
                inserted_count += 1

            if "XAG" not in existing_records:
                db.add(
                    MetalPrice(
                        metal_type="XAG",
                        price_usd=current_xag_usd,
                        price_try=current_xag_try,
                        date=current_date,
                    )
                )
                inserted_count += 1

            current_date += timedelta(days=1)

        db.commit()
        print(f"{inserted_count} kayıt eklendi.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
