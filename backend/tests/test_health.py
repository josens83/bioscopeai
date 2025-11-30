"""
Health Check 테스트
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_basic_health_check(client: AsyncClient):
    """기본 헬스 체크 테스트"""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_detailed_health_check(client: AsyncClient):
    """상세 헬스 체크 테스트"""
    response = await client.get("/api/v1/health/detailed")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "system" in data["checks"]
    assert data["checks"]["database"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """준비 상태 체크 테스트 (Kubernetes readiness probe)"""
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient):
    """생존 상태 체크 테스트 (Kubernetes liveness probe)"""
    response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data
