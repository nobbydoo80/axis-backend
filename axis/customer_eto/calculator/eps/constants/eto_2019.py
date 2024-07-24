"""eto_2019: Django ETO-2019 Constants"""


# pylint disable=wildcard-import,unused-wildcard-import
from .eto_2018 import *

__author__ = "Steven Klass"
__date__ = "12/14/2018 08:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR = {
    "natural gas": 11.7,
    "pacific power": 1.09,
    "portland general": 1.09,
    "bpa": 0.067,
}
EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA = EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR

ALTERNATE_METHOD_ELECTRIC_SAVINGS_ALLOCATION = 0.237473
ALTERNATE_METHOD_GAS_SAVINGS_ALLOCATION = 0.762527
ALTERNATE_METHOD_ELECTRIC_INCENTIVE_ALLOCATION = 0.667763
ALTERNATE_METHOD_GAS_INCENTIVE_ALLOCATION = 0.332237
