"""training.py: """


from django.db.models import Q
from django.db.models.query import QuerySet

__author__ = "Artem Hruzd"
__date__ = "02/27/2020 17:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingQuerySet(QuerySet):
    def filter_by_user(self, user, *args, **kwargs):
        if not user.company:
            return self.none()
        if user.is_superuser:
            return self.filter(*args, **kwargs)
        return self.filter(Q(trainee=user) | Q(trainingstatus__company=user.company)).filter(
            *args, **kwargs
        )
