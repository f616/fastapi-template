# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, User, Inv
from app.auth import get_password_hash

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for get_db used in routers
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use pytest fixtures to set up the test database and client

@pytest.fixture(scope="module")
def test_db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # Drop the tables after tests complete
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    # Insert a sample user with hashed password and inventory items
    hashed_password = get_password_hash("testpassword")
    sample_user = User(username="testuser", hashed_password=hashed_password)
    test_db.add(sample_user)
    test_db.commit()

    inv_item1 = Inv(item_name="Widget", quantity=100)
    inv_item2 = Inv(item_name="Gadget", quantity=50)
    test_db.add_all([inv_item1, inv_item2])
    test_db.commit()

    # Override the get_db dependencies in both routers
    from app.routers.auth import get_db as auth_get_db
    from app.routers.inv import get_db as inv_get_db
    app.dependency_overrides[auth_get_db] = override_get_db
    app.dependency_overrides[inv_get_db] = override_get_db

    with TestClient(app) as client:
        yield client

def test_token(client):
    # Test the /token endpoint to obtain a JWT token
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_inv(client):
    # First, obtain a valid access token
    token_response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Now, access the secured /inv endpoint
    response = client.get("/inv", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # Optionally, verify the returned items
    item_names = [item["item_name"] for item in data]
    assert "Widget" in item_names
    assert "Gadget" in item_names
