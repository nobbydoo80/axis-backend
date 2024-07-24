"""messages.py: """

__author__ = "Artem Hruzd"
__date__ = "07/10/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.apps import apps

from axis.messaging.messages import ModernMessage

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLScoringUploadNotificationMessage(ModernMessage):
    title = "New Verification Report Uploaded"
    content = (
        "Verification Report({verification_report_type}) has been uploaded by "
        '<a href="{uploaded_user_profile_url}" target="_blank">{uploaded_user}</a>. '
        '<a href="{home_url}#/tabs/programs" '
        'target="_blank">View project</a>'
    )
    category = "Verification Report Upload"
    level = "info"
    sticky_alert = False

    verbose_name = "Verification Report Uploaded"
    description = "Sent when new Verification Report has been uploaded for Home"
    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]


class HIRLScoringUploadFinalOutstandingFeeBalanceMessage(ModernMessage):
    title = "Final Inspection Report Uploaded with Missing Fees"
    content = (
        "A Final Inspection Report has been uploaded for a building with an "
        "outstanding fee balance. "
        "Certification of building "
        '<a href="{project_url}" target="_blank">{project_id}</a> located at '
        '<a href="{home_url}" target="_blank">{home_address}</a> will be '
        "gated by receipt of the outstanding fees."
    )
    level = "info"

    category = "Verification Report Upload"
    verbose_name = "Final Inspection Report Uploaded with Missing Fees "
    description = (
        "Sent when the final inspection report is uploaded "
        "but there is an outstanding balance for the project"
    )
