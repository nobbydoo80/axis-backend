"""forms.py: Django core"""


import logging

from django import forms

__author__ = "Steven Klass"
__date__ = "9/20/11 3:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)


class FilterSelect(forms.Select):
    """Standard filter select widget."""

    show_label = True
    template_name = "widgets/filter/select.html"


class FilterCheckbox(forms.CheckboxInput):
    """Standard filter checkbox widget."""

    show_label = False
    label = None
    template_name = "widgets/filter/checkbox.html"

    def __init__(self, label, *args, **kwargs):
        self.label = label
        super(FilterCheckbox, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        """Add custom `label` attribute to context."""

        context = super(FilterCheckbox, self).get_context(name, value, attrs)
        context["widget"]["label"] = self.label
        return context


class BigSelectMultiple(forms.SelectMultiple):
    """
    Define for duallist widget on AXIS
    """

    pass
