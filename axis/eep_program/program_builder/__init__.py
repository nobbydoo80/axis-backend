"""Checklist builder"""


__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from .base import ProgramBuilder
from axis.eep_program.program_builder.programs.home_builder_association.built_green_king_sno import (
    BuiltGreenKingSno,
)
from .programs.home_builder_association.built_green_wa import (
    BuiltGreenWAPerformance,
    BuiltGreenWAPrescriptive,
)
from .programs.home_builder_association.built_green_tri_cities import BuiltGreenTriCities

from .programs.bullseye_eri_certification import BullseyeEriCertification
from .programs.doe.doe_zero_energy_06_performance import DoeZeroEnergyReadyRev05PerformancePath
from .programs.doe.doe_zero_energy_ready_rev_05_prescriptive_pat import (
    DoeZeroEnergyReadyRev05PrescriptivePat,
)
from .programs.earth_advantage import EarthAdvantageCertifiedHome
from .programs.epa.energy_star_31_08 import EnergyStarVersion31Rev08
from .programs.epa.energy_star_32_08 import EnergyStarVersion32Rev08
from .programs.epa.energy_star_3_08 import EnergyStarVersion3Rev08
from .programs.epa.energy_star_version_3_rev_07 import EnergyStarVersion3Rev07
from .programs.epa.energy_star_version_31_rev_05 import EnergyStarVersion31Rev05
from .programs.epa.energy_star_version_32_rev_09 import EnergyStarVersion32Rev09
from .programs.epa.indoor_airplus_01_03 import IndoorAirplusVersion1Rev03
from .programs.epa.watersense_version_12 import WatersenseVersion12

from .programs.bonded_builders_residential_energy_guarantee import (
    BondedBuildersResidentialEnergyGuarantee,
)
from .programs.bpca_monthly_reporting import BpcaMonthlyReporting
from .programs.mass_new_homes_with_energy_star_2012 import Program2012MassNewHomesWithEnergyStar
from .programs.mass_code_testing import MassCodeTesting
from .programs.nyserda_incentive_application_form import NyserdaIncentiveApplicationForm
from .programs.nyserda_qualification_form import NyserdaQualificationForm
from .programs.leed import Leed
from .programs.phius import Phius
from .programs.stretch_code_2012 import Program2012StretchCode
from .programs.wsu_2020 import Wsu2020
