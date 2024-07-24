"""managers.py: Django scheduling"""


from collections import namedtuple

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from axis.company.models import Company

__author__ = "Gaurav Kapoor"
__date__ = "6/25/12 9:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Gaurav Kapoor",
    "Steven Klass",
]

from axis.core.managers.utils import queryset_user_is_authenticated


class ConstructionStageManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.filter(Q(is_public=True) | Q(owner=company), **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def available_stages(self, company):
        return self.filter(Q(owner=company) | Q(is_public=True)).all().order_by("order")


class ConstructionStatusManager(models.Manager):
    def get_current_status_values_for_home(self, home, company_ids=None):
        kwargs = {"home": home}
        if company_ids:
            kwargs["company_id__in"] = company_ids
        vals = self.filter(**kwargs).values_list(
            "id",
            "company_id",
            "company__name",
            "stage__name",
            "stage_id",
            "stage__order",
            "home_id",
            "start_date",
        )
        obj = namedtuple(
            "LatestStatusByCompanyId",
            [
                "id",
                "company_id",
                "company_name",
                "home_id",
                "stage",
                "stage_id",
                "stage_order",
                "start_date",
            ],
        )
        data = {}
        for cs_id, co_id, co_name, stage, stage_id, stage_order, h_id, start in vals:
            if co_id not in data.keys():
                data[co_id] = obj(cs_id, co_id, co_name, h_id, stage, stage_id, stage_order, start)
                continue
            if stage_order >= data[co_id].stage_order and start >= data[co_id].start_date:
                data[co_id] = obj(cs_id, co_id, co_name, h_id, stage, stage_id, stage_order, start)
        return sorted(data.values(), key=lambda x: x.id)

    def get_current_status_for_home(self, company, home):
        """This requires the stages be ordered correctly - first by stage__priority
        then reverse pk to deal with re-inspections"""
        statuses = self.filter(home=home, company=company, start_date__lte=now()).order_by(
            "stage__order", "-pk"
        )
        if not statuses.count():
            return None
        else:
            return statuses.reverse()[0]

    def get_next_status_for_home(self, user, home):
        """This requires the stages be ordered correctly - first by stage__priority
        then reverse pk to deal with re-inspections"""
        from axis.scheduling.models import ConstructionStage

        current_stages = self.get_current_status_values_for_home(home, [user.company.id])
        current_stage = next(
            (x for x in current_stages if x.company_name == user.company.name), None
        )
        stages = list(ConstructionStage.objects.filter_by_company(company=user.company))
        if current_stage is None:
            return stages[0]
        current = next((x for x in stages if x.id == current_stage.stage_id))
        try:
            next_stage = stages[stages.index(current) + 1]
            statuses = self.filter(home=home, company=user.company, stage=next_stage)
            if not statuses.count():
                return None
            else:
                statuses = statuses.reverse()
            if statuses[0] != current:
                return statuses[0]
            if statuses.count() > 1:
                return statuses[1]
            return None
        except IndexError:
            pass

        return None


class TaskTypeQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self.filter(Q(company=user.company) | Q(company=None))


class TaskTypeManager(models.Manager):
    def get_queryset(self):
        return TaskTypeQuerySet(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user=user)


class TaskQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        """
                    | Public | Private
        ------------|--------|---------
        Assigner    |  Yes   |  Yes
        Assignee    |  Yes   |  Yes
        Related     |  Yes   |  No
        Super       |  Yes   |  Yes
        Random      |  No   |  No
        """
        qs = self._filter_private_by_company(user.company) | self._filter_public_by_company(
            user.company
        )
        return qs.distinct()

    def _filter_private_by_company(self, company):
        return self.filter(Q(assigner__company=company) | Q(assignees__company=company))

    def _filter_public_by_company(self, company):
        return self.filter(home__relationships__company=company, is_public=True)


class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user=user)
