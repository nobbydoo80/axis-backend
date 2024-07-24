"""accounts.py: Django ETO Accounts Serializer"""


import logging

from rest_framework import serializers

from axis.company.utils import can_view_or_edit_eto_account, can_edit_eto_ccb_number
from axis.customer_eto import models

__author__ = "Steven K"
__date__ = "08/29/2019 11:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class ETOAccountSerializer(serializers.ModelSerializer):
    """`ETOAccount` serializer with access restrictions.

    Restricted fields:
      - `account_number`: requesting user requires `can_view_or_edit_eto_account()`
      - `ccb_number`: requesting user requires `can_edit_eto_ccb_number()`
    """

    class Meta:
        """Meta Options"""

        model = models.ETOAccount
        fields = ("id", "account_number", "ccb_number", "company")

    def _remove_unauthorized_fields(self, validated_data):
        user = self.context["request"].user
        company_type = self.context["company_type"]
        if not can_view_or_edit_eto_account(user, company_type):
            del validated_data["account_number"]
        if not can_edit_eto_ccb_number(user, company_type):
            del validated_data["ccb_number"]

    def create(self, validated_data):
        """Create"""
        self._remove_unauthorized_fields(validated_data)
        return super(ETOAccountSerializer, self).create(validated_data)

    def updated(self, instance, validated_data):
        """Updated - Do we even use this??"""
        self._remove_unauthorized_fields(validated_data)
        return super(ETOAccountSerializer, self).updated(instance, validated_data)
