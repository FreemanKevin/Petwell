import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from typing import Generator
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Use PostgreSQL in test environment
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5434/petwell_test"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database"""
    Base.metadata.drop_all(bind=engine)  # Clean existing tables
    Base.metadata.create_all(bind=engine)  # Create new tables
    yield
    Base.metadata.drop_all(bind=engine)  # Clean up after tests

@pytest.fixture
def db():
    """Use independent database session for each test case"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db) -> Generator:
    """Test client"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """Create test user"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers"""
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}
