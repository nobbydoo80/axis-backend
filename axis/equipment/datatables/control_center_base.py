"""control_center_base.py: """


from django.urls import reverse
from datatableview import datatables, columns, helpers

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentControlCenterBaseDatatable(datatables.Datatable):
    select_data = columns.CheckBoxSelectColumn()
    equipment_type = columns.TextColumn(
        source="equipment_type", processor="get_equipment_type_display"
    )
    calibration_date = columns.DateColumn(source="calibration_date")
    calibration_cycle = columns.TextColumn(
        source="calibration_cycle", processor="get_calibration_cycle_display"
    )
    calibration_company = columns.TextColumn(source="calibration_company")
    bms = columns.TextColumn(
        label="B/M/S", sources=["brand", "equipment_model", "serial"], processor="get_bms_data"
    )
    assignees = columns.TextColumn(
        label="Assignees",
        source=["assignees__first_name", "assignees__last_name"],
        processor="get_assignees_display",
    )
    owner_company = columns.TextColumn(
        label="Company",
        source="owner_company__name",
        processor=helpers.link_to_model(key=helpers.attrgetter("owner_company")),
    )
    approval_status_notes = columns.TextColumn(
        label="Approval Notes", processor="get_approval_status_notes"
    )
    applicable_companies = columns.TextColumn(
        label="Applicable companies", processor="get_applicable_companies_data"
    )

    class Meta:
        columns = [
            "select_data",
            "equipment_type",
            "calibration_date",
            "calibration_cycle",
            "calibration_company",
            "bms",
            "assignees",
            "owner_company",
            "approval_status_notes",
            "applicable_companies",
        ]

    def get_bms_data(self, obj, **kwargs):
        return "{}/{}/{}".format(obj.brand, obj.equipment_model, obj.serial)

    def get_equipment_type_display(self, obj, **kwargs):
        return obj.get_equipment_type_display()

    def get_calibration_cycle_display(self, obj, **kwargs):
        return obj.get_calibration_cycle_display()

    def get_assignees_display(self, obj, **kwargs):
        names = [
            '<a href="{}">{}</a>'.format(
                reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name()
            )
            for user in obj.assignees.all()
        ]
        return ", ".join(names)

    def get_applicable_companies_data(self, obj, **kwargs):
        applicable_companies = obj.equipmentsponsorstatus_set.filter(
            state=kwargs["view"].equipment_state
        ).values_list("company__name", flat=True)
        return ", ".join(applicable_companies)

    def get_approval_status_notes(self, obj, **kwargs):
        approval_status_notes = ""
        for equipment_status in obj.equipmentsponsorstatus_set.filter(
            state=kwargs["view"].equipment_state
        ):
            if equipment_status.state_notes:
                approval_status_notes += "<i>{}:</i><br>".format(equipment_status.approver)
                approval_status_notes += "{}<br>".format(equipment_status.state_notes)
        return approval_status_notes
