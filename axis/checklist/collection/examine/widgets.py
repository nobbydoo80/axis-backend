"""Examine template widgets"""


import logging

from django import forms


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class BootstrapButtonStripWidget(forms.RadioSelect):
    template_name = "checklist/examine/angular/button_strip_choices.html"


class BootstrapTextBoxWidget(forms.TextInput):
    template_name = "checklist/examine/angular/textbox.html"


class BootstrapDateWidget(forms.DateInput):
    template_name = "checklist/examine/angular/date.html"
