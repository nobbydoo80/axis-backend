"""strings.py: Subdivision"""

from axis.home import strings as _home_strings

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

SUBDIVISION_HELP_TEXT_NAME = """A subdivision is a parcel of land in which one builder intends to build several homes.  To add a subdivision association or create a new subdivision, type the first few letters of the name of the subdivision that you wish to associate with.  If the subdivision you wish to associate with already exists within the database, select it from the "Select from existing" list and click on "Submit" at the bottom of this page to create the association.  If the subdivision does not exist within the database, type the name of the subdivision, select it in the "Create new" list, and populate the fields below."""
SUBDIVISION_HELP_TEXT_BUILDER_ORG = """Type the first few letters of the name of the Builder that is building all homes in this subdivision, and select the correct company from the list presented.  If the correct company is not available, click "Add New" to add a new Builder or Builder association."""
SUBDIVISION_HELP_TEXT_COMMUNITY = """A community, also known as a "master-planned community", is a parcel of land in which one or more builders intend to build one or more subdivisions.  Select the community from the list presented.  If the correct community is not available, click "Add New" to add a new community or community association."""
SUBDIVISION_HELP_TEXT_CITY = """Type the first few letters of the name of the city the subdivision is located in and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database."""
SUBDIVISION_HELP_TEXT_CROSS_ROADS = (
    """Enter the crossroads or street intersection of this subdivision or leave blank if unknown."""
)
SUBDIVISION_HELP_TEXT_BUILDER_NAME = """If applicable, enter an alternate name or identifier for the subdivision such as the accounting code."""

SUBDIVISION_VERBOSE_NAME_BUILDER_NAME = "Alternate Name or Code"
SUBDIVISION_VERBOSE_NAME_COMMUNITY = "Community Name"
SUBDIVISION_VERBOSE_NAME_CITY = "City/State/County"
SUBDIVISION_VERBOSE_NAME_NAME = "Subdivision Name"
SUBDIVISION_VERBOSE_NAME_CROSS_ROADS = "Crossroads"
SUBDIVISION_VERBOSE_NAME_BUILDER_ORG = "Builder"

SUBDIVISION_HELP_TEXT_HOME_BUILDER = _home_strings.HOME_HELP_TEXT_HOME_BUILDER
SUBDIVISION_HELP_TEXT_PROVIDERS = _home_strings.HOME_HELP_TEXT_PROVIDERS
SUBDIVISION_HELP_TEXT_HVAC_CONTRACTORS = _home_strings.HOME_HELP_TEXT_HVAC_CONTRACTORS
SUBDIVISION_HELP_TEXT_QA_QC_COMPANIES = _home_strings.HOME_HELP_TEXT_QA_QC_COMPANIES
SUBDIVISION_HELP_TEXT_PROGRAM_SPONSORS = _home_strings.HOME_HELP_TEXT_PROGRAM_SPONSORS
SUBDIVISION_HELP_TEXT_UTILITY_COMPANIES = _home_strings.HOME_HELP_TEXT_UTILITY_COMPANIES
SUBDIVISION_HELP_TEXT_GENERAL_COMPANIES = _home_strings.HOME_HELP_TEXT_GENERAL_COMPANIES
SUBDIVISION_HELP_TEXT_USERS = _home_strings.HOME_HELP_TEXT_USERS

SUBDIVISION_FLOORPLAN_TAB_NAME = (
    """Enter the "marketing name" of the floorplan specified by the Builder."""
)
SUBDIVISION_FLOORPLAN_TAB_NUMBER = """Enter the numerical identifier for the floorplan."""
SUBDIVISION_FLOORPLAN_TAB_SQUARE_FOOTAGE = """Enter the square footage of the floorplan."""
SUBDIVISION_FLOORPLAN_TAB_DELETE = (
    """Click the "Delete" icon below to delete the floorplan from the database."""
)

SUBDIVISION_ASSOCIATION_REMOVAL_ERROR = """Unable to remove association for {owner} to {object}.  {owner} is an active customer; Please contact them for for removal."""

SUBDIVISION_AVAILABLE_FOR_REM_UPLOADS = """Subdivision <a href="{url}">{subdivision}</a> has been created and is available for REM/Rate™ uploads."""

# BULK Uploads
MISSING_SUBDIVISION = "No Subdivision or Builder Name provided"
UNKNOWN_SUBDIVISION = "Unknown Subdivision '{subdivision}'"
UNKNOWN_SUBDIVISION_BY_ID = "Unknown Subdivision with id '{id}'"

UNKNOWN_SUBDIVISION_WITH_BUILDER_NAME = "Unknown Subdivision with builder name of '{builder_name}'"
SUBDIVISION_NOT_EXIST_WITH_BUILDER = "'{subdivision}' does not exist with builder of '{builder}'"
SUBDIVISION_EXISTS_NO_RELATION = (
    "Subdivision '{subdivision}' exists but you don't have a association to it"
)
MULTIPLE_SUBDIVISIONS_FOUND = "Multiple Subdivisions found for '{subdivision}'"
SUBDIVISION_INCORRECT_COMMUNITY = (
    "Subdivision <a href='{url}'>{subdivision}</a> exists but is " "not part of '{community}'"
)
SUBDIVISION_MULTIFAMILY_MISMATCH = "Subdivision <a href='{url}'>{subdivision}</a> exists but doesn't share the same multi-family setting as '{community}'"
FOUND_SUBDIVISION = "Using Subdivision <a href='{url}'>{subdivision}</a>"
PROGRAM_OWNER_UNATTACHED = "Program owner {owner} is not assigned to this subdivision or has not agreed to be part of subdivision <a href='{url}'>{subdivision}</a>"
PROGRAM_IN_USE = "The {program} is already being used by {company} in subdivision <a href='{url}'>{subdivision}</a>"
SUBSTAT_USED_CREATE = (
    "{create} binding for {company} and {program} to <a href='{url}'>{subdivision}</a>"
)
