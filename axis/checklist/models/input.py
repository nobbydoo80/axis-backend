"""django_input_collection integration"""


import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

from django_input_collection.models import AbstractCollectedInput, AbstractBoundSuggestedResponse

from axis.core.fields import AxisJSONField
from axis.core.utils import randomize_filename, unrandomize_filename
from . import managers


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class CollectedInput(AbstractCollectedInput):
    objects = managers.CollectedInputQuerySet.as_manager()

    data = AxisJSONField()
    customer_documents = GenericRelation("filehandling.CustomerDocument")

    # Hints for the context in which this input was collected
    home = models.ForeignKey("home.Home", on_delete=models.CASCADE)
    home_status = models.ForeignKey("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    user_role = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ("qa", "QA"),
            ("rater", "Rater"),
            ("other", "[Other]"),
        ],
    )

    # Failure modes
    is_failure = models.BooleanField(default=False)
    failure_is_reviewed = models.BooleanField(default=False)


class AxisBoundSuggestedResponse(AbstractBoundSuggestedResponse):
    """Extends the answer choice model to add hints unrelated to conditional questions."""

    is_considered_failure = models.BooleanField(default=False)
    comment_required = models.BooleanField(default=False)
    document_required = models.BooleanField(default=False)
    photo_required = models.BooleanField(default=False)

    def __str__(self):
        flags_info = sorted(self.get_flags().items())
        return "{} ({})".format(
            self.suggested_response.data,
            ", ".join("=".join((k, "{}".format(v))) for k, v in flags_info),
        )

    def get_flags(self):
        return {
            "is_considered_failure": self.is_considered_failure,
            "comment_required": self.comment_required,
            "document_required": self.document_required,
            "photo_required": self.photo_required,
        }
