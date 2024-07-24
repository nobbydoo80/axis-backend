"""forms.py: Django customer_neea"""


import logging

from django import forms

from localflavor.us.us_states import US_STATES

import axis
from axis.company.models import Company
from axis.company.strings import COMPANY_TYPES
from axis.customer_neea.models import LegacyNEEAPartner, LegacyNEEABOP
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.geographic.models import Metro
from axis.home.forms import HomeStatusReportForm
from axis.home.models import EEPProgramHomeStatus
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.qa.state_machine import QAStateMachine
from axis.subdivision.models import Subdivision

__author__ = "Steven Klass"
__date__ = "7/29/13 9:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


BLANK_CHOICE = ("", "---------")


class LegacyNEEAHomeStatusForm(forms.Form):
    partner = forms.ModelMultipleChoiceField(
        queryset=LegacyNEEAPartner.objects.none(), required=False
    )
    bop = forms.ModelMultipleChoiceField(
        queryset=LegacyNEEABOP.objects.none(), required=False, label="BOP"
    )
    us_state = forms.ChoiceField(choices=US_STATES, required=False, label="US State")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LegacyNEEAHomeStatusForm, self).__init__(*args, **kwargs)


# NEEA HSR Subclasses.
# NOTE: It is important that mixin providing form fields be a direct subclass of Form, or else we
# get stuck having the composed result not noticing the field meant to be inherited.
class NEEAReportsExtraFilters(HomeStatusReportForm):
    has_bpa_association = forms.ChoiceField(
        label="BPA Affiliation",
        choices=(
            BLANK_CHOICE,
            ("false", "No"),
            ("true", "Yes"),
        ),
        required=False,
    )


class HomeStatusUtilityRawReportForm(NEEAReportsExtraFilters):
    def clean_task_name(self):
        """This is the task name"""
        from .tasks import export_home_data_raw_task

        return export_home_data_raw_task


class HomeStatusUtilityCustomReportForm(NEEAReportsExtraFilters):
    def clean_task_name(self):
        """This is the task name"""
        from .tasks import export_home_data_custom_task

        return export_home_data_custom_task


class HomeStatusUtilityBPAReportForm(NEEAReportsExtraFilters):
    def clean_task_name(self):
        """This is the task name"""
        from .tasks import export_home_data_bpa_task

        return export_home_data_bpa_task
