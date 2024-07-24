"""strings.py: Geographic"""


from axis.home.strings import (
    HOME_VERBOSE_NAME_LOT_NUMBER,
    HOME_VERBOSE_NAME_STREET_LINE1,
    HOME_VERBOSE_NAME_STREET_LINE2,
    HOME_VERBOSE_NAME_ZIPCODE,
    HOME_VERBOSE_NAME_CITY,
    HOME_HELP_TEXT_LOT_NUMBER,
    HOME_HELP_TEXT_STREET_LINE1,
    HOME_HELP_TEXT_STREET_LINE2,
    HOME_HELP_TEXT_ZIPCODE,
    HOME_HELP_TEXT_CITY,
)

from axis.subdivision.strings import (
    SUBDIVISION_VERBOSE_NAME_CROSS_ROADS,
    SUBDIVISION_VERBOSE_NAME_COMMUNITY,
    SUBDIVISION_VERBOSE_NAME_CITY,
    SUBDIVISION_HELP_TEXT_CROSS_ROADS,
    SUBDIVISION_HELP_TEXT_COMMUNITY,
    SUBDIVISION_HELP_TEXT_CITY,
)

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# These two are generic because we define them before the subclasses are made
PLACEDMODEL_VERBOSE_NAME_STREET_LINE1 = None
PLACEDMODEL_VERBOSE_NAME_CITY = SUBDIVISION_VERBOSE_NAME_CITY
PLACEDMODEL_VERBOSE_NAME_CROSS_ROADS = SUBDIVISION_VERBOSE_NAME_CROSS_ROADS
PLACEDMODEL_VERBOSE_NAME_MULTI_FAMILY = "Multi-family"
PLACEDMODEL_VERBOSE_NAME_COUNTY = "County"
PLACEDMODEL_VERBOSE_NAME_METRO = "Metro"
PLACEDMODEL_VERBOSE_NAME_STATE = "State"
PLACEDMODEL_VERBOSE_NAME_ADDRESS_OVERRIDE = "Override address"
PLACEDMODEL_HELP_TEXT_STREET_LINE1 = HOME_HELP_TEXT_STREET_LINE1
PLACEDMODEL_HELP_TEXT_COUNTY = None
PLACEDMODEL_HELP_TEXT_CITY = """Type the first few letters of the name of the city of the location and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database."""
PLACEDMODEL_HELP_TEXT_CROSS_ROADS = SUBDIVISION_HELP_TEXT_CROSS_ROADS
PLACEDMODEL_HELP_TEXT_ADDRESS_OVERRIDE = """Bypass the attempt to normalize the address via a mapping service. Changing address fields after marking this option will unmark it."""

PLACE_HELP_TEXT_CITY = "The city where this parcel of land resides"
PLACE_HELP_TEXT_COUNTY = "The county where this parcel of land resides"
PLACE_HELP_TEXT_CROSS_ROADS = (
    "The street intersection or crossroads where this parcel of land resides."
)
PLACE_HELP_TEXT_MULTI_FAMILY = "This denotes a multi-family project, such as an apartment or condo"
PLACE_HELP_TEXT_GEOCODE_RESPONSE = "The response this place was constructed from."

# US DOE Information
COUNTY_TYPES = (
    ("1", "County"),
    ("2", "Parish"),
    ("3", "City"),
    ("4", "Borough"),
    ("5", "Municipality"),
    ("6", "Municipio"),
    ("7", "Census Area"),
)
GEO_REGIONS = (("1", "Northeast"), ("2", "Midwest"), ("3", "South"), ("4", "West"))
GEO_DIVISIONS = (
    ("1", "New England"),
    ("2", "Middle Atlantic"),
    ("3", "East North Central"),
    ("4", "West North Central"),
    ("5", "South Atlantic"),
    ("6", "East South Central"),
    ("7", "West South Central"),
    ("8", "Mountain"),
    ("9", "Pacific"),
)
DOE_MOISTURE_REGIMES = (("B", "Dry"), ("A", "Moist"), ("C", "Marine"))
DOE_MOISTURE_REGIMES_MAP = dict(map(reversed, DOE_MOISTURE_REGIMES))
PLACE_ENTITY_TYPES = ["city", "county", "street_address", "neighborhood", "intersection"]
PLACE_ENTITY_CHOICES = [(x, x.replace("_", " ").capitalize()) for x in PLACE_ENTITY_TYPES]

# Bulk upload
MISSING_COUNTY = "No County provided"
UNKNOWN_COUNTY = "Unknown County '{county}'"
UNKNOWN_COUNTY_IN_STATE = "Unknown County '{county}' in state {state}"
MULTIPLE_COUNTIES_FOUND = "Multiple Counties found for '{county}'"
MULTIPLE_COUNTIES_FOUND_IN_STATE = "Multiple Counties found for '{county}'in {state}"
FOUND_COUNTY = "Using County {county}"

MISSING_CITY = "No City provided"
UNKNOWN_CITY = "Unknown City '{city}'"
UNKNOWN_CITY_IN_STATE = "Unknown City '{city}' in state {state}"
MULTIPLE_CITIES_FOUND = "Multiple Cities found for '{city}'"
MULTIPLE_CITIES_FOUND_IN_STATE = "Multiple Cities found for '{city}'in {state}"
FOUND_CITY = "Using City <a href='{url}'>{city}</a>"
