"""hirl_project.py: """

__author__ = "Artem Hruzd"
__date__ = "04/23/2021 15:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db.models import Q

from axis.customer_hirl.models import HIRLProjectRegistration, HIRLProject
from axis.home.api_v3.serializers import HomeAddressIsUniqueRequestDataSerializer
from axis.qa.models import QAStatus


CERTIFICATION_LEVEL_MAP = {
    QAStatus.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED: {
        "title": "BRONZE",
        "color": (0.722, 0.471, 0.365),
    },
    QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED: {
        "title": "SILVER",
        "color": (0.86, 0.86, 0.86),
    },
    QAStatus.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED: {
        "title": "GOLD",
        "color": (0.776, 0.588, 0.039),
    },
    QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED: {
        "title": "EMERALD",
        "color": (0, 0.698, 0.455),
    },
    QAStatus.CERTIFIED_HIRL_CERTIFICATION_LEVEL_AWARDED: {"title": "CERTIFIED", "color": (0, 0, 0)},
    QAStatus.CONFORMING_HIRL_CERTIFICATION_LEVEL_AWARDED: {
        "title": "CONFORMING",
        "color": (0, 0, 0),
    },
    None: {"title": "UNKNOWN", "color": (0, 0, 0)},
}


def hirl_project_address_is_unique(
    street_line1, city, zipcode, project_type, street_line2="", project=None, geocode_response=None
):
    """
    Check if provided address is already using by Home or HIRLProject
    :param street_line1: string
    :param city: City object
    :param zipcode: string
    :param project_type: HIRLProjectRegistration.project_type
    :param street_line2: string
    :param project: HIRLProject or None
    :param geocode_response: HIRLProject geocode_response or None
    :return: Boolean
    """
    home = None
    if project and project.home_status:
        home = project.home_status.home

    is_unique, _ = HomeAddressIsUniqueRequestDataSerializer().home_address_is_unique(
        instance=home,
        street_line1=street_line1,
        street_line2=street_line2,
        is_multi_family=project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        city=city.pk,
        zipcode=zipcode,
        geocode_response=geocode_response,
        second_pass=True,
    )

    projects_query = HIRLProject.objects.filter(
        Q(
            home_address_geocode__raw_street_line1=street_line1,
            home_address_geocode__raw_street_line2=street_line2,
            home_address_geocode__raw_zipcode=zipcode,
            home_address_geocode__raw_city=city,
            home_address_geocode_response__isnull=True,
        )
        | Q(
            home_address_geocode_response=geocode_response,
            home_address_geocode_response__isnull=False,
        )
    )

    if project:
        projects_query = projects_query.exclude(pk=project.pk)
    projects_exists = projects_query.exists()

    if not is_unique or projects_exists:
        return False
    return True


def get_hirl_project_address_components(home_address_geocode, home_address_geocode_response):
    """
    Get main address components from Geocode and GeocodeResponse fields for HIRLProject
    :param home_address_geocode: Geocode object or None
    :param home_address_geocode_response: GeocodeResponse object or None
    :return: Dict address components or None
    """
    if home_address_geocode:
        street_line1 = home_address_geocode.raw_street_line1
        street_line2 = home_address_geocode.raw_street_line2
        city = home_address_geocode.raw_city
        zipcode = home_address_geocode.raw_zipcode
    elif (
        home_address_geocode_response
        and home_address_geocode_response.broker
        and home_address_geocode_response.broker.place
    ):
        street_line1 = home_address_geocode_response.broker.place.street_line1
        street_line2 = home_address_geocode_response.broker.place.street_line2
        city = home_address_geocode_response.broker.city_object
        zipcode = home_address_geocode_response.broker.place.zipcode
    else:
        return None
    return {
        "street_line1": street_line1,
        "street_line2": street_line2,
        "city": city,
        "zipcode": zipcode,
    }
