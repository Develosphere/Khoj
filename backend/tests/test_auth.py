from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.core import security
from app.main import app

client = TestClient(app)


class MockMfa:
    def enroll(self, factor_type: str):
        assert factor_type == "totp"
        return SimpleNamespace(id="factor-123", totp=SimpleNamespace(qr_code="otpauth://totp/khoj"))

    def challenge(self, factor_id: str):
        assert factor_id == "factor-123"
        return SimpleNamespace(id="challenge-123", expires_at="2030-01-01T00:00:00Z")

    def verify(self, factor_id: str, challenge_id: str, code: str):
        assert factor_id == "factor-123"
        assert challenge_id == "challenge-123"
        assert code == "123456"
        return SimpleNamespace(
            aal="aal2",
            session=SimpleNamespace(access_token="aal2-token"),
        )

    def unenroll(self, factor_id: str):
        assert factor_id == "factor-123"
        return {"id": factor_id}


class MockAuth:
    mfa = MockMfa()

    def sign_up(self, credentials: dict):
        if credentials["email"] == "exists@example.com":
            raise Exception("email already registered")
        return SimpleNamespace(
            user=SimpleNamespace(
                id="user-123",
                email=credentials["email"],
                user_metadata={},
            )
        )

    def sign_in_with_password(self, credentials: dict):
        if credentials["password"] != "correct-password":
            raise Exception("invalid credentials")
        return SimpleNamespace(
            session=SimpleNamespace(access_token="valid-token", aal="aal1"),
            user=SimpleNamespace(
                id="user-123",
                email=credentials["email"],
                user_metadata={},
            ),
        )

    def get_user(self, token: str):
        if token == "aal1-token":
            aal = "aal1"
        elif token in {"valid-token", "aal2-token"}:
            aal = "aal2" if token == "aal2-token" else "aal1"
        else:
            raise Exception("invalid jwt")
        return SimpleNamespace(
            user=SimpleNamespace(
                id="user-123",
                email="user@example.com",
                user_metadata={"name": "Test User"},
                aal=aal,
            )
        )


class MockSupabase:
    auth = MockAuth()


def test_me_without_authorization_header_returns_401():
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Authorization bearer token"


def test_me_with_mocked_valid_supabase_token_returns_user(monkeypatch):
    monkeypatch.setattr(security, "supabase", MockSupabase())

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "user-123",
        "email": "user@example.com",
        "metadata": {"name": "Test User"},
    }


def test_mfa_enroll_with_mocked_valid_token_returns_factor(monkeypatch):
    monkeypatch.setattr(security, "supabase", MockSupabase())
    from app.api.v1.endpoints import auth as auth_endpoint

    monkeypatch.setattr(auth_endpoint, "supabase", MockSupabase())

    response = client.post(
        "/api/v1/auth/mfa/enroll",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "factor_id": "factor-123",
        "qr_code_url": "otpauth://totp/khoj",
    }


def test_mfa_challenge_verify_and_unenroll_with_mocked_valid_token(monkeypatch):
    monkeypatch.setattr(security, "supabase", MockSupabase())
    from app.api.v1.endpoints import auth as auth_endpoint

    monkeypatch.setattr(auth_endpoint, "supabase", MockSupabase())
    headers = {"Authorization": "Bearer valid-token"}

    challenge_response = client.post(
        "/api/v1/auth/mfa/challenge",
        json={"factor_id": "factor-123"},
        headers=headers,
    )
    assert challenge_response.status_code == 200
    assert challenge_response.json()["challenge_id"] == "challenge-123"

    verify_response = client.post(
        "/api/v1/auth/mfa/verify",
        json={
            "factor_id": "factor-123",
            "challenge_id": "challenge-123",
            "code": "123456",
        },
        headers=headers,
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["aal"] == "aal2"
    assert verify_response.json()["access_token"] == "aal2-token"

    unenroll_response = client.post(
        "/api/v1/auth/mfa/unenroll",
        json={"factor_id": "factor-123"},
        headers=headers,
    )
    assert unenroll_response.status_code == 200
    assert unenroll_response.json()["status"] == "unenrolled"


def test_register_success_and_error(monkeypatch):
    from app.api.v1.endpoints import auth as auth_endpoint

    monkeypatch.setattr(auth_endpoint, "supabase", MockSupabase())

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "secret-password"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert response.json()["id"] == "user-123"

    error_response = client.post(
        "/api/v1/auth/register",
        json={"email": "exists@example.com", "password": "secret-password"},
    )
    assert error_response.status_code == 400
    assert "email already registered" in error_response.json()["detail"]


def test_login_success_and_error(monkeypatch):
    from app.api.v1.endpoints import auth as auth_endpoint

    monkeypatch.setattr(auth_endpoint, "supabase", MockSupabase())

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-password"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "valid-token"
    assert response.json()["aal"] == "aal1"
    assert response.json()["user"]["email"] == "user@example.com"

    error_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )
    assert error_response.status_code == 401
    assert "invalid credentials" in error_response.json()["detail"]


def test_me_with_invalid_token_returns_401(monkeypatch):
    monkeypatch.setattr(security, "supabase", MockSupabase())

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or malformed JWT token"


def test_mfa_guard_requires_aal2(monkeypatch):
    monkeypatch.setattr(security, "supabase", MockSupabase())

    aal1_response = client.get(
        "/api/v1/auth/mfa/protected",
        headers={"Authorization": "Bearer aal1-token"},
    )
    assert aal1_response.status_code == 403

    aal2_response = client.get(
        "/api/v1/auth/mfa/protected",
        headers={"Authorization": "Bearer aal2-token"},
    )
    assert aal2_response.status_code == 200
    assert aal2_response.json() == {"status": "ok", "aal": "aal2"}
