import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse
from django.utils import timezone

from axis.core.fields import AxisJSONField

__author__ = "Autumn Valenta"
__date__ = "08/10/18 2:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class ProtoObject(models.Model):
    """
    Object carrying data to be imported.  The content_type must be provided, but the object_id and
    content_object will stay null until a match is confirmed.
    """

    # Generic FK to fully realized object, once it exists
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # ID of the object (not Candidate) that should become the content_object once finalized
    selected_object_id = models.PositiveIntegerField(db_index=True, null=True, blank=True)

    # Data to import
    data = AxisJSONField(default=dict)
    data_profile = models.CharField(max_length=128)

    # Technical data
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(auto_now=True)
    import_failed = models.BooleanField(default=False)
    import_error = models.CharField(max_length=500, blank=True, null=True)
    import_traceback = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{Model} ({matched}{selected}{n} candidates): {repr}".format(
            **{
                "Model": self.content_type.model.capitalize(),
                "matched": "Matched, " if self.content_object else "",
                "selected": "Selected, " if self.content_object else "",
                "n": self.candidate_set.count(),
                "repr": self.data_profile[:10],
            }
        )

    def get_absolute_url(self):
        return reverse("proto:view", kwargs={"pk": self.id})

    def assign_error(self, message, tb=None):
        self.import_failed = True
        self.import_error = message
        self.import_traceback = tb
        self.save()


class Candidate(models.Model):
    proto_object = models.ForeignKey("ProtoObject", on_delete=models.CASCADE)

    # Generic FK to an existing candidate Axis object
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    levenshtein_distance = models.PositiveIntegerField()
    profile_delta = models.IntegerField()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return "{}".format(self.content_object)
