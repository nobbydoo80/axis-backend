"""TRC EPS data"""


import os.path
import logging


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
prefix = os.path.dirname(__file__) + "/"

# Make sure tables are in the desired hierarchical filter order from left to right.
with open(prefix + "sources/furnaces.csv") as f:
    FURNACE_LOOKUPS = f.read()

with open(prefix + "sources/heat_pumps.csv") as f:
    HEAT_PUMP_LOOKUPS = f.read()

with open(prefix + "sources/water_heaters.csv") as f:
    WATER_HEATER_LOOKUPS = f.read()

with open(prefix + "sources/refrigerators.csv") as f:
    REFRIGERATOR_LOOKUPS = f.read()

with open(prefix + "sources/dishwashers.csv") as f:
    DISHWASHER_LOOKUPS = f.read()

with open(prefix + "sources/clothes_washers.csv") as f:
    CLOTHES_WASHER_LOOKUPS = f.read()

with open(prefix + "sources/clothes_dryers.csv") as f:
    CLOTHES_DRYER_LOOKUPS = f.read()

with open(prefix + "sources/ventilation_balanced.csv") as f:
    VENTILATION_BALANCED_LOOKUPS = f.read()

with open(prefix + "sources/ventilation_exhaust.csv") as f:
    VENTILATION_EXHAUST_LOOKUPS = f.read()
