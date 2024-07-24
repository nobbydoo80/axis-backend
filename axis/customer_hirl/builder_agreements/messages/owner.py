__author__ = "Steven Klass"
__date__ = "11/9/18 11:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.apps import apps
from axis.messaging.messages import ModernMessage

customer_hirl_app = apps.get_app_config("customer_hirl")


class NewBuilderEnrollmentMessage(ModernMessage):
    """New enrollment has been submitted by enrollee for approval."""

    title = "New Enrollment Submitted: {company}"
    content = (
        '<a href="{url}">Review and approve this enrollment</a>, '
        'or <a href="{list_url}">view all pending enrollments</a>.'
    )
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "New NGBS Enrollment"
    description = "Sent when a builder submits their enrollment."
    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class LegalAgreementSignedMessage(ModernMessage):
    """Agreement has been signed by enrollee."""

    title = "NGBS Legal Agreement: Signing Completed"
    content = (
        "{company} has signed the legal agreement and will upload their Certificate of "
        'Insurance. <a href="{url}">View the builder agreement for the signed document.'
        "</a>"
    )
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement signature complete"
    description = "Sent when the builder has digitally signed the legal agreement."
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class LegalAgreementReadyForCountersigningMessage(ModernMessage):
    """Agreement is submitted to signing backend and ready."""

    title = "NGBS Legal Agreement: Countersigning Required"
    content = (
        "{company} has signed the legal agreement. "
        "Check {email} for the link to countersign securely via DocuSign."
    )
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement requires countersignature"
    description = "Sent when AXIS receives the signed legal agreement from DocuSign."
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class NewExtensionRequestMessage(ModernMessage):
    title = "New NGBS Extension Request Agreement"
    content = '{company} has requested an extension for <a href="{client_agreement_url}">Client Agreement</a>.'
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "New Extension Request"
    description = "Sent when client initiate new extension request"
    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class ExtensionRequestAgreementReadyForCountersigningMessage(ModernMessage):
    """Extension Request Agreement is submitted to signing backend and ready."""

    title = "NGBS Extension Request Agreement: Countersigning Required"
    content = (
        "{company} has signed the extension request agreement. "
        "Check {email} for the link to countersign securely via DocuSign."
    )
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Extension Request Agreement requires countersignature"
    description = "Sent when AXIS receives the signed legal agreement from DocuSign."
    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class NewBuilderAgreementDocumentMessage(ModernMessage):
    """A document has been added to the Agreement by someone who is not the owner."""

    title = "New Document Available"
    content = (
        '<a href="{url}">Builder agreement for {company}</a> has a new document posted: '
        '<a href="{download_url}">Download <em>{filename}</em></a>'
    )
    category = "Client Agreement"
    level = "info"

    verbose_name = "New document for Client Agreement"
    description = (
        "Sent when a document is saved to a builder agreement by "
        "someone other than the NGBS staff."
    )
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class AgreementExpirationWarningMessage(ModernMessage):
    """Agreement is approaching its preset `agreement_expiration_date`."""

    unique = True
    title = "Client Agreement Expiring"
    content = (
        "Builder agreement for {company} is expiring in {days} days. "
        '<a href="{url}">Manage the agreement.</a>'
    )
    category = "Client Agreement"
    level = "warning"

    verbose_name = "Client Agreement expiration warning"
    description = "Sent when the Agreement is nearing its expiration date."
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]
    company_admins_only = True

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class ExpiredOwnerAgreementMessage(ModernMessage):
    """Agreement has been expired"""

    title = "NGBS Legal Agreement Expired"
    content = (
        "{company} builder agreement has expired. "
        '<a href="{url}">Expired enrollment information will remain available.</a>'
    )
    category = "Client Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Client Agreement ended"
    description = "Sent when builder agreement expired"
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class ExpiredInsuranceOwnerAgreementMessage(ModernMessage):
    """Agreement has been expired"""

    title = "NGBS COI Expired"
    content = (
        "{company} certificate of insurance has expired. "
        '<a href="{url}">Expired enrollment information will remain available.</a>'
    )
    category = "Client Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Insurance for builder agreement ended"
    description = "Sent when insurance for builder agreement expired"
    company_slugs = [customer_hirl_app.CUSTOMER_SLUG]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]
