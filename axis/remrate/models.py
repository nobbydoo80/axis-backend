"""models.py: remrate models"""

import datetime
import logging

from celery.result import EagerResult
from django.db import models
from django.utils.timezone import now
from django.conf import settings

from axis.core.fields import EncryptedCharField
from .managers import RemRateUserManager
from .remrate_exe import RemRateExe, RemRateRegistrationFailure
from .tasks import validate_remrateuser

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


log = logging.getLogger(__name__)

RESERVED_USERNAMES = {"root", "sklass", "pivotal", "admin"} | {
    db["NAME"] for db in settings.DATABASES.values()
}
RESERVED_PASSWORDS = [
    "Pa55w0rd",
    "Pa55W0rd",
    "pa55w0rd",
    "pa55W0rd",
    "PA55W0RD",
    "Pa55 W0rd",
    "Pa55 w0rd",
    "pa55 w0rd",
    "pA55w0rD",
    "P@$$w0rd",
    "password",
    "pass",
]


class RemRateLog(models.Model):
    """The logfile for remrate transactions"""

    trigger = models.CharField(max_length=64)
    log = models.CharField(max_length=128)
    time = models.DateTimeField(default=datetime.datetime.now, editable=False)


class RemRateUser(models.Model):
    """This is the list of mysql usernames which are writing to aec_remrate db"""

    username = models.CharField(max_length=128, unique=True)
    password = EncryptedCharField(max_length=613, blank=True, null=True)
    company = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="remrate_user_ids"
    )
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=now, editable=False)
    last_used = models.DateTimeField("Last updated", auto_now=True)

    objects = RemRateUserManager.as_manager()

    class Meta:
        verbose_name = "REM/Rate User"
        ordering = ("username",)

    def __str__(self):
        return "{} ({})".format(self.username, self.company)

    def get_absolute_url(self):
        """Returns the edit url, since these user objects don't really use full detail views."""

    @classmethod
    def can_be_added(cls, user):
        return user.has_perm("remrate.add_remrateuser")

    def can_be_edited(self, user):
        return user.has_perm("remrate.change_remrateuser")

    def can_be_deleted(self, user):
        return user.has_perm("remrate.delete_remrateuser")


class RemRateAccount(models.Model):
    """This will actually store the RemRate account information as required in RemRate."""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    username = models.CharField(
        max_length=32, blank=True, null=True
    )  # Tools -> Web Services -> Register REM
    password = models.CharField(
        max_length=613, blank=True, null=True
    )  # Tools -> Web Services -> Register REM

    resnet_user_id = models.CharField(
        "RESNET User ID", max_length=64, blank=True, null=True
    )  # Tools -> RESNET Building Registry
    resnet_password = models.CharField(
        "RESNET Password", max_length=128, blank=True, null=True
    )  # Tools -> RESNET Building Registry

    account_type = models.CharField(max_length=32, blank=True, null=True)  # About -> Role
    expires = models.DateField(blank=True, null=True)  # About -> Expires
    export_user_account = models.ForeignKey(
        "RemRateUser", on_delete=models.CASCADE, blank=True, null=True
    )

    created_on = models.DateTimeField(default=datetime.datetime.now, editable=False)
    last_validated = models.DateTimeField(blank=True, null=True, editable=False)

    latest_notes = models.TextField(
        blank=True, null=True, editable=False
    )  # A way to report back to the user
    task_id = models.CharField(max_length=255, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = "REM/Rate Account Detail"

    def __str__(self):
        return "{} for {}".format(self._meta.verbose_name, self.company)

    def get_absolute_url(self):
        pass

    def save(self, **kwargs):
        orig = RemRateAccount.objects.get(id=self.pk) if self.pk else None
        super(RemRateAccount, self).save(**kwargs)
        if not self.is_valid() and not self.task_id:
            changed = True
            if orig:
                changed = orig.username != self.username or orig.password != self.password
            if changed and self.username and self.password:
                task = validate_remrateuser.delay(account_id=self.id)
                if not isinstance(task, EagerResult):
                    self.task_id = task
                    self.save()

    @classmethod
    def can_be_added(cls, user):
        return user.has_perm("remrate.add_remrateaccount")

    def can_be_edited(self, user):
        return user.has_perm("remrate.change_remrateaccount")

    def can_be_deleted(self, user):
        return user.has_perm("remrate.delete_remrateaccount")

    def is_valid(self):
        """Can this user run REMRate"""
        if not self.last_validated:
            return False
        elif not self.expires:
            return False
        elif self.expires < datetime.date.today():
            return False
        return True

    def validate_user(self):
        """This will fire off REMRate and validate the user"""

        remrate = RemRateExe()
        remrate.start()
        data = {"task_id": None, "last_validated": now()}
        try:
            remrate.set_user(self.username, self.password)
        except RemRateRegistrationFailure as err:
            data["expires"] = None
            data["account_type"] = None
            data["latest_notes"] = str(err)
        else:
            about = remrate.about()
            data["expires"] = about.get("expires")
            data["account_type"] = about.get("account_type")
            data["latest_notes"] = None
        remrate.exit()
        log.info("Completed validation - {}".format(data))
        return data
