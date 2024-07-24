from axis.customer_neea import api
from ..router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(r"customer_neea_legacy_home", api.LegacyNEEAViewSet, "legacy_neea_home")
