"""Builder Agreement and related state machine."""


import logging

from datatableview import datatables, columns, helpers

from . import MANAGEMENT_LABELS, STATE_LABEL

__author__ = "Artem Hruzd"
__date__ = "2020-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Artem Hruzd"]

log = logging.getLogger(__name__)


class VerifierAgreementFilterDatatable(datatables.Datatable):
    """Datatable that is filtered by the administrative filtering form."""

    verifier = columns.TextColumn(
        label="Verifier Name",
        sources=["verifier__first_name", "verifier__last_name"],
        processor=helpers.link_to_model,
    )

    class Meta:  # pylint: disable=old-style-class, missing-docstring
        columns = (
            "verifier",
            "state",
            "agreement_start_date",
            "agreement_expiration_date",
        )
        labels = dict(MANAGEMENT_LABELS, state=STATE_LABEL)
        processors = {
            "state": lambda obj, **kwargs: obj.get_state_display(),
        }
