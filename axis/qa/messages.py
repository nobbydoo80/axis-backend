"""Modern configurable messages for qa app."""
__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]
import os.path

from django.apps import apps
from django.conf import settings

from axis.messaging.messages import ModernMessage
from . import strings


customer_hirl_app = apps.get_app_config("customer_hirl")


# NOTE: These two messages are sort of the same thing, just to different audiences.
class QaIsGatingCertificationMessage(ModernMessage):
    title = "QA Certification Gate"
    content = strings.QA_HAS_BEEN_NOTIFIED_MSG
    sticky_alert = True
    category = "QA"
    level = "info"
    unique = True

    verbose_name = "QA Certification Gate"
    description = "A QA company is gating certification of a project."

    company_types = ["rater", "provider"]


class YourQaCompanyIsGatingCertficationMessage(ModernMessage):
    title = "QA Certification Gate"
    content = strings.QA_IS_GATING_CERTIFICATION
    sticky_alert = True
    category = "QA"
    level = "info"
    unique = True

    verbose_name = "QA Certification Gate"
    description = "Your QA company is gating certification of a project."

    company_types = ["qa"]


class QaRecommendedMessage(ModernMessage):
    title = "QA Recommended"
    content = strings.QA_RECOMMENDED_MSG
    sticky_alert = True
    category = "QA"
    level = "info"
    unique = True

    verbose_name = "QA Recommended"
    description = "Sent when QA can be added for a project."

    company_types = ["qa"]


class QAAddedMessage(ModernMessage):
    title = "QA has been selected for project"
    content = strings.QA_HAS_BEEN_ADDED_MSG
    sticky_alert = True
    category = "QA"
    level = "info"
    unique = True

    verbose_name = "QA has been selected for project."
    description = "When QA (Field / File) QA has been added where QA is not 100% required."

    company_types = ["rater", "provider"]


class NEEABPAQACompleteFailedMessage(ModernMessage):
    title = "NEEA BPA QA Complete Review Failed"
    content = """
    <a href="{obj_edit}">{obj}</a> participating in the Utility Incentive V2 - Single Family
    program has failed QA and does not meet the requirements of the program.
    """
    sticky_alert = True
    category = "QA"
    level = "error"

    verbose_name = "NEEA BPA QA Complete Failed"
    description = "Sent when QA is complete but failed on NEEA BPA program."
    company_types = ["rater", "utility"]


class QaCorrectionRequiredMessage(ModernMessage):
    title = "QA Correction Required"
    content = (
        "{qa_company} has requested information in the QA of {obj_type} "
        '<a href="{obj_edit}">{obj}</a>.  Please click <a href="{action_url}">'
        "here</a> to resolve this."
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "qa_correction_required_email.html",
    )
    sticky_alert = True
    category = "QA"
    level = "error"

    verbose_name = "Correction Required"
    description = "Sent when the QA company triggers a request for correction."

    company_types = ["rater"]


class QaCorrectionReceivedMessage(ModernMessage):
    title = "QA Correction Received"
    content = strings.QA_CORRECTION_RECEIVED
    sticky_alert = True
    category = "QA"
    level = "info"

    verbose_name = "Correction Received"
    description = "Sent when the Rating company has submitted a correction."

    company_types = ["qa", "provider"]


class CustomerHIRLQaCorrectionReceivedMessage(ModernMessage):
    title = "{requirement_type} QA Correction Received for {qa_designee_name}"
    content = (
        '<a href="{verifier_url}">{verifier_name}</a> has responded to information in the {requirement_type} '
        'QA of the home <a href="{home_url}">{home_address}</a>, '
        'as requested by <a href="{qa_designee_url}">{qa_designee_name}</a>. <a href="{qa_link}">View QA</a>'
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "customer_hirl_qa_correction_received_email.html",
    )
    sticky_alert = True
    category = "QA"
    level = "info"

    verbose_name = "Correction Received"
    description = "Sent when the Verifier company has submitted a correction  for HI."

    company_types = ["qa", "provider"]


class QaCompleteMessage(ModernMessage):
    title = "QA Complete"
    content = '{qa_company} has completed {type} QA on <a href="{obj_edit}">{obj}</a>'
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "qa_complete_email.html",
    )

    category = "QA"
    level = "info"

    verbose_name = "QA Completed"
    description = "Sent when non Certification gating QA has been completed."


class QAGatingCompleteMessage(ModernMessage):
    title = "Gating QA Complete"
    content = '{qa_company} has completed certification gating {type} QA on <a href="{obj_edit}">{obj}</a>'
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "qa_gating_complete_email.html",
    )
    category = "QA"
    level = "info"

    verbose_name = "Gating QA Completed"
    description = "Sent when a Certification gating QA has been completed."


class QACycleTimeReporting(ModernMessage):
    title = "QA Cycle Time Reporting"
    content = '{instance_type} <a href="{instance_url}">{instance}</a> has been in {state} for {countdown}.'
    category = "QA"
    level = "warning"

    verbose_name = "QA Cycle Time Reporting"


class HomeAddedToMultiFamilySubdivision(ModernMessage):
    title = "New Multi-Family Project"
    content = strings.QA_SUBDIVISION_HAS_HOME_ADDED
    category = "QA"
    level = "info"
    company_types = ["qa"]

    verbose_name = "Project Added to Multi-family Subdivision"


class QASubdivisionGatingCertification(ModernMessage):
    title = "Multi-family Subdivision QA"
    content = strings.QA_SUBDIVISION_GATING_HOMES
    category = "QA"
    level = "info"
    company_types = ["qa"]
    unique = True

    verbose_name = "Certification Gated by Subdivision QA"


class QACorrectionRequiredDailyEmail(ModernMessage):
    title = "Daily QA Report - {total} outstanding project(s) have QA corrections requested"
    content = """{total} project(s) require outstanding corrections for {full_date}."""

    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "templates",
            "qa",
            "emails",
            "correction_required_daily_email.html",
        )
    )

    category = "QA"

    level = "info"
    company_types = ["rater", "provider"]
    company_admins_only = True
    unique = False

    verbose_name = "Daily email sent when outstanding correction requested actions are present"
    description = (
        "This will send a list of projects that have outstanding QA correction "
        "requested actions needed before it passes QA."
    )


class QAFailingHomesDailyEmail(ModernMessage):
    title = "{num_homes} Failed QA in Axis"
    content = "{num_homes} project(s) have Failed QA in Axis"

    email_content = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "templates", "qa", "failing_qa_email.html")
    )

    category = "QA"

    level = "warning"
    company_types = ["rater", "provider", "utility", "eep_sponsor"]
    company_admins_only = True
    unique = True

    verbose_name = "Daily email sent when outstanding projects have failed QA"
    description = "This is will be sent when projects have have failed QA."


class QADesigneeAssigneeMessage(ModernMessage):
    title = "{title}"
    content = (
        "QA for project {home_address} has been assigned to {qa_designee}. "
        '<a href="{home_link}">View details</a>'
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "qa_designee_assignee_email.html",
    )

    category = "QA"
    level = "info"

    verbose_name = "QA Designee invitation"
    description = "This is will be sent when new QA Designee set for QA."


class CustomerHIRLQADesigneeAssigneeMessage(ModernMessage):
    title = "{requirement_type} Review Assigned - {home_city}"
    content = (
        "Dear {qa_designee_name}, {requirement_type} review assigned for project "
        '<a href="{home_link}">{home_address}</a>'
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "qa",
        "templates",
        "qa",
        "emails",
        "customer_hirl_qa_designee_assignee_email.html",
    )

    category = "QA"
    level = "info"

    verbose_name = "QA Designee invitation"
    description = "This is will be sent when new QA Designee set for QA for HI."
    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]
