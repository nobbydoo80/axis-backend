"""Modern configurable messages for customer_eto app."""


from axis.messaging.messages import ModernMessage

try:
    from . import strings
except ImportError:
    from axis.customer_eto import strings


__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class NewETOAccountMessage(ModernMessage):
    content = strings.NEW_ETO_ACCOUNT_NOTIFICATION
    sticky_alert = True
    category = "ETO"
    level = "info"

    verbose_name = "Builder without Account"
    description = (
        "Sent when a builder has been associated to an Energy Trust project, but does not "
        "have an ETO Account Number assigned"
    )

    unique = True
    company_slugs = ["eto"]


class ETOAccountNumberAddedSingleMessage(ModernMessage):
    content = (
        strings.ETO_ACCOUNT_NUMBER_ADDED_BASE + strings.ETO_ACCOUNT_NUMBER_ADDED_NOTIFICATION_SINGLE
    )
    sticky_alert = True
    category = "ETO"
    level = "info"

    verbose_name = "Account Added for Project"
    description = (
        "Sent when an ETO account number has been added to Axis that "
        "allows a project in the Energy Trust program to proceed."
    )

    unique = True
    company_slugs = ["eto"]


class ETOAccountNumberAddedMultipleMessage(ModernMessage):
    content = (
        strings.ETO_ACCOUNT_NUMBER_ADDED_BASE + strings.ETO_ACCOUNT_NUMBER_ADDED_NOTIFICATION_MULTS
    )
    sticky_alert = True
    category = "ETO"
    level = "info"

    verbose_name = "Account Added for Projects"
    description = (
        "Sent when an ETO account number has been added to Axis that allows multiple "
        "projects in the Energy Trust program to proceed."
    )

    unique = True
    company_slugs = ["eto"]


class HomeInspectedMessage(ModernMessage):
    content = strings.HOME_REACHED_INSPECTED_STATUS
    sticky_alert = True
    category = "project"
    level = "info"

    verbose_name = "Project Inspected"
    description = "Sent when a project reaches the Inspected status for a program run."

    unique = True


class ProjectTrackerSuccessSubmissionMessage(ModernMessage):
    content = strings.ETO_FASTTRACK_SUBMISSION_SUCCESS
    sticky_alert = False
    category = "ETO"
    level = "success"

    verbose_name = "Project Tracker Success"
    description = "Sent when a Project Tracker entry has been successfully submitted"

    unique = True
    companies_with_relationship_or_self = ["eto"]


class ProjectTrackerFailedSubmissionMessage(ModernMessage):
    content = strings.ETO_FASTTRACK_SUBMISSION_FAILED
    sticky_alert = True
    category = "ETO"
    level = "error"

    verbose_name = "Project Tracker Failed"
    description = "Sent when a Project Tracker entry has been failed submission"

    unique = False
    company_slugs = ["eto", "peci"]
    company_admins_only = True


class EPSCalculatorDataNotValid(ModernMessage):
    content = strings.EPS_CALCULATOR_NOT_VALID
    category = "ETO"
    level = "warning"

    verbose_name = "EPS Calculator Invalid"
    description = "Sent when a projects EPS Calculator data is not valid yet."

    company_slugs = ["pivotal-energy-solutions"]


class WashingtonCodeCreditUploadComplete(ModernMessage):
    content = """Upload for Washington Code Credit is complete <a href='{url}'>{home}</a>."""
    category = "ETO"
    level = "info"

    verbose_name = "Washington Code Credit Upload is finished"
    description = "Sent when Washington Code Credit Upload has completed."

    companies_with_relationship_or_self = ["eto"]
