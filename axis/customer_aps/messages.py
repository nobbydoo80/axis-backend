""" Modern configurable messages for customer_aps. """

from axis.messaging.messages import ModernMessage

__author__ = "Rajesh Pethe"
__date__ = "09/14/2020 17:48:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class ApsHomeUtilityCustomExportCompletedMessage(ModernMessage):
    """Modern message sent to APS"""

    title = "Download Completed"
    content = """APS Subdivision custom report has completed and is ready for download."""
    sticky_alert = True
    category = "APS"
    level = "info"

    verbose_name = "APS Subdivision custom report"
    description = "Sent when a APS Subdivision custom report is prepared and ready for download."

    companies_with_relationship_or_self = ["aps"]


class ApsUpdatedMetersetMessage(ModernMessage):
    title = "Home Program has been updated"
    content = "The Program on home <a href='{home_url}'>{home}</a> has been updated to "
    "the {program} based on the HERS Score of {hers} and "
    "climate zone {climate_zone}."

    sticky_alert = True
    category = "APS"
    verbose_name = "APS Notification about Home program updates"
    description = "Sent when program changed for Home"
    companies_with_relationship_or_self = ["aps"]
