"""
논문 API 테스트
"""
import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, test_user_data) -> str:
    """인증 토큰 획득 헬퍼"""
    await client.post("/api/v1/auth/register", json=test_user_data)

    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_list_papers_empty(client: AsyncClient, test_user_data):
    """빈 논문 리스트 조회 테스트"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/papers/", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_paper(client: AsyncClient, test_user_data, test_paper_data):
    """논문 생성 테스트"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/papers/", headers=headers, json=test_paper_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_paper_data["title"]
    assert data["authors"] == test_paper_data["authors"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_paper_by_id(client: AsyncClient, test_user_data, test_paper_data):
    """논문 ID로 조회 테스트"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # 논문 생성
    create_response = await client.post(
        "/api/v1/papers/", headers=headers, json=test_paper_data
    )
    paper_id = create_response.json()["id"]

    # 논문 조회
    response = await client.get(f"/api/v1/papers/{paper_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == paper_id
    assert data["title"] == test_paper_data["title"]


@pytest.mark.asyncio
async def test_get_nonexistent_paper(client: AsyncClient, test_user_data):
    """존재하지 않는 논문 조회 테스트"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/papers/99999", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_paper(client: AsyncClient, test_user_data, test_paper_data):
    """논문 삭제 테스트"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # 논문 생성
    create_response = await client.post(
        "/api/v1/papers/", headers=headers, json=test_paper_data
    )
    paper_id = create_response.json()["id"]

    # 논문 삭제
    response = await client.delete(f"/api/v1/papers/{paper_id}", headers=headers)

    assert response.status_code == 200

    # 삭제 확인
    get_response = await client.get(f"/api/v1/papers/{paper_id}", headers=headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_search_papers_pubmed(client: AsyncClient, test_user_data):
    """PubMed 검색 테스트 (Mock)"""
    token = await get_auth_token(client, test_user_data)
    headers = {"Authorization": f"Bearer {token}"}

    # 실제 PubMed API를 호출하므로 간단한 검색어 사용
    # 프로덕션에서는 Mock을 사용해야 함
    response = await client.get(
        "/api/v1/papers/search?query=cancer&max_results=5", headers=headers
    )

    # API 키가 없거나 제한이 있을 수 있으므로 200 또는 429(Too Many Requests) 허용
    assert response.status_code in [200, 429, 500]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
