__author__ = "Artem Hruzd"
__date__ = "03/04/2021 17:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os
from django.conf import settings
from axis.messaging.messages import ModernMessage


class InvoiceCreatedNotificationMessage(ModernMessage):
    title = "Invoice Created"
    content = (
        'New Invoice available. <a href="{invoice_detail_url}" target="_blank">View invoice</a>'
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "invoicing",
        "templates",
        "emails",
        "invoice_created_notification_email.html",
    )
    category = "Invoicing"
    level = "info"
    sticky_alert = False

    verbose_name = "Invoice created"
    description = "Sent to customer when Invoice have been created"

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


# HIRL Specific messages
class HIRLInvoicePaidMessage(ModernMessage):
    title = "Invoice has been Paid"
    content = (
        "Invoice successfully PAID"
        "<a href='{invoice_detail_url}' "
        "target='_blank'>View invoice</a>"
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "invoicing",
        "templates",
        "emails",
        "hirl_invoice_paid_notification_email.html",
    )
    category = "Invoicing"
    level = "success"
    sticky_alert = False

    verbose_name = "Invoice Paid"
    description = "Sent to Builder and Verifier and Home Innovations when Invoice is ready to pay"

    company_types = ("builder", "rater", "provider")

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class HIRLInvoiceCancelledMessage(ModernMessage):
    title = "Invoice Declined"
    content = (
        "Invoice has been cancelled"
        "<a href='{invoice_detail_url}' "
        "target='_blank'>View invoice</a>"
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "invoicing",
        "templates",
        "emails",
        "hirl_invoice_cancelled_notification_email.html",
    )
    category = "Invoicing"
    level = "error"
    sticky_alert = False

    verbose_name = "Invoice Declined"
    description = "Sent to Builder, Verifier and Home Innovations when Invoice is ready to pay"

    company_types = ("builder", "rater", "provider")

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]
