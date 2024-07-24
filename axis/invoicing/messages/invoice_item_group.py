"""invoice_item_group.py: """

__author__ = "Artem Hruzd"
__date__ = "03/18/2021 21:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.messaging.messages import ModernMessage
from axis.company.models import Company


class HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage(ModernMessage):
    title = "Project Fee Created"
    content = (
        'Fees are due for NGBS Project <a href="{project_url}">{project_id}</a>.  '
        '<a href="{url}">View projects with outstanding balances '
        "and generate a payment invoice.</a>"
    )
    category = "Invoicing"
    level = "info"
    sticky_alert = False

    verbose_name = "Project Fee Created"
    description = "Sent to entity Responsible for Payment Company when Fee has been created"

    company_types = (
        Company.BUILDER_COMPANY_TYPE,
        Company.ARCHITECT_COMPANY_TYPE,
        Company.COMMUNITY_OWNER_COMPANY_TYPE,
        Company.DEVELOPER_COMPANY_TYPE,
        Company.PROVIDER_COMPANY_TYPE,
    )


class HIRLInvoiceItemGroupUpdatedMessage(ModernMessage):
    title = "Project Fees Have Been Updated"
    content = (
        'Fees have been updated for <a href="{home_url}">{home_address}</a>.  '
        '<a href="{invoice_item_groups_url}">View projects with outstanding balances '
        "and generate a payment invoice.</a>"
    )
    category = "Invoicing"
    level = "info"
    sticky_alert = False

    verbose_name = "Project Fees Have Been Updated"
    description = "Sent when Fees have been updated"

    company_types = (
        Company.BUILDER_COMPANY_TYPE,
        Company.ARCHITECT_COMPANY_TYPE,
        Company.COMMUNITY_OWNER_COMPANY_TYPE,
        Company.DEVELOPER_COMPANY_TYPE,
        Company.PROVIDER_COMPANY_TYPE,
    )

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]
