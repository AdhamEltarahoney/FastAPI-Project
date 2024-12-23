from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import sessionmaker
from TodoApp.main import app
from TodoApp.database import Base
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase

from TodoApp.models import Todos  # Updated for SQLAlchemy 2.0
from TodoApp.models import Users
from ..routers.auth import bcrypt_context







SQL_ALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# Create an in-memory SQLite database engine
engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create a testing session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the SQLAlchemy base
class Base(DeclarativeBase):  # Updated for SQLAlchemy 2.0
    pass

# Create tables in the database for testing
Base.metadata.create_all(bind=engine)

# Dependency override for database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency override for current user
def override_get_current_user():
    return {"username": "Adham", "id": 1, "user_role": "admin"}

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(title="Test Todo", description="Test Description", priority= 5, complete = False, owner_id = 1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username="codingwithroby",
        email="codingwithrobytest@email.com",
        first_name="Eric",
        last_name="Roby",
        hashed_password=bcrypt_context.hash("testpassword"),
        role = "admin",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)  # Ensure the user object is up-to-date with the DB
    yield user  # Yield the user for use in tests
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM USERS"))
        connection.commit()
