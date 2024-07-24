"""forms.py: Django remrate"""


import logging

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.forms.models import ModelForm

from axis.company.models import BuilderOrganization
from axis.eep_program.models import EEPProgram
from .models import RemRateUser

__author__ = "Steven Klass"
__date__ = "6/5/12 7:13 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

RESERVED_USERNAMES = {"root", "sklass", "pivotal", "admin"} | {
    db["NAME"] for db in settings.DATABASES.values()
}
RESERVED_PASSWORDS = [
    "Pa55w0rd",
    "Pa55W0rd",
    "pa55w0rd",
    "pa55W0rd",
    "PA55W0RD",
    "Pa55 W0rd",
    "Pa55 w0rd",
    "pa55 w0rd",
    "pA55w0rD",
    "P@$$w0rd",
    "password",
    "pass",
]


class RemRateUserCreateForm(ModelForm):
    password = forms.CharField(label="New password", widget=forms.PasswordInput, strip=False)
    new_password2 = forms.CharField(
        label="New password confirmation", strip=False, widget=forms.PasswordInput
    )

    class Meta(object):
        fields = ("username", "password")
        model = RemRateUser

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super(RemRateUserCreateForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        if self.initial.get("username") and self.cleaned_data.get("username") == self.initial.get(
            "username"
        ):
            return self.cleaned_data.get("username")
        if self.cleaned_data.get("username") in RESERVED_USERNAMES:
            raise forms.ValidationError("Sorry you cannot use that reserved name")
        if RemRateUser.objects.filter(username=self.cleaned_data.get("username")).count():
            raise forms.ValidationError(
                "Sorry the user '{}' already exists".format(self.cleaned_data.get("username"))
            )
        return self.cleaned_data.get("username")

    def clean_new_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("new_password2")
        if password and password2:
            if password != password2:
                raise forms.ValidationError("The two passwords do not match")
        if password in RESERVED_PASSWORDS:
            raise forms.ValidationError("Too obvious - please try something else.")
        # using django AUTH_PASSWORD_VALIDATORS complexity validation
        password_validation.validate_password(password2)
        return password2

    def save(self, commit=True):
        obj = super(RemRateUserCreateForm, self).save(commit=False)
        obj.company = self.company
        obj.save()
        return obj


class RemRateUserUpdateForm(RemRateUserCreateForm):
    class Meta(RemRateUserCreateForm.Meta):
        widgets = {
            "username": forms.TextInput(attrs={"readonly": "readonly"}),
        }
