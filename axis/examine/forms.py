"""Helper forms"""


import logging

from django import forms

from axis.core.utils import clean_base64_encoded_payload


__author__ = "Autumn Valenta"
__date__ = "11/26/19 11:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class AjaxBase64FileFormMixin(object):
    """
    Generic form mixin for making target FileFields support ajax submission as base64-encoded
    payloads.

        Base64Mixin = AjaxBase64FileFormMixin.for_fields(['document'])
        class MyForm(Base64Mixin, forms.ModelForm):
            class Meta:
                model = MyModel

    By naming the filefields for the dynamic mixin, a corresponding "FOO_raw" and "FOO_raw_name"
    are generated, along with a "clean_FOO_raw()" method to decode the base64 payload into a
    standard UploadedFile instance found in a normal cleaned_data, which is patched into the
    original field's cleaned_data[FOO] entry.  This essentially makes the base64
    serialization-deserialization loop completely transparent, and the form can have its "save()"
    method called, and it does the right thing.

    In order to instantiate a copy of the form that targets only the base64 "raw" fields, init the
    form with the special kwarg "raw_file_only=True".  This will remove all other form fields so
    that the base64 request payload can be isolated and saved to an instance that may have already
    been created or saved elsewhere:

    # django-rest-framework API example
    def perform_save(self, serializer):
        obj = serializer.save()
        form = MyForm(self.request.data, instance=obj, raw_file_only=True)
        form.save()

    """

    # List of "xxxxx/yyyyy" mimetype strings allowed by the file fields
    # None means all types are allowed.
    # All fields named by the classmethod for_fields() will use the same mimetype list
    valid_content_types = None

    _raw_suffix = None
    _raw_source_fields = None
    _raw_fields = None

    @classmethod
    def for_fields(cls, fields, suffix="_raw"):
        attrs = {
            "_raw_suffix": suffix,
            "_raw_source_fields": fields,
            "_raw_fields": [],
        }

        # Factored out of next for-loop to avoid bad closure leak of loop var
        def get_cleaner(field):
            return lambda self: self._clean_file_raw((field + suffix), (field + suffix + "_name"))

        for field in fields:
            attrs["_raw_fields"].extend(
                [
                    field,
                    field + suffix,
                    field + suffix + "_name",
                ]
            )

            attrs["clean_%s_raw" % (field,)] = get_cleaner(field)

        return type(str("ConfiguredAjaxBase64FileFormMixin"), (cls,), attrs)

    def __init__(self, *args, **kwargs):
        self.raw_file_only = kwargs.pop("raw_file_only", False)
        self.valid_content_types = kwargs.pop("valid_content_types", self.valid_content_types)
        self.user = kwargs.pop("user", None)
        super(AjaxBase64FileFormMixin, self).__init__(*args, **kwargs)

        # Add the raw fields, which are not picked up during ModelForm declaration
        if isinstance(self, forms.ModelForm):
            formfield = forms.CharField(widget=forms.HiddenInput, required=False)
            for field_name in self._raw_source_fields:
                # IMPORTANT: '_name' field comes first so that it is cleaned first!
                self.fields[field_name + self._raw_suffix + "_name"] = formfield
                self.fields[field_name + self._raw_suffix] = formfield
                if self.raw_file_only:
                    self.fields[field_name].required = False

        # Remove everything else but these fields if we're doing a base64 deserialization phase
        if self.raw_file_only:
            for k in list(self.fields.keys()):
                if k not in self._raw_fields:
                    del self.fields[k]

    def _clean_file_raw(self, field, name_field):
        """Common handler for all raw file fields added to this form."""
        if name_field not in self.cleaned_data:
            return None
        filename = self.cleaned_data[name_field]
        data = self.cleaned_data[field]

        val = clean_base64_encoded_payload(
            filename, data, formfield=forms.FileField, valid_content_types=self.valid_content_types
        )

        return val

    def clean(self):
        """Validates that either 'document' or 'document_raw' exists."""
        cleaned_data = super(AjaxBase64FileFormMixin, self).clean()

        for field in self._raw_source_fields:
            file_field = cleaned_data.get(field)
            file_field_raw = cleaned_data.get(field + self._raw_suffix)
            if file_field_raw:
                cleaned_data[field] = file_field_raw
            elif not file_field and not self.raw_file_only:
                raise forms.ValidationError("'%s' is required." % (field,))

        return cleaned_data
