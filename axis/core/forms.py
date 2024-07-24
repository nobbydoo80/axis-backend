"""forms.py: Django core"""


import logging
import re

import bleach
from captcha.fields import ReCaptchaField
from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserChangeForm,
    SetPasswordForm,
    UserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
)
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from tensor_registration.forms import TensorApproveUserForm, TensorAnonymousRegistrationForm

from axis.company.models import Company
from axis.core.fields import ApiModelChoiceField
from axis.core.messages import AxisOutsideContactMessage
from axis.core.models import ContactCard, ContactCardEmail, ContactCardPhone
from axis.customer_hirl.models import HIRLUserProfile
from axis.examine.forms import AjaxBase64FileFormMixin
from axis.geographic.fields import UnrestrictedCityChoiceWidget
from axis.home.models import EEPProgramHomeStatus
from axis.messaging.models import Message
from axis.user_management.models import Training, Accreditation, InspectionGrade

__author__ = "Steven Klass"
__date__ = "9/20/11 3:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class UserAdminCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

    def clean_username(self):
        """This has to be over written to use Axis' declared Auth Model."""
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147
        username = self.cleaned_data["username"]
        UserModel = get_user_model()
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages["duplicate_username"],
            code="duplicate_username",
        )


class CompanyApproveModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} (Users: {})".format(obj, obj.counter)


class CustomTensorApproveUserForm(TensorApproveUserForm):
    company = CompanyApproveModelChoiceField(
        queryset=Company.objects.all().annotate(counter=Count("users")),
        widget=forms.Select(attrs={"autofocus": True}),
    )


class CustomTensorAnonymousRegistrationForm(TensorAnonymousRegistrationForm):
    captcha = ReCaptchaField(label="")

    def clean_email(self):
        """Clean email field"""
        if User.objects.filter(email__iexact=self.cleaned_data["email"]).exists():
            raise forms.ValidationError(
                mark_safe(
                    "The email address provided is already "
                    "associated with an existing AXIS account. "
                    "If you have forgotten your password, please click "
                    '<a href="{reset_password_url}">here</a> to reset it.  '
                    "Otherwise, contact {contact_email} "
                    "to help resolve your registration issue.".format(
                        reset_password_url=reverse_lazy("password_reset"),
                        contact_email=",".join(settings.CONTACT_EMAILS),
                    )
                )
            )
        return self.cleaned_data["email"]


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(UserAdminChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get("groups", None)
        if f is None:
            qs = Group.objects.filter(
                Q(name__startswith="builder")
                | Q(name__startswith="eep")
                | Q(name__startswith="rater")
                | Q(name__startswith="hvac")
                | Q(name__startswith="utility")
                | Q(name__startswith="qa")
                | Q(name__startswith="general")
            )
            self.fields["groups"].queryset = qs


class UserFormMixin(forms.ModelForm):
    title = forms.CharField(max_length=32, required=False)
    # increase speed for Examine view loading by removing choices for select fields
    company = forms.CharField(required=False)

    mailing_geocode_street_line1 = forms.CharField(
        max_length=100, label="Address Line 1", required=False
    )
    mailing_geocode_street_line2 = forms.CharField(
        max_length=100, label="Address Line 2", required=False
    )
    mailing_geocode_zipcode = forms.CharField(max_length=15, label="ZIP Code", required=False)
    mailing_geocode_city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget, required=False, label="City"
    )

    shipping_geocode_street_line1 = forms.CharField(
        max_length=100, label="Address Line 1", required=True
    )
    shipping_geocode_street_line2 = forms.CharField(
        max_length=100, label="Address Line 2", required=False
    )
    shipping_geocode_zipcode = forms.CharField(max_length=15, label="ZIP Code", required=True)
    shipping_geocode_city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget, required=True, label="City"
    )


class UserChangeForm(AjaxBase64FileFormMixin.for_fields(["signature_image"]), UserFormMixin):
    """
    We make fields required false to allow serializer validate
    errors and display for user in examine view, in other case invalid values will not be send
    to server from js
    """

    hes_username = forms.CharField(required=False, label="DOE HES Username")
    hes_password = forms.CharField(required=False, label="DOE HES Password")

    work_phone = forms.CharField(required=True)
    cell_phone = forms.CharField(required=False)
    fax_number = forms.CharField(required=False)
    alt_phone = forms.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "email",
            "title",
            "department",
            "work_phone",
            "cell_phone",
            "fax_number",
            "alt_phone",
            "is_active",
            "is_public",
            "is_company_admin",
            "company",
            "timezone_preference",
            "rater_roles",
            "rater_id",
            "signature_image",
            "resnet_username",
            "resnet_password",
        )

    def __init__(self, **kwargs):
        instance = kwargs.get("instance")
        super(UserChangeForm, self).__init__(**kwargs)

        if instance:
            try:
                hes_credentials = instance.hes_credentials
            except ObjectDoesNotExist:
                pass
            else:
                # use this if hack, because our form is using to validate image
                # where we delete all fields except _raw
                if self.fields.get("hes_username"):
                    self.fields["hes_username"].initial = hes_credentials.username
                    self.fields["hes_password"].initial = hes_credentials.password


class BaseUserChangeForm(UserFormMixin):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "email",
            "title",
            "department",
            "work_phone",
            "cell_phone",
            "fax_number",
            "alt_phone",
            "is_active",
            "is_public",
            "company",
            "timezone_preference",
        )


class HIRLUserProfileForm(forms.ModelForm):
    is_qa_designee = forms.BooleanField(label="QA Designee")

    class Meta:
        model = HIRLUserProfile
        fields = ("is_qa_designee",)


class AxisSetPasswordForm(SetPasswordForm):
    """
    Override default auth.SetPasswordForm form to remove help text
    from password field
    """

    def __init__(self, *args, **kwargs):
        super(AxisSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = ""


class AxisPasswordChangeForm(PasswordChangeForm):
    """
    Override default auth.PasswordChangeForm form to remove help text
    from password field
    """

    def __init__(self, *args, **kwargs):
        super(AxisPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = ""


class AxisPasswordResetForm(PasswordResetForm):
    """
    Override default auth.PasswordResetForm form to add additional tos field
    """

    tos = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label="I have read and agree to the Terms of Service",
        required=True,
    )


class DynamicGetOrCreateMixin(object):
    """
    Form mixin for targeting a ``name`` field as an identifier of an existing object.  The initial
    field class should be one of the ``UnattachedOrNew{*}ChoiceField`` field classes.  This mixin
    will change the field to a plain CharField when the form is not in creation mode.
    """

    def __init__(self, *args, **kwargs):
        super(DynamicGetOrCreateMixin, self).__init__(*args, **kwargs)

        if self.instance.pk or "data" in kwargs:
            self.fields["name"] = forms.CharField()


class ContactForm(forms.Form):
    """
    Sends a contact intent to site administrator.
    """

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea())
    body = forms.CharField(max_length=200, required=False)  # Honeypot should be empty. It's hidden
    captcha = ReCaptchaField(label="")

    @classmethod
    def is_censored(cls, text, return_banned=False):
        """I don't want any part of an email that contains this"""
        banned_words = [
            "anal",
            "anus",
            "arse",
            "ass",
            "backlinks",
            "ballsack",
            "balls",
            "bastard",
            "bitch",
            "biatch",
            "bloody",
            "blowjob",
            "blow",
            "booty",
            "bollock",
            "bollok",
            "boner",
            "boob",
            "bugger",
            "bum",
            "butt",
            "buttplug",
            "casino",
            "casinos",
            "cialis",
            "clitoris",
            "cock",
            "coon",
            "credit card",
            "crap",
            "cunt",
            "damn",
            "dick",
            "dildo",
            "dyke",
            "fag",
            "feck",
            "fellate",
            "fellatio",
            "felching",
            "fuck",
            "fudgepacker",
            "fudge",
            "packer",
            "flange",
            "gamble",
            "gambling",
            "Goddamn",
            "God",
            "grown-up",
            "damn",
            "hell",
            "homo",
            "jerk",
            "jizz",
            "knobend",
            "knob",
            "labia",
            "lmao",
            "lmfao",
            "moz",
            "muff",
            "nigger",
            "nigga",
            "nymphomania",
            "omg",
            "payday",
            "penis",
            "piss",
            "pills",
            "poker",
            "poop",
            "p0rn",
            "porn",
            "prick",
            "pube",
            "pussy",
            "queer",
            "seo",
            "semrush",
            "scrotum",
            "sex",
            "shit",
            "sh1t",
            "slut",
            "smegma",
            "spunk",
            "teen",
            "tit",
            "tosser",
            "turd",
            "twat",
            "vagina",
            "wank",
            "whore",
            "Б",
            "б",
            "в",
            "Г",
            "г",
            "Д",
            "д",
            "д",
            "Е",
            "Ё",
            "ё",
            "Ж",
            "ж",
            "З",
            "з",
            "И",
            "и",
            "Й",
            "й",
            "к",
            "Л",
            "л",
            "м",
            "н",
            "П",
            "п",
            "и",
            "т",
            "Ф",
            "ф",
            "Ц",
            "ц",
            "Ч",
            "ч",
            "ч",
            "ц",
            "Ш",
            "ш",
            "Щ",
            "щ",
            "Ъ",
            "ъ",
            "Ы",
            "ы",
            "Ь",
            "ь",
            "Э",
            "э",
            "з",
            "Ю",
            "ю",
            "Я",
            "я",
            ".ru",
            "ù",
            "ó",
            "à",
            "ư",
            "ê",
            "ẫ",
            "ư",
            "ớ",
            "ư",
            "click here",
            "powerful",
            "cost-effective",
            " pill",
            "casino",
            "1000x",
            "100x",
            "10x",
            "affordable prices",
            "roi",
            "bitcoin",
            "dogecoin",
            "coinbase",
        ]

        _banned = []
        for banned_string in banned_words:
            if len(banned_string) > 1:
                if re.search(r"\b%s\b" % banned_string.lower(), text.lower()):
                    _banned.append(banned_string)
            elif banned_string in text.lower():
                _banned.append(banned_string)

        if _banned:
            return True if not return_banned else _banned
        return False if not return_banned else _banned

    def send(self):
        """
        Send an email message to site administrator with parameters
        filled with form field.
        """

        censored = self.is_censored(self.cleaned_data["message"]) or self.is_censored(
            self.cleaned_data["subject"]
        )
        if censored or len(self.cleaned_data["body"]):
            msg = f"Message from {self.cleaned_data['email']} was censored."
            if len(self.cleaned_data["body"]):
                msg += "  Body had content."
            log.info(msg)
            return

        self.cleaned_data["message"] = bleach.clean(
            self.cleaned_data["message"],
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            strip_comments=True,
        )

        users = User.objects.filter(company__slug="pivotal-energy-solutions", is_superuser=True)
        if not users.count():
            return
        AxisOutsideContactMessage().send(users=users, context=self.cleaned_data)
        log.debug(f"Sending contact request to {users.count()} users")


class SystemMessengerForm(forms.ModelForm):
    """Handles an admin attempt to issue a platform notification."""

    companies = forms.ModelMultipleChoiceField(queryset=Company.objects.all())
    cc = forms.BooleanField(label="Also CC me", required=False)

    class Meta:
        model = Message
        fields = ("title", "content", "level", "url", "sticky_alert")
        labels = {
            "content": "Message",
            "level": "Severity",
            "url": "Link",
            "sticky_alert": "Stay visible until dismissed",
        }


class UserTrainingForm(AjaxBase64FileFormMixin.for_fields(["certificate"]), forms.ModelForm):
    class Meta:
        model = Training
        exclude = (
            "trainee",
            "statuses",
        )


class UserAccreditationForm(forms.ModelForm):
    def __init__(self, company, *args, **kwargs):
        super(UserAccreditationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Accreditation
        exclude = ("trainee", "approver", "state_changed_at")


class UserCertificationMetricForm(forms.ModelForm):
    """
    Form is not editable and using to avoid errors in machinery
    """

    eep_program = forms.ChoiceField(choices=[])
    home = forms.ChoiceField(label="Address", choices=[])

    class Meta:
        model = EEPProgramHomeStatus
        fields = ("eep_program", "home", "certification_date")


class UserInspectionGradeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(UserInspectionGradeForm, self).__init__(*args, **kwargs)
        if (
            not user.company
            or user.company.inspection_grade_type == Company.LETTER_INSPECTION_GRADE
        ):
            del self.fields["numeric_grade"]
            self.fields["letter_grade"].required = True
        else:
            del self.fields["letter_grade"]
            self.fields["numeric_grade"].required = True

    class Meta:
        model = InspectionGrade
        fields = ("graded_date", "letter_grade", "numeric_grade", "notes")
        labels = {"letter_grade": "Grade", "numeric_grade": "Grade", "graded_date": "Date Graded"}


class ContactCardForm(forms.ModelForm):
    class Meta:
        model = ContactCard
        fields = ("first_name", "last_name", "title")


class ContactCardPhoneForm(forms.ModelForm):
    phone = forms.CharField(required=True)

    class Meta:
        model = ContactCardPhone
        fields = ("phone", "description")


class ContactCardEmailForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = ContactCardEmail
        fields = ("email", "description")
