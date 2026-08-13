import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_me_without_authorization_header_returns_401(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert "Authorization" in response.json()["detail"]


def test_me_with_mocked_supabase_token_returns_user(client, monkeypatch):
    def fake_get_user_from_token(token: str):
        assert token == "valid-test-token"
        return {
            "id": "user_123",
            "email": "user@example.com",
            "user_metadata": {"full_name": "Test User"},
        }

    monkeypatch.setattr("app.core.security.get_user_from_token", fake_get_user_from_token)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid-test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "user_123",
        "email": "user@example.com",
        "metadata": {"full_name": "Test User"},
    }


def _unsigned_jwt(payload: dict) -> str:
    import base64
    import json

    def encode(part: dict) -> str:
        raw = json.dumps(part, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    return f"{encode({'alg': 'none', 'typ': 'JWT'})}.{encode(payload)}."


@pytest.mark.asyncio
async def test_require_mfa_rejects_aal1_token(monkeypatch):
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    from app.core.security import require_mfa

    token = _unsigned_jwt({"sub": "user_123", "aal": "aal1"})

    monkeypatch.setattr("app.core.security.get_user_from_token", lambda _: {"id": "user_123"})

    with pytest.raises(HTTPException) as exc:
        await require_mfa(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))

    assert exc.value.status_code == 403
    assert "Complete 2FA" in exc.value.detail


@pytest.mark.asyncio
async def test_require_mfa_allows_aal2_token(monkeypatch):
    from fastapi.security import HTTPAuthorizationCredentials

    from app.core.security import require_mfa

    expected_user = {"id": "user_123"}
    token = _unsigned_jwt({"sub": "user_123", "aal": "aal2"})

    monkeypatch.setattr("app.core.security.get_user_from_token", lambda _: expected_user)

    user = await require_mfa(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))

    assert user == expected_user


def test_me_with_expired_token_returns_descriptive_401(client, monkeypatch):
    def fake_get_user_from_token(token: str):
        raise RuntimeError("JWT expired")

    monkeypatch.setattr("app.core.security.get_user_from_token", fake_get_user_from_token)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer expired-test-token"},
    )

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_me_with_malformed_token_returns_descriptive_401(client, monkeypatch):
    def fake_get_user_from_token(token: str):
        raise RuntimeError("invalid JWT: malformed token")

    monkeypatch.setattr("app.core.security.get_user_from_token", fake_get_user_from_token)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer malformed-test-token"},
    )

    assert response.status_code == 401
    assert "malformed" in response.json()["detail"].lower()
