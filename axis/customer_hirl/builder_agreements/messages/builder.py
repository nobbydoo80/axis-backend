__author__ = "Steven Klass"
__date__ = "11/9/18 11:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


from axis.messaging.messages import ModernMessage


class LegalAgreementReadyForSigningMessage(ModernMessage):
    """Agreement is submitted to signing backend and ready."""

    title = "NGBS Legal Agreement: Signing Required"
    content = (
        "{owner} has posted a legal agreement for digital signature. "
        "Check {email} for the link to sign the document via DocuSign."
    )
    category = "Client Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement requires signature"
    description = "Sent when the NGBS staff have posted your agreement for signing."
    company_types = ["builder", "developer", "architect", "communityowner"]


class EnrollmentCompleteMessage(ModernMessage):
    title = "NGBS Legal Agreement Completed"
    content = (
        "Your legal agreement with {owner} "
        "has been completed, in effect through {end}. "
        '<a href="{url}">You can keep your agreement information current from this page '
        ".</a>"
    )
    category = "Client Agreement"
    level = "info"

    verbose_name = "Agreement complete"
    description = "Sent when the NGBS staff counter-sign your agreement."
    company_types = ["builder", "developer", "architect", "communityowner"]


class ExtensionRequestApprovedMessage(ModernMessage):
    title = "NGBS Legal Agreement Extension Request Approved"
    content = (
        "Your extension request agreement with {owner} "
        "has been approved, and now you can sign it via Docusgin email. "
        '<a href="{client_agreement_url}">View Client Agreement</a> '
    )
    category = "Client Agreement"
    level = "info"

    verbose_name = "Agreement Approved"
    description = "Sent when the NGBS approved extension agreement"
    company_types = ["builder", "developer", "architect", "communityowner"]


class ExtensionRequestRejectedMessage(ModernMessage):
    title = "NGBS Legal Agreement Extension Request Rejected"
    content = (
        "Your extension request agreement with {owner} "
        "has been Rejected. Reason: {extension_request_reject_reason}. "
        '<a href="{client_agreement_url}">View Client Agreement</a> '
    )
    category = "Client Agreement"
    level = "info"

    verbose_name = "Agreement Approved"
    description = "Sent when the NGBS approved extension agreement"
    company_types = ["builder", "developer", "architect", "communityowner"]


class ExtensionRequestCompleteMessage(ModernMessage):
    title = "NGBS Legal Agreement Extension Request Completed"
    content = (
        "Your extension request agreement with {owner} "
        "has been completed, in effect through {end}. "
        '<a href="{url}">You can keep your agreement information current from this page '
        ".</a>"
    )
    category = "Client Agreement"
    level = "info"

    verbose_name = "Agreement complete"
    description = "Sent when the NGBS staff counter-sign your agreement."
    company_types = ["builder", "developer", "architect", "communityowner"]


class BuilderAgreementExpirationWarningMessage(ModernMessage):
    """Agreement is approaching its preset `agreement_expiration_date`."""

    title = "NGBS Legal Agreement Expiring"
    content = (
        "Your builder agreement with {owner} is expiring in {days} days. "
        '<a href="{url}">Manage the agreement.</a>'
    )
    category = "Client Agreement"
    level = "warning"

    verbose_name = "Client Agreement expiration warning"
    description = "Sent when the Agreement is nearing its expiration date."
    company_types = ["builder", "developer", "architect", "communityowner"]


class ExpiredBuilderAgreementMessage(ModernMessage):
    """Agreement has been expired"""

    title = "NGBS Legal Agreement Expired"
    content = (
        "Your builder agreement with {owner} has been expired. "
        '<a href="{url}">Your expired enrollment information will remain available.</a>'
    )
    category = "Client Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Agreement ended"
    description = "Sent when agreement expired"
    company_types = ["builder", "developer", "architect", "communityowner"]


class ExpiredInsuranceBuilderAgreementMessage(ModernMessage):
    """Insurance for builder agreement has expired"""

    title = "NGBS COI Expired"
    content = (
        "Your certificate of insurance for builder agreement has expired."
        '<a href="{url}">Your expired enrollment information will remain available.</a>'
    )
    category = "Client Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Insurance for builder agreement ended"
    description = "Sent when insurance for builder agreement expired"
    company_types = ["builder", "developer", "architect", "communityowner"]
