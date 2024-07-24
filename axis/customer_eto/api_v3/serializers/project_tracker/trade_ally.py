"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "8/21/21 13:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.customer_eto.models import ETOAccount
from .base import BaseXMLSerializer

log = logging.getLogger(__name__)


class TradeAllySerializer(BaseXMLSerializer):
    """This is the Trade Allies portion of ETO XML"""

    def to_representation_default(self, instance):
        builder = instance.home_status.home.get_builder()
        builder_eto_account = ETOAccount.objects.get(company_id=builder.id).account_number

        verifier = instance.home_status.company
        verifier_eto_account = ETOAccount.objects.get(company_id=verifier.id).account_number

        verifier_role = "VERIFIER"
        if self.context.get("project_type") == "SLE":
            verifier_role = "SOINSP"

        return [
            {
                "InternalID": builder_eto_account,
                "Associations": {
                    "Projects": {
                        "Project": {
                            "@ID": instance.home_status.id,
                            "Role": "BUILDER",
                            "Measures": {"Measure": []},
                        }
                    },
                },
            },
            {
                "InternalID": verifier_eto_account,
                "Associations": {
                    "Projects": {
                        "Project": {
                            "@ID": instance.home_status.id,
                            "Role": verifier_role,
                            "Measures": {"Measure": []},
                        }
                    },
                },
            },
        ]
