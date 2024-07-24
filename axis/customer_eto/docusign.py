"""tasks.py: Django customer_eto"""


import logging

from django.apps import apps

from axis.filehandling.docusign import DocuSignDeclarativeTemplate

__author__ = "Steven Klass"
__date__ = "9/17/13 11:05 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = logging.getLogger(__name__)
eto_app = apps.get_app_config("customer_eto")


class ETOBaseDocuSignDeclarativeTemplate(DocuSignDeclarativeTemplate):
    def __init__(self, user_id=None, account_id=None, **kwargs):
        super(ETOBaseDocuSignDeclarativeTemplate, self).__init__(
            user_id=eto_app.DOCUSIGN_ACCOUNT_ID,
            account_id=eto_app.DOCUSIGN_ACCOUNT_ID,
            **kwargs,
        )


class BuildingPermit(ETOBaseDocuSignDeclarativeTemplate):
    """Permit builder.  Call `build(customer_document, user=USER)`"""

    email_subject = "City Of Hillsboro: Building Permit Report Signing Required"
    email_message = """
        {company} has posted a City of Hillsboro building permit compliance report for {address}.
        Please review and sign the document at the provided link.
    """
    signers = [
        {
            "kwarg": "user",
            "page": 1,
            "coordinates": (70, 634),
            "fields": {
                "House Plan": {
                    "page": 1,
                    "coordinates": (170, 166),
                    "dimensions": (100, 38),
                    "type": "text_tabs",
                },
            },
        }
    ]


class CertificateOfOccupancy(ETOBaseDocuSignDeclarativeTemplate):
    """Occupancy builder.  Call `build(customer_document, user=USER)`"""

    email_subject = "City Of Hillsboro: Certificate Of Occupancy Report Signing Required"
    email_message = """
        {company} has posted a City of Hillsboro sustainability compliance report for {address}.
        Please review and sign the document at the provided link.
    """
    signers = [{"kwarg": "user", "page": 1, "coordinates": (370, 634)}]
