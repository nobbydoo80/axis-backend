"""Builder Agreement and related state machine."""

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta", "Artem Hruzd"]

import logging

from datatableview import datatables, columns, helpers
from . import ui

log = logging.getLogger(__name__)


class FilterDatatable(datatables.Datatable):
    """Datatable that is filtered by the administrative filtering form."""

    company = columns.TextColumn(
        label="Company", source="company__name", processor=helpers.link_to_model
    )
    client_id = columns.TextColumn(
        label="Client ID", source="company__hirlcompanyclient__id", processor="get_ngbs_client_id"
    )
    coi_document_max_start_date = columns.TextColumn(
        label="Insurance Start Date", source="coi_document_max_start_date"
    )
    coi_document_max_expiration_date = columns.TextColumn(
        label="Insurance Expiration Date", source="coi_document_max_expiration_date"
    )
    insurance_status = columns.TextColumn(
        label="Insurance Status", source="active_coi_document_count", processor="get_coi_state"
    )

    class Meta:  # pylint: disable=old-style-class, missing-docstring
        columns = (
            "company",
            "client_id",
            "state",
            "agreement_start_date",
            "agreement_expiration_date",
            "insurance_status",
            "coi_document_max_start_date",
            "coi_document_max_expiration_date",
        )
        labels = dict(ui.MANAGEMENT_LABELS, state=ui.STATE_LABEL)
        processors = {
            "state": lambda obj, **kwargs: obj.get_state_display(),
        }

    def get_coi_state(self, obj, *args, **kwargs):
        if obj:
            if obj.coi_document_count == 0:
                return ""
            if obj.active_coi_document_count > 0:
                return "Active"
        return "Expired"

    def get_ngbs_client_id(self, obj, *args, **kwargs):
        hirl_company_client = getattr(obj.company, "hirlcompanyclient", None)
        if hirl_company_client:
            return f"<a href='{obj.company.get_absolute_url()}'>{hirl_company_client.id}</a>"
        return ""
