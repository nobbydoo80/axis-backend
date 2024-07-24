__author__ = "Steven Klass"
__date__ = "3/2/12 11:27 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import csv
import operator
import typing
import logging
from functools import reduce

import dateutil.parser
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, SET_NULL
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from axis.core.utils import slugify_uniquely, LONG_DASHES
from .managers import AnnotationQuerySet, AnnotationTypeQueryset


log = logging.getLogger(__name__)

_applicable_types_queries = [
    Q(**{"app_label": pair[0], "model": pair[1]})
    for pair in (
        ("community", "community"),
        ("subdivision", "subdivision"),
        ("floorplan", "floorplan"),
        ("home", "home"),
        ("home", "eepprogramhomestatus"),
        ("incentive_payment", "incentivepaymentstatus"),
    )
]

# strftime format used to normalized dates parsed with VALID_DATE_FORMATS
NORMALIZED_DATE_FORMAT = "%b %d, %Y"  # January 13, 2012


def get_applicable_types():
    return ContentType.objects.filter(reduce(operator.or_, _applicable_types_queries))


def _limit_choices_to():
    return list(get_applicable_types().values_list("id", flat=True))


class Type(models.Model):
    """Represents a type for an ``Annotation``.  Types are given an independent model so that they
    can be assigned as part of the ``relationship`` app.

    Intended type examples: "comment", "issue", external un-managed annotation

    As in the case of the latter, a client admin can create a field such as "Legacy ID", enabling
    other users to create annotations on a home (for example) of this type.

    A Type is created with a direct association to another model, so that a "Legacy ID" type isn't
    coincidentally available to the end users on every database model.  For example, the Home model
    might be specified when creating the "Legacy ID" Type.

    ``is_unique`` introduces a constraint that an annotation of this type can only be created once
    on an object.  For example, if a "Legacy ID" type is unique, there can only be one such
    annotation made on target objects.
    """

    DATA_TYPE_OPEN = "open"
    DATA_TYPE_MULTIPLE_CHOICE = "multiple-choice"
    DATA_TYPE_DATE = "date"
    DATA_TYPE_INTEGER = "integer"
    DATA_TYPE_FLOAT = "float"

    DATA_TYPE_CHOICES = (
        (DATA_TYPE_OPEN, "Open"),
        (DATA_TYPE_MULTIPLE_CHOICE, "Multiple Choice"),
        (DATA_TYPE_DATE, "Date"),
        (DATA_TYPE_INTEGER, "Whole Number"),
        (DATA_TYPE_FLOAT, "Decimal Number"),
    )

    objects = AnnotationTypeQueryset.as_manager()

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    data_type = models.CharField(
        max_length=50,
        choices=DATA_TYPE_CHOICES,
        help_text="Specifies the format of annotations made with this type.",
    )
    is_unique = models.BooleanField(default=False)

    applicable_content_types = models.ManyToManyField(
        ContentType,
        verbose_name="Applicable Types",
        # limit_choices_to={'id__in': _limit_choices_to}
    )

    valid_multiplechoice_values = models.CharField("Possible values", max_length=500, blank=True)
    is_required = models.BooleanField(default=False)

    slug = models.SlugField(unique=True, editable=False, max_length=255)

    class Meta:
        """Anything that's not a field"""

        ordering = ("name",)
        verbose_name = "Annotation Type"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Adds a unique slug to the type"""
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        super(Type, self).save(*args, **kwargs)

    @classmethod
    def set_valid_multiplechoice_values(cls, items: list) -> str:
        """A class method showing how to store items, this correctly handles commas"""
        data = []
        for item in items:
            item = item.strip()
            if "," in item:
                item = f'"{item}"'
            data.append(item)
        return ",".join(data)

    def get_valid_multiplechoice_values(self) -> list:
        """Get the choice option list.  This supports quoted options where commas are involved"""
        return [
            x
            for x in list(
                csv.reader([self.valid_multiplechoice_values], delimiter=",", quotechar='"')
            )[0]
        ]

    def get_multiplechoice_value(
        self, value: str, app_log: typing.Union[logging.Logger, None] = None
    ):
        """
        Does a fuzzy check of value against the items in ``valid_multiplechoice_values``.  If the
        value cannot match a valid choice, None is returned.
        """
        app_log = app_log if app_log else logging.getLogger(__name__)
        value_normalized = LONG_DASHES.sub("-", "{}".format(value.strip()).lower())
        candidates = self.get_valid_multiplechoice_values()
        for candidate in candidates:
            candidate_normalized = LONG_DASHES.sub("-", candidate.lower())
            if candidate_normalized == value_normalized:
                value = candidate
                break
        else:
            # Destroy the value so we make it clear that it's not a valid choice.
            app_log.error(
                f"Annotation choice {value} for {self!r} is invalid.  It must be one "
                f"of {self.valid_multiplechoice_values}"
            )
            value = None
        return value


class Annotation(models.Model):
    """
    Generically attaches to another model, providing a textual annotation for the referenced object.
    ``Annotation`` provides a ``type`` field to help users manage a list of annotations on a single
    object.

    According to the value of ``annotation.Type.is_unique``, multiple annotations with the same type
    on the same object may or may not be allowed.

    """

    objects = AnnotationQuerySet.as_manager()
    type = models.ForeignKey("Type", on_delete=models.CASCADE, verbose_name="Annotation Type")
    content = models.CharField(max_length=500, verbose_name="Value")

    # Enable generic foreign key to other models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    history = HistoricalRecords()

    created_on = models.DateTimeField(default=now, editable=False)
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=SET_NULL)

    field_name = models.CharField(max_length=30, blank=True)
    is_public = models.BooleanField(default=True)

    # TODO: Validate that the associated content_type matches type.applicable_content_type

    class Meta:
        ordering = ("type__name",)

    def __str__(self):
        return "{}".format(self.content)

    def clean(self):
        """Clean the values prior to savings."""

        data_format = self.type.data_type

        if self.content:
            if data_format == "date":
                try:
                    date_obj = dateutil.parser.parse(self.content)
                except ValueError:
                    raise ValidationError("Can't determine a date from the given value.")
                self.content = date_obj.strftime(NORMALIZED_DATE_FORMAT)

            elif data_format == "integer":
                try:
                    self.content = str(int(self.content))
                except ValueError:
                    raise ValidationError("The value must be an integer.")

            elif data_format == "float":
                try:
                    self.content = str(float(self.content))
                except ValueError:
                    raise ValidationError("The value must be a valid decimal.")
            elif data_format == "multiple-choice":
                content = self.content.strip()
                if content not in self.type.get_valid_multiplechoice_values():
                    raise ValidationError("Value is not valid for the given choices.")
        else:
            self.content = ""

    def save(self, **kwargs):
        if not self.id:
            self.created_on = now()
        self.last_update = now()
        return super(Annotation, self).save(**kwargs)
