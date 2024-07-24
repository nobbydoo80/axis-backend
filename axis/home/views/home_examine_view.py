"""Base class for Home Examine Views"""

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType

from analytics.models import AnalyticRollup

from axis.checklist.models import QAAnswer
from axis.core.views.generic import AxisExamineView
from axis.core.views.machinery import object_relationships_machinery_factory
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.home.models import Home, EEPProgramHomeStatus
from axis.home.views.utils import _get_home_contributor_flag
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.qa.models import QANote, QAStatus, get_stats_available_for_qa, QARequirement
from axis.scheduling.models import TaskType, Task
from axis.core.models import RecentlyViewed
from axis.scheduling.views import TaskTypeMachinery, TaskHomeMachinery
from .machineries import (
    HomeExamineMachinery,
    HomeQANoteDocumentExamineMachinery,
    HomeQAAnswerDocumentExamineMachinery,
    HomeAnswerDocumentExamineMachinery,
    HomeStatusExamineMachinery,
    HomeUsersExamineMachinery,
    HomeRelationshipsExamineMachinery,
    InvoiceHomeStatusExamineMachinery,
    HIRLProjectRegistrationContactsHomeStatusExamineMachinery,
    HomeDocumentAgreementBase,
    HomeDocumentActionsMachinery,
)
from axis.customer_hirl.models import HIRLProject

customer_hirl_app = apps.get_app_config("customer_hirl")


class HomeExamineView(LoginRequiredMixin, AxisExamineView):
    """Builds the machineries required for loading the page."""

    model = Home
    homestatuses = None

    def get_queryset(self):
        """Returns a queryset for the user"""
        return Home.objects.filter_by_user(user=self.request.user)

    def get_machinery_kwargs(self):
        """Returns the machinery kwargs - this will feed the machineries"""
        return {
            "create_new": self.create_new,
            "context": {"lightweight": True, "request": self.request},
        }

    def get_machinery(self):
        """Returns the machinery machinery"""
        # pylint: disable=too-many-locals

        home = self.object
        user = self.request.user

        # Common kwargs sent to all machineries
        kwargs = self.get_machinery_kwargs()

        machineries = {}

        # Home
        machinery = HomeExamineMachinery(instance=home, **kwargs)
        machineries[machinery.type_name_slug] = machinery
        self.primary_machinery = machinery

        # Relationships
        machinery_class = object_relationships_machinery_factory(
            self.model, bases=(HomeRelationshipsExamineMachinery,)
        )

        machinery = machinery_class(instance=self.object, **kwargs)
        machineries["relationships"] = machinery

        # Homestatuses
        homestatuses = EEPProgramHomeStatus.objects.none()
        if not self.create_new:
            homestatuses = (
                EEPProgramHomeStatus.objects.filter_by_user(
                    user=user, home=home, eep_program__is_qa_program=False
                )
                .select_related("floorplan", "eep_program")
                .order_by("id")
            )
        machinery = HomeStatusExamineMachinery(objects=homestatuses, **kwargs)
        machineries[machinery.type_name_slug] = machinery
        self.homestatuses = homestatuses  # Save this for get_context_data stuff

        # Documents
        documents, answers_with_docs, qaanswers_with_docs, qanotes_with_docs = (
            [],
            [],
            [],
            [],
        )
        if not self.create_new:
            documents = home.customer_documents.filter_by_user(user, include_public=True)
            answers_with_docs = (
                home.get_answers().filter(customer_documents__id__isnull=False).distinct()
            )

            qaanswers_with_docs = QAAnswer.objects.filter_by_home(home, allow_sampling=False)
            qaanswers_with_docs = qaanswers_with_docs.filter(
                customer_documents__id__isnull=False
            ).distinct()

            qanotes = QANote.objects.filter(qa_status__in=home.get_qa_statuses())
            qanotes_with_docs = qanotes.filter(customer_documents__id__isnull=False).distinct()

        if home and home.pk:
            parent_hirl_project = HIRLProject.objects.filter(home_status__home=home).first()
            if parent_hirl_project:
                child_projects = (
                    parent_hirl_project.vr_batch_submission_rough_childrens.all()
                    | parent_hirl_project.vr_batch_submission_final_childrens.all()
                ).distinct()

                if child_projects:
                    home_document_actions_machinery = HomeDocumentActionsMachinery(
                        instance=home, **kwargs
                    )
                    machineries[
                        home_document_actions_machinery.type_name_slug
                    ] = home_document_actions_machinery

        customer_document_machinery_class = customerdocument_machinery_factory(
            self.model,
            allow_multiple=True,
            bases=(HomeDocumentAgreementBase,),
        )

        machineries.update(
            {
                "documents": customer_document_machinery_class(objects=documents, **kwargs),
                "answers_with_docs": HomeAnswerDocumentExamineMachinery(
                    objects=answers_with_docs, **kwargs
                ),
                "qaanswers_with_docs": HomeQAAnswerDocumentExamineMachinery(
                    objects=qaanswers_with_docs, **kwargs
                ),
                "qanotes_with_docs": HomeQANoteDocumentExamineMachinery(
                    objects=qanotes_with_docs, **kwargs
                ),
            }
        )

        # Home.users
        # This is automatically correct by sending it self.create_new with an unsaved instance.
        machinery = HomeUsersExamineMachinery(instance=home, **kwargs)
        machineries[machinery.type_name_slug] = machinery

        # Home status machinery that contains Invoice Item Groups
        homestatuses_with_hirl_project = homestatuses.filter(customer_hirl_project__isnull=False)
        machinery = InvoiceHomeStatusExamineMachinery(
            objects=homestatuses_with_hirl_project, **kwargs
        )
        machineries[machinery.type_name_slug] = machinery

        machinery = HIRLProjectRegistrationContactsHomeStatusExamineMachinery(
            objects=homestatuses_with_hirl_project, **kwargs
        )
        machineries[machinery.type_name_slug] = machinery

        task_types, tasks = [], []
        if not self.create_new:
            task_types = TaskType.objects.filter_by_user(user).filter(
                content_type=ContentType.objects.get_for_model(Home)
            )
            tasks = Task.objects.filter_by_user(user).filter(home=home)

        task_kwargs = self.get_machinery_kwargs()
        task_kwargs["context"]["home_id"] = home.pk
        # content_type for TaskType machinery
        task_kwargs["context"]["content_type"] = "Home"

        machineries.update(
            {
                "task_types": TaskTypeMachinery(objects=task_types, **task_kwargs),
                "home_task": TaskHomeMachinery(objects=tasks, **task_kwargs),
            }
        )

        kwargs.pop("create_new")

        # qa statuses
        qa_statuses = []
        if not self.create_new:
            if user.company.company_type == "eep":
                editable_qa_statuses = QAStatus.objects.filter(
                    home_status__eep_program__owner=user.company
                )
            else:
                editable_qa_statuses = QAStatus.objects.filter_by_user(user)
            editable_qa_statuses = list(editable_qa_statuses.filter(home_status__in=homestatuses))
            readonly_qa_statuses = list(
                QAStatus.objects.filter(
                    home_status__eep_program__owner=user.company,
                    home_status__in=homestatuses,
                ).exclude(id__in=[o.pk for o in editable_qa_statuses])
            )
            qa_statuses = editable_qa_statuses + readonly_qa_statuses
        # Import inline to avoid circular dependency
        from axis.qa.views.examine import QAStatusExamineMachinery

        machinery = QAStatusExamineMachinery(objects=qa_statuses, content_object=home, **kwargs)
        if (
            user.company.company_type == "eep"
            or user.is_sponsored_by_company(customer_hirl_app.CUSTOMER_SLUG, only_sponsor=True)
            or (user.is_customer_hirl_company_member() and not user.is_company_admin)
        ):
            machinery.can_add_new = False

        machineries[machinery.type_name_slug] = machinery

        # Analysis
        from axis.customer_eto.views.examine import ETOAnalyticsRollupMachinery

        analytics = []
        if not self.create_new and homestatuses.exists():
            content_type = ContentType.objects.get_for_model(homestatuses.first())
            homestatus_ids = homestatuses.values_list("pk", flat=True)
            analytics = AnalyticRollup.objects.filter(
                content_type=content_type, object_id__in=homestatus_ids
            )
        machinery = ETOAnalyticsRollupMachinery(objects=analytics, **kwargs)
        machineries[machinery.type_name_slug] = machinery

        return machineries

    def get_object_name(self):
        """Returns name of the object"""
        return self.object.get_addr(company=self.request.company)

    # pylint: disable=too-many-locals
    def get_context_data(self, **kwargs):
        """Returns context data"""
        # pylint: disable=too-many-locals
        from axis.eep_program.models import EEPProgram as Program

        context = super(HomeExamineView, self).get_context_data(**kwargs)

        user = self.request.user

        old_aps_programs = []
        if self.object.pk:
            old_aps_programs = self.object.homestatuses.filter(
                eep_program__program_start_date__year__lte="2017",
            )

            for legacy_name in settings.HOME_EEP_PROGRAM_LEGACY_CHECKLIST_NAMES:
                old_aps_programs = old_aps_programs.filter(
                    Q(eep_program__owner__name__icontains=legacy_name)
                )

            old_aps_programs = old_aps_programs.values_list("eep_program__name", flat=True)

        if old_aps_programs:
            context["input_collection"] = False
        else:
            # Add input-collection checklist for current view
            has_collection_requests = False
            if self.object.pk:
                has_collection_requests = self.object.homestatuses.filter(
                    eep_program__collection_request__isnull=False
                ).exists()

            needs_collection_assets = (
                Program.objects.filter_active_for_home_status_creation_by_user(user).filter(
                    collection_request__isnull=False
                )
            )
            context["input_collection"] = has_collection_requests or needs_collection_assets

        # Examine, documents, tabs
        ipp_items = IncentivePaymentStatus.objects.filter_by_user(user).filter(
            home_status__in=self.homestatuses
        )

        subdivision = self.object.subdivision
        stats_available_for_qa = get_stats_available_for_qa(user, self.object)
        company_hints = self.object.relationships.all().get_orgs(ids_only=True)
        qa_requirements = QARequirement.objects.filter_by_user(user, company_hints=company_hints)
        if user.company.company_type == "eep":
            qa_objects = QAStatus.objects.filter(home_status__eep_program__owner=user.company)
        else:
            qa_objects = QAStatus.objects.filter_by_user(user)
        qa_objects = qa_objects.filter(home_status__in=self.homestatuses)
        owns_programs_in_qa = QAStatus.objects.filter(
            home_status__eep_program__owner=user.company,
            home_status__in=self.homestatuses,
        )
        has_mf_qa = subdivision and subdivision.is_multi_family and subdivision.qastatus_set.count()

        show_qa = any(
            [
                stats_available_for_qa.count(),
                qa_requirements.count(),
                qa_objects.count(),
                owns_programs_in_qa,
                has_mf_qa,
            ]
        )

        answers_with_documents = (
            self.object.get_answers()
            .filter(customer_documents__id__isnull=False)
            .values_list("customer_documents__id", flat=True)
        )
        qaanswers_with_documents = (
            QAAnswer.objects.filter_by_home(self.object, allow_sampling=False)
            .filter(customer_documents__id__isnull=False)
            .values_list("customer_documents__id", flat=True)
        )
        qanotes_with_documents = (
            QANote.objects.filter(qa_status__in=self.object.get_qa_statuses())
            .filter(customer_documents__id__isnull=False)
            .values_list("customer_documents__id", flat=True)
        )
        document_count = sum(
            [
                answers_with_documents.count(),
                qaanswers_with_documents.count(),
                qanotes_with_documents.count(),
            ]
        )

        eep_program_ids = []
        if self.object.pk:
            eep_program_ids = list(
                map(
                    int,
                    list(
                        self.object.eep_programs.filter_by_user(
                            user, ignore_dates=True
                        ).values_list("id", flat=True)
                    ),
                )
            )

        # If the user company doesn't have a relationship to justify their access, fall back to
        # finding a candidate Association to allow 'contributer' editing permission.
        if self.object.relationships.filter(company=self.request.company).exists():
            is_contributor = True
        else:
            is_contributor = _get_home_contributor_flag(self.object, user)

        association_owners = None
        association_model_class = EEPProgramHomeStatus.associations.rel.related_model
        associations = association_model_class.objects.filter(
            eepprogramhomestatus__home=self.object
        )
        associations = associations.filter_for_user(user, is_active=True)
        if associations:
            association_owners = [i.owner for i in associations]

        show_analytics = False
        if self.object.pk:
            from analytics.models import Metric

            programs = Program.objects.filter(id__in=eep_program_ids)
            show_analytics = Metric.objects.filter(programs__in=programs).count()

        customer_hirl_app = apps.get_app_config("customer_hirl")

        context.update(
            {
                "is_contributor": is_contributor,
                "association_owners": association_owners,
                # invoicing
                "show_invoicing_tab": self.object.pk
                and self.request.user.is_superuser
                or self.request.user.is_customer_hirl_company_member()
                or self.request.user.is_sponsored_by_companies(
                    [
                        customer_hirl_app.CUSTOMER_SLUG,
                    ]
                ),
                # Incentives tab
                "ipp_objects": ipp_items,
                # QA tab
                "show_qa": show_qa,
                "has_mf_qa": has_mf_qa,
                "extra_document_count": document_count,
                "eep_program_ids": eep_program_ids,
                "show_analytics": show_analytics,
            }
        )

        RecentlyViewed.objects.view(instance=self.object, by=self.request.user)

        return context
