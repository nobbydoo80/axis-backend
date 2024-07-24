"""models.py: Django resnet"""


import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import SET_NULL
from phonenumber_field.modelfields import PhoneNumberField

from axis.company.validators import validate_provider_id
from .managers import RESNETCompanyManager, RESNETContactManager

__author__ = "Steven Klass"
__date__ = "7/25/14 4:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RESNETContact(models.Model):
    """A RESNET Contact bound to a RESNET Company"""

    name = models.CharField(max_length=256)
    title = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    resnet_company = models.ForeignKey(
        "RESNETCompany", on_delete=models.CASCADE, blank=True, null=True
    )

    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    objects = RESNETContactManager()

    class Meta:
        verbose_name = "RESNET Contact"

    def __str__(self):
        return self.name


class RESNETCompany(models.Model):
    """A RESNET Company as pulled from RESNET"""

    name = models.CharField(max_length=256)
    street_line1 = models.CharField(max_length=100, blank=True, null=True)
    street_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField("ZIP Code", max_length=15, blank=True, null=True)
    office_phone = PhoneNumberField(blank=True, null=True)
    office_fax = PhoneNumberField(blank=True, null=True)
    home_page = models.URLField(blank=True, null=True)

    is_rater = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    is_sampling_provider = models.BooleanField(default=False)
    is_training_provider = models.BooleanField(default=False)
    is_watersense_provider = models.BooleanField(default=False)

    certification_number = models.CharField(max_length=16, unique=True, blank=True, null=True)
    provider_id = models.CharField(
        max_length=8, validators=[validate_provider_id], blank=True, null=True
    )

    resnet_expiration = models.DateField(blank=True, null=True)
    resnet_profile_url = models.URLField(blank=True, null=True)

    company = models.OneToOneField(
        "company.Company", blank=True, null=True, on_delete=SET_NULL, related_name="resnet"
    )

    is_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    objects = RESNETCompanyManager()

    class Meta:
        verbose_name = "RESNET Company"
        verbose_name_plural = "RESNET Companies"

    def __str__(self):
        if self.provider_id:
            return "{} ({})".format(self.name, self.provider_id)
        return self.name

    def clean_provider_id(self):
        """Clean the provider ID"""
        if self.provider_id != "":
            if RESNETCompany.objects.filter(provider_id=self.provider_id):
                raise ValidationError("%s already exists in database" % self.provider_id)
        if self.provider_id == "":
            self.provider_id = None

    def clean_certification_number(self):
        """Clean the Certification Number"""
        if self.certification_number != "":
            if RESNETCompany.objects.filter(certification_number=self.certification_number):
                raise ValidationError("%s already exists in database" % self.certification_number)
        if self.certification_number == "":
            self.certification_number = None
