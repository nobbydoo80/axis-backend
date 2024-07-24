"""models.py: Django builder_agreement"""


import logging
import os.path

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.core.utils import randomize_filename, unrandomize_filename
from .managers import BuilderAgreementManager

__author__ = "Steven Klass"
__date__ = "3/2/12 1:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def builder_agreement_file_name(instance, filename):
    """Location of any builder agreement documents
    :param filename: Filename for the supplementary document
    :param instance: Instance the logo is bound to.
    """
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        "builder_agreements",
        randomize_filename(filename),
    )


HELP_TEXT = {
    "builder_org": "The name of the builder the agreement is for",
    "subdivision": "The sudivision this agreement will cover.  If this for custom homes you may "
    "leave this blank",
    "total_lots": "Total number of lots this agreement covers",
    "eep_programs": "The name of the Energy Efficiency Programs this agreement will cover.  "
    "Incentive payments will check this.",
    "start_date": "The start date that this agreement begins.  Incentive Payments will be "
    "checked against this.",
    "expire_date": "The expiration date that this agreement ends on.  Incentive Payments will be "
    "checked against this.",
    "document": "The hard copy of the builder agreement.",
    "documents": "Any supporting documentation that pertains to this builder agreement",
    "comment": "Additional notes.",
    "is_active": "This a master switch.  Incentive Payments will be checked against this.",
    "is_legacy": "A flag to indicate that Incentive Payment checks should not validate items.",
}


class BuilderAgreement(models.Model):
    """This is an agreement between a builder and a utility company."""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    builder_org = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="builder_agreements",
        help_text=HELP_TEXT["builder_org"],
    )
    subdivision = models.ForeignKey(
        "subdivision.Subdivision",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text=HELP_TEXT["subdivision"],
    )
    total_lots = models.IntegerField(null=True, blank=True, help_text=HELP_TEXT["total_lots"])
    eep_programs = models.ManyToManyField(
        "eep_program.EEPProgram", help_text=HELP_TEXT["eep_programs"]
    )
    start_date = models.DateField(null=True, blank=True, help_text=HELP_TEXT["start_date"])
    expire_date = models.DateField(null=True, blank=True, help_text=HELP_TEXT["expire_date"])
    document = models.FileField(
        upload_to=builder_agreement_file_name,
        null=True,
        max_length=512,
        blank=True,
        help_text=HELP_TEXT["document"],
    )

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    comment = models.TextField(
        max_length=350, blank=True, null=True, help_text=HELP_TEXT["comment"]
    )
    lots_paid = models.IntegerField(default=0)  # Tracking only

    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text=HELP_TEXT["is_active"])
    is_legacy = models.BooleanField(default=False, help_text=HELP_TEXT["is_legacy"])

    objects = BuilderAgreementManager()
    history = HistoricalRecords()

    class Meta:
        ordering = ("subdivision__name", "subdivision__community__name", "builder_org__name")
        verbose_name = "Builder Agreement"

    def __str__(self):
        if self.subdivision:
            return "{} {} Agreement".format(self.company, self.subdivision.name)
        return "{} {} Agreement".format(self.company, self.builder_org)

    def get_absolute_url(self):
        return reverse("builder_agreement:view", kwargs={"pk": self.pk})

    def filename(self):
        """Returns the actual filename."""
        return os.path.basename(unrandomize_filename(self.document.name))

    @classmethod
    def can_be_added(cls, requesting_user):
        return requesting_user.has_perm("builder_agreement.add_builderagreement")

    def can_be_deleted(self, user):
        """Allows deletion if ``lots_paid`` is false-like."""
        if user.is_superuser or user.has_perm("builder_agreement.delete_builderagreement"):
            return not self.lots_paid
        return False

    def can_be_edited(self, user):
        """Allows editing in the default case."""
        if user.is_superuser or user.has_perm("builder_agreement.change_builderagreement"):
            return True
        return False
