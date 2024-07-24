"""Modern configurable messages for customer_neea app."""


from axis.messaging.messages import ModernMessage
from . import strings

__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class NEEAMissingAssociationWithCompanyType(ModernMessage):
    """Modern message sent to NEEA"""

    title = "Missing Association"
    content = strings.NEEA_MISSING_ASSOCIATION
    category = "associations"
    level = "info"

    verbose_name = "Required Association Missing"
    description = (
        "Sent when a NEEA program is assigned to a project, and the Project has "
        "associations with Companies NEEA does not."
    )

    unique = True
    company_slugs = ["neea"]


class NeeaUnapprovedUtilityMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = strings.NEEA_NO_UTILITY_RELATIONSHIP
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "No Utility association"
    description = "Sent if no association exists between NEEA and a project's Utility."

    unique = True
    companies_with_relationship = ["neea"]


class NeeaUnapprovedBuilderMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = strings.NEEA_NO_BUILDER_RELATIONSHIP
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "No Builder association"
    description = "Sent if no association exists between NEEA and a project's Builder."

    unique = True
    companies_with_relationship = ["neea"]


class NeeaUnapprovedHvacMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = strings.NEEA_NO_HVAC_RELATIONSHIP
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "No HVAC association"
    description = "Sent if no association exists between NEEA and a project's HVAC."

    unique = True
    companies_with_relationship = ["neea"]


class NeeaHomeStatusExportCompletedMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = """NEEA Project Export has completed.  Filters used: {filters}"""
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "NEEA Project Export"
    description = "Sent when a Project export is prepared and ready for download."

    companies_with_relationship_or_self = ["neea"]


class NeeaHomeUtilityStatusRawExportCompletedMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = """Project Utility Status Export has completed and is ready for download."""
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "Project Utility Export"
    description = "Sent when a Project Utility Status export is prepared and ready for download."

    companies_with_relationship_or_self = ["neea"]


class NeeaHomeUtilityStatusCustomExportCompletedMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = """Project Utility Report has completed and is ready for download."""
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "Project Utility Custom Report"
    description = "Sent when a Project Utility Custom Report is prepared and ready for download."

    companies_with_relationship_or_self = ["neea"]


class NeeaHomeUtilityStatusBPAExportCompletedMessage(ModernMessage):
    """Modern message sent to NEEA"""

    content = (
        """Performance Path Calculator Summary Report has completed and is ready for download."""
    )
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "Performance Path Calculator Summary Report"
    description = (
        "Sent when a Performance Path Calculator Summary Report is prepared and ready for download."
    )

    companies_with_relationship_or_self = ["neea"]


class NeeaMonthlyHomeUtilityStatusBPAExportAvailableMessage(ModernMessage):
    """Modern message sent to NEEA"""

    title = """Performance Path Calculator Summary Report for {month} {year}"""
    content = """Monthly Performance Path Calculator Summary Report has completed and is ready for download.
    <a href="{url}">Click here to download it directly.</a>"""
    sticky_alert = True
    category = "NEEA"
    level = "info"

    verbose_name = "Performance Path Calculator Summary Report (Monthly)"
    description = (
        "Sent on the first of each month when the BPA Utility "
        "Report is automatically prepared and ready for download."
    )

    companies_with_relationship_or_self = ["neea"]
