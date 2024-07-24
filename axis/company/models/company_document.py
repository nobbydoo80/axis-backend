"""company_document.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import logging
import os.path

from django.apps import apps
from django.db import models
from simple_history.models import HistoricalRecords

from axis.company.managers import (
    CompanyDocumentManager,
)
from axis.core.utils import randomize_filename, unrandomize_filename

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


def _content_file_name(instance, filename):
    # This is an upload_to handler
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        "company_shared",
        instance.shared_company.slug,
        randomize_filename(filename),
    )


class CompanyDocument(models.Model):
    """This will allow you to share generic docs between two companies."""

    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="company_document"
    )
    shared_company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="shared_document"
    )
    admin_only = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    document = models.FileField(upload_to=_content_file_name, max_length=512)

    # Misc
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

    objects = CompanyDocumentManager()
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.filename())

    def filename(self):
        """Used to return the real name of the file."""
        return os.path.basename(unrandomize_filename(self.document.name))
