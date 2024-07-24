"""company_role.py: """

__author__ = "Artem Hruzd"
__date__ = "02/22/2023 00:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models

from axis.core.managers.utils import queryset_user_is_authenticated


class CompanyRoleQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self


class CompanyRole(models.Model):
    IS_COMPANY_ADMIN = "is_company_admin"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255)

    objects = CompanyRoleQuerySet.as_manager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"Company Role - {self.name}"
