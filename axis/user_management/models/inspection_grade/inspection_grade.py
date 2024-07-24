"""inspection_grade.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2019 13:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.user_management.managers import InspectionGradeQuerySet

User = get_user_model()


class InspectionGrade(models.Model):
    A_GRADE = 1
    B_GRADE = 2
    C_GRADE = 3
    D_GRADE = 4
    F_GRADE = 5

    LETTER_GRADE_CHOICES = (
        (A_GRADE, "A"),
        (B_GRADE, "B"),
        (C_GRADE, "C"),
        (D_GRADE, "D"),
        (F_GRADE, "F"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # object that we want to be graded with user
    qa_status = models.ForeignKey(
        "qa.QAStatus",
        max_length=255,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    approver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="inspection_grade_approvers"
    )
    graded_date = models.DateField()
    letter_grade = models.PositiveSmallIntegerField(choices=LETTER_GRADE_CHOICES, null=True)
    numeric_grade = models.PositiveIntegerField(null=True)

    notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()
    objects = InspectionGradeQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Verification Grade"
        verbose_name_plural = "Verification Grades"

    def __str__(self):
        return "Verification Grade {grade}".format(grade=self.display_grade())

    def display_grade(self):
        if (
            self.approver.company
            and self.approver.company.inspection_grade_type == Company.NUMERIC_INSPECTION_GRADE
        ):
            return self.numeric_grade
        return self.get_letter_grade_display()

    def get_inspection_grade_link(self):
        """
        Get task list location based on Content Type of Task.
        :return: str url or empty str in case of new object
        """

        if getattr(self, "qa_status", None):
            return "{}#/tabs/qa".format(
                reverse_lazy("home:view", kwargs={"pk": self.qa_status.home_status.home.pk})
            )
        return None

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if user.company == self.approver.company:
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if user.company == self.approver.company:
            return True

        return False
