"""测试夹具：使用内存 SQLite 数据库，不污染真实数据。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# StaticPool 保证内存数据库在多个连接间共享
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前重建表，保证测试之间隔离。"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """注册一个测试用户并返回 token 和用户信息。"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "secret123",
            "display_name": "测试用户",
        },
    )
    assert response.status_code == 201
    user = response.json()

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "secret123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"token": token, "user": user, "headers": {"Authorization": f"Bearer {token}"}}
