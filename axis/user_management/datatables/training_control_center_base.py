"""training_control_center_base.py: """


from datatableview import datatables, columns, helpers

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingControlCenterBaseDatatable(datatables.Datatable):
    select_data = columns.CheckBoxSelectColumn()
    name = columns.TextColumn(source="name")
    company = columns.TextColumn(
        label="Company",
        source="trainee__company__name",
        processor=helpers.link_to_model(key=helpers.attrgetter("trainee.company")),
    )
    address = columns.TextColumn(source="address")
    training_date = columns.DateColumn(label="Training Date", source="training_date")
    training_type = columns.TextColumn(
        source="training_type", processor="get_training_type_display"
    )
    attendance_type = columns.TextColumn(
        source="attendance_type", processor="get_attendance_type_display"
    )
    credit_hours = columns.FloatColumn(source="credit_hours")
    trainee = columns.TextColumn(
        label="Name",
        sources=["trainee__first_name", "trainee__last_name"],
        processor=helpers.link_to_model(key=helpers.attrgetter("trainee")),
    )
    approval_status_notes = columns.TextColumn(
        label="Approval Notes", processor="get_approval_status_notes"
    )
    applicable_companies = columns.DisplayColumn(
        label="Applicable Companies", processor="get_applicable_companies_data"
    )

    class Meta:
        columns = [
            "select_data",
            "trainee",
            "company",
            "name",
            "address",
            "training_type",
            "training_date",
            "attendance_type",
            "credit_hours",
            "approval_status_notes",
            "applicable_companies",
        ]

    def get_attendance_type_display(self, obj, **kwargs):
        return obj.get_attendance_type_display()

    def get_training_type_display(self, obj, **kwargs):
        return obj.get_training_type_display()

    def get_applicable_companies_data(self, obj, **kwargs):
        applicable_companies = obj.trainingstatus_set.filter(
            state=kwargs["view"].training_state
        ).values_list("company__name", flat=True)
        return ", ".join(applicable_companies)

    def get_approval_status_notes(self, obj, **kwargs):
        approval_status_notes = ""
        for training_status in obj.trainingstatus_set.filter(state=kwargs["view"].training_state):
            if training_status.state_notes:
                approval_status_notes += "<i>{}:</i><br>".format(training_status.approver)
                approval_status_notes += "{}<br>".format(training_status.state_notes)
        return approval_status_notes
