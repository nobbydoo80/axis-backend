"""project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2021 12:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.db import models
from axis.company.models import Company
from axis.core.managers.utils import queryset_user_is_authenticated

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectRegistrationQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return self
        # Allow builders/developer/architects/owners
        # view projects in which they have been selected
        if user.company and user.company.company_type == Company.BUILDER_COMPANY_TYPE:
            return self.filter(builder_organization=user.company)
        if user.company and user.company.company_type == Company.ARCHITECT_COMPANY_TYPE:
            return self.filter(architect_organization=user.company)
        if user.company and user.company.company_type == Company.DEVELOPER_COMPANY_TYPE:
            return self.filter(developer_organization=user.company)
        if user.company and user.company.company_type == Company.COMMUNITY_OWNER_COMPANY_TYPE:
            return self.filter(community_owner_organization=user.company)
        return self.filter(registration_user__company=user.company).distinct()
