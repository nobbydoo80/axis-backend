import logging

from django.db import models
from django.db.models.query import QuerySet
from django.utils.timezone import now
from django.conf import settings

__author__ = "Autumn Valenta"
__date__ = "3/3/15 1:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class MessageManager(models.Manager):
    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def since(self, target_datetime, end_datetime=None):
        if target_datetime:
            return self.get_queryset().since(target_datetime, end_datetime=end_datetime)
        return self.get_queryset()

    def is_debouncing(self):
        return self.get_queryset().is_debouncing()

    def threshold(self, threshold):
        return self.get_queryset().threshold(threshold)


class MessageQuerySet(QuerySet):
    def since(self, target_datetime, end_datetime=None):
        if target_datetime:
            queryset = self.filter(date_created__gte=target_datetime)
            if end_datetime:
                queryset = queryset.filter(date_created__lte=end_datetime)
            return queryset
        return self.filter()

    def is_debouncing(self):
        debounce_started = now() - settings.MESSAGING_DUPLICATE_DEBOUNCE
        return self.filter(date_created__gte=debounce_started).exists()

    def threshold(self, threshold):
        queryset = self

        if not threshold:
            queryset = queryset.filter(id=-1)
        elif threshold == "alerts":
            # Only messages that weren't delivered via email already
            queryset = queryset.filter(date_sent=None)
        elif threshold == "emails":
            # Any messages that had an email counterpart
            queryset = queryset.exclude(date_sent=None)

        return queryset
