# Course Enrollment Platform API

A FastAPI-based backend for managing users, courses, and enrollments with SQLAlchemy models and Alembic migrations.

## Project structure

- `app/main.py` - FastAPI application entrypoint
- `app/routers/` - API route modules for auth, courses, and enrollments
- `app/models/` - SQLAlchemy ORM models and base metadata
- `app/schemas/` - Pydantic request/response schemas
- `app/core/` - configuration, database setup, and security utilities
- `tests/test_app.py` - lightweight runtime tests for the API
- `alembic/` - migration environment and configuration

## Requirements

- Python 3.14
- `requirements.txt` contains dependencies used by the project
- A PostgreSQL database is the default runtime database via `app/core/config.py`

## Setup

1. Create or activate your virtual environment.
2. Install dependencies:
   ```bash
   env/Scripts/python -m pip install -r requirements.txt
   ```
3. If you want to use PostgreSQL, update `DATABASE_URL` in `.env` or `app/core/config.py`.

## Running the app

Start the FastAPI service with Uvicorn:

```bash
env/Scripts/python -m uvicorn app.main:app --reload
```

Then visit the automatic API docs at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Testing

Run the test suite with:

```bash
env/Scripts/python -m pytest tests -q
```

The current tests use a temporary SQLite database file and verify the `/health` and `/courses` endpoints.

## Alembic migrations

- `alembic.ini` and `alembic/env.py` are configured to read the application database URL.
- Use Alembic to generate and apply migrations once your database is configured.

Example:

```bash
env/Scripts/python -m alembic revision --autogenerate -m "create schemas"
env/Scripts/python -m alembic upgrade head
```

## Notes

- The app currently creates database tables using `Base.metadata.create_all` during startup.
- Pydantic and FastAPI may emit deprecation warnings for class-based config and `@app.on_event("startup")`; these can be refactored later.
