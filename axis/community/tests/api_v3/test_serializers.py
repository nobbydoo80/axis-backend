"""serializers.py"""

from axis.community.api_v3.serializers import CommunityFlatListSerializer
from axis.geographic.tests.factories import city_factory, metro_factory
from axis.community.tests.factories import community_factory
from axis.core.tests.testcases import AxisTestCase

__author__ = "Naruhito Kaide"
__date__ = "05/01/2023 10:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Naruhito Kaide",
]


class TestCommunityFlatListSerializer(AxisTestCase):
    def test_serializer(self):
        self.city = city_factory()
        self.metro = metro_factory()
        self.community = community_factory(city=self.city, metro=self.metro)
        self.serializer = CommunityFlatListSerializer(instance=self.community)
        self.community.metro = self.metro
        self.community.metro.save()
        serializer = CommunityFlatListSerializer(instance=self.community)
        self.assertTrue(serializer)
        data = serializer.data
        self.dump_test_data(data)

    def test_get_city_metro(self):
        self.city = city_factory()
        self.metro = metro_factory()
        self.community = community_factory(city=self.city, metro=self.metro)
        self.serializer = CommunityFlatListSerializer(instance=self.community)
        self.community.metro = self.metro
        self.community.metro.save()
        expected_output = f"{self.city.name} ({self.metro.name})"
        self.assertEqual(self.serializer.get_city_metro(self.community), expected_output)
