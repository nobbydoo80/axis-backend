import logging

from django.db.models.query import QuerySet, Q

from axis.core.managers.mixins import OwnedObjectMixin, AssociationObjectMixin

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class unset:
    pass


class WorkflowQuerySet(OwnedObjectMixin, QuerySet):
    owner_field = "eepprogram__owner"


class CertifiableObjectQuerySet(OwnedObjectMixin, QuerySet):
    owner_field = "owner"


class WorkflowStatusQuerySet(OwnedObjectMixin, AssociationObjectMixin, QuerySet):
    owner_field = "owner"

    def _get_filter_data_query(self, field_name, value=unset):
        # This is built on querying the json blob in the database column as a text field.  We can't
        # query into the structure but it is easy enough to detect that the key is present and is
        # not None.

        lookup_tail = ""
        if value is unset:
            # Test for presence of key only
            lookup_tail = "__isnull"
            value = False

        lookup = "data__{field_name}{tail}".format(field_name=field_name, tail=lookup_tail)
        return Q(**{lookup: value})

    def filter_data(self, field_name, value=unset):
        return self.filter(self._get_filter_data_query(field_name, value))

    def exclude_data(self, field_name, value=unset):
        return self.exclude(self._get_filter_data_query(field_name, value))

    def has_data(self, *field_names):
        return self.filter(*[self._get_filter_data_query(field_name) for field_name in field_names])

    def has_no_data(self, *field_names):
        return self.exclude(
            *[self._get_filter_data_query(field_name) for field_name in field_names]
        )
