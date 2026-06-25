# Product Browser Backend

This project is a take-home backend task for browsing around **200,000 products**. It supports newest-first product listing, category filtering, and fast cursor-based pagination.

## What I Built

- FastAPI backend to browse products
- Product table with:
  - `id`
  - `name`
  - `category`
  - `price`
  - `created_at`
  - `updated_at`
- Seed script to generate 200,000 products
- Cursor-based pagination (keyset pagination)
- Category filtering
- Simple browser UI (bonus)
- Automated tests

---

## Tech Stack

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **PostgreSQL**
- **Pydantic**
- **Pytest**
- **Uvicorn**

---

## Why This Approach

The main requirement was fast and stable pagination for large product datasets.

I used **keyset pagination** instead of offset pagination.

### Offset pagination:

```text
page=1000&limit=50
```

This becomes slower because the database skips many rows.

### Keyset pagination:

```text
/products?limit=50&cursor=...
```

This is faster because it continues from the last seen record.

Products are sorted by:

```text
created_at DESC, id DESC
```

This ensures newest products come first.

The cursor stores:

```text
last_created_at
last_id
snapshot_created_at
snapshot_id
```

This prevents duplicates or missing products when new products are inserted while browsing.

---

## Project Structure

```text
app/main.py          FastAPI routes
app/models.py        Product database model
app/schemas.py       Request and response schemas
app/crud.py          Product logic
app/database.py      Database connection
app/config.py        App settings
app/utils.py         Cursor helpers
scripts/seed.py      Seed script
static/index.html    Simple UI
tests/               Automated tests
render.yaml          Render deployment config
Dockerfile           Docker deployment config
```

---

## API Endpoints

### Health Check

```http
GET /health
```

### List Products

```http
GET /products?limit=50&category=books&cursor=...
```

Returns newest products first.

### Categories

```http
GET /categories
```

Returns all categories.

### Create Product

```http
POST /products
```

### Update Product

```http
PATCH /products/{product_id}
```

---

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate sample data:

```bash
python scripts/seed.py --count 200 --reset
```

Generate full dataset:

```bash
python scripts/seed.py --count 200000 --reset
```

Run server:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Run Tests

```bash
pytest
```

---

## Database

Default:

```text
products.db
```

Production:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

Recommended:
- PostgreSQL
- Neon
- Supabase
- Render Postgres

---

## Deployment

Supports deployment on Render using:

- `render.yaml`
- `Dockerfile`

Set:

```text
DATABASE_URL
```

After deployment, run the seed script.

---

## Tests Covered

- Product creation
- Product listing
- Category filtering
- Cursor pagination
- Stable pagination when new products are inserted

---

## Future Improvements

- Alembic migrations
- Authentication
- Rate limiting
- Performance benchmarks
- Admin-only seed endpoint

---

## AI Usage Note

AI was used to help structure the FastAPI project, generate the initial implementation, and write tests. The final implementation was reviewed and verified manually.
