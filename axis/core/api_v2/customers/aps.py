from axis.customer_aps import api
from axis.customer_aps.api import APSSmartThermostatOptionViewSet
from ..router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(r"customer/aps/apshome", api.APSHomeViewSet, "apshome")
api_router.register(
    r"subdivision/aps_thermostat_options", APSSmartThermostatOptionViewSet, "aps_thermostat_options"
)
