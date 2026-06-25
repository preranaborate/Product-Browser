from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


Index("ix_products_created_id_desc", Product.created_at.desc(), Product.id.desc())
Index("ix_products_category_created_id_desc", Product.category, Product.created_at.desc(), Product.id.desc())
