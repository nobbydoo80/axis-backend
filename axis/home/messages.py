"""Modern configurable messages for home app."""
import os

from axis.messaging.messages import ModernMessage

try:
    from . import strings
except ImportError:
    from axis.home import strings


__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeStatusExportCompletedMessage(ModernMessage):
    content = strings.HOMESTATUS_EXPORT_COMPLETED
    sticky_alert = False
    category = "project"
    level = "success"

    verbose_name = "Status Report Export"
    description = "Indicates that a Project Report export is complete " "and ready for download."


class HomeStatusProgramReportsCompletedMessage(ModernMessage):
    content = strings.HOMESTATUS_REPORT_COMPLETED
    sticky_alert = False
    category = "project"
    level = "success"

    verbose_name = "Program Report Export"
    description = (
        "Indicates that a Project Program Report export is complete " "and ready for download."
    )


class NEEABPAHomeCertificationPendingMessage(ModernMessage):
    content = (
        "<a href='{home_detail}'>{home}</a> "
        "participating in {program} program is ready for review."
    )
    category = "project"
    level = "info"

    verbose_name = "NEEA BPA Certification Pending"
    description = "Project has been inspected and is pending certification."

    unique = True

    companies_with_relationship_or_self = ["neea"]


class WSUHomeCertificationPendingMessage(ModernMessage):
    content = (
        "<a href='{home_detail}'>{home}</a> participating "
        "in {program} program is ready for review."
    )
    category = "project"
    level = "info"

    verbose_name = "WSU Certification Pending"
    description = "Project has been inspected and is pending certification."

    unique = True

    companies_with_relationship_or_self = ["provider-washington-state-university-extension-ene"]


class NEEABPAHomeCertifiedRaterMessage(ModernMessage):
    title = "NEEA BPA Certified Rater"
    content = (
        "<a href='{home_url}'>{home}</a> participating in "
        "the {program} program has been reviewed and finalized. "
        "This notification does not guarantee an incentive. "
        "Work with your utility to complete any additional requirements."
    )
    sticky_alert = True
    category = "project"
    level = "success"

    verbose_name = "NEEA BPA Project Certified Rater"
    description = "Sent to the Rater when a project in teh NEEA BPA program reaches certification"
    company_types = ["rater"]


class NEEABPAHomeCertifiedUtilityMessage(ModernMessage):
    title = "NEEA BPA Certified Utility"
    content = """
    <a href="{home_url}">{home}</a> participating in the {program} program
    has been reviewed and finalized. This notification does not guarantee an incentive. Work with the
    Rater and Builder to complete any additional requirements. Navigate to the Utility Reports to view
    and download reports.
    """
    sticky_alert = True
    category = "project"
    level = "success"

    verbose_name = "NEEA BPA Project Certified Utility"
    description = (
        "Sent to the Utilities when a project in the NEEA BPA program reaches certification"
    )
    company_types = ["utility"]
    companies_with_relationship_or_self = ["neea"]


class HomeCertifiedMessage(ModernMessage):
    title = "Certification"
    content = (
        "Project {project_name} was "
        "{certification_type} on {certification_date} by {certifying_company}."
    )
    sticky_alert = True
    category = "project"
    level = "success"

    verbose_name = "Project Certified"
    description = "Sent when a project reaches certification for a program"

    unique = True
    company_types = ["builder", "rater", "provider", "architect", "developer", "communityowner"]


class RaterAssociatedWithHomeStatMessage(ModernMessage):
    content = strings.COMPANY_ASSOCIATED_WITH_HOME_STATUS
    category = "project"
    level = "info"

    verbose_name = "Assigned to Project"
    description = "A Company has been assigned to a Project by another Company"

    company_types = ["rater", "provider"]


class PendingCertificationsDailyEmail(ModernMessage):
    title = "{num_homes} pending certification in Axis"
    content = None
    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "templates", "home", "certification_pending_email.html"
        )
    )

    category = "home"

    level = "info"
    company_types = ["provider", "utility", "eep_sponsor"]
    company_admins_only = True
    unique = True

    verbose_name = "Daily email sent when there are pending certifications in place"
    description = (
        "This is will be sent to any company responsible for the certification "
        "of a program on a project when they are holding up the process."
    )


class CertificationsDailyEmail(ModernMessage):
    title = "{num_homes} Certified Homes in Axis for {company}"
    content = None
    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "templates", "home", "new_certifications_email.html"
        )
    )

    category = "home"

    level = "info"
    company_types = ["rater", "provider", "utility", "eep_sponsor"]
    unique = True

    verbose_name = "Daily email sent when project completion/certifications occur"
    description = (
        "This is a daily email will be sent to rating company / program sponsor when a "
        "certifications occur."
    )


class BPACertificationsDailyEmail(ModernMessage):
    title = "{num_homes} Certified Projects in Axis for {program}"
    content = None
    email_content = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "templates", "home", "new_bpa_certification_email.html"
        )
    )

    category = "home"

    level = "info"
    company_types = ["rater", "provider", "utility", "eep_sponsor"]
    unique = True

    verbose_name = "Daily email sent when NEEA BPA completion/certifications occur"
    description = (
        "This is a daily email will be sent to rating company / program sponsor when a "
        "certifications occur."
    )

    companies_with_relationship_or_self = ["neea"]


class PivotalAdminDailyEmail(ModernMessage):
    title = "{title}"
    content = None
    email_content = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "templates", "home", "admin_daily_email.html")
    )

    category = "system"
    level = "info"

    unique = True

    verbose_name = "Daily email sent on status of Axis"
    description = "This is a daily email will be sent regarding the status of Axis."

    company_slugs = ["pivotal-energy-solutions"]


class HomeRelationshipRemovalErrorMessage(ModernMessage):
    title = "Home Association Removal Error"
    content = (
        "Unable to remove association for {owner} to {object}.  "
        "{owner} is an active customer; Please contact them for for removal."
    )
    category = "warning"
    level = "info"

    verbose_name = "Home Association Removal Error"
    description = "Sent when unable to remove association between Owner and Home"


class HomeChangeBuilderForSubdivisionMismatchMessage(ModernMessage):
    title = "Home and Subdivision Builder mismatch"
    content = (
        "You provided a builder {builder} which does not "
        "match the builder {sub_builder} which was specified "
        "for the subdivision {subdivision}, not adding association to {builder}"
    )
    category = "warning"
    level = "info"

    verbose_name = "Home and Subdivision Builder mismatch"
    description = "Sent when builder for home not match Builder for subdivision"


class HomeUserAttachedWithoutCompanyAssociationMessage(ModernMessage):
    title = "Attached User To Home without Company association"
    content = "The company {company_name} is not attached, but you added the user {user_full_name} to this home."

    category = "warning"
    level = "info"

    verbose_name = "Attached User To Home without Company association"
    description = (
        "When you attach user to Home, but there is no association between Users company and Home"
    )


class HomeIIPProgramOwnerHasNotAgreedToBeAttachedToHomeMessage(ModernMessage):
    title = "Program owner has not agreed to be attached to home"
    content = (
        "Program '{program_name}' has incentive dollars attached to in and the EEP "
        "Program owner {owner_company_name} has not agreed to be attached to home. "
        "You will not be able to certify this home until they are attached."
    )

    category = "warning"
    level = "info"

    verbose_name = "Program owner has not agreed to be attached to home"
    description = (
        "When Home has incentive dollars attached, but owner has not agreed to be attached to Home"
    )
