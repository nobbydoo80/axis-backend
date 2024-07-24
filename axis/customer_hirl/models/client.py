"""client.py: """

__author__ = "Artem Hruzd"
__date__ = "05/03/2022 19:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models


class HIRLCompanyClient(models.Model):
    company = models.OneToOneField("company.Company", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = "HI Company Client"
        verbose_name_plural = "HI Company Client"

    def __str__(self):
        return f"HI Client Company {self.id}"
