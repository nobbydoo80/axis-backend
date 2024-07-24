"""Forms."""


from django import forms

from .models import NEEACertification, Candidate


__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CertificationForm(forms.ModelForm):
    """Map the NEEA internal names to ours."""

    class Meta:
        model = NEEACertification
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CertificationForm, self).__init__(*args, **kwargs)

        # Convert remote names
        if self.data:
            self.data = self.data.copy()
            for k, v in list(self.data.items()):
                k = k.strip()
                if k in self.Meta.model.FIELDS:
                    self.data.pop(k)  # QueryDict returns a list here, but we already have ``v``
                    self.data[self.Meta.model.FIELDS[k]] = v

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
