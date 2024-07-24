"""factories.py """

__author__ = "Artem Hruzd"
__date__ = "6/10/19 11:00 AM"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]

import random
import re

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from axis.core.tests.factories import basic_user_factory, SET_NULL
from axis.core.utils import random_sequence
from axis.home.tests.factories import custom_home_factory
from axis.scheduling.models import Task, TaskType


def task_type_factory(content_type, **kwargs):
    kwrgs = {"company": None, "name": random_sequence(4), "content_type": content_type}

    kwrgs.update(kwargs)
    task_type = TaskType.objects.create(**kwrgs)
    return task_type


def task_factory(**kwargs):
    assignees = kwargs.pop("assignees")

    task_type = kwargs.pop("task_type", None)

    home = kwargs.pop("home", None)

    content_type = ContentType.objects.first()

    if home is SET_NULL:
        kwargs["home"] = None
    else:
        if not home:
            c_kwrgs = {}
            for k, v in list(kwargs.items()):
                if k.startswith("home__"):
                    c_kwrgs[re.sub(r"home__", "", k)] = kwargs.pop(k)
            kwargs["home"] = custom_home_factory(**c_kwrgs)
        else:
            kwargs["home"] = home

        content_type = ContentType.objects.get_for_model(kwargs["home"]._meta.model)

    if not task_type:
        c_kwrgs = {
            "content_type": content_type,
        }
        for k, v in list(kwargs.items()):
            if k.startswith("task_type__"):
                c_kwrgs[re.sub(r"task_type__", "", k)] = kwargs.pop(k)
        task_type = task_type_factory(**c_kwrgs)

    kwrgs = {
        "task_type": task_type,
        "assigner": basic_user_factory(),
        "datetime": timezone.now(),
        "status": random.choice(Task.TASK_STATUS_CHOICES)[0],
        "status_changed_at": timezone.now(),
        "status_approver": basic_user_factory(),
        "status_annotation": random_sequence(4),
        "approval_state": Task.APPROVAL_STATE_NEW,
    }
    kwrgs.update(kwargs)
    task = Task.objects.create(**kwrgs)

    for assign_user in assignees:
        task.assignees.add(assign_user)
    return task
