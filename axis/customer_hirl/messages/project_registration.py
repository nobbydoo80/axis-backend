"""project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "05/04/2021 16:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps

from axis.messaging.messages import ModernMessage

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectRegistrationCreatedMessage(ModernMessage):
    title = "New Registration created"
    content = (
        "New Registration <a href=\"{url}\" target='_blank'>"
        "#{registration_id}</a> created by {verifier} "
    )
    category = "NGBS Project Registration"
    level = "info"
    sticky_alert = False
    verbose_name = "When Registration record has been created without Buildings"
    description = "Informing that new NGBS Registration has been created"
    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]


class ProjectRegistrationERFPNotificationMessage(ModernMessage):
    title = "Entity Responsible For Payment changed"
    content = (
        "Entity Responsible For Payment has "
        "been changed to {new_company_type}. "
        "<a href=\"{url}\" target='_blank'>View Project Registration</a>. \n Project H-Numbers: {h_numbers}"
    )
    category = "NGBS Project Registration"
    level = "info"
    sticky_alert = False

    verbose_name = "Entity Responsible For Payment has been changed"
    description = (
        "Informing when a change has been made to the "
        "Entity Responsible For Payment in Project Registration"
    )

    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]


class HIRLProjectRegistrationStateChangedMessage(ModernMessage):
    title = "Project Registration Status Changed"
    content = (
        "Registration created by {verifier} changed status from <b>{old_state}</b> "
        "to <b>{new_state}</b><br>"
        '<a href="{url}"'
        "target='_blank'>View Registration</a>"
    )
    category = "NGBS Project Registration"
    level = "info"
    sticky_alert = False

    verbose_name = "NGBS Registration Status changed"
    description = "Sent once the NGBS Registration status been changed"

    companies_with_relationship_or_self = [customer_hirl_app.CUSTOMER_SLUG]


class HIRLProjectRegistrationRejectedMessage(ModernMessage):
    title = "Project Registration Rejected"
    content = (
        "Registration <a href=\"{url}\" target='_blank'>#{project_registration_id}</a> "
        "has been rejected by NGBS due to the following reason: {reason}.  "
    )
    category = "NGBS Project Registration"
    level = "warning"
    sticky_alert = False

    verbose_name = "NGBS Project Registration Rejected"
    description = "Sent when registration been rejected by NBGS"


class HIRLProjectRegistrationApprovedByHIRLCompanyMessage(ModernMessage):
    title = "NGBS Project Registration Approved"
    content = (
        "The following project registration has been approved by NGBS. "
        "<a href=\"{url}\" target='_blank'>View Registration</a>"
    )
    category = "NGBS Project Registration"
    level = "success"
    sticky_alert = False

    verbose_name = "NGBS Project state changed"
    description = "Sent once the NGBS Project has been approved by NGBS"
