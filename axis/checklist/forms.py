import logging
import os
import re
from base64 import b64decode

from django import forms
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile

from axis.core.utils import random_sequence
from axis.filehandling.forms import AsynchronousProcessedDocumentForm
from . import strings

__author__ = "Autumn Valenta"
__date__ = "1/3/13 10:15 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)

BULK_UPLOAD_EQUIV_MAP = (
    ("Builder", "builder_org"),
    ("Subdivision", "subdivision"),
    ("Community", "community"),
    ("Floorplan", "floorplan"),
    ("Street Address", "street_line1"),
    ("State", "state"),
    ("ZIP Code", "zipcode"),
    ("Rating Type", "rating_type"),
    ("Type", "rating_type"),
    ("Lot #", "lot_number"),
    ("City", "city"),
    ("Program", "eep_program"),
    ("EEP Program", "eep_program"),
    ("Sample Set", "sample_set"),
    ("Street Line 2", "street_line2"),
    ("Certification Date", "certification_date"),
    ("Subdivision Builder Name", "subdivision_builder_name"),
    ("Is Multi-Family", "is_multi_family"),
    ("Is Multi Family", "is_multi_family"),
    ("External ID", "alt_name"),
    ("Const. Stage", "construction_stage"),
    ("Site ID", "alt_name"),
    ("Rater of Record", "rater_of_record"),
    ("Upload to Registry", "upload_to_registry"),
)

FILE_TYPE_EXTENSION_MAP = {
    "png": "png",
    "jpeg": "jpg",
    "jpg": "jpg",
    "txt": "txt",
    "pdf": "pdf",
    "docx": "docx",
    "doc": "doc",
    "xls": "xls",
    "xlsx": "xlsx",
    "blg": "blg",
    "vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
}

BASE64_CONTENT_PATTERN = re.compile(
    r"^data:(?P<content_type>(application|image)/(?P<type>{}));base64,(?P<data>.*)$".format(
        r"|".join(FILE_TYPE_EXTENSION_MAP.keys())
    )
)


def get_raw_field_file(raw_data, filename, field_type=forms.FileField):
    """
    Used to get a field from a base64 encoded file.
    :param raw_data: result of re.match().
    :param filename: string
    :param field_type: field type
    :return: type passed in field_type, default forms.FileField
    """
    filename, extension = os.path.splitext(filename)
    ran_seq = random_sequence(4, include_unicode=False)

    filename = "{}_{}{}".format(filename, ran_seq, extension)

    content_type = raw_data.group("content_type")
    data = b64decode(raw_data.group("data") + (len(raw_data.group("data")) % 4 * "="))

    content_file = ContentFile(data, name=filename)
    uploaded_file = UploadedFile(content_file, filename, content_type, size=content_file.size)

    return field_type().to_python(uploaded_file)


class AsynchronousChecklistCreateForm(AsynchronousProcessedDocumentForm):
    """Sets the name of the task to execute on upload."""

    def clean_task_name(self):
        from .tasks import process_checklist

        return process_checklist


class BulkChecklistUploadForm(AsynchronousProcessedDocumentForm):
    """Sets the name of the task to execute on upload."""

    # This decision branch is handled by the view using the form
    update_existing_answers = forms.BooleanField(
        label="Update answers for existing homes",
        help_text=strings.UPDATE_EXISTING_ANSWERS_HELP_TEXT,
        required=False,
    )

    def clean_task_name(self):
        from .tasks import bulk_checklist_process

        return bulk_checklist_process
