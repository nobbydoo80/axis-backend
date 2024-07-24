"""Appraisal Addendum customer extension."""


import os

from django.conf import settings

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10-10-2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class AppraisalAddendumConfig(customers.ExtensionConfig):
    FORM_FIELD_TEMPLATE = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "sources/eaaa_form_field_template.pdf")
    )

    def ready(self):
        super(AppraisalAddendumConfig, self).ready()
        assert os.path.exists(self.FORM_FIELD_TEMPLATE)
