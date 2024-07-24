"""filters.py: """

import django_filters
from django.apps import apps
from django.utils import timezone

from axis.customer_hirl.models import BuilderAgreement

__author__ = "Artem Hruzd"
__date__ = "11/10/2020 22:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]
customer_hirl_app = apps.get_app_config("customer_hirl")


class BuilderAgreementExpirationDateRangeFilter(django_filters.DateRangeFilter):
    choices = [
        ("", "Any date"),
        ("1", "Expire in 30 Days"),
        ("2", "Expire in 60 Days"),
        ("3", "Expire in 90 Days"),
        ("4", "Expire in more than 90 days"),
    ]
    filters = {
        "": lambda qs, name: qs,
        "1": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=30)),
            }
        ),
        "2": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=60)),
            }
        ),
        "3": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=90)),
            }
        ),
        "4": lambda qs, name: qs.filter(
            **{
                f"{name}__gt": timezone.now() + timezone.timedelta(days=90),
            }
        ),
    }


class BuilderAgreementInsuranceExpirationDateRangeFilter(django_filters.DateRangeFilter):
    choices = [
        ("", "Any date"),
        ("1", "Expire in 30 Days"),
        ("2", "Expire in 60 Days"),
        ("3", "Expire in 90 Days"),
        ("4", "Expire in more than 90 days"),
    ]
    filters = {
        "": lambda qs, name: qs,
        "1": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=30)),
            }
        ),
        "2": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=60)),
            }
        ),
        "3": lambda qs, name: qs.filter(
            **{
                f"{name}__range": (timezone.now(), timezone.now() + timezone.timedelta(days=90)),
            }
        ),
        "4": lambda qs, name: qs.filter(
            **{
                f"{name}__gt": timezone.now() + timezone.timedelta(days=90),
            }
        ),
    }


class BuilderAgreementFilter(django_filters.FilterSet):
    agreement_expiration_date = BuilderAgreementExpirationDateRangeFilter(
        field_name="agreement_expiration_date"
    )
    agreement_insurance_expiration_date = BuilderAgreementInsuranceExpirationDateRangeFilter(
        field_name="coi_document_max_expiration_date"
    )

    class Meta:
        model = BuilderAgreement
        fields = ["state", "company"]

    @property
    def qs(self):
        if not hasattr(self, "_qs"):
            qs = (
                self.queryset.all()
                .filter_by_user(user=self.request.user)
                .annotate_company_coi_info()
            )
            if self.is_bound:
                # ensure form validation before filtering
                self.errors
                qs = self.filter_queryset(qs)
            self._qs = qs
        return self._qs
