"""forms.py: Django customer_appraisal_institute"""


import logging

from django import forms

from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "6/2/13 9:10 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GreenEnergyEfficientAddendumForm(forms.Form):
    """Home Label Form used for printing Green Energy Efficient Addendum."""

    homes = forms.MultipleChoiceField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(GreenEnergyEfficientAddendumForm, self).__init__(*args, **kwargs)

        # Generates a list of possible ID choices for the user.
        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        if user.company.company_type not in ["rater", "provider"]:
            queryset = queryset.filter(certification_date__isnull=False)
        id_list = list(queryset.values_list("id", flat=True))
        self.fields["homes"].choices = zip(id_list, id_list)
