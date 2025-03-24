import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base

# initialize test db
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """initiazling test db before each module test"""
    Base.metadata.create_all(bind=engine)
    
  
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

        Base.metadata.drop_all(bind=engine)