"""views.py: Django core views"""


import logging

from django import forms

from .models import Message, MessagingPreference
from .utils import get_preferences_report

__author__ = "Steven Klass"
__date__ = "2011/08/04 15:21:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)


class MessagingPreferenceForm(forms.ModelForm):
    class Meta:
        model = MessagingPreference
        fields = ("receive_notification", "receive_email")


class MessagesFilterForm(forms.ModelForm):
    level = forms.ChoiceField(label="Type", required=False)
    category = forms.ChoiceField(required=False)
    delivery_type = forms.ChoiceField(label="Delivery type", required=False)
    date_created_start = forms.DateField(label="Issued After", required=False)
    date_created_end = forms.DateField(label="Issued Before", required=False)
    date_alerted_start = forms.DateField(label="Received After", required=False)
    date_alerted_end = forms.DateField(label="Received Before", required=False)
    # user = UserChoiceField(label='Recipient')
    # sender = UserChoiceField(label='Recipient')

    class Meta:
        model = Message
        fields = ()

    def __init__(self, user, *args, **kwargs):
        super(MessagesFilterForm, self).__init__(*args, **kwargs)

        _blank = (("", "All"),)
        my_categories = get_preferences_report(user, trimmed=True).keys()
        message_categories = ((c[0].capitalize() + c[1:]) for c in my_categories if c)
        self.fields["category"].choices = _blank + tuple((c, c) for c in sorted(message_categories))
        self.fields["level"].choices = _blank + tuple(
            c for c in Message.MESSAGE_LEVELS if c[0] != "debug"
        )
        self.fields["delivery_type"].choices = _blank + (
            ("alert", "In-system alerts"),
            ("alerts_only", "In-system-only alerts"),
            ("email", "Emailed notifications"),
        )
