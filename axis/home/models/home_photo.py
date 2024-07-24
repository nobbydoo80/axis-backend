"""home_photo.py: """

import os
from django.db import models
from .home import Home

__author__ = "Artem Hruzd"
__date__ = "11/26/2020 19:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


def home_photo_image_upload_to(instance, filename):
    return os.path.join("homes", str(instance.home.pk), "photos", filename)


class HomePhoto(models.Model):
    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to=home_photo_image_upload_to)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Home Photo {self.file}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        One of home photos must be is_primary after save
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        is_primary_exists = (
            self.__class__.objects.filter(home=self.home, is_primary=True)
            .exclude(pk=self.pk)
            .exists()
        )

        if not self.is_primary and not is_primary_exists:
            self.is_primary = True

        if self.is_primary and is_primary_exists:
            self.__class__.objects.filter(home=self.home).update(is_primary=False)

        super(HomePhoto, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def delete(self, using=None, keep_parents=False):
        """
        One of home photos must be is_primary after delete
        :param using:
        :param keep_parents:
        :return:
        """
        is_primary_exists = (
            self.__class__.objects.filter(home=self.home, is_primary=True)
            .exclude(pk=self.pk)
            .exists()
        )

        super(HomePhoto, self).delete(using=using, keep_parents=keep_parents)

        if not is_primary_exists:
            home_photo = self.__class__.objects.filter(home=self.home, is_primary=False).first()
            if home_photo:
                home_photo.is_primary = True
                home_photo.save()
