__author__ = "Michael Jeffrey"
__date__ = "3/3/16 10:57 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

from django.apps import apps
from django.urls import reverse
from django.utils.functional import cached_property

from axis import examine
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisExamineView
from axis.core.views.machinery import AxisPrimaryMachinery
from axis.eep_program.api import EEPProgramViewSet
from axis.eep_program.forms import EEPProgramForm
from axis.eep_program.models import EEPProgram

customer_hirl_app = apps.get_app_config("customer_hirl")


class EEPProgramExamineView(AuthenticationMixin, AxisExamineView):
    model = EEPProgram

    @cached_property
    def is_customer_hirl_view(self):
        return (
            self.request.user.is_sponsored_by_company(
                customer_hirl_app.CUSTOMER_SLUG, only_sponsor=True
            )
            or self.request.user.is_customer_hirl_company_member()
        )

    def has_permission(self):
        if self.create_new:
            return self.request.user.is_superuser
        return True

    def get_template_names(self):
        if self.is_customer_hirl_view:
            return "eep_program/eepprogram_customer_hirl_examine.html"
        return super(EEPProgramExamineView, self).get_template_names()

    def get_queryset(self):
        return self.model.objects.filter_by_user(user=self.request.user, visible_for_use=True)

    def get_machinery(self):
        machineries = {}
        kwargs = {
            "instance": self.object,
            "create_new": self.create_new,
            "context": {"request": self.request},
        }

        primary_machinery_cls = EEPProgramExamineMachinery

        if self.is_customer_hirl_view:
            primary_machinery_cls = EEPProgramCustomerHIRLExamineMachinery

        machinery = primary_machinery_cls(**kwargs)
        machineries[machinery.type_name_slug] = machinery
        self.primary_machinery = machinery

        if not self.is_customer_hirl_view:
            for Machinery in [
                EEPProgramRequirementsMachinery,
                EEPProgramSettingsMachinery,
                EEPProgramAnnotationsMachinery,
                EEPProgramChecklistMachinery,
            ]:
                machinery = Machinery(**kwargs)
                machineries[machinery.type_name_slug] = machinery

        return machineries


class EEPProgramExamineMachineryMixin(object):
    model = EEPProgram
    form_class = EEPProgramForm
    api_provider = EEPProgramViewSet

    def _format_url_name(self, url_name, **kwargs):
        return url_name.format(model="eep_program")

    def get_form_kwargs(self, instance):
        return {"user": self.context["request"].user}

    def get_context(self):
        context = super(EEPProgramExamineMachineryMixin, self).get_context()
        if getattr(self, "fieldset", False):
            context["fieldset"] = self.fieldset
        return context

    def get_region_dependencies(self):
        return {"eep_program": [{"field_name": "id", "serialize_as": "id"}]}

    def can_delete_object(self, instance, user=None):
        if self.type_name == "eep_program":
            return super(EEPProgramExamineMachineryMixin, self).can_delete_object(
                instance, user=user
            )
        return False


class EEPProgramRequirementsMachinery(EEPProgramExamineMachineryMixin, examine.ExamineMachinery):
    type_name = "eep_program_requirements"
    fieldset = "requirements"
    form_template = "examine/eep_program/eep_program_requirements_form.html"
    detail_template = "examine/eep_program/eep_program_requirements_detail.html"


class EEPProgramSettingsMachinery(EEPProgramExamineMachineryMixin, examine.ExamineMachinery):
    type_name = "eep_program_settings"
    fieldset = "settings"
    form_template = "examine/eep_program/eep_program_settings_form.html"
    detail_template = "examine/eep_program/eep_program_settings_detail.html"


class EEPProgramAnnotationsMachinery(EEPProgramExamineMachineryMixin, examine.ExamineMachinery):
    type_name = "eep_program_annotations"
    fieldset = "annotations"
    form_template = "examine/eep_program/eep_program_annotations_form.html"
    detail_template = "examine/eep_program/eep_program_annotations_detail.html"


class EEPProgramChecklistMachinery(EEPProgramExamineMachineryMixin, examine.ExamineMachinery):
    type_name = "eep_program_checklists"
    fieldset = "checklist"
    form_template = "examine/eep_program/eep_program_checklist_form.html"
    detail_template = "examine/eep_program/eep_program_checklist_detail.html"


class EEPProgramExamineMachinery(EEPProgramExamineMachineryMixin, AxisPrimaryMachinery):
    type_name = "eep_program"
    fieldset = "main"
    detail_template = "examine/eep_program/eep_program_detail.html"
    form_template = "examine/eep_program/eep_program_form.html"

    def get_object_list_url(self):
        """
        It returns an {app_name} instead of a {model_name}.
        Our urls for this axis are very simple.
        So automatic searching doesn't find it.
         - Tim
        """
        return reverse("eep_program:list")

    def get_delete_success_url(self):
        return self.get_object_list_url()

    def get_helpers(self, instance):
        helpers = super(EEPProgramExamineMachinery, self).get_helpers(instance)
        helpers["page_title"] = "{} {}".format(
            self.get_verbose_name(instance), "{}".format(instance)
        )
        return helpers

    def get_region_dependencies(self):
        return {}


class EEPProgramCustomerHIRLExamineMachinery(EEPProgramExamineMachineryMixin, AxisPrimaryMachinery):
    type_name = "eep_program"
    fieldset = "main"
    detail_template = "examine/eep_program/eep_program_customer_hirl_detail.html"
    form_template = "examine/eep_program/eep_program_form.html"

    def get_object_list_url(self):
        """
        It returns an {app_name} instead of a {model_name}.
        Our urls for this axis are very simple.
        So automatic searching doesn't find it.
         - Tim
        """
        return reverse("eep_program:list")

    def can_edit_object(self, instance, user=None):
        if user and user.is_superuser:
            return True
        return False

    def can_delete_object(self, instance, user=None):
        if user and user.is_superuser:
            return True
        return False

    def get_delete_success_url(self):
        return self.get_object_list_url()

    def get_helpers(self, instance):
        helpers = super(EEPProgramCustomerHIRLExamineMachinery, self).get_helpers(instance)
        helpers["page_title"] = "{} {}".format(
            self.get_verbose_name(instance), "{}".format(instance)
        )
        return helpers

    def get_region_dependencies(self):
        return {}
