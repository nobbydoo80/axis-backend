"""City Of Hillsboro customer extension."""


import os

from django.conf import settings

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10-10-2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_ETO", {})


class CityOfHillsboroConfig(customers.ExtensionConfig):
    CITY_OF_HILLSBORO_PARTICIPANT_SLUGS = (
        "earth-advantage-institute",
        "rater-moffet-energy-modeling",
    )
    CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS = {
        # 'community-slug': '(models.PermitAndOccupancySettings.)fieldname',
        "reeds-crossing": "reeds_crossing_compliance_option",
        "rosedale-parks": "rosedale_parks_compliance_option",
    }
    CITY_OF_HILLSBORO_COMMUNITY_SLUGS = tuple(CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS.keys())
    CITY_OF_HILLSBORO_FIELDS = tuple(CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS.values())
    CITY_OF_HILLSBORO_COMMUNITY_FORM_TEMPLATES = {
        "reeds-crossing": "{prefix}/../static/templates/compliance_reeds_crossing.pdf".format(
            prefix=os.path.dirname(__file__)
        ),
        "rosedale-parks": "{prefix}/../static/templates/compliance_rosedale_parks.pdf".format(
            prefix=os.path.dirname(__file__)
        ),
    }

    PERMIT_DESCRIPTION = "City of Hillsboro Building Permit Compliance Report"
    OCCUPANCY_DESCRIPTION = "City of Hillsboro Certificate of Occupancy Compliance Report"
    PERMIT_PAGE_COUNTS = {
        "reeds-crossing": 2,
        "rosedale-parks": 1,
    }

    def get_hillsboro_participants(self):
        """Return Company queryset for companies who make Hillsboro reports."""

        from axis.company.models import Company

        return Company.objects.filter(slug__in=self.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS)

    def get_permitandoccupancysettings_communities(self):  # pylint: disable=invalid-name
        """Return queryset of communities that participate in City Of Hillsboro settings."""

        from axis.community.models import Community

        return Community.objects.filter(slug__in=self.CITY_OF_HILLSBORO_COMMUNITY_SLUGS)
