import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app import models
import os


@pytest.fixture(scope="function")
def test_engine():
    """Create a new engine for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_api_key():
    """Return the test API key"""
    return "test-api-key-123456"


@pytest.fixture(scope="function")
def auth_headers(test_api_key):
    """Return authentication headers"""
    return {"X-API-Key": test_api_key}


@pytest.fixture(scope="function")
def sample_buildings(db_session):
    """Create sample buildings"""
    buildings = [
        models.Building(
            address="Test Address 1", latitude=55.751244, longitude=37.618423
        ),
        models.Building(
            address="Test Address 2", latitude=55.756244, longitude=37.625423
        ),
        models.Building(
            address="Test Address 3", latitude=59.934280, longitude=30.335099
        ),
    ]
    db_session.add_all(buildings)
    db_session.commit()
    for building in buildings:
        db_session.refresh(building)
    return buildings


@pytest.fixture(scope="function")
def sample_activities(db_session):
    """Create sample activities with tree structure"""
    # Level 1
    food = models.Activity(name="Food", level=1)
    cars = models.Activity(name="Cars", level=1)

    db_session.add_all([food, cars])
    db_session.commit()
    db_session.refresh(food)
    db_session.refresh(cars)

    # Level 2
    meat = models.Activity(name="Meat", parent_id=food.id, level=2)
    dairy = models.Activity(name="Dairy", parent_id=food.id, level=2)
    trucks = models.Activity(name="Trucks", parent_id=cars.id, level=2)
    passenger = models.Activity(name="Passenger", parent_id=cars.id, level=2)

    db_session.add_all([meat, dairy, trucks, passenger])
    db_session.commit()

    for activity in [meat, dairy, trucks, passenger]:
        db_session.refresh(activity)

    # Level 3
    parts = models.Activity(name="Parts", parent_id=passenger.id, level=3)
    db_session.add(parts)
    db_session.commit()
    db_session.refresh(parts)

    return {
        "food": food,
        "cars": cars,
        "meat": meat,
        "dairy": dairy,
        "trucks": trucks,
        "passenger": passenger,
        "parts": parts,
    }


@pytest.fixture(scope="function")
def sample_organizations(db_session, sample_buildings, sample_activities):
    """Create sample organizations"""
    org1 = models.Organization(name="Test Org 1", building_id=sample_buildings[0].id)
    org1.activities.extend([sample_activities["meat"], sample_activities["dairy"]])
    db_session.add(org1)
    db_session.commit()
    db_session.refresh(org1)

    # Add phone numbers
    phone1 = models.PhoneNumber(number="123-456-789", organization_id=org1.id)
    phone2 = models.PhoneNumber(number="987-654-321", organization_id=org1.id)
    db_session.add_all([phone1, phone2])

    org2 = models.Organization(name="Test Org 2", building_id=sample_buildings[1].id)
    org2.activities.append(sample_activities["trucks"])
    db_session.add(org2)
    db_session.commit()
    db_session.refresh(org2)

    phone3 = models.PhoneNumber(number="555-555-555", organization_id=org2.id)
    db_session.add(phone3)

    org3 = models.Organization(name="Test Org 3", building_id=sample_buildings[0].id)
    org3.activities.append(sample_activities["food"])
    db_session.add(org3)
    db_session.commit()
    db_session.refresh(org3)

    db_session.commit()

    return [org1, org2, org3]
