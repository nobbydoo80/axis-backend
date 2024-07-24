"""managers.py: Django core"""

__author__ = "Steven Klass"
__date__ = "2/2/13 7:45 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models, OperationalError
from django.db.models import Q, Count, Value
from django.db.models.functions import Concat

from axis.company.models import Company
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import UserManager as AuthUserManager

from axis.core.managers.utils import queryset_user_is_authenticated

customer_hirl_app = apps.get_app_config("customer_hirl")

log = logging.getLogger(__name__)


class UserQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        if not user.is_superuser:
            companies = Company.objects.filter_by_company(company=user.company, include_self=True)
            return self.filter(company__in=companies)
        return self

    def only_active(self):
        """
        Filter only active and approved users
        :return: queryset
        """
        return self.filter(is_active=True, is_approved=True)

    def common_annotations(self):
        from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
        from axis.user_management.models import Accreditation

        return self.annotate(
            active_customer_hirl_verifier_agreements_count=Count(
                "customer_hirl_enrolled_verifier_agreements",
                filter=Q(
                    customer_hirl_enrolled_verifier_agreements__state=VerifierAgreementStates.COUNTERSIGNED
                ),
                distinct=True,
            ),
            customer_hirl_project_accreditations_count=Count(
                "accreditations",
                filter=~Q(accreditations__state=Accreditation.INACTIVE_STATE)
                & Q(
                    accreditations__name__in=[
                        Accreditation.NGBS_2020_NAME,
                        Accreditation.NGBS_2015_NAME,
                    ]
                ),
                distinct=True,
            ),
        )

    def verify_rater_of_record_for_company(self, rater_of_record, company, log=None):
        log = log if log else logging.getLogger(__name__)
        str_rater_of_record = f"{rater_of_record}"
        if str_rater_of_record.isnumeric():
            users = self.filter(Q(rater_id=rater_of_record) | Q(id=rater_of_record))
            if users.count() != 1:
                log.warning(
                    f"Could not find Rater of Record with RESNET RTIN or Axis username "
                    f"{rater_of_record!r} working for {company}"
                )
                return

        else:
            users = self.annotate(full_name=Concat("first_name", Value(" "), "last_name")).filter(
                Q(full_name__iexact=rater_of_record)
                | Q(first_name__iexact=rater_of_record)
                | Q(last_name__iexact=rater_of_record)
                | Q(username=rater_of_record)
            )
            if users.count() != 1:
                log.warning(
                    f"Could not find Rater of Record name or username of "
                    f"{rater_of_record!r} working for {company}"
                )
                return
        user = users.get()
        log.info(f"Using {user} as rater of record {rater_of_record}")
        return user


class UserManager(AuthUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user=user)

    def update_users_for_company(self, users, admins, company):
        """Updates a ``company``'s users and admins to match the provided lists of such."""

        # User removals and additions
        for user in self.filter(company=company):
            if user not in users:
                user.company = None
                user.is_company_admin = False
                user.save()
        for user in users:
            if user.company_id != company.id:
                user.company_id = company.id
                user.save()

        # Admin removals and additions
        for user in self.filter(company=company, is_company_admin=True):
            if user not in admins:
                user.is_company_admin = False
                user.save()
        for user in admins:
            if user.is_company_admin is False:
                user.is_company_admin = True
                user.save()

    def verify_rater_of_record_for_company(self, rater_of_record, company, log=None):
        return self.get_queryset().verify_rater_of_record_for_company(rater_of_record, company, log)


class RecentlyViewedManager(models.Manager):
    def view(self, instance, by):
        """
        :param instance: Object with ID
        :param by: request User
        :return: Object and created flag
        """
        if not instance.pk:
            return None, False
        if not by.is_authenticated:
            return None, False
        try:
            return self.update_or_create(
                user=by,
                object_id=instance.pk,
                content_type=ContentType.objects.get_for_model(instance),
            )
        except OperationalError as err:
            # 1213, Deadlock found when trying to get lock; try restarting transaction
            # Because this isn't a critical thing we can allow this to pass through.
            if "Deadlock found" not in str(err):
                raise
            msg = (
                f"Deadlock found updating RecentlyViewed for {instance} ({instance.id}) "
                f"for user {by} ({by.id}) skipping."
            )
            log.warning(msg, exc_info=True)
            return None, False
        except MultipleObjectsReturned:
            # This happens when a merge models occurs
            primary = self.filter(
                user=by,
                object_id=instance.pk,
                content_type=ContentType.objects.get_for_model(instance),
            ).first()
            self.filter(
                user=by,
                object_id=instance.pk,
                content_type=ContentType.objects.get_for_model(instance),
            ).exclude(id=primary.pk).delete()
            return self.view(instance, by)


class AxisFlatPageQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        from axis.company.models import Company

        if (
            user.company.company_type == Company.RATER_COMPANY_TYPE
            and user.company.is_sponsored_by_customer_hirl()
        ):
            return self.filter(url__icontains=customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL)

        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return self.filter(
                Q(url__icontains=customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL)
                | Q(url=customer_hirl_app.BUILDER_CENTRAL_PAGE_URL)
            )

        return self.none()
