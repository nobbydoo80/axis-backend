"""strings.py: This is common strings to be used"""

from axis.company.strings import COMPANY_TYPES_MAPPING

__author__ = "Autumn Valenta"
__date__ = "8/28/12 3:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

# Names of certification requirements as shown to the user in a checklist form.
# Note that 'already_certified' and 'is_sampled_home' are situational and won't actually be shown
# to the user unless the requirement is already failing.
REQUIREMENT_NAME_ALREADY_CERTIFIED = "Certified Check"  # placeholer value only
REQUIREMENT_NAME_IS_SAMPLED_HOME = "Sampling Check"  # placeholder value only
REQUIREMENT_NAME_SAMPLED_HOUSE = "Validate sampling requirements"
REQUIREMENT_NAME_REQUIRED_QUESTIONS_REMAINING = "Submit required checklist responses"
REQUIREMENT_NAME_OPTIONAL_QUESTIONS_REMAINING = "Submit optional checklist responses"
REQUIREMENT_NAME_PERCENT_COMPLETION = "Receive 100% checklist completion"
REQUIREMENT_NAME_MODEL_FILE = "Upload a REM/Rate™ Data File"
REQUIREMENT_NAME_MODEL_DATA = "Associate Simulation Data"
REQUIREMENT_NAME_EPA_ACTIVE_BUILDER = "Active EPA Builder"
REQUIREMENT_NAME_REQUIRED_ANNOTATIONS = "Complete required annotations"
REQUIREMENT_NAME_PROGRAM_OWNER_ATTACHED = "Validate Program Sponsor association"
REQUIREMENT_NAME_BUILDER_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["builder"]
REQUIREMENT_NAME_PROVIDER_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["provider"]
REQUIREMENT_NAME_RATER_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["rater"]
REQUIREMENT_NAME_UTILITY_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["utility"]
REQUIREMENT_NAME_HVAC_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["hvac"]
REQUIREMENT_NAME_QA_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["qa"]
REQUIREMENT_NAME_ARCHITECT_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["architect"]
REQUIREMENT_NAME_DEVELOPER_REQUIRED = "Associate a %s" % COMPANY_TYPES_MAPPING["developer"]
REQUIREMENT_NAME_COMMUNITYOWNER_REQUIRED = (
    "Associate a %s" % COMPANY_TYPES_MAPPING["communityowner"]
)
REQUIREMENT_NAME_EPS_CALCULATOR = "Complete EPS calculator questions"
REQUIREMENT_NAME_APS_DOUBLE_PAYMENT = "Ensure only one APS Program"
REQUIREMENT_NAME_ETO_BUILDER_ACCOUNT_NUMBER = "Validate Builder has ETO Account"
REQUIREMENT_NAME_ETO_RATER_ACCOUNT_NUMBER = "Validate Rating Company has ETO Account"
REQUIREMENT_NAME_QA_COMPLETE_AND_PASSING = "QA is 100% and passing"
REQUIREMENT_NAME_GET_ETO_QA = "QA is 100% and passing"
REQUIREMENT_NAME_MULTIPLE_UTILITY_CHECK = "Associate a Utility(s)"
REQUIREMENT_NAME_APS_CALCULATOR = "Ensure APS can calculate incentive"
REQUIREMENT_NAME_NEEA_UTILITIES_SATISFIED = "Utility matches Heat Source type"
REQUIREMENT_NAME_RESNET_APPROVED_PROVIDER = "RESNET sampling approved provider"
REQUIREMENT_NAME_UNCOVERED_QUESTIONS = "Provide answers through sampling"
REQUIREMENT_NAME_HQUITO_ACCREDIATION = "Provide H-QUITO Accreditation status"
REQUIREMENT_NAME_NEEA_INVALID_PROGRAM = "Validate program selection"
REQUIREMENT_NAME_NWESH_INVALID_QA_PROGRAM = "Validate QA program selection"
REQUIREMENT_NAME_GET_GENERIC_SINGLEFAMILY_SUPPORT = "Validate Single Family"
REQUIREMENT_NAME_GET_REMRATE_FLAVOR_SUPPORT = "Validate REM/Rate® flavor"
REQUIREMENT_NAME_GET_GATING_QA_REQUIREMENT = "Ensure that QA is complete"
REQUIREMENT_NAME_FLOORPLAN_REMRATE_DATA_ERROR = "REMRate Data alignment check"
REQUIREMENT_NAME_FLOORPLAN_REMRATE_DATA_WARNING = "REMRate Data alignment check"
REQUIREMENT_NAME_FLOORPLAN_REMRATE_FILE = "REM data and REM .blg file match"
REQUIREMENT_NAME_RATER_OF_RECORD = "Assign Rater of Record"
REQUIREMENT_NAME_ENERGY_MODELER = "Assign Energy Modeler"
REQUIREMENT_NAME_FIELD_INSPECTORS = "Assign Field Inspector(s)"
REQUIREMENT_NAME_FLOORPLAN_SUBDIVISION_MATCHES_HOME_SUBDIVISION = (
    "Project's subdivision/MF development matches floorplan's subdivision association"
)
REQUIREMENT_NAME_GET_PROGRAM_CERTIFICATION_ELIGIBILITY = "Ensure program eligibility dates"
REQUIREMENT_NAME_GET_ETO_2017_ANSWER_SETS = (
    "Ensure at least one question is answered for each group."
)
REQUIREMENT_NAME_REMRATE_FLAVOR = "REMRate Flavor"
REQUIREMENT_NAME_REMRATE_VERSION = "REMRate Version"
REQUIREMENT_NAME_BUILT_GREEN_ANNOTATIONS = "Built Green Annotations"
REQUIREMENT_NAME_PNW_UTILITY_REQUIRED = "Verify Required Utilities"
REQUIREMENT_NAME_WATER_HEATER = "Verify water heater type"
REQUIREMENT_NAME_DUCT_SYSTEM_TEST = "Verify duct systems testing"
REQUIREMENT_NAME_VENTILATION_TYPE = "Verify ventilation type"
REQUIREMENT_NAME_BPA_ANNOTATION = "Verify BPA Annotations"
REQUIREMENT_NAME_STD_PROTOCOL_PERCENT_IMPROVEMENT = "Percent Improvement > 10%"

# Messages sent to the UI when program requirements have a failing status
ALREADY_CERTIFIED = "Project is already certified"
HAS_UNANSWERED_REQUIRED_QUESTIONS = "{n} unanswered question"
HAS_UNANSWERED_REQUIRED_QUESTIONS_PLURAL = "{n} unanswered questions"
HAS_UNANSWERED_OPTIONAL_QUESTIONS = "{n} unanswered optional question"
HAS_UNANSWERED_OPTIONAL_QUESTIONS_PLURAL = "{n} unanswered optional questions"
HAS_UNCOVERED_QUESTIONS = "{n} unprovided question from its sampleset"
HAS_UNCOVERED_QUESTIONS_PLURAL = "{n} unprovided questions from its sampleset"
MISSING_FLOORPLAN_FILE = "Need Floorplan with REM/Rate® data file"  # only applies to rem anyway
MISSING_FLOORPLAN_DATA = "Need Floorplan with {input_type} data"
MISSING_REMRATE_FILE = "Missing REM/Rate® Data File"
MISSING_REMRATE_DATA = "Missing REM/Rate® Data"
MISSING_EKOTROPE_DATA = "Missing Ekotrope Data"

MISSING_SIMULATION_DATA = "Missing Simulation Data"
MISSING_ERI_SCORE = "No default analysis found - unable to get ERI score"
ERI_SCORE_TOO_HIGH = "ERI Score of {eri:.0f} is higher than acceptable limit for program"
ERI_SCORE_TOO_LOW = "ERI Score of {eri:.0f} is higher than acceptable limit for program"

MISSING_TEST_HOME = "{rating_type} does not have a Test Project in sample set"
MISSING_SAMPLESET = "{rating_type} does not have a sample set identified"
MISSING_BUILDER_BASIC = "Missing %s" % COMPANY_TYPES_MAPPING["builder"]
HERS_SCORE_TOO_HIGH = "HERS score {hers} is too high for this Program {max}"
HERS_SCORE_TOO_LOW = "HERS score {hers} is too low for this Program {min}"
COMPANY_NOT_EPA_ACTIVE = "This {company_type} is not listed as active (or inactive) in the EPA database, indicating that the {company_type} has not taken the mandatory EPA orientation training or certified a project in the last 12-24 months. This project cannot be certified until the {company_type} status from the EPA changes to active (or inactive). Please contact energystarhomes@energystar.gov to determine steps required for activation."
FLOORPLAN_REMRATE_FILE = "Please export the data from REM again, then attach that data set and the correct REM .blg file to this project"

MISSING_REQUIRED_ANNOTATIONS = (
    "Before an inspection can begin the program sponsor requires {n} annotations."
)
PROGRAM_OWNER_NOT_ATTACHED = "Program owner {owner} has not agreed to be attached to project."

MISSING_BUILDER = (
    "Program {program} requires a %s be assigned to the project." % COMPANY_TYPES_MAPPING["builder"]
)
MISSING_BUILDER_RELATIONSHIP = "Program {program} requires an association to the builder.  {owner} does not have an association with the builder."

MISSING_PROVIDER = (
    "Program {program} requires a %s be assigned to the project."
    % COMPANY_TYPES_MAPPING["provider"]
)
MISSING_PROVIDER_RELATIONSHIP = "Program {program} requires an association to the provider.  {owner} does not have an association with any of the provider companies."

MISSING_RATER = (
    "Program {program} requires a %s be assigned to the project." % COMPANY_TYPES_MAPPING["rater"]
)
MISSING_RATER_RELATIONSHIP = "Program {program} requires an association to the rater.  {owner} does not have an association with any of the rating companies."

MISSING_UTILITY = (
    "Program {program} requires a %s be assigned to the project." % COMPANY_TYPES_MAPPING["utility"]
)
MISSING_UTILITY_RELATIONSHIP = "Program {program} requires an association to the utility.  {owner} does not have an association with any of the utility companies."

MISSING_HVAC = (
    "Program {program} requires a %s be assigned to the project." % COMPANY_TYPES_MAPPING["hvac"]
)
MISSING_HVAC_RELATIONSHIP = "Program {program} requires an association to the HVAC.  {owner} does not have an association with any of the HVAC companies."

MISSING_QA = (
    "Program {program} requires a %s be assigned to the project." % COMPANY_TYPES_MAPPING["qa"]
)
MISSING_QA_RELATIONSHIP = "Program {program} requires an association to the QA organization.  {owner} does not have an association with any of the QA companies."

MISSING_ARCHITECT = (
    "Program {program} requires a %s be assigned to the project."
    % COMPANY_TYPES_MAPPING["architect"]
)
MISSING_ARCHITECT_RELATIONSHIP = "Program {program} requires an association to the Architect organization.  {owner} does not have an association with any of the Architect companies."

MISSING_DEVELOPER = (
    "Program {program} requires a %s be assigned to the project."
    % COMPANY_TYPES_MAPPING["developer"]
)
MISSING_DEVELOPER_RELATIONSHIP = "Program {program} requires an association to the Developer organization.  {owner} does not have an association with any of the Developer companies."

MISSING_COMMUNITYOWNER = (
    "Program {program} requires a %s be assigned to the project."
    % COMPANY_TYPES_MAPPING["communityowner"]
)
MISSING_COMMUNITYOWNER_RELATIONSHIP = "Program {program} requires an association to the Community organization.  {owner} does not have an association with any of the Community companies."


MISSING_ETO_CALCULATION_REQUIREMENTS = (
    "Missing required checklist data points ({missing}).{other_errors}"
)
MISSING_RATER_OF_RECORD = "Statistics will be unattributed to the rater unless assigned."
MISSING_ENERGY_MODELER = (
    "Statistics will be unattributed to the rater unless Energy Modeler assigned."
)
MISSING_FIELD_INSPECTOR = (
    "Statistics will be unattributed to the rater unless Field Inspector assigned."
)

DUPLICATE_APS_PROGRAMS = (
    "Program {program} has already been assigned.  You cannot assign {new_program} to it."
)
LEGACY_APS_HOME = (
    "This project already has a legacy payment on it.  You cannot assign {new_program} to it."
)
ETO_BAD_REMRATE_TYPE = 'You must use correct REM/Rate® export identified by "UDRH As Is Building"'
MISSING_ETO_ACCOUNT_NUMBER = (
    "Program requires the {company_type} to have an ETO Account number.  "
    "Please contact Energy Trust to get this added."
)
MULTIPLE_SPECIFIC_UTILITY = "More than one specific {utility_type} attached to project"
NO_OPTIMAL_APS_PROGRAM = "Unable to identify an optimal program with a HERS score of {hers:.0f}."
NON_OPTIMAL_APS_PROGRM = "With a hers score of {hers} you should use {program} program."

APS_MULTIPLE_PROGRAMS_NOT_ALLOWED = "Only one APS program can be assigned to this project."
APS_THERMOSTAT_PROGRAM_NOT_SUPPORTED = "APS program not yet supported for this project."

NEEA_HEAT_TYPE_NOT_PROVIDED = "Heat Source has not yet been provided."
NEEA_ELECTRIC_UTILITY_REQUIRED = (
    "Heat Source '{heat_source}' requires that an electric utility be assigned."
)
NEEA_GAS_UTILITY_REQUIRED = "Heat Source '{heat_source}' requires that a gas utility be assigned."
NEEA_ELECTRIC_AND_GAS_UTILITIES_REQUIRED = (
    "Heat Source '{heat_source}' requires that both an electric and gas utility be assigned."
)
NEEA_INVALID_PROGRAM = (
    "{program} was closed on July 1 2015.  Please change this to the NEEA 2015 ENERGY STAR Program."
)

UNAPPROVED_RESNET_PROVIDERS = (
    "Program {program} requires sampled projects to be certified by "
    "RESNET Sampling approved providers. {providers} are not approved."
)

INVALID_HVAC_COMPANY = "{company} does not appear to be a valid HVAC company"

THERMOSTAT_INCONSISTANCY = (
    "Checklist indicates a smart thermostat, yet REM/Rate has a programmable thermostat"
)

UNKNOWN_HQUITO_STATUS = (
    "{company} is not listed as H-QUITO accredited for {program} certification. "
    "The Program Sponsor will be notified to review and provide next steps to ensure proper H-QUITO accreditation. "
    "Projects must have an H-QUITO accredited contractor for certification."
)

FAILING_HQUITO_STATUS = (
    "{company} is not listed as H-QUITO accredited for {program} certification. Projects must "
    "have an H-QUITO accredited contractor for certification. Please work with your HVAC "
    "contractor to complete the steps to ensure proper H-QUITO accreditation. The Program Sponsor "
    "will be notified and will update the contractor’s H-QUITO status once fully accredited. "
    "Details on enrollment can be found on the ENERGY STAR Homes website at http://1.usa.gov/1PQyltv"
)
ONLY_SINGLE_FAMILY_ALLOWED = """Only single family projects are allowed in {program}"""
INVALID_REMRATE_FLAVOR = """Program requires REM/Rate® flavor {required_flavor} to be used.  Please re-export using the correct version of REM/Rate®"""
EKOTROPE_HERS_ANALYSIS_FAILED_TO_IMPORT = (
    """The analysis for Ekotrope HousePlan {houseplan_id} has failed to import to Axis."""
)
EKOTROPE_HERS_IMPORT_UNDER_WAY = (
    """Import of HERS data from Ekotrope HousePlan {houseplan_id} is still processing."""
)

NWESH_NEW_HOMES_PROGRAM_REM_VERSION_REQUIREMENT = (
    """Program {program} only allows rating data from REM/Rate™ versions {versions}."""
)
NWESH_NEW_HOMES_PROGRAM_EKOTROPE_VERSION_REQUIREMENT = (
    """Program {program} only allows rating data from Ekotrope version(s) {allowed_versions}."""
)
NWESH_NEW_HOMES_PROGRAM_REM_FLAVOR_REQUIREMENT = (
    """Program {program} only allows rating data from the {accepted_flavor} version of REM/Rate™."""
)

REQUIRED_QA_NOT_STARTED = "QA is required and has not yet started"
QA_IN_PROGRESS = "QA has started but is not yet complete"

PROGRAM_TOO_EARLY = "{program} is not yet eligible for certification."
PROGRAM_TOO_LATE = (
    "{program} is no longer eligible for certification.  Certification closed on {date}"
)

PERCENT_IMPROVEMENT_TOO_LOW = "Project total improvement must be at least 10% in order to qualify"
BUILDER_INCENTIVE_TOO_LOW = "Project must meet EPS % above code requirements and receive service from an Energy Trust utility"

COMPANY_ASSOCIATED_WITH_HOME_STATUS = """
    <a target="_blank" href="{assigning_company_url}">{assigning_company}</a> has associated
    <a target="_blank" href="{assigned_company_url}">{assigned_company}</a> to project
    <a target="_blank" href="{home_url}">{home}</a>
"""

HOME_VERBOSE_NAME_LOT_NUMBER = "Lot number"
HOME_VERBOSE_NAME_STREET_LINE1 = "Street Address"
HOME_VERBOSE_NAME_STREET_LINE2 = "Unit number (if applicable)"
HOME_VERBOSE_NAME_CITY = "City"
HOME_VERBOSE_NAME_ZIPCODE = "ZIP Code"

HOME_HELP_TEXT_LOT_NUMBER = """Enter the lot number of the project (typical for a "production builder" in a subdivision or development of multiple projects), or leave blank or "N/A" if unknown or not applicable."""
HOME_HELP_TEXT_STREET_LINE1 = (
    """Enter the street number and street name of the project (e.g. 123 Main St)."""
)
HOME_HELP_TEXT_STREET_LINE2 = """Enter the unit number (where multiple dwelling units share a common street address), or leave blank if not applicable."""
HOME_HELP_TEXT_CITY = """Type the first few letters of the name of the city the project is located in and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database."""
HOME_HELP_TEXT_ZIPCODE = """Enter the 5-digit ZIP Code of project."""
HOME_HELP_TEXT_CONSTRUCTION_STAGE = """Enter construction stage if known or desired, or leave blank.  To add custom construction stages for your company, click <here> for instructions."""
HOME_HELP_TEXT_SUBDIVISION = """If this project is in a Subdivision/MF Development of projects all built by the same project builder, then type the first few letters of the name of the subdivision and select the correct subdivision from the list presented.  If the correct subdivision is not available, click "Add New" to add a subdivision to the database.  If this project is not part of a subdivision/MF development, leave this field blank."""
HOME_HELP_TEXT_HOME_BUILDER = """Type the first few letters of the name of the Builder and select the correct company from the list presented.  If the correct company is not available, click <here> to add Builder company associations."""
HOME_HELP_TEXT_PROVIDERS = """Type the first few letters of the name of the Provider for this project and select the correct company from the list presented.  If the correct company is not available, click <here> to add Rating Provider company associations."""
HOME_HELP_TEXT_HVAC_CONTRACTORS = """Type the first few letters of the name of the HVAC Contractor for this project and select the correct company from the list presented.  If the correct company is not available, click <here> to add HVAC Contractor company associations.  Note that you may add both the HVAC design and installation company if applicable."""
HOME_HELP_TEXT_QA_QC_COMPANIES = """Type the first few letters of the name of the QA/QC Company(s) (if separate from the Rater's QA Provider) for this project and select the correct company(s) from the list presented.  If the correct company(s) is not available, click <here> to add QA/QC Company associations."""
HOME_HELP_TEXT_PROGRAM_SPONSORS = """Type the first few letters of the name of the Program Sponsor(s) for this project and select the correct company(s) from the list presented.  If the correct company(s) is not available, click <here> to add Program Sponsor company associations."""
HOME_HELP_TEXT_UTILITY_COMPANIES = """Type the first few letters of the name of the Utility Company(s) for this project and select the correct company(s) from the list presented.  If the correct company(s) is not available, click <here> to add Utility Company associations.  Note that you may add both the electric and gas utility if applicable."""
HOME_HELP_TEXT_GENERAL_COMPANIES = """Type the first few letters of the name of General Companies you wish to associate to this project and select the correct company(s) from the list presented.  If the correct company(s) is not available, click <here> to add General Companies company associations."""
HOME_HELP_TEXT_USERS = """Type the fist few letters of names of individuals you wish to associate with this project and select the correct individual from the list presented."""

PROGRAM_HELP_OWNER = "Assign the company responsible for data collection"

EEP_PROGRAM_HOME_STATUS_FORM_ADDITION_TYPE = (
    """Click to add data to the project such as an energy model file or data set."""
)
EEP_PROGRAM_HOME_STATUS_FORM_EEP_PROGRAM = (
    "Select the program from the list presented. "
    "You may add multiple programs to a project using "
    "the 'Add new program' button below. "
    "You may customize the list of programs presented "
    "on the Tasks -> Programs page."
)
EEP_PROGRAM_HOME_STATUS_FORM_RATER_OF_RECORD = (
    """The name specified will be used to track the number of ratings by individual."""
)
EEP_PROGRAM_HOME_STATUS_FORM_RATING_FIELD_INSPECTOR = (
    """The name(s) specified will be used to track the number of projects by individual."""
)

DOCUMENTS_TAB_DOCUMENTS = """Click on "Select file" and select a file from the file browser.  Once selected, click on "Change" to select a new file or "Remove" to delete the file."""
DOCUMENTS_TAB_DECSRIPTION = """Enter a description of the file if desired."""
DOCUMENTS_TAB_PUBLIC = """Click on the selection box to make this document visible to users from other associated companies.  Unselect the selection box to keep the document private to your company's users."""
DOCUMENTS_TAB_REMOVE = (
    """Click the "Remove" button below and click on "Submit" to remove the document."""
)

FAILED_CERTIFICATION_INCOMPLETE_PERCENTAGE = """The program requirements are only {completion:.2f}% complete. This project was not certified."""
FAILED_CERTIFICATION_NOT_ALLOWED_TO_CERTIFY = (
    """Only providers can certify this program. This project was not certified."""
)
INELIGIBLE_FOR_NEXT_PHASE = """Project is not eligible for the next phase"""
FAILED_GATING_QA_REQUIREMENT = """This program has a gating QA requirement which hasn't been met"""

HOMESTATUS_EXPORT_COMPLETED = """Project Export has completed.  Filters used: {filters}"""
HOMESTATUS_REPORT_COMPLETED = """Project Report has completed.  Filters used: {filters}"""

# BULK Uploads
INVALID_RATING_TYPE = """Invalid Rating Type '{rating_type}' should be one of the following: Confirmed Rating, Sampled House, or Sampled Test House"""
FOUND_RATING_TYPE = """Using Rating Type of {rating_type}"""

MISSING_LOT_NUMBER = """Lot Number was not provided"""
INVALID_LOT_NUMBER = (
    """Lot Number '{lot_number}' is too long.  It must be less than 16 characters."""
)
MISSING_STREET_LINE1 = """Street Line 1 was not provided"""
MISSING_ZIP_CODE = """ZIP Code was not provided"""
MISSING_CITY = """City was not provided either directly or via the subdivision"""
MISSING_COUNTY = """County was not provided either directly or via the subdivision"""
MISSING_STATE = """State was not provided either directly or via the subdivision"""
CITY_SUBDIVISON_MISMATCH = (
    """City provided '{city}' does not match subdivision city {subdivision_city}"""
)
COUNTY_SUBDIVISON_MISMATCH = (
    """County provided '{county}' does not match subdivision city {subdivision_county}"""
)
STATE_SUBDIVISON_MISMATCH = (
    """State provided '{state}' does not match subdivision state {subdivision_state}"""
)
MISSING_SUBDIVISION_OR_BUILDER = (
    """You must provide either a subdivision or a builder (for custom projects)"""
)
HOME_MULTIFAMLY_MISMATCH = """Multi-family subdivision <a href="{url}">{subdivision}</a> requires only multi-family projects be assigned to it"""
ADDRESS_USED_MULTIPLE_SUBS = """Address is used in multiple Subdivisions/MF Developments"""
CUSTOM_HOME_ERROR = """Existing address used is a custom project, but builder was not specified"""
EXISTING_HOME = """Using existing project <a href='{url}'>{home}</a>"""
EXISTING_HOME_ID = """Using existing project ID: {home_id}"""
EXISTING_HOME_CITY_ERROR = """Existing project <a href='{url}'>{home}</a> does not have the same city {city} as upload dictates {file_city}"""
MULTIPLE_HOMES_FOUND = """Multiple projects found for address provided"""
HOME_USED_CREATE = """{create} {custom}{multifamily}<a href='{url}'>{home}</a> project {subdivision}with a{confirmed} address"""

PROGRAM_ON_HOME_IN_USE = (
    """{company} has already registered {program} with <a href='{url}'>{home}</a>"""
)
PREVIOUSLY_DEFINED_FLOORPLAN = """The floorplan '{floorplan}' does not match the previously defined '{prior_floorplan}' on <a href='{url}'>{home}</a>"""
USING_PREVIOUSLY_DEFINED_FLOORPLAN = """The previously defined floorplan '{prior_floorplan}' will be used on <a href='{url}'>{home}</a> as none was provided"""

PREVIOUSLY_DEFINED_RATING_TYPE = """The rating type '{rating_type}' does not match the previously defined '{prior_rating_type}' on <a href='{url}'>{home}</a>"""
PREVIOUSLY_DEFINED_SAMPLESET = """The sampleset '{sampleset}' does not match the previously defined '{prior_sampleset}' on <a href='{url}'>{home}</a>"""
NEWLY_ADDED_SAMPLESET = """Program {program} on <a href='{url}'>{home}</a> previously did not have a sampleset now it's being defined {sampleset}"""
EXISTING_PROGRAM_ALREADY_CERTIFIED = (
    """<a href='{url}'>{home}</a> with {program} has already been certified"""
)
NOT_ELIGIBLE_FOR_CERTIFICATION = """<a href='{url}'>{home}</a> with {program} is not eligible for certification.  Check the program requirements on the project detail page."""

INVALID_IS_BILLABLE = """Unknown 'is_billable' value '{is_billable}'"""
MULTIPLE_HOME_STATS_FOUND = (
    """Multiple programs {program} have been added to project <a href='{url}'>{home}</a>"""
)
STAT_USED_CREATE = """{create} binding for {program} to <a href='{url}'>{home}</a>"""

# A few homestatus form errors
INCENTIVES_ALREADY_RECORDED = (
    """You cannot modify this Project as Incentives have been recorded against it."""
)
PRESCRIPTIVE_REQUIRES_MULTIFAMILY = """As of July 1, 2014, the Prescriptive Path program is available only for multi-family residences.  If this is a multi-family residence, please select the "Multi-family" checkbox in the address information above, otherwise select the Performance Path program to continue."""
PRESCRIPTIVE_2015_REQUIRES_MULTIFAMILY = """The program selected is available only for multi-family residences. If this is a multi-family residence, please select the "Multi-family" checkbox in the address information above, otherwise select a Performance Path program to continue."""
PERFORMANCE_REQUIRES_NON_MULTIFAMILY = """The Performance Path program is available only for single-family residences.  If this is a single-family residence, please unselect the "Multi-family" checkbox in the address information above, otherwise select the Prescriptive Path program to continue."""
BAD_NWESH_QA_PROGRAM = (
    """The QA Program you are using should be one of {qa_programs} based on the program {program}"""
)
GENERIC_REQUIRES_MULTIFAMILY = """This program is available only for multi-family residences. If this is a multi-family residence, please select the "Multi-family" checkbox in the address information above."""
GENERIC_REQUIRES_SINGLEFAMILY = """This program is available only for single-family residences. If this is single-family residence, please unselect the "Multi-family" checkbox in the address information above."""

# Certification email Strings

# Program Text
NEEA_DEFAULT_PROGRAM_TEXT = """These projects have been certified by your Provider. Click on the project address to
        navigate to the project in AXIS. ENERGY STAR® Labels must be printed and attached on or near the breaker
        box of each project. Certificates may also be generated at this time. To access the label and certificate
        feature in Axis, go to the Reports menu drop down and select ENERGY STAR Labels or Project Certificates
        from the “Printing” section. Contact your Provider with questions about the project certification.
        Contact the AXIS Support Team with questions about generating the label and certificate.
        Feel free to contact the Northwest ENERGY STAR Projects program with any other questions."""
NEEA_EFFICIENT_HOMES_PROGRAM_TEXT = """These projects have met the requirements of NEEA’s Efficient Projects Pilot and have
        been completed by CLEAResult QA. Click on the project address to navigate to the project in AXIS.
        Feel free to contact the NEEA Efficient Projects Pilot team with questions (terra.bell@clearesult.com)."""
