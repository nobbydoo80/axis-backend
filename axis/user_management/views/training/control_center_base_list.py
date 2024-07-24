"""control_center_base_list.py: """

from django.apps import apps
from django.db.models import Case, When, Count, IntegerField
from django.utils.functional import cached_property

from axis.company.models import Company
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisFilterView
from axis.user_management.datatables import TrainingControlCenterBaseDatatable
from axis.user_management.filters import TrainingFilter
from axis.user_management.forms import TrainingControlCenterBaseFilterForm
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.states import TrainingStatusStates

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

user_management_app = apps.get_app_config("user_management")


class TrainingControlCenterBaseListView(AuthenticationMixin, AxisFilterView):
    datatable_class = TrainingControlCenterBaseDatatable
    form_class = TrainingControlCenterBaseFilterForm
    show_add_button = False
    template_name = "training/control_center_base_list.html"

    def has_permission(self):
        return (
            self.request.company.slug in user_management_app.TRAINING_APPLICABLE_COMPANIES_SLUGS
            or self.request.user.is_superuser
        )

    @property
    def training_state(self):
        raise NotImplementedError

    @cached_property
    def training(self):
        trainings = Training.objects.filter(trainingstatus__state=self.training_state)
        if not self.request.user.is_superuser:
            trainings = trainings.filter(
                trainingstatus__state=self.training_state,
                trainingstatus__company=self.request.user.company,
            )

        trainings = trainings.prefetch_related("statuses")
        return trainings

    def get_queryset(self):
        return TrainingFilter(
            data=self.request.GET, request=self.request, queryset=self.training
        ).qs

    def get_form_kwargs(self):
        kwargs = super(TrainingControlCenterBaseListView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        if self.request.user.is_superuser:
            kwargs["companies"] = Company.objects.filter(
                pk__in=self.training.values_list("trainee__company__pk", flat=True)
            ).distinct()
        return kwargs

    def get_datatable(self):
        datatable = super(TrainingControlCenterBaseListView, self).get_datatable()

        if not self.request.user.is_superuser:
            del datatable.columns["applicable_companies"]

        return datatable

    def get_context_data(self, **kwargs):
        context = super(TrainingControlCenterBaseListView, self).get_context_data(**kwargs)

        trainings = Training.objects.all()
        if not self.request.user.is_superuser:
            trainings = trainings.filter(trainingstatus__company=self.request.user.company)

        statuses_count = trainings.aggregate(
            new_count=Count(
                Case(
                    When(trainingstatus__state=TrainingStatusStates.NEW, then=1),
                    output_field=IntegerField(),
                )
            ),
            approved_count=Count(
                Case(
                    When(trainingstatus__state=TrainingStatusStates.APPROVED, then=1),
                    output_field=IntegerField(),
                )
            ),
            rejected_count=Count(
                Case(
                    When(trainingstatus__state=TrainingStatusStates.REJECTED, then=1),
                    output_field=IntegerField(),
                )
            ),
        )

        context.update(statuses_count)

        context["total_count"] = sum(
            [
                statuses_count["new_count"],
                statuses_count["approved_count"],
                statuses_count["rejected_count"],
            ]
        )

        context["training_status_state_choices"] = TrainingStatusStates.choices
        context["training_state"] = self.training_state
        if self.request.user.is_superuser:
            context["company_choices"] = (
                TrainingStatus.objects.filter(state=self.training_state)
                .distinct()
                .values_list("company__pk", "company__name")
            )
        return context
