__author__ = "Artem Hruzd"
__date__ = "02/21/2023 23:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.conf import settings
from django.db import models


class CompanyAccessQuerySet(models.QuerySet):
    def filter_by_user(self, user):
        if not user:
            return self.none()

        if not user.is_authenticated:
            return self.none()

        if not user.company:
            return self.none()

        return self.filter(company__in=user.companies.all(), user=user)


class CompanyAccess(models.Model):
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    roles = models.ManyToManyField("CompanyRole", blank=True)

    objects = CompanyAccessQuerySet.as_manager()

    class Meta:
        ordering = ("id",)
        verbose_name = "Company access"
        verbose_name_plural = "Company accesses"
        unique_together = (("company", "user"),)

    def __str__(self):
        return f"{self.company} company access for {self.user}"
