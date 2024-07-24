from collections import OrderedDict

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

COMPANY_TYPES_PLURAL = OrderedDict(
    [
        ("builder", ("Builder", "Builders")),
        ("eep", ("Program Sponsor", "Program Sponsors")),
        ("provider", ("Certification Organization", "Certification Organizations")),
        ("rater", ("Rating/Verification Company", "Rating/Verification Companies")),
        ("utility", ("Utility Company", "Utility Companies")),
        ("hvac", ("HVAC Contractor", "HVAC Contractors")),
        ("qa", ("QA/QC Company", "QA/QC Companies")),
        ("architect", ("Architect Company", "Architect Companies")),
        ("developer", ("Developer Company", "Developer Companies")),
        ("communityowner", ("Owner Company", "Owner Companies")),
        ("general", ("General Company", "General Companies")),
    ]
)

COMPANY_TYPES = [(key, COMPANY_TYPES_PLURAL[key][0]) for key in COMPANY_TYPES_PLURAL.keys()]
COMPANY_TYPES_MAPPING = OrderedDict(COMPANY_TYPES)
COMPANY_PLURAL_TYPES = [(key, COMPANY_TYPES_PLURAL[key][1]) for key in COMPANY_TYPES_PLURAL.keys()]
COMPANY_TYPES_PLURAL_MAPPING = OrderedDict(COMPANY_PLURAL_TYPES)

# Views
COMPANY_PROFILE_UPDATED = (
    """{user} has updated the {company} profile.  <a href="{url}">View current profile</a>."""
)

# Bulk Upload
MISSING_COMPANY = "No {company_type} provided"
COMPANY_EXISTS_NO_RELATION = (
    "{company_type} '{company}' exists but you don't have a association to them"
)
UNKNOWN_COMPANY = "Unknown {company_type} with name '{company}'"
UNKNOWN_COMPANY_BY_ID = "Unknown {company_type} with id '{id}'"
MULTIPLE_COMPANIES_FOUND = "Multiple {company_type} found for '{company}'"
FOUND_COMPANY = "Using {company_type} <a href='{url}'>{company}</a>"

HELP_TEXT_IS_CUSTOMER = """If the company is a paying us they are a customer"""

SUBDIVISION_HELP_TEXT_NAME = """Type the first few letters of the name of the company that you wish to associate with.  If the company you wish to associate with already exists within the database, select it from the "Select from existing" list and click on "Submit" at the bottom of this page to create the association.  If the company does not exist within the database, type the full name of the company, select it in the "Create new" list, and populate the fields below."""
SUBDIVISION_HELP_TEXT_STREET_LINE1 = """Enter the street address of the company.  Use the second line for a PO box or leave it blank."""
SUBDIVISION_HELP_TEXT_CITY = """Type the first few letters of the name of the city the company is located in and select the correct city/state/county combination from the list presented."""
SUBDIVISION_HELP_TEXT_ZIPCODE = """Enter the 5-digit ZIP Code of home."""
SUBDIVISION_HELP_TEXT_HOME_PAGE = """Optional field - Enter the website for the company."""
SUBDIVISION_HELP_TEXT_OFFICE_PHONE = (
    """Enter the main company phone number in the format XXX-XXX-XXXX."""
)
SUBDIVISION_HELP_TEXT_DEFAULT_EMAIL = """Enter a default email address for the company."""
SUBDIVISION_HELP_TEXT_COUNTIES = """Click on a county from the box below to add it to the list of Counties of Operation for this company represented in the box to the below-right.  To remove counties from the list of Counties of Operation, click on a county in the box to the below-right.  Click on "Submit" when finished."""
SUBDIVISION_HELP_TEXT_COUNTRIES = """Click on a country from the box below to add it to the list
of Countries of Operation for this company represented in the box to the below-right.  To remove
counties from the list of Countries of Operation, click on a country in the box to the
below-right.  Click on "Submit" when finished."""
SUBDIVISION_HELP_TEXT_ALTERNATIVE_NAMES = """If the company does business by one or more names ("Doing-Business-As" or "DBAs"), enter the alternative name of the company.  You may add additional alternative names by clicking on "Add another" below.  Click on "Submit" when finished."""
SUBDIVISION_HELP_TEXT_AUTO_ADD_DIRECT_RELATIONSHIPS = """Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted."""
SUBDIVISION_HELP_TEXT_IS_PUBLIC = """The allows the company to be viewed publicly."""
SUBDIVISION_HELP_TEXT_IS_ACTIVE = """Master Switch - This will remove them from everything"""
SUBDIVISION_HELP_TEXT_DISPLAY_RAW_ADDRESSES = """Set preference to view addresses as-entered rather than normalized by the geocoder.  Addresses will continue to be geocoded, but the results not displayed."""

HELP_TEXT_HQUITO_STATUS = """Set the H-QUITO accredited status based on EPA or Advanced Energy"""

HVAC_HQUITO_STATUS_SINGLE = """{company} HQUITO Status is {status}.  Please <a href="{url}" target="_blank">update</a> it with a valid status."""
HVAC_HQUITO_STATUS_MULTIPLE = """{company} HQUITO Status is {status}.  {company} is being used on multiple homes.  Please <a href="{url}" target="_blank">update</a> it with a valid status."""

HELP_TEXT_AUTO_SUBMIT_TO_REGISTRY = """Auto Submit home to RESNET Registry upon certification."""
