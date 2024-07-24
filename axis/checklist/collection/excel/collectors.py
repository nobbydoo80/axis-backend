"""Excel xls-to-db collector"""

import logging

from django_input_collection.models import CollectionInstrument

from . import methods
from .. import methods as axis_methods
from ..collectors import ChecklistCollector

__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class ExcelChecklistCollector(ChecklistCollector):
    method_mixins = {
        axis_methods.BaseCascadingSelectMethod: {
            "prefix": "Excel",
            "mixin": methods.ExcelCascadingSelectMethodMixin,
        },
    }

    # Conversion of possible special method.data_type values to Excel type names
    type_validations = {
        "open": {
            "type": "textLength",
            "operator": "lessThan",
            "formula1": "256",
            "error": "Entry must be less than 255 characters.",
        },
        "float": {
            "type": "decimal",
        },
        "integer": {
            "type": "whole",
        },
    }

    extra_choices_map = {
        "cascading-select": {
            "equipment-furnace": ["Not listed", "Not installed"],
            "equipment-furnace-2": ["Not listed", "Not installed"],
            "equipment-heat-pump": ["Not applicable", "Not listed"],
            "equipment-heat-pump-2": ["Not applicable", "Not listed"],
            "equipment-water-heater": ["Not listed", "Not installed"],
            "equipment-ventilation-balanced": ["Not applicable", "Not listed"],
            "equipment-ventilation-exhaust": ["Not applicable", "Not listed"],
            "equipment-ventilation-hrv-erv": ["Not applicable", "Not listed"],
        }
    }

    # `get_xls_instruments()` will remove these measures if they
    XLS_SKIP_MEASURES = [
        "bpa_upload_docs",
    ]

    def get_xls_instruments(self):
        """Alias for active instruments plus any instrument with an answer-dependent condition."""
        if not hasattr(self, "_xls_instruments"):
            active_flags = [
                True,  # Anything that reports active anyway
                {"instrument": self.speculate_instrument_availability},
            ]

            # Allow "failing" rem-driven conditions when no simulation is even present.
            # This applies to program-tier CollectionRequests, and also homestatuses that have no
            # resolvable remrate simulation.
            rem_available = None
            simulation_available = None
            if self.is_bound:
                floorplan = self.collection_request.eepprogramhomestatus.floorplan
                rem_available = bool(floorplan and floorplan.remrate_target)
                simulation_available = bool(floorplan and floorplan.simulation)
            flags = {}
            if not simulation_available:
                flags["simulation"] = False
            # TODO REM REMOVAL
            if not rem_available:
                flags["rem"] = False
            if flags:
                active_flags.append(flags)

            self._xls_instruments = self.get_instruments(active=active_flags).exclude(
                measure_id__in=self.XLS_SKIP_MEASURES
            )

        return self._xls_instruments

    def get_xls_validation_info(self, instrument):
        info = self.type_validations.get(instrument.type_id)
        if info:
            return info.copy()
        return None

    def get_instrument_choices(self, instrument):
        """
        Returns ``instrument.get_choices()`` or the Method choices for 'cascading-select' types.
        """
        if instrument.type_id == "cascading-select":
            extra_choices = self.extra_choices_map[instrument.type_id].get(
                instrument.measure_id, []
            )
            try:
                return self.get_method(instrument).get_flat_choices() + extra_choices
            except AttributeError:
                raise AttributeError(f"Unable to get flat choices for Instrument {instrument!r}")
        return instrument.get_choices()

    def speculate_instrument_availability(self, instrument, flag=False):
        """
        Returns a boolean to indicate whether this instrument should be included in the queryset for
        ``get_xls_instruments()``.
        """
        # NOTE: This is being called in a controlled context, so only instruments that are already
        # failing their availability check are being sent to this method.

        for parent in instrument.get_parent_instruments():
            # Parent has data and it hasn't enabled this instrument, so skip it
            if self.is_bound and self.get_inputs(parent).exists():
                return False
        return True

    def is_input_allowed(self, instrument, user=None):
        is_legacy = not getattr(instrument, "collection_request", None)
        if is_legacy:
            return True
        return super(ExcelChecklistCollector, self).is_input_allowed(instrument, user=user)

    def store(self, measure, data, **kwargs):
        # Uses a measure code instead of an instrument to resolve late, because the cleaning step
        # doesn't get a chance to have the latest reference if it's a program template
        # FIXME: maybe wrong target program -> collection_request, instrument says it's None
        instrument = self.get_instrument(measure=measure)
        kwargs["instrument"] = instrument
        kwargs["collection_request"] = instrument.collection_request
        return super(ExcelChecklistCollector, self).store(data=data, **kwargs)


class BulkExcelChecklistCollector(ExcelChecklistCollector):
    # If ``split_choices`` is True, suggested responses will each get their own copy of the column
    # with the choice appended. In that scenario, the data is treated like a checkbox system of
    # selecting multiple choices by marking such a column for a data row.
    split_choices = False

    # Internals
    BLANK_VALUES = ("", None)
    MAX_TEXT_LENGTH = 255
    HEADER_SEPARATOR = " - "

    def __init__(self, collection_request, split_choices=False, **kwargs):
        super(BulkExcelChecklistCollector, self).__init__(collection_request, **kwargs)

        self.split_choices = split_choices

    def resolve_instrument(self, instrument_text, _raise=True):
        """
        Returns the instrument with the matching prefix text or a CollectionInstrument.DoesNotExist
        exception.
        """

        instrument_text = instrument_text.split(self.HEADER_SEPARATOR, 1)[0]

        if not hasattr(self, "_resolved_instruments"):
            self._resolved_instruments = {}

        if instrument_text in self._resolved_instruments:
            return self._resolved_instruments[instrument_text]

        error = None
        instruments = self.get_xls_instruments()
        for suffix in ["", " ", ". "]:
            try:
                instrument = instruments.get(text__istartswith=instrument_text + suffix)
            except Exception as e:
                error = e
            else:
                self._resolved_instruments[instrument_text] = instrument
                return instrument
        else:
            if _raise:
                msg = "Cannot resolve bulk instrument with leading text %r: %r"
                raise instruments.model.DoesNotExist(msg % (instrument_text, error))
        return None

    def make_payload(self, measure, data, **kwargs):
        payload = super(BulkExcelChecklistCollector, self).make_payload(measure, data, **kwargs)

        # Store a reference to the original data
        payload["data"]["raw"] = data["input"]

        # Re-interpret instrument as its underlying measure code.  The way this collector is used,
        # data must be formed and cleaned prior to the step where the homestatus and its
        # collectionrequest are created, during the late 'commit' mode of the file processing.
        if not self.is_bound:
            payload["measure"] = payload["instrument"].measure_id
            del payload["instrument"]
            del payload["collection_request"]  # set from wrong 'instrument' reference

        return payload

    def get_xls_instrument_headers(self):
        """
        Returns a list of instrument texts to be set as headers across the top of a bulk xls
        template.
        """

        headers = []

        for instrument in self.get_xls_instruments():
            headers.extend(self.make_headers(instrument))

        return headers

    def make_headers(self, instrument):
        """Returns a list of header texts required to represent the question and its answers."""
        headers = []

        choices = instrument.get_choices()

        if choices and self.split_choices:
            # Each SuggestedResponse spawns its own column that the data rows can mark or not.
            for data in choices:
                headers.append(self._make_header(instrument.text, data))
        else:
            headers.append(self._make_header(instrument.text))

        headers.append(self._make_header(instrument.text, "Comment"))

        return headers

    def _make_header(self, *segments):
        """
        Returns a text label for an instrument with various appended suffixes, where the
        instrument's base text label might be truncated to fit the total MAX_TEXT_LENGTH allowed for
        such a header.
        """

        if not segments:
            raise ValueError("Need at least one positional argument.")

        segments = list(segments)
        tail = self.HEADER_SEPARATOR.join(segments[1:])
        max_text_length = self.MAX_TEXT_LENGTH - len(tail)

        # Trunctate to fit
        segments[0] = segments[0][:max_text_length]

        return self.HEADER_SEPARATOR.join(segments)

    def get_type_display(self, instrument):
        code = instrument.type_id
        if code:
            if code == "cascading-select":
                return "Multiple Choice"  # Customers don't care about our distinction
            return " ".join(word.capitalize() for word in code.replace("-", " ").split())

    def create_payloads_for_row_inputs(self, row_result):
        """Translates a row of question text mapped to answers to a list of stageable payloads."""
        payloads = []

        for text, input in row_result.items():
            if input in self.BLANK_VALUES or text.endswith(" - comment"):
                continue

            try:
                instrument = self.resolve_instrument(text)
            except CollectionInstrument.DoesNotExist:
                # Non-question column or malformed
                continue

            # if self.split_choices:

            comment_header = self._make_header(text, "Comment")
            comment = row_result.get(comment_header.lower())

            payload = self.make_payload(instrument, {"input": input}, extra={"comment": comment})
            payloads.append(payload)

        return payloads
