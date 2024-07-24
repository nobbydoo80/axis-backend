"""Collection method objects and data"""


import logging

from django import forms

import dateutil

from .. import methods as axis_methods
from . import widgets


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class HorizontalStripSelectMethod(axis_methods.CharMethod):
    formfield = forms.CharField(widget=widgets.BootstrapButtonStripWidget)


class TextBoxMethod(axis_methods.CharMethod):
    formfield = forms.CharField(widget=widgets.BootstrapTextBoxWidget)


class NumberBoxMethod(axis_methods.IntegerMethod):
    formfield = forms.IntegerField(widget=widgets.BootstrapTextBoxWidget)


class DecimalBoxMethod(axis_methods.DecimalMethod):
    formfield = forms.DecimalField(widget=widgets.BootstrapTextBoxWidget)


class DateBoxMethod(axis_methods.DateMethod):
    formfield = forms.DateField(widget=widgets.BootstrapDateWidget)

    def clean(self, date_string):
        """Clean dateutil-parsed date_string, normalized to `yyyy-mm-dd`."""
        try:
            date_obj = dateutil.parser.parse(date_string)
        except ValueError:
            raise forms.ValidationError("Unrecognized date formate")
        date_string = date_obj.strftime("%Y-%m-%d")
        return super(DateBoxMethod, self).clean(date_string)


class ExamineCascadingSelectMethodMixin(object):
    allow_custom = True

    # Parsing 'choices' here means parsing just the characteristics portion for values.
    def get_display_format_patterns(self):
        """Returns abbreviated format used by the Characteristics part of the widget."""
        return [
            self.get_display_format_pattern(self.leaf_display_format),
        ]

    def clean(self, data):
        """Parses the value in data['characteristics'] into the usual dict parts."""
        characteristics = data.pop("characteristics")
        if characteristics:
            characteristics_data = self.parse_choice(characteristics)
            data.update(characteristics_data)

        return super(ExamineCascadingSelectMethodMixin, self).clean(data)
