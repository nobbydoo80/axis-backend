import logging

from django import forms

from axis.home.models import EEPProgramHomeStatus

__author__ = "Michael Jeffrey"
__date__ = "8/9/17 3:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class HighPerformanceHomeAddendumForm(forms.Form):
    homes = forms.MultipleChoiceField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(HighPerformanceHomeAddendumForm, self).__init__(*args, **kwargs)

        # Generates a list of possible ID choices for the user.
        queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
        if user.company_type not in ["rater", "provider"]:
            queryset = queryset.filter(certification_date__isnull=False)
        id_list = list(queryset.values_list("id", flat=True))
        self.fields["home"].choices = zip(id_list, id_list)
