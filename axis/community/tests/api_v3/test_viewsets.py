"""viewsets.py: """

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient

from axis.community.models import Community
from axis.community.tests.mixins import CommunityViewTestMixin
from axis.community.tests.factories import community_factory
from axis.geographic.tests.factories import city_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.geographic.models import City
from axis.core.tests.factories import (
    provider_user_factory,
    builder_user_factory,
)

__author__ = "Artem Hruzd"
__date__ = "09/14/2020 11:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]


User = get_user_model()


class TestCommunityViewSet(ApiV3Tests):
    def setUp(self):
        self.client = APIClient()
        self.community = community_factory()

    def test_create_community(self):
        user = provider_user_factory(
            first_name="test_user", company__name="provider", is_company_admin=True
        )
        create_url = reverse_lazy("api_v3:communities-list")
        city = City.objects.first()
        community_name = f"Test Community Created by {user}"
        kwargs = dict(
            url=create_url,
            user=user,
            data=dict(
                name=community_name,
                city=city.pk,
                website="https://testwebsite.com/",
            ),
        )
        obj = self.create(**kwargs)
        self.assertEqual(obj["name"], community_name)
        self.assertEqual(obj["city"], city.pk)
        self.assertEqual(obj["website"], "https://testwebsite.com/")

        community = Community.objects.get(id=obj["id"])
        self.community = community
        # check for created relationships
        self.assertEqual(community.relationships.filter(company=user.company).count(), 1)

    def test_for_update_community(self):
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder", is_superuser=True
        )

        city = city_factory()
        self.assertNotEqual(city.id, self.community.city.id)
        self.client.force_authenticate(user=superuser)
        url = reverse_lazy("api_v3:communities-detail", args=[self.community.pk])
        data = {"name": "Updated Community", "city": city.pk}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Community")
        self.assertEqual(response.data["city"], city.id)

    def test_retrieve_community(self):
        url = reverse_lazy("api_v3:communities-detail", args=[self.community.pk])
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder", is_superuser=True
        )
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.community.pk)
        self.assertEqual(response.data["name"], self.community.name)
        self.assertEqual(response.data["city"], self.community.city.pk)
        self.assertEqual(response.data["website"], self.community.website)

    def test_retrieve_nonexistent_community(self):
        url = reverse_lazy("api_v3:communities-detail", args=[self.community.pk])
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder", is_superuser=True
        )
        self.client.force_authenticate(user=superuser)
        max_id = Community.objects.order_by("-id").first().id
        url = reverse_lazy("api_v3:communities-detail", args=[max_id + 1])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_delete_community(self):
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder", is_superuser=True
        )

        self.client.force_authenticate(user=superuser)
        prev_count = Community.objects.count()
        url = reverse_lazy("api_v3:communities-detail", args=[self.community.pk])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        next_count = Community.objects.count()
        self.assertEqual(prev_count - next_count, 1)

    def test_for_all_list(self):
        superuser = builder_user_factory(
            first_name="superuser", company__name="builder", is_superuser=True
        )

        url = reverse_lazy("api_v3:communities-all-list")
        self.client.force_authenticate(user=superuser)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
