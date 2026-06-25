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
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_and_list_products(client):
    response = client.post("/products", json={"name": "Phone", "category": "electronics", "price": 499.99})
    assert response.status_code == 201

    page = client.get("/products", params={"limit": 10}).json()
    assert page["items"][0]["name"] == "Phone"
    assert page["next_cursor"] is None


def test_category_filter(client):
    client.post("/products", json={"name": "Phone", "category": "electronics", "price": 499})
    client.post("/products", json={"name": "Book", "category": "books", "price": 19})

    page = client.get("/products", params={"category": "books"}).json()
    assert [item["category"] for item in page["items"]] == ["books"]
