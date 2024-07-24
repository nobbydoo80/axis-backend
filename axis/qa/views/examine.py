__author__ = "Michael Jeffrey"
__date__ = "9/8/15 11:18 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import random
from datetime import datetime

from django.urls import reverse
from django.apps import apps
from django.utils import timezone

from axis import examine
from axis.checklist.forms import AsynchronousChecklistCreateForm
from axis.filehandling.machinery import (
    customerdocument_machinery_factory,
    BaseCustomerDocumentExamineMachinery,
)
from axis.home.models import EEPProgramHomeStatus, Home
from axis.home.views.machineries import HomeStatusExamineMachinery
from axis.qa.views.machineris.home_qa_inspection_grade import HomeQAInspectionGradeExamineMachinery
from axis.subdivision.models import Subdivision
from ..api import QAStatusViewSet, QARequirementViewSet, QANoteViewSet, ObservationTypeViewSet
from ..forms import QAStatusForm, QANoteForm, ObservationTypeForm, QADocumentCustomerHIRLForm
from ..models import QAStatus, QARequirement, QANote, ObservationType


customer_hirl_app = apps.get_app_config("customer_hirl")


class QADocumentBase(BaseCustomerDocumentExamineMachinery):
    template_set = "default"
    form_template = "examine/qa/qa_document_form.html"
    regionset_template = "examine/qa/qa_document_regionset.html"

    def get_region_dependencies(self):
        return {}

    def get_edit_actions(self, instance):
        return []

    def get_default_actions(self, instance):
        return []

    def get_form(self, instance):
        form = super(QADocumentBase, self).get_form(instance)
        form.fields["document"].label = "Document"
        form.fields["document"].required = False
        return form

    def get_verbose_name(self, instance=None):
        return "QA Document"


class QADocumentCustomerHIRLBase(BaseCustomerDocumentExamineMachinery):
    form_class = QADocumentCustomerHIRLForm
    verbose_name = "Document"
    detail_template = "examine/qa/qa_document_customer_hirl_detail.html"
    form_template = "examine/qa/qa_document_customer_hirl_form.html"
    regionset_template = "examine/qa/qa_document_customer_hirl_regionset.html"
    visible_fields = ["document", "description", "last_update"]

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        verbose_names = super(QADocumentCustomerHIRLBase, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )
        verbose_names["last_update"] = "Last Update"
        return verbose_names

    def can_edit_object(self, instance, user=None):
        if instance and instance.pk and user:
            if user.is_superuser:
                return True
            if user.company.slug == customer_hirl_app.CUSTOMER_SLUG and user.is_company_admin:
                if instance.company.is_sponsored_by_customer_hirl():
                    return True
        return False

    def can_delete_object(self, instance, user=None):
        if instance and instance.pk and user:
            if user.is_superuser:
                return True
            if user.company.slug == customer_hirl_app.CUSTOMER_SLUG and user.is_company_admin:
                if instance.company.is_sponsored_by_customer_hirl():
                    return True
        return False


class QARequirementExamineMachinery(examine.ReadonlyMachinery):
    model = QARequirement
    type_name = "qa_requirement"
    api_provider = QARequirementViewSet

    template_set = "accordion"
    detail_template = "examine/qa/qa_requirement_detail.html"
    region_template = "examine/qa/qa_requirement_region.html"

    def __init__(self, *args, **kwargs):
        self.home = kwargs.pop("home", False)
        super(QARequirementExamineMachinery, self).__init__(*args, **kwargs)

    def get_home(self):
        if not self.home:
            from axis.home.models import Home

            home_id = self.context["request"].query_params.get("home")
            self.home = Home.objects.get(id=home_id)

        return self.home

    def get_home_status(self, instance):
        return EEPProgramHomeStatus.objects.get(
            home_id=self.get_home().id, eep_program=instance.eep_program
        )

    def get_region_dependencies(self):
        return {
            "home": [{"field_name": "id", "serialize_as": "home"}],
        }

    def get_context(self):
        context = super(QARequirementExamineMachinery, self).get_context()
        context["home"] = getattr(self.home, "id", "__home__")
        return context

    def get_helpers(self, instance):
        helpers = super(QARequirementExamineMachinery, self).get_helpers(instance)

        helpers["machinery"] = {}

        kwargs = {"context": self.context, "requirement": self.instance, "home": self.get_home()}

        statuses = self.get_home().homestatuses.values_list("id", flat=True)
        try:
            qa_status = QAStatus.objects.get(requirement=self.instance, home_status__in=statuses)
        except QAStatus.DoesNotExist:
            qa_status = None
            nested_qa_status_machinery = QAStatusExamineMachinery(create_new=True, **kwargs)
            helpers["machinery"]["add_qa_status"] = nested_qa_status_machinery.get_summary()
        else:
            nested_qa_status_machinery = QAStatusExamineMachinery(instance=qa_status, **kwargs)
            helpers["machinery"]["qa_status"] = nested_qa_status_machinery.get_summary()

        # Notes
        if qa_status and not self.create_new:
            notes = qa_status.qanote_set.all()

            nested_qa_notes_machinery = QANoteExamineMachinery(objects=notes, **kwargs)

            helpers["machinery"]["qa_notes"] = nested_qa_notes_machinery.get_summary()
            helpers["show_qa_notes"] = True
        else:
            helpers["show_qa_notes"] = False

        return helpers


class QAStatusExamineMachinery(examine.ExamineMachinery):
    model = QAStatus
    form_class = QAStatusForm
    type_name = "qa_status"
    api_provider = QAStatusViewSet

    template_set = "accordion"
    regionset_template = "examine/qa/qa_status_regionset.html"
    region_template = "examine/qa/qa_status_region.html"
    detail_template = "examine/qa/qa_status_detail.html"
    form_template = "examine/qa/qa_status_form.html"

    def __init__(self, *args, **kwargs):
        self.content_object = kwargs.pop("content_object", None)
        super(QAStatusExamineMachinery, self).__init__(*args, **kwargs)

        if not self.content_object:
            data = self.context["request"].query_params
            if "home" in data:
                model = Home
                id = data["home"]
            elif "subdivision" in data:
                model = Subdivision
                id = data["subdivision"]
            self.content_object = model.objects.get(id=id)

    def configure_for_instance(self, instance):
        if self.create_new:
            instance.state = "in_progress"

    def get_verbose_name(self, instance=None):
        return "QA"

    def get_object_name(self, instance):
        if instance.pk:
            type = instance.requirement.get_type_display()
            home_status = instance.get_home_status()
            eep_program = home_status.eep_program.name
            return "{}: {}".format(type, eep_program)
        return super(QAStatusExamineMachinery, self).get_object_name(instance)

    def get_qa_home_status(self, instance):
        if not instance.pk:
            return None
        home_status = instance.get_home_status()
        program_slug = home_status.eep_program.slug + "-qa"
        try:
            return EEPProgramHomeStatus.objects.filter_by_user(self.context["request"].user).get(
                eep_program__slug=program_slug, home_id=home_status.home_id
            )
        except EEPProgramHomeStatus.DoesNotExist:
            return None

    def get_static_actions(self, instance):
        actions = super(QAStatusExamineMachinery, self).get_static_actions(instance)

        user = self.context["request"].user
        if (
            user.is_superuser
            or user.company.company_type in ["qa", "provider"]
            and user.is_company_admin
        ):
            actions.append(
                self.Action(
                    "Manage observation types",
                    icon="gear",
                    instruction="manage_observations",
                    modal={
                        "templateUrl": examine.template_url(
                            "examine/qa/manage_observation_types.html"
                        ),
                    },
                )
            )

        if instance.pk and instance.requirement.type == "field":
            qa_home_status = self.get_qa_home_status(instance)
            if qa_home_status:
                machinery = FieldQAHomeStatusExamineMachinery(
                    instance=qa_home_status, context=self.context
                )
                machinery.configure_for_instance(qa_home_status)
                actions.append(machinery._get_checklist_actions(qa_home_status))

        return actions

    def get_default_actions(self, instance):
        """Returns normal actions even when instance is unsaved."""
        actions = []

        request = self.context.get("request", None)
        user = request.user if request else None

        if self.can_delete_object(instance, user=user):
            actions.append(
                self.Action(self.delete_name, instruction="delete", icon=self.delete_icon)
            )
        if self.can_edit_object(instance, user=user):
            actions.append(
                self.Action(
                    self.save_name,
                    instruction=self.save_instruction,
                    style="primary",
                    icon=self.save_icon,
                )
            )

        if (
            instance.pk
            and user
            and user.is_customer_hirl_company_member()
            and instance.home_status
            and getattr(instance.home_status, "customer_hirl_project", None)
        ):
            hirl_project = instance.home_status.customer_hirl_project
            if instance.requirement.type == QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE:
                childrens = hirl_project.vr_batch_submission_rough_childrens.all()
            else:
                childrens = hirl_project.vr_batch_submission_final_childrens.all()
            if childrens:
                actions.append(
                    self.Action(
                        "Sync Across Batch",
                        style="primary",
                        instruction="customer_hirl_qa_sync_batch",
                    )
                )

        return actions

    def get_region_dependencies(self):
        model_name = self.content_object._meta.model_name
        return {model_name: [{"field_name": "id", "serialize_as": model_name}]}

    def get_form_kwargs(self, instance):
        return {
            "user": self.context["request"].user,
            "content_object": self.content_object,
            "initial": {
                "hirl_commercial_space_confirmed": "false",
                "hirl_water_sense_confirmed": "false",
            },
        }

    def get_field_order(self, instance, form):
        return ["requirement", "qa_designee", "new_state", "result", "note"]

    def get_helpers(self, instance):
        helpers = super(QAStatusExamineMachinery, self).get_helpers(instance)

        user = self.context["request"].user
        helpers["machinery"] = {}

        if instance.pk:
            helpers["customer_hirl_qa_sync_batch_endpoint"] = reverse(
                "apiv2:qa_status-customer-hirl-sync-batch", kwargs={"pk": instance.pk}
            )
            helpers["can_edit_qa_designee"] = self.context["request"].company == instance.owner

            helpers["can_view_hirl_verifier_fields"] = False
            helpers["can_edit_hirl_verifier_fields"] = False

            if instance.requirement and instance.requirement.type in [
                QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                QARequirement.FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
            ]:
                helpers["can_view_hirl_verifier_fields"] = True

                if user and (user.is_superuser or user.is_customer_hirl_company_member()):
                    helpers["can_edit_hirl_verifier_fields"] = True

            documents = instance.customer_documents.all()

            helpers["customer_hirl_documents_machinery"] = None

            helpers["use_qa_notes_form"] = self.can_edit_object(instance, user=user)
            helpers["is_customer_hirl_project_program"] = (
                instance.requirement.eep_program.slug
                in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            )

            if helpers["is_customer_hirl_project_program"]:
                # Documents
                machinery_class = customerdocument_machinery_factory(
                    self.model,
                    machinery_name="QADocumentCustomerHIRLMachinery",
                    bases=(QADocumentCustomerHIRLBase,),
                )
                machinery = machinery_class(
                    objects=documents, context={"request": self.context["request"]}
                )
                helpers["customer_hirl_documents_machinery"] = machinery.get_summary()
            else:
                machinery_class = customerdocument_machinery_factory(
                    QANote, bases=(QADocumentBase,)
                )
                helpers["new_documents"] = machinery_class(
                    instance=None, create_new=True
                ).get_summary()

                helpers["existing_documents"] = machinery_class(
                    objects=documents, create_new=False
                ).get_summary()

            notes = instance.qanote_set.all()
            notes_machinery = QANoteExamineMachinery(
                objects=notes, requirement=instance.requirement, context=self.context
            )
            helpers["machinery"]["qa_notes"] = notes_machinery.get_summary()

            objects = ObservationType.objects.filter_by_user(user)
            observationtypes_machinery = ObservationTypeMachinery(
                objects=objects, context=self.context
            )
            helpers["machinery"]["observation_types"] = observationtypes_machinery.get_summary()

            helpers["history"] = self.get_instance_history(instance)
            helpers["mismatched_answers"] = self.get_mismatched_answers(instance)

            verifier = instance.get_customer_hirl_grading_verifier()

            if verifier:
                inspection_gradings = instance.inspectiongrade_set.filter(user=verifier)
                if not user.is_superuser and verifier != user and user.company.company_type != "qa":
                    inspection_gradings = inspection_gradings.filter(approver__company=user.company)

                machinery = HomeQAInspectionGradeExamineMachinery(
                    objects=inspection_gradings,
                    create_new=True,
                    context={"request": self.context["request"], "user": verifier},
                )
                machinery_summary = machinery.get_summary()
                machinery_summary["region_dependencies"]["qa_status"] = [
                    {"serialize_as": "user_id", "field_name": "hirl_verifier"}
                ]
                helpers["machinery"]["{}".format(machinery.type_name_slug)] = machinery_summary
                helpers["verifier"] = {
                    "full_name": verifier.get_full_name(),
                    "profile_url": reverse("profile:detail", kwargs={"pk": verifier.id}),
                }

            if instance.home_status.eep_program.collection_request:
                if instance.home_status.collection_request is None:
                    instance.home_status.set_collection_from_program()
                helpers["collection_request"] = instance.home_status.collection_request.id

            if instance.requirement.type == "field":
                qa_home_status = self.get_qa_home_status(instance)
                if qa_home_status:
                    helpers["home_status"] = FieldQAHomeStatusExamineMachinery(
                        instance=qa_home_status, context=self.context
                    ).get_regions()[0]

                if not self.create_new:
                    form = AsynchronousChecklistCreateForm(initial={"company": user.company})
                    helpers["checklist_upload_form"] = self.serialize_form_spec(instance, form)

        return helpers

    def get_mismatched_answers(self, instance):
        if not instance.home_status:
            return []

        home = instance.home_status.home
        answers = home.answer_set.all()
        qa_answers = home.qaanswer_set.all()

        send_back = []

        for qa in qa_answers:
            try:
                matching = answers.get(question=qa.question)
            except home.answer_set.model.DoesNotExist:
                pass
            else:
                if qa.answer != matching.answer:
                    send_back.append({"answer": matching, "qa_answer": qa, "question": qa.question})

        return send_back

    def get_instance_history(self, instance):
        history = []

        state_history_entities = instance.state_history.all().order_by("-start_time")

        # QA created manually without state_history
        if not state_history_entities:
            history.append(
                {
                    "id": 0,
                    "start_time": instance.created_on,
                    "end_time": instance.created_on,
                    "duration": (timezone.now() - instance.created_on).total_seconds(),
                    "state": "QA Created",
                }
            )

            return history

        end_time = timezone.now()

        for state_history in state_history_entities:
            start_time = state_history.start_time
            state = state_history.get_to_state_display()

            history.append(
                {
                    "id": state_history.id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": (end_time - start_time).total_seconds(),
                    "state": state,
                }
            )

            end_time = start_time

        # There are occasions when a state change will occur before the instance gas been saved.
        # When that happens, the time difference in negligible, so we can use the created_on
        # time to prevent a negative duration form occurring.
        if end_time < instance.created_on:
            end_time = instance.created_on

        history.append(
            {
                "id": 0,
                "start_time": instance.created_on,
                "end_time": end_time,
                "duration": (end_time - instance.created_on).total_seconds(),
                "state": "QA Created",
            }
        )

        return reversed(history)

    def get_context(self):
        context = super(QAStatusExamineMachinery, self).get_context()
        model_name = self.content_object._meta.model_name
        placeholder_name = "__%s__" % (model_name,)
        context[model_name] = (
            getattr(self.content_object, "id", placeholder_name) or placeholder_name
        )
        return context


class QANoteExamineMachinery(examine.TableMachinery):
    model = QANote
    api_provider = QANoteViewSet
    form_class = QANoteForm
    type_name = "qa_note"

    can_add_new = False

    regionset_template = "examine/qa/qa_note_regionset.html"
    detail_template = "examine/qa/qa_note_detail.html"

    verbose_names = {
        "id": "ID",
        "qa_status": "Qa status",
        "note": "Note",
        "user": "User",
        "content_type": "Content type",
        "object_id": "Object id",
        "created_on": "created on",
        "last_update": "Last update",
        "observations": "Observations",
    }

    def __init__(self, *args, **kwargs):
        self.requirement = kwargs.pop("requirement", None)
        self.home = kwargs.pop("home", None)
        self.subdivision = kwargs.pop("subdivision", None)
        self.home_status = None
        self.qa_status = None
        super(QANoteExamineMachinery, self).__init__(*args, **kwargs)

        if not self.home:
            data = self.context["request"].query_params
            if "home" in data:
                home_id = data["home"]
                self.home = Home.objects.get(id=home_id)
            elif "subdivision" in data:
                subdivision_id = data["subdivision"]
                self.subdivision = Subdivision.objects.get(id=subdivision_id)

        if not self.requirement:
            requirement_id = self.context["request"].query_params.get("requirement")
            self.requirement = QARequirement.objects.get(id=requirement_id)

        if self.home:
            self.content_object = EEPProgramHomeStatus.objects.get(
                home_id=self.home.id, eep_program=self.requirement.eep_program
            )
            self.qa_status = QAStatus.objects.get(
                requirement=self.requirement, home_status=self.content_object
            )
        elif self.subdivision:
            self.content_object = self.subdivision
            self.qa_status = QAStatus.objects.get(
                requirement=self.requirement, subdivision=self.content_object
            )

    def get_verbose_name(self, instance=None):
        return "QA Note"

    def configure_for_instance(self, instance):
        if self.create_new:
            from django.contrib.contenttypes.models import ContentType

            instance.qa_status = self.qa_status
            instance.content_type = ContentType.objects.get_for_model(EEPProgramHomeStatus)
            instance.object_id = self.content_object.id
            instance.user = self.context["request"].user
            instance.last_update = datetime.now(timezone.utc)

    def get_field_order(self, instance, form):
        return self.get_visible_fields(instance, form)

    def get_visible_fields(self, instance, form):
        return ["last_update", "user", "observations", "note"]

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        return super(QANoteExamineMachinery, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )

    def get_form(self, instance):
        form = super(QANoteExamineMachinery, self).get_form(instance)

        self._setup_qa_status_field(form)
        self._setup_user_field(form)
        self._setup_content_type_field(form)
        self._setup_object_id_field(form)
        self._setup_last_update_field(form)

        return form

    def _setup_qa_status_field(self, form):
        field = form.fields["qa_status"]

        form.initial["qa_status"] = self.qa_status
        field.queryset = field.queryset.filter(id=self.qa_status.id)
        field.widget = field.hidden_widget()

    def _setup_user_field(self, form):
        form.initial["user"] = self.context["request"].user
        form.fields["user"].widget = form.fields["user"].hidden_widget()

    def _setup_content_type_field(self, form):
        from django.contrib.contenttypes.models import ContentType

        field = form.fields["content_type"]

        form.initial["content_type"] = ContentType.objects.get_for_model(EEPProgramHomeStatus)
        field.widget = field.hidden_widget()

    def _setup_object_id_field(self, form):
        field = form.fields["object_id"]

        form.initial["object_id"] = self.content_object.id
        field.widget = field.hidden_widget()

    def _setup_last_update_field(self, form):
        form.fields["last_update"].widget = form.fields["last_update"].hidden_widget()

    def get_region_dependencies(self):
        return {
            "qa_requirement": [{"field_name": "id", "serialize_as": "requirement"}],
            "home": [{"field_name": "id", "serialize_as": "home"}],
        }

    def get_context(self):
        context = super(QANoteExamineMachinery, self).get_context()
        if self.requirement and self.content_object:
            context["requirement"] = self.requirement.id
            model_name = self.content_object._meta.model_name
            if model_name == "eepprogramhomestatus":
                id = self.content_object.home.id
            elif model_name == "subdivision":
                id = self.content_object.id
            context[model_name] = id
        else:
            context["requirement"] = "__requirement__"
            data = self.context["request"].query_params
            if "home" in data:
                model_name = "home"
            elif "subdivision" in data:
                model_name = "subdivision"
            context[model_name] = "__%s__" % model_name
        return context


class ObservationTypeMachinery(examine.TableMachinery):
    model = ObservationType
    api_provider = ObservationTypeViewSet
    type_name = "observation_type"
    form_class = ObservationTypeForm

    def can_edit_object(self, instance, user=None):
        if user and not user.is_superuser:
            return user.is_company_admin
        return super(ObservationTypeMachinery, self).can_edit_object(instance, user)

    def can_delete_object(self, instance, user=None):
        if user and not user.is_superuser:
            return user.is_company_admin
        return super(ObservationTypeMachinery, self).can_delete_object(instance, user)


class FieldQAHomeStatusExamineMachinery(HomeStatusExamineMachinery):
    """
    Inherits from the homestatus machinery, and applies to the HomeStatus for the hidden ``*-qa``
    program underlying the qastatus.  This will be consulted for the helper data generated by the
    parent class, but not actually rendered into the template.

    One of these is also instantiated inside of QAStatusExamineMachinery so that it can copy the
    actions built by the parent class.
    """

    template_set = "panel"
    form_template = None

    def get_field_order(self, instance, form):
        return ["company"]

    def get_static_actions(self, instance):
        return []

    def get_default_actions(self, instance):
        actions = super(FieldQAHomeStatusExamineMachinery, self).get_default_actions(instance)
        actions.append(
            self.Action(
                self.edit_name,
                instruction="edit",
                icon=self.edit_icon,
                is_mode=True,
                style="primary",
            )
        )
        return actions
