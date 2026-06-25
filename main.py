from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import crud
from app.config import get_settings
from app.database import init_db
from app.dependencies import get_db
from app.schemas import ProductCreate, ProductOut, ProductPage, ProductUpdate


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/categories", response_model=list[str])
def categories(db: Session = Depends(get_db)) -> list[str]:
    return crud.get_categories(db)


@app.get("/products", response_model=ProductPage)
def products(
    category: str | None = None,
    limit: int = Query(default=settings.default_page_size, ge=1, le=settings.max_page_size),
    cursor: str | None = None,
    db: Session = Depends(get_db),
) -> ProductPage:
    items, next_cursor = crud.list_products(db, category=category, limit=limit, cursor=cursor)
    return ProductPage(items=items, next_cursor=next_cursor, limit=limit, category=category)


@app.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductOut:
    return crud.create_product(db, payload)


@app.patch("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)) -> ProductOut:
    product = crud.update_product(db, product_id, payload)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
