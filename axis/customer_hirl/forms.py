"""Forms."""

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


from django import forms
from django.contrib.auth import get_user_model
from django.forms import Select

from axis.filehandling.forms import AsynchronousProcessedDocumentForm

from .models import Certification, Candidate
from .scoring import scoring_registry, BaseScoringExtraction

User = get_user_model()

COLUMN_NAMES = {
    "CertificationRecID": "id",
    "ProjectID": "project_id",
    "CheckList": "checklist",
    "ScoringPath": "scoring_path",
    "Builder": "builder",
    "RoughInLocation": "rough_in_location",
    "AddressL1": "street_line1",
    "City": "city",
    "StateAbbr": "state_abbreviation",
    "State": "state",
    "County": "county",
    "CertificationLevel": "certification_level",
    "CertificateNumber": "certificate_number",
    "CertificateSentDate": "certificate_sent_date",
    "CommunityProject": "community_project",
    "CertificationType": "certification_type",
    "Zip": "zipcode",
    "UnitCount": "unit_count",
    "HersIndex": "hers_score",
}


class CertificationForm(forms.ModelForm):
    """Map the NGBS internal mssql names to ours."""

    class Meta:
        model = Certification
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CertificationForm, self).__init__(*args, **kwargs)

        if self.data:
            # Convert any of the remote MSSQL names from HIRL to use ours instead.
            # This maintains compatibility with internal use of the form, but allows us also to
            # catch incoming data from them.
            self.data = self.data.copy()
            for k, v in list(self.data.items()):
                if k in COLUMN_NAMES:
                    self.data.pop(k)  # QueryDict returns a list here, but we already have ``v``
                    self.data[COLUMN_NAMES[k]] = v

    def save(self, commit=True):
        """Manage candidate object creation and removal, based on attempted save."""

        final_homes = self.cleaned_data.pop("candidates", [])
        certification = super(CertificationForm, self).save(commit=False)
        if commit:
            certification.save()
            if "candidates" in self.changed_data:
                initial_homes = self.initial["candidates"].all()

                # create and save new members
                for home in final_homes:
                    if home not in initial_homes:
                        Candidate.objects.create(home=home, certification=certification)

                # delete old members that were removed from the form
                for home in initial_homes:
                    if home not in final_homes:
                        Candidate.objects.filter(home=home, certification=certification).delete()

        return certification


class ScoringVerifierSelect(Select):
    """
    Allows to show disabled options in Select
    """

    disabled_choices = []

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        if option.get("value") in self.disabled_choices:
            option["attrs"]["disabled"] = "disabled"

        return option


class ScoringVerifierModelChoiceField(forms.ModelChoiceField):
    """
    Disable verifiers based on criteria
    """

    widget = ScoringVerifierSelect()

    def label_from_instance(self, user):
        label = f"{user.first_name} {user.last_name}"
        if (
            not user.active_customer_hirl_verifier_agreements_count
            and not user.customer_hirl_project_accreditations_count
        ):
            label += " (Does not have an active Verifier Agreement or Accreditations)"
            self.widget.disabled_choices.append(user.pk)
        elif not user.active_customer_hirl_verifier_agreements_count:
            label += " (Does not have an active Verifier Agreement)"
            self.widget.disabled_choices.append(user.pk)
        elif not user.customer_hirl_project_accreditations_count:
            label += " (Does not have any active Accreditations)"
            self.widget.disabled_choices.append(user.pk)

        return label


class ScoringAsynchronousProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    template_type = forms.ChoiceField(
        choices=scoring_registry.as_choices(), label="NGBS Standard Version/Scoring Path"
    )
    data_type = forms.ChoiceField(
        choices=(
            (BaseScoringExtraction.ROUGH_DATA_TYPE, "Rough Verification Report"),
            (BaseScoringExtraction.FINAL_DATA_TYPE, "Final Verification Report"),
        ),
        label="Verification Report Type",
    )
    verifier = ScoringVerifierModelChoiceField(queryset=User.objects.none())
    document = forms.FileField(required=True, help_text="")

    def __init__(self, **kwargs):
        user = kwargs.pop("user")
        super(ScoringAsynchronousProcessedDocumentForm, self).__init__(**kwargs)
        if user.company:
            queryset = user.company.users.filter(is_active=True)
            if not user.is_company_admin:
                queryset = queryset.filter(id=user.id)

            self.fields["verifier"].queryset = queryset.common_annotations()

    def clean_task_name(self):
        from .tasks import scoring_upload_task

        return scoring_upload_task

    def clean(self):
        cleaned_data = super(ScoringAsynchronousProcessedDocumentForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data
