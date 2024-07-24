"""register.py: """

from axis.customer_aps.api_v3.viewsets import APSHomeDataExportViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class CustomerAPSRouter:
    @staticmethod
    def register(router):
        # customer_aps app
        aps_router = router.register(r"aps_home_data", APSHomeDataExportViewSet, "aps_home_data")
