from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models import Product


@pytest.fixture()
def client_and_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    base = datetime.now(timezone.utc)
    products = [
        Product(
            id=f"product-{index:03d}",
            name=f"Product {index}",
            category="books" if index % 2 == 0 else "electronics",
            price=10 + index,
            created_at=base - timedelta(seconds=index),
            updated_at=base - timedelta(seconds=index),
        )
        for index in range(30)
    ]
    db.add_all(products)
    db.commit()

    def override_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app), db
    db.close()
    app.dependency_overrides.clear()


def test_cursor_pagination_does_not_duplicate_or_skip_when_new_rows_arrive(client_and_session):
    client, db = client_and_session

    first = client.get("/products", params={"limit": 10}).json()
    first_ids = [item["id"] for item in first["items"]]

    now = datetime.now(timezone.utc) + timedelta(minutes=1)
    db.add_all(
        [
            Product(
                id=f"new-{index}",
                name=f"New {index}",
                category="books",
                price=99,
                created_at=now + timedelta(seconds=index),
                updated_at=now + timedelta(seconds=index),
            )
            for index in range(5)
        ]
    )
    db.commit()

    second = client.get("/products", params={"limit": 10, "cursor": first["next_cursor"]}).json()
    third = client.get("/products", params={"limit": 10, "cursor": second["next_cursor"]}).json()

    seen = first_ids + [item["id"] for item in second["items"]] + [item["id"] for item in third["items"]]
    assert len(seen) == 30
    assert len(seen) == len(set(seen))
    assert all(not product_id.startswith("new-") for product_id in seen)


def test_category_cursor_pagination_is_stable(client_and_session):
    client, _ = client_and_session

    first = client.get("/products", params={"category": "books", "limit": 4}).json()
    second = client.get(
        "/products",
        params={"category": "books", "limit": 20, "cursor": first["next_cursor"]},
    ).json()

    items = first["items"] + second["items"]
    assert len(items) == 15
    assert {item["category"] for item in items} == {"books"}
    assert len({item["id"] for item in items}) == 15
