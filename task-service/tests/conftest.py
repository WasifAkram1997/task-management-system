import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from config import get_settings
from dependencies import get_current_user_id
import uuid

settings = get_settings()

TEST_DATABASE_URL = f"postgresql://postgres:{settings.TASK_DB_PASSWORD}@localhost:5434/task_db_test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock user ID for tests
TEST_USER_ID = uuid.uuid4()
   
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
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """Test client with database and mocked auth"""
    def get_test_db():
        yield db
    
    def mock_get_current_user_id():
        return TEST_USER_ID
    
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_current_user_id] = mock_get_current_user_id
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()