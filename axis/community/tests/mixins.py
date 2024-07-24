"""fixturecompilers.py: Django community"""


import logging

__author__ = "Steven Klass"
__date__ = "3/19/14 10:13 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityViewTestMixin:
    @classmethod
    def setUpTestData(cls):
        from axis.geocoder.models import Geocode
        from axis.geographic.models import City
        from axis.geographic.tests.factories import real_city_factory
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.community.tests.factories import community_factory
        from axis.community.tests.test_views import (
            get_create_intersection_address,
            get_update_intersection_address,
        )
        from axis.core.tests.factories import general_user_factory, general_admin_factory
        from axis.relationship.models import Relationship

        city = real_city_factory("Gilbert", "AZ")

        user = general_admin_factory(company__city=city)
        general_user_factory(company=user.company)

        community_1 = community_factory(city=city)
        subdivision = subdivision_factory(city=city, community=community_1)
        community_2 = community_factory(city=city)
        community_3 = community_factory(city=city)

        Relationship.objects.validate_or_create_relations_to_entity(community_1, user.company)
        Relationship.objects.validate_or_create_relations_to_entity(community_2, user.company)

        real_city_factory("Mesa", "AZ")

        # This shows how to add a Geocode response object - Notice I created a "real" City..
        create_addr = get_create_intersection_address()
        update_addr = get_update_intersection_address()
        Geocode.objects.get_matches(raw_address=None, **create_addr)
        Geocode.objects.get_matches(raw_address=None, **update_addr)

        assert City.objects.all().count() == 2, "We only want 2 cities {}".format(
            City.objects.all()
        )
        user.company.counties.add(community_1.city.county)
        user.company.countries.add(community_1.city.country)
