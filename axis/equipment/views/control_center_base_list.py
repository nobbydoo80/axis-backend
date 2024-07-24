"""control_center_base_list.py: """

from django.apps import apps
from django.db.models import Case, When, Count, IntegerField
from django.utils.functional import cached_property
from axis.core.mixins import AuthenticationMixin

from axis.company.models import Company
from axis.core.views.generic import AxisFilterView
from axis.equipment.filters import EquipmentFilter
from ..datatables import EquipmentControlCenterBaseDatatable
from ..forms import EquipmentControlCenterBaseFilterForm
from ..models import Equipment, EquipmentSponsorStatus
from ..states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

app = apps.get_app_config("equipment")


class EquipmentControlCenterBaseListView(AuthenticationMixin, AxisFilterView):
    datatable_class = EquipmentControlCenterBaseDatatable
    form_class = EquipmentControlCenterBaseFilterForm
    show_add_button = False
    template_name = "equipment/control_center_base_list.html"

    def has_permission(self):
        return (
            self.request.company.slug in app.EQUIPMENT_APPLICABLE_COMPANIES_SLUGS
            or self.request.user.is_superuser
        )

    @property
    def equipment_state(self):
        raise NotImplementedError

    @cached_property
    def equipment(self):
        equipment = Equipment.objects.filter(equipmentsponsorstatus__state=self.equipment_state)
        return equipment

    def get_queryset(self):
        return EquipmentFilter(
            data=self.request.GET, request=self.request, queryset=self.equipment
        ).qs

    def get_form_kwargs(self):
        kwargs = super(EquipmentControlCenterBaseListView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["companies"] = Company.objects.filter(
            pk__in=self.equipment.values_list("owner_company__pk", flat=True)
        ).distinct()
        return kwargs

    def get_datatable(self):
        datatable = super(EquipmentControlCenterBaseListView, self).get_datatable()

        if not self.request.user.is_superuser:
            del datatable.columns["applicable_companies"]

        return datatable

    def get_context_data(self, **kwargs):
        context = super(EquipmentControlCenterBaseListView, self).get_context_data(**kwargs)

        equipment = Equipment.objects.all()
        if not self.request.user.is_superuser:
            equipment = equipment.filter(equipmentsponsorstatus__company=self.request.user.company)

        statuses_count = equipment.aggregate(
            new_count=Count(
                Case(
                    When(
                        equipmentsponsorstatus__state=EquipmentSponsorStatusStates.NEW,
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            active_count=Count(
                Case(
                    When(
                        equipmentsponsorstatus__state=EquipmentSponsorStatusStates.ACTIVE,
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            rejected_count=Count(
                Case(
                    When(
                        equipmentsponsorstatus__state=EquipmentSponsorStatusStates.REJECTED,
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            expired_count=Count(
                Case(
                    When(
                        equipmentsponsorstatus__state=EquipmentSponsorStatusStates.EXPIRED,
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
        )

        context.update(statuses_count)

        context["total_count"] = sum(
            [
                statuses_count["new_count"],
                statuses_count["active_count"],
                statuses_count["rejected_count"],
                statuses_count["expired_count"],
            ]
        )

        context["equipment_sponsor_status_state_choices"] = EquipmentSponsorStatusStates.choices
        context["equipment_state"] = self.equipment_state
        if self.request.user.is_superuser:
            context["company_choices"] = (
                EquipmentSponsorStatus.objects.filter(state=self.equipment_state)
                .distinct()
                .values_list("company__pk", "company__name")
            )
        return context
