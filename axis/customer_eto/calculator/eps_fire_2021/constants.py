"""constants.py - Axis"""

__author__ = "Steven K"
__date__ = "12/4/21 08:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.customer_eto.calculator.eps_2021.base import (
    HomePath,
    HomeSubType,
    LoadProfile,
    ElectricLoadProfile,
    GasLoadProfile,
)
from axis.customer_eto.calculator.eps_2021.constants import Constants
from axis.customer_eto.enumerations import PNWUSStates, ElectricUtility

log = logging.getLogger(__name__)


class FireConstants(Constants):
    def get_default_load_profile_data(self):
        return {
            # Path 1
            (HomePath.PATH_1, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                33.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_1, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                34.0,
                0.990,
                0.010,
            ),
            (HomePath.PATH_1, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.360,
                0.640,
            ),
            (HomePath.PATH_1, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.290,
                0.710,
            ),
            # Path 2
            (HomePath.PATH_2, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                41.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_2, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                42.0,
                0.910,
                0.090,
            ),
            (HomePath.PATH_2, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.320,
                0.680,
            ),
            (HomePath.PATH_2, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                41.0,
                0.250,
                0.750,
            ),
            # Path 3
            (HomePath.PATH_3, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                33.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_3, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                35.0,
                0.910,
                0.090,
            ),
            (HomePath.PATH_3, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                37.0,
                0.310,
                0.690,
            ),
            (HomePath.PATH_3, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.260,
                0.740,
            ),
            # Path 4
            (HomePath.PATH_4, HomeSubType.EHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.NONE,
                34.0,
                1.0,
                0.0,
            ),
            (HomePath.PATH_4, HomeSubType.EHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_ASHP,
                GasLoadProfile.HOT_WATER,
                35.0,
                0.910,
                0.090,
            ),
            (HomePath.PATH_4, HomeSubType.GHEW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_WATER_HEAT,
                GasLoadProfile.RESIDENTIAL_HEATING,
                37.0,
                0.320,
                0.680,
            ),
            (HomePath.PATH_4, HomeSubType.GHGW): LoadProfile(
                ElectricLoadProfile.RESIDENTIAL_CENTRAL_AC,
                GasLoadProfile.RESIDENTIAL_HEATING,
                39.0,
                0.270,
                0.730,
            ),
        }
