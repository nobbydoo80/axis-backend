"""utils.py: Django customer_neea"""


import itertools
import logging
import os

from django.core import management
from django.urls import reverse

from . import messages
from .models import (
    LegacyNEEAPartner,
    LegacyNEEAHome,
    LegacyNEEAPartnerToHouse,
    LegacyNEEAAddress,
    LegacyNEEAContact,
    LegacyNEEAZipPlus,
    LegacyNEEAZipCounty,
)

__author__ = "Steven Klass"
__date__ = "10/29/12 12:41 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# These are broken up into categories, but we only care about the values
DEPRECATED_BOP_VALUES = list(
    itertools.chain(
        *(
            {
                "2011 ID/MT BOP 1": ["2011 ID/MT BOP 1"],
                "2011 ID/MT BOP 2": ["2011 ID/MT BOP 2"],
                "2011 WA BOP 1": [
                    "2011 WA BOP 1 - Ducts in Conditioned Space",
                    "2011 WA BOP 1 - Equipment Upgrade",
                    "2011 WA BOP 1 - Envelope Pathway",
                ],
                "2011 WA BOP 2": ["2011 WA BOP 2 - Zonal Electric; Propane and Oil"],
                "2012 OR BOP 1": [
                    "2012 OR BOP 1 - Ducts in Conditioned Space",
                    "2012 OR BOP 1 - Equipment Upgrade",
                    "2012 OR BOP 1 - Envelope Pathway",
                ],
                "2012 OR BOP 2": ["2012 OR BOP 2 - Zonal Electric; Propane and Oil"],
                "OPPH": ["Oregon Premium Performance Home (OPPH)"],
            }.values()
        )
    )
)

NEEA_PROGRAM_SLUGS = [
    "neea-energy-star-v3",
    "neea-energy-star-v3-performance",
    "neea-prescriptive-2015",
    "neea-performance-2015",
    "utility-incentive-v1-single-family",
    "utility-incentive-v1-multifamily",
    "neea-bpa",
]
NEEA_GENERIC_PROGRAM_SLUGS = [
    "utility-incentive-v1-single-family",
    "utility-incentive-v1-multifamily",
]

NEEA_BPA_SLUGS = [
    "neea-bpa",
    "neea-bpa-v3",
]


def dump_test_data():
    """Dumps the test data"""
    fixture = os.path.abspath("%s/fixtures/test_neea_legacy.json" % os.path.dirname(__file__))

    # Identify the items we want to keep.
    log.warning("This will take time..  Be patient")
    log.info("Pruning Homes")
    h_ids = [26221, 23499, 26423, 16760]
    for h in LegacyNEEAHome.objects.all().exclude(id__in=h_ids):
        h.delete()

    # Identify the relevant Partners..
    log.info("Pruning Partners")
    p_ids = LegacyNEEAPartnerToHouse.objects.filter(home__in=h_ids).values_list(
        "partner", flat=True
    )
    partner_ids = list(p_ids) + [3236, 2674, 1746]
    for p in LegacyNEEAPartner.objects.all().exclude(id__in=partner_ids):
        p.delete()

    # Relevant Contacts..
    log.info("Pruning Contacts")
    for c in LegacyNEEAContact.objects.all().exclude(partner_id__in=p_ids):
        c.delete()

    # Relevant Addresses
    log.info("Pruning Addresses")
    a_ids = list(LegacyNEEAHome.objects.filter(id__in=h_ids).values_list("address", flat=True))
    a_ids += list(LegacyNEEAPartner.objects.filter(id__in=p_ids).values_list("address", flat=True))
    a_ids += list(
        LegacyNEEAContact.objects.filter(partner_id__in=p_ids).values_list("address", flat=True)
    )
    for a in LegacyNEEAAddress.objects.all().exclude(id__in=a_ids):
        a.delete()

    # Relevant Addresses
    log.info("Pruning ZIP Codes")
    z_ids = LegacyNEEAAddress.objects.filter(id__in=a_ids).values_list("zip_code", flat=True)
    for c in LegacyNEEAZipCounty.objects.all().exclude(zip_code__in=z_ids):
        c.delete()
    for z in LegacyNEEAZipPlus.objects.all().exclude(zip_code__in=z_ids):
        z.delete()

    includes = ["customer_neea"]
    management.call_command(
        "dumpdata",
        *includes,
        format="json",
        indent=4,
        database="customer_neea",
        use_natural_keys=True,
        traceback=True,
        stdout=open(fixture, "w"),
    )


def send_neea_missing_relationship_message(home_status, company, neea):
    """Sends EEP Program HomeStatus company message on missing relationships"""

    message, context, recipient = None, None, None
    if home_status.eep_program.slug in NEEA_GENERIC_PROGRAM_SLUGS:
        recipient = neea
        if company.company_type == "builder":
            message = messages.NeeaUnnaprovedBuilderGenericProgramMessage()
        elif company.company_type == "hvac":
            message = messages.NeeaUnnaprovedHvacGenericProgramMessage()

        add_relationship = reverse(
            "relationship:add_id",
            kwargs={
                "model": "company",
                "app_label": "company",
                "object_id": company.id,
            },
        )

        context = {
            "company": "{}".format(company),
            "program": "{}".format(home_status.eep_program),
            "home_url": home_status.get_absolute_url(),
            "home": home_status.home.get_home_address_display(
                include_lot_number=True, include_city_state_zip=True
            ),
            "add_relationship": add_relationship,
        }

    elif home_status.eep_program.slug in NEEA_PROGRAM_SLUGS:
        recipient = home_status.company
        if company.company_type == "builder":
            message = messages.NeeaUnapprovedBuilderMessage()
            if home_status.eep_program.slug in NEEA_BPA_SLUGS:
                message = None
        elif company.company_type == "hvac":
            message = messages.NeeaUnapprovedHvacMessage()
            if home_status.eep_program.slug in NEEA_BPA_SLUGS:
                message = None
        elif company.company_type == "utility":
            message = messages.NeeaUnapprovedUtilityMessage()

        context = {
            "company": "{}".format(company),
            "program": "{}".format(home_status.eep_program),
        }

    if message:
        message.send(context=context, company=recipient)
