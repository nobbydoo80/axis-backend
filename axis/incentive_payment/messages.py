"""Modern configurable messages for incentive_payment app."""


from axis.messaging.messages import ModernMessage

try:
    from . import strings
except ImportError:
    from axis.incentive_payment import strings


__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class IPPFailureMessage(ModernMessage):
    title = "Payment Rejected"
    content = strings.FAILED_IPP
    sticky_alert = True
    category = "incentive payments"
    level = "error"

    verbose_name = "Payment Rejected"
    description = "Sent when an Incentive Payment Failure Report is available."


class IPPCorrectionMessage(ModernMessage):
    title = "Correction Received"
    content = strings.CORRECTED_IPP
    sticky_alert = True
    category = "incentive payments"
    level = "info"

    verbose_name = "Correction Received"
    description = "Sent when a Pending Incentive Payment Report is available."


class IPPApprovedPayment(ModernMessage):
    title = "Approved for Payment"
    content = strings.APPROVED_IPP
    sticky_alert = True
    category = "incentive payments"
    level = "info"

    verbose_name = "Approved for Payment"
    description = "Sent when a Pending Incentive Payment is Approved."
