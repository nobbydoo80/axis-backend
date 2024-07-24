"""permissions.py: """

from rest_framework.permissions import BasePermission
from axis.company.models import Company

__author__ = "Rajesh Pethe"
__date__ = "08/31/2020 18:21:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


class APSCompanyMemberPermission(BasePermission):
    """Allows access only to APS company members"""

    def has_permission(self, request, view):
        return (
            request.user.company
            and request.user.company.company_type == Company.UTILITY_COMPANY_TYPE
            and request.user.company.slug == "aps"
        )
