from django.conf import settings
from infrastructure.utils import symbol_by_name

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_APS", {})


class CustomerAPSConfig(customers.CustomerAppConfig):
    """Customer APS configuration."""

    name = "axis.customer_aps"
    CUSTOMER_SLUG = "aps"

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.eep_programs:Aps2015Audit"),
            symbol_by_name(f"{self.name}.eep_programs:Aps2019"),
            symbol_by_name(f"{self.name}.eep_programs:Aps2019Addon"),
            symbol_by_name(f"{self.name}.eep_programs:Aps2019Tstat"),
            symbol_by_name(f"{self.name}.eep_programs:ApsEnergyStarV3"),
            symbol_by_name(f"{self.name}.eep_programs:ApsEnergyStarV32014"),
            symbol_by_name(f"{self.name}.eep_programs:ApsEnergyStarV32018"),
            symbol_by_name(f"{self.name}.eep_programs:ApsEnergyStarV3Hers602018"),
            symbol_by_name(f"{self.name}.eep_programs:AzEnergyStarV32017"),
            symbol_by_name(f"{self.name}.eep_programs:Ed3MockEnergyStarHomes"),
            symbol_by_name(f"{self.name}.eep_programs:SrpEnergyStarHomes"),
        ]
