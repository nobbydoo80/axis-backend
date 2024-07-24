"""strings.py: Hard-coded messages that get sent to the front-end. """

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# Question type validation errors for submitted answers
VALUE_NOT_AN_INTEGER = """A whole number is required."""
VALUE_NOT_A_FLOAT = """A decimal number is required."""
VALUE_TOO_SMALL = """The value should be at least {minimum}."""
VALUE_TOO_LARGE = """The value should be no larger than {maximum}."""
INVALID_QUESTION_CHOICE = """This is not a valid choice. Valid choices are %s"""
QUESTION_CHOICE_REQUIRES_COMMENT = """This choice requires a comment be provided."""
UNKNOWN_DATE_FORMAT = """Unknown date format; best format is YYYY-MM-DD."""
UNKNOWN_DATETIME_FORMAT = """Unknown datetime format; best format is YYYY-MM-DD HH:MM."""
UNKNOWN_KVFLOATCSV_VALUE = """Unknown value type for for '{key}' (item {i}).  Expecting format such as 'Bedroom: 2.0,Front: 2.3'."""
VALUE_NOT_A_CSV_LIST = """Unknown format for Comma Separated Value."""
VALUE_NOT_A_KVFLOATCSV_LIST = """Unknown format for Key Value (float) Comma Separated list. This should look like this <key>:<number>,<key2>:<number>,,,,"""

# Bulk uploads
# Errors
ALLOW_OVERWRITE = """Allowing overwrites for answers."""
MISSING_CORE = """Missing items {items}"""
SUBMIT_MSG = """{user} submitted {document} for processing with task [{task_id}]"""
BAD_XLSX = """{document} does not appear to be a Microsoft Excel file in XLSX format."""
XLS_LOAD_ERROR = """Unable to load {document}; Error: {error}"""
XLS_BAD_COLUMNS = """Unable to identify columns in {document}; Error {error}"""
XLS_MISSING_COLUMNS = """{document} is missing required columns: {missing}"""
XLS_NO_RESULTING_DATA = """{document} contains no home data to process.."""
NO_HEADERS = """Document ({document}) has no column headers. And could not be processed."""
STAGE_ONE_COMPLETE = """Stage one: file validation complete"""
STAGE_TWO_COMPLETE = """Stage two: home validation complete"""
STAGE_THREE_COMPLETE = """Stage three: home processing complete"""
STAGE_TWO_PCT_INCREMENT = """{stat} Stage 2: home validation complete"""
INVALID_US_STATE = """State '{state}' is not a State or may be misspelled."""
NO_US_STATE = """Unable to determine US State"""
INVALID_CERT_DATE = """Unable to determine the certification date from '{date}'. Please use a common date format, such as MM/DD/YYYY."""
UNIDENTIFIABLE_CONSTRUCTION_STAGE = (
    """Unable to identify Construction Stage '{stage}'. Valid stages are: {valid_stages}"""
)
CONTSRUCTION_STAGE_AFTER_REPORTED = (
    """Existing Construction Stage '{ostage}' comes after reported construction stage '{tstage}'"""
)
ADDING_HOME_EXCEEDS_SAMPLESET = """Sample Set <a href='{url}'>{sampleset}</a> already has 7 homes. This home must be put in a different Sample Set."""
FAILS_AUDIT = """Sample Set '{sampleset}' does not pass audit!"""
HOME_MULTIFAMLY_MISMATCH = """Multi-family subdivision <a href="{url}">{subdivision}</a> requires only multi-family homes be assigned to it"""
SAMPLESET_FAILS_CAN_BE_CERTIFIED = """Sampleset '{sampleset}' has homes that are not able to be certified. Certification for {home} may not continue until all homes can be certified."""
CERTIFY_ERROR = """Certify Error : {error}"""
NO_BUILDER_NO_SUBDIVISION = """Axis could not identify a Builder. Please provide a valid Axis Builder or a valid Axis Subdivision."""

# warnings
CERTIFICATION_DATE_AND_CONSTRUCTION_STAGE = """You provided a construction stage and a certification date. The certification date will override the construction stage."""
SAMPLESET_PROGRAM_DOES_NOT_MATCH_HOME_PROGRAM = """Program {oprogram} specified on {home} does match {tprogram} specified for Sample Set {sampleset}"""
MULTIPLE_CERT_DATES = """Sample Set '{sampleset}' has multiple Sample Test Homes with different certification dates. This is not allowed."""
UNABLE_TO_CERTIFY_WITH_DATE_ONLY_HOME_IN_BATCH = """Unable to certify Sample Set '{sampleset}' with date {date}. The Sample Test Home has no certification date."""
UNABLE_TO_CERTIFY_INVALID_USER = (
    """{user} is not allowed to certify program on home <a href='{url}'>{home}</a>"""
)
CERT_DATE_DOES_NOT_MATCH_PRIOR_DATE = """Certication date '{cert_date}' of {home} does not match preexisting certification date '{test_cert_date}' of Sample Test Home {test_home}. You must use '{test_cert_date}'"""
BUILDER_SUBDIVISION_BUILDER_MISMATCH = """Builder provided '{builder}' does not match Subdivision builder '{sub_builder}'. Using '{sub_builder}'"""

# info
DEPRECATED_HEADER_RATING_TYPE = """The 'Rating Type' header is no longer required.  Certified Ratings will be assigned automatically during certification, and Sampled Houses and Sampled Test Houses will be detected when a sample set is given and checklist data is available for a home."""
USER_SUBMITTED_DOCUMENT_FOR_PROCESSING = (
    """{user} submitted {document} for processing wiht task {task} [{task_id}]"""
)
ADDING_UPDATING_TYPE = """Added {added} {type} and updated {updated} {type}."""
COMPLETED_PROCESSING = """Completed processing {document} for {company}"""
SKIPPING_PROCESSING = """Skipping any further processing of {home}"""
UPDATE_SUBDIVISION_RELATIONSHIPS_DIFFERENT_FROM_HOME = (
    """{stat} Updating subdivision relationships as they differ from the home."""
)
SKIPPING_CERTIFIED_HOME = """Skipping previously certified home. <a href='{url}'>{home}</a>"""
UPDATED_SAMPLING_RECORDS = """Updated {results} Sampling accounting records."""
CERTIFIED_SAMPLED_HOME = """Certified Sampled Home <a href='{url}'>{home}</a> on {date}"""
CERTIFIED_HOME = """Certified <a href="{url}">{home}</a> on {date}."""
USING_SAMPLESET = """Using Sample Set {sampleset}."""
ALREADY_HANDLED = """Home <a href="{home_url}">{home}</a> has been certified in connection with the sampleset <a href="{sampleset_url}">{sampleset}</a>. """

OVERWRITE_ANSWER = (
    """Overwriting existing answer '{answer}' for question '{question}' with '{new_answer}'"""
)
REUSE_ANSWER = (
    """No new answer given, reusing existing answer '{answer}' for question '{question}'"""
)
BULK_ANSWERING_SUMMARY = """Added {created} answers, discarded {overwritten} answers, and reused {reused} answers for {home}"""

# Form help texts
UPDATE_EXISTING_ANSWERS_HELP_TEXT = """When an item with an answer on the uploaded spreadsheet has already been answered for the home in Axis, this option will replace the answer already in Axis with the answer on the spreadsheet."""

CONSTRUCTION_STAGE_ORDER = (
    "Existing Construction Stage '{stage}' comes after reported construction stage '{new_stage}'"
)
INVALID_CONSTRUCTION_STAGE = "You provided a construction stage and a certification date.  The certification date will override the construction stage."
EXCEED_SAMPLESET_SIZE = "Adding home {home} to existing Sample Set <a href='{url}'>{sampleset}</a> will exceed the maximum of 7 homes. This home must be put in a different Sample Set."
ALREADY_COMPLETE = "{program} on <a href='{url}'>{home}</a> was already completed and certified. Skipping this home."
