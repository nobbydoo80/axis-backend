"""project.py: Manager for HIRLProject model"""

__author__ = "Artem Hruzd"
__date__ = "12/07/2020 21:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.db import models
from django.db.models import Sum, F, Max, Subquery, OuterRef, DecimalField, When, Case
from django.db.models.functions import Coalesce

from axis.company.models import Company
from axis.core.managers.utils import queryset_user_is_authenticated
from axis.invoicing.models import InvoiceItemTransaction, InvoiceItem

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return self
        # Allow builders/developer/architects/owners
        # view projects in which they have been selected
        if user.company and user.company.company_type == Company.BUILDER_COMPANY_TYPE:
            return self.filter(registration__builder_organization=user.company)
        if user.company and user.company.company_type == Company.ARCHITECT_COMPANY_TYPE:
            return self.filter(registration__architect_organization=user.company)
        if user.company and user.company.company_type == Company.DEVELOPER_COMPANY_TYPE:
            return self.filter(registration__developer_organization=user.company)
        if user.company and user.company.company_type == Company.COMMUNITY_OWNER_COMPANY_TYPE:
            return self.filter(registration__community_owner_organization=user.company)
        return self.filter(registration__registration_user__company=user.company).distinct()

    def annotate_fee_balance(self):
        """
        Attach fee fee_total fee_total_paid fee_current_balance attributes. Calculations based
        on InvoiceItem to each project
        :return: QuerySet
        """
        # https://stackoverflow.com/a/45803258/1786016
        return self.annotate(
            fee_total=Coalesce(
                Subquery(
                    InvoiceItem.objects.filter(
                        group__home_status__customer_hirl_project=OuterRef("pk")
                    )
                    .values("group__home_status__customer_hirl_project")
                    .order_by("group__home_status__customer_hirl_project")
                    .annotate(
                        fee_total=Sum("cost"),
                    )
                    .values("fee_total")[:1]
                ),
                0,
                output_field=DecimalField(),
            ),
            fee_total_paid=Coalesce(
                Subquery(
                    InvoiceItemTransaction.objects.filter(
                        item__group__home_status__customer_hirl_project=OuterRef("pk")
                    )
                    .values("item__group__home_status__customer_hirl_project")
                    .order_by("item__group__home_status__customer_hirl_project")
                    .annotate(
                        fee_total_paid=Sum("amount"),
                    )
                    .values("fee_total_paid")[:1]
                ),
                0,
                output_field=DecimalField(),
            ),
            fee_current_balance=Coalesce(
                F("fee_total") - F("fee_total_paid"), 0, output_field=DecimalField()
            ),
        )

    def annotate_billing_info(self):
        """
        Attach billing_state that is using for Green energy exports
        and fields from annotate_fee_balance method
        :return: QuerySet
        """
        return self.annotate_fee_balance().annotate(
            most_recent_payment_received=Max(
                "home_status__invoiceitemgroup__invoiceitem__transactions__created_at"
            ),
        )

    def annotate_client_ca_status(self):
        """
        Customer HIRL specific: Annotate current Project Client Agreement status.
        By default use Builder Organization CA state
        :return:
        """
        from axis.customer_hirl.models import HIRLProjectRegistration

        return self.annotate(
            client_ca_status=Case(
                When(
                    registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
                    then=F(
                        "registration__builder_organization__customer_hirl_enrolled_agreements__state"
                    ),
                ),
                When(
                    registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
                    then=F(
                        "registration__architect_organization__customer_hirl_enrolled_agreements__state"
                    ),
                ),
                When(
                    registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
                    then=F(
                        "registration__developer_organization__customer_hirl_enrolled_agreements__state"
                    ),
                ),
                When(
                    registration__project_client=HIRLProjectRegistration.PROJECT_CLIENT_OWNER,
                    then=F(
                        "registration__community_owner_organization__customer_hirl_enrolled_agreements__state"
                    ),
                ),
                default=F(
                    "registration__builder_organization__customer_hirl_enrolled_agreements__state"
                ),
            )
        )
