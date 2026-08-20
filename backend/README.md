# Voltana Backend

FastAPI backend for the Voltana EV route planner.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database URL and OpenRouteService API key

# Run migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed_db.py

# Start development server
uvicorn app.main:app --reload
```

## API Endpoints

### Vehicles
- `GET /vehicles` - List vehicles with pagination and filters
- `GET /vehicles/makes` - List all makes
- `GET /vehicles/{id}` - Get vehicle details
- `POST /vehicles` - Create vehicle
- `PATCH /vehicles/{id}` - Update vehicle
- `DELETE /vehicles/{id}` - Delete vehicle
- `POST /vehicles/{id}/efficiency-curve` - Add efficiency curve point
- `PUT /vehicles/{id}/range-confidence` - Set range confidence

### Chargers
- `GET /chargers/networks` - List charger networks
- `POST /chargers/networks` - Create network
- `GET /chargers` - List chargers with filters
- `GET /chargers/{id}` - Get charger details
- `POST /chargers` - Create charger
- `PATCH /chargers/{id}` - Update charger
- `DELETE /chargers/{id}` - Delete charger

### Trip Planning
- `POST /trip/plan` - Plan a trip with charging stops

### Health
- `GET /health` - Health check

## Project Structure

```
backend/
├── app/
│   ├── core/           # Config, database
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # FastAPI route handlers
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic (trip planner, routing)
│   └── main.py         # FastAPI app entry point
├── scripts/
│   └── seed_db.py      # Database seeding
├── alembic/            # Database migrations
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Running with Docker

```bash
docker build -t voltana-backend .
docker run -p 8000:8000 --env-file .env voltana-backend
```