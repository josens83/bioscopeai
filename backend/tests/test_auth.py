"""
인증 API 테스트
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user_data):
    """사용자 등록 테스트"""
    response = await client.post("/api/v1/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data  # 비밀번호는 응답에 포함되지 않아야 함


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user_data):
    """중복 이메일 등록 실패 테스트"""
    # 첫 번째 등록
    await client.post("/api/v1/auth/register", json=test_user_data)

    # 같은 이메일로 다시 등록 시도
    response = await client.post("/api/v1/auth/register", json=test_user_data)

    assert response.status_code == 400
    assert "이미 등록된 이메일" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user_data):
    """로그인 성공 테스트"""
    # 사용자 등록
    await client.post("/api/v1/auth/register", json=test_user_data)

    # 로그인
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user_data):
    """잘못된 비밀번호 로그인 실패 테스트"""
    # 사용자 등록
    await client.post("/api/v1/auth/register", json=test_user_data)

    # 잘못된 비밀번호로 로그인
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "올바르지 않습니다" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """존재하지 않는 사용자 로그인 실패 테스트"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    """인증 토큰 없이 보호된 라우트 접근 시도"""
    response = await client.get("/api/v1/papers/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_token(client: AsyncClient, test_user_data):
    """인증 토큰으로 보호된 라우트 접근"""
    # 사용자 등록 및 로그인
    await client.post("/api/v1/auth/register", json=test_user_data)

    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    token = login_response.json()["access_token"]

    # 토큰으로 보호된 라우트 접근
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/papers/", headers=headers)

    assert response.status_code == 200
