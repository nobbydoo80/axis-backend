"""tasks.py: Django aec_remrate"""

import datetime
import logging

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.exceptions import FieldError
from django.utils.timezone import now

from .utils import TABLE_MAP, AEC_Triggers

__author__ = "Steven Klass"
__date__ = "7/20/14 8:30 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
logger = get_task_logger(__name__)

# These tables all get looked at when an export happens.
LMAX_TABLES = {
    "AshpType": "lASTASTNo",
    "BuildRun": "lBldgRunNo",
    "Building": "lBldgNo",
    "CeilType": "lCTCTNo",
    "ClgType": "lCETCETNo",
    "CompType": "lTCTTCTTNo",
    "DfhpType": "lDFTDFTNo",
    "DhwDistrib": "lDhwDistNo",
    "DhwType": "lDETDETNo",
    "DoorType": "lDTDTNo",
    "DuctSystem": "lDSDSNo",
    "EqInst": "lEIEINo",
    "Equip": "lEIEINo",
    "FlrType": "lFTFTNo",
    "FndwType": "lFWTWTNo",
    "GshpType": "lGSTGSTNo",
    "GshpWell": "lGWellNo",
    "HtDhType": "lHTDHTDNo",
    "HtgType": "lHETHETNo",
    "SeasnRat": "lSRSRNo",
    "SlabType": "lSTSTNo",
    "UtilRate": "lURURNo",
    "WallType": "lWTWTNo",
    "WndwType": "lWDTWinNo",
}


def _get_field_from_column(model, field):
    final = None
    for t_field in model._meta.fields:
        try:
            if t_field.db_column and t_field.db_column.lower() == field.lower():
                final = t_field
                break
        except AttributeError:
            log.error("Unable to find column for field {} with model {}".format(field, model))
            raise
    return final


@shared_task(time_limit=60 * 5)
def prune_remrate_data(**kwargs):
    """This is the celery task which will prune the remrate database side of thing."""

    from axis.remrate_data.models import DataTracker

    before_now = now() - datetime.timedelta(hours=kwargs.get("hours", 48))
    exclude = DataTracker.objects.using("default").filter(last_update__gte=before_now)
    exclude = list(exclude.values_list("_result_number", flat=True))

    del_tables, del_rows = 0, 0
    for idx, (source_model_name, destination_model_name) in enumerate(TABLE_MAP):
        SourceModelObj = AEC_Triggers().get_source_model(source_model_name)

        sources = SourceModelObj.objects.all()

        last_one = None
        if source_model_name in LMAX_TABLES.keys():
            # We need to keep at least one of these..
            field = _get_field_from_column(SourceModelObj, LMAX_TABLES[source_model_name])
            last_one = SourceModelObj.objects.all().order_by(field.name).last()
            sources = sources.exclude(pk=last_one.pk)

        try:
            sources = sources.exclude(result_number__in=exclude)
        except FieldError:
            pass

        if sources.count():
            del_tables += 1

        for source in sources:
            source.delete()
            del_rows += 1

        if last_one:
            TargetObj = AEC_Triggers().get_destination_model(destination_model_name)
            field = _get_field_from_column(SourceModelObj, LMAX_TABLES[source_model_name])
            target_last = TargetObj.objects.all().order_by("pk").last()
            number = 1 if not target_last else target_last.pk + 1
            if getattr(last_one, field.name) != number:
                try:
                    SourceModelObj.objects.filter(pk=last_one.pk).update(**{field.name: number})
                except Exception as err:
                    logger.error(
                        "Issue attempting to Update - Please manually update: %r %s: %s -- %r",
                        source_model_name,
                        field.db_column,
                        number,
                        err,
                    )

    return "Pruned {} tables with {} rows removed".format(del_tables, del_rows)
