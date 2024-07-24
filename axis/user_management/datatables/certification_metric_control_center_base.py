"""certification_metric_control_center_base.py: """

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.urls import reverse
from django.apps import apps
from datatableview import datatables, columns, helpers


customer_hirl_app = apps.get_app_config("customer_hirl")


class CertificationMetricControlCenterListDatatable(datatables.Datatable):
    select_data = columns.CheckBoxSelectColumn()
    name = columns.TextColumn(
        label="Role",
        sources=[
            "rater_of_record__first_name",
            "rater_of_record__last_name",
            "energy_modeler__first_name",
            "energy_modeler__last_name",
            "field_inspectors__first_name",
            "field_inspectors__last_name",
            "customer_hirl_rough_verifier__first_name",
            "customer_hirl_rough_verifier__last_name",
            "customer_hirl_final_verifier__first_name",
            "customer_hirl_final_verifier__last_name",
        ],
        processor="get_name_display",
    )
    company = columns.TextColumn(
        label="Company",
        sources=[
            "rater_of_record__company__name",
        ],
        processor="get_company_display",
    )
    program = columns.TextColumn(
        label="Program",
        sources=[
            "eep_program__name",
        ],
        processor=helpers.link_to_model(key=helpers.attrgetter("eep_program")),
    )
    address = columns.TextColumn(
        label="Address",
        sources=[
            "home__address",
        ],
        processor=helpers.link_to_model(key=helpers.attrgetter("home")),
    )
    certification_date = columns.DateColumn(source="certification_date")

    class Meta:
        columns = ["select_data", "name", "company", "address", "program", "certification_date"]

    def _display_user_link(self, user, role):
        return '<a href="{}" target="_blank">{}({})</a>'.format(
            reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name(), role
        )

    def get_name_display(self, obj, **kwargs):
        names = []
        if obj.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
            if getattr(obj, "customer_hirl_rough_verifier", None):
                names.append(
                    self._display_user_link(
                        user=obj.customer_hirl_rough_verifier, role="Rough Verifier"
                    )
                )
            if getattr(obj, "customer_hirl_final_verifier", None):
                names.append(
                    self._display_user_link(
                        user=obj.customer_hirl_final_verifier, role="Final Verifier"
                    )
                )
        else:
            if obj.rater_of_record:
                names.append(
                    self._display_user_link(user=obj.rater_of_record, role="Rater of Record")
                )
            if obj.energy_modeler:
                names.append(
                    self._display_user_link(user=obj.energy_modeler, role="Energy Modeler")
                )
            names += [
                self._display_user_link(user=user, role="Field Inspector")
                for user in obj.field_inspectors.all()
            ]
        return ", ".join(names)

    def _display_company_link(self, company):
        return '<a href="{}" target="_blank">{}</a>'.format(
            company.get_absolute_url(), company.name
        )

    def get_company_display(self, obj, **kwargs):
        if obj.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
            if getattr(obj, "customer_hirl_rough_verifier", None):
                if getattr(obj.customer_hirl_rough_verifier, "company", None):
                    return self._display_company_link(obj.customer_hirl_rough_verifier.company)
            if getattr(obj, "customer_hirl_final_verifier", None):
                if getattr(obj.customer_hirl_final_verifier, "company", None):
                    return self._display_company_link(obj.customer_hirl_final_verifier.company)
        elif getattr(obj, "rater_of_record", None):
            if getattr(obj.rater_of_record, "company", None):
                return self._display_company_link(obj.rater_of_record.company)
        return ""
