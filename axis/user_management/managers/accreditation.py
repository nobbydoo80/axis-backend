"""managers.py: """

__author__ = "Artem Hruzd"
__date__ = "12/27/2019 11:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.db import models
from django.db.models import fields, Case, When, Q
from django.db.models.expressions import RawSQL, F
from axis.core.managers.utils import queryset_user_is_authenticated


class AccreditationQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self.filter(Q(trainee__company=user.company) | Q(approver__company=user.company))

    def annotate_expiration_date(self):
        """Allow to filter queryset by expiration date based on Accreditation Cycle"""
        return self.annotate(
            expiration_date=Case(
                When(
                    manual_expiration_date__isnull=False,
                    then=F("manual_expiration_date"),
                ),
                When(
                    accreditation_cycle=self.model.ANNUAL_ACCREDITATION_CYCLE,
                    then=RawSQL("DATE_ADD(date_last, INTERVAL %s YEAR)", params=(1,)),
                ),
                When(
                    accreditation_cycle=self.model.EVERY_2_YEARS_ACCREDITATION_CYCLE,
                    then=RawSQL("DATE_ADD(date_last, INTERVAL %s YEAR)", params=(2,)),
                ),
                When(
                    accreditation_cycle=self.model.EVERY_3_YEARS_ACCREDITATION_CYCLE,
                    then=RawSQL("DATE_ADD(date_last, INTERVAL %s YEAR)", params=(3,)),
                ),
                When(
                    accreditation_cycle=self.model.EVERY_4_YEARS_ACCREDITATION_CYCLE,
                    then=RawSQL("DATE_ADD(date_last, INTERVAL %s YEAR)", params=(4,)),
                ),
                output_field=fields.DateField(),
            )
        )


class AccreditationManager(models.Manager):
    def get_queryset(self):
        return AccreditationQuerySet(self.model, using=self._db)

    def filter_by_user(self, user, *args, **kwargs):
        return self.get_queryset().filter_by_user(user, *args, **kwargs)

    def annotate_expiration_date(self):
        return self.get_queryset().annotate_expiration_date()
