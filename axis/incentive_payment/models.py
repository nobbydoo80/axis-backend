"""models.py: Django incentive_payment"""


import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now, localtime
from django_states.models import StateModel
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.core.fields import UUIDField
from .managers import (
    IncentiveDistributionManager,
    IPPItemManager,
    IncentivePaymentStatusManager,
)
from .state_machine import IPPItemStateMachine

__author__ = "Steven Klass"
__date__ = "3/16/12 1:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class IncentivePaymentStatus(StateModel):
    """This is just a tracking table to know where these things are after it's certified through
    payment"""

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    home_status = models.OneToOneField("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    annotations = GenericRelation("annotation.Annotation")

    created_on = models.DateTimeField(editable=False)
    last_update = models.DateTimeField(editable=True)

    Machine = IPPItemStateMachine
    objects = IncentivePaymentStatusManager()

    def get_absolute_url(self):
        return reverse("home:view", kwargs={"pk": self.home_status.home.id})

    class Meta:
        verbose_name = "Incentive Payment Status"
        verbose_name_plural = "Incentive Payment Statuses"

    def save(self, *args, **kwargs):
        if not self.id and not self.created_on:
            self.created_on = now()
        self.last_update = now()
        return super(IncentivePaymentStatus, self).save(*args, **kwargs)

    def get_state_display(self):
        return self.get_state_info().description

    @classmethod
    def can_be_added(cls, requesting_user):
        return requesting_user.has_perm("incentive_payment.add_incentivepaymentstatus")

    def should_show_data(self, user):
        if user.is_superuser or user.company.id in [
            self.owner.id,
            self.home_status.company.id,
        ]:
            return True
        if IncentiveDistribution.objects.filter_by_user(
            user=user, ippitem__home_status_id=self.home_status.id
        ).count():
            return True
        return False

    def get_full_status(self, user):
        """This returns a complete list of things attached to this"""

        show_details = self.should_show_data(user)
        data = {
            "exists": True,
            "show_details": show_details,
            "distributions": [],
            "annotations": [],
        }
        if not show_details:
            return data

        distributions = IncentiveDistribution.objects.filter_by_user(
            user=user, ippitem__home_status_id=self.home_status.id
        )

        for item in distributions.values():
            company = Company.objects.get(id=item["company_id"])
            customer = Company.objects.get(id=item["customer_id"])
            _data = {
                "url": IncentiveDistribution.objects.get(pk=item["id"]).get_absolute_url(),
                "company": "{}".format(company),
                "company_url": company.get_absolute_url(),
                "customer": "{}".format(customer),
                "customer_url": customer.get_absolute_url(),
                "status_display": next(
                    (
                        x[1]
                        for x in IncentiveDistribution.INCENTIVE_STATUS
                        if x[0] == item["status"]
                    ),
                    "",
                ),
            }
            _data.update(dict(item.items()))
            if _data["paid_date"]:
                _data["paid_date"] = _data["paid_date"].strftime("%m/%d/%Y")
            if _data["check_requested_date"]:
                _data["check_requested_date"] = _data["check_requested_date"].strftime("%m/%d/%Y")
            _data["total"] = "${0:,}".format(_data["total"])
            try:
                cost = IPPItem.objects.get(
                    incentive_distribution__id=item["id"], home_status=self.home_status
                ).cost
                _data["unit_cost"] = "${0:,}".format(cost)
            except ObjectDoesNotExist:
                pass
            if user.company != company and not user.is_superuser:
                _data.pop("check_number")
            if user.company.id in [company.id, customer.id] or user.is_superuser:
                data["distributions"].append(_data)

        if user.company.id in [self.home_status.company.id, self.owner.id] or user.is_superuser:
            for annotation in self.annotations.order_by("-created_on").values():
                _data = {"user": user}
                if annotation.get("user_id"):
                    _data = {"user": User.objects.get(id=annotation.get("user_id")).get_full_name()}
                _data.update(dict(annotation.items()))
                _data["created_on"] = localtime(_data["created_on"]).strftime("%m/%d/%Y")
                _data["last_update"] = localtime(_data["last_update"]).strftime("%m/%d/%Y")
                data["annotations"].append(_data)

        data.update(
            {
                "home_url": self.home_status.home.get_absolute_url(),
                "owner": "{}".format(self.owner),
                "owner_url": self.owner.get_absolute_url(),
                "created_on": localtime(self.created_on).strftime("%m/%d/%Y"),
                "last_update": localtime(self.created_on).strftime("%m/%d/%Y"),
                "state_display": self.get_state_display(),
                "state": self.state,
                "show_details": True,
            }
        )

        return data


class IncentiveDistribution(models.Model):
    """This is a group of homes which need to get paid on"""

    CHECK_REQUESTED_STATUS = 1
    PAID_STATUS = 2
    REFUND_STATUS = 3

    INCENTIVE_STATUS = (
        (CHECK_REQUESTED_STATUS, "Check Requested"),
        (PAID_STATUS, "Paid"),
        (REFUND_STATUS, "Refund"),
    )
    company = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="eep_sponsor"
    )

    customer = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="eep_recipient"
    )

    check_to_name = models.CharField(max_length=64, null=True)

    invoice_number = models.CharField(max_length=64, blank=True, null=True)

    check_requested = models.BooleanField(default=False)
    check_requested_date = models.DateField(null=True)

    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)  # User allowed to modify
    # recorded_paid_date = models.DateField(blank=True, null=True)    # The date the paid got recorded
    check_number = models.CharField(max_length=24, blank=True, null=True)

    status = models.IntegerField(choices=INCENTIVE_STATUS)

    total = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        help_text="Automatically filled in from sum tasks and expenses on save.",
    )

    comment = models.TextField(blank=True, null=True)

    slug = UUIDField(unique=True, editable=False)

    rater_incentives = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="parent_incentive_distributions",
    )

    objects = IncentiveDistributionManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Incentive Payment"
        ordering = ["invoice_number"]

    def __str__(self):
        return "{} - {}".format((self.invoice_number or self.slug)[:8], self.customer)

    def save(self, *args, **kwargs):
        # TODO: Move view logic for setting self.total to this method

        if not self.invoice_number:
            self.invoice_number = self.slug[:8]

        if self.check_number not in [None, "", "undefined"]:
            conflicting_instances = IncentiveDistribution.objects.filter(
                company=self.company, check_number=self.check_number
            )

            if self.id is not None:
                conflicting_instances = conflicting_instances.exclude(pk=self.id)

            if conflicting_instances.exists():
                # FIXME: Use a more explicit exception.  Verify that other code won't break
                # if we change this to something like ValueError.  Not enough tests yet exist.
                raise Exception(
                    "IncentiveDistribution with this company and or check number " "already exists"
                )

        # if not self.recorded_paid_date and self.paid_date:
        #     self.recorded_paid_date = now()

        super(IncentiveDistribution, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("incentive_payment:view", kwargs={"pk": self.id})

    @classmethod
    def can_be_added(cls, requesting_user):
        return requesting_user.has_perm("incentive_payment.add_incentivedistribution")

    def can_be_deleted(self, requesting_user):
        """Check that only one relationship is exists and is owned by the user's company."""
        if requesting_user.is_superuser:
            return True
        if hasattr(requesting_user, "company") and requesting_user.company.id != self.company.id:
            return False
        if (
            "incentive_payment.delete_incentivedistribution"
            not in requesting_user.get_all_permissions()
        ):
            return False
        if self.is_paid:
            return False
        return True

    def can_be_edited(self, requesting_user):
        """Check that only one relationship is exists and is owned by the user's company."""
        if hasattr(requesting_user, "company") and requesting_user.company.id != self.company.id:
            return False
        if (
            "incentive_payment.change_incentivedistribution"
            not in requesting_user.get_all_permissions()
        ):
            return False
        return True

    def total_cost(self):
        """Returns the sum of IPPItem costs if the status is not "Refund" """
        if self.status != self.REFUND_STATUS:
            return self.ippitem_set.aggregate(total=Sum("cost"))["total"]


class IPPItem(models.Model):
    """This represents a line item on an Incentive Payment"""

    home_status = models.ForeignKey("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    incentive_distribution = models.ForeignKey("IncentiveDistribution", on_delete=models.CASCADE)
    cost = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    objects = IPPItemManager()

    class Meta:
        verbose_name = "Incentive Item"
        ordering = ["home_status__home"]

    def __str__(self):
        return self.home_status.home.get_home_address_display()

    def get_absolute_url(self):
        return reverse("incentive_payment:view", kwargs={"pk": self.incentive_distribution.id})
