"""home.standard_disclosure_settings.py: """


import logging

from django.db import models
from django.forms.models import model_to_dict

from axis.home.managers import StandardDisclosureSettingsQuerySet

__author__ = "Artem Hruzd"
__date__ = "06/26/2019 18:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

log = logging.getLogger(__name__)


class StandardDisclosureSettings(models.Model):
    RATER_RESPONSIBILITY_NONE = "none"
    RATER_RESPONSIBILITY_SELLER = "seller"
    RATER_RESPONSIBILITY_MORTGAGOR = "mortgagor"
    RATER_RESPONSIBILITY_EMPLOYEE = "employee"

    RATER_RESPONSIBILITY_CHOICES = (
        (RATER_RESPONSIBILITY_NONE, "None"),
        (RATER_RESPONSIBILITY_SELLER, "Seller of home or agent"),
        (RATER_RESPONSIBILITY_MORTGAGOR, "Mortgagor for some portion of payments"),
        (RATER_RESPONSIBILITY_EMPLOYEE, "An employee or contractor for utility"),
    )

    owner = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="ownedstandarddisclosuresettings_set",
    )

    # Exactly one of these three FKs must be set
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    subdivision = models.ForeignKey(
        "subdivision.Subdivision", on_delete=models.CASCADE, blank=True, null=True
    )
    home_status = models.ForeignKey(
        "EEPProgramHomeStatus", on_delete=models.CASCADE, blank=True, null=True
    )

    # Section 1
    _nullableboolean_choices = (
        (None, "Use general setting"),
        (False, "No"),
        (True, "Yes"),
    )
    rater_receives_fee = models.BooleanField(
        "Rater or employer is receiving " "a fee for rating this home",
        null=True,
        default=None,
        choices=_nullableboolean_choices,
    )

    # Section 2
    service_mechanical_design = models.BooleanField(
        "Mechanical system design", null=True, default=None, choices=_nullableboolean_choices
    )
    service_moisture_consulting = models.BooleanField(
        "Moisture control or indoor " "air quality consulting",
        null=True,
        default=None,
        choices=_nullableboolean_choices,
    )
    service_performance_testing = models.BooleanField(
        "Performance testing and/or " "commissioning other than required " "for the rating itself",
        null=True,
        default=None,
        choices=_nullableboolean_choices,
    )
    service_training = models.BooleanField(
        "Training for sales or " "construction personnel",
        null=True,
        default=None,
        choices=_nullableboolean_choices,
    )
    service_other = models.CharField("Other (specify)", max_length=100, blank=True, null=True)

    # Section 3
    rater_responsibility = models.CharField(
        "Rater or employer is",
        max_length=10,
        blank=True,
        null=True,
        choices=RATER_RESPONSIBILITY_CHOICES,
    )

    # Section 4
    _section_4_choices = (
        ("none", "None"),
        ("rater_installed", "Rater installed in home"),
        ("employer_installed", "Employer installed in home"),
        ("rater_supplied", "Rater is supplier"),
        ("employer_supplied", "Employer is supplier"),
    )
    supplier_hvac = models.CharField(
        "HVAC", max_length=20, blank=True, null=True, choices=_section_4_choices
    )

    supplier_thermal = models.CharField(
        "Themal insulation", max_length=20, blank=True, null=True, choices=_section_4_choices
    )

    supplier_sealing = models.CharField(
        "Air sealing of envelope or duct",
        max_length=20,
        blank=True,
        null=True,
        choices=_section_4_choices,
    )

    supplier_windows = models.CharField(
        "Windows or shades", max_length=20, blank=True, null=True, choices=_section_4_choices
    )

    supplier_appliances = models.CharField(
        "Appliances", max_length=20, blank=True, null=True, choices=_section_4_choices
    )

    supplier_construction = models.CharField(
        "Builder, developer, construction contractor, etc",
        max_length=20,
        blank=True,
        null=True,
        choices=_section_4_choices,
    )

    supplier_other = models.CharField(
        "Other", max_length=20, blank=True, null=True, choices=_section_4_choices
    )

    supplier_other_specify = models.CharField(
        "Other (specify)", max_length=100, blank=True, null=True
    )

    # Section 5
    verified = models.BooleanField(
        "Is sampled", null=True, default=None, choices=_nullableboolean_choices
    )

    objects = StandardDisclosureSettingsQuerySet.as_manager()

    HEADERS = {
        "service_mechanical_design": "Rater or employer is a supplier or installer:",
        "rater_responsibility": "The Rater or Rater's employer is involved in the real "
        "estate transaction, financing of the home, or "
        "utility servicing this home:",
        "supplier_hvac": "Rater or employer is a supplier or installer:",
        "verified": "Home has been verified under the provisions of Chapter 6, Section 603 "
        "“Technical Requirements for Sampling” of the Mortgage Industry National "
        "Home Energy Rating Standard:",
    }

    def save(self, *args, **kwargs):
        # TODO: This should be move to .clean() method instead
        # https://docs.djangoproject.com/en/1.11/ref/models/instances/#django.db.models.Model.clean
        if not any((self.company, self.subdivision, self.home_status)):
            raise ValueError("Need one of 'company', 'subdivision', 'home_status' set.")
        if len(list(filter(None, [self.company, self.subdivision, self.home_status]))) > 1:
            raise ValueError("Need only one of 'company', 'subdivision', 'home_status' set.")
        super(StandardDisclosureSettings, self).save(*args, **kwargs)

    def as_dict(self, raw_values=True, display_values=False):
        raw = model_to_dict(self)
        display = {}

        if display_values:
            for k in raw:
                if hasattr(self, "get_%s_display" % k):
                    if self.company and raw[k] is None:
                        display[k] = "Not set"
                    else:
                        display[k] = getattr(self, "get_%s_display" % k)()

        data = {}
        if raw_values:
            data.update(raw)
        if display_values:
            suffix = ""
            if raw_values and display_values:
                suffix = "_display"
            data.update({(k + suffix): v for k, v in display.items()})
        return data
