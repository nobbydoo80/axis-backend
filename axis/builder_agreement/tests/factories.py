"""factories.py: factory_boy classes for builder_agreement app."""


import datetime
import logging
import re

from django.core.files.uploadedfile import SimpleUploadedFile

from axis.core.utils import random_sequence, random_digits
from axis.builder_agreement.models import BuilderAgreement

__author__ = "Autumn Valenta"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def builder_agreement_factory(**kwargs):
    from axis.company.tests.factories import builder_organization_factory

    """A builder agreement factory.  get_or_create based on the field 'name', 'builder_org'."""

    company = kwargs.pop("company", None)
    builder_org = kwargs.pop("builder_org", None)
    eep_programs = kwargs.pop("eep_programs", [])
    if "eep_program" in kwargs:
        eep_programs.append(kwargs.pop("eep_program"))
    documents = kwargs.pop("documents", [])
    document = kwargs.pop("document", None)

    kwrgs = {
        "subdivision": None,
        "total_lots": random_digits(2),
        "start_date": datetime.date.today(),
        "expire_date": datetime.date.today() + datetime.timedelta(weeks=52),
        "comment": f"{random_sequence(4)} comment",
        "lots_paid": 1,
    }
    if not company:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwrgs["company"] = builder_organization_factory(**c_kwrgs)
    else:
        kwrgs["company"] = company

    if not builder_org:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("builder_org__"):
                c_kwrgs[re.sub(r"builder_org__", "", k)] = kwargs.pop(k)
        kwrgs["builder_org"] = builder_organization_factory(**c_kwrgs)
    else:
        kwrgs["builder_org"] = builder_org

    if not document:
        content = f"builder_agreement {random_sequence(4)}".encode("utf-8")
        kwrgs["document"] = SimpleUploadedFile(
            f"builder_agreement_{random_sequence(4)}.doc", content
        )
    else:
        kwrgs["document"] = document

    kwrgs.update(kwargs)
    company = kwrgs.pop("company")
    builder_org = kwrgs.pop("builder_org")
    subdivision = kwrgs.pop("subdivision")

    agreement, create = BuilderAgreement.objects.get_or_create(
        company=company, builder_org=builder_org, subdivision=subdivision, defaults=kwrgs
    )
    if create:
        if eep_programs and isinstance(eep_programs, list):
            agreement.eep_programs.add(*eep_programs)
        elif eep_programs:
            raise TypeError("EEP Programs must be sent as a list")

        if documents and isinstance(documents, list):
            for doc in documents:
                agreement.customer_documents.create(document=doc)
        elif documents:
            raise TypeError("Documents must be sent as a list")

    return agreement
