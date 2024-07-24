"""coi_document.py: """

__author__ = "Artem Hruzd"
__date__ = "10/12/2020 21:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.db import models
from django.db.models import Q
from django.utils import timezone
from axis.company.models import Company
from axis.core.managers.utils import queryset_user_is_authenticated

customer_hirl_app = apps.get_app_config("customer_hirl")


class COIDocumentQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return self
        if user.company.company_type == Company.RATER_COMPANY_TYPE:
            available_companies = Company.objects.filter_by_user(user)
            return self.filter(Q(company__in=available_companies) | Q(company=user.company))
        return self.filter(company=user.company)

    def active(self):
        return self.filter(expiration_date__gt=timezone.now())

    def expired(self):
        return self.filter(expiration_date__lte=timezone.now())
