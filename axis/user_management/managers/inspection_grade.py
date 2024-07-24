"""inspection_grade.py: """

__author__ = "Artem Hruzd"
__date__ = "02/27/2020 17:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.db.models import Q
from django.db.models.query import QuerySet

from axis.company.models import Company
from axis.core.managers.utils import queryset_user_is_authenticated

customer_hirl_app = apps.get_app_config("customer_hirl")


class InspectionGradeQuerySet(QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            available_companies = Company.objects.filter_by_user(user)
            return self.filter(
                Q(user__company__in=available_companies) | Q(user__company=user.company)
            )
        return self.filter(Q(user=user) | Q(user__company=user.company))
