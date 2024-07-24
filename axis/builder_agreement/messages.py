"""messages: Django builderagreement"""


import logging
from axis.messaging.messages import ModernMessage

__author__ = "Steven Klass"
__date__ = "8/21/15 1:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementExportCompletedMessage(ModernMessage):
    content = """Builder Information Report export has completed."""
    sticky_alert = True
    category = "agreement"
    level = "success"

    verbose_name = "Builder Information Report"
    description = (
        "Indicates that a Builder Information Report export is complete " "and ready for download."
    )
