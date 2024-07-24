"""test_api.py: """


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

__author__ = "Autumn Valenta"
__date__ = "07/25/2019 18:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class APITests(APITestCase):
    def test_menu_access_anonymous(self):
        response = self.client.get(reverse("api_v3:menu"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
