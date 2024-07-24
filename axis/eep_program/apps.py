from django.conf import settings

from axis.core import platform
from infrastructure.utils import symbol_by_name

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "EEP_PROGRAM", {})


class EEPProgramConfig(platform.PlatformAppConfig):
    """EEP Program platform configuration."""

    name = "axis.eep_program"

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.program_builder:BpcaMonthlyReporting"),
            symbol_by_name(f"{self.name}.program_builder:BondedBuildersResidentialEnergyGuarantee"),
            symbol_by_name(f"{self.name}.program_builder:BuiltGreenKingSno"),
            symbol_by_name(f"{self.name}.program_builder:BuiltGreenTriCities"),
            symbol_by_name(f"{self.name}.program_builder:BuiltGreenWAPerformance"),
            symbol_by_name(f"{self.name}.program_builder:BuiltGreenWAPrescriptive"),
            symbol_by_name(f"{self.name}.program_builder:BullseyeEriCertification"),
            symbol_by_name(f"{self.name}.program_builder:DoeZeroEnergyReadyRev05PerformancePath"),
            symbol_by_name(f"{self.name}.program_builder:DoeZeroEnergyReadyRev05PrescriptivePat"),
            symbol_by_name(f"{self.name}.program_builder:EarthAdvantageCertifiedHome"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion31Rev05"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion31Rev08"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion32Rev08"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion32Rev09"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion3Rev07"),
            symbol_by_name(f"{self.name}.program_builder:EnergyStarVersion3Rev08"),
            symbol_by_name(f"{self.name}.program_builder:IndoorAirplusVersion1Rev03"),
            symbol_by_name(f"{self.name}.program_builder:WatersenseVersion12"),
            symbol_by_name(f"{self.name}.program_builder:Leed"),
            symbol_by_name(f"{self.name}.program_builder:MassCodeTesting"),
            symbol_by_name(f"{self.name}.program_builder:NyserdaIncentiveApplicationForm"),
            symbol_by_name(f"{self.name}.program_builder:NyserdaQualificationForm"),
            symbol_by_name(f"{self.name}.program_builder:Phius"),
            symbol_by_name(f"{self.name}.program_builder:Program2012MassNewHomesWithEnergyStar"),
            symbol_by_name(f"{self.name}.program_builder:Program2012StretchCode"),
            symbol_by_name(f"{self.name}.program_builder:Wsu2020"),
        ]
