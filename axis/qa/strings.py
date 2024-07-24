"""strings.py: Django qa"""

import logging

__author__ = "Steven Klass"
__date__ = "12/26/13 1:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

QA_RECOMMENDED_MSG = (
    "The {program} program has been associated with "
    '<a href="{home_detail}">{home}</a>. {qa_company} is currently below the '
    "{program} percentage threshold of {percent:.1%}. Click "
    '<a href="{action_url}">here</a> to add QA to this home.'
)
QA_RECOMMENDED_CUSTOMER_MSG = 'QA has been requested on <a href="{home_detail}">{home}</a>.'

QA_IS_GATING_CERTIFICATION = (
    'All requirements for <a href="{home_detail}">{home}</a> have been '
    "completed.  QA is currently gating the certification of the home.  "
    "Please complete QA on this home so it can be certified."
)
QA_HAS_BEEN_NOTIFIED_MSG = (
    "{qa_company} has been notified they are gating the certification of "
    '<a href="{home_url}" target="_blank">{home}</a>.'
)

QA_HAS_BEEN_ADDED_MSG = (
    '<a href="{home_url}" target="_blank">{home}</a> has been selected for {qa_type} QA by '
    "{qa_company}."
)

MISSING_REQUIRED_NOTE = "{state_description} requires that you include a note."
MISSING_RESULT = "When changing state to complete you must include a final result."
INCORRECT_STATE_FOR_COMPLETE = "Assigning a result is only allowed when transitioning to complete."
QA_CORRECTION_RECEIVED = (
    "{company} has responded to information in the QA of {obj_type} "
    '<a href="{obj_edit}">{obj}</a>.  Please click <a href="{action_url}">'
    "here</a> to continue QA."
)
QA_SUBDIVISION_HAS_HOME_ADDED = """A project has been added to <a href="{url}"
target='_blank'>{subdivision}</a>, which will require the addition of QA for {program}."""
QA_SUBDIVISION_GATING_HOMES = (
    """<a href="{url}">{subdivision}</a> is gating certification for {program} projects."""
)

START_DATE_FILTER_FIELD_TOOLTIP = (
    """ Set a date range to filter the table below by home certification date """
)

FILE_QA_CERTIFIED_HOMES_TOOLTIP = """ Homes certified in the specified date range """
FILE_QA_QA_PENDING_TOOLTIP = """ Homes that entered Pending QA in the specified date range """
FILE_QA_QA_IN_PROGRESS_TOOLTIP = (
    """ Subset of certified homes with an existing QA status other than Complete """
)
FILE_QA_QA_COMPLETED_TOOLTIP = """ Subset of certified homes that have had QA completed """
FILE_QA_FIRST_TIME_PASS_TOOLTIP = """ Homes that completed QA without requiring correction """
FILE_QA_REQUIRED_CORRECTIONS_TOOLTIP = """ Homes that completed QA but DID require correction """
FILE_QA_TOTAL_QA_TOOLTIP = """ Total that have had QA
completed - the running QA percentage for the specified date range """

# FIELD_QA_RATING_COMPANY_TOOLTIP = """  """
FIELD_QA_RATER_OF_RECORD_TOOLTIP = (
    """ Field inspectors are listed under each Rater where applicable """
)
FIELD_QA_CERTIFIED_HOMES_TOOLTIP = """ Homes certified in the specified date range;
includes certifications by Rater, along with the subset of Rater homes inspected by each RFI """
FIELD_QA_QA_IN_PROGRESS_TOOLTIP = (
    """ Subset of certified homes with an existing QA status other than Complete """
)
FIELD_QA_QA_COMPLETED_TOOLTIP = """ Subset of certified homes that have had QA complete """
FIELD_QA_FIRST_TIME_PASS_TOOLTIP = """ Homes that completed QA without requiring correction """
FIELD_QA_REQUIRED_CORRECTIONS_TOOLTIP = """ Homes that completed QA but DID require correction """
FIELD_QA_TOTAL_QA_TOOLTIP = """ Total that have had QA
completed - the running QA percentage for the specified date range """

PROGRAM_METRICS_CERTIFIED_HOMES_TOOLTIP = """ Homes certified in the specified date range """
PROGRAM_METRICS_FILE_QA_COMPLETE_TOOLTIP = (
    """ Subset of certified homes with a QA status of Complete """
)
PROGRAM_METRICS_FIELD_QA_COMPLETE_TOOLTIP = (
    """ Subset of certified homes with a QA status of Complete """
)
PROGRAM_METRICS_FILE_QA_FIRST_TIME_PASS_TOOLTIP = (
    """ Homes that completed QA without requiring correction """
)
PROGRAM_METRICS_FILE_QA_TOTAL_QA_TOOLTIP = """Total that have had QA completed -
the running QA percentage for the specified date range """
PROGRAM_METRICS_FIELD_QA_FIRST_TIME_PASS_TOOLTIP = (
    """ Homes that completed QA without requiring correction """
)
PROGRAM_METRICS_FIELD_QA_TOTAL_QA_TOOLTIP = """ Total that have had QA completed - the running QA percentage for the specified date range """
