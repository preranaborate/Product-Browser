from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Product, utc_now
from app.schemas import ProductCreate, ProductUpdate
from app.utils import decode_cursor, encode_cursor


def _before_or_equal(created_at: datetime, product_id: str):
    return or_(Product.created_at < created_at, and_(Product.created_at == created_at, Product.id <= product_id))


def create_product(db: Session, data: ProductCreate) -> Product:
    now = utc_now()
    product = Product(
        name=data.name,
        category=data.category,
        price=data.price,
        created_at=now,
        updated_at=now,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: str, data: ProductUpdate) -> Product | None:
    product = db.get(Product, product_id)
    if product is None:
        return None
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    product.updated_at = utc_now()
    db.commit()
    db.refresh(product)
    return product


def get_categories(db: Session) -> list[str]:
    rows = db.execute(select(Product.category).distinct().order_by(Product.category)).scalars().all()
    return list(rows)


def list_products(
    db: Session,
    *,
    limit: int,
    category: str | None = None,
    cursor: str | None = None,
) -> tuple[list[Product], str | None]:
    filters = []
    snapshot_at: datetime | None = None
    snapshot_id: str | None = None

    if category:
        filters.append(Product.category == category)

    if cursor:
        cursor_created_at, cursor_id, snapshot_at, snapshot_id = decode_cursor(cursor)
        filters.append(_before_or_equal(snapshot_at, snapshot_id))
        filters.append(or_(Product.created_at < cursor_created_at, and_(Product.created_at == cursor_created_at, Product.id < cursor_id)))
    else:
        snapshot_query = select(Product.created_at, Product.id).order_by(Product.created_at.desc(), Product.id.desc()).limit(1)
        if category:
            snapshot_query = snapshot_query.where(Product.category == category)
        snapshot = db.execute(snapshot_query).first()
        if snapshot is None:
            return [], None
        snapshot_at, snapshot_id = snapshot
        filters.append(_before_or_equal(snapshot_at, snapshot_id))

    query = select(Product).order_by(Product.created_at.desc(), Product.id.desc()).limit(limit + 1)
    if filters:
        query = query.where(*filters)

    products = list(db.execute(query).scalars().all())
    page = products[:limit]
    has_more = len(products) > limit

    next_cursor = None
    if has_more and page:
        last = page[-1]
        next_cursor = encode_cursor(last.created_at, last.id, snapshot_at, snapshot_id)

    return page, next_cursor
