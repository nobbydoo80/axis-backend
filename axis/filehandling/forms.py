"""forms.py: Django filehandling"""


import logging

from django import forms

from axis.examine.forms import AjaxBase64FileFormMixin
from .models import CustomerDocument, AsynchronousProcessedDocument

__author__ = "Steven Klass"
__date__ = "5/27/12 5:22 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AsynchronousProcessedDocumentForm(forms.ModelForm):
    """Base form for starting the intake process of a file chosen by the user.

    `clean_task_name()` should be overridden to return a task reference to trigger when valid.
    This form will not run the task itself, but provides it to the view in a streamlined way.
    """

    class Meta:
        model = AsynchronousProcessedDocument
        fields = ("document", "task_name", "company")
        widgets = {"company": forms.HiddenInput()}

    def clean_task_name(self):
        """Hook for task target."""

        raise NotImplementedError(
            "You must override `clean_task_name()` and return a task function reference"
        )


# FIXME: Document this its unexpectedly irregular super() calls.  Get it out of the standard code.
class TestAsynchronousProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    """REMOVE ME: this is for testing only"""

    def clean_task_name(self):
        """See class docstring."""

        from .tasks import file_uploading_test

        log.info("Test Assignment of the task name")
        return file_uploading_test

    def clean(self):
        """See class docstring."""

        cleaned_data = super(AsynchronousProcessedDocumentForm, self).clean()  # noqa (see class)
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data


class CustomerDocumentForm(AjaxBase64FileFormMixin.for_fields(["document"]), forms.ModelForm):
    """Standard `CustomerDocument` upload form.

    This form supports base64-encoded payloads on the `document_raw` field, which is preferred over
    `document` if it is present.
    """

    class Meta:
        model = CustomerDocument
        fields = ("document", "description", "is_public", "login_required")

    def __init__(self, *args, **kwargs):
        """Accept extra kwargs `allow_multiple` and `raw_field_only`.

        NOTE: `raw_field_only` is an internal kwarg from the `AjaxBase64FileFormMixin` base, which
        drops all fields but `document_raw` for trivial form cleaning of that field in isolation.
        """

        allow_multiple = kwargs.pop("allow_multiple", False)
        raw_file_only = kwargs.get("raw_file_only")
        super(CustomerDocumentForm, self).__init__(*args, **kwargs)

        # The document field will not exist when we're expecting only raw inputs.
        if not raw_file_only:
            self.fields["document"].widget.attrs["multiple"] = allow_multiple
