"""admin_utils.py: """

__author__ = "Artem Hruzd"
__date__ = "08/10/2020 18:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
    SimpleListFilter,
)


class DropdownFilter(AllValuesFieldListFilter):
    template = "admin/includes/dropdown_filter.html"


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = "admin/includes/dropdown_filter.html"


class RelatedDropdownFilter(RelatedFieldListFilter):
    """
    Usage example:
    list_filter = (('owner', RelatedDropdownFilter),)
    """

    template = "admin/includes/dropdown_filter.html"


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = "admin/includes/dropdown_filter.html"


class InputFilter(SimpleListFilter):
    """
    Usage example:
    class SizeLessFilter(InputFilter):
        parameter_name = 'size__lt'

    class WordsLessFilter(InputFilter):
        parameter_name = 'words__lt'
    """

    template = "admin/includes/input_filter.html"

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (k, v) for k, v in changelist.get_filters_params().items() if k != self.parameter_name
        )
        yield all_choice
