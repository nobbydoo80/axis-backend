"""permissions.py: """

from rest_framework.permissions import BasePermission

from axis.company.models import EepOrganization, Company

__author__ = "Artem Hruzd"
__date__ = "07/17/2020 12:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class NEEACompanyMemberPermission(BasePermission):
    """Allows access only to NEEA company members"""

    def has_permission(self, request, view):
        return (
            request.user.company
            and request.user.company.company_type == Company.EEP_COMPANY_TYPE
            and request.user.company.slug == "neea"
        )


class NEEACalculatorPermission(BasePermission):
    """Basic Perms for the API Endpoint"""

    def has_permission(self, request, view):
        """Does the user have perms"""
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        if request.user.company.slug == "neea":
            return True
        elif request.user.company.sponsors.filter(slug="neea").exists():
            return request.user.company.company_type in ["rater", "provider", "qa", "utility"]
