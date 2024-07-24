"""Test viewsets.py: """


__author__ = "Artem Hruzd"
__date__ = "09/07/2020 17:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from axis.community.models import Community
from axis.core.tests.testcases import ApiV3Tests
from axis.geographic.models import City
from axis.subdivision.models import Subdivision

from axis.subdivision.tests.mixins import SubdivisionViewTestMixin

User = get_user_model()


class TestSubdivisionViewSet(SubdivisionViewTestMixin, ApiV3Tests):
    def test_create(self):
        rater = self.get_admin_user(company_type="rater")
        create_url = reverse_lazy("api_v3:subdivisions-list")
        city = City.objects.first()
        builder_company = (
            rater.company.relationships.get_companies(is_customer=False)
            .filter(company_type="builder")
            .first()
        )
        community = Community.objects.filter_by_user(rater).first()

        kwargs = dict(
            url=create_url,
            user=rater,
            data=dict(
                name="Test Subdivision Created by {}".format(rater),
                builder_org=builder_company.pk,
                community=community.pk,
                city=city.pk,
                is_multi_family=True,
                use_sampling=True,
                use_metro_sampling=True,
                cross_roads="Test Cross Roads",
                builder_name="Test Alternate Name",
            ),
        )
        obj = self.create(**kwargs)
        self.assertEqual(obj["name"], "Test Subdivision Created by {}".format(rater))
        self.assertEqual(obj["builder_org"], builder_company.pk)
        self.assertEqual(obj["community"], community.pk)
        self.assertEqual(obj["city"], city.pk)
        self.assertTrue(obj["is_multi_family"])
        self.assertTrue(obj["use_sampling"])
        self.assertTrue(obj["use_metro_sampling"])
        self.assertEqual(obj["cross_roads"], "Test Cross Roads")
        self.assertEqual(obj["builder_name"], "Test Alternate Name")

        subdivision = Subdivision.objects.get(id=obj["id"])
        # check for created relationships
        self.assertEqual(subdivision.relationships.filter(company=builder_company).count(), 1)
        self.assertEqual(community.relationships.filter(company=rater.company).count(), 1)
