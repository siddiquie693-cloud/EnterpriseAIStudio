from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class UserAuthenticationAPITests(APITestCase):
    def setUp(self):
        self.password = "OldPassword@123"

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password=self.password,
        )

        self.login_url = reverse("user-login")
        self.change_password_url = reverse("change-password")
        self.refresh_url = reverse("token-refresh")

    def get_tokens(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return response.data

    def test_change_password_success(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("NewPassword@123"))

    def test_change_password_wrong_old_password(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "WrongPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_change_password_mismatch(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@123",
                "confirm_password": "DifferentPassword@123",
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_change_password_same_password(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": self.password,
                "confirm_password": self.password,
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_refresh_token_blacklisted_after_password_change(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.credentials()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_with_new_password(self):
        tokens = self.get_tokens()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
                "refresh_token": tokens["refresh"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.credentials()

        response = self.client.post(
            self.login_url,
            {
                "email": self.user.email,
                "password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
