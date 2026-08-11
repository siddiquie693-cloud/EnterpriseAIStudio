from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckAPITests(APITestCase):
    def test_health_check(self):
        url = reverse("health")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data,
            {
                "status": "success",
                "message": "EnterpriseAIStudio API is running.",
                "version": "v1",
            },
        )

    def test_health_check_url(self):
        response = self.client.get("/api/v1/health/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
