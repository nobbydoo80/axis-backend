"""menu_data.py: Menu builder for Axis"""

import logging

from django.apps import apps
from django.urls import reverse_lazy

from ..company.models import Company
from ..company.strings import COMPANY_TYPES_PLURAL

__author__ = "Steven Klass"
__date__ = "3/3/12 5:37 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Kevin Riggens"]

from axis.core.utils import get_frontend_url

log = logging.getLogger(__name__)

customer_hirl_app = apps.get_app_config("customer_hirl")
customer_neea_app = apps.get_app_config("customer_neea")
equipment_app = apps.get_app_config("equipment")
frontend_app = apps.get_app_config("frontend")
user_management_app = apps.get_app_config("user_management")


# pylint: disable=too-many-arguments, invalid-name
def GENERIC_MENUS(
    user,
    company_id=None,
    company_slug=None,
    company_name=None,
    company_type=None,
    company_is_eep_sponsor=False,
    sponsor_slugs=None,
    permissions=None,
    path="/",
):
    """A list of generic menus"""
    user_profile_url = reverse_lazy("profile:detail", kwargs={"pk": user.id})

    company_url = None
    if company_id and company_type:
        company_url = get_frontend_url("company", company_type, "detail", company_id)

    company_sponsors = sponsor_slugs if sponsor_slugs else []
    permissions = permissions if permissions else []
    return {
        "index": {
            "title": "Home",
            "path": reverse_lazy("home:list"),
            "conditions": "home.view_home" in permissions,
        },
        "login": {"title": "Logon", "path": reverse_lazy("auth:login"), "conditions": True},
        "logout": {"title": "Logout", "path": reverse_lazy("auth:logout"), "conditions": True},
        "contact": {
            "title": "Contact",
            "path": reverse_lazy("contact"),
        },
        "news": {
            "title": "News",
            "path": reverse_lazy("news"),
        },
        "products": {
            "title": "Products",
            "path": reverse_lazy("products"),
        },
        "pricing": {
            "title": "Pricing",
            "path": reverse_lazy("pricing"),
        },
        "about": {
            "title": "About",
            "path": reverse_lazy("about"),
        },
        "my_company": {
            "title": company_name if company_name else "My Company",
            "path": company_url,
            "conditions": bool(company_url),
        },
        "my_profile": {"title": "My User Profile", "path": user_profile_url, "conditions": True},
        "community_list": {
            "title": "Communities",
            "path": "community:list",
            "conditions": "community.view_community" in permissions,
        },
        "community_add": {
            "title": "Add Community",
            "path": "community:add",
            "conditions": "community.add_community" in permissions,
        },
        "subdivision_list": {
            "title": "Subdivisions/MF Developments",
            "path": "subdivision:list",
            "conditions": "subdivision.view_subdivision" in permissions,
        },
        "subdivision_add": {
            "title": "Add Subdivision/MF Development",
            "path": "subdivision:add",
            "conditions": "subdivision.add_subdivision" in permissions,
        },
        "energy_costs": {
            "title": "Energy Costs",
            "path": "report:subdivision",
            "conditions": "remrate_data.view_simulation" in permissions
            and (
                company_type not in ["builder", "hvac"]
                or company_slug not in ["trc", "advanced-energy"]
            ),
        },
        "home_list": {
            "title": "Projects",
            "path": "home:list",
            "conditions": "home.view_home" in permissions,
        },
        "home_add": {
            "title": "Add Project",
            "path": "home:add",
            "conditions": "home.add_home" in permissions,
        },
        "single_home_upload": {
            "title": "Single Project (Home) Upload",
            "path": "home:single_upload",
            "conditions": "home.add_home" in permissions,
        },
        "bulk_home_upload": {
            "title": "Bulk Project (Home) Upload",
            "path": "home:upload",
            "conditions": "home.add_home" in permissions,
        },
        "estar_labels": {
            "title": "ENERGY STAR Labels",
            "path": "home:report:energy_star_certificate",
            "conditions": company_type in ("rater", "provider", "eep")
            and company_slug not in ["trc", customer_hirl_app.CUSTOMER_SLUG]
            # if company have multiple sponsors ignore this rule
            and not (len(sponsor_slugs) == 1 and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs),
        },
        "home_certs": {
            "title": "Project Certificates",
            "path": "home:report:certificate",
            "conditions": company_type in ("rater", "provider", "eep")
            and company_slug not in ["trc", customer_hirl_app.CUSTOMER_SLUG]
            # if company have multiple sponsors ignore this rule
            and not (len(sponsor_slugs) == 1 and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs),
        },
        "home_status_report": {
            "title": "Project Status",
            "path": "home:report:status",
            "conditions": "home.view_home" in permissions,
        },
        "provider_dashboard": {
            "title": "Provider Dashboard",
            "path": "home:report:provider_dashboard",
            "conditions": (
                company_type == "provider"
                and company_slug not in ["trc", customer_hirl_app.CUSTOMER_SLUG]
                or company_type == "qa"
                and "neea" in sponsor_slugs
            ),
        },
        "floorplan_list": {
            "title": "Floorplans",
            "path": get_frontend_url("floorplans"),
            "conditions": "floorplan.view_floorplan" in permissions,
        },
        "eep_program_list": {
            "title": "Programs",
            "path": "eep_program:list",
            "conditions": "eep_program.view_eepprogram" in permissions
            and (
                company_slug != customer_hirl_app.CUSTOMER_SLUG
                and not user.is_sponsored_by_company(
                    customer_hirl_app.CUSTOMER_SLUG, only_sponsor=True
                )
            ),
        },
        "eep_program_add": {
            "title": "Program Add",
            "path": "eep_program:add",
            "conditions": user.is_superuser,
        },
        "builder_agreement_list": {
            "title": "Builder Agreements",
            "path": "builder_agreement:list",
            "conditions": "builder_agreement.view_builderagreement" in permissions,
        },
        "builder_agreement_add": {
            "title": "Add Builder Agreement",
            "path": "builder_agreement:add",
            "conditions": "builder_agreement.add_builderagreement" in permissions,
        },
        "builder_signed_report": {
            "title": "Builder Information Report",
            "path": "builder_agreement:status",
            "conditions": (
                company_is_eep_sponsor
                or company_type in ("builder", "provider")
                or company_slug == "aps"
            )
            and company_type not in ("hvac",)
            and company_slug != "advanced-energy"
            and "incentive_payment.view_incentivedistribution" in permissions,
        },
        "ipp_pending_list": {
            "title": "Pending IPP",
            "path": "incentive_payment:pending",
            "conditions": company_is_eep_sponsor
            and "incentive_payment.add_incentivedistribution" in permissions,
        },
        "incentive_payments_status": {
            "title": "Incentive Payments",
            "path": "incentive_payment:pending",
            "conditions": company_slug in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS
            and "incentive_payment.change_incentivepaymentstatus" in permissions,
        },
        "ipp_checks_list": {
            "title": "Incentive Checks",
            "path": "incentive_payment:list",
            "conditions": (
                company_is_eep_sponsor or company_type in ("builder", "provider", "rater")
            )
            and "incentive_payment.view_incentivedistribution" in permissions,
        },
        "ipp_control_center": {
            "title": "Incentive Processing",
            "path": "incentive_payment:control_center",
            "conditions": company_is_eep_sponsor
            and "incentive_payment.add_incentivedistribution" in permissions,
        },
        # 'ipp_legacy_import': {
        #     'title': 'Legacy IPP Import',
        #     'path': 'aps_ipp_legacy_add',
        #     'conditions': False
        # },
        "ipp_pending_failure_report": {
            "title": "Pending Incentive Payment Failure     Report",
            "path": "incentive_payment:failures",
            "conditions": "incentive_payment.view_incentivedistribution" in permissions
            and ("aps" in company_sponsors)
            and company_type in ("provider", "rater")
            and company_slug != "advanced-energy",
        },
        "remrate_list": {
            "title": "REM/Rate&#8482; Data",
            "path": "floorplan:input:remrate",
            "conditions": "remrate_data.view_simulation" in permissions
            and company_type != "hvac"
            and company_slug not in ["advanced-energy", "trc", customer_hirl_app.CUSTOMER_SLUG],
        },
        "ekotrope_list": {
            "title": "Ekotrope Data",
            "path": "floorplan:input:ekotrope",
            "conditions": "ekotrope.view_project" in permissions
            and company_type != "hvac"
            and company_slug != "advanced-energy",
        },
        # hide processed documents for Customer HIRL sponsored companies
        "processed_documents_list": {
            "title": "Processed Documents",
            "path": "async_document_list",
            "conditions": "filehandling.view_asynchronousprocesseddocument" in permissions,
        },
        "bulk_completed_checklist_upload": {
            "title": "Bulk Checklist Upload",
            "path": "checklist:bulk_checklist_upload",
            "conditions": "checklist.add_answer" in permissions,
        },
        "inspection_phase_list": {
            "title": "Inspection Phases",
            "path": "checklist:phase_list",
            "conditions": user.is_superuser and False,
        },
        "scheduling_home_assign": {
            "title": "Scheduled tasks",
            "path": "scheduling_home_assign",
            "conditions": "scheduling.view_constructionstatus" in permissions,
        },
        "scheduling_home_list": {
            "title": "Construction Schedule",
            "path": "scheduling_home_list",
            "conditions": False,
        },
        "construction_stage_list": {
            "title": "Construction Stages",
            "path": "construction_stage_list",
            "conditions": "scheduling.view_constructionstatus" in permissions
            and company_type in ("rater", "provider"),
        },
        "sampling_list": {
            "title": "Sample Sets",
            "path": "sampleset:list",
            "conditions": "sampleset.view_sampleset" in permissions,
        },
        "sampling_control": {
            "title": "Sampling Control",
            "path": "sampleset:control_center",
            "conditions": "sampleset.view_samplesethomestatus" in permissions,
        },
        # 'sampling_eligibility': {
        #     'title': 'Sampling Eligibility',
        #     'path': 'sampling_eligibility',
        #     'conditions':
        #         company_type in ('rater', 'provider') and
        #         user.has_perm('sampling.view_sampleset') and user.is_superuser
        # },
        "annotation_types": {
            "title": "Annotations",
            "path": "annotation:manage",
            "conditions": "annotation.add_type" in permissions,
        },
        "message_list": {
            "title": "Message Center",
            "path": "messaging:list",
            "conditions": "messaging.view_message" in permissions,
        },
        "associations_dashboard": {
            "title": "Home Sharing",
            "path": "relationship:associations",
            "conditions": user.is_superuser,
        },
        "user_add": {
            "title": "Add User",
            "path": "tensor_registration:register",
            "conditions": "core.add_user" in permissions,
        },
        "accreditation_approvals": {
            "title": "Accreditation",
            "path": "user_management:accreditation:control_center_list",
            "conditions": company_slug
            in user_management_app.ACCREDITATION_APPLICABLE_COMPANIES_SLUGS,
        },
        "equipment_approvals": {
            "title": "Equipment",
            "path": "equipment:control_center_new_list",
            "conditions": company_slug in equipment_app.EQUIPMENT_APPLICABLE_COMPANIES_SLUGS,
        },
        "training_approvals": {
            "title": "Training",
            "path": "user_management:training:control_center_new_list",
            "conditions": company_slug in user_management_app.TRAINING_APPLICABLE_COMPANIES_SLUGS,
        },
        "certification_metric_approvals": {
            "title": "Certification Metrics",
            "path": "user_management:certification_metric:control_center_list",
            "conditions": user.is_authenticated
            and user.company
            and user.is_company_admin
            and user.company.slug
            in user_management_app.CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS,
        },
        "inspection_grade_approvals": {
            "title": "Grading",
            "path": f"/{frontend_app.DEPLOY_URL}user_management/inspection_grades",
            "conditions": user.is_authenticated
            and user.company
            and (
                (
                    user.is_company_type_member("rater")
                    and user.is_sponsored_by_company(customer_hirl_app.CUSTOMER_SLUG)
                )
                or user.company.slug
                in user_management_app.INSPECTION_GRADE_APPLICABLE_COMPANIES_SLUGS
            ),
        },
        "scheduling_tasks": {
            "title": "Scheduling",
            "path": f"/{frontend_app.DEPLOY_URL}scheduling/tasks",
            "conditions": user.is_authenticated and user.is_company_admin,
        },
        "geea_report": {
            "title": "Green & Energy Efficient Addendum",
            "path": "appraisal_institute:green_addendum",
            "conditions": "customer_appraisal_institute.view_geeadata" in permissions,
        },
        "contact_reports": {
            "title": "Contact Reports",
            "conditions": company_slug == "neea",
        },
        "builder_contact_report": {
            "title": "Builder Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "builder"}),
            "conditions": company_type != "builder",
        },
        "provider_contact_report": {
            "title": "Provider Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "provider"}),
            "conditions": company_type != "provider",
        },
        "rater_contact_report": {
            "title": "Rater Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "rater"}),
            "conditions": company_type != "rater",
        },
        "utility_contact_report": {
            "title": "Utility Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "utility"}),
            "conditions": company_type != "utility",
        },
        "qa_contact_report": {
            "title": "QA Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "qa"}),
            "conditions": company_type != "qa",
        },
        "hvac_contact_report": {
            "title": "HVAC Contact Report",
            "path": reverse_lazy("company:contact_list", kwargs={"type": "hvac"}),
            "conditions": company_type != "hvac",
        },
        "search": {
            "title": "Search",
            "path": "search:search",
            "conditions": user.is_authenticated,
        },
        # APS
        "aps_legacy_builder_list": {
            "title": "Builders",
            "path": "aps_legacy_builder_list_view",
            "conditions": "customer_aps.view_legacyapsbuilder" in permissions
            and company_slug == "aps",
        },
        "aps_legacy_subdivision_list": {
            "title": "Subdivisions",
            "path": "aps_legacy_subdivision_list_view",
            "conditions": "customer_aps.view_legacyapssubdivision" in permissions
            and company_slug == "aps",
        },
        "aps_legacy_home_list": {
            "title": "Homes",
            "path": "aps_legacy_home_list_view",
            "conditions": "customer_aps.view_legacyapshome" in permissions
            and company_slug == "aps",
        },
        "aps_meterset_import": {
            "title": "Meter Set Import",
            "path": "aps_homes_list_view",
            "conditions": "customer_aps.view_apshome" in permissions and company_slug == "aps",
        },
        "custom_data_export": {
            "title": "Custom Data Export",
            "path": "api_v3:aps_home_data-list",
            "conditions": "customer_aps.view_apshome" in permissions and company_slug == "aps",
        },
        # NEEA
        "neea_legacy_partners_list": {
            "title": "Partners",
            "path": "neea_legacy_partners_list",
            "conditions": company_slug == "neea",
        },
        "neea_legacy_home_list": {
            "title": "Homes",
            "path": "neea_legacy_home_list",
            "conditions": company_slug == "neea",
        },
        "neea_utility_report": {
            "title": "NEEA Utility Report",
            "path": "neea_utility_report",
            "conditions": all(
                (
                    "neea" in company_sponsors or company_slug == "neea",
                    company_type not in ["rater", "provider"],
                )
            ),
        },
        "neea_model_requirements_15p7p1": {
            "title": "NW Modeling Requirements REM/Rate 15.7.1",
            "path": "https://betterbuiltnw.com/resources/northwest-modeling-requirements-v18.1",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_remrate_library_15p7p1": {
            "title": "REM/Rate UDRHs 15.7.1",
            "path": "https://betterbuiltnw.com/resources/libraries-udrh-v15.7.1",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_modeling_flowchart": {
            "title": "Equipment Modeling Flowchart REM/Rate 15.7.1",
            "path": "https://betterbuiltnw.com/resources/equipmentflowchart",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_betterbuiltNW_website": {
            "title": "BetterBuiltNW",
            "path": "https://betterbuiltnw.com/",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_water_heater_list": {
            "title": "Water Heater List",
            "path": "https://neea.org/img/documents/qualified-products-list.pdf",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_clothes_dryer": {
            "title": "Clothes Dryer List",
            "path": "https://conduitnw.org/Pages/File.aspx?rid=2844",
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_performance_label_template": {
            "title": "Performance Test Label Template",
            "path": (
                "http://www.northwestenergystar.com/sites/default/files/"
                "resources/PerformTestSticker_editable_FINAL.pdf"
            ),
            "conditions": ("neea" in company_sponsors) or company_slug == "neea",
            "url_attrs": {"target": "_blank"},
        },
        "neea_calculator_v2": {
            "title": "BetterBuilt<sup>NW</sup> Performance Path Savings Estimator V2",
            "path": "neea_calculator_v2",
            "conditions": (
                "neea" in company_sponsors
                and company_type in ["rater", "provider", "qa", "utility"]
            )
            or company_slug == "neea",
        },
        "neea_calculator_v3": {
            "title": "BetterBuilt<sup>NW</sup> Performance Path Savings Estimator V3",
            "path": "neea_calculator_v3",
            "conditions": (
                "neea" in company_sponsors
                and company_type in ["rater", "provider", "qa", "utility"]
            )
            or company_slug == "neea",
        },
        # BPCA
        "bpca_report": {
            "title": "BPCA Status Report",
            "path": "integralbuilding:bpca_report",
            "conditions": company_slug == "integral-building",
        },
        # ETO
        "eto_calculator": {
            "title": "EPS Calculator",
            "path": "eto:calculator",
            "conditions": ("home.add_home" in permissions and "eto" in company_sponsors),
        },
        "eto_calculator_basic": {
            "title": "EPS Calculator Basic",
            "path": "eto:basic_calculator",
            "conditions": ("home.add_home" in permissions and "eto" in company_sponsors),
        },
        "eto_eps_report": {
            "title": "EPS Report",
            "path": "eto:download",
            "conditions": ("home.view_home" in permissions and "eto" in company_sponsors),
        },
        "eto_washington_code_credit_upload": {
            "title": "Washington Code Credit Upload",
            "path": "eto:wcc-upload",
            "conditions": ("home.view_home" in permissions and "eto" in company_sponsors),
        },
        "eto_wcc_project_tracker": {
            "title": "Project Tracker Dashboard",
            "path": f"/{frontend_app.DEPLOY_URL}project_tracker_submissions",
            "conditions": ("home.view_home" in permissions and "eto" in company_sponsors),
        },
        # HIRL
        "hirl_rpc_updater_request_list": {
            "title": "NGBS VR Updater Tool",
            "path": "/{}hi/hirl_rpc_updater_request_list/create".format(frontend_app.DEPLOY_URL),
            "conditions": (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in [
                        Company.RATER_COMPANY_TYPE,
                    ]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_builder_enrollment": {
            "title": "NGBS Client Enrollment",
            "path": reverse_lazy("hirl:enroll"),
            "conditions": (
                customer_hirl_app.ENROLLMENT_ENABLED
                and "customer_hirl.add_builderagreement" in permissions
            ),
        },
        "hirl_builder_agreement_list": {
            "title": "NGBS Client Agreements",
            "path": reverse_lazy("hirl:agreements:list"),
            "conditions": (
                customer_hirl_app.ENROLLMENT_ENABLED
                and company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in [
                        "rater",
                    ]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_verifier_agreement_enrollment": {
            "title": "NGBS Verifier Agreement Enrollment",
            "path": reverse_lazy("hirl:verifier_agreements:enroll"),
            "conditions": (
                customer_hirl_app.VERIFIER_AGREEMENT_ENROLLMENT_ENABLED
                and "customer_hirl.add_verifieragreement" in permissions
            ),
        },
        "hirl_verifier_agreement_list": {
            "title": "NGBS Verifier Agreements",
            "path": reverse_lazy("hirl:verifier_agreements:list"),
            "conditions": (
                user.is_authenticated
                and customer_hirl_app.ENROLLMENT_ENABLED
                and (
                    company_slug == customer_hirl_app.CUSTOMER_SLUG
                    or (
                        "customer_hirl.add_verifieragreement" in permissions
                        and company_type in ["rater", "provider"]
                        and user.is_company_admin
                    )
                )
            ),
        },
        "hirl_project_control_center": {
            "title": "NGBS Project Registration",
            "path": f"/{frontend_app.DEPLOY_URL}hi/projects",
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in ["builder", "architect", "communityowner", "developer", "rater", "provider"]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_project_registration_control_center": {
            "title": "NGBS MF Developments",
            "path": f"/{frontend_app.DEPLOY_URL}hi/project_registrations",
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in ["builder", "architect", "communityowner", "developer", "rater", "provider"]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_project_invoice_item_groups": {
            "title": "NGBS Invoice Management",
            "path": "/{}hi/invoice_item_groups".format(frontend_app.DEPLOY_URL),
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in ["builder", "architect", "communityowner", "developer", "rater", "provider"]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                    and user.is_company_admin
                )
            ),
        },
        "hirl_project_invoices": {
            "title": "NGBS Invoices",
            "path": "/{}hi/invoices".format(frontend_app.DEPLOY_URL),
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in ["builder", "architect", "communityowner", "developer", "rater", "provider"]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_qa_dashboard": {
            "title": "NGBS QA Dashboard",
            "path": "/{}hi/qa/dashboard".format(frontend_app.DEPLOY_URL),
            "conditions": user.is_authenticated and company_slug == customer_hirl_app.CUSTOMER_SLUG,
        },
        "hirl_scoring_upload": {
            "title": "NGBS Verification Report Upload",
            "path": f"/{frontend_app.DEPLOY_URL}hi/scoring_upload",
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or company_type in ["rater", "provider"]
                and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
            ),
        },
        "hirl_jamis_dashboard": {
            "title": "JAMIS Dashboard",
            "path": "/{}hi/jamis/dashboard".format(frontend_app.DEPLOY_URL),
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and company_slug == customer_hirl_app.CUSTOMER_SLUG,
        },
        "hirl_verifier_central": {
            "title": "NGBS Verifier Central",
            "path": f"/{frontend_app.DEPLOY_URL}hi/verifier/{user.id}/resources",
            "conditions": user.is_authenticated
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or company_type in ["rater", "provider"]
                and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
            ),
        },
        "hirl_bulk_certificate_download": {
            "title": "NGBS Download Certificates",
            "path": f"/{frontend_app.DEPLOY_URL}hi/projects/certificate/download",
            "conditions": user.is_authenticated
            and customer_hirl_app.HIRL_PROJECT_ENABLED
            and (
                company_slug == customer_hirl_app.CUSTOMER_SLUG
                or (
                    company_type
                    in ["builder", "architect", "communityowner", "developer", "rater", "provider"]
                    and customer_hirl_app.CUSTOMER_SLUG in sponsor_slugs
                )
            ),
        },
        "hirl_builder_central": {
            "title": "NGBS Builder Central",
            "path": f"/{frontend_app.DEPLOY_URL}ngbs/builder/central",
            "conditions": True,
        },
        "hirl_copy_move_ca_coi": {
            "title": "Copy/Move Client Agreement/COI",
            "path": f"/{frontend_app.DEPLOY_URL}hi/copy/ca",
            "conditions": user.is_authenticated and company_slug == customer_hirl_app.CUSTOMER_SLUG,
        },
        "sponsor_preferences_create": {
            "title": "Create Affiliation",
            "path": f"/{frontend_app.DEPLOY_URL}sponsor_preferences/create",
            "conditions": user.is_authenticated and company_slug == customer_hirl_app.CUSTOMER_SLUG,
        },
        "ngbs_scoring_tools": {
            "title": "NGBS Scoring Tools",
            "path": "https://www.homeinnovation.com/greenscoring",
            "conditions": (customer_hirl_app.CUSTOMER_SLUG in company_sponsors)
            or company_slug == customer_hirl_app.CUSTOMER_SLUG,
            "url_attrs": {"target": "_blank"},
        },
        "ngbs_marketing_materials": {
            "title": "NGBS Marketing Materials",
            "path": "https://www.homeinnovation.com/marketgreencertified",
            "conditions": (customer_hirl_app.CUSTOMER_SLUG in company_sponsors)
            or company_slug == customer_hirl_app.CUSTOMER_SLUG,
            "url_attrs": {"target": "_blank"},
        },
        "ngbs_green_site": {
            "title": "NGBS Green Site",
            "path": "https://www.homeinnovation.com/green",
            "conditions": (customer_hirl_app.CUSTOMER_SLUG in company_sponsors)
            or company_slug == customer_hirl_app.CUSTOMER_SLUG,
            "url_attrs": {"target": "_blank"},
        },
        "ngbs_training_site": {
            "title": "NGBS Training Site",
            "path": "https://ngbsgreenpro.homeinnovation.com/",
            "conditions": (customer_hirl_app.CUSTOMER_SLUG in company_sponsors)
            or company_slug == customer_hirl_app.CUSTOMER_SLUG,
            "url_attrs": {"target": "_blank"},
        },
        "ngbs_metrics": {
            "title": "NGBS Metrics",
            "path": f"/{frontend_app.DEPLOY_URL}misc/dashboard",
            "conditions": company_slug == customer_hirl_app.CUSTOMER_SLUG,
        },
        # Support
        "support": {
            "title": "Support",
            "path": "http://support.pivotalenergysolutions.com/login",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_authenticated,
        },
        "admin": {"title": "Admin", "path": "/admin", "conditions": user.is_superuser},
        "system_messenger": {
            "title": "System Messenger",
            "path": reverse_lazy("system_messenger"),
            "conditions": user.is_superuser,
        },
        "impersonate": {
            "title": "Impersonate",
            "path": "/impersonate/list/?next={path}".format(path=path),
            "conditions": user.is_superuser,
        },
        "rabbitmq": {"title": "RabbitMQ", "path": "/rabbitmq", "conditions": user.is_superuser},
        "splunk": {
            "title": "Splunk Analytics",
            "path": "https://analytics.pivotalenergy.net",
            "conditions": user.is_superuser,
        },
        "analytics": {
            "title": "Google Analytics",
            "path": "https://www.google.com/analytics/web/?"
            "hl=en&pli=1#home/a26647319w51473920p52173021/",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "webmaster_tools": {
            "title": "Google Webmaster Tools",
            "path": "https://www.google.com/webmasters/tools/dashboard?"
            "hl=en&siteUrl=http%3A%2F%2Faxis.pivotalenergy.net%2F",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "aws_console": {
            "title": "Amazon AWS",
            "path": "https://console.aws.amazon.com/",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "ec2": {
            "title": "EC2",
            "path": "https://console.aws.amazon.com/ec2/home?region=us-west-1#",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "rds": {
            "title": "RDS",
            "path": "https://console.aws.amazon.com/rds/home?region=us-west-1",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "elasticache": {
            "title": "ElastiCache",
            "path": "https://console.aws.amazon.com/elasticache/home?region=us-west-1",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "route_53": {
            "title": "Route 53",
            "path": "https://console.aws.amazon.com/route53/home?region=us-west-1",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "cloud_watch": {
            "title": "Cloud Watch",
            "path": "https://console.aws.amazon.com/cloudwatch/home?region=us-west-1",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "production_load": {
            "title": "Production CPU Load",
            "path": (
                "https://console.aws.amazon.com/cloudwatch/home"
                "?region=us-west-1#metrics:graph=!D03!E07!ET6!MN5!NS2!PD1!SS4!ST0!VA-PT6H~300"
                "~AWS%252FEC2~AutoScalingGroupName~Average~CPUUtilization~P0D~production"
            ),
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "beta_load": {
            "title": "Beta CPU Load",
            "path": (
                "https://console.aws.amazon.com/cloudwatch/home"
                "?region=us-west-1#metrics:graph=!D03!E07!ET6!MN5!NS2!PD1!SS4!ST0!VA-PT6H~300"
                "~AWS%252FEC2~AutoScalingGroupName~Average~CPUUtilization~P0D~beta"
            ),
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "demo_load": {
            "title": "Demo CPU Load",
            "path": (
                "https://console.aws.amazon.com/cloudwatch/home"
                "?region=us-west-1#metrics:graph=!D03!E07!ET6!MN5!NS2!PD1!SS4!ST0!VA-PT6H~300"
                "~AWS%252FEC2~AutoScalingGroupName~Average~CPUUtilization~P0D~demo"
            ),
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "staging_load": {
            "title": "Staging CPU Load",
            "path": (
                "https://console.aws.amazon.com/cloudwatch/home"
                "?region=us-west-1#metrics:graph=!D03!E07!ET6!MN5!NS2!PD1!SS4!ST0!VA-PT6H~300"
                "~AWS%252FEC2~AutoScalingGroupName~Average~CPUUtilization~P0D~staging"
            ),
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "status": {
            "title": "Status",
            "path": "status",
            "url_attrs": {"target": "_blank"},
            "conditions": user.is_superuser,
        },
        "cities": {
            "title": "Cities",
            "path": f"/{frontend_app.DEPLOY_URL}geographic/city",
            "conditions": user.is_superuser,
        },
    }


# pylint: disable=unused-argument,invalid-name
def COMPANY_MENUS(user, company_type=None, permissions=None, path="/"):
    """List the basic company menus"""

    permissions = permissions if permissions else []

    data = {}
    for co_type, (verbose_name, verbose_name_plural) in COMPANY_TYPES_PLURAL.items():
        try:
            view_perm = "company.view_%sorganization" % co_type in permissions
        except AttributeError:
            view_perm = False

        data["{company_type}_list".format(company_type=co_type)] = {
            "title": verbose_name_plural,
            "conditions": view_perm and company_type != co_type,
            "path": get_frontend_url("company", co_type),
        }
    return data


# pylint: disable=too-many-arguments, invalid-name
def MENU_ITEMS(
    user,
    company_id=None,
    company_slug=None,
    company_name=None,
    company_type=None,
    company_is_eep_sponsor=False,
    sponsor_slugs=None,
    permissions=None,
    path="/",
    **kwargs,
):
    """Return all menu data."""
    data = COMPANY_MENUS(user, company_type=company_type, permissions=permissions, path=path)
    data.update(
        GENERIC_MENUS(
            user,
            company_id=company_id,
            company_slug=company_slug,
            company_name=company_name,
            company_type=company_type,
            company_is_eep_sponsor=company_is_eep_sponsor,
            sponsor_slugs=sponsor_slugs,
            permissions=permissions,
            path=path,
        )
    )
    return data
