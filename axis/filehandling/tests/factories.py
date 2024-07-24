"""factories.py: Django customer_docs factory"""


import logging
import os
import re

from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from axis.core.tests import factories as core_factories
from axis.core.utils import random_sequence
from axis.filehandling.models import CustomerDocument

__author__ = "Steven Klass"
__date__ = "06/18/2019 14:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def customer_document_factory(**kwargs):
    """A Customer Document Factory"""
    company = kwargs.pop("company", None)

    if company is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                _kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        company = core_factories.general_admin_factory(**_kwrgs).company

    document = kwargs.pop("document", None)
    if document is None or not os.path.exists(document):
        document = __file__

    document_name = kwargs.pop("document_name", os.path.basename(document))

    content_object = kwargs.pop("content_object", company)
    content_type = ContentType.objects.get_for_model(content_object)
    object_id = content_object.pk

    with open(document) as fh:
        doc, _cr = CustomerDocument.objects.get_or_create(
            content_type=content_type,
            object_id=object_id,
            company=company,
            document=File(fh, name=document_name),
            **kwargs,
        )

    return doc
