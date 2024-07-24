"""App configs."""


from django.conf import settings

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


settings = getattr(settings, "CUSTOMER_HIRL", {})


# pylint: disable=invalid-name
class BuilderEnrollmentConfig(customers.ExtensionConfig):
    """NGBS Builder Enrollment platform config"""

    ENROLLMENT_ENABLED = settings.get("ENROLLMENT_ENABLED", False)

    # Configuration

    BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME = settings.get(
        "BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME", "NGBSadmin"
    )

    @property
    def enrollee_queryset(self):
        """Return the BuilderOrganization queryset of companies with enrollments."""

        from axis.company.models import Company

        return Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).filter(
            customer_hirl_enrolled_agreements__owner__slug=self.CUSTOMER_SLUG
        )
