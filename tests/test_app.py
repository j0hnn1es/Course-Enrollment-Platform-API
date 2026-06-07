import importlib
import os
import sys

from fastapi.testclient import TestClient
from app.models.base import Base


def build_app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    for module_name in ["app.core.config", "app.core.database", "app.main"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    import app.core.database as database
    import app.main as main

    return main.app, database.engine


def test_health_endpoint(tmp_path):
    app, engine = build_app(tmp_path)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "operational",
            "engine": "FastAPI Uvicorn Execution Layer",
        }


def test_courses_endpoint_returns_list(tmp_path):
    app, engine = build_app(tmp_path)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        response = client.get("/courses")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json() == []
