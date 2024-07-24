"""Django AEC Models - Theses are the source data coming in on the rate database."""


import datetime
import logging

import dateutil.parser
from django.db import models

from axis.remrate_data.strings import EXPORT_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Simulation(models.Model):
    """The Simulation Table"""

    result_number = models.IntegerField(primary_key=True, db_column="LBLDGRUNNO")
    simulation_date = models.DateField(max_length=93, db_column="SBRDATE", blank=True)
    version = models.CharField(max_length=120, db_column="SBRPROGVER", blank=True)
    flavor = models.CharField(max_length=255, db_column="SBRPROGFLVR", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SBRRATENO", blank=True)
    building_run_flag = models.CharField(max_length=90, db_column="SBRFLAG", blank=True)
    export_type = models.IntegerField(
        null=True, db_column="LBREXPTPE", blank=True, choices=EXPORT_TYPES
    )
    number_of_runs = models.IntegerField(null=True, db_column="NINSTANCE", blank=True)

    udrh_filename = models.CharField(max_length=255, db_column="SBRUDRNAME", blank=True, null=True)
    udrh_checksum = models.CharField(max_length=255, db_column="SBRUDRCHK", blank=True, null=True)

    class Meta:
        db_table = "BuildRun"
        managed = False

    def can_be_deleted(self, retain_hours=48):
        """Defines the circumstances when this can be deleted.
        - We should always keep the last two entries.
        - We should always keep the last week of failures.
        """

        from axis.remrate_data.models import Simulation as FinalSim
        from axis.remrate_data.models import Building as FinalBuilding

        keep = FinalBuilding.objects.all().order_by("-last_update")
        keep_ids = list(keep.values_list("_result_number", flat=True))[:2]

        if self.result_number in keep_ids:
            log.info("Retaining %s as we want to keep the last 2 entries", self.result_number)
            return False

        passing_expire_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            hours=retain_hours
        )
        failing_expire_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            hours=retain_hours * 3
        )
        sim_date = dateutil.parser.parse(self.simulation_date).replace(tzinfo=datetime.timezone.utc)

        try:
            final = FinalSim.objects.get(_source_result_number=self.result_number)
            if final.building.sync_status == 1:
                if sim_date < passing_expire_date:
                    log.info("Allowing delete successful sync")
                    return True
            else:
                if sim_date < failing_expire_date:
                    log.info("Allowing delete unsuccessful expired sync")
                    return True

        except FinalSim.DoesNotExist:
            if sim_date < failing_expire_date:
                log.info("Allowing delete non-existent unsuccessful expired sync")
                return True

        log.info("Retaining %s", self.result_number)
        return False
