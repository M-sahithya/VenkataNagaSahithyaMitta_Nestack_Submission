import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    database = TestingSessionLocal()

    try:
        yield database
    finally:
        database.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_a(client):
    client.post("/register", json={
        "username": "usera",
        "password": "Password@123"
    })

    response = client.post("/login", json={
        "username": "usera",
        "password": "Password@123"
    })

    return response.json()["access_token"]


@pytest.fixture
def user_b(client):
    client.post("/register", json={
        "username": "userb",
        "password": "Password@123"
    })

    response = client.post("/login", json={
        "username": "userb",
        "password": "Password@123"
    })

    return response.json()["access_token"]