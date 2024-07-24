"""views.py: Django community"""


import logging

import datatableview
from datatableview import datatables, helpers
from django.utils import formats
from django.utils.text import slugify
from app_metrics.models import Gauge


__author__ = "Hunter Hardwick"
__date__ = "7/7/17 10:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementListDatatable(datatables.Datatable):
    owner = datatables.TextColumn(
        "Owner", sources=["company__name"], processor=helpers.link_to_model
    )
    builder = datatables.TextColumn(
        "Builder", sources=["builder_org__name"], processor=helpers.link_to_model
    )
    subdivision = datatables.TextColumn(
        "Subdivision",
        sources=["subdivision__name", "subdivision__builder_name"],
        processor="get_column_Subdivision_data",
    )
    community = datatables.TextColumn(
        "Community",
        sources=["subdivision__community__name"],
        processor="get_column_Community_data",
    )
    lots_paid = datatables.TextColumn("Lots Paid", sources=["lots_paid"])
    start_date = datatables.DateColumn(
        "Start Date", sources=["start_date"], processor="get_column_Start_Date_data"
    )
    expire_date = datatables.DateColumn(
        "Expire Date", sources=["expire_date"], processor="get_column_Expire_Date_data"
    )

    class Meta:
        columns = [
            "owner",
            "builder",
            "subdivision",
            "community",
            "total_lots",
            "lots_paid",
            "start_date",
            "expire_date",
        ]
        ordering = ["owner", "builder"]

    def __init__(self, company, *args, **kwargs):
        super(BuilderAgreementListDatatable, self).__init__(*args, **kwargs)

        if company.company_type == "builder":
            self._meta.ordering = ["owner"]
            del self.columns["builder"]
        if company.is_eep_sponsor:
            self._meta.ordering = ["builder"]
            del self.columns["owner"]

    def get_column_Subdivision_data(self, instance, *args, **kwargs):
        subdivision = instance.subdivision

        if not subdivision:
            return "Custom"
        return helpers.link_to_model(subdivision)

    def get_column_Community_data(self, instance, *args, **kwargs):
        if instance.subdivision and instance.subdivision.community:
            return helpers.link_to_model(instance.subdivision.community)
        return ""

    def get_column_Start_Date_data(self, instance, *args, **kwargs):
        if instance.start_date:
            return formats.date_format(instance.start_date, "SHORT_DATE_FORMAT")
        return ""

    def get_column_Expire_Date_data(self, instance, *args, **kwargs):
        if instance.expire_date:
            return formats.date_format(instance.expire_date, "SHORT_DATE_FORMAT")
        return ""


class BuilderAgreementStatusListDatatable(datatables.Datatable):
    builder = datatables.TextColumn(
        "Builder", sources=["builder_org__name"], processor="get_column_Builder_data"
    )
    provider = datatables.TextColumn("Provider", sources=[""], processor="get_column_Provider_data")
    subdivision = datatables.TextColumn(
        "Subdivision",
        sources=["subdivision__name"],
        processor="get_column_Subdivision_data",
    )
    community = datatables.TextColumn(
        "Community",
        sources=["subdivision__community__name"],
        processor="get_column_Community_data",
    )
    signed_lots = datatables.TextColumn("Signed Lots", sources=["total_lots"])
    lots_paid = datatables.TextColumn("Lots Paid", sources=["lots_paid"])
    builder_amount_paid = datatables.TextColumn(
        "Builder Amount Paid",
        sources=[""],
        processor="get_column_Builder_Amount_Paid_data",
    )
    contract_signed_date = datatables.TextColumn("Contract Signed Date", sources=["start_date"])

    class Meta:
        columns = [
            "builder",
            "provider",
            "subdivision",
            "community",
            "signed_lots",
            "lots_paid",
            "builder_amount_paid",
            "contract_signed_date",
        ]
        ordering = ["builder"]

    def get_column_Subdivision_data(self, instance, *args, **kwargs):
        subdivision = instance.subdivision

        if not subdivision:
            return "Custom"
        return datatableview.helpers.link_to_model(subdivision)

    def get_column_Community_data(self, instance, *args, **kwargs):
        if instance.subdivision and instance.subdivision.community:
            return datatableview.helpers.link_to_model(instance.subdivision.community)
        return ""

    def get_column_Provider_data(self, instance, rater=None, *args, **kwargs):
        if not rater:
            if instance.subdivision:
                relationship_source = instance.subdivision
            else:
                relationship_source = instance.builder_org
            rater = relationship_source.relationships.get_provider_orgs().first()
        if not rater:
            return ""
        return datatableview.helpers.link_to_model(rater)

    def get_column_Builder_data(self, instance, *args, **kwargs):
        return datatableview.helpers.link_to_model(instance.builder_org)

    def get_column_Builder_Amount_Paid_data(self, instance, builder_paid=0, *args, **kwargs):
        slug = slugify("Builder Agreement {} builder Payment".format(instance.id))
        try:
            return "$ {:,.2f}".format(Gauge.objects.get(slug=slug).current_value)
        except Gauge.DoesNotExist:
            return "$ {:,}".format(0)

    def get_column_Contract_Signed_Date_data(self, instance, *args, **kwargs):
        if instance.start_date:
            return formats.date_format(instance.start_date, "SHORT_DATE_FORMAT")
        return ""
