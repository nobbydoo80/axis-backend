"""Examine input methods"""
import csv
import logging
import re
from collections import OrderedDict

from django import forms
from django.core.exceptions import ValidationError
from django_input_collection.collection import methods

from . import utils

__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


# Mixins
class AxisMixin(object):
    allow_custom = None

    display_format = "{input}"
    display_format_short = None

    def __init__(self, *args, **kwargs):
        super(AxisMixin, self).__init__(*args, **kwargs)

        # Keep 'short' version populated
        if self.display_format_short is None:
            self.display_format_short = self.display_format


class RangeMixin(object):
    min_value = None
    max_value = None

    def get_constraints(self):
        attrs = ["min_value", "max_value"]
        return {attr: getattr(self, attr, None) for attr in attrs}

    def clean(self, result):
        result = super(RangeMixin, self).clean(result)

        if self.min_value and result < self.min_value:
            raise ValidationError("Must be at least %r" % (self.min_value,))
        elif self.max_value and result > self.max_value:
            raise ValidationError("Must be at most %r" % (self.max_value,))

        return result


# Concrete classes
class CharMethod(AxisMixin, methods.FormFieldMethod):
    formfield = forms.CharField


class DateMethod(AxisMixin, methods.FormFieldMethod):
    formfield = forms.DateField


class IntegerMethod(RangeMixin, AxisMixin, methods.FormFieldMethod):
    formfield = forms.IntegerField


class DecimalMethod(RangeMixin, AxisMixin, methods.FormFieldMethod):
    formfield = forms.DecimalField


# Cascading Select
class BaseCascadingSelectMethod(utils.PreProcessingMethod, AxisMixin, methods.FormFieldMethod):
    formfield = forms.CharField
    widget_template_name = "checklist/examine/angular/cascading_select.html"

    # Must be specified with instantiation kwarg or subclass
    labels = None
    source = None
    leaf_display_format = None

    # Automatic preprocessing
    preprocess_attrs = ("source", "labels")

    # Useful residue attributes set during preprocessing
    raw_source = None
    source_rows = None
    source_structured = None
    label_codes = None
    leaf_labels = None
    leaf_label_codes = None

    def get_data_display(self, data):
        """Takes a dict of codes mapped to values and serializes it to a string."""
        if not data:
            data = {}
        leaf_placeholder = "{%s}" % (self.label_codes[-1],)  # '{characteristics}'
        full_format = self.display_format.replace(leaf_placeholder, self.leaf_display_format)
        blanks = dict.fromkeys(re.findall(r"\{(\w+)\}", full_format), "")
        return full_format.format(**dict(blanks, **data))

    # Preprocessing
    def preprocess_labels(self, labels, source_rows, **kwargs):
        """Generate codes for labels that are safe for use as mapping keys."""
        # Note that this runs after preprocess_source(), so we'll use data generated from that here
        num_filters = len(labels) - 1
        leaf_labels = source_rows[0][num_filters:]
        return {
            "labels": labels,
            "label_codes": [self.make_label_code(label) for label in labels],
            "leaf_labels": leaf_labels,
            "leaf_label_codes": [self.make_label_code(label) for label in leaf_labels],
        }

    def preprocess_source(self, source, **kwargs):
        """Modify the declared csv data to the cascade format."""

        raw_source = source
        source_rows = utils.get_csv_rows(raw_source)
        source_structured = self.structure_source()

        return {
            "source": source,
            "raw_source": raw_source,
            "source_rows": source_rows,
            "source_structured": source_structured,
        }

    def structure_source(self):
        """
        Builds an OrderedDict from the CSV where each key maps to the next set of distinct options
        in the column to the right.  This continues for the officially labeled columns, and any
        remaining columns to the right are put into a combined dictionary and enumerated as a list,
        each combined dictionary representing a leaf option of those combined values.
        """

        # 'Characteristics' is a pseudo label of all remaining columns, so don't count it as a
        # hierarchical filter.
        num_filters = len(self.labels) - 1

        result = OrderedDict()
        rows = list(utils.open_csv(self.source))
        headers = rows.pop(0)
        if not num_filters:
            num_filters = len(headers)
        for row in sorted(rows):
            insert_dict = result  # Start at top level
            for i, column in enumerate(row[:num_filters]):
                is_last_column = i == num_filters - 1
                if column == "":
                    column = "N/A"
                if not is_last_column:
                    insert_dict.setdefault(column, OrderedDict())
                    insert_dict = insert_dict[column]
                else:
                    insert_dict.setdefault(column, [])

            # Combine all remaining column values for a single leaf entry
            if num_filters < len(row):
                # NOTE: Can't use self.leaf_label_codes yet because that was generated in this same
                # preprocessing step and hasn't been assigned to self yet.
                leaf_codes = list(map(self.make_label_code, headers[num_filters:]))
                leaf_data = dict(zip(leaf_codes, row[num_filters:]))
                if leaf_data not in insert_dict[column]:
                    insert_dict[column].append(leaf_data)
                    insert_dict[column].sort(key=lambda x: list(x.keys())[0], reverse=False)
        return result

    # Utils
    def get_display_format_patterns(self):
        # Legacy formats are required for successful parsing into raw data dict of codes.
        # For example: r'^Some Label=(?P<foo>.+?) Other Label=(?P<bar>.+?)$'
        return [
            self.get_display_format_pattern(),
        ]

    def get_display_format_pattern(
        self, display_format=None, full_match=None, head_match=None, tail_match=None
    ):
        """'{foo}; {bar}' -> '^(?P<foo>.+?); (?P<bar>.+?)$'"""

        num_options = len(
            list(filter(lambda o: o is not None, (full_match, head_match, tail_match)))
        )
        true_options = len(list(filter(bool, (full_match, head_match, tail_match))))
        if num_options == 0:
            full_match = True
        elif true_options > 1:
            raise ValueError("Only one option can be specified: full_match, head_match, tail_match")

        if full_match:
            head_match = True
            tail_match = True

        if display_format is None:
            display_format = self.display_format

        def _placeholder_to_capture_group(match):
            return "(?P<{code}>.*)".format(code=match.group("code"))

        display_format = display_format.replace("{characteristics}", self.leaf_display_format)

        # Weak escape. I'm avoiding re.escape() because it messes up '_{}' characters in the string
        # formatting placeholders.
        pattern = re.sub(r"([)(\]\[.])", r"\\\1", display_format)

        pattern = re.sub(r"\{(?P<code>[^}]+)\}", _placeholder_to_capture_group, pattern)
        if head_match:
            pattern = "^{}".format(pattern)
        if tail_match:
            pattern = "{}$".format(pattern)
        return pattern

    def parse_choice(self, choice):
        """Parses a flat choice string into a dictionary of label codes to data points."""
        pattern_list = self.get_display_format_patterns()
        for pattern in pattern_list:
            match = re.match(pattern, choice)
            if match:
                return match.groupdict()
        else:
            raise ValidationError(
                "Unknown cascading choice format %r.  Known patterns: %r"
                % (
                    choice,
                    pattern_list,
                )
            )

    def verify_choice(self, data):
        """Validates each component choice value in a data dict.  Returns results info dict."""

        filter_codes = self.label_codes[:-1]
        leaf_code = self.label_codes[-1]
        lookups = self.source_structured

        # Make sure both 'codes' and 'values' are mutable so we avoid destructive side effects
        codes = filter_codes + self.leaf_label_codes
        values = list(v for k, v in sorted(data.items(), key=lambda k_v: codes.index(k_v[0])))

        extra = {
            "hints": {},
            "notices": {},
        }
        has_custom = False
        while not isinstance(lookups, list):
            code = codes.pop(0)
            value = values.pop(0)

            # is_custom check
            if value not in lookups:
                has_custom = True
                extra["hints"].setdefault(code, {})["is_custom"] = True

            # Move to next set of choices
            if has_custom:
                if filter_codes[-1] == code:
                    lookups = []  # time to be done, move into leaf verification
                else:
                    lookups = {}  # keep going, determinine next item is_custom, too
            else:
                lookups = lookups[value]

        # Prove matching characteristics entry exists for remaining codes/values
        characteristics = dict(zip(codes, values))
        if characteristics not in lookups:
            extra["hints"].setdefault(leaf_code, {})["is_custom"] = True

        # Add simple flag without any field granularity
        if has_custom:
            extra["hints"]["is_custom"] = True

        # Purge keys with empty dicts
        for k, v in list(extra.items()):
            if not v:
                del extra[k]

        return extra

    def make_label_code(self, label):
        """'Filter Label (kw/yr)' → 'filter_label_kw_yr'"""
        return re.sub(r"[^a-z\d]+", "_", label.lower()).strip("_")

    def make_label(self, code):
        """'filter_label_kw_yr' → 'Filter Label (kw/yr)'"""
        if code in self.label_codes:
            lookups = dict(zip(self.label_codes, self.labels))
        elif code in self.leaf_label_codes:
            lookups = dict(zip(self.leaf_label_codes, self.leaf_labels))
        else:
            raise ValueError(
                "Unknown label code %r. Valid codes: %r"
                % (
                    code,
                    self.label_codes + self.leaf_label_codes,
                )
            )
        return lookups[code]

    # Action methods
    def serialize(self, *args, **kwargs):
        """Remove messy attributes in serialization."""
        info = super(BaseCascadingSelectMethod, self).serialize(*args, **kwargs)
        del info["source"]
        del info["raw_source"]
        del info["source_rows"]
        return info

    def clean(self, data):
        """Pass data through as constructed by the subclass for the backend JSONField to store."""

        extra = self.verify_choice(data)

        if extra.get("hints", {}).get("is_custom"):
            # Choice isn't built-in, so disallow explicit characteristics for data integrity.
            data.update(dict.fromkeys(self.leaf_label_codes, None))

        return data, extra
