"""coi.py: """

__author__ = "Artem Hruzd"
__date__ = "10/26/2021 11:35 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.verifier_agreements.messages.owner import app
from axis.messaging.messages import ModernMessage


class COIAvailableMessage(ModernMessage):
    """Enrollee company has saved a value for `insurance_certificate`."""

    title = "Certificate of Insurance: Available for Review"
    content = (
        "{company} has posted their Certificate of Insurance. "
        "<a href='{url}' target='blank'>View</a>"
    )
    category = "Certificate of Insurance"
    level = "info"
    sticky_alert = True

    verbose_name = "Certificate of Insurance made available"
    description = "Sent when company supplies a certificate of insurance for review."
    company_slugs = [app.CUSTOMER_SLUG]


class COIChangedMessage(ModernMessage):
    """Enrollee company has changed a value for `insurance_certificate`."""

    title = "Certificate of Insurance: Changed"
    content = (
        "{company} changed their Certificate of Insurance. "
        "<a href='{url}' target='blank'>View</a>"
    )
    category = "Certificate of Insurance"
    level = "info"
    sticky_alert = True

    verbose_name = "Certificate of Insurance has been changed"
    description = "Sent when company changed existing certificate of insurance."
    company_slugs = [app.CUSTOMER_SLUG]
