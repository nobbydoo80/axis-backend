__author__ = "Steven K"
__date__ = "8/10/21 08:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from .viewsets import (
    ProjectTrackerXMLViewSet,
    WashingtonCodeCreditCalculatorViewSet,
    ETO2021CalculatorViewSet,
    EPSReportViewSet,
    WCCReportViewSet,
    EPS2021FireRebuildCalculatorViewSet,
    ProjectTrackerViewSet,
)
from .viewsets.calculators.eto_2022 import ETO2022CalculatorViewSet
from .viewsets.eto_account import ETOAccountViewSet

log = logging.getLogger(__name__)


class CustomerETORouter:
    @staticmethod
    def register(router):
        router.register(
            r"calculator/eto-2022",
            ETO2022CalculatorViewSet,
            "eto_2022",
        )
        router.register(
            r"calculator/washington-code-credit",
            WashingtonCodeCreditCalculatorViewSet,
            "washington_code_credit",
        )
        router.register(
            r"calculator/eto-2021",
            ETO2021CalculatorViewSet,
            "eto_2021",
        )
        router.register(
            r"calculator/eto-fire-2021",
            EPS2021FireRebuildCalculatorViewSet,
            "eto_fire_2021",
        )
        router.register(
            r"project-tracker",
            ProjectTrackerXMLViewSet,
            "project_tracker",
        )
        router.register(
            r"eps-report",
            EPSReportViewSet,
            "eps_report",
        )
        router.register(
            r"wcc-report",
            WCCReportViewSet,
            "wcc_report",
        )
        router.register(
            r"project-tracker-list",
            ProjectTrackerViewSet,
            "project_tracker-list",
        )

        router.register("eto-account", ETOAccountViewSet, "eto-account")
