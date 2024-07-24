"""customer_hirl_project.py: """

__author__ = "Artem Hruzd"
__date__ = "02/04/2021 21:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps

from axis.core.views.machineries import ContactCardReadOnlyExamineMachinery
from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
from axis.examine import PanelMachinery
from axis.home.api import HomeStatusHIRLProjectViewSet, HomeStatusViewSet
from axis.home.forms import (
    HomeStatusHIRLSingleFamilyProjectForm,
    HomeStatusHIRLMultiFamilyProjectForm,
    HomeStatusForm,
    HomeStatusHIRLLandDevelopmentProjectForm,
)
from axis.home.models import EEPProgramHomeStatus

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectSingleFamilyExamineMachinery(PanelMachinery):
    model = HIRLProject
    form_class = HomeStatusHIRLSingleFamilyProjectForm
    api_provider = HomeStatusHIRLProjectViewSet
    can_add_new = False
    type_name = "home_status_hirl_project"

    region_template = "examine/home/hirl_project_region_panel.html"
    detail_template = "examine/home/hirl_project_sf_detail.html"
    form_template = "examine/home/hirl_project_sf_form.html"

    def can_delete_object(self, instance, user=None):
        return False

    def get_form_kwargs(self, instance):
        kwargs = super(HIRLProjectSingleFamilyExamineMachinery, self).get_form_kwargs(instance)
        if instance:
            kwargs["eep_program_slug"] = instance.registration.eep_program.slug
            kwargs["is_accessory_structure"] = instance.is_accessory_structure
            kwargs["is_accessory_dwelling_unit"] = instance.is_accessory_dwelling_unit
        return kwargs

    def get_helpers(self, instance):
        helpers = super(HIRLProjectSingleFamilyExamineMachinery, self).get_helpers(instance)
        if instance:
            eep_program_slug = instance.registration.eep_program.slug
            helpers["is_require_rough_inspection"] = (
                eep_program_slug in customer_hirl_app.REQUIRE_ROUGH_INSPECTION_PROGRAM_LIST
            )
            helpers["is_require_water_sense_certification"] = (
                eep_program_slug in customer_hirl_app.WATER_SENSE_PROGRAM_LIST
            )
            helpers["is_require_wri_certification"] = (
                eep_program_slug in customer_hirl_app.WRI_SEEKING_PROGRAM_LIST
            )
            helpers["is_build_to_rent"] = instance.registration.is_build_to_rent
            helpers["is_appeals_project"] = instance.is_appeals_project
        return helpers


class HIRLProjectMultiFamilyExamineMachinery(PanelMachinery):
    model = HIRLProject
    form_class = HomeStatusHIRLMultiFamilyProjectForm
    api_provider = HomeStatusHIRLProjectViewSet
    can_add_new = False
    type_name = "home_status_hirl_project"

    region_template = "examine/home/hirl_project_region_panel.html"
    detail_template = "examine/home/hirl_project_mf_detail.html"
    form_template = "examine/home/hirl_project_mf_form.html"

    def can_delete_object(self, instance, user=None):
        return False

    def get_form_kwargs(self, instance):
        kwargs = super(HIRLProjectMultiFamilyExamineMachinery, self).get_form_kwargs(instance)
        if instance:
            kwargs["eep_program_slug"] = instance.registration.eep_program.slug
            kwargs["is_accessory_structure"] = instance.is_accessory_structure
            kwargs["is_include_commercial_space"] = instance.is_include_commercial_space
            kwargs["is_accessory_dwelling_unit"] = instance.is_accessory_dwelling_unit
        return kwargs

    def get_helpers(self, instance):
        helpers = super(HIRLProjectMultiFamilyExamineMachinery, self).get_helpers(instance)
        if instance:
            eep_program_slug = instance.registration.eep_program.slug
            helpers["is_require_rough_inspection"] = (
                eep_program_slug in customer_hirl_app.REQUIRE_ROUGH_INSPECTION_PROGRAM_LIST
            )
            helpers["is_require_water_sense_certification"] = (
                eep_program_slug in customer_hirl_app.WATER_SENSE_PROGRAM_LIST
            )
            helpers["is_require_wri_certification"] = (
                eep_program_slug in customer_hirl_app.WRI_SEEKING_PROGRAM_LIST
            )
            helpers["is_appeals_project"] = instance.is_appeals_project
        return helpers


class HIRLProjectLandDevelopmentExamineMachinery(PanelMachinery):
    model = HIRLProject
    form_class = HomeStatusHIRLLandDevelopmentProjectForm
    api_provider = HomeStatusHIRLProjectViewSet
    can_add_new = False
    type_name = "home_status_hirl_project"

    region_template = "examine/home/hirl_project_region_panel.html"
    detail_template = "examine/home/hirl_project_ld_detail.html"
    form_template = "examine/home/hirl_project_ld_form.html"

    def can_delete_object(self, instance, user=None):
        return False

    def get_helpers(self, instance):
        helpers = super(HIRLProjectLandDevelopmentExamineMachinery, self).get_helpers(instance)
        helpers["registration_projects_list"] = []
        for project in (
            instance.registration.projects.all()
            .order_by("land_development_phase_number")
            .select_related("home_status", "home_status__eep_program", "home_status__home")
        ):
            helpers["registration_projects_list"].append(
                {
                    "id": project.id,
                    "home_status_id": project.home_status.id,
                    "home_status_url": project.home_status.get_absolute_url(),
                    "home_status_address": f'<a href="{project.home_status.get_absolute_url()}">'
                    f"{project.home_status.home.get_home_address_display()} - "
                    f"{project.home_status.eep_program} "
                    f"({project.home_status.get_state_display()})</a>",
                }
            )
        return helpers


class HIRLProjectRegistrationContactsHomeStatusExamineMachinery(PanelMachinery):
    """Home Status Machinery"""

    model = EEPProgramHomeStatus
    form_class = HomeStatusForm
    type_name = "hirl_project_registration_home_status"
    api_provider = HomeStatusViewSet

    template_set = "accordion"
    region_template = "examine/home/hirl_project_registration_contacts_homestatus_region.html"
    detail_template = "examine/home/hirl_project_registration_contacts_homestatus_detail.html"

    can_add_new = False

    def get_form_kwargs(self, instance):
        return {
            "user": self.context["request"].user,
        }

    def get_object_name(self, instance):
        if instance.pk:
            return instance.eep_program.name
        return super(
            HIRLProjectRegistrationContactsHomeStatusExamineMachinery, self
        ).get_object_name(instance)

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False

    def get_helpers(self, instance):
        helpers = super(
            HIRLProjectRegistrationContactsHomeStatusExamineMachinery, self
        ).get_helpers(instance)
        kwargs = {"context": self.context}
        helpers["machineries"] = {}

        verifier_organization_contact = (
            instance.customer_hirl_project.registration.registration_user.contact_cards.first()
        )

        if verifier_organization_contact:
            machinery = ContactCardReadOnlyExamineMachinery(
                instance=verifier_organization_contact,
                **kwargs,
            )
            helpers["machineries"]["verifier_organization_contact"] = machinery.get_summary()

        builder_organization_contact = (
            instance.customer_hirl_project.registration.builder_organization_contact
        )
        if builder_organization_contact:
            machinery = ContactCardReadOnlyExamineMachinery(
                instance=builder_organization_contact,
                **kwargs,
            )
            helpers["machineries"]["builder_organization_contact"] = machinery.get_summary()

        if (
            instance.customer_hirl_project.registration.project_type
            == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
        ):
            architect_organization_contact = (
                instance.customer_hirl_project.registration.architect_organization_contact
            )
            if architect_organization_contact:
                machinery = ContactCardReadOnlyExamineMachinery(
                    instance=architect_organization_contact,
                    **kwargs,
                )
                helpers["machineries"]["architect_organization_contact"] = machinery.get_summary()

            developer_organization_contact = (
                instance.customer_hirl_project.registration.developer_organization_contact
            )

            if developer_organization_contact:
                machinery = ContactCardReadOnlyExamineMachinery(
                    instance=developer_organization_contact,
                    **kwargs,
                )
                helpers["machineries"]["developer_organization_contact"] = machinery.get_summary()

            community_owner_organization_contact = (
                instance.customer_hirl_project.registration.community_owner_organization_contact
            )

            if community_owner_organization_contact:
                machinery = ContactCardReadOnlyExamineMachinery(
                    instance=instance.customer_hirl_project.registration.community_owner_organization_contact,
                    **kwargs,
                )
                helpers["machineries"][
                    "community_owner_organization_contact"
                ] = machinery.get_summary()
        return helpers
