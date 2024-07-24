__author__ = "Autumn Valenta"
__date__ = "9/5/12 5:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
import operator
from collections import Counter
from functools import reduce

import dateutil
import dateutil.parser
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Prefetch
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django_input_collection.collection import collectors
from django_states.exceptions import TransitionCannotStart
from rest_framework import viewsets, serializers, views, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from axis.certification.utils import get_owner_swap_queryset
from axis.checklist.models import Answer, Question
from axis.checklist.serializers import AnswerSerializer, QuestionSerializer, QAAnswerSerializer
from axis.checklist.utils import build_questionanswer_dict
from axis.core.caching import cache_api_response
from axis.core.utils import clean_base64_encoded_payload
from axis.customer_hirl.models import HIRLProject
from axis.customer_neea.models import LegacyNEEAHome
from axis.eep_program.messages import ProgramSunsetMessage, ProgramSubmitSunsetMessage
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.home.serializers import HIRLInvoiceItemGroupSerializer
from axis.invoicing.models import InvoiceItemGroup, InvoiceItem, Invoice
from axis.qa.models import QARequirement, QAStatus, QANote
from axis.relationship.utils import create_or_update_spanning_relationships
from .models import Home, EEPProgramHomeStatus
from .serializers import (
    HomeSerializer,
    HomeStatusSerializer,
    HomeUsersSerializer,
    HomeStatusAnnotationsSerializer,
    HomeStatusFloorplansThroughSerializer,
    HomeStatusHIRLProjectSerializer,
    HIRLInvoiceItemSerializer,
)
from .state_machine import HomeStatusStateMachine
from .utils import get_required_annotations_form, get_eps_data, HomeCertification
from ..customer_neea.rtf_calculator.calculator import NEEAV3Calculator
from ..filehandling.models import CustomerDocument
from ..floorplan.api_v3.serializers import FloorplanFromBlgSerializer
from ..floorplan.api_v3.serializers.simulation import SimulationHomeBuildingParameterSerializer
from ..qa.messages import HomeAddedToMultiFamilySubdivision

log = logging.getLogger(__name__)


# Normally each answer's "confirmed" flag (set during certification) locks the users out of
# editing the objects, and the checklist is free to let that be the only mechanism guarding
# answer manipulation.
# Locking the checklist for any other state requires us to explicitly take action to stamp
# over the "confirmed" flag on each answer.
CHECKLIST_LOCKED_STATES = {
    "eto-2017": ["certification_pending"],
    "eto-2018": ["certification_pending"],
    "eto-2019": ["certification_pending"],
}


def notify_of_subdivision_qa(homestatus, user):
    """Generate a unique message about the home's program for the subdivision."""
    home = homestatus.home
    subdivision = home.subdivision
    if subdivision and subdivision.is_multi_family:
        qa_company = home.get_qa_company()
        url = subdivision.get_absolute_url() + "#/tabs/qa"
        requirements = QARequirement.objects.filter_for_add(subdivision, user).filter(
            eep_program=homestatus.eep_program_id, qa_company=qa_company
        )
        for requirement in requirements:
            context = {
                "subdivision": "{}".format(subdivision),
                "url": url,
                "program": homestatus.eep_program.name,
            }
            HomeAddedToMultiFamilySubdivision(
                url=url,
            ).send(
                context=context,
                company=requirement.qa_company,
            )


class HomeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Home
    queryset = model.objects.all()
    serializer_class = HomeSerializer

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import (
            HomeExamineReadonlyChecklistMachinery,
            HomeExamineReadonlyMachinery,
            HomeBLGCreationExamineMachinery,
            HomeExamineMachinery,
            HomeDocumentActionsMachinery,
        )

        return {
            None: HomeExamineMachinery,
            "HomeDocumentActionsMachinery": HomeDocumentActionsMachinery,
            "HomeExamineMachinery": HomeExamineMachinery,
            "HomeExamineReadonlyMachinery": HomeExamineReadonlyMachinery,
            "HomeExamineReadonlyChecklistMachinery": HomeExamineReadonlyChecklistMachinery,
            "HomeBLGCreationExamineMachinery": HomeBLGCreationExamineMachinery,
        }

    def filter_queryset(self, queryset):
        params = self.request.query_params.dict()
        valid_fields = set()
        for field in self.model._meta.get_fields(include_parents=False, include_hidden=False):
            if field.is_relation and field.many_to_one and field.related_model is None:
                continue
            valid_fields.add(field.name)
            if hasattr(field, "attname"):
                valid_fields.add(field.attname)
        provided_fields = set(params.keys())
        return queryset.filter(**{k: params[k] for k in provided_fields.intersection(valid_fields)})

    @action(detail=True)
    def collectors(self, request, *args, **kwargs):
        home = self.get_object()
        user = self.request.user

        if "collector" in self.request.query_params:
            collector_id = self.request.query_params["collector"]
            CollectorClass = collectors.resolve(collector_id)
        else:
            from axis.checklist.collection.examine import BootstrapAngularChecklistCollector

            CollectorClass = BootstrapAngularChecklistCollector

        lookup_kwargs = {}
        collection_request_ids = self.request.query_params.getlist("collection_request_id")
        if collection_request_ids:
            lookup_kwargs["collection_request_id__in"] = collection_request_ids
        else:
            lookup_kwargs["eep_program__collection_request__isnull"] = False

        # Get requests
        home_statuses = home.homestatuses.filter_by_user(user).filter(**lookup_kwargs)
        home_statuses = EEPProgramHomeStatus.objects.filter(
            id__in=list(home_statuses.values_list("id", flat=True))
        )
        info = {}

        for home_status in home_statuses:
            if home_status.collection_request is None:
                home_status.set_collection_from_program()
            collection_request = home_status.collection_request

            context = {
                "user": user,
            }
            if user.is_superuser:
                # Get a rater or a sponsor view of the checklist
                shadow_user = home_status.company.users.filter(is_active=True).first()
                if not shadow_user:
                    shadow_user = home_status.eep_program.owner.users.filter(is_active=True).first()
                if shadow_user:
                    context["user"] = shadow_user
            elif user.company.slug == home_status.eep_program.owner.slug:
                # Get a qa or rater view of the checklist
                shadow_user = home_status.company.users.filter(is_active=True).first()
                if shadow_user:
                    context["user"] = shadow_user

            collector = CollectorClass(collection_request, **context)
            info[collection_request.id] = {
                "specification": collector.specification,
                "instruments": collector.serialized_data,
            }
            # with open("spec.json", "w") as f:
            #     f.write(f"{json.dumps(collector.specification, indent=4)}\n")
            # with open("current_instruments.json", "w") as f:
            #     f.write(f"{json.dumps(info[collection_request.id]['instruments'], indent=4)}\n")

        return Response(info)

    @action(detail=True)
    def questions(self, request, *args, **kwargs):
        home = self.get_object()
        user = self.request.user
        eep_program_id = kwargs["eep_program_id"]

        # Question: Do we want to be ignoring the phase during one of these?
        try:
            stat = home.homestatuses.get(eep_program_id=eep_program_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        if stat.collection_request is None and stat.eep_program.collection_request:
            stat.set_collection_from_program()

        lock_answers = stat.state in CHECKLIST_LOCKED_STATES.get(stat.eep_program.slug, [])

        is_qa_program = stat.eep_program.is_qa_program
        question_sets = [stat.get_questions_and_permission_for_user(user)]

        from axis.checklist.models import Answer, QAAnswer

        qa_answers = (
            QAAnswer.objects.filter_by_home_status(stat, user)
            if is_qa_program
            else QAAnswer.objects.none()
        )
        is_associated = stat.associations.filter(company=user.company, is_active=True)
        answers = Answer.objects.filter_by_home_status(stat, user, by_association=is_associated)

        select_related = AnswerSerializer.select_related()
        prefetch_related = AnswerSerializer.prefetch_related()

        qa_answers = qa_answers.select_related(*select_related).prefetch_related(*prefetch_related)
        answers = answers.select_related(*select_related).prefetch_related(*prefetch_related)

        answers = {
            answer["question"]: answer for answer in AnswerSerializer(answers, many=True).data
        }
        qa_answers = {
            answer["question"]: answer for answer in QAAnswerSerializer(qa_answers, many=True).data
        }

        answer_storage_key = "related_answer" if is_qa_program else "answer"
        qa_answer_storage_key = "answer" if is_qa_program else "qa_answer"

        all_questions = []
        for questions, permission in question_sets:
            readonly = permission == "readonly"
            questions = QuestionSerializer(questions, many=True).data

            for question in questions:
                question["readonly"] = readonly

                answer = answers.get(question["id"])
                if answer and not (
                    answer["is_considered_failure"] and answer["failure_is_reviewed"]
                ):
                    if lock_answers:
                        answer["confirmed"] = lock_answers
                    question[answer_storage_key] = answer

                qa_answer = qa_answers.get(question["id"])
                if qa_answer:
                    if lock_answers:
                        qa_answer["confirmed"] = lock_answers
                    question[qa_answer_storage_key] = qa_answer

                all_questions.append(question)

        return Response(all_questions)

    @action(detail=False, methods=["post"])
    def parse_blg(self, request, *args, **kwargs):
        fieldfile = clean_base64_encoded_payload("file", request.data.get("blg_file_raw", ""))
        serializer = FloorplanFromBlgSerializer(
            data={"file": fieldfile}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        floorplan = serializer.save()
        serializer = SimulationHomeBuildingParameterSerializer(instance=floorplan.simulation)
        return Response({"blg_data": serializer.data})

    @action(detail=True, methods=["get"])
    def eto_compliance_document(self, request, *args, **kwargs):
        """Issue current ETO City Of Hillsboro compliance document for signing."""

        from axis.customer_eto.serializers import PermitAndOccupancySettingsSerializer

        customer_eto_app = apps.get_app_config("customer_eto")

        home = self.get_object()
        user = self.request.user

        settings_obj, _ = home.permitandoccupancysettings_set.get_or_create(
            owner=user.company, home=home
        )

        # Lock settings, including anything that was inherited implicitly until now
        flat_settings = home.get_permit_and_occupancy_settings(user.company)
        serializer = PermitAndOccupancySettingsSerializer(
            instance=settings_obj, data=dict(request.data, **flat_settings)
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        permit_customer_document = home.customer_documents.filter(
            company=user.company, description=customer_eto_app.PERMIT_DESCRIPTION
        ).first()
        occupancy_customer_document = home.customer_documents.filter(
            company=user.company, description=customer_eto_app.OCCUPANCY_DESCRIPTION
        ).first()

        if not permit_customer_document:
            settings_obj.post_building_permit(user)
        elif not occupancy_customer_document:
            settings_obj.post_certificate_of_occupancy(user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def eto_compliance_option(self, request, *args, **kwargs):
        """Update ETO City Of Hillsboro compliance option."""

        from axis.customer_eto.models import PermitAndOccupancySettings
        from axis.customer_eto.serializers import PermitAndOccupancySettingsSerializer

        obj = self.get_object()
        user = self.request.user

        settings, created = PermitAndOccupancySettings.objects.get_or_create(
            owner=user.company, home=obj
        )
        serializer = PermitAndOccupancySettingsSerializer(instance=settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def customer_hirl_sync_documents_across_batch(self, request, *args, **kwargs):
        home = self.get_object()

        parent_hirl_project = HIRLProject.objects.filter(home_status__home=home).first()

        if not parent_hirl_project:
            return Response("NGBS Project not found", status=status.HTTP_400_BAD_REQUEST)

        child_projects = (
            parent_hirl_project.vr_batch_submission_rough_childrens.all()
            | parent_hirl_project.vr_batch_submission_final_childrens.all()
        ).distinct()

        child_homes = Home.objects.filter(homestatuses__customer_hirl_project__in=child_projects)

        for parent_document in home.customer_documents.all():
            for child_home in child_homes:
                CustomerDocument.objects.update_or_create(
                    company=parent_document.company,
                    document=parent_document.document,
                    object_id=child_home.pk,
                    content_type=ContentType.objects.get_for_model(Home),
                    defaults=dict(
                        is_active=parent_document.is_active,
                        is_public=parent_document.is_public,
                        type=parent_document.type,
                        filesize=parent_document.filesize,
                        description=parent_document.description,
                    ),
                )

        return Response("ol", status=status.HTTP_200_OK)


class HomeUsersViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Home
    queryset = model.objects.all()
    serializer_class = HomeUsersSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.home.views.machineries import HomeUsersExamineMachinery

        return HomeUsersExamineMachinery


class HomeStatusViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = EEPProgramHomeStatus
    queryset = model.objects.all()
    serializer_class = HomeStatusSerializer
    throttle_scope = "checklist"

    # ExamineView add-ins
    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import (
            HomeStatusExamineMachinery,
            InvoiceHomeStatusExamineMachinery,
            HIRLProjectRegistrationContactsHomeStatusExamineMachinery,
        )
        from axis.subdivision.views import (
            HIRLProjectRegistrationContactsSubdivisionExamineMachinery,
        )
        from axis.qa.views.examine import FieldQAHomeStatusExamineMachinery

        return {
            None: HomeStatusExamineMachinery,
            "HomeStatusExamineMachinery": HomeStatusExamineMachinery,
            "FieldQAHomeStatusExamineMachinery": FieldQAHomeStatusExamineMachinery,
            "InvoiceHomeStatusExamineMachinery": InvoiceHomeStatusExamineMachinery,
            "HIRLProjectRegistrationContactsHomeStatusExamineMachinery": HIRLProjectRegistrationContactsHomeStatusExamineMachinery,
            "HIRLProjectRegistrationContactsSubdivisionExamineMachinery": HIRLProjectRegistrationContactsSubdivisionExamineMachinery,
        }

    def get_object(self):
        # NOTE: There is no per-user filtering here.  Not sure if that's intended.

        lookup = {}

        if "pk" in self.kwargs:
            lookup["pk"] = self.kwargs["pk"]
        if "home_id" in self.kwargs:
            lookup["home_id"] = self.kwargs["home_id"]
        if "eep_program_id" in self.kwargs:
            lookup["eep_program_id"] = self.kwargs["eep_program_id"]

        if lookup:
            queryset = EEPProgramHomeStatus.objects.filter_by_user(self.request.user)
            objects = queryset.filter(**lookup)
            obj = objects.first()
        else:
            obj = super(HomeStatusViewSet, self).get_object()

        return obj

    def filter_queryset(self, queryset):
        params = self.request.query_params.dict()
        valid_fields = [f.name for f in self.model._meta.get_fields()]
        provided_fields = set(params.keys())
        return queryset.filter(**{k: params[k] for k in provided_fields.intersection(valid_fields)})

    # Externals
    def list(self, request, *args, **kwargs):
        if "progress" in self.request.path:
            return self.progress(request, *args, **kwargs)
        return super(HomeStatusViewSet, self).list(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def invoice_item_groups_machinery(self, request, *args, **kwargs):
        """
        Return machinery from external API endpoint to be able to refresh whole RegionSet
        """
        from axis.home.views.machineries import HIRLInvoiceItemGroupExamineMachinery

        instance = self.get_object()
        invoice_item_group_machinery = HIRLInvoiceItemGroupExamineMachinery(
            objects=instance.invoiceitemgroup_set.all(), context={"request": self.request}
        )
        return Response(invoice_item_group_machinery.get_summary())

    @action(detail=True, methods=["post"])
    def decertify(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        user = self.request.user
        if obj.can_be_decertified(user):
            obj.decertify(user=user, check_only=False, report=False)
        else:
            log.error("Homestatus pk=%r cannot be decertified", obj.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def progress(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Initialize input-collection if required
        # NOTE: In general, this is to combat the fact that Axis doesn't have a very
        # unified way to guarantee the initialization state of objects it creates in its
        # various ways, since even the state machine isn't guaranteed to be ready when
        # methods like this is are called too incidentally as the object is being handled.
        uses_input_collection = obj.eep_program.collection_request_id
        needs_initialization = not obj.collection_request
        if uses_input_collection and needs_initialization:
            obj.set_collection_from_program()

        return Response(
            obj.get_progress_analysis(
                as_list=True, skip_certification_check=True, user=self.request.user
            )
        )

    @action(detail=False)
    def progress_multiple(self, request, *args, **kwargs):
        objects = self.filter_queryset(self.get_queryset())
        id_list = request.query_params.getlist("id")
        valid_integers = list(filter(lambda val: val.isdigit(), id_list))
        objects = objects.filter(id__in=valid_integers)

        data = {
            "object_list": {
                o.pk: o.get_progress_analysis(
                    as_list=True, skip_certification_check=True, user=request.user
                )
                for o in objects
            }
        }

        return Response(data)

    @action(detail=True)
    def questions(self, request, *args, **kwargs):
        home_status = self.get_object()
        user = self.request.user
        readonly = kwargs.get("readonly")

        if "eep_program_id" in kwargs:
            owner = home_status.company
            eep_program = home_status.eep_program
        else:
            owner = user.company
            eep_program = None

        questions = self.get_questions(home_status, owner, eep_program, readonly)
        answers = self.get_answers(home_status, owner, eep_program, readonly)
        answers = AnswerSerializer(answers, many=True).data

        for question in questions:
            answer = [x for x in answers if x["question"] == question["id"]]
            answer = [
                x for x in answer if not (x["is_considered_failure"] and x["failure_is_reviewed"])
            ]
            if answer:
                question["answer"] = answer[0]

        return Response(questions)

    @action(detail=True)
    def question_summary(self, request, *args, **kwargs):
        from axis.checklist.models import Question

        obj = self.get_object()
        questions = Question.objects.filter_by_home_status(obj)

        source_answers = build_questionanswer_dict(
            questions, obj.get_source_sampleset_answers(include_failures=False)
        )
        contributed_answers = build_questionanswer_dict(
            questions, obj.get_contributed_sampleset_answers()
        )
        failing_answers = build_questionanswer_dict(questions, obj.get_failing_sampleset_answers())

        builder = obj.home.get_builder()
        sshs = obj.get_samplesethomestatus()
        if sshs:
            is_test_home = sshs.is_test_home
        else:
            is_test_home = bool(obj.get_source_sampleset_answers().count())
        return Response(
            {
                "home_status_id": obj.id,
                "eep_program_id": obj.eep_program_id,
                "is_test_home": is_test_home,
                "eep_program": obj.eep_program.name,
                "subdivision_id": obj.home.subdivision_id,
                "subdivision": getattr(obj.home.subdivision, "name", None),
                "metro_id": obj.home.metro_id,
                "metro": getattr(obj.home.metro, "name", None),
                "builder_id": builder.id,
                "builder": builder.name,
                "name": obj.home.get_addr(),
                "source_answers": source_answers,
                "contributed_answers": contributed_answers,
                "failing_answers": failing_answers,
                "is_certified": bool(obj.certification_date),
                "detail_url": obj.home.get_absolute_url(),
            }
        )

    def get_questions(self, home_status, owner, eep_program, readonly):
        # TODO: write a test.
        return Question.objects.filter_by_home_status(home_status)
        # return Question.objects.filter_by_home_for_rating_company(
        #     home_status.home, owner, include_unphased=True,
        #     eep_program=eep_program, readonly=readonly)

    def get_answers(self, home_status, owner, eep_program, readonly):
        # TODO: write a test.
        # TODO: how to handle filtering along side samplesets in this case

        answers = (
            Answer.objects.filter_by_home(home_status.home).filter_by_company(owner).filter_by_eep
        )

        if eep_program:
            answers = answers.filter_by_eep(eep_program)

        return answers

    def get_examine_form_kwargs(self, form_class):
        kwargs = super(HomeStatusViewSet, self).get_examine_form_kwargs(form_class)
        kwargs["user"] = self.request.user
        if self.object.pk:
            kwargs["home"] = self.object.home
        else:
            home_id = getattr(self.request, self.request.method).get("home")
            if home_id:
                try:
                    home = Home.objects.filter_by_user(self.request.user).get(id=home_id)
                except Home.DoesNotExist:
                    home = None
            else:
                home = None
            kwargs["home"] = home
        return kwargs

    def _save(self, serializer):
        from .tasks import update_home_states

        try:
            company_id = int(self.request.data.get("company"))
        except Exception:
            company = None
        else:
            queryset = get_owner_swap_queryset(self.request.user)
            if queryset:
                company = queryset.filter(id=company_id).first()
            else:
                company = None

        # Reset to dynamic
        if company is None:
            company = self.request.company

        obj = serializer.save(company=company)

        update_home_states(eepprogramhomestatus_id=obj.id, user_id=self.request.user.id)

        # Re-fetch the object from the database.
        # The instance will have cached its value for the current state (StateModel), and doing
        # more saves will actually revert the state to the cached one.
        obj = obj.__class__.objects.get(id=obj.id)

        create_or_update_spanning_relationships(self.request.user.company, obj)

        # Ping valid ``QARequirement.qa_company`` companies of new programs used in subdivision.
        notify_of_subdivision_qa(obj, self.request.user)

    def perform_create(self, serializer):
        self._save(serializer)

        # Newly saved instance
        obj = serializer.instance

        eep_program = obj.eep_program
        url = obj.home.get_absolute_url()
        context = {
            "home": """<a href="{url}">{address}</a>""".format(url=url, address=obj.home),
            "visibility_date": eep_program.program_visibility_date.strftime("%B %d, %Y")
            if eep_program.program_visibility_date
            else None,
            "start_date": eep_program.program_start_date.strftime("%B %d, %Y")
            if eep_program.program_start_date
            else None,
            "close_date": eep_program.program_close_date.strftime("%B %d, %Y")
            if eep_program.program_close_date
            else None,
            "submit_date": eep_program.program_submit_date.strftime("%B %d, %Y")
            if eep_program.program_submit_date
            else None,
            "end_date": eep_program.program_end_date.strftime("%B %d, %Y")
            if eep_program.program_end_date
            else None,
        }

        # Deliver notification of program sunset if applicable
        today = now().date()
        if (
            obj.eep_program.program_submit_warning_date
            and obj.eep_program.program_submit_warning_date <= today
        ):
            msg = ProgramSubmitSunsetMessage(url=url)
            msg.content = eep_program.program_submit_warning
            msg().send(context=context, user=self.request.user)

        if (
            obj.eep_program.program_close_warning_date
            and obj.eep_program.program_close_warning_date <= today
        ):
            msg = ProgramSunsetMessage(url=url)
            msg.content = eep_program.program_close_warning
            msg().send(context=context, user=self.request.user)

    def perform_update(self, serializer):
        self._save(serializer)

    def _get_floorplan_regions(self, home_status):
        from axis.home.views.machineries import HomeStatusFloorplanExamineMachinery

        floorplans = home_status.floorplans.all()
        machinery = HomeStatusFloorplanExamineMachinery(
            objects=floorplans,
            context={
                "home_status": home_status,
            },
        )
        return machinery.get_regions()

    def get_form_content_context(self, **kwargs):
        """Adds extra form information for a set of inlines."""
        context = super(HomeStatusViewSet, self).get_form_content_context(**kwargs)
        obj = context["form"].instance
        if obj.pk:
            context["floorplan_regions"] = self._get_floorplan_regions(obj)
            # context['simplified_status'] = obj.get_simplified_status_for_user(self.request.user)
        return context

    @action(detail=True)
    def eps_data(self, request, *args, **kwargs):
        """This brings the core of the resulting data for EPS - Allows for a force recalculate"""

        obj = self.get_object()
        if obj is None or obj.eep_program is None:
            return Response({"errors": ["We have been deleted"]}, status=status.HTTP_204_NO_CONTENT)

        if "eto" not in obj.eep_program.slug:
            return Response({"errors": ["This only applies to the ETO Program"]})

        results = get_eps_data(obj, **kwargs)

        status_code = status.HTTP_400_BAD_REQUEST if ("errors" in results) else status.HTTP_200_OK

        return Response(results, status=status_code)

    @action(detail=True, methods=["post"])
    def transition(self, request, *args, **kwargs):
        """
        Uses the state transition name in POST data as ``action`` to move the homestatus down the
        state machine pipeline.
        """

        from django_states.exceptions import PermissionDenied

        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        action = request.data["action"]

        try:
            instance.full_transition(action, request.user)
        except PermissionDenied:
            states = dict(instance.Machine.get_state_choices())
            to_state = instance.Machine.transitions[action].to_state

            pretty_name = states[to_state]
            message = "Cannot transition to {}, Permission denied.".format(pretty_name)
            return Response(message, status=status.HTTP_403_FORBIDDEN)
        except TransitionCannotStart as err:
            return Response(str(err), status=status.HTTP_304_NOT_MODIFIED)
        else:
            return Response("OK", status=status.HTTP_200_OK)

    @action(detail=True)
    def can_certify(self, request, *args, **kwargs):
        from axis.home.utils import HomeCertification

        check = HomeCertification(
            self.request.user,
            self.get_object(),
            datetime.datetime.today().date(),
            log=log,
            fail_fast=False,
        )

        if not check.verify(log_errors=False):
            return Response(check.errors, status=400)

        return Response()

    @action(detail=True)
    def certify(self, request, *args, **kwargs):
        from axis.home.tasks import certify_single_home
        from datetime import datetime

        bypass_check = request.GET.get("bypass_check", False) == "true"
        certification_date = request.GET.get("certification_date", False)

        try:
            certification_date = datetime.strptime(certification_date, "%Y-%m-%d").date()
        except ValueError:
            try:
                certification_date = dateutil.parser.parse(certification_date).date()
            except Exception as e:
                log.error(e, exc_info=True, extra={"request": request})
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # Update stats to make sure everything is at the latest.
        obj = self.get_object()
        obj.update_stats()
        obj = self.get_object()

        try:
            report = {
                "data": certify_single_home(
                    self.request.user,
                    obj,
                    certification_date,
                    bypass_check=bypass_check,
                    throw_errors=True,
                ),
                "state": self.get_object().state,
            }
        except Exception as e:
            log.error(e, exc_info=True, extra={"request": request})
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(report)

    @action(
        detail=True,
        methods=[
            "POST",
        ],
    )
    def customer_hirl_certify_childrens(self, request, *args, **kwargs):
        instance = self.get_object()
        reports = [
            "Success",
        ]

        home_status_list = [
            instance,
        ]
        certification_list = []
        certification_date = timezone.now()

        if getattr(instance, "customer_hirl_project", None):
            hirl_project = instance.customer_hirl_project
            final_childrens = hirl_project.vr_batch_submission_final_childrens.exclude(
                home_status__state=EEPProgramHomeStatus.COMPLETE_STATE
            ).select_related("home_status")
            for child in final_childrens:
                home_status_list.append(child.home_status)

        for home_status in home_status_list:
            certification = HomeCertification(
                user=self.request.user,
                stat=home_status,
                certification_date=certification_date,
                log=log,
            )
            if certification.already_certified:
                continue
            if not certification.verify():
                raise serializers.ValidationError(certification.errors)
            certification_list.append(certification)

        for certification in certification_list:
            certification.certify()

        return Response(reports)

    @action(detail=True)  # FIXME: This is a GET endpoint but it performs POST-like work
    def add_program_review_qa(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Get QA Requirement
        try:
            requirement = QARequirement.objects.get(
                qa_company=request.user.company, eep_program=obj.eep_program, type="program_review"
            )
        except QARequirement.DoesNotExist:
            message = "{company} does not have any QA Requirements for {program}"
            message = message.format(program=obj.eep_program, company=request.user.company)
            return Response([message], status=status.HTTP_400_BAD_REQUEST)

        # Create QAStatus for Home Status
        try:
            qa_status = QAStatus.objects.create(
                owner=request.user.company,
                requirement=requirement,
                state="correction_required",
                home_status=obj,
            )
        except IntegrityError:
            return Response("Home already has QA.", status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {"message": "Program Review Added", "object": qa_status}

        # Roll this thing back to pending QA.
        if obj.state == "certification_pending":
            try:
                obj.make_transition("certification_pending_to_pending_qa", user=request.user)
                data["message"] += " and program state moved to %s" % obj.state_description
            except Exception as err:
                log.warning("User: %s Project: %s - %s", request.user, obj.id, err)
        else:
            log.info("Program %s - ", obj.state)

        # Check if the user provided a note
        try:
            note = request.GET["note"]
        except KeyError:
            pass
        else:
            content_type = ContentType.objects.get_for_model(obj)
            content_type_id = obj.id
            note_kwargs = {
                "qa_status": qa_status,
                "note": note,
                "user": request.user,
                "content_type": content_type,
                "object_id": content_type_id,
            }
            QANote.objects.create(**note_kwargs)

            data["message"] += " - QA Note added"

        # send message that Home Status is in Correction Required
        from axis.qa.messages import QaCorrectionRequiredMessage
        from axis.qa.utils import get_content_object_data_for_qa_messages, get_qa_message_context

        # Send correction required message here.
        # The state machine only handles messages when transitioning into correction required.
        # Here we're creating the status in correction required.
        qa_message_data = get_content_object_data_for_qa_messages(qa_status)
        context = get_qa_message_context(qa_status, qa_message_data)
        QaCorrectionRequiredMessage(
            url=context["action_url"],
        ).send(
            context=context,
            company=obj.company,
        )

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True)
    def resnet(self, request, *args, **kwargs):
        from axis.resnet.utils import submit_home_status_to_registry

        try:
            return Response(submit_home_status_to_registry(self.get_object(), request.user))
        except Exception as err:
            return Response(
                {"message": err.args[0], "errors": err.args}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True)
    def rtf_calculator(self, request, *args, **kwargs):
        from axis.customer_neea.rtf_calculator.calculator import NEEAV2Calculator
        from ..customer_neea.rtf_calculator.base import RTFInputException

        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        answer_data = dict(instance.annotations.all().values_list("type__slug", "content"))
        answer_data = {k.replace("-", "_"): v for k, v in answer_data.items()}

        input_values = instance.get_input_values(user_role="rater")
        input_answers = {
            measure.replace("neea-", ""): value for measure, value in input_values.items()
        }

        answer_data.update(input_answers)

        calculator_class = NEEAV3Calculator
        if instance.eep_program.slug == "neea-bpa":
            calculator_class = NEEAV2Calculator

        try:
            calculator = calculator_class(home_status_id=instance.id, **answer_data)
            # print(calculator.report())
            # print(calculator.heating_cooling_report())
            # print(calculator.hot_water_report())
            # print(calculator.lighting_report())
            # print(calculator.appliance_report())
            # print(calculator.thermostat_report())
            # print(calculator.shower_head_report())
            # print(calculator.total_report())
            # print(calculator.incentives.report())
        except RTFInputException as issues:
            return Response(
                {"message": issues.args[0], "errors": issues.args[1:]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(calculator.result_data())


class HomeStatusFloorplansViewSet(viewsets.ModelViewSet):
    """An m2m deletion endpoint provider."""

    model = EEPProgramHomeStatus.floorplans.through
    queryset = model.objects.all()

    serializer_class = HomeStatusFloorplansThroughSerializer

    def perform_destroy(self, instance):
        home_status = instance.eepprogramhomestatus
        super(HomeStatusFloorplansViewSet, self).perform_destroy(instance)

        home_status.floorplan = home_status.calculate_active_floorplan()
        home_status.save()
        home_status.validate_references()


class HomeStatusAnnotationsViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = EEPProgramHomeStatus
    queryset = model.objects.all()
    serializer_class = HomeStatusAnnotationsSerializer

    _update = False

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.home.views.machineries import AnnotationsHomeStatusExamineMachinery

        return AnnotationsHomeStatusExamineMachinery

    def update(self, *args, **kwargs):
        """Set a flag before running the normal Update process when PUT/PATCH is used."""
        self._update = True
        return super(HomeStatusAnnotationsViewSet, self).update(*args, **kwargs)

    def _built_green_serializer(self, serializer):
        sections = [
            serializer.data["built-green-points-section-1"],
            serializer.data["built-green-points-section-2"],
            serializer.data["built-green-points-section-3"],
            serializer.data["built-green-points-section-4"],
            serializer.data["built-green-points-section-5"],
            serializer.data["built-green-points-section-6"],
            serializer.data["built-green-points-section-7"],
        ]
        sections = [float(section) for section in sections if section not in [None, ""]]
        if len(sections) == 7:
            serializer.cleaned_data["total-built-green-points"] = sum(sections)
        return serializer

    def _wa_code_study(self, serializer):
        """Gets the Washington Code Study points"""
        from axis.customer_neea.strings import WA_CODE_STUDY_POINTS_ASSIGNMENT

        points = 0
        for key, values in WA_CODE_STUDY_POINTS_ASSIGNMENT.items():
            if key == "dwelling-type":
                continue
            points += WA_CODE_STUDY_POINTS_ASSIGNMENT[key][serializer.data[key]]
        serializer.cleaned_data["wa-code-study-score"] = points
        return serializer

    def _save(self, serializer):
        if "built-green-points-section-1" in serializer.data:
            serializer = self._built_green_serializer(serializer)
        if "dwelling-type" in serializer.data:
            serializer = self._wa_code_study(serializer)

        obj = serializer.save()

        from .tasks import update_home_states

        update_home_states(eepprogramhomestatus_id=obj.id, user_id=self.request.user.id)
        obj.validate_references()

    perform_create = _save
    perform_update = _save

    def get_serializer(self, instance, *args, **kwargs):
        """Returns the form class that can save the annotations instead of a serializer."""
        # This is pretty much hack city, but eventually we can merge the idea of the form and the
        # serializer so that this isn't a thing anymore.
        if self._update:
            form = get_required_annotations_form(instance, *args, user=self.request.user, **kwargs)
            form.object = form.instance
            return form
        return super(HomeStatusAnnotationsViewSet, self).get_serializer(instance, *args, **kwargs)


class HomeStatusPipelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This is used for pipeline reporting
    """

    model = EEPProgramHomeStatus
    serializer_class = HomeStatusSerializer

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(self.request.user)
        return self.filter_queryset(queryset)

    def filter_queryset(self, queryset):
        filters = self.request.query_params.dict()

        start = filters.get("created_date__gte", "{}-1-1".format(now().year))
        self.start = dateutil.parser.parse(start)
        end = filters.get("end_date", "{}-{}-{}".format(now().year, now().month, now().day))
        self.end = dateutil.parser.parse(end) + datetime.timedelta(hours=23, minutes=59, seconds=59)

        filters["created_date__gte"] = self.start
        filters["created_date__lte"] = self.end

        return queryset.filter(**filters)

    @cache_api_response(by_user=True)
    def list(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        counted = Counter(list(self.object_list.values_list("state", flat=True)))

        data = {"object_list": [], "start-date": self.start, "end-end": self.end}
        if self.request.query_params.dict():
            data["filters"] = self.request.query_params.dict()
        for state, label in HomeStatusStateMachine.get_state_choices():
            if state in counted.keys():
                data["object_list"].append(
                    {"state": state, "label": label, "count": counted.get(state)}
                )

        return Response(data)


class FindCertifiedHomeSerializer(serializers.ModelSerializer):
    street_line1 = serializers.SerializerMethodField()
    street_line2 = serializers.SerializerMethodField()
    zipcode = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    eep_program = serializers.SerializerMethodField()
    floorplan = serializers.SerializerMethodField()
    home = serializers.SerializerMethodField()
    certification_date = serializers.SerializerMethodField()
    is_legacy = serializers.SerializerMethodField()

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "id",
            "certification_date",
            "city_name",
            "eep_program",
            "floorplan",
            "home",
            "is_legacy",
            "state",
            "street_line1",
            "street_line2",
            "zipcode",
        )

    def get_home(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return reverse("apiv2:legacy_neea_home-detail", kwargs={"pk": obj.pk})
        return reverse("apiv2:home-detail", kwargs={"pk": obj.pk})

    def get_certification_date(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            try:
                return obj.legacyneeainspection_set.all()[0].certification_date
            except (IndexError, AttributeError):
                return "-"
        return obj.certification_date

    def get_street_line1(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return obj.address.get_formatted_address(line1_only=True)
        return obj.home.street_line1

    def get_street_line2(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return None
        return obj.home.street_line2

    def get_zipcode(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return obj.address.zip_code.zip_code
        return obj.home.zipcode

    def get_state(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            try:
                return obj.address.zip_code.state_abbr
            except AttributeError:
                return "-"
        return obj.home.city.state

    def get_city_name(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            try:
                return obj.address.zip_code.city
            except AttributeError:
                return "-"
        return obj.home.city.name

    def get_eep_program(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            try:
                return obj.legacyneeainspection_set.all()[0].bop.name
            except (IndexError, AttributeError):
                return "-"
        return obj.eep_program.name

    def get_floorplan(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return None
        try:
            return obj.floorplan.name
        except AttributeError:
            return "-"

    def get_is_legacy(self, obj):
        if isinstance(obj, LegacyNEEAHome):
            return True
        return False


class FindCertifiedHomeViewSet(viewsets.ReadOnlyModelViewSet):
    model = EEPProgramHomeStatus
    queryset = model.objects.all()
    serializer_class = FindCertifiedHomeSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(self.request.user)

        legacy_home_qs = LegacyNEEAHome.objects.filter_by_user(self.request.user)

        return self.filter_querysets(queryset, legacy_home_qs)

    def filter_queryset(self, queryset):
        """
        If any filtering needs to be done, do it in self.filter_querysets().
        By the time the querysets get to here, they are lists because of the requirements
        of this endpoint.
        """
        return queryset

    def filter_querysets(self, queryset, legacy_home_qs):
        # Only get certified objects
        queryset = queryset.filter(certification_date__isnull=False)
        legacy_home_qs = legacy_home_qs.filter(
            legacyneeainspection__certification_date__isnull=False
        )

        # Apply user filters
        filters = self.request.query_params.dict()
        applicable_filters = self.build_filters(filters=filters)
        applicable_neea_filters, extra_q = self.build_neea_filters(filters=applicable_filters)

        queryset = queryset.filter(**applicable_filters["filter"]).exclude(
            **applicable_filters["exclude"]
        )
        legacy_home_qs = legacy_home_qs.filter(**applicable_neea_filters["filter"]).exclude(
            **applicable_neea_filters["exclude"]
        )
        if extra_q:
            legacy_home_qs = legacy_home_qs.filter(extra_q)

        # Because we are paginating, prefetching things slows down making them a list.
        # select and prefetch needed related
        # queryset = queryset.select_related('home', 'home__city', 'home__city__county__state',
        #                                    'eep_program', 'floorplan')
        # legacy_home_qs = legacy_home_qs.select_related('legacyneeainspection_set__bop__name',
        #                                                'address')

        return list(queryset) + list(legacy_home_qs)

    def build_neea_filters(self, filters):
        # Includes everything except for street name fields (number, modifier, name)
        neea_filters = {
            "home__zipcode": "address__zip_code",
            "certification_date": "legacyneeainspection__certification_date",
            "home__city__name": "address__zip_code__city",
            "home__state": "address__zip_code__state_abbr",
            "eep_program__name": "legacyneeainspection__bop__name",
        }
        new_filters = {}
        suffixes = ("startswith", "endswith", "contains", "icontains", "exact")

        def split_suffix(field):
            bits = field.split("__")
            has_suffix = False
            suffix = bits[-1]
            if suffix in suffixes:
                field = "__".join(bits[:-1])
                has_suffix = True
            return field, suffix, has_suffix

        for filter_type, filter in iter(filters.items()):
            new_filters[filter_type] = {}
            for field, value in iter(filter.items()):
                field, suffix, has_suffix = split_suffix(field)
                new_field = neea_filters.get(field)

                if not new_field:
                    log.warning("Skipping legacy raw.. {}".format(field))
                    continue

                if has_suffix:
                    new_field += "__" + suffix
                new_filters[filter_type][new_field] = value

        # Now build the street address filter.
        # The street name is broken up into three separate db columns, and guessing how to parse the
        # incoming string into components to put against those columns.
        full_query_list = []  # Only 2 items, for 'filter' and 'exclude' respectively
        for filter_type, filter in iter(filters.items()):
            full_field = None
            for k in filter:
                if k.startswith("home__street_line1"):
                    full_field = k
                    break
            else:
                continue

            field, suffix, has_suffix = split_suffix(full_field)
            bits = [bit.strip() for bit in filter[full_field].split()]
            if bits:
                filter_query_list = []  # 1 Q() per split component in the search
                for bit in bits:
                    field_query_list = []  # For the current search bit, 1 Q() per search column
                    for column in [
                        "address__street_no",
                        "address__street_modifier",
                        "address__street_name",
                    ]:
                        q = Q(**{column + "__contains": bit})
                        field_query_list.append(q)
                    # Join with OR operator, because it doesn't matter which column the search bit
                    # is found in.
                    filter_query_list.append(reduce(operator.or_, field_query_list))
                # Join with AND operator, because all search bits need to be found
                query = reduce(operator.and_, filter_query_list)
                if filter_type == "exclude":
                    query = ~query
                full_query_list.append(query)
        # Join with AND operator, because 'filter' and 'exclude' are be considered simultaneously.
        # We could have 0, 1, or 2 items in the list, based on combinations of filter/exclude.
        if full_query_list:
            extra_query = reduce(operator.and_, full_query_list)
        else:
            extra_query = None

        # if new_field == 'address__street_no':
        #     value_bits = value.split(' ', 1)
        #     if value_bits[0].isdigit():
        #         sub_field = new_field
        #         if has_suffix:
        #             sub_field += "__" + suffix
        #         new_filters[filter_type][sub_field] = value_bits[0]
        #
        #         if len(value_bits) == 2:
        #             value = value_bits[1]
        #             new_field = 'address__street_name'
        #     else:
        #         new_field = 'address__street_name'

        return new_filters, extra_query

    def build_filters(self, filters=None):
        applicable_filters = {"filter": {}, "exclude": {}}
        if not filters:
            return applicable_filters

        suffixes = ("startswith", "endswith", "contains", "icontains", "exact")
        auto_suffix_fields = ("home__street_line1",)

        def ensure_suffix(field):
            invert = field.endswith("!")

            suffix = field.split("__")[-1]
            if invert:  # take operator away
                field = suffix[:-1]

            suffix = field.split("__")[-1]
            if suffix not in suffixes:
                field += "__icontains"

            if invert:  # add operator back
                field += "!"
            return field

        for x in filters:
            if x in ["page", "format", "fields"]:
                continue
            orm_field = x
            if x in auto_suffix_fields:
                orm_field = ensure_suffix(x)

            if x.endswith("!"):
                applicable_filters["exclude"][orm_field] = filters[x]
            else:
                applicable_filters["filter"][orm_field] = filters[x]

        return applicable_filters


class HomeStatusExportFieldsFormAPIView(views.APIView):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        from axis.home.forms import HomeStatusExportFieldsForm

        form = HomeStatusExportFieldsForm()
        excluded = form.get_excluded_fields(request.user, exclude_fields=True)

        return Response(
            {"form": form, "excluded": excluded},
            template_name="home/includes/export_fields_form.html",
            content_type="text/html",
        )


class ReportQuickLinksCountViewSet(viewsets.ViewSet):
    def list(self, request):
        view = self.get_view(request)
        quick_links = view.process_quick_links(view.get_quick_links())
        return Response(quick_links)

    def get_view(self, request):
        view_class = self.get_view_class()
        return view_class(request=request)

    def get_view_class(self):
        view_classes = self.get_view_classes()

        view_name = self.request.query_params.get("view", None)
        view_class = view_classes.get(view_name)

        if view_class:
            return view_class

        if None in view_classes:
            return view_classes[None]

        raise ValueError(
            "%s must return a class from 'get_view_classes()'" % (self.__class__.__name__,)
        )

    def get_view_classes(self):
        from axis.home.views import ProviderDashboardView

        return {"provider_dashboard": ProviderDashboardView}


class HomeStatusHIRLProjectViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = HIRLProject
    queryset = model.objects.all()
    serializer_class = HomeStatusHIRLProjectSerializer

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(user=self.request.user)

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import (
            HIRLProjectSingleFamilyExamineMachinery,
            HIRLProjectMultiFamilyExamineMachinery,
            HIRLProjectLandDevelopmentExamineMachinery,
        )

        return {
            "HIRLProjectSingleFamilyExamineMachinery": HIRLProjectSingleFamilyExamineMachinery,
            "HIRLProjectMultiFamilyExamineMachinery": HIRLProjectMultiFamilyExamineMachinery,
            "HIRLProjectLandDevelopmentExamineMachinery": HIRLProjectLandDevelopmentExamineMachinery,
        }


class HIRLInvoiceItemGroupViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = InvoiceItemGroup
    queryset = model.objects.all().prefetch_related(
        Prefetch("invoice", queryset=Invoice.objects.all())
    )
    serializer_class = HIRLInvoiceItemGroupSerializer

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(user=self.request.user)

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import HIRLInvoiceItemGroupExamineMachinery

        return {
            "HIRLInvoiceItemGroupExamineMachinery": HIRLInvoiceItemGroupExamineMachinery,
        }


class HIRLInvoiceItemViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = InvoiceItem
    queryset = model.objects.all()
    serializer_class = HIRLInvoiceItemSerializer

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(user=self.request.user)

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import HIRLInvoiceItemExamineMachinery

        return {
            "HIRLInvoiceItemExamineMachinery": HIRLInvoiceItemExamineMachinery,
        }
