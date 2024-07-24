"""appconfig.py: Django customer_neea"""
import datetime
import logging

from django.conf import settings

from infrastructure.utils import symbol_by_name

from axis.core import customers
from .neea_data_report.config import NEEADataReportConfig

__author__ = "Steven Klass"
__date__ = "1/17/17 06:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


settings = getattr(settings, "CUSTOMER_NEEA", {})


class CustomerNEEAConfig(customers.CustomerAppConfig):
    name = "axis.customer_neea"
    CUSTOMER_SLUG = "neea"
    extensions = customers.CustomerAppConfig.extensions + (NEEADataReportConfig,)
    NEEA_SP_INCENTIVE_UTILITY_SLUGS = [
        "clark-pud",
        "sno-pud",
        "utility-city-of-richland",
        "benton-rea",
        "puget-sound-energy",
        "central-electric",
        "pacific-power",
        "idaho-power",
        "inland-power",
        "utility-eugene-water-electric-board",
        "utility-tacoma-public-utilities",
        "utility-peninsula-power-light",
    ]

    NEEA_V2_ID_SUBMIT_DATE = datetime.date(2021, 7, 31)
    NEEA_V3_ID_AVAILABLE_DATE = datetime.date(2021, 8, 9)
    NEEA_V2_ID_CERTIFICATION_DATE = datetime.date(2021, 8, 31)

    NEEA_V2_WA_SUBMIT_DATE = datetime.date(2021, 9, 30)
    NEEA_V3_WA_AVAILABLE_DATE = datetime.date(2021, 10, 1)
    NEEA_V2_WA_CERTIFICATION_DATE = datetime.date(2022, 1, 1)

    NEEA_V2_OR_SUBMIT_DATE = datetime.date(2022, 3, 28)
    NEEA_V3_OR_AVAILABLE_DATE = datetime.date(2022, 3, 28)
    NEEA_V2_OR_CERTIFICATION_DATE = datetime.date(2022, 4, 30)

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.eep_programs:NeeaBpa"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaBpaV3"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaEfficientHomes"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaEnergyStarV3"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaEnergyStarV3Performance"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaEnergyStarV3Qa"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaPerformance2015"),
            symbol_by_name(f"{self.name}.eep_programs:NeeaPrescriptive2015"),
            symbol_by_name(f"{self.name}.eep_programs:NorthwestEnergyStarV3R8QaShort"),
            symbol_by_name(f"{self.name}.eep_programs:NorthwestEnergyStarV3R8QaLong"),
            symbol_by_name(f"{self.name}.eep_programs:NorthwestEnergyStarVersion32014Qa"),
            symbol_by_name(f"{self.name}.eep_programs:NorthwestEnergyStarVersion32014FullQa"),
            symbol_by_name(f"{self.name}.eep_programs:UtilityIncentiveV1Multifamily"),
            symbol_by_name(f"{self.name}.eep_programs:UtilityIncentiveV1SingleFamily"),
            symbol_by_name(f"{self.name}.eep_programs:WACodeStudy"),
        ]
