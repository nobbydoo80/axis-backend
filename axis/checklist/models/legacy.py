"""checklist models"""


import logging
import os.path
from functools import partial

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Count, SET_NULL
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.core.utils import randomize_filename, unrandomize_filename
from axis.core.utils import slugify_uniquely
from .managers import CheckListManager, SectionManager, AnswerManager, QuestionManager
from .. import validators

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

TYPE_CHOICES = (
    ("open", "Open"),
    ("multiple-choice", "Multiple Choice"),
    ("date", "Date"),
    ("datetime", "DateTime"),
    ("integer", "Whole Number"),
    ("int", "Whole Number"),
    ("float", "Decimal Number"),
    ("csv", "Comma Separated Value"),
    ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
)

QUESTION_TYPE_VALIDATORS = {
    type: getattr(validators, "validate_{}_answer".format(type.replace("-", "_")))
    for type, _ in TYPE_CHOICES
}


class Question(models.Model):
    """Questions of type open or multiple-choice."""

    objects = QuestionManager()

    priority = models.IntegerField(default=1)
    question = models.TextField(help_text="Enter Question")
    type = models.CharField(
        choices=TYPE_CHOICES, max_length=100, default="open", help_text="Select type of Question"
    )
    description = models.TextField(null=True, blank=True, help_text="Enter Question Description")
    help_url = models.CharField(max_length=512, null=True, blank=True)
    climate_zone = models.ForeignKey(
        "geographic.ClimateZone", on_delete=models.CASCADE, null=True, blank=True
    )
    unit = models.CharField(max_length=50, null=True, blank=True)
    question_choice = models.ManyToManyField("QuestionChoice")

    # Determines whether or not a question can be bulk filled in.
    allow_bulk_fill = models.BooleanField(default=False)

    is_optional = models.BooleanField(default=False)

    # If provided on a type=integer or type=float question, these will contribute to validator
    # logic.
    minimum_value = models.FloatField(default=None, blank=True, null=True)
    maximum_value = models.FloatField(default=None, blank=True, null=True)

    display_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        ordering = (
            "priority",
            "question",
        )

    def __str__(self):
        """
        Returns a blank string if the question has no content.  Primarily useful for unsaved
        instances on a giant formset.

        """
        return self.question or ""

    def save(self, *args, **kwargs):
        """Removes multiple-choice options if the question becomes non-multiple-choice."""

        if not self.slug:
            self.slug = slugify_uniquely(self.question, self.__class__)
        results = super(Question, self).save(*args, **kwargs)

        if self.type != "multiple-choice":
            self.question_choice.clear()
        return results

    def can_be_edited(self, user):
        """Returns ``False `` if the question has been assigned to a checklist or section."""
        if user.has_perm("checklist.change_question"):
            if self.checklist_set.count() == 0 and self.section_set.count() == 0:
                return True
        return False

    def can_be_deleted(self, user):
        return user.has_perm("checklist.delete_question")

    def get_validator_for_type(self, **kwargs):
        """
        Returns the callable validator function for the question's ``type``, wrapped in a partial()
        that includes a reference to the question instance.  The only way for the validator to know
        specific conditions of the validation (min/max ranges, etc) is via this question reference.
        """
        return partial(QUESTION_TYPE_VALIDATORS[self.type], self, **kwargs)

    # django-input-collection compatibility
    def test_conditions(self, *args, **kwargs):
        return True


class QuestionChoice(models.Model):
    choice = models.CharField(max_length=255)
    photo_required = models.BooleanField(default=False)
    document_required = models.BooleanField(default=False)
    email_required = models.BooleanField(default=False)
    comment_required = models.BooleanField(default=False)
    is_considered_failure = models.BooleanField(default=False)
    display_as_failure = models.BooleanField(default=False)
    choice_order = models.IntegerField()
    display_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("choice_order",)

    def __str__(self):
        return self.choice[:40]


class CheckList(models.Model):
    objects = CheckListManager()

    # TODO: Add unique=True to this field, since we're using slugify_uniquely in the save() method.
    slug = models.SlugField()

    name = models.CharField(max_length=200)
    public = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField("Question")
    group = models.ForeignKey(
        "auth.Group",
        on_delete=models.CASCADE,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    display_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Sets a default slug."""
        if not self.slug:
            self.slug = slugify_uniquely(self.name[:45], self.__class__)
        super(CheckList, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.slug,)  # must return a tuple


class Section(models.Model):
    objects = SectionManager()

    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField("Question")
    checklist = models.ForeignKey("CheckList", on_delete=models.CASCADE, blank=True, null=True)
    priority = models.IntegerField(default=1)
    display_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("priority",)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)  # must return a tuple

    def save(self, *args, **kwargs):
        """Sets a default slug."""
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)
        return super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("checklist:section_detail", kwargs={"slug": self.slug})

    def can_be_edited(self, user):
        """Returns ``False`` if any non-"open" questions in the section have been answered."""
        if user.has_perm("checklist.change_section"):
            return self.questions.exclude(type="open").aggregate(n=Count("answer"))["n"] == 0
        return False

    def can_be_deleted(self, user):
        return user.has_perm("checklist.delete_section")


class AnswerBase(models.Model):
    objects = AnswerManager()

    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    home = models.ForeignKey("home.Home", on_delete=models.CASCADE)
    answer = models.TextField()
    comment = models.TextField(blank=True, null=True)
    system_no = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=50, default="open", choices=TYPE_CHOICES)
    photo_required = models.BooleanField(default=False)
    document_required = models.BooleanField(default=False)
    email_required = models.BooleanField(default=False)
    email_sent = models.BooleanField(null=True, default=None)
    is_considered_failure = models.BooleanField(default=False)
    display_as_failure = models.BooleanField(default=False)
    failure_is_reviewed = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    display_flag = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    bulk_uploaded = models.BooleanField(default=False)

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    class Meta:
        abstract = True

    def __str__(self):
        if self.answer:
            return "{}".format(self.answer)[:50]
        return "Unanswered"

    def get_other_answers(self):
        """Returns the sibling answers for the same question/home/system_no combination."""
        manager = getattr(self.question, "{}_set".format(self.__class__.__name__.lower()))
        return manager.filter(
            home=self.home, system_no=self.system_no, user__company=self.user.company
        ).exclude(pk=self.pk)

    def get_conflicting_answers(self):
        """
        Returns the sibling answers via ``get_other_answers()`` which are NOT failures.  Answers are
        NOT considered conflicting if ``is_considered_failure`` is True.

        """
        return self.get_other_answers().filter(is_considered_failure=False)


class Answer(AnswerBase):
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"


class QAAnswer(AnswerBase):
    history = HistoricalRecords()

    class Meta:
        verbose_name = "QA Answer"
        verbose_name_plural = "QA Answers"


def _photo_location(instance, filename):
    """Returns the filesystem location for a Floorplan photo."""
    if not isinstance(filename, str):
        filename = filename.name
    company = instance.answer.user.company
    return os.path.join(
        "documents",
        company.company_type,
        company.slug,
        "answer_images",
        randomize_filename(filename),
    )


class AnswerImage(models.Model):
    photo = models.FileField(upload_to=_photo_location, max_length=512, blank=True, null=True)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE, blank=True, null=True)

    def filename(self):
        """Return the photo's unrandomized filename."""
        return os.path.basename(unrandomize_filename(self.photo.name))


def _document_location(instance, filename):
    """Returns the filesystem location for a Floorplan BLG file."""
    if not isinstance(filename, str):
        filename = filename.name
    company = instance.answer.user.company
    return os.path.join(
        "documents",
        company.company_type,
        company.slug,
        "answer_documents",
        randomize_filename(filename),
    )
