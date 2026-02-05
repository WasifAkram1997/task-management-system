import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from config import get_settings

settings = get_settings()

TEST_DATABASE_URL = f"postgresql://postgres:{settings.AUTH_DB_PASSWORD}@localhost:5433/auth_db_test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create tables before all tests and drop after tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Give each test a database session with rollback"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind = connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """Test client with database"""
    def get_test_db():
        yield db

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()