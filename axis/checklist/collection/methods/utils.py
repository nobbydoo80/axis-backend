"""Collection method utilities"""
import _csv
import csv
import logging
from functools import lru_cache


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def _preprocess_attrs(obj, attrs=None):
    """
    Calls processing methods on compliant PreProcessingMethod ``obj`` with ``**attrs`` for
    arguments.  ``attrs`` may be sent to this function as either a dict of attributes to values for
    direct preprocessing via ``obj`` methods, or else a list of attribute names for which values
    should be extracted from ``obj`` and then preprocessed.  If ``attrs`` isn't given, the
    ``obj.preprocess_attrs`` names list will be used instead.
    """
    if attrs is None:
        # Use the object's nominated list
        attrs = obj.preprocess_attrs

    # Convert a list of names to a dict of names and values
    if not isinstance(attrs, dict):
        attrs = {attr: getattr(obj, attr) for attr in attrs}

    preprocessed_attrs = {}
    for attr in list(attrs.keys()):
        raw_value = attrs[attr]
        preprocessed_attrs[attr] = raw_value
        if raw_value is not None:
            f = getattr(obj, "preprocess_{attr}".format(attr=attr))
            new_attrs = f(**preprocessed_attrs)
            preprocessed_attrs.update(new_attrs)
    return preprocessed_attrs


class PreProcessingMethodType(type):
    """Calls 'preprocess_FOO' for every FOO in the ``preprocess_attrs`` list."""

    blacklist = (
        "PreProcessingMethodType",
        "PreProcessingMethod",
        "BaseCascadingSelectMethod",
    )

    def __new__(cls, name, bases, attrs):
        DeclaredClass = super(PreProcessingMethodType, cls).__new__(cls, name, bases, attrs)
        if name not in cls.blacklist:
            preprocessed_attrs = _preprocess_attrs(DeclaredClass())
            for k, v in preprocessed_attrs.items():
                setattr(DeclaredClass, k, v)
        return DeclaredClass


class PreProcessingMethod(metaclass=PreProcessingMethodType):
    preprocess_attrs = ()

    def __init__(self, *args, **kwargs):
        super(PreProcessingMethod, self).__init__(*args, **kwargs)

        # Preprocess supported items in this instantiation
        attrs = [attr for attr in kwargs.keys() if attr in self.preprocess_attrs]
        self.preprocess(attrs)

    def preprocess(self, *args, **kwargs):
        """
        Iterates kwargs and calls ``self.preprocess_FOO(VALUE)`` for each key and value.
        """
        preprocessed_attrs = _preprocess_attrs(self, *args, **kwargs)
        for k, v in preprocessed_attrs.items():
            setattr(self, k, v)

    def serialize(self, *args, **kwargs):
        info = super(PreProcessingMethod, self).serialize(*args, **kwargs)
        del info["preprocess_attrs"]
        return info


def open_csv(data: str) -> _csv.reader:
    dialect = csv.Sniffer().sniff(data[:1024])
    return csv.reader(data.splitlines(), dialect=dialect)


@lru_cache
def get_csv_rows(data: str) -> list:
    return list(open_csv(data))
