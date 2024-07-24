""" Hard-coded messages that get sent to the front-end. """


__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

UNABLE_TO_TRANSITION_HOME = (
    """Unable to transition home {home_url} to {tstate} from {ostate}; This is not allowed."""
)
UNABLE_TO_TRANSITION_HOME_NO_HOME = (
    """Unable to transition from {ostate} to {tstate}. This is not allowed."""
)
UNABLE_TO_REVERT_HOME_NO_HOME = """Unable to revert to Received from {ostate}"""

ERROR_NO_CHECK_NUMBER = """In order to mark this paid you must provide a Check Number."""
ERROR_NO_PAID_DATE = """You must provide a Paid Date in addition to the check number."""
ERROR_PAID_DATE_BEFORE_CHECK_REQUEST_DATE = (
    """Your paid date is earlier than the check request date."""
)
ERROR_DATE_IN_FUTURE = """You can't request a date more than 3 days from now."""
ERROR_CHECK_NUMBER_ALREADY_EXISTS = (
    """The check number you provided has already been used in invoice(s): {}"""
)

ERROR_NO_HOMES_SUPPLIED = (
    """You need to select some homes. Simply click the homes you want to  pay on."""
)
ERROR_MULTIPLE_BUILDERS = """You have multiple home builders ({}, {}) selected.  Only one  builder is allowed per check request."""
ERROR_EXCEEDED_AVAILABLE_LOTS = """You will have exceeded the available lots in {} ({}) by {}.  Please select fewer homes or increase the total lots on the builder agreement. Note this accounts for both pending and paid status"""

ERROR_NO_BUILDER_ORG_OR_SUBDIVISION = """You must select a builder or a subdivision or both!"""
ERROR_BUILDER_ORG_DOES_NOT_REPRESENT_SUBDIVISION = """{} does not represent {} - Did you mean {}?"""
ERROR_START_END_DATE_IN_FUTURE = (
    """Sorry. I can't predict the future.  Your start date is later than today."""
)
ERROR_END_DATE_BEFORE_START_DATE = """Sorry.  Your end date is before your start date"""

ERROR_NO_ANNOTATION = """You must provide a message!"""

INVENTIVE_DISTRIBUTION_CUSTOMER_CHANGED_CONFIRMATION = """Changing the customer will affect payments for all homes in this Incentive Distribution. Do you wish to continue?"""


FAILED_IPP = """{company} has REJECTED {num_homes} home{plural} from payment on {date}.  Please review the <a href="{url}">Incentive Payment Failure Report</a> for details."""
CORRECTED_IPP = """{company} has corrected {num_homes} home{plural} from payment on {date}.  Please review the <a href="{url}">Pending Incentive Payment Report</a> for details."""
APPROVED_IPP = """{company} has approved {num_homes} home{plural} for payment on {date}."""
