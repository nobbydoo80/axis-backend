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


class Compliance(models.Model):
    """Describes the compliance of the simulation"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    hers_index = models.FloatField(null=True, db_column="FHERSSCOR", blank=True)
    hers_index_wo_pv = models.FloatField(null=True, db_column="FHERS_PV", blank=True)
    hers_index_reference_design = models.FloatField(null=True, db_column="FES_HERS", blank=True)
    hers_index_target_saf_adj = models.FloatField(null=True, db_column="FES_HERSSA", blank=True)
    hers_total_cost = models.FloatField(null=True, db_column="FHERSCOST", blank=True)
    hers_stars = models.FloatField(null=True, db_column="FHERSSTARS", blank=True)
    reference_annual_heating_mmbtu = models.FloatField(null=True, db_column="FHERSRHCN", blank=True)
    reference_annual_cooling_mmbtu = models.FloatField(null=True, db_column="FHERSRCCN", blank=True)
    reference_annual_hot_water_mmbtu = models.FloatField(
        null=True, db_column="FHERSRDCN", blank=True
    )
    reference_annual_lights_appl_mmbtu = models.FloatField(
        null=True, db_column="FHERSRLACN", blank=True
    )
    reference_annual_solar_mmbtu = models.FloatField(null=True, db_column="FHERSRPVCN", blank=True)
    reference_total_mmbtu = models.FloatField(null=True, db_column="FHERSRTCN", blank=True)
    estimated_annual_heating_mmbtu = models.FloatField(null=True, db_column="FHERSDHCN", blank=True)
    estimated_annual_cooling_mmbtu = models.FloatField(null=True, db_column="FHERSDCCN", blank=True)
    estimated_annual_hot_water_mmbtu = models.FloatField(
        null=True, db_column="FHERSDDCN", blank=True
    )
    estimated_annual_lights_appl_mmbtu = models.FloatField(
        null=True, db_column="FHERSDLACN", blank=True
    )
    estimated_annual_solar_mmbtu = models.FloatField(null=True, db_column="FHERSDPVCN", blank=True)
    estimated_total_mmbtu = models.FloatField(null=True, db_column="FHERSDTCN", blank=True)

    pass_IECC98 = models.FloatField(null=True, db_column="B98IECC", blank=True)
    pass_IECC00 = models.FloatField(null=True, db_column="B00IECC", blank=True)
    pass_IECC01 = models.FloatField(null=True, db_column="B01IECC", blank=True)
    pass_IECC03 = models.FloatField(null=True, db_column="B03IECC", blank=True)
    pass_IECC04 = models.FloatField(null=True, db_column="B04IECC", blank=True)
    pass_IECC06 = models.FloatField(null=True, db_column="B06IECC", blank=True)
    pass_IECC09 = models.FloatField(null=True, db_column="B09IECC", blank=True)
    pass_NY_IECC = models.FloatField(null=True, db_column="BNYECC", blank=True)
    pass_NV_IECC = models.FloatField(null=True, db_column="BNVECC", blank=True)
    pass_energy_star_v2 = models.BooleanField(null=True, db_column="BESTARV2", blank=True)
    pass_energy_star_v2p5 = models.BooleanField(null=True, db_column="BESTARV25", blank=True)
    pass_energy_star_v3 = models.BooleanField(null=True, db_column="BESTARV3", blank=True)
    pass_energy_star_v3p1 = models.BooleanField(null=True, db_column="bESTARV31", blank=True)
    pass_energy_star_v3HI = models.BooleanField(null=True, db_column="bESTARV3HI", blank=True)
    pass_tax_credit = models.BooleanField(null=True, db_column="BTAXCREDIT", blank=True)
    pass_ashrae_90p2 = models.BooleanField(null=True, db_column="B90_2ASCCP", blank=True)
    size_adjustment_factor = models.FloatField(db_column="FES_SZADJF", blank=True, null=True)

    # -- Not used --
    f98ierhcn = models.FloatField(null=True, db_column="F98IERHCN", blank=True)
    f98ierccn = models.FloatField(null=True, db_column="F98IERCCN", blank=True)
    f98ierdcn = models.FloatField(null=True, db_column="F98IERDCN", blank=True)
    f98ierlacn = models.FloatField(null=True, db_column="F98IERLACN", blank=True)
    f98ierpvcn = models.FloatField(null=True, db_column="F98IERPVCN", blank=True)
    f98iertcn = models.FloatField(null=True, db_column="F98IERTCN", blank=True)
    f98iedhcn = models.FloatField(null=True, db_column="F98IEDHCN", blank=True)
    f98iedccn = models.FloatField(null=True, db_column="F98IEDCCN", blank=True)
    f98ieddcn = models.FloatField(null=True, db_column="F98IEDDCN", blank=True)
    f98iedlacn = models.FloatField(null=True, db_column="F98IEDLACN", blank=True)
    f98iedpvcn = models.FloatField(null=True, db_column="F98IEDPVCN", blank=True)
    f98iedtcn = models.FloatField(null=True, db_column="F98IEDTCN", blank=True)
    f00ierhcn = models.FloatField(null=True, db_column="F00IERHCN", blank=True)
    f00ierccn = models.FloatField(null=True, db_column="F00IERCCN", blank=True)
    f00ierdcn = models.FloatField(null=True, db_column="F00IERDCN", blank=True)
    f00ierlacn = models.FloatField(null=True, db_column="F00IERLACN", blank=True)
    f00ierpvcn = models.FloatField(null=True, db_column="F00IERPVCN", blank=True)
    f00iertcn = models.FloatField(null=True, db_column="F00IERTCN", blank=True)
    f00iedhcn = models.FloatField(null=True, db_column="F00IEDHCN", blank=True)
    f00iedccn = models.FloatField(null=True, db_column="F00IEDCCN", blank=True)
    f00ieddcn = models.FloatField(null=True, db_column="F00IEDDCN", blank=True)
    f00iedlacn = models.FloatField(null=True, db_column="F00IEDLACN", blank=True)
    f00iedpvcn = models.FloatField(null=True, db_column="F00IEDPVCN", blank=True)
    f00iedtcn = models.FloatField(null=True, db_column="F00IEDTCN", blank=True)
    f01ierhcn = models.FloatField(null=True, db_column="F01IERHCN", blank=True)
    f01ierccn = models.FloatField(null=True, db_column="F01IERCCN", blank=True)
    f01ierdcn = models.FloatField(null=True, db_column="F01IERDCN", blank=True)
    f01ierlacn = models.FloatField(null=True, db_column="F01IERLACN", blank=True)
    f01ierpvcn = models.FloatField(null=True, db_column="F01IERPVCN", blank=True)
    f01iertcn = models.FloatField(null=True, db_column="F01IERTCN", blank=True)
    f01iedhcn = models.FloatField(null=True, db_column="F01IEDHCN", blank=True)
    f01iedccn = models.FloatField(null=True, db_column="F01IEDCCN", blank=True)
    f01ieddcn = models.FloatField(null=True, db_column="F01IEDDCN", blank=True)
    f01iedlacn = models.FloatField(null=True, db_column="F01IEDLACN", blank=True)
    f01iedpvcn = models.FloatField(null=True, db_column="F01IEDPVCN", blank=True)
    f01iedtcn = models.FloatField(null=True, db_column="F01IEDTCN", blank=True)
    f03ierhcn = models.FloatField(null=True, db_column="F03IERHCN", blank=True)
    f03ierccn = models.FloatField(null=True, db_column="F03IERCCN", blank=True)
    f03ierdcn = models.FloatField(null=True, db_column="F03IERDCN", blank=True)
    f03ierlacn = models.FloatField(null=True, db_column="F03IERLACN", blank=True)
    f03ierpvcn = models.FloatField(null=True, db_column="F03IERPVCN", blank=True)
    f03iertcn = models.FloatField(null=True, db_column="F03IERTCN", blank=True)
    f03iedhcn = models.FloatField(null=True, db_column="F03IEDHCN", blank=True)
    f03iedccn = models.FloatField(null=True, db_column="F03IEDCCN", blank=True)
    f03ieddcn = models.FloatField(null=True, db_column="F03IEDDCN", blank=True)
    f03iedlacn = models.FloatField(null=True, db_column="F03IEDLACN", blank=True)
    f03iedpvcn = models.FloatField(null=True, db_column="F03IEDPVCN", blank=True)
    f03iedtcn = models.FloatField(null=True, db_column="F03IEDTCN", blank=True)
    f04ierhct = models.FloatField(null=True, db_column="F04IERHCT", blank=True)
    f04iercct = models.FloatField(null=True, db_column="F04IERCCT", blank=True)
    f04ierdct = models.FloatField(null=True, db_column="F04IERDCT", blank=True)
    f04ierlact = models.FloatField(null=True, db_column="F04IERLACT", blank=True)
    f04ierpvct = models.FloatField(null=True, db_column="F04IERPVCT", blank=True)
    f04iersvct = models.FloatField(null=True, db_column="F04IERSVCT", blank=True)
    f04iertct = models.FloatField(null=True, db_column="F04IERTCT", blank=True)
    f04iedhct = models.FloatField(null=True, db_column="F04IEDHCT", blank=True)
    f04iedcct = models.FloatField(null=True, db_column="F04IEDCCT", blank=True)
    f04ieddct = models.FloatField(null=True, db_column="F04IEDDCT", blank=True)
    f04iedlact = models.FloatField(null=True, db_column="F04IEDLACT", blank=True)
    f04iedpvct = models.FloatField(null=True, db_column="F04IEDPVCT", blank=True)
    f04iedsvct = models.FloatField(null=True, db_column="F04IEDSVCT", blank=True)
    f04iedtct = models.FloatField(null=True, db_column="F04IEDTCT", blank=True)
    f06ierhct = models.FloatField(null=True, db_column="F06IERHCT", blank=True)
    f06iercct = models.FloatField(null=True, db_column="F06IERCCT", blank=True)
    f06ierdct = models.FloatField(null=True, db_column="F06IERDCT", blank=True)
    f06ierlact = models.FloatField(null=True, db_column="F06IERLACT", blank=True)
    f06ierpvct = models.FloatField(null=True, db_column="F06IERPVCT", blank=True)
    f06iersvct = models.FloatField(null=True, db_column="F06IERSVCT", blank=True)
    f06iertct = models.FloatField(null=True, db_column="F06IERTCT", blank=True)
    f06iedhct = models.FloatField(null=True, db_column="F06IEDHCT", blank=True)
    f06iedcct = models.FloatField(null=True, db_column="F06IEDCCT", blank=True)
    f06ieddct = models.FloatField(null=True, db_column="F06IEDDCT", blank=True)
    f06iedlact = models.FloatField(null=True, db_column="F06IEDLACT", blank=True)
    f06iedpvct = models.FloatField(null=True, db_column="F06IEDPVCT", blank=True)
    f06iedsvct = models.FloatField(null=True, db_column="F06IEDSVCT", blank=True)
    f06iedtct = models.FloatField(null=True, db_column="F06IEDTCT", blank=True)
    fnyecrhcn = models.FloatField(null=True, db_column="FNYECRHCN", blank=True)
    fnyecrccn = models.FloatField(null=True, db_column="FNYECRCCN", blank=True)
    fnyecrdcn = models.FloatField(null=True, db_column="FNYECRDCN", blank=True)
    fnyecrlacn = models.FloatField(null=True, db_column="FNYECRLACN", blank=True)
    fnyecrpvcn = models.FloatField(null=True, db_column="FNYECRPVCN", blank=True)
    fnyecrtcn = models.FloatField(null=True, db_column="FNYECRTCN", blank=True)
    fnyecdhcn = models.FloatField(null=True, db_column="FNYECDHCN", blank=True)
    fnyecdccn = models.FloatField(null=True, db_column="FNYECDCCN", blank=True)
    fnyecddcn = models.FloatField(null=True, db_column="FNYECDDCN", blank=True)
    fnyecdlacn = models.FloatField(null=True, db_column="FNYECDLACN", blank=True)
    fnyecdpvcn = models.FloatField(null=True, db_column="FNYECDPVCN", blank=True)
    fnyecdtcn = models.FloatField(null=True, db_column="FNYECDTCN", blank=True)
    fnvecrhcn = models.FloatField(null=True, db_column="FNVECRHCN", blank=True)
    fnvecrccn = models.FloatField(null=True, db_column="FNVECRCCN", blank=True)
    fnvecrdcn = models.FloatField(null=True, db_column="FNVECRDCN", blank=True)
    fnvecrlacn = models.FloatField(null=True, db_column="FNVECRLACN", blank=True)
    fnvecrpvcn = models.FloatField(null=True, db_column="FNVECRPVCN", blank=True)
    fnvecrtcn = models.FloatField(null=True, db_column="FNVECRTCN", blank=True)
    fnvecdhcn = models.FloatField(null=True, db_column="FNVECDHCN", blank=True)
    fnvecdccn = models.FloatField(null=True, db_column="FNVECDCCN", blank=True)
    fnvecddcn = models.FloatField(null=True, db_column="FNVECDDCN", blank=True)
    fnvecdlacn = models.FloatField(null=True, db_column="FNVECDLACN", blank=True)
    fnvecdpvcn = models.FloatField(null=True, db_column="FNVECDPVCN", blank=True)
    fnvecdtcn = models.FloatField(null=True, db_column="FNVECDTCN", blank=True)
    f92mecreuo = models.FloatField(null=True, db_column="F92MECREUO", blank=True)
    f92mecaduo = models.FloatField(null=True, db_column="F92MECADUO", blank=True)
    b92mecdup = models.FloatField(null=True, db_column="B92MECDUP", blank=True)
    b92mecuop = models.FloatField(null=True, db_column="B92MECUOP", blank=True)
    f93mecreuo = models.FloatField(null=True, db_column="F93MECREUO", blank=True)
    f93mecaduo = models.FloatField(null=True, db_column="F93MECADUO", blank=True)
    b93mecdup = models.FloatField(null=True, db_column="B93MECDUP", blank=True)
    b93mecuop = models.FloatField(null=True, db_column="B93MECUOP", blank=True)
    f95mecreuo = models.FloatField(null=True, db_column="F95MECREUO", blank=True)
    f95mecaduo = models.FloatField(null=True, db_column="F95MECADUO", blank=True)
    b95mecdup = models.FloatField(null=True, db_column="B95MECDUP", blank=True)
    b95mecuop = models.FloatField(null=True, db_column="B95MECUOP", blank=True)
    f98ieccruo = models.FloatField(null=True, db_column="F98IECCRUO", blank=True)
    f98ieccduo = models.FloatField(null=True, db_column="F98IECCDUO", blank=True)
    b98ieccdup = models.IntegerField(null=True, db_column="B98IECCDUP", blank=True)
    b98ieccuop = models.IntegerField(null=True, db_column="B98IECCUOP", blank=True)
    f00ieccruo = models.FloatField(null=True, db_column="F00IECCRUO", blank=True)
    f00ieccduo = models.FloatField(null=True, db_column="F00IECCDUO", blank=True)
    b00ieccdup = models.IntegerField(null=True, db_column="B00IECCDUP", blank=True)
    b00ieccuop = models.IntegerField(null=True, db_column="B00IECCUOP", blank=True)
    f01ieccruo = models.FloatField(null=True, db_column="F01IECCRUO", blank=True)
    f01ieccduo = models.FloatField(null=True, db_column="F01IECCDUO", blank=True)
    b01ieccdup = models.IntegerField(null=True, db_column="B01IECCDUP", blank=True)
    b01ieccuop = models.IntegerField(null=True, db_column="B01IECCUOP", blank=True)
    f03ieccruo = models.FloatField(null=True, db_column="F03IECCRUO", blank=True)
    f03ieccduo = models.FloatField(null=True, db_column="F03IECCDUO", blank=True)
    b03ieccdup = models.IntegerField(null=True, db_column="B03IECCDUP", blank=True)
    b03ieccuop = models.IntegerField(null=True, db_column="B03IECCUOP", blank=True)
    f04ieccrua = models.FloatField(null=True, db_column="F04IECCRUA", blank=True)
    f04ieccdua = models.FloatField(null=True, db_column="F04IECCDUA", blank=True)
    b04ieccdup = models.IntegerField(null=True, db_column="B04IECCDUP", blank=True)
    b04ieccuap = models.IntegerField(null=True, db_column="B04IECCUAP", blank=True)
    f06ieccrua = models.FloatField(null=True, db_column="F06IECCRUA", blank=True)
    f06ieccdua = models.FloatField(null=True, db_column="F06IECCDUA", blank=True)
    b06ieccdup = models.IntegerField(null=True, db_column="B06IECCDUP", blank=True)
    b06ieccuap = models.IntegerField(null=True, db_column="B06IECCUAP", blank=True)
    f92mecrhcn = models.FloatField(null=True, db_column="F92MECRHCN", blank=True)
    f92mecrccn = models.FloatField(null=True, db_column="F92MECRCCN", blank=True)
    f92mecrdcn = models.FloatField(null=True, db_column="F92MECRDCN", blank=True)
    f92mecrlcn = models.FloatField(null=True, db_column="F92MECRLCN", blank=True)
    f92mecrpcn = models.FloatField(null=True, db_column="F92MECRPCN", blank=True)
    f92mecrtcn = models.FloatField(null=True, db_column="F92MECRTCN", blank=True)
    f92mecdhcn = models.FloatField(null=True, db_column="F92MECDHCN", blank=True)
    f92mecdccn = models.FloatField(null=True, db_column="F92MECDCCN", blank=True)
    f92mecddcn = models.FloatField(null=True, db_column="F92MECDDCN", blank=True)
    f92mecdlcn = models.FloatField(null=True, db_column="F92MECDLCN", blank=True)
    f92mecdpcn = models.FloatField(null=True, db_column="F92MECDPCN", blank=True)
    f92mecdtcn = models.FloatField(null=True, db_column="F92MECDTCN", blank=True)
    b92meccc = models.FloatField(null=True, db_column="B92MECCC", blank=True)
    f93mecrhcn = models.FloatField(null=True, db_column="F93MECRHCN", blank=True)
    f93mecrccn = models.FloatField(null=True, db_column="F93MECRCCN", blank=True)
    f93mecrdcn = models.FloatField(null=True, db_column="F93MECRDCN", blank=True)
    f93mecrlcn = models.FloatField(null=True, db_column="F93MECRLCN", blank=True)
    f93mecrpcn = models.FloatField(null=True, db_column="F93MECRPCN", blank=True)
    f93mecrtcn = models.FloatField(null=True, db_column="F93MECRTCN", blank=True)
    f93mecdhcn = models.FloatField(null=True, db_column="F93MECDHCN", blank=True)
    f93mecdccn = models.FloatField(null=True, db_column="F93MECDCCN", blank=True)
    f93mecddcn = models.FloatField(null=True, db_column="F93MECDDCN", blank=True)
    f93mecdlcn = models.FloatField(null=True, db_column="F93MECDLCN", blank=True)
    f93mecdpcn = models.FloatField(null=True, db_column="F93MECDPCN", blank=True)
    f93mecdtcn = models.FloatField(null=True, db_column="F93MECDTCN", blank=True)
    b93meccc = models.FloatField(null=True, db_column="B93MECCC", blank=True)
    f95mecrhcn = models.FloatField(null=True, db_column="F95MECRHCN", blank=True)
    f95mecrccn = models.FloatField(null=True, db_column="F95MECRCCN", blank=True)
    f95mecrdcn = models.FloatField(null=True, db_column="F95MECRDCN", blank=True)
    f95mecrlcn = models.FloatField(null=True, db_column="F95MECRLCN", blank=True)
    f95mecrpcn = models.FloatField(null=True, db_column="F95MECRPCN", blank=True)
    f95mecrtcn = models.FloatField(null=True, db_column="F95MECRTCN", blank=True)
    f95mecdhcn = models.FloatField(null=True, db_column="F95MECDHCN", blank=True)
    f95mecdccn = models.FloatField(null=True, db_column="F95MECDCCN", blank=True)
    f95mecddcn = models.FloatField(null=True, db_column="F95MECDDCN", blank=True)
    f95mecdlcn = models.FloatField(null=True, db_column="F95MECDLCN", blank=True)
    f95mecdpcn = models.FloatField(null=True, db_column="F95MECDPCN", blank=True)
    f95mecdtcn = models.FloatField(null=True, db_column="F95MECDTCN", blank=True)
    b95meccc = models.FloatField(null=True, db_column="B95MECCC", blank=True)
    f90_2aslc = models.FloatField(null=True, db_column="F90_2ASLC", blank=True)
    b90_2asecp = models.FloatField(null=True, db_column="B90_2ASECP", blank=True)
    f90_2asrcn = models.FloatField(null=True, db_column="F90_2ASRCN", blank=True)
    f90_2asrct = models.FloatField(null=True, db_column="F90_2ASRCT", blank=True)
    f90_2asdcn = models.FloatField(null=True, db_column="F90_2ASDCN", blank=True)
    f90_2asdct = models.FloatField(null=True, db_column="F90_2ASDCT", blank=True)
    fnyhers = models.FloatField(null=True, db_column="FNYHERS", blank=True)
    srateno = models.CharField(max_length=93, db_column="SRATENO", blank=True)
    f09ierhct = models.FloatField(null=True, db_column="F09IERHCT", blank=True)
    f09iercct = models.FloatField(null=True, db_column="F09IERCCT", blank=True)
    f09ierdct = models.FloatField(null=True, db_column="F09IERDCT", blank=True)
    f09ierlact = models.FloatField(null=True, db_column="F09IERLACT", blank=True)
    f09ierpvct = models.FloatField(null=True, db_column="F09IERPVCT", blank=True)
    f09iersvct = models.FloatField(null=True, db_column="F09IERSVCT", blank=True)
    f09iertct = models.FloatField(null=True, db_column="F09IERTCT", blank=True)
    f09iedhct = models.FloatField(null=True, db_column="F09IEDHCT", blank=True)
    f09iedcct = models.FloatField(null=True, db_column="F09IEDCCT", blank=True)
    f09ieddct = models.FloatField(null=True, db_column="F09IEDDCT", blank=True)
    f09iedlact = models.FloatField(null=True, db_column="F09IEDLACT", blank=True)
    f09iedpvct = models.FloatField(null=True, db_column="F09IEDPVCT", blank=True)
    f09iedsvct = models.FloatField(null=True, db_column="F09IEDSVCT", blank=True)
    f09iedtct = models.FloatField(null=True, db_column="F09IEDTCT", blank=True)
    f09ieccrua = models.FloatField(null=True, db_column="F09IECCRUA", blank=True)
    f09ieccdua = models.FloatField(null=True, db_column="F09IECCDUA", blank=True)
    b09ieccdup = models.IntegerField(null=True, db_column="B09IECCDUP", blank=True)
    b09ieccuap = models.IntegerField(null=True, db_column="B09IECCUAP", blank=True)
    fnvrebate = models.FloatField(null=True, db_column="FNVREBATE", blank=True)
    bpass04iecc = models.IntegerField(null=True, db_column="BPASS04IECC", blank=True)
    bpass06iecc = models.IntegerField(null=True, db_column="BPASS06IECC", blank=True)
    bpass09iecc = models.IntegerField(null=True, db_column="BPASS09IECC", blank=True)
    bpass12iecc = models.IntegerField(null=True, db_column="BPASS12IECC", blank=True)
    bpassdoechall = models.FloatField(null=True, db_column="bDOECHALL", blank=True)
    fhers130 = models.FloatField(null=True, db_column="FHERS130", blank=True)
    doe_hers = models.FloatField(null=True, db_column="FDOE_Hers", blank=True)
    doe_hers_saf_adjusted = models.FloatField(null=True, db_column="FDOE_HersSA", blank=True)

    class Meta:
        db_table = "Compliance"
        managed = False
