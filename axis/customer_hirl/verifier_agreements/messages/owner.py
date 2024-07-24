"""Owner messages"""


import logging

from django.apps import apps

from axis.messaging.messages import ModernMessage

__author__ = "Steven Klass"
__date__ = "11/9/18 11:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class NewVerifierAgreementEnrollmentMessage(ModernMessage):
    """New enrollment has been submitted by enrollee for approval."""

    title = "New Enrollment Submitted: {verifier}"
    content = (
        "<a href='{url}'>Review and approve this enrollment</a>, "
        "or <a href='{list_url}'>view all pending enrollments</a>."
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "New NGBS Enrollment"
    description = "Sent when a verifier submits their enrollment."
    company_slugs = [app.CUSTOMER_SLUG]
    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class VerifierLegalAgreementReadyForCountersigningMessage(ModernMessage):
    """Agreement is submitted to signing backend and ready."""

    title = "Enrollment Legal Agreement: Countersigning Required"
    content = (
        "{verifier} has signed the legal agreement. "
        "Check {email} for the link to countersign securely via DocuSign."
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement requires countersignature"
    description = "Sent when Axis receives the signed legal agreement from DocuSign."
    company_slugs = [app.CUSTOMER_SLUG]
    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class NewVerifierAgreementDocumentMessage(ModernMessage):
    """A document has been added to the Agreement by someone who is not the owner."""

    title = "New Document Available"
    content = (
        '<a href="{url}">Verifier agreement for {verifier}</a> has a new document posted: '
        '<a href="{download_url}">Download <em>{filename}</em></a>'
    )
    category = "Verifier Agreement"
    level = "info"

    verbose_name = "New document for Verifier Agreement"
    description = (
        "Sent when a document is saved to a verifier agreement by "
        "someone other than the NGBS staff."
    )
    company_slugs = [app.CUSTOMER_SLUG]
    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class VerifierAgreementChangedByVerifierMessage(ModernMessage):
    """Agreement has been changed by verifier"""

    title = "NGBS Verifier Agreement has been changed"
    content = (
        "Information in Verifier Agreement for {verifier} has been changed."
        "<a href='{url}#/tabs/history'>View Verifier Agreement history.</a>"
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Agreement changed"
    description = "Sent when Verifier Agreement changed by Verifier"
    company_slugs = [app.CUSTOMER_SLUG]
    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class VerifierAgreementExpirationWarningMessage(ModernMessage):
    """Agreement is approaching its preset `agreement_expiration_date`."""

    unique = True
    title = "Verifier Agreement Expiring"
    content = (
        "Verifier agreement for {verifier} is expiring in {days} days. "
        '<a href="{url}">Manage the agreement.</a>'
    )
    category = "Verifier Agreement"
    level = "warning"

    verbose_name = "Verifier Agreement expiration warning"
    description = "Sent when the Agreement is nearing its expiration date."

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class ExpiredOwnerVerifierAgreementMessage(ModernMessage):
    """Agreement has been expired"""

    title = "Verifier Agreement Expired"
    content = (
        "{verifier} verifier agreement has been expired. "
        "<a href='{url}'>Expired enrollment information will remain available.</a>"
    )
    category = "Verifier Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Verifier Agreement ended"
    description = "Sent when Verifier Agreement expired"
    company_slugs = [app.CUSTOMER_SLUG]
    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]
