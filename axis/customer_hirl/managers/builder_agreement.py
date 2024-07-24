"""builder_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "10/10/2021 11:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.db import models
from django.db.models import Count, Q, Max, F
from django.utils import timezone

from axis.company.models import Company
from axis.core.managers.utils import queryset_user_is_authenticated

customer_hirl_app = apps.get_app_config("customer_hirl")


class BuilderAgreementQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return self

        if user.company.company_type == Company.RATER_COMPANY_TYPE:
            companies = Company.objects.filter_by_user(user=user)
            return self.filter(company__in=companies)

        return self.filter(
            Q(company=user.company)
            | Q(created_by__company=user.company)
            | Q(initiator__company=user.company)
        )

    def annotate_company_coi_info(self, *args, **kwargs):
        return self.annotate(
            active_coi_document_count=Count(
                "company__coi_documents",
                filter=Q(company__coi_documents__expiration_date__gt=timezone.now()),
            ),
            expired_coi_document_count=Count(
                "company__coi_documents",
                filter=Q(company__coi_documents__expiration_date__lte=timezone.now()),
            ),
            coi_document_count=F("active_coi_document_count") + F("expired_coi_document_count"),
            coi_document_max_start_date=Max("company__coi_documents__start_date"),
            coi_document_max_expiration_date=Max("company__coi_documents__expiration_date"),
        )
