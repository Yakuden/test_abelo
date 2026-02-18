import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_process(client: AsyncClient):
    payload = {"data": "hello world", "priority": 3}
    response = await client.post("/process", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["data_length"] == 11
    assert body["result"] == "processed-3"
    assert "request_id" in body


@pytest.mark.anyio
async def test_process_default_priority(client: AsyncClient):
    response = await client.post("/process", json={"data": "test"})
    assert response.status_code == 200
    assert response.json()["result"] == "processed-1"


@pytest.mark.anyio
async def test_process_validation_error(client: AsyncClient):
    response = await client.post("/process", json={"data": "", "priority": 1})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_message(client: AsyncClient):
    response = await client.get("/message/1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert "text" in body
    assert "author" in body
    assert "created_at" in body


@pytest.mark.anyio
async def test_get_message_not_found(client: AsyncClient):
    response = await client.get("/message/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Message not found"


@pytest.mark.anyio
async def test_metrics_endpoint(client: AsyncClient):
    await client.get("/health")
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "app_requests_total" in body
    assert "python_gc" in body
