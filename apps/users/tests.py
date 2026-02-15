import pytest
from django.urls import reverse
from rest_framework import status


REGISTER_URL = reverse("users:register")
LOGIN_URL = reverse("users:login")
PROFILE_URL = reverse("users:profile")


# ─── Register Tests ────────────────────────────────


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, api_client):
        payload = {
            "email": "new@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]
        assert response.data["data"]["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, api_client, user):
        payload = {
            "email": "test@example.com",  # user fixture already has this
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "Dup",
            "last_name": "User",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        payload = {
            "email": "short@example.com",
            "password": "123",
            "password_confirm": "123",
            "first_name": "Short",
            "last_name": "Pass",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client):
        payload = {
            "email": "mismatch@example.com",
            "password": "strongpass123",
            "password_confirm": "differentpass",
            "first_name": "Mis",
            "last_name": "Match",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_first_name(self, api_client):
        payload = {
            "email": "noname@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "",
            "last_name": "User",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, api_client):
        payload = {
            "email": "not-an-email",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "Bad",
            "last_name": "Email",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─── Login Tests ───────────────────────────────────


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, user):
        payload = {"email": "test@example.com", "password": "testpass123"}
        response = api_client.post(LOGIN_URL, payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]

    def test_login_wrong_password(self, api_client, user):
        payload = {"email": "test@example.com", "password": "wrongpass"}
        response = api_client.post(LOGIN_URL, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_login_nonexistent_email(self, api_client):
        payload = {"email": "ghost@example.com", "password": "whatever"}
        response = api_client.post(LOGIN_URL, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ─── Profile Tests ─────────────────────────────────


@pytest.mark.django_db
class TestProfile:
    def test_get_profile_success(self, auth_client, user):
        response = auth_client.get(PROFILE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert response.data["first_name"] == user.first_name

    def test_update_profile(self, auth_client, user):
        payload = {"first_name": "Updated", "last_name": "Name"}
        response = auth_client.put(PROFILE_URL, payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"

    def test_profile_unauthenticated(self, api_client):
        response = api_client.get(PROFILE_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ─── Token Refresh Tests ──────────────────────────


REFRESH_URL = reverse("users:token-refresh")


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_token_success(self, api_client, user):
        # Login to get tokens
        login_response = api_client.post(
            LOGIN_URL, {"email": "test@example.com", "password": "testpass123"}
        )
        refresh_token = login_response.data["data"]["tokens"]["refresh"]

        # Use refresh token to get new access token
        response = api_client.post(REFRESH_URL, {"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_token_invalid(self, api_client):
        response = api_client.post(REFRESH_URL, {"refresh": "invalid-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
