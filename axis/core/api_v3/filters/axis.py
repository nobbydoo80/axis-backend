"""AxisSearchFilter.py: """

from django.utils.encoding import force_str
from django_filters import filters, compat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import SearchFilter, OrderingFilter

__author__ = "Artem Hruzd"
__date__ = "03/03/2020 11:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AxisSearchFilter(SearchFilter):
    """
    Documentation enhancement to display search_fields.
    Issue: https://github.com/axnsan12/drf-yasg/issues/522
    """

    def get_schema_fields(self, view):
        search_fields = super(AxisSearchFilter, self).get_search_fields(view, view.request) or []
        fields = super(AxisSearchFilter, self).get_schema_fields(view)
        # add code formatting to strings for better display in Swagger
        formatted_search_fields = ["`{}`".format(search_field) for search_field in search_fields]
        new_field = coreapi.Field(
            name=fields[0].name,
            required=fields[0].required,
            location=fields[0].location,
            schema=coreschema.String(
                title=force_str(self.search_title),
                description="Search within these fields: {}".format(
                    ", ".join(formatted_search_fields)
                ),
            ),
        )
        return [
            new_field,
        ]


class AxisOrderingFilter(OrderingFilter):
    """
    Documentation enhancement to display ordering_fields.
    Issue: https://github.com/axnsan12/drf-yasg/issues/522
    """

    def get_schema_fields(self, view):
        fields = super(AxisOrderingFilter, self).get_schema_fields(view)
        ordering_fields = getattr(view, "ordering_fields", [])
        # add code formatting to strings for better display in Swagger
        formatted_ordering_fields = [
            "`{}`".format(ordering_field) for ordering_field in ordering_fields
        ]
        new_field = coreapi.Field(
            name=fields[0].name,
            required=fields[0].required,
            location=fields[0].location,
            schema=coreschema.String(
                title=force_str(self.ordering_title),
                description="Fields to use when ordering the results: {}".format(
                    ", ".join(formatted_ordering_fields)
                ),
            ),
        )
        return [
            new_field,
        ]


class AxisFilterBackend(DjangoFilterBackend):
    def get_coreschema_field(self, field):
        if issubclass(type(field), (filters.NumberFilter,)):
            field_cls = compat.coreschema.Number
        elif issubclass(type(field), (filters.ModelChoiceFilter,)):
            field_cls = compat.coreschema.String
        elif issubclass(
            type(field),
            (
                filters.DateRangeFilter,
                filters.ChoiceFilter,
            ),
        ):
            field_choices = field.extra.get("choices", [])
            formatted_field_choices = [
                "`{}` - {}".format(field_choice[0], field_choice[1])
                for field_choice in field_choices
            ]
            return compat.coreschema.Enum(
                enum=[choice[0] for choice in field_choices],
                description=("{}".format("\n".join(formatted_field_choices))),
            )
        elif issubclass(type(field), (filters.BooleanFilter,)):
            field_cls = compat.coreschema.Boolean
        else:
            field_cls = compat.coreschema.String
        return field_cls(description=field.extra.get("help_text", ""))
