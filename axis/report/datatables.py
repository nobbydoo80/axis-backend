"""views.py: Django """


import logging
from operator import attrgetter
from functools import partial

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db.models import Q

import datatableview.helpers
from datatableview import datatables

from axis.company.models import Company
from axis.relationship.models import Relationship
from axis.subdivision.models import Subdivision

__author__ = "Autumn Valenta"
__date__ = "5/19/17 9:24 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SubdivisionReportDatatable(datatables.Datatable):
    city = datatables.TextColumn("City", "city__name")
    builder = datatables.TextColumn("Builder", "builder_org__name")

    class Meta:
        columns = ["name", "city", "builder"]
        processors = {
            "name": datatableview.helpers.link_to_model,
            "builder": datatableview.helpers.link_to_model(key=attrgetter("builder_org")),
        }

    def __init__(self, *args, **kwargs):
        super(SubdivisionReportDatatable, self).__init__(*args, **kwargs)
        self.subdivision_ids = kwargs.pop("subdivision_ids", [])
        self._append_eepcompany_columns()

    def _append_eepcompany_columns(self):
        subdivision_ct = ContentType.objects.get_for_model(Subdivision)

        company_ids = set()
        user = self.view.request.user
        if not user.company.is_eep_sponsor:
            comps = Company.objects.filter_by_user(user).values_list("id", flat=True)
            rels = Relationship.objects.filter(
                Q(company__is_eep_sponsor=True) | Q(company__company_type="eep"),
                content_type=subdivision_ct,
                company_id__in=comps,
                object_id__in=self.subdivision_ids,
            )
            company_ids = rels.values_list("company_id", flat=True)
        else:
            company_ids.add(user.company.id)
        companies = Company.objects.filter(id__in=company_ids).order_by("name")

        # Add dynamic Company columns to the table
        for pk, name in companies.values_list("id", "name"):
            processor = partial(self.get_eep_data, eep_company_id=pk)
            column = datatables.DisplayColumn(name, processor=processor)
            self.columns["company_{}".format(pk)] = column

    def get_eep_data(self, obj, eep_company_id, **kwargs):
        href = '<a href="{}" class="btn btn-default">{}</a>'
        if obj.relationships.filter(company_id=eep_company_id).exists():
            url = reverse(
                "report:energy_cost",
                kwargs={"subdivision_id": obj.id, "company_id": eep_company_id},
            )
            return href.format(url, "Report")
        return "-"
