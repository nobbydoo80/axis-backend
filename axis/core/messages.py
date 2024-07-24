""" System-level message placeholder """


import logging
import os

from axis.messaging.messages import ModernMessage

__author__ = "Autumn Valenta"
__date__ = "2015-03-04 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AxisDjangoMessage(ModernMessage):
    """
    Using when you need to display a one-time notification message (also known as “flash message”)
    to the user after processing a form or some other types of user input.
    Replacement for django.contrib.messages
    """

    title = "System Notification"
    category = "system"
    level = "system"

    verbose_name = "System Notifications"
    description = "System information messages"


class AxisSystemMessage(ModernMessage):
    # Title and Content information are to be filled in when the warnings are generated at runtime.
    # title =
    # content =

    sticky_alert = True
    category = "system"
    level = "system"

    verbose_name = "System Warning"
    description = "Custom messages from Axis regarding system or program availability information."

    unique = True

    company_slugs = ["pivotal-energy-solutions"]


class TensorAnonymousActivationMessage(ModernMessage):
    category = "registration"
    level = "info"

    verbose_name = "User Request to be a member"
    description = "A new user is requesting to use AXIS as part of your company"
    required = True

    company_admins_only = True

    title = "New User Registration"
    content = (
        "A new user {user_fullname} ({user_email}) has requested approval from {company} to use "
        'AXIS. Click <a href="{approval_url}"><here></a> to activate their account.'
    )

    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "tensor_registration",
            "admin",
            "company_admin_anonymous_user_activation_email.html",
        )
    )

    email_subject = "A new user is requesting to use AXIS as member of {company}"


class TensorAnonymousActivationWithoutCompanyMessage(TensorAnonymousActivationMessage):
    verbose_name = "User Request to be a member without a company"

    content = (
        "A new user {user_fullname} ({user_email}) has requested approval to use AXIS without "
        'company. Click <a href="{approval_url}">here</a> to activate their account.'
    )
    required = True

    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "tensor_registration",
            "admin",
            "pivotal_admin_anonymous_user_activation_email.html",
        )
    )

    email_subject = "A new user is requesting to use AXIS without a company."
    company_slugs = [
        "pivotal-energy-solutions",
    ]


class TensorCompanyApprovalMessage(ModernMessage):
    category = "registration"
    level = "success"
    required = True

    verbose_name = "Company Approvals"
    description = "The company a user requested to be a part of has approved the user's request."

    title = "Company Approval Confirmation"
    content = "{user_email} has been approved for login."

    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "tensor_registration",
            "account_approved_notification_for_user_email.html",
        )
    )
    email_subject = "Your AXIS account has been approved"


class TensorUserApprovalMessage(ModernMessage):
    category = "registration"
    level = "success"
    required = True

    verbose_name = "User approved by company"
    description = (
        "Confirmation to the user that a company has approved them to use Axis under their company."
    )

    title = "User Approval Confirmation Notice"
    content = "{company_name} has approved {user_fullname} ({user_email}) for login."


class TensorCompanyAdminUserApprovalMessage(TensorUserApprovalMessage):
    verbose_name = "User has been approved as an admin"
    content = (
        "{user_fullname} ({user_email}) has been approved as a "
        "<a href={company_url}>{company_name}</a> company administrator."
    )
    required = True


class TensorAuthenticatedUserApproveMessage(ModernMessage):
    category = "registration"
    level = "info"
    required = True

    verbose_name = "New user activated his account"
    description = "User added by company activates their account."

    title = "New User Registration"
    content = "A new company user {user_fullname} ({user_email}) has activated their account"

    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "tensor_registration",
            "admin",
            "company_admin_authenticated_user_activation_email.html",
        )
    )
    email_subject = "{user_fullname} has activated their account"


class TrainingCreatedStatusCompanyMessage(ModernMessage):
    title = "Training created"
    content = (
        "New training {training} created by {trainee} "
        "<a href='{url}#/tabs/training' "
        "target='_blank'>View training list</a>"
    )
    category = "User training"
    level = "info"
    sticky_alert = True

    verbose_name = "Training created"
    description = "Sent when new training has been created"


class AxisOutsideContactMessage(ModernMessage):
    title = "Pivotal Contact Request: {subject}"
    content = None
    email_content = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "templates", "core", "contact_email.html")
    )

    category = "system"
    level = "info"

    unique = True

    verbose_name = "Sent when an outsider wants info on Pivotal/Axis"
    description = "Outside Contact Information Request"

    company_slugs = ["pivotal-energy-solutions"]
