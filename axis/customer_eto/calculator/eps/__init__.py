__author__ = "Steven Klass"
__date__ = "8/3/15 3:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from .constants.original import ETO_2019_FUEL_RATES, ETO_2019_FUEL_RATES_WA_OVERRIDE
from .constants.eto_2020 import ETO_2020_FUEL_RATES, ETO_2020_FUEL_RATES_WA_OVERRIDE
from .utils import get_eto_calculation_completed_form, get_eto_calculation_data, ETO_GEN2
from .calculator import EPSCalculator
