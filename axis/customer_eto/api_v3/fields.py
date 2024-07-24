"""fields.py - Axis"""

__author__ = "Steven K"
__date__ = "9/29/21 10:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from rest_framework import serializers

log = logging.getLogger(__name__)


class CappedIntegerField(serializers.IntegerField):
    """This will strongly coerce an integer value"""

    def __init__(
        self,
        minimum_acceptable_value: int | None = None,
        maximum_acceptable_value: int | None = None,
        **kwargs,
    ):
        # Note this is NOT the same as min_value / max_value this will set the value.
        self.minimum_acceptable_value = minimum_acceptable_value
        self.maximum_acceptable_value = maximum_acceptable_value
        super(CappedIntegerField, self).__init__(**kwargs)

    def _apply_min_max_caps(self, value):
        if self.minimum_acceptable_value is not None:
            value = max([self.minimum_acceptable_value, value])
        if self.maximum_acceptable_value is not None:
            value = min([self.maximum_acceptable_value, value])
        return value

    def to_internal_value(self, data: str | float | int) -> int:
        if "." in str(data):
            data = int(round(float(data)))
        data = super(CappedIntegerField, self).to_internal_value(data)
        return self._apply_min_max_caps(data)

    def to_representation(self, data: int | float) -> int:
        if "." in str(data):
            data = int(round(float(data)))
        value = super(CappedIntegerField, self).to_representation(data)
        return self._apply_min_max_caps(value)


class CappedIntegerCommaField(CappedIntegerField):
    """This will force an integer value"""

    def __init__(self, prefix: str = "", suffix: str = "", **kwargs):
        self.prefix = prefix
        self.suffix = suffix
        super(CappedIntegerCommaField, self).__init__(**kwargs)

    def to_internal_value(self, value: str | int | float) -> int:
        if self.prefix and str(value).startswith(self.prefix):
            value = str(value).replace(self.prefix, "")
        if self.suffix and str(value).endswith(self.suffix):
            value = str(value).replace(self.suffix, "")
        if "," in str(value):
            value = value.replace(",", "")
        return super().to_internal_value(value)

    def to_representation(self, data: int | float) -> str:
        value = super(CappedIntegerCommaField, self).to_representation(data)
        return f"{self.prefix}{value:,}{self.suffix}"


class CappedFloatField(serializers.FloatField):
    """This will coerce a float value"""

    def __init__(
        self,
        minimum_acceptable_value: float | int | None = None,
        maximum_acceptable_value: float | int | None = None,
        round_value: int | None = None,
        **kwargs,
    ):
        self.minimum_acceptable_value = minimum_acceptable_value
        if isinstance(self.minimum_acceptable_value, int):
            self.minimum_acceptable_value = float(self.minimum_acceptable_value)
        self.maximum_acceptable_value = maximum_acceptable_value
        if isinstance(self.maximum_acceptable_value, int):
            self.maximum_acceptable_value = float(self.maximum_acceptable_value)
        self.round_value = round_value
        super(CappedFloatField, self).__init__(**kwargs)

    def _apply_min_max_caps(self, value):
        if self.minimum_acceptable_value is not None:
            value = max([self.minimum_acceptable_value, value])
        if self.maximum_acceptable_value is not None:
            value = min([self.maximum_acceptable_value, value])
        return value

    def to_internal_value(self, data):
        value = super(CappedFloatField, self).to_internal_value(data)
        return self._apply_min_max_caps(value)

    def to_representation(self, data: float) -> float:
        value = self._apply_min_max_caps(super(CappedFloatField, self).to_representation(data))
        if self.round_value:
            return round(value, self.round_value)
        return value


class CappedCommaFloatField(CappedFloatField):
    """This will transform it to a comma value"""

    def __init__(
        self,
        prefix: str = "",
        suffix: str = "",
        round_value: int | None = None,
        represent_percent: bool = False,
        represent_negatives_as_paren: bool = False,
        **kwargs,
    ):
        self.prefix = prefix
        self.suffix = suffix
        self.represent_percent = represent_percent
        self.represent_negatives_as_paren = represent_negatives_as_paren
        super(CappedCommaFloatField, self).__init__(**kwargs)
        self.round_value = round_value

    def to_internal_value(self, value):
        if self.prefix and str(value).startswith(self.prefix):
            value = str(value).replace(self.prefix, "")
        if self.suffix and str(value).endswith(self.suffix):
            value = str(value).replace(self.suffix, "")
        if self.represent_percent and str(value).endswith("%"):
            value = str(value).replace("%", "")
        if "(" in str(value) and ")" in str(value) and self.represent_negatives_as_paren:
            value = value.replace("(", "-").replace(")", "")
        if "," in str(value):
            value = value.replace(",", "")
        value = super().to_internal_value(value)
        if self.represent_percent:
            value /= 100.0
        return value

    def to_representation(self, data):
        value = super(CappedCommaFloatField, self).to_internal_value(data)
        if self.round_value is not None:
            designator = "f" if not self.represent_percent else "%"
            if value < 0 and self.represent_negatives_as_paren:
                return f"{self.prefix}({-value:,.{self.round_value}{designator}}){self.suffix}"
            return f"{self.prefix}{value:,.{self.round_value}{designator}}{self.suffix}"

        designator = "" if not self.represent_percent else "%"
        if value < 0 and self.represent_negatives_as_paren:
            return f"{self.prefix}({-value:,{designator}}){self.suffix}"
        return f"{self.prefix}{value:,{designator}}{self.suffix}"
