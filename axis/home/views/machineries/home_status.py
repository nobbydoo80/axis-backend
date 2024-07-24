""" Home Status Machinery"""


from datetime import datetime
from typing import List

from django.apps import apps
from django.urls import reverse

from axis.annotation.machinery import annotations_machinery_factory
from axis.checklist.forms import AsynchronousChecklistCreateForm
from axis.customer_eto.apps import ETO_GEN_3_SLUGS
from axis.customer_eto.calculator.eps import get_eto_calculation_completed_form
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.examine.machinery import ExamineMachinery, template_url
from axis.home.api import HomeStatusViewSet
from axis.home.forms import HomeStatusForm
from axis.home.models import EEPProgramHomeStatus
from axis.resnet.views import user_can_submit_to_resnet_registry, get_resnet_registry_action
from .active_floorplan import ActiveFloorplanExamineMachinery
from .annotations_home_status import AnnotationsHomeStatusExamineMachinery
from .hirl_project import (
    HIRLProjectSingleFamilyExamineMachinery,
    HIRLProjectMultiFamilyExamineMachinery,
    HIRLProjectLandDevelopmentExamineMachinery,
)
from .home_status_floorplan import HomeStatusFloorplanExamineMachinery
from .invoice_item_group import HIRLInvoiceItemGroupExamineMachinery

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

customer_neea_app = apps.get_app_config("customer_neea")
customer_hirl_app = apps.get_app_config("customer_hirl")
customer_wsu_app = apps.get_app_config("customer_wsu")
customer_eto_app = apps.get_app_config("customer_eto")


class HomeStatusExamineMachinery(ExamineMachinery):
    """Home Status Machinery"""

    model = EEPProgramHomeStatus
    form_class = HomeStatusForm
    type_name = "home_status"
    api_provider = HomeStatusViewSet

    template_set = "accordion"
    region_template = "examine/home/homestatus_region.html"
    detail_template = "examine/home/homestatus_detail.html"
    form_template = "examine/home/homestatus_form.html"

    simplified_status = None
    association = None
    is_contributor = True  # Defaults to True for same reason as home function flag does
    shares = None

    def configure_for_instance(self, instance):
        """Given an Instance configure me"""
        user = self.context["request"].user

        if not self.create_new:
            # Heavy, but necessary for ETO and checklist action buttons
            self.simplified_status = instance.get_simplified_status_for_user(user)

        # Fetch association and is_contributor flag so that actions can be restricted to readonly
        # NOTE: We're going soft on the association fetch because we don't use them pervasively.
        self.association = (
            instance.associations.filter_for_user(user).first() if instance.pk else None
        )
        if self.association:
            self.is_contributor = self.association.is_contributor

        self.shares = []
        if instance.pk and not self.association:
            self.shares = instance.associations.filter_by_user(user)

    def get_verbose_name(self, instance=None):
        return "Program"

    def get_object_name(self, instance):
        if instance.pk:
            return instance.eep_program.name
        return super(HomeStatusExamineMachinery, self).get_object_name(instance)

    def get_static_actions(self, instance: EEPProgramHomeStatus) -> dict:
        actions = super(HomeStatusExamineMachinery, self).get_static_actions(instance)

        user = self.context["request"].user

        if not instance.pk:
            return actions

        # Cog (superuser actions and infrequent actions)
        cog_actions = []
        if self.is_contributor:
            if user.is_superuser:
                update_stats_url = reverse("home:update_stats", kwargs={"pk": instance.pk})
                green_addendum_url = reverse(
                    "appraisal_institute:green_addendum", kwargs={"home_status": instance.pk}
                )
                cog_actions.extend(
                    [
                        {"name": "Update Stats", "href": update_stats_url, "icon": "tasks"},
                        {"name": "Green Addendum", "href": green_addendum_url, "icon": "file"},
                    ]
                )

            if instance.can_be_decertified(user):
                cog_actions.extend(
                    [
                        {"name": "Decertify", "instruction": "decertify", "icon": "history"},
                    ]
                )
            if user.company.slug in ["eto", "peci"] or user.is_superuser:
                if (
                    instance.eep_program.owner.slug == "eto"
                    and getattr(instance, "fasttracksubmission", False)
                    and not instance.eep_program.is_qa_program
                ):
                    fasttrack_debug_url = reverse(
                        "api_v3:project_tracker-xml", kwargs={"pk": instance.pk}
                    )

                    cog_actions.extend(
                        [
                            {
                                "name": "View Project Tracker XML",
                                "href": fasttrack_debug_url,
                                "icon": "code",
                            },
                        ]
                    )

                    try:
                        locked = instance.fasttracksubmission.is_locked()
                    except AttributeError:
                        locked = False

                    ft_icon = "long-arrow-right"
                    label = "Submit"
                    if locked:
                        ft_icon = "repeat"
                        label = "Re-Submit"

                    cog_actions.extend(
                        [
                            {
                                "name": "{label} to Project Tracker".format(label=label),
                                "instruction": "fasttrack",
                                "icon": ft_icon,
                            },
                        ]
                    )

            try:
                adjustment_allowed = instance.fasttracksubmission.can_payment_be_updated(user)
            except Exception:
                adjustment_allowed = False

            if adjustment_allowed:
                payment_adjustment_url = reverse(
                    "eto:payment_adjust", kwargs={"home_status": instance.pk}
                )
                cog_actions.extend(
                    [
                        {
                            "name": "Adjust Incentive Payment",
                            "href": payment_adjustment_url,
                            "icon": "edit",
                        },
                    ]
                )

        if user_can_submit_to_resnet_registry(instance, user):
            cog_actions.append(self.Action(**get_resnet_registry_action()))

        if (
            instance.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            and instance.state
            in [
                EEPProgramHomeStatus.PENDING_INSPECTION_STATE,
                EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_PROJECT_DATA,
                EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE,
            ]
            and (user.is_superuser or user.is_customer_hirl_company_member())
        ):
            cog_actions.extend(
                [
                    {
                        "name": "Bypass Rough QA",
                        "href": reverse("home:bypass_rough_qa", kwargs={"pk": instance.pk}),
                        "icon": "forward",
                    },
                ]
            )

        if len(cog_actions):
            actions.extend(
                [
                    self.Action(
                        "", icon="cog", instruction=None, type="dropdown", items=cog_actions
                    ),
                ]
            )

        if self.shares:
            sharing_items = [
                {
                    "name": "{}".format(share.user or share.company),
                }
                for share in self.shares
            ]
            actions.append(
                self.Action(
                    "Sharing ({})".format(len(self.shares)),
                    icon="users",
                    instruction=None,
                    type="dropdown",
                    items=sharing_items,
                )
            )

        # Abandon/Re-Instate button
        if (
            self.is_contributor
            and instance.eep_program.slug not in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
        ):
            next_state = instance.get_next_state()
            if next_state:
                if next_state == "to_abandoned_transition":
                    actions.append(
                        self.Action("Abandon", icon="chain-broken", instruction="toggle_abandon")
                    )
                else:
                    actions.append(
                        self.Action("Re-Instate", icon="chain", instruction="toggle_abandon")
                    )

        # Report button
        report_items = [
            {
                "name": "Project Report",
                "href": reverse("home:report:checklist", args=(instance.pk,)),
            },
        ]

        has_remrate_data = instance.floorplan and instance.floorplan.remrate_target
        has_simulation_data = instance.floorplan and instance.floorplan.simulation

        available_for_scoring_path_eep_programs = (
            customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
        )

        if instance.eep_program.slug in available_for_scoring_path_eep_programs:
            if instance.state == "complete" and instance.certification_date:
                report_items.append(
                    {
                        "name": "Scoring Path Certificate",
                        "href": reverse(
                            "home:report:customer_hirl_scoring_path_certificate",
                            kwargs={"pk": instance.pk},
                        ),
                    }
                )

                if (
                    getattr(instance, "customer_hirl_project", None)
                    and instance.customer_hirl_project.is_require_water_sense_certification
                    and instance.qastatus_set.filter(hirl_water_sense_confirmed=True).exists()
                ):
                    report_items.append(
                        {
                            "name": "WaterSense Certificate",
                            "href": reverse(
                                "home:report:customer_hirl_water_sense_certificate",
                                kwargs={"pk": instance.pk},
                            ),
                        }
                    )

        if (
            instance.eep_program.slug in customer_wsu_app.HERS_BROCHURE_PROGRAM_SLUGS
            and instance.state == "complete"
        ):
            if (
                user.is_superuser
                or (user.company and user.company.slug == customer_wsu_app.CUSTOMER_SLUG)
                or (user.company and user.company.company_type == "rater")
            ):
                report_items.append(
                    {
                        "name": "WSU HERS Brochure",
                        # Earth Advantage Appraisal Addendum
                        "href": reverse("customer_wsu:hers_brochure", kwargs={"pk": instance.pk}),
                    }
                )

        if has_remrate_data or instance.eep_program.owner.slug == customer_hirl_app.CUSTOMER_SLUG:
            if instance.eep_program.owner.slug == "eto":
                report_items.append(
                    {
                        "name": "HPH Cost Data Addendum",
                        # Earth Advantage Appraisal Addendum
                        "href": reverse(
                            "earth_advantage:eaaa_addendum", kwargs={"home_status": instance.pk}
                        ),
                    }
                )
            else:
                report_items.append(
                    {
                        "name": "G&EEA",
                        # Green & Energy Efficiency Appraisal Addendum
                        "href": reverse(
                            "appraisal_institute:green_addendum",
                            kwargs={"home_status": instance.pk},
                        ),
                    }
                )

        if (
            has_simulation_data
            and instance.eep_program.slug in ETO_GEN_3_SLUGS
            and getattr(instance, "fasttracksubmission", None)
        ):
            report_items.append(
                {
                    "name": "EPS Report",
                    "href": reverse("api_v3:eps_report-report", kwargs={"pk": instance.pk}),
                }
            )
        if (
            instance.eep_program.slug == "washington-code-credit"
            and getattr(instance, "fasttracksubmission", False)
            and not instance.eep_program.is_qa_program
        ):
            report_items.append(
                {
                    "name": "Washington Code Credit Report",
                    "href": reverse("api_v3:wcc_report-report", kwargs={"pk": instance.pk}),
                }
            )
        # NOTE: Releasing without report download support,
        # until they can get us a finalized pdf.

        # if instance.eep_program.slug in [
        #         'built-green-wa-prescriptive',
        #         'built-green-wa-performance']:
        #     report_items.append(self._get_built_green_wa_report_item(instance))

        actions.append(
            self.Action(
                "Reports", icon="file-o", instruction=None, type="dropdown", items=report_items
            )
        )

        # Checklist dropdown
        actions.append(self._get_checklist_actions(instance))

        return actions

    def _get_checklist_actions(self, instance: EEPProgramHomeStatus) -> dict:
        checklist_actions = [
            {"name": "View", "instruction": "view_checklist"},
        ]

        # TODO: Should this be dynamically based on some kind of active time window instead?
        checklist_blacklist = ["eto", "eto-2015", "eto-2016", "eto-2017"]

        if instance.eep_program.slug not in checklist_blacklist:
            checklist_actions.append(
                {
                    "name": "Download",
                    "instruction": None,
                    "href": reverse(
                        "home:download_single_homestatus",
                        kwargs={
                            "home_status": instance.id,
                        },
                    ),
                }
            )
            if self.is_contributor and self.simplified_status.can_edit:
                checklist_actions.append(
                    {
                        "name": "Upload",
                        "instruction": "upload_checklist",
                        "modal": {
                            "templateUrl": template_url("examine/home/upload_checklist.html")
                        },
                    }
                )

        return self.Action(
            "Checklist", icon="list-ul", instruction=None, type="dropdown", items=checklist_actions
        )

    def _get_built_green_wa_report_item(self, instance: EEPProgramHomeStatus) -> dict:
        return {
            "name": "Built Green Certificate of Merit",
            "href": reverse("home:report:built_green_wa", args=(instance.pk,)),
        }

    def get_default_actions(self, instance: EEPProgramHomeStatus) -> List[dict]:
        actions = super(HomeStatusExamineMachinery, self).get_default_actions(instance)

        user = self.context["request"].user

        if self.simplified_status:
            certify_action = None
            if self.simplified_status.can_certify:
                url = reverse("home:certify", kwargs={"pk": instance.pk})
                certify_action = self.Action(
                    "Certify",
                    instruction=None,
                    type="split-dropdown",
                    style="primary",
                    href=url,
                    items=[],
                )

                certify_action["items"].append(
                    {
                        "name": "Certify with Today's Date",
                        "instruction": "certify_today",
                    }
                )

            elif self.simplified_status.can_transition_to_certify:
                certify_action = self.Action(
                    "Ready to Certify", instruction="ready", style="primary"
                )

            if certify_action:
                for i, action in enumerate(actions):
                    if action["instruction"] == "edit":
                        actions.insert(i, certify_action)
                        break
                else:
                    actions.append(certify_action)

            if (
                instance.pk
                and getattr(instance, "customer_hirl_project", None)
                and instance.state
                in [
                    EEPProgramHomeStatus.COMPLETE_STATE,
                    EEPProgramHomeStatus.CERTIFICATION_PENDING_STATE,
                ]
            ):
                hirl_project = instance.customer_hirl_project
                final_childrens = hirl_project.vr_batch_submission_final_childrens.exclude(
                    home_status__state=EEPProgramHomeStatus.COMPLETE_STATE
                )
                if final_childrens:
                    actions.append(
                        self.Action(
                            "Certify Batch",
                            style="primary",
                            instruction="customer_hirl_certify_childrens",
                        )
                    )

        if (
            not self.create_new
            and (user.company.slug == "peci" or user.is_superuser)
            and instance.is_allowed_by_projecttracker()
            and instance.can_be_submitted_to_projecttracker()
        ):
            actions.append(
                self.Action(
                    "Submit to Project Tracker",
                    instruction="fasttrack",
                    style="primary",
                    icon="rocket",
                )
            )

        return actions

    def get_region_dependencies(self) -> dict:
        return {
            "home": [
                {
                    "field_name": "id",
                    "serialize_as": "home",
                }
            ],
        }

    def get_form_kwargs(self, instance: EEPProgramHomeStatus) -> dict:
        return {
            "user": self.context["request"].user,
        }

    def get_helpers(self, instance: EEPProgramHomeStatus) -> dict:
        helpers = super(HomeStatusExamineMachinery, self).get_helpers(instance)

        # The helpers in this machinery are pretty query-heavy.  Avoid running this code if the
        # main view has built the machinery with the lightweight=True flag in the context.
        if self.context.get("lightweight"):
            return helpers

        user = self.context["request"].user

        if not self.create_new:
            try:
                fuel_usage_annotation = instance.annotations.get(
                    type__slug="beat-annual-fuel-usage"
                ).content
            except instance.annotations.model.DoesNotExist:
                fuel_usage_annotation = None

            certify_today_url = "{}?certification_date={}".format(
                reverse("apiv2:home_status-certify", kwargs={"pk": instance.pk}),
                datetime.now().strftime("%Y-%m-%d"),
            )

            fasttrack_submission_url = reverse(
                "api_v3:project_tracker-submit", kwargs={"pk": instance.pk}
            )
            fasttrack_xml_url = reverse("api_v3:project_tracker-xml", kwargs={"pk": instance.pk})

            helpers["customer_hirl_certify_childrens_endpoint"] = reverse(
                "apiv2:home_status-customer-hirl-certify-childrens",
                kwargs={"pk": instance.pk},
            )

            helpers.update(
                {
                    "show_performance_items": (
                        instance.eep_program.slug
                        in [
                            "neea-energy-star-v3-performance",
                            "neea-performance-2015",
                            "neea-efficient-homes",
                        ]
                    ),
                    "program_requires_floorplan": instance.eep_program.requires_floorplan(),
                    "fasttrack_submission_url": fasttrack_submission_url,
                    "fasttrack_xml_url": fasttrack_xml_url,
                    "resnet_submission_url": reverse(
                        "apiv2:home_status-resnet", kwargs={"pk": instance.pk}
                    ),
                    "decertify_url": reverse(
                        "apiv2:home_status-decertify", kwargs={"pk": instance.pk}
                    ),
                    "certify_today_url": certify_today_url,
                    "state_transition_url": reverse(
                        "apiv2:home_status-transition", kwargs={"pk": instance.pk}
                    ),
                    "next_state": instance.get_next_state(),
                    "has_checklist": self.simplified_status.has_checklist
                    if self.simplified_status
                    else False,
                    "annotation_beats_annual_fuel_usage": fuel_usage_annotation,
                    "show_disclaimer": (
                        instance.eep_program.slug
                        in [
                            "neea-energy-star-v3-performance",
                            "neea-performance-2015",
                            "neea-efficient-homes",
                        ]
                    ),
                    "show_nwesh_disclaimer": (
                        instance.eep_program.slug
                        in ["neea-energy-star-v3-performance", "neea-performance-2015"]
                    ),
                    "show_hp_disclaimer": (instance.eep_program.slug in ["neea-efficient-homes"]),
                    "show_floorplan_review": (
                        instance.eep_program.owner.slug == "aps"
                        and (user.company.slug == "aps" or user.is_superuser)
                    ),
                    "collection_request": instance.collection_request_id,  # Potentially ``None``
                }
            )

        helpers["machinery"] = {}

        floorplans = []
        if instance.pk:
            floorplans = instance.floorplans.all()
        floorplan_context = dict(
            self.context,
            **{
                "home_status_id": instance.id,
            },
        )
        nested_floorplan_machinery = HomeStatusFloorplanExamineMachinery(
            objects=floorplans, context=floorplan_context
        )
        helpers["machinery"]["floorplan"] = nested_floorplan_machinery.get_summary()

        if (
            instance.pk
            and instance.eep_program
            and instance.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
        ):
            helpers["machinery"]["floorplan"] = None

        notes = (
            instance.annotations.filter_by_user(user=self.context["request"].user)
            if instance.pk
            else []
        )
        NotesMachinery = annotations_machinery_factory(
            EEPProgramHomeStatus, type_slug="note", form_class=None
        )
        notes_machinery = NotesMachinery(objects=notes, context=self.context)
        helpers["machinery"]["notes"] = notes_machinery.get_summary()

        if instance.pk:
            active_floorplan = instance.floorplan
            if active_floorplan:
                floorplan_context = dict(
                    self.context,
                    **{
                        "home_status_id": instance.id,
                    },
                )
                active_floorplan_machinery = ActiveFloorplanExamineMachinery(
                    instance=active_floorplan, context=floorplan_context
                )
                helpers["machinery"]["active_floorplan"] = active_floorplan_machinery.get_summary()

            helpers["is_customer_hirl_project_program"] = (
                instance.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            )

        if instance.pk and getattr(instance, "customer_hirl_project", None):
            hirl_project = instance.customer_hirl_project
            if hirl_project:
                if (
                    hirl_project.registration.project_type
                    == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
                ):
                    hirl_project_machinery = HIRLProjectSingleFamilyExamineMachinery(
                        instance=hirl_project, context={"request": self.context["request"]}
                    )
                    helpers["machinery"]["hirl_project"] = hirl_project_machinery.get_summary()
                elif (
                    hirl_project.registration.project_type
                    == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
                ):
                    hirl_project_machinery = HIRLProjectMultiFamilyExamineMachinery(
                        instance=hirl_project, context={"request": self.context["request"]}
                    )
                    helpers["machinery"]["hirl_project"] = hirl_project_machinery.get_summary()
                elif (
                    hirl_project.registration.project_type
                    == HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE
                ):
                    hirl_project_machinery = HIRLProjectLandDevelopmentExamineMachinery(
                        instance=hirl_project, context={"request": self.context["request"]}
                    )
                    helpers["machinery"]["hirl_project"] = hirl_project_machinery.get_summary()

                invoice_item_group_machinery = HIRLInvoiceItemGroupExamineMachinery(
                    objects=instance.invoiceitemgroup_set.all(),
                    context={"request": self.context["request"]},
                )
                helpers["machinery"][
                    "invoice_item_group_machinery"
                ] = invoice_item_group_machinery.get_summary()

        if not self.create_new and instance.eep_program.required_annotation_types.exists():
            nested_annotations_machinery = AnnotationsHomeStatusExamineMachinery(
                instance=instance, context={"request": self.context["request"]}
            )
            helpers["machinery"]["annotations"] = nested_annotations_machinery.get_summary()

        if (
            not self.create_new
            and "eto" in instance.eep_program.slug
            and not instance.eep_program.is_qa_program
        ):
            show_admin = user.is_superuser or user.company.slug in [
                "eto",
                "peci",
                "csg-qa",
            ]
            helpers["eps_showview"] = show_admin
            try:
                builder_updates = (
                    instance.fasttracksubmission.original_builder_incentive is not None
                )
                helpers["eps_show_original_builder_incentive"] = (
                    builder_updates and helpers["eps_showview"]
                )
                rater_updates = instance.fasttracksubmission.original_rater_incentive is not None
                helpers["eps_show_original_rater_incentive"] = (
                    rater_updates and helpers["eps_showview"]
                )
            except AttributeError:
                helpers["eps_show_original_builder_incentive"] = False
                helpers["eps_show_original_rater_incentive"] = False

            if instance.eep_program.slug not in ETO_GEN_3_SLUGS:
                helpers["show_legacy_eps_table"] = True
                helpers["eps_url"] = (
                    reverse("apiv2:home_status-detail", kwargs={"pk": instance.pk}) + "eps_data/"
                )
                calculations_form = get_eto_calculation_completed_form(instance)
                helpers["eps_calculations_form"] = calculations_form.as_p()
                helpers["eps_calculations_valid"] = calculations_form.is_valid()
            elif instance.eep_program.slug in ETO_GEN_3_SLUGS:
                helpers["show_eps_table"] = True
                url = f"api_v3:{instance.eep_program.slug.replace('-', '_')}-generate"
                helpers["eps_url"] = reverse(url, kwargs={"pk": instance.pk})
                if instance.state != "complete" and show_admin:
                    helpers["show_admin"] = True
                helpers["show_admin"] = True
                helpers["show_debug"] = user.is_superuser

        if not self.create_new and self.simplified_status.can_edit:
            form = AsynchronousChecklistCreateForm(initial={"company": user.company})
            helpers["checklist_upload_form"] = self.serialize_form_spec(instance, form)

        if not self.create_new and instance.eep_program.slug in NEEA_BPA_SLUGS:
            helpers["show_rtf_table"] = True
            helpers["has_bpa_affiliation"] = user.company.sponsors.filter(slug="bpa").exists()
            helpers["program_slug"] = instance.eep_program.slug

            can_view_utility_payment = any(
                [
                    user.is_superuser,
                    user.company.slug
                    in ["neea", "clearesult-qa", "qa-pacific-power-qa-wa"]
                    + customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS,
                ]
            )

            if can_view_utility_payment:
                helpers["show_utility_payment"] = True
                can_view_admin_data_post_certification = all(
                    [
                        # Reserved for supers (when circumstances are right and won't cause UI problems
                        user.is_superuser,
                        instance.standardprotocolcalculator_set.exclude(reports="{}")
                        .values_list("reports", flat=True)
                        .first(),
                    ]
                )
                if instance.state != "complete" or can_view_admin_data_post_certification:
                    helpers["show_admin"] = True
            helpers["rtf_url"] = reverse(
                "apiv2:home_status-rtf-calculator", kwargs={"pk": instance.pk}
            )

        if (
            not self.create_new
            and instance.eep_program.slug == "washington-code-credit"
            and not instance.eep_program.is_qa_program
        ):
            helpers["show_wcc_table"] = True

            wcc_admin_slugs = ["eto", "peci"]
            admin_view = user.is_superuser or user.company.slug in wcc_admin_slugs
            helpers["show_admin"] = instance.state != "complete" and admin_view
            helpers["wcc_url"] = reverse(
                "api_v3:washington_code_credit-generate", kwargs={"pk": instance.pk}
            )

        return helpers
