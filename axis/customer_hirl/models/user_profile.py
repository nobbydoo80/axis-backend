"""user_profile.py: """

from django.contrib.auth import get_user_model
from django.db import models

__author__ = "Artem Hruzd"
__date__ = "10/16/2020 19:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


User = get_user_model()


class HIRLUserProfile(models.Model):
    """ "
    customer HIRL specific fields
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_qa_designee = models.BooleanField(verbose_name="QA Designee", default=False)

    class Meta:
        verbose_name = "HI User Settings"
        verbose_name_plural = "HI User Settings"

    def __str__(self):
        return f"{self.user}"
