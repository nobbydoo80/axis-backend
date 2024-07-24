"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Result(models.Model):
    """Result data"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    annual_heating_cost = models.FloatField(max_length=93, db_column="FHCOST", blank=True)
    annual_cooling_cost = models.FloatField(max_length=93, db_column="FCCOST", blank=True)
    annual_water_heating_cost = models.FloatField(max_length=93, db_column="FWCOST", blank=True)
    annual_lights_and_appliance_cost = models.FloatField(
        max_length=93, db_column="FLATOTCOST", blank=True
    )
    annual_photovoltaics_cost = models.FloatField(max_length=93, db_column="FPVTOTCOST", blank=True)
    annual_service_charges = models.FloatField(max_length=93, db_column="FSERVCOST", blank=True)
    annual_total_cost = models.FloatField(max_length=93, db_column="FTOTCOST", blank=True)
    annual_heating_consumption = models.FloatField(null=True, db_column="FHCONS", blank=True)
    annual_cooling_consumption = models.FloatField(null=True, db_column="FCCONS", blank=True)
    annual_water_heating_consumption = models.FloatField(null=True, db_column="FWCONS", blank=True)
    annual_lights_and_appliance_consumption = models.FloatField(
        null=True, db_column="FLATOTCONS", blank=True
    )
    annual_photovoltaics_consumption = models.FloatField(
        null=True, db_column="FPVTOTCONS", blank=True
    )
    insulated_shell_area = models.FloatField(db_column="FSHELLAREA", blank=True)

    # -- Not Used --
    fhteff = models.FloatField(null=True, db_column="FHTEFF", blank=True)
    fclgeff = models.FloatField(null=True, db_column="FCLGEFF", blank=True)
    fhweff = models.FloatField(null=True, db_column="FHWEFF", blank=True)
    flhroof = models.FloatField(null=True, db_column="FLHROOF", blank=True)
    flcroof = models.FloatField(null=True, db_column="FLCROOF", blank=True)
    flhjoist = models.FloatField(null=True, db_column="FLHJOIST", blank=True)
    flcjoist = models.FloatField(null=True, db_column="FLCJOIST", blank=True)
    flhagwall = models.FloatField(null=True, db_column="FLHAGWALL", blank=True)
    flcagwall = models.FloatField(null=True, db_column="FLCAGWALL", blank=True)
    flhfndwall = models.FloatField(null=True, db_column="FLHFNDWALL", blank=True)
    flcfndwall = models.FloatField(null=True, db_column="FLCFNDWALL", blank=True)
    flhwndosk = models.FloatField(null=True, db_column="FLHWNDOSK", blank=True)
    flcwndosk = models.FloatField(null=True, db_column="FLCWNDOSK", blank=True)
    flhfflr = models.FloatField(null=True, db_column="FLHFFLR", blank=True)
    flcfflr = models.FloatField(null=True, db_column="FLCFFLR", blank=True)
    flhcrawl = models.FloatField(null=True, db_column="FLHCRAWL", blank=True)
    flccrawl = models.FloatField(null=True, db_column="FLCCRAWL", blank=True)
    flhslab = models.FloatField(null=True, db_column="FLHSLAB", blank=True)
    flcslab = models.FloatField(null=True, db_column="FLCSLAB", blank=True)
    flhinf = models.FloatField(null=True, db_column="FLHINF", blank=True)
    flcinf = models.FloatField(null=True, db_column="FLCINF", blank=True)
    flhmechvnt = models.FloatField(null=True, db_column="FLHMECHVNT", blank=True)
    flcmechvnt = models.FloatField(null=True, db_column="FLCMECHVNT", blank=True)
    flhduct = models.FloatField(null=True, db_column="FLHDUCT", blank=True)
    flcduct = models.FloatField(null=True, db_column="FLCDUCT", blank=True)
    flhasol = models.FloatField(null=True, db_column="FLHASOL", blank=True)
    flcasol = models.FloatField(null=True, db_column="FLCASOL", blank=True)
    flhss = models.FloatField(null=True, db_column="FLHSS", blank=True)
    flcss = models.FloatField(null=True, db_column="FLCSS", blank=True)
    flhigain = models.FloatField(null=True, db_column="FLHIGAIN", blank=True)
    flcigain = models.FloatField(null=True, db_column="FLCIGAIN", blank=True)
    flhwhf = models.FloatField(null=True, db_column="FLHWHF", blank=True)
    flcwhf = models.FloatField(null=True, db_column="FLCWHF", blank=True)
    flhdoor = models.FloatField(null=True, db_column="FLHDOOR", blank=True)
    flcdoor = models.FloatField(null=True, db_column="FLCDOOR", blank=True)
    flhtotal = models.FloatField(null=True, db_column="FLHTOTAL", blank=True)
    flctotal = models.FloatField(null=True, db_column="FLCTOTAL", blank=True)
    ftotdhw = models.FloatField(null=True, db_column="FTOTDHW", blank=True)
    fsolsave = models.FloatField(null=True, db_column="FSOLSAVE", blank=True)
    fhtpeak = models.FloatField(null=True, db_column="FHTPEAK", blank=True)
    facspeak = models.FloatField(null=True, db_column="FACSPEAK", blank=True)
    faclpeak = models.FloatField(null=True, db_column="FACLPEAK", blank=True)
    factpeak = models.FloatField(null=True, db_column="FACTPEAK", blank=True)
    fhbuck = models.FloatField(null=True, db_column="FHBUCK", blank=True)
    facbuck = models.FloatField(null=True, db_column="FACBUCK", blank=True)
    fwbuck = models.FloatField(null=True, db_column="FWBUCK", blank=True)
    frefrcons = models.FloatField(null=True, db_column="FREFRCONS", blank=True)
    ffrzcons = models.FloatField(null=True, db_column="FFRZCONS", blank=True)
    fdrycons = models.FloatField(null=True, db_column="FDRYCONS", blank=True)
    fovencons = models.FloatField(null=True, db_column="FOVENCONS", blank=True)
    flaothcons = models.FloatField(null=True, db_column="FLAOTHCONS", blank=True)
    flihscons = models.FloatField(null=True, db_column="FLIHSCONS", blank=True)
    flicscons = models.FloatField(null=True, db_column="FLICSCONS", blank=True)
    frefrcost = models.FloatField(null=True, db_column="FREFRCOST", blank=True)
    ffrzcost = models.FloatField(null=True, db_column="FFRZCOST", blank=True)
    fdrycost = models.FloatField(null=True, db_column="FDRYCOST", blank=True)
    fovencost = models.FloatField(null=True, db_column="FOVENCOST", blank=True)
    flaothcost = models.FloatField(null=True, db_column="FLAOTHCOST", blank=True)
    flightcost = models.FloatField(null=True, db_column="FLIGHTCOST", blank=True)
    fhtgldphdd = models.FloatField(null=True, db_column="FHTGLDPHDD", blank=True)
    fclgldphdd = models.FloatField(null=True, db_column="FCLGLDPHDD", blank=True)
    fhtgddphdd = models.FloatField(null=True, db_column="FHTGDDPHDD", blank=True)
    fclgddphdd = models.FloatField(null=True, db_column="FCLGDDPHDD", blank=True)
    fhtgach = models.FloatField(null=True, db_column="FHTGACH", blank=True)
    fclgach = models.FloatField(null=True, db_column="FCLGACH", blank=True)
    srateno = models.CharField(max_length=93, db_column="SRATENO", blank=True)
    femco2tot = models.FloatField(null=True, db_column="FEMCO2TOT", blank=True)
    femso2tot = models.FloatField(null=True, db_column="FEMSO2TOT", blank=True)
    femnoxtot = models.FloatField(null=True, db_column="FEMNOXTOT", blank=True)
    femco2htg = models.FloatField(null=True, db_column="FEMCO2HTG", blank=True)
    femco2clg = models.FloatField(null=True, db_column="FEMCO2CLG", blank=True)
    femco2dhw = models.FloatField(null=True, db_column="FEMCO2DHW", blank=True)
    femco2la = models.FloatField(null=True, db_column="FEMCO2LA", blank=True)
    femco2pv = models.FloatField(null=True, db_column="FEMCO2PV", blank=True)
    femso2htg = models.FloatField(null=True, db_column="FEMSO2HTG", blank=True)
    femso2clg = models.FloatField(null=True, db_column="FEMSO2CLG", blank=True)
    femso2dhw = models.FloatField(null=True, db_column="FEMSO2DHW", blank=True)
    femso2la = models.FloatField(null=True, db_column="FEMSO2LA", blank=True)
    femso2pv = models.FloatField(null=True, db_column="FEMSO2PV", blank=True)
    femnoxhtg = models.FloatField(null=True, db_column="FEMNOXHTG", blank=True)
    femnoxclg = models.FloatField(null=True, db_column="FEMNOXCLG", blank=True)
    femnoxdhw = models.FloatField(null=True, db_column="FEMNOXDHW", blank=True)
    femnoxla = models.FloatField(null=True, db_column="FEMNOXLA", blank=True)
    femnoxpv = models.FloatField(null=True, db_column="FEMNOXPV", blank=True)
    femhersco2 = models.FloatField(null=True, db_column="FEMHERSCO2", blank=True)
    femhersso2 = models.FloatField(null=True, db_column="FEMHERSSO2", blank=True)
    femhersnox = models.FloatField(null=True, db_column="FEMHERSNOX", blank=True)
    fsrcegyhtg = models.FloatField(null=True, db_column="FSRCEGYHTG", blank=True)
    fsrcegyclg = models.FloatField(null=True, db_column="FSRCEGYCLG", blank=True)
    fsrcegydhw = models.FloatField(null=True, db_column="FSRCEGYDHW", blank=True)
    fsrcegyla = models.FloatField(null=True, db_column="FSRCEGYLA", blank=True)
    fsrcegypv = models.FloatField(null=True, db_column="FSRCEGYPV", blank=True)
    fDHWNoLoss = models.FloatField(null=True, db_column="fDHWNoLoss", blank=True)

    class Meta:
        db_table = "Results"
        managed = False
