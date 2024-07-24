"""accreditation_control_center_base.py: """

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from datatableview import datatables, columns, helpers


class AccreditationControlCenterListDatatable(datatables.Datatable):
    """Control center datatable display class"""

    select_data = columns.CheckBoxSelectColumn()
    name = columns.TextColumn(label="Name", sources="name", processor="get_name_display")
    company = columns.TextColumn(
        label="Company",
        source="trainee__company__name",
        processor="get_company_display",
    )
    accreditation_id = columns.TextColumn(label="ID", source="accreditation_id")
    role = columns.TextColumn(source="role", processor="get_role_display")
    state = columns.TextColumn(label="Status", source="state", processor="get_state_display")
    accreditation_cycle = columns.TextColumn(
        label="Cycle", source="accreditation_cycle", processor="get_accreditation_cycle_display"
    )
    date_initial = columns.DateColumn(source="date_initial")
    date_last = columns.DateColumn(source="date_last")
    expiration_date = columns.DateColumn(source="get_expiration_date")
    trainee = columns.TextColumn(
        label="Name",
        sources=["trainee__first_name", "trainee__last_name"],
        processor=helpers.link_to_model(key=helpers.attrgetter("trainee")),
    )

    class Meta:
        columns = [
            "select_data",
            "trainee",
            "company",
            "name",
            "accreditation_id",
            "role",
            "state",
            "accreditation_cycle",
            "date_initial",
            "date_last",
            "expiration_date",
        ]

    def get_accreditation_cycle_display(self, obj, **kwargs):
        return obj.get_accreditation_cycle_display()

    def get_name_display(self, obj, **kwargs):
        return obj.get_name_display()

    def get_role_display(self, obj, **kwargs):
        return obj.get_role_display()

    def get_state_display(self, obj, **kwargs):
        return obj.get_state_display()

    def get_company_display(self, obj, **kwargs):
        if obj.trainee.company:
            company = obj.trainee.company
            return """<a href="{0}">{1}</a>""".format(company.get_absolute_url(), company.name)
        return ""
