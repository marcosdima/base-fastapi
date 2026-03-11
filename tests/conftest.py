import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DB_PATH = BASE_DIR / 'tests' / 'test.sqlite3'

os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'
os.environ['POSTGRES_URL'] = f'sqlite:///{TEST_DB_PATH}'


from app.db import engine
from app.main import app


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
	if TEST_DB_PATH.exists():
		TEST_DB_PATH.unlink()

	SQLModel.metadata.create_all(engine)

	yield

	if TEST_DB_PATH.exists():
		TEST_DB_PATH.unlink()


@pytest.fixture(scope='function')
def db_session():
	with Session(engine) as session:
		yield session
		session.rollback()


@pytest.fixture(scope='function')
def client(setup_test_db):
	with TestClient(app) as c:
		yield c
