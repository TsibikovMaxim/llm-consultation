import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "other_password"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_success(client):
    await client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    login = await client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_me_no_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    response = await client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
