"""Builder messages"""


import logging

from axis.messaging.messages import ModernMessage

__author__ = "Steven Klass"
__date__ = "11/9/18 11:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class VerifierAgreementRequestForCertificateOfInsuranceMessage(ModernMessage):
    """Enrollment is approved by owner."""

    title = "Certificate of Insurance Requested"
    content = (
        "{owner} requires your Certificate of Insurance to complete enrollment. "
        '<a href="{url}">Add your Certificate of Insurance to continue.</a>'
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Certificate of Insurance Requested"
    description = "Sent when the NGBS staff have appoved your enrollment."
    company_types = "rater"


class VerifierLegalAgreementReadyForSigningMessage(ModernMessage):
    """Agreement is submitted to signing backend and ready."""

    title = "NGBS Legal Agreement: Signing Required"
    content = (
        "{owner} has posted a legal agreement for digital signature. "
        "Check {email} for the link to sign the document via DocuSign."
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement requires your signature"
    description = "Sent when the NGBS staff have posted your agreement for signing."
    company_types = "rater"


class OfficerLegalAgreementReadyForSigningMessage(ModernMessage):
    """Agreement is submitted to signing backend and ready."""

    title = "NGBS Legal Agreement: Officer Signing Required"
    content = (
        "{owner} has posted a legal agreement for digital signature. "
        "Check {email} for the link to sign the document via DocuSign."
    )
    category = "Verifier Agreement"
    level = "info"
    sticky_alert = True

    verbose_name = "Legal Agreement requires Officer signature"
    description = "Sent when your agreement require officer signing."
    company_types = "rater"


class VerifierEnrollmentCompleteMessage(ModernMessage):
    """Agreement has been deactivated by owner."""

    title = "NGBS Legal Agreement: Completed"
    content = (
        "Your enrollment with {owner} has been completed, in effect through {end}. "
        "<a href='{url}'>You can keep your enrollment information current from the "
        "enrollment page.</a>"
    )
    category = "Verifier Agreement"
    level = "info"

    verbose_name = "Agreement complete"
    description = "Sent when the NGBS staff counter-sign your agreement."
    company_types = "rater"


class ExpiredVerifierAgreementMessage(ModernMessage):
    """Agreement has been expired"""

    title = "Verifier Agreement Expired"
    content = (
        "Your verifier agreement with {owner} has expired. "
        "<a href='{url}'>Your expired enrollment information will remain available.</a>"
    )
    category = "Verifier Agreement"
    level = "warning"
    sticky_alert = True

    verbose_name = "Verifier Agreement ended"
    description = "Sent when Verifier Agreement expired"
    company_types = "rater"
