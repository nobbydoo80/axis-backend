"""inspection_grade.py: """

__author__ = "Artem Hruzd"
__date__ = "12/03/2019 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os

from django.apps import apps
from django.conf import settings

from axis.messaging.messages import ModernMessage

customer_hirl_app = apps.get_app_config("customer_hirl")


class InspectionGradeCreatedUserMessage(ModernMessage):
    title = "Verification Grade created"
    content = (
        "New Inspection grade: <b>{inspection_grade}</b> created by {approver_company} "
        "<a href='{url}#/tabs/inspection_grade' "
        "target='_blank'>View Verification Grades list</a>"
    )
    category = "User inspection grade"
    level = "info"
    sticky_alert = True

    verbose_name = "Verification Grade created"
    description = (
        "Sent to user when new Verification Grade " "has been created by Oversight Company"
    )


class InspectionGradeCustomerHIRLQuarterReportMessage(ModernMessage):
    title = "NGBS Green Verifier Performance Report from {from_date} to {to_date}"
    content = (
        "Congratulations! Throughout {from_date} to {to_date}, "
        "you consistently earned high performance marks from the NGBS Green Review team. Great job! "
        "<a href='{url}' "
        "target='_blank'>View your current NGBS Green 6-month grade average</a>"
    )

    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "templates",
        "inspection_grade",
        "customer_hirl_inspection_grade_quarter_report_email.html",
    )

    category = "User inspection grade"
    level = "info"
    verbose_name = "Verification Grade quarter report"
    description = "Sending to user two times in a year"

    companies_with_relationship_or_self = [customer_hirl_app.CUSTOMER_SLUG]
