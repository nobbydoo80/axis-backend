"""examine.py: Django APS Examine Machinery"""


import logging

from axis import examine
from axis.customer_aps.api import APSSmartThermostatOptionViewSet
from axis.customer_aps.forms import APSSmartThermostatOptionsForm
from axis.subdivision.models import Subdivision

__author__ = "Steven K"
__date__ = "07/23/2019 12:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class APSSmartThermostatOptionsMachinery(examine.SingleObjectMachinery):
    """Machinery for APS Smart Thermostat Options"""

    model = Subdivision
    form_class = APSSmartThermostatOptionsForm
    type_name = "aps_thermostat_options"
    api_provider = APSSmartThermostatOptionViewSet
    form_template = "examine/subdivision/aps_thermostat_option_form.html"
    detail_template = "examine/subdivision/aps_thermostat_option_detail.html"

    def can_edit_object(self, instance, user):
        """Who can edit this"""
        return user.is_superuser or user.company.slug == "aps"

    def can_delete_object(self, instance, user):
        """We do not allow delete"""
        return False
