from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal
from app.models.metals import MetalPrice


CSV_COLUMNS = ["symbol", "timeframe", "time", "open", "high", "low", "close", "volume"]


def import_csv(filepath, metal_type):
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV dosyası bulunamadı: {file_path}")

    df = pd.read_csv(file_path, header=None, names=CSV_COLUMNS)
    df["time"] = pd.to_datetime(df["time"], format="%Y.%m.%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["time", "close"]).copy()
    df["date"] = df["time"].dt.date
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])

    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    try:
        existing_dates = {
            row.date
            for row in db.query(MetalPrice.date).filter(MetalPrice.metal_type == metal_type).all()
        }
        seen_dates = set()

        for _, row in df.iterrows():
            record_date = row["date"]

            if record_date in existing_dates or record_date in seen_dates:
                skipped_count += 1
                continue

            db.add(
                MetalPrice(
                    metal_type=metal_type,
                    price_usd=float(row["close"]),
                    price_try=None,
                    date=record_date,
                )
            )
            seen_dates.add(record_date)
            inserted_count += 1

        db.commit()
        print(f"{metal_type}: {inserted_count} eklendi, {skipped_count} atlandı.")
    finally:
        db.close()


if __name__ == "__main__":
    gold_csv_path = r"C:\Users\PC\Downloads\GOLD_History.csv"
    silver_csv_path = r"C:\Users\PC\Downloads\SILVER_History.csv"

    import_csv(gold_csv_path, "XAU")
    import_csv(silver_csv_path, "XAG")
