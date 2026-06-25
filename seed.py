import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, init_db
from app.models import Product


CATEGORIES = ["books", "electronics", "fashion", "home", "sports", "toys", "beauty", "grocery"]
ADJECTIVES = ["Smart", "Fresh", "Classic", "Compact", "Premium", "Daily", "Urban", "Eco"]
NOUNS = ["Kit", "Pack", "Bottle", "Bag", "Lamp", "Shoes", "Watch", "Speaker", "Chair", "Notebook"]


def build_batch(start: int, size: int, base_time: datetime) -> list[dict]:
    rows = []
    for offset in range(size):
        number = start + offset
        created_at = base_time - timedelta(seconds=number)
        rows.append(
            {
                "id": str(uuid4()),
                "name": f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {number}",
                "category": CATEGORIES[number % len(CATEGORIES)],
                "price": round(random.uniform(5, 999), 2),
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    return rows


def seed(count: int, batch_size: int, reset: bool) -> None:
    init_db()
    base_time = datetime.now(timezone.utc)

    with SessionLocal() as db:
        if reset:
            db.execute(delete(Product))
            db.commit()

        inserted = 0
        while inserted < count:
            size = min(batch_size, count - inserted)
            db.bulk_insert_mappings(Product, build_batch(inserted, size, base_time))
            db.commit()
            inserted += size
            print(f"Inserted {inserted}/{count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed product data quickly using batched inserts.")
    parser.add_argument("--count", type=int, default=200_000)
    parser.add_argument("--batch-size", type=int, default=5_000)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    seed(count=args.count, batch_size=args.batch_size, reset=args.reset)


if __name__ == "__main__":
    main()
