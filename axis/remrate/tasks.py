"""tasks.py: Django remrate"""


import hashlib
import json
import os

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

__author__ = "Steven Klass"
__date__ = "9/1/14 3:23 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from rest_framework.exceptions import ValidationError

logger = get_task_logger(__name__)

User = get_user_model()


@shared_task
def validate_remrateuser(account_id, **kwargs):
    from axis.remrate.models import RemRateAccount

    log = kwargs.get("log", logger)

    try:
        account = RemRateAccount.objects.get(id=account_id)
    except RemRateAccount.DoesNotExist:
        raise RemRateAccount.DoesNotExist("Is transaction management enabled - it shouldn't be.")

    results = account.validate_user()
    for k, v in results.items():
        setattr(account, k, v)
    account.save(update_fields=results.keys())
    log.info("Validated account {}".format(account), kwargs=results)


@shared_task
def get_floorplan_blg_data(floorplan_id: int):
    from axis.floorplan.models import Floorplan
    from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
    from simulation.serializers.simulation.base import SimulationSerializer

    obj = Floorplan.objects.get(id=floorplan_id)
    try:
        blg_instance = get_blg_simulation_from_floorplan(obj)
        simulation_serializer = SimulationSerializer(instance=blg_instance)
        return simulation_serializer.data
    except (ValidationError, ValueError, IOError, OSError) as err:
        return ({"error": f"Associated Floorplan or BLG File does not exist - {err}"},)
