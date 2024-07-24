"""filters.py: """

import django_filters

from django.apps import apps
from django.utils import timezone

from axis.customer_hirl.models import VerifierAgreement

__author__ = "Artem Hruzd"
__date__ = "11/11/2020 15:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

customer_hirl_app = apps.get_app_config("customer_hirl")


class VerifierAgreementExpirationDateRangeFilter(django_filters.DateRangeFilter):
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


class VerifierAgreementFilter(django_filters.FilterSet):
    expiration_date = VerifierAgreementExpirationDateRangeFilter(
        field_name="agreement_expiration_date"
    )

    class Meta:
        model = VerifierAgreement
        fields = ["state", "verifier__company"]

    @property
    def qs(self):
        queryset = super(VerifierAgreementFilter, self).qs
        queryset = queryset.filter(verifier__is_active=True)
        if self.request.user.is_superuser or (
            self.request.user and self.request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
        ):
            return queryset
        return queryset.filter(verifier__company=self.request.user.company)
