"""views.py: Django """


import logging

from datatableview import helpers

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import LegacyAxisDatatableView
from ..models import EEPProgram

__author__ = "Steven Klass"
__date__ = "1/20/12 8:05 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EEPProgramListView(AuthenticationMixin, LegacyAxisDatatableView):
    """Get the Programs for a Program Sponsor"""

    permission_required = "eep_program.view_eepprogram"
    datatable_options = {
        "columns": [
            ("Name", "name"),
            ("Sponsor", "owner__name"),
            ("Participate", None, "get_column_Participate_data"),
        ],
        "unsortable_columns": ["Participate"],
    }

    def get_datatable_options(self):
        datatable_options = self.datatable_options.copy()
        datatable_options["columns"] = datatable_options["columns"][:]
        if self.request.user.is_superuser:
            column_count = len(datatable_options["columns"])
            # Insert separately so we can keep Participating column on the right.
            datatable_options["columns"].insert(
                column_count - 1, ("Active", "is_active", helpers.make_boolean_checkmark)
            )
            datatable_options["columns"].insert(
                column_count - 1, ("Public", "is_public", helpers.make_boolean_checkmark)
            )
        return datatable_options

    def get_queryset(self):
        """Narrow this based on your company"""
        self.opted_in_programs = EEPProgram.objects.filter(
            opt_in=True, opt_in_out_list=self.request.company
        )
        self.opted_out_programs = EEPProgram.objects.filter(
            opt_in=False, opt_in_out_list=self.request.company
        )
        return EEPProgram.objects.filter_by_user(
            user=self.request.user, visible_for_use=True
        ).order_by("-id")

    def get_column_Name_data(self, instance, *args, **kwargs):
        return helpers.link_to_model(instance, text=instance.name)

    def get_column_Sponsor_data(self, instance, *args, **kwargs):
        return helpers.link_to_model(instance.owner, text=instance.owner.name)

    def get_columns_Min_Max_Hers_data(self, instance, *args, **kwargs):
        return "{}/{}".format(instance.min_hers_score, instance.max_hers_score)

    def get_column_Participate_data(self, instance, *args, **kwargs):
        template = """
        <input type='checkbox' data-program-id='{program_id}'
        data-company-id='{company_id}' {checked}/>
        """

        if instance.opt_in:
            checked = self.is_opted_in(instance)
        else:
            checked = self.is_not_opted_out(instance) or self.is_empty(instance)

        kwargs = {
            "program_id": instance.id,
            "company_id": self.request.company.id,
            "checked": "checked" if checked else "",
        }

        return template.format(**kwargs)

    def is_opted_in(self, instance):
        return instance in self.opted_in_programs

    def is_not_opted_out(self, instance):
        return instance not in self.opted_out_programs

    def is_empty(self, instance):
        return instance.opt_in is False and instance.opt_in_out_list.count() == 0
