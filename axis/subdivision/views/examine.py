"""Examine support for `Subdivision`."""

__author__ = "Autumn Valenta"
__date__ = "09-19-14 12:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from datatableview.views import MultipleDatatableMixin
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy, reverse

from axis.core.models import RecentlyViewed
from axis.core.utils import values_to_dict
from axis.core.views.generic import AxisExamineView
from axis.core.views.machinery import (
    AxisGeocodedMachineryMixin,
    AxisPrimaryMachinery,
    object_relationships_machinery_factory,
)
from axis.customer_aps.views.examine import APSSmartThermostatOptionsMachinery
from axis.eep_program.models import EEPProgram
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.floorplan.models import Floorplan
from axis.home.models import Home, EEPProgramHomeStatus
from axis.home.utils import get_inheritable_settings_form_info
from axis.qa.models import QAStatus, get_stats_available_for_qa
from ..api import SubdivisionViewSet
from ..datatables import (
    SubdivisionHomesDatatable,
    SubdivisionFloorplansDatatable,
    HIRLSubdivisionHomesDataTable,
)
from ..forms import SubdivisionForm
from ..models import Subdivision, FloorplanApproval
from axis.home.views.machineries import HIRLProjectRegistrationContactsHomeStatusExamineMachinery

customer_hirl_app = apps.get_app_config("customer_hirl")


class SubdivisionDependentMixin(object):
    """Provide region dependency for a presumed top-level 'subdivision' machinery."""

    def get_region_dependencies(self):
        """Link remote `subdivision.id` value locally as `subdivision`."""

        return {
            "subdivision": [
                {
                    "field_name": "id",
                    "serialize_as": "subdivision",
                }
            ]
        }


class HIRLProjectRegistrationContactsSubdivisionExamineMachinery(
    HIRLProjectRegistrationContactsHomeStatusExamineMachinery
):
    """
    Examine for one common contact from HIRLProjectRegistration to display in subdivision
    """

    def get_object_name(self, instance):
        return ""


# View
class SubdivisionExamineView(LoginRequiredMixin, MultipleDatatableMixin, AxisExamineView):
    """Build the machineries required for loading the page."""

    model = Subdivision

    datatable_classes = {
        "homes": SubdivisionHomesDatatable,
        "floorplans": SubdivisionFloorplansDatatable,
        "customer_hirl_homes": HIRLSubdivisionHomesDataTable,
        # 'samplesets': ,
    }

    @property
    def primary_machinery(self):
        """Return centeral Subdivision machinery."""

        return SubdivisionExamineMachinery

    def get_queryset(self):
        """Include attached objects when user's `company_type` is `'qa'`."""

        kwargs = {}
        if self.request.user.company.company_type == "qa":
            kwargs["show_attached"] = True
        return Subdivision.objects.filter_by_user(user=self.request.user, **kwargs)

    def get_machinery(self):
        """Return dict of this and the supported page regions.

        Supplies related regions for `Relationship`, `CustomerDocument`, and `QAStatus`.
        """

        machineries = {}
        kwargs = {
            "create_new": self.create_new,
            "context": {
                "request": self.request,
            },
        }

        user = self.request.user

        subdivision = self.object
        machinery = SubdivisionExamineMachinery(instance=subdivision, **kwargs)
        machineries[machinery.type_name_slug] = machinery

        # Relationships
        # RelationshipsMachinery = object_relationships_machinery_factory(self.model)
        RelationshipsMachinery = object_relationships_machinery_factory(
            self.model,
            company_types=[
                # 'builder',  # Taking away builder because it's already in the main subdivision form
                "rater",
                "provider",
                "eep",
                "hvac",
                "qa",
                "general",
                "gas_utility",
                "electric_utility",
                "architect",
                "developer",
                "communityowner",
            ],
        )
        machinery = RelationshipsMachinery(instance=subdivision, **kwargs)
        machineries["relationships"] = machinery

        # Documents
        documents = []
        if not self.create_new:
            documents = subdivision.customer_documents.filter_by_user(
                self.request.user, include_public=True
            )
        machinery_class = customerdocument_machinery_factory(self.model)
        machinery = machinery_class(objects=documents, **kwargs)
        machineries["documents"] = machinery

        # get first available homestatus with HIRLProjectRegistration and use contacts from it
        # all project contacts are the same for MF Project Registration
        homestatus_with_hirl_project = EEPProgramHomeStatus.objects.filter(
            home__subdivision=subdivision, customer_hirl_project__registration__isnull=False
        ).first()
        if homestatus_with_hirl_project:
            machinery = HIRLProjectRegistrationContactsSubdivisionExamineMachinery(
                instance=homestatus_with_hirl_project, **kwargs
            )
            machineries[machinery.type_name_slug] = machinery

        # qa statuses
        qa_statuses = []
        if not self.create_new:
            qa_statuses = QAStatus.objects.filter_by_user(user, subdivision=subdivision)
        from axis.qa.views.examine import QAStatusExamineMachinery

        machinery = QAStatusExamineMachinery(
            objects=qa_statuses, content_object=subdivision, **kwargs
        )
        machineries[machinery.type_name_slug] = machinery

        return machineries

    def get_context_data(self, **kwargs):
        """Add `show_qa` and `programs_in_use` context hints for initial page render."""

        context = super(SubdivisionExamineView, self).get_context_data(**kwargs)

        user = self.request.user
        stats_available_for_qa = get_stats_available_for_qa(user, subdivision=self.object)
        qa_objects = QAStatus.objects.filter_by_user(user).filter(subdivision=self.object)
        show_qa = stats_available_for_qa.count() or qa_objects.count()
        context["show_qa"] = show_qa

        context["show_samplesets"] = True
        context["show_floorplans"] = True
        context["hirl_project_registration"] = getattr(self.object, "hirlprojectregistration", None)

        if context["hirl_project_registration"]:
            context["show_samplesets"] = False
            context["show_floorplans"] = False
            context["show_qa"] = False
            context["hirl_project_registration"] = self.object.hirlprojectregistration

        if not self.create_new:
            context["programs_in_use"] = EEPProgram.objects.filter(
                home__subdivision=self.object
            ).distinct()

        RecentlyViewed.objects.view(instance=self.object, by=self.request.user)
        return context

    # Satellite Datatables stuff
    def get_homes_datatable_queryset(self):
        """Return `Home` queryset for embedded `homes` datatable."""

        subdivision = self.get_object()
        if subdivision and subdivision.pk:
            return subdivision.home_set.filter_by_user(user=self.request.user, show_attached=False)
        return Home.objects.none()

    def get_homes_datatable_kwargs(self, **kwargs):
        """Return dict of extra hints for embedded `homes` datatable."""

        related_data = self._get_related_home_values(kwargs["object_list"])
        user_floorplans = set(
            Floorplan.objects.filter_by_user(self.request.user).values_list("id", flat=True)
        )
        user_programs = set(
            EEPProgram.objects.filter_by_company(self.request.company).values_list("id", flat=True)
        )

        kwargs.update(
            {
                "user": self.request.user,
                # Extra stuff for columns to use
                "related_data": related_data,
                "user_floorplans": user_floorplans,
                "user_programs": user_programs,
                "result_counter_id": "id_home_count",
            }
        )
        return kwargs

    def get_customer_hirl_homes_datatable_queryset(self):
        return self.get_homes_datatable_queryset()

    def get_customer_hirl_homes_datatable_kwargs(self, **kwargs):
        return self.get_homes_datatable_kwargs(**kwargs)

    def get_floorplans_datatable_queryset(self):
        """Return `FloorplanApproval` queryset for embedded `floorplans` datatable."""

        subdivision = self.get_object()
        if not subdivision:
            return FloorplanApproval.objects.none()
        return (
            FloorplanApproval.objects.filter_by_user_and_subdivision(
                subdivision=subdivision, user=self.request.user
            )
            .select_related("floorplan")
            .distinct()
        )

    def get_floorplans_datatable_kwargs(self, **kwargs):
        """Return dict of extra hints for embedded `floorplans` datatable."""

        kwargs.update(
            {
                "user": self.request.user,
                "result_counter_id": "id_floorplan_count",
            }
        )
        return kwargs

    def _get_related_home_values(self, queryset):
        preloaded_values = {}

        convert_attrs = {
            "floorplans": {
                "homestatuses__floorplan__name": "name",
                "homestatuses__floorplan__number": "number",
                "homestatuses__floorplan__id": "floorplan",
                "homestatuses__floorplan__owner__id": "owner",
            },
            "programs": {
                "homestatuses__eep_program__name": "name",
                "homestatuses__eep_program__id": "program",
                "homestatuses__eep_program__owner__id": "owner",
            },
            "states": {
                "homestatuses__state": "state",
            },
            "customer_hirl_projects": {
                "homestatuses__customer_hirl_project__registration__id": "registration_id",
                "homestatuses__customer_hirl_project__id": "id",
            },
        }

        for key, spec in convert_attrs.items():
            data = values_to_dict(
                queryset.values("id", *list(spec.keys())), key="id", value_as_list=True
            )

            for items in data.values():
                for i, item in enumerate(items):
                    items[i] = {spec.get(k, k): item[k] for k in item}

            preloaded_values[key] = data
        return preloaded_values


# Machinery classes
class SubdivisionExamineMachineryMixin(AxisGeocodedMachineryMixin, AxisPrimaryMachinery):
    """Primary specification for a single-subdivision workflow."""

    model = Subdivision
    form_class = SubdivisionForm
    api_provider = SubdivisionViewSet
    type_name = "subdivision"
    type_name_slug = "subdivision"

    detail_template = "examine/subdivision/subdivision_detail.html"
    form_template = "examine/subdivision/subdivision_form.html"

    delete_success_url = reverse_lazy("subdivision:list")

    def get_verbose_name(self, instance=None):
        """Update for Multi-Family"""
        if instance and instance.is_multi_family:
            return "MF Development"
        return "Subdivision"

    def get_verbose_name_plural(self, instance=None):
        """Update for Multi-Family"""
        if instance and instance.is_multi_family:
            return "MF Developments"
        return "Subdivisions"

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        """Update for Multi-Family"""
        verbose_names = super(SubdivisionExamineMachineryMixin, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )
        if instance and instance.is_multi_family:
            if instance.community is None:
                verbose_names["community"] = "Complex"
            elif instance.community and instance.community.is_multi_family:
                verbose_names["community"] = "Complex"
        verbose_names["city"] = "City"
        return verbose_names

    def get_form_kwargs(self, instance):
        """Provide `user` kwarg to `form_class` constructor."""

        return {"user": self.context["request"].user}

    def serialize_form_spec(self, instance, form):
        """Add `relationship_add_url` to the local 'name' field's options dict."""

        data = super(SubdivisionExamineMachineryMixin, self).serialize_form_spec(instance, form)
        # if isinstance(form, self.form_class):  # we send multiple forms through serialization
        #     if hasattr(form.fields['name'], 'relationship_add_url'):
        #         data['name']['options']['relationship_add_url'] = (
        #             form.fields['name'].relationship_add_url)
        return data

    def get_helpers(self, instance):
        """Add `page_title` and `samplesets_url` hints for use in templates."""

        helpers = super(SubdivisionExamineMachineryMixin, self).get_helpers(instance)
        helpers.update(
            {
                "samplesets_url": reverse(
                    "sampleset:list", kwargs={"subdivision_id": instance.id or 0}
                ),
            }
        )
        helpers["page_title"] = "{} {}".format(self.get_verbose_name(instance), instance)

        helpers["show_unit_count"] = False
        user = self.context["request"].user
        if (
            user.is_customer_hirl_company_member()
            or user.is_sponsored_by_company(customer_hirl_app.CUSTOMER_SLUG)
            or user.is_superuser
        ):
            helpers["show_unit_count"] = True

            if instance.pk:
                helpers["customer_hirl_total_unit_count"] = (
                    EEPProgramHomeStatus.objects.filter(home__subdivision__id=instance.pk)
                    .annotate_customer_hirl_unit_count()
                    .aggregate(total_unit_count=Sum("unit_count"))["total_unit_count"]
                )
        return helpers


class SubdivisionExamineMachinery(SubdivisionExamineMachineryMixin, AxisPrimaryMachinery):
    """Primary specification for a single-subdivision workflow."""

    def get_helpers(self, instance):
        """Add hints for related associations.

        Related hints:
          - `associated_programs`: list of `eep_program.EEPProgram` url/text serializations
          - `builder_agreements`: list of `builder_agreements.BuilderAgreement` url/text
            serializations
          - `permitandoccupancysettings`: (via `get_hillsboro_helper()`) dict of form and
            inheritance info
        """

        helpers = super(SubdivisionExamineMachinery, self).get_helpers(instance)
        user = self.context["request"].user

        if not self.create_new:
            program_ids = set(
                instance.home_set.filter_by_user(user).values_list("eep_programs__id", flat=True)
            )
            associated_programs = EEPProgram.objects.filter(id__in=program_ids)
            helpers["associated_programs"] = [
                {
                    "url": obj.get_absolute_url(),
                    "text": "{}".format(obj),
                }
                for obj in associated_programs
            ]

            helpers["allow_sampling"] = associated_programs.filter(allow_sampling=True).exists()

            program_ids = set(
                instance.home_set.filter_by_user(user).values_list("eep_programs__id", flat=True)
            )
            helpers["builder_agreements"] = [
                {
                    "url": obj.get_absolute_url(),
                    "text": "{}".format(obj),
                }
                for obj in instance.builderagreement_set.all()
            ]

        hillsboro_helper = self.get_hillsboro_helper(instance)
        if hillsboro_helper:
            helpers["permitandoccupancysettings"] = hillsboro_helper

        if instance.is_aps_thermostat_incentive_applicable(user):
            aps_thermostat_machinery = APSSmartThermostatOptionsMachinery(instance=instance)
            helpers["show_aps_thermostat_incentive_machinery"] = True
            helpers["aps_thermostat_machinery"] = aps_thermostat_machinery.get_summary()

        return helpers

    def get_hillsboro_helper(self, instance):
        """Return dict for permit and occupancy settings and form."""

        from axis.customer_eto.forms import PermitAndOccupancySettingsForm
        from axis.customer_eto.strings import COMPLIANCE_LONGFORM_HTML_CHOICES

        customer_eto_app = apps.get_app_config("customer_eto")

        user = self.context["request"].user
        if not all(
            [
                not self.create_new,
                user.has_perm("customer_eto.change_permitandoccupancysettings"),
                (
                    instance.community
                    and (
                        instance.community.slug
                        in customer_eto_app.CITY_OF_HILLSBORO_COMMUNITY_SLUGS
                    )
                ),
            ]
        ):
            return None

        helper = get_inheritable_settings_form_info(
            user.company,
            instance,
            "permitandoccupancysettings_set",
            form_class=PermitAndOccupancySettingsForm,
            settings_action_url="eto-compliance-option",
            document_action_url="eto-compliance-document",
        )
        helper["html_choices"] = COMPLIANCE_LONGFORM_HTML_CHOICES
        helper["form"] = self.serialize_form_spec(instance, helper["form"])
        return helper
