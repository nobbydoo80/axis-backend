"""utils.py: Django aec_remrate"""


import logging
import subprocess  # nosec

from django.apps import apps

get_models = apps.get_models

__author__ = "Steven Klass"
__date__ = "4/24/12 5:49 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

TABLE_MAP = (
    ("BuildRun", "Simulation"),
    ("UtilRate", "UtilityRate"),
    ("SeasnRat", "SeasonalRate"),
    ("Block", "Block"),
    ("Building", "Building"),
    ("Project", "Project"),
    ("BldgInfo", "BuildingInfo"),
    ("FndwType", "FoundationWallType"),
    ("FndWall", "FoundationWall"),
    ("SlabType", "SlabType"),
    ("Slab", "Slab"),
    ("CompType", "CompositeType"),
    ("HeatPath", "HeatPath"),
    ("CeilType", "CeilingType"),
    ("Roof", "Roof"),
    ("WallType", "WallType"),
    ("AGWall", "AboveGradeWall"),
    ("FlrType", "FloorType"),
    ("FrameFlr", "FrameFloor"),
    ("Joist", "Joist"),
    ("DoorType", "DoorType"),
    ("Door", "Door"),
    ("WndwType", "WindowType"),
    ("Window", "Window"),
    ("Skylight", "Skylight"),
    ("Equip", "GeneralMechanicalEquipment"),
    ("HtgType", "Heater"),
    ("ClgType", "AirConditioner"),
    ("DhwType", "HotWaterHeater"),
    ("GshpType", "GroundSourceHeatPump"),
    ("AshpType", "AirSourceHeatPump"),
    ("DfhpType", "DualFuelHeatPump"),
    ("HtDhType", "IntegratedSpaceWaterHeater"),
    ("DehumidType", "Dehumidifier"),
    ("SharedType", "SharedEquipment"),
    ("WLHPType", "WaterLoopHeatPump"),
    ("EqInst", "InstalledEquipment"),
    ("GSHPWell", "GroundSourceHeatPumpWell"),
    ("DhwDistrib", "HotWaterDistribution"),
    ("HvacCx", "HVACCommissioning"),
    ("DuctSystem", "DuctSystem"),
    ("Duct", "Duct"),
    ("Infilt", "Infiltration"),
    ("MechVent", "Ventilation"),
    ("LightApp", "LightsAndAppliance"),
    ("LAInst", "InstalledLightsAndAppliances"),
    ("MandReq", "MandatoryRequirements"),
    ("DOEChallenge", "DOEChallenge"),
    ("AddMass", "AdditionalMass"),
    ("ActSolar", "SolarSystem"),
    ("PhotoVol", "PhotoVoltaic"),
    ("SunSpace", "SunSpace"),
    ("SSMass", "SunSpaceMass"),
    ("SSCmnWal", "SunSpaceCommonWall"),
    ("SSWindow", "SunSpaceWindow"),
    ("SSSkLght", "SunSpaceSkylight"),
    ("ResnetDisc", "ResnetDisc"),
    ("ESRequire", "EnergyStarRequirements"),
    ("FuelSum", "FuelSummary"),
    ("EconParam", "EconomicParameters"),
    ("Results", "Results"),
    ("Compliance", "Compliance"),
    ("RegionalCode", "RegionalCode"),
    ("HERSCode", "HERS"),
    ("ENERGYSTAR", "ENERGYSTAR"),
    ("IECC", "IECC"),
    ("CostRate", "CostRate"),
    ("AccMeas", "AcceptedMeasure"),
    ("RejMeas", "RejectedMeasure"),
    ("Econ", "Economic"),
    ("SimpInp", "SimplifiedInput"),
    ("NevMeas", "NevMeas"),
    ("Florida", "Florida"),
    ("HercInfo", "HercInfo"),
    ("Site", "Site"),
)


def runcmd(cmd):
    """Simple tool to run a command"""
    log.info("Running %s" % cmd)
    process = subprocess.Popen(  # nosec
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    accepted = [
        "Warning: Using a password on the command line interface can be insecure.",
        "",
        "mysql: [Warning] Using a password on the command line interface can be insecure.",
    ]
    stderr = [x.strip() for x in stderr.decode("utf-8").split("\n") if x.strip() not in accepted]
    stdout = [x.strip() for x in stdout.decode("utf-8").split("\n") if x.strip() != ""]
    if process.returncode < 0 or len(stderr):
        log.error('Error running "%(cmd)s"', {"cmd": cmd})
        raise SystemError("\n".join(stderr))
    if len(stdout):
        log.info("\n".join(stdout))
    return stdout


class AEC_Triggers:
    def __init__(self, *args, **kwargs):
        self.output = None
        self.output_file = kwargs.get("output_file")
        if self.output_file:
            self.output = open(self.output_file, "w")

        self.result = []
        self.source_database = "remrate"
        self.source_app_label = kwargs.get("source_app_label", "aec_remrate")
        self.destination_database = "axis"
        self.destination_app_label = kwargs.get("destination_app_label", "remrate_data")

        log_level = kwargs.get("loglevel")
        if log_level:
            log = kwargs.get("log", logging.getLogger(__name__))
            log.setLevel(log_level)
        self.use_sql_log = kwargs.get("use_sql_log", False)
        self.source_models = [m for m in get_models() if m._meta.app_label == self.source_app_label]

    def _get_model(self, name, app_label):
        models = [m for m in get_models() if m._meta.app_label == app_label]
        model = next((m for m in models if m._meta.db_table.lower() == name.lower()), None)
        if model is None:
            try:
                model = next((m for m in models if m._meta.object_name.lower() == name.lower()))
            except StopIteration:
                log.exception("Unable to find either a table or object named %s", name)
                raise
        return model

    def get_source_model(self, name):
        """
        Given a name get the source model
        """
        return self._get_model(name, self.source_app_label)

    def get_destination_model(self, name):
        """
        Given a name get the destination model
        """
        return self._get_model(name, self.destination_app_label)

    def write(self, data):
        if self.output:
            self.output.write("{}\n".format(data))
        else:
            self.result.append(data)

    def save(self):
        self.output.close()

    def add_drop_trigger(self, source_model):
        self.write(
            "DROP TRIGGER IF EXISTS `after_{}_copy_trigger` $$".format(
                source_model._meta.model_name.lower()
            )
        )

    def add_log(self, source_model, msg, quote_msg=True):
        if not self.use_sql_log:
            return

        self.write(
            "    INSERT INTO {}.remrate_remratelog (`trigger`, `log`, `time` )".format(
                self.destination_database
            )
        )
        if quote_msg:
            msg = "'{}'".format(msg)
        self.write(
            "      VALUES ('after_{}_copy_trigger', {}, NOW());".format(source_model.lower(), msg)
        )

    def add_create_trigger(self, source_model):
        self.write(
            "CREATE TRIGGER after_{}_copy_trigger".format(source_model._meta.model_name.lower())
        )
        self.write("    AFTER INSERT on {} FOR EACH ROW".format(source_model._meta.db_table))
        self.write("    BEGIN")

    def add_end_trigger(self, source_model):
        self.write("    END $$\n")

    def _get_field_from_column(self, model, field):
        final = None
        for t_field in model._meta.fields:
            try:
                if t_field.db_column and t_field.db_column.lower() == field.db_column.lower():
                    final = t_field
                    break
            except AttributeError:
                log.error(
                    "Unable to find column for field {} ({}) with model {}".format(
                        field, field.__class__.__name__, model
                    )
                )
                raise
        # log.debug("Field {} in {} → {}".format(field.db_column, model._meta.object_name, final))
        return final

    def add_basic_insert(self, source_model, destination_model, keys=None, values=None, indent=1):
        keys = keys if keys else []
        values = values if values else []

        s_fields = [
            f
            for f in source_model._meta.fields
            if f.__class__.__name__ not in ["AutoField", "BigAutoField"]
        ]
        d_fields = [
            f
            for f in destination_model._meta.fields
            if f.__class__.__name__ not in ["AutoField", "BigAutoField"]
        ]

        self.write(
            "{}   INSERT INTO {}.{}".format(
                " " * indent, self.destination_database, destination_model._meta.db_table
            )
        )

        field_keys, field_values = [], []
        for s_field in s_fields:
            _key = self._get_field_from_column(destination_model, s_field).db_column
            if _key.upper() not in [x.upper() for x in keys]:
                field_keys.append(_key)
                field_values.append(s_field.db_column)

        if len(keys + field_keys) != len(d_fields):
            v_keys = keys + [
                x.db_column for x in d_fields if hasattr(x, "db_column") and x.db_column
            ]
            v_keys += [
                "{}_id".format(x.name) for x in d_fields if hasattr(x, "related") and x.related
            ]
            for field in [x for x in keys + field_keys if x not in v_keys]:
                log.warning("Missing %s field %s", destination_model._meta.verbose_name, field)

        if len(values + field_values) != len(keys + field_keys):
            if len(values) != len(keys):
                log.error(
                    "%s Input values != Input keys -- %s != %s",
                    source_model._meta.verbose_name,
                    keys,
                    values,
                )
            if len(field_values) != len(field_keys):
                log.error(
                    "%s Field values != Field keys -- %s != %s",
                    source_model._meta.verbose_name,
                    field_keys,
                    field_values,
                )

        values = values + ["NEW.{}".format(x) for x in field_values]
        self.write("{}     (`{}`) VALUES".format(" " * indent, "`, `".join(keys + field_keys)))
        self.write("{}     ( {} );".format(" " * indent, ", ".join(values)))

        return keys, values

        # Generic FK's

    def _get_where(self, source_model, status_id=None):
        tgt = [y.lower() for y in ["lBldgNo", "lBldgRunNo"]]
        source_fields = [
            x.db_column
            for x in source_model._meta.fields
            if x.db_column and x.db_column.lower() in tgt
        ]
        where = []
        if "lBldgNo".lower() in [x.lower() for x in source_fields]:
            where.append("`lBldgNo`=NEW.LBLDGNO")
        if "lBldgRunNo".lower() in [x.lower() for x in source_fields]:
            where.append("`lBldgRunNo`=NEW.LBLDGRUNNO")

        if status_id is None:
            status = " IN (0,-1)"
            if len(where) == 2:
                status = "=0"
        else:
            status = "={}".format(status_id)

        where.append("`status`{}".format(status))
        assert len(where) > 1, "Umm missing something."
        return " AND ".join(where)

    def get_simulation_and_building(self, source_model, destination_model):
        self.write("    DECLARE sim_id INT;")
        self.write("    DECLARE bldg_id INT;")
        self.write("    DECLARE version_id varchar(12);")
        self.write("    DECLARE lbldgrunno_id INT;")
        self.write("    DECLARE lbldgno_id INT;\n")
        self.write("    SET lbldgrunno_id=NEW.LBLDGRUNNO;")
        self.write("    SET lbldgno_id=NEW.LBLDGNO;\n")
        self.write(
            "    SELECT simulation_id, building_id, version INTO sim_id, bldg_id, version_id "
            "FROM axis.remrate_data_datatracker WHERE"
        )
        self.write("      ({}) ORDER BY -id LIMIT 1;\n".format(self._get_where(source_model)))
        log.debug(
            "%s Adding Generic Simulation and Building Foreign Keys",
            source_model._meta.verbose_name,
        )
        return ["simulation_id", "building_id"], ["sim_id", "bldg_id"]

    def get_simulation(self, source_model, destination_model):
        self.write("    DECLARE sim_id INT;")
        self.write("    DECLARE version_id varchar(12);")
        self.write("    DECLARE lbldgrunno_id INT;\n")
        self.write("    SET lbldgrunno_id=NEW.LBLDGRUNNO;\n")
        self.write(
            "    SELECT simulation_id, version INTO sim_id, version_id "
            "FROM axis.remrate_data_datatracker WHERE"
        )
        self.write("      ({}) ORDER BY -id LIMIT 1;\n".format(self._get_where(source_model)))
        log.debug("%s Adding Generic Simulation Foreign Keys", source_model._meta.verbose_name)
        return ["simulation_id"], ["sim_id"]

    def get_building(self, source_model, destination_model):
        self.write("    DECLARE bldg_id INT;")
        self.write("    DECLARE version_id varchar(12);")
        self.write("    DECLARE lbldgno_id INT;\n")
        self.write("    SET lbldgno_id=NEW.LBLDGNO;\n")
        self.write(
            "    SELECT building_id, version INTO bldg_id, version_id "
            "FROM axis.remrate_data_datatracker WHERE"
        )
        self.write("      ({}) ORDER BY -id LIMIT 1;\n".format(self._get_where(source_model)))
        log.debug("%s Adding Generic Building Foreign Keys", source_model._meta.verbose_name)
        return ["building_id"], ["bldg_id"]

    # Specialized.
    def pre_simulation_task(self, source_model, destination_model, skip_date=False):
        self.write("    DECLARE user_name varchar(32);")
        self.write("    DECLARE org_id INT;")
        self.write("    DECLARE user_id INT;")
        self.write("    DECLARE major_id INT;")
        self.write("    DECLARE minor_id INT;")
        self.write("    DECLARE lbldgrunno_id INT;")
        if not skip_date:
            self.write("    DECLARE correct_date varchar(96);\n")

        self.write("    SET lbldgrunno_id=NEW.LBLDGRUNNO;")
        if not skip_date:
            self.write("    SET correct_date=STR_TO_DATE(NEW.SBRDATE, '%m/%d/%Y %H:%i:%s');\n")

        self.write("    -- Grab the username and let's use it!")
        self.write("    SELECT SUBSTRING_INDEX(USER(),'@',1) INTO user_name;\n")

        self.write("    -- Figure out the org_id which holds that user..")
        self.write(
            "    SELECT company_id INTO org_id FROM axis.remrate_remrateuser WHERE "
            "username=user_name;"
        )

        self.write("\n    -- Update the user or insert him/her into our usertable.")
        self.write("    INSERT INTO axis.remrate_remrateuser")
        self.write("      (`username`, `company_id`, `is_active`, `created_on`, `last_used`)")
        self.write("      VALUES( user_name, org_id, '1', NOW(), NOW())")
        self.write("      ON DUPLICATE KEY UPDATE last_used=NOW();\n")

        self.write(
            "    SELECT id INTO user_id FROM axis.remrate_remrateuser WHERE username=user_name;\n"
        )
        self.write(
            "    SELECT lVersion, lMinor INTO major_id, minor_id "
            "FROM remrate.Version WHERE lID=1;\n"
        )

        if skip_date:
            return ["company_id", "remrate_user_id"], ["org_id", "user_id"]

        return ["company_id", "remrate_user_id", "sBRDate"], ["org_id", "user_id", "correct_date"]

    def simulation_task(self, source_model, destination_model, keys=None, values=None):
        non_flavor = ["12.5", "12.99A", "13.0", "14.0", "14.1", "14.2", "14.3", "14.4", "14.4.1"]
        self.write("    -- Do not push the flavor on old versions")
        self.write("    IF NEW.SBRPROGVER IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("      INSERT INTO axis.remrate_data_simulation")
        self.write(
            "          (`company_id`, `remrate_user_id`, `lBldgRunNo`, `sBRDate`, `sBRProgVer`, "
            "`SBRProgFlvr`, `sBRRateNo`, `sBRFlag`, `lBRExpTpe`, `nInstance`) VALUES"
        )
        self.write(
            '          ( org_id, user_id, NEW.LBLDGRUNNO, correct_date, NEW.SBRPROGVER, "", '
            "NEW.SBRRATENO, NEW.SBRFLAG, NEW.LBREXPTPE, NEW.NINSTANCE );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")
        return keys[:-1], values[:-1]

    def post_simulation_task(self, source_model, destination_model, keys, values):
        self.write("\n")
        self.write("    INSERT INTO axis.remrate_data_datatracker")
        self.write(
            "      (`lBldgRunNo`, `version`, `db_major_version`, `db_minor_version`, "
            "`simulation_id`, `company_id`, `remrate_user_id`, `user_host`, `created_on`, "
            "`last_update`, `status`) VALUES"
        )
        self.write(
            "      ( NEW.LBLDGRUNNO, NEW.SBRPROGVER, major_id, minor_id, LAST_INSERT_ID(), "
            "org_id, user_id, USER(), NOW(), NOW(), -1);\n"
        )

        self.add_log(
            "after_simulation_copy_trigger",
            "CONCAT('Done lBldgRunNo: ',  lbldgrunno_id, " "' DataTracker ID:', LAST_INSERT_ID())",
            quote_msg=False,
        )

    def pre_building_task(self, source_model, destination_model):
        self.write("    DECLARE sim_id INT;")
        self.write("    DECLARE version_id varchar(12);")
        self.write("    DECLARE lbldgno_id INT;\n")

        keys, values = self.pre_simulation_task(source_model, destination_model, skip_date=True)
        self.write("    SET lbldgno_id=NEW.LBLDGNO;\n")

        self.write("    -- Figure out the lBldgRunNo")
        self.write(
            "    SELECT simulation_id, version INTO sim_id, version_id "
            "FROM axis.remrate_data_datatracker WHERE"
        )
        self.write(
            "      lBldgRunNo=NEW.lBldgRunNo AND lBldgNo IS NULL "
            "AND STATUS=-1 ORDER BY -id LIMIT 1;"
        )
        self.write(
            "    SELECT id into user_id FROM axis.remrate_remrateuser WHERE username=user_name;\n"
        )

        keys += ["simulation_id", "created_on", "last_update", "sync_status", "user_host"]
        values += ["sim_id", "NOW()", "NOW()", "-1", "USER()"]

        return keys, values

    def building_task(self, source_model, destination_model, keys=None, values=None):
        missing_fwin_floor = ["12.5", "12.99A", "13.0", "14.0", "14.1", "14.2"]
        self.write("    -- Do not push the window and wall ratios < 14.3")
        self.write("    IF version_id IN ('{}') THEN".format("', '".join(missing_fwin_floor)))
        self.write("       INSERT INTO axis.remrate_data_building")
        self.write(
            "         (`company_id`, `remrate_user_id`, `simulation_id`, `created_on`, "
            "`last_update`, `sync_status`, `user_host`, `lBldgRunNo`, `lBldgNo`, `sBUBldgNam`, "
            "`sBURateNo`, `nBUBlgType`, `fCeilAtRo`, `fCeilAtAr`, `fCeilCaRo`, `fCeilCaAr`, "
            "`fAGWCORo`, `fAGWCOAr`, `fAGWBORo`, `fAGWBOAr`, `fJoiCORo`, `fJoiCOAr`, `fJoiBORo`, "
            "`fJoiBOAr`, `fFndCORo`, `fFndCOAr`, `fFndBORo`, `fFndBOAr`, `fFrFCARo`, `fFrFCAAr`, "
            "`fWinCORo`, `fWinCOAr`, `fSkyCORo`, `fSkyCOAr`, `fDorCORo`, `fDorCOAr`, `fAMThDry`, "
            "`fWinWall`, `fWinFloor`, `sNotes`) VALUES"
        )
        self.write(
            "         ( org_id, user_id, sim_id, NOW(), NOW(), -1, USER(), NEW.LBLDGRUNNO, "
            "NEW.LBLDGNO, NEW.SBUBLDGNAM, NEW.SBURATENO, NEW.NBUBLGTYPE, NEW.FCEILATRO, "
            "NEW.FCEILATAR, NEW.FCEILCARO, NEW.FCEILCAAR, NEW.FAGWCORO, NEW.FAGWCOAR, "
            "NEW.FAGWBORO, NEW.FAGWBOAR, NEW.FJOICORO, NEW.FJOICOAR, NEW.FJOIBORO, NEW.FJOIBOAR, "
            "NEW.FFNDCORO, NEW.FFNDCOAR, NEW.FFNDBORO, NEW.FFNDBOAR, NEW.FFRFCARO, NEW.FFRFCAAR, "
            "NEW.FWINCORO, NEW.FWINCOAR, NEW.FSKYCORO, NEW.FSKYCOAR, NEW.FDORCORO, NEW.FDORCOAR, "
            "NEW.FAMTHDRY, NULL, NULL, NEW.sNotes );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")
        return keys, values

    def post_building_task(self, source_model, destination_model, keys, values):
        self.write("\n")
        self.write("    UPDATE axis.remrate_data_datatracker SET")
        self.write("      `lBldgNo`=NEW.LBLDGNO, `building_id`=LAST_INSERT_ID(),")
        self.write("      `last_update`=NOW(), `status`=0 WHERE")
        self.write(
            "      `lBldgRunNo`=NEW.lBldgRunNo AND lBldgNo IS NULL "
            "AND `status`=-1 ORDER BY -id LIMIT 1;\n"
        )

        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Done lBldgRunNo: ',  lbldgrunno_id, ' lBldgNo:', lbldgno_id, "
            "' Simulation: ', sim_id, ' Version: ', version_id)",
            quote_msg=False,
        )

    def pre_bldginfo_task(self, source_model, destination_model):
        return self.get_simulation(source_model, destination_model)

    def post_bldginfo_task(self, source_model, destination_model, keys, values):
        self.write("\n")
        self.write("    UPDATE axis.remrate_data_building SET")
        self.write("      `building_info_id`=LAST_INSERT_ID() WHERE")
        self.write(
            "      `lBldgRunNo`=NEW.lBldgRunNo AND `lBldgNo`=NEW.lBldgNo AND "
            "`simulation_id`=sim_id;\n"
        )

    def project_task(self, source_model, destination_model, keys=None, values=None):
        non_flavor = ["12.5", "12.99A", "13.0"]

        self.write("    -- Do not push the builder permits < 13.0")
        self.write("    IF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("        INSERT INTO axis.remrate_data_project")
        self.write(
            "          (`building_id`, `lBldgRunNo`, `lBldgNo`, `sPIBlgName`, `sPIPOwner`, "
            "`sPIStreet`, `sPICity`, `sPIState`, `sPIZip`, `sPIPhone`, `sPIBldrPrmt`, `SPIBuilder`,"
            " `sPIBldrStr`, `sPIBldrCty`, `sPIBldrEml`, `sPIBldrPho`, `sPIModel`, `sPIBldrDev`, "
            "`sPIRatOrg`, `sPIRatStr`, `sPIRatCity`, `sPIRatSt`, `sPIRatZip`, `sPIRatPhon`, "
            "`sPIRatWeb`, `sPIPRVDRID`, `sPIRatName`, `sPIRaterNo`, `sPIRatEMal`, `sPIRatDate`, "
            "`sPIRatngNo`, `sPIRatType`, `sPIRatReas`, `SPISAMSETID`, `sPIREGID`) VALUES"
        )
        self.write(
            "          ( bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.SPIBLGNAME, NEW.SPIPOWNER, "
            'NEW.SPISTREET, NEW.SPICITY, NEW.SPISTATE, NEW.SPIZIP, NEW.SPIPHONE, "", '
            "NEW.SPIBUILDER, NEW.SPIBLDRSTR, NEW.SPIBLDRCTY, NEW.SPIBLDREML, NEW.SPIBLDRPHO, "
            "NEW.SPIMODEL, NEW.SPIBLDRDEV, NEW.SPIRATORG, NEW.SPIRATSTR, NEW.SPIRATCITY, "
            "NEW.SPIRATST, NEW.SPIRATZIP, NEW.SPIRATPHON, NEW.SPIRATWEB, NEW.SPIPRVDRID, "
            "NEW.SPIRATNAME, NEW.SPIRATERNO, NEW.SPIRATEMAL, NEW.SPIRATDATE, NEW.SPIRATNGNO, "
            "NEW.SPIRATTYPE, NEW.SPIRATREAS, NEW.SPISAMSETID, NEW.SPIREGID );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")

        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Done lBldgNo: ',  lbldgno_id, ' Version: ', version_id)",
            quote_msg=False,
        )

        return keys, values

    def _get_fk_field(
        self, key_name, value_name, source_table, source_field, source_value, status=0
    ):
        self.write("    -- Figure out the {source_field}".format(source_field=source_field))
        self.write(
            "    SELECT axis.{source_table}.id INTO {value_name} FROM axis.{source_table}".format(  # nosec
                source_table=source_table, value_name=value_name
            )
        )
        self.write(
            "      INNER JOIN axis.remrate_data_simulation ON "
            "(axis.{source_table}.simulation_id = axis.remrate_data_simulation.id)".format(
                source_table=source_table
            )
        )
        self.write(
            "      INNER JOIN axis.remrate_data_datatracker ON "
            "(axis.remrate_data_simulation.id = axis.remrate_data_datatracker.simulation_id)"
        )
        self.write(
            "      WHERE (axis.{source_table}.lBldgRunNo = NEW.LBLDGRUNNO AND "
            "axis.{source_table}.{source_field} = NEW.{source_value} AND "
            "axis.remrate_data_datatracker.status = {status});\n".format(
                source_table=source_table,
                source_field=source_field,
                source_value=source_value,
                status=status,
            )
        )

    def pre_seasonalrate_task(self, source_model, destination_model):
        self.write("    DECLARE utility_id INT;")
        keys, values = self.get_simulation(source_model, destination_model)
        self._get_fk_field(
            "rate_id", "utility_id", "remrate_data_utilityrate", "lURURNo", "LSRURNO", "-1"
        )
        return ["rate_id"] + keys, ["utility_id"] + values

    def pre_block_task(self, source_model, destination_model):
        self.write("    DECLARE season_id INT;")
        keys, values = self.get_simulation(source_model, destination_model)
        self._get_fk_field(
            "seasonal_rate_id", "season_id", "remrate_data_seasonalrate", "lSRSRNo", "LBLSRNO", "-1"
        )
        return ["seasonal_rate_id"] + keys, ["season_id"] + values

    def pre_foundationwall_task(self, source_model, destination_model):
        self.write("    DECLARE foundation_wall_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id",
            "foundation_wall_id",
            "remrate_data_foundationwalltype",
            "lFWTWTNo",
            "LFWFWTNO",
        )
        return ["type_id"] + keys, ["foundation_wall_id"] + values

    def pre_slab_task(self, source_model, destination_model):
        self.write("    DECLARE slab_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field("type_id", "slab_id", "remrate_data_slabtype", "lSTSTNo", "LSFSLABTNO")
        return ["type_id"] + keys, ["slab_id"] + values

    def pre_comptype_task(self, source_model, destination_model, source_value):
        self.write("    DECLARE comp_type_id INT;")
        keys, values = self.get_simulation(source_model, destination_model)
        self._get_fk_field(
            "composite_type_id",
            "comp_type_id",
            "remrate_data_compositetype",
            "lTCTTCTTNo",
            source_value,
        )
        return ["composite_type_id"] + keys, ["comp_type_id"] + values

    def pre_heatpath_task(self, source_model, destination_model):
        return self.pre_comptype_task(source_model, destination_model, "LHPTCTTNO")

    def pre_ceilingtype_task(self, source_model, destination_model):
        return self.pre_comptype_task(source_model, destination_model, "LCTCOMPNO")

    def pre_roof_task(self, source_model, destination_model):
        self.write("    DECLARE ctype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id", "ctype_id", "remrate_data_ceilingtype", "lCTCTNo", "LROCEILTNO"
        )
        return ["type_id"] + keys, ["ctype_id"] + values

    def pre_walltype_task(self, source_model, destination_model):
        return self.pre_comptype_task(source_model, destination_model, "LWTCOMPNO")

    def pre_abovegradewall_task(self, source_model, destination_model):
        self.write("    DECLARE wtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field("type_id", "wtype_id", "remrate_data_walltype", "lWTWTNo", "LAGWALLTNO")
        return ["type_id"] + keys, ["wtype_id"] + values

    def pre_framefloortype_task(self, source_model, destination_model):
        return self.pre_comptype_task(source_model, destination_model, "NFTTCTNO")

    def pre_framefloor_task(self, source_model, destination_model):
        self.write("    DECLARE ftype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field("type_id", "ftype_id", "remrate_data_floortype", "lFTFTNo", "LFFFLORTNO")
        return ["type_id"] + keys, ["ftype_id"] + values

    def pre_door_task(self, source_model, destination_model):
        self.write("    DECLARE dtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field("type_id", "dtype_id", "remrate_data_doortype", "lDTDTNo", "lDODoorTNo")
        return ["type_id"] + keys, ["dtype_id"] + values

    def pre_window_task(self, source_model, destination_model):
        self.write("    DECLARE wtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id", "wtype_id", "remrate_data_windowtype", "lWDTWinNo", "lWDWinTNo"
        )
        return ["type_id"] + keys, ["wtype_id"] + values

    def pre_skylight_task(self, source_model, destination_model):
        self.write("    DECLARE wtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id", "wtype_id", "remrate_data_windowtype", "lWDTWinNo", "lSKWinTNo"
        )
        return ["type_id"] + keys, ["wtype_id"] + values

    def pre_sswindow_task(self, source_model, destination_model):
        self.write("    DECLARE wtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id", "wtype_id", "remrate_data_windowtype", "lWDTWinNo", "LSSWWDWTNO"
        )
        return ["type_id"] + keys, ["wtype_id"] + values

    def pre_sssklght_task(self, source_model, destination_model):
        self.write("    DECLARE wtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "type_id", "wtype_id", "remrate_data_windowtype", "lWDTWinNo", "LSSSWDWTNO"
        )
        return ["type_id"] + keys, ["wtype_id"] + values

    def pre_installedequipment_task(self, source_model, destination_model):
        self.write("    DECLARE htg_id INT;")
        self.write("    DECLARE gshp_id INT;")
        self.write("    DECLARE dfhp_id INT;")
        self.write("    DECLARE clg_id INT;")
        self.write("    DECLARE dhw_id INT;")
        self.write("    DECLARE ashp_id INT;")
        self.write("    DECLARE iswh_id INT;")
        self.write("    DECLARE dehumid_id INT;")
        self.write("    DECLARE shared_id INT;")

        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field("heater_id", "htg_id", "remrate_data_heater", "lHETHETNo", "LEIHETNO")
        self._get_fk_field(
            "ground_source_heat_pump_id",
            "gshp_id",
            "remrate_data_groundsourceheatpump",
            "lGSTGSTNo",
            "LEIGSTNO",
        )
        self._get_fk_field(
            "dual_fuel_heat_pump_id",
            "dfhp_id",
            "remrate_data_dualfuelheatpump",
            "lDFTDFTNo",
            "LEIDFTNO",
        )
        self._get_fk_field(
            "air_conditioner_id", "clg_id", "remrate_data_airconditioner", "lCETCETNo", "LEICLTNO"
        )
        self._get_fk_field(
            "hot_water_heater_id", "dhw_id", "remrate_data_hotwaterheater", "lDETDETNo", "LEIDHTNO"
        )
        self._get_fk_field(
            "air_source_heat_pump_id",
            "ashp_id",
            "remrate_data_airsourceheatpump",
            "lASTASTNo",
            "LEIASTNO",
        )
        self._get_fk_field(
            "integrated_space_water_heater_id",
            "iswh_id",
            "remrate_data_integratedspacewaterheater",
            "lHTDHTDNo",
            "LEIHDTNO",
        )
        self._get_fk_field(
            "dehumidifier_id", "dehumid_id", "remrate_data_dehumidifier", "lDhuEqKey", "lDhuEqKey"
        )
        self._get_fk_field(
            "shared_equipment_id",
            "shared_id",
            "remrate_data_sharedequipment",
            "lSharedEqKey",
            "lSharedEqKey",
        )

        return [
            "heater_id",
            "ground_source_heat_pump_id",
            "dual_fuel_heat_pump_id",
            "air_conditioner_id",
            "hot_water_heater_id",
            "air_source_heat_pump_id",
            "integrated_space_water_heater_id",
            "dehumidifier_id",
            "shared_equipment_id",
        ] + keys, [
            "htg_id",
            "gshp_id",
            "dfhp_id",
            "clg_id",
            "dhw_id",
            "ashp_id",
            "iswh_id",
            "dehumid_id",
            "shared_id",
        ] + values

    def pre_sharedequipment_task(self, source_model, destination_model):
        self.write("    DECLARE gshp_id INT;")
        self.write("    DECLARE wlhp_id INT;")

        keys, values = self.get_simulation(source_model, destination_model)
        self._get_fk_field(
            "ground_source_heat_pump_id",
            "gshp_id",
            "remrate_data_groundsourceheatpump",
            "lGSTGSTNo",
            "lGshpEqKey",
        )
        self._get_fk_field(
            "water_loop_heat_pump_id",
            "wlhp_id",
            "remrate_data_waterloopheatpump",
            "lWlhpEqKey",
            "lWlhpEqKey",
        )

        return ["ground_source_heat_pump_id", "water_loop_heat_pump_id"] + keys, [
            "gshp_id",
            "wlhp_id",
        ] + values

    def pre_duct_task(self, source_model, destination_model):
        self.write("    DECLARE dtype_id INT;")
        keys, values = self.get_simulation_and_building(source_model, destination_model)
        self._get_fk_field(
            "duct_system_id", "dtype_id", "remrate_data_ductsystem", "lDSDSNo", "LDUDSNO"
        )
        return ["duct_system_id"] + keys, ["dtype_id"] + values

    def pre_rejectedmeasure_task(self, source_model, destination_model, source_value="LRMCRNO"):
        self.write("    DECLARE cost_id INT;")
        keys, values = self.get_simulation(source_model, destination_model)
        self._get_fk_field(
            "cost_rate_id", "cost_id", "remrate_data_costrate", "lCRCRNo", source_value
        )
        return ["cost_rate_id"] + keys, ["cost_id"] + values

    def pre_acceptedmeasure_task(self, source_model, destination_model):
        return self.pre_rejectedmeasure_task(self, source_model, destination_model, "LAMCRNO")

    def pre_economic_task(self, source_model, destination_model):
        return self.pre_rejectedmeasure_task(self, source_model, destination_model, "LECCRNO")

    def compliance_task(self, source_model, destination_model, keys=None, values=None):
        self.write("    -- Do not push the flavor on some new compliance pieces")
        non_flavor = ["12.5", "12.99A", "13.0"]
        self.write("    IF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("       INSERT INTO axis.remrate_data_compliance")
        self.write(
            "         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, "
            "`fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, "
            "`fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, "
            "`fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, "
            "`b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, "
            "`bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, "
            "`f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, "
            "`f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, "
            "`f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, "
            "`f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, "
            "`f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, "
            "`f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, "
            "`f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, "
            "`f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, "
            "`f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, "
            "`f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, "
            "`f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, "
            "`f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, "
            "`f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, "
            "`fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, "
            "`fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, "
            "`fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, "
            "`fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, "
            "`f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, "
            "`b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, "
            "`f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, "
            "`b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, "
            "`f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, "
            "`b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, "
            "`f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, "
            "`f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, "
            "`f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, "
            "`f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, "
            "`f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, "
            "`f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, "
            "`b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, "
            "`sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, "
            "`f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, "
            "`f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, "
            "`b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`,"
            " `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES"
        )
        self.write(
            "         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, "
            "NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, "
            "NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, "
            "NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, "
            "NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, "
            "NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, "
            "NEW.BTAXCREDIT, NEW.B90_2ASCCP, NULL, NEW.F98IERHCN, NEW.F98IERCCN, NEW.F98IERDCN, "
            "NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, NEW.F98IEDCCN, "
            "NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, NEW.F00IERHCN, "
            "NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, NEW.F00IERTCN, "
            "NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, NEW.F00IEDPVCN, "
            "NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, NEW.F01IERLACN, "
            "NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, NEW.F01IEDDCN, "
            "NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, NEW.F03IERCCN, "
            "NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, NEW.F03IEDHCN, "
            "NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, NEW.F03IEDTCN, "
            "NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, NEW.F04IERPVCT, "
            "NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, NEW.F04IEDDCT, "
            "NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, NEW.F06IERHCT, "
            "NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, NEW.F06IERSVCT, "
            "NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, NEW.F06IEDLACT, "
            "NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, NEW.FNYECRCCN, "
            "NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, NEW.FNYECDHCN, "
            "NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, NEW.FNYECDTCN, "
            "NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, NEW.FNVECRPVCN, "
            "NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, NEW.FNVECDLACN, "
            "NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, NEW.B92MECDUP, "
            "NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, NEW.B93MECUOP, "
            "NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, NEW.F98IECCRUO, "
            "NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, NEW.F00IECCDUO, "
            "NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, NEW.B01IECCDUP, "
            "NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, NEW.B03IECCUOP, "
            "NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, NEW.F06IECCRUA, "
            "NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, NEW.F92MECRCCN, "
            "NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, NEW.F92MECDHCN, "
            "NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, NEW.F92MECDTCN, "
            "NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, NEW.F93MECRLCN, "
            "NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, NEW.F93MECDDCN, "
            "NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, NEW.F95MECRHCN, "
            "NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, NEW.F95MECRTCN, "
            "NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, NEW.F95MECDPCN, "
            "NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, NEW.F90_2ASRCN, "
            "NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, NEW.SRATENO, "
            "NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, NEW.F09IERPVCT, "
            "NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, NEW.F09IEDDCT, "
            "NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, NEW.F09IECCRUA, "
            "NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, NEW.BPASS04IECC, "
            "NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NULL, NULL, NULL, NULL );"
        )
        non_flavor = ["14.0", "14.1", "14.2"]
        self.write("    ELSEIF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("       INSERT INTO axis.remrate_data_compliance")
        self.write(
            "         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, "
            "`fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, "
            "`fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, "
            "`fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, "
            "`b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, "
            "`bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, "
            "`f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, "
            "`f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, "
            "`f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, "
            "`f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, "
            "`f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, "
            "`f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, "
            "`f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, "
            "`f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, "
            "`f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, "
            "`f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, "
            "`f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, "
            "`f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, "
            "`f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, "
            "`fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, "
            "`fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, "
            "`fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, "
            "`fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, "
            "`f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, "
            "`b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, "
            "`f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, "
            "`b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, "
            "`f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, "
            "`b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, "
            "`f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, "
            "`f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, "
            "`f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, "
            "`f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, "
            "`f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, "
            "`f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, "
            "`b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, "
            "`sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, "
            "`f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, "
            "`f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, "
            "`b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, `bPass12IECC`,"
            " `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES"
        )
        self.write(
            "         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS,"
            " NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, "
            "NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, "
            "NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, "
            "NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, "
            "NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, "
            "NEW.BTAXCREDIT, NEW.B90_2ASCCP, NEW.FES_SZADJF, NEW.F98IERHCN, NEW.F98IERCCN, "
            "NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, "
            "NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, "
            "NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, "
            "NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, "
            "NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, "
            "NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, "
            "NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, "
            "NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, "
            "NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, "
            "NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, "
            "NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, "
            "NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, "
            "NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, "
            "NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, "
            "NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, "
            "NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, "
            "NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, "
            "NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, "
            "NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, "
            "NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, "
            "NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, "
            "NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, "
            "NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, "
            "NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, "
            "NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, "
            "NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, "
            "NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, "
            "NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, "
            "NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, "
            "NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, "
            "NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, "
            "NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, "
            "NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, "
            "NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, "
            "NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, "
            "NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, "
            "NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, "
            "NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, "
            "NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, "
            "NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, "
            "NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NULL, "
            "NEW.FHERS130, NULL, NULL );"
        )
        non_flavor = ["14.3"]
        self.write("    ELSEIF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("       INSERT INTO axis.remrate_data_compliance")
        self.write(
            "         (`simulation_id`, `lBldgRunNo`, `fHERSScor`, `fHERS_PV`, `fES_HERS`, "
            "`fES_HERSSA`, `fHERSCost`, `fHERSStars`, `fHERSRHCn`, `fHERSRCCn`, `fHERSRDCN`, "
            "`fHERSRLACn`, `fHERSRPVCn`, `fHERSRTCn`, `fHERSDHCn`, `fHERSDCCn`, `fHERSDDCN`, "
            "`fHERSDLACn`, `fHERSDPVCn`, `fHERSDTCn`, `b98IECC`, `b00IECC`, `b01IECC`, `b03IECC`, "
            "`b04IECC`, `b06IECC`, `b09IECC`, `bNYECC`, `bNVECC`, `bEStarv2`, `bEStarv25`, "
            "`bEStarv3`, `bTaxCredit`, `b90_2ASCCP`, `FES_SZADJF`, `f98IERHCn`, `f98IERCCn`, "
            "`f98IERDCN`, `f98IERLACn`, `f98IERPVCn`, `f98IERTCn`, `f98IEDHCn`, `f98IEDCCn`, "
            "`f98IEDDCN`, `f98IEDLACn`, `f98IEDPVCn`, `f98IEDTCn`, `f00IERHCn`, `f00IERCCn`, "
            "`f00IERDCN`, `f00IERLACn`, `f00IERPVCn`, `f00IERTCn`, `f00IEDHCn`, `f00IEDCCn`, "
            "`f00IEDDCN`, `f00IEDLACn`, `f00IEDPVCn`, `f00IEDTCn`, `f01IERHCn`, `f01IERCCn`, "
            "`f01IERDCN`, `f01IERLACn`, `f01IERPVCn`, `f01IERTCn`, `f01IEDHCn`, `f01IEDCCn`, "
            "`f01IEDDCN`, `f01IEDLACn`, `f01IEDPVCn`, `f01IEDTCn`, `f03IERHCn`, `f03IERCCn`, "
            "`f03IERDCN`, `f03IERLACn`, `f03IERPVCn`, `f03IERTCn`, `f03IEDHCn`, `f03IEDCCn`, "
            "`f03IEDDCN`, `f03IEDLACn`, `f03IEDPVCn`, `f03IEDTCn`, `f04IERHCT`, `f04IERCCT`, "
            "`f04IERDCT`, `f04IERLACT`, `f04IERPVCT`, `f04IERSVCT`, `f04IERTCT`, `f04IEDHCT`, "
            "`f04IEDCCT`, `f04IEDDCT`, `f04IEDLACT`, `f04IEDPVCT`, `f04IEDSVCT`, `f04IEDTCT`, "
            "`f06IERHCT`, `f06IERCCT`, `f06IERDCT`, `f06IERLACT`, `f06IERPVCT`, `f06IERSVCT`, "
            "`f06IERTCT`, `f06IEDHCT`, `f06IEDCCT`, `f06IEDDCT`, `f06IEDLACT`, `f06IEDPVCT`, "
            "`f06IEDSVCT`, `f06IEDTCT`, `fNYECRHCn`, `fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, "
            "`fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, `fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, "
            "`fNYECDPVCn`, `fNYECDTCn`, `fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, "
            "`fNVECRPVCn`, `fNVECRTCn`, `fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, "
            "`fNVECDPVCn`, `fNVECDTCn`, `f92MECReUo`, `f92MECADUo`, `b92MECDuP`, `b92MECuoP`, "
            "`f93MECReUo`, `f93MECADUo`, `b93MECDuP`, `b93MECuoP`, `f95MECReUo`, `f95MECADUo`, "
            "`b95MECDuP`, `b95MECuoP`, `f98IECCRUo`, `f98IECCDUo`, `b98IECCDuP`, `b98IECCuoP`, "
            "`f00IECCRUo`, `f00IECCDUo`, `b00IECCDuP`, `b00IECCuoP`, `f01IECCRUo`, `f01IECCDUo`, "
            "`b01IECCDuP`, `b01IECCuoP`, `f03IECCRUo`, `f03IECCDUo`, `b03IECCDuP`, `b03IECCuoP`, "
            "`f04IECCRUA`, `f04IECCDUA`, `b04IECCDuP`, `b04IECCuAP`, `f06IECCRUA`, `f06IECCDUA`, "
            "`b06IECCDuP`, `b06IECCuAP`, `f92MECRHCn`, `f92MECRCCn`, `f92MECRDCn`, `f92MECRLCn`, "
            "`f92MECRPCn`, `f92MECRTCn`, `f92MECDHCn`, `f92MECDCCn`, `f92MECDDCn`, `f92MECDLCn`, "
            "`f92MECDPCn`, `f92MECDTCn`, `b92MECCC`, `f93MECRHCn`, `f93MECRCCn`, `f93MECRDCn`, "
            "`f93MECRLCn`, `f93MECRPCn`, `f93MECRTCn`, `f93MECDHCn`, `f93MECDCCn`, `f93MECDDCn`, "
            "`f93MECDLCn`, `f93MECDPCn`, `f93MECDTCn`, `b93MECCC`, `f95MECRHCn`, `f95MECRCCn`, "
            "`f95MECRDCN`, `f95MECRLCn`, `f95MECRPCn`, `f95MECRTCn`, `f95MECDHCn`, `f95MECDCCn`, "
            "`f95MECDDCN`, `f95MECDLCn`, `f95MECDPCn`, `f95MECDTCn`, `b95MECCC`, `f90_2ASLC`, "
            "`b90_2ASECP`, `f90_2ASRCn`, `f90_2ASRCt`, `f90_2ASDCn`, `f90_2ASDCt`, `FNYHERS`, "
            "`sRateNo`, `f09IERHCT`, `f09IERCCT`, `f09IERDCT`, `f09IERLACT`, `f09IERPVCT`, "
            "`f09IERSVCT`, `f09IERTCT`, `f09IEDHCT`, `f09IEDCCT`, `f09IEDDCT`, `f09IEDLACT`, "
            "`f09IEDPVCT`, `f09IEDSVCT`, `f09IEDTCT`, `f09IECCRUA`, `f09IECCDUA`, `b09IECCDuP`, "
            "`b09IECCuAP`, `fNVRebate`, `bPass04IECC`, `bPass06IECC`, `bPass09IECC`, "
            "`bPass12IECC`, `bDOECHALL`, `FHERS130`, `FDOE_Hers`, `FDOE_HersSA`) VALUES"
        )
        self.write(
            "         ( sim_id, NEW.LBLDGRUNNO, NEW.FHERSSCOR, NEW.FHERS_PV, NEW.FES_HERS, "
            "NEW.FES_HERSSA, NEW.FHERSCOST, NEW.FHERSSTARS, NEW.FHERSRHCN, NEW.FHERSRCCN, "
            "NEW.FHERSRDCN, NEW.FHERSRLACN, NEW.FHERSRPVCN, NEW.FHERSRTCN, NEW.FHERSDHCN, "
            "NEW.FHERSDCCN, NEW.FHERSDDCN, NEW.FHERSDLACN, NEW.FHERSDPVCN, NEW.FHERSDTCN, "
            "NEW.B98IECC, NEW.B00IECC, NEW.B01IECC, NEW.B03IECC, NEW.B04IECC, NEW.B06IECC, "
            "NEW.B09IECC, NEW.BNYECC, NEW.BNVECC, NEW.BESTARV2, NEW.BESTARV25, NEW.BESTARV3, "
            "NEW.BTAXCREDIT, NEW.B90_2ASCCP, NEW.FES_SZADJF, NEW.F98IERHCN, NEW.F98IERCCN, "
            "NEW.F98IERDCN, NEW.F98IERLACN, NEW.F98IERPVCN, NEW.F98IERTCN, NEW.F98IEDHCN, "
            "NEW.F98IEDCCN, NEW.F98IEDDCN, NEW.F98IEDLACN, NEW.F98IEDPVCN, NEW.F98IEDTCN, "
            "NEW.F00IERHCN, NEW.F00IERCCN, NEW.F00IERDCN, NEW.F00IERLACN, NEW.F00IERPVCN, "
            "NEW.F00IERTCN, NEW.F00IEDHCN, NEW.F00IEDCCN, NEW.F00IEDDCN, NEW.F00IEDLACN, "
            "NEW.F00IEDPVCN, NEW.F00IEDTCN, NEW.F01IERHCN, NEW.F01IERCCN, NEW.F01IERDCN, "
            "NEW.F01IERLACN, NEW.F01IERPVCN, NEW.F01IERTCN, NEW.F01IEDHCN, NEW.F01IEDCCN, "
            "NEW.F01IEDDCN, NEW.F01IEDLACN, NEW.F01IEDPVCN, NEW.F01IEDTCN, NEW.F03IERHCN, "
            "NEW.F03IERCCN, NEW.F03IERDCN, NEW.F03IERLACN, NEW.F03IERPVCN, NEW.F03IERTCN, "
            "NEW.F03IEDHCN, NEW.F03IEDCCN, NEW.F03IEDDCN, NEW.F03IEDLACN, NEW.F03IEDPVCN, "
            "NEW.F03IEDTCN, NEW.F04IERHCT, NEW.F04IERCCT, NEW.F04IERDCT, NEW.F04IERLACT, "
            "NEW.F04IERPVCT, NEW.F04IERSVCT, NEW.F04IERTCT, NEW.F04IEDHCT, NEW.F04IEDCCT, "
            "NEW.F04IEDDCT, NEW.F04IEDLACT, NEW.F04IEDPVCT, NEW.F04IEDSVCT, NEW.F04IEDTCT, "
            "NEW.F06IERHCT, NEW.F06IERCCT, NEW.F06IERDCT, NEW.F06IERLACT, NEW.F06IERPVCT, "
            "NEW.F06IERSVCT, NEW.F06IERTCT, NEW.F06IEDHCT, NEW.F06IEDCCT, NEW.F06IEDDCT, "
            "NEW.F06IEDLACT, NEW.F06IEDPVCT, NEW.F06IEDSVCT, NEW.F06IEDTCT, NEW.FNYECRHCN, "
            "NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, "
            "NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, "
            "NEW.FNYECDTCN, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, NEW.FNVECRLACN, "
            "NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, NEW.FNVECDDCN, "
            "NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.F92MECREUO, NEW.F92MECADUO, "
            "NEW.B92MECDUP, NEW.B92MECUOP, NEW.F93MECREUO, NEW.F93MECADUO, NEW.B93MECDUP, "
            "NEW.B93MECUOP, NEW.F95MECREUO, NEW.F95MECADUO, NEW.B95MECDUP, NEW.B95MECUOP, "
            "NEW.F98IECCRUO, NEW.F98IECCDUO, NEW.B98IECCDUP, NEW.B98IECCUOP, NEW.F00IECCRUO, "
            "NEW.F00IECCDUO, NEW.B00IECCDUP, NEW.B00IECCUOP, NEW.F01IECCRUO, NEW.F01IECCDUO, "
            "NEW.B01IECCDUP, NEW.B01IECCUOP, NEW.F03IECCRUO, NEW.F03IECCDUO, NEW.B03IECCDUP, "
            "NEW.B03IECCUOP, NEW.F04IECCRUA, NEW.F04IECCDUA, NEW.B04IECCDUP, NEW.B04IECCUAP, "
            "NEW.F06IECCRUA, NEW.F06IECCDUA, NEW.B06IECCDUP, NEW.B06IECCUAP, NEW.F92MECRHCN, "
            "NEW.F92MECRCCN, NEW.F92MECRDCN, NEW.F92MECRLCN, NEW.F92MECRPCN, NEW.F92MECRTCN, "
            "NEW.F92MECDHCN, NEW.F92MECDCCN, NEW.F92MECDDCN, NEW.F92MECDLCN, NEW.F92MECDPCN, "
            "NEW.F92MECDTCN, NEW.B92MECCC, NEW.F93MECRHCN, NEW.F93MECRCCN, NEW.F93MECRDCN, "
            "NEW.F93MECRLCN, NEW.F93MECRPCN, NEW.F93MECRTCN, NEW.F93MECDHCN, NEW.F93MECDCCN, "
            "NEW.F93MECDDCN, NEW.F93MECDLCN, NEW.F93MECDPCN, NEW.F93MECDTCN, NEW.B93MECCC, "
            "NEW.F95MECRHCN, NEW.F95MECRCCN, NEW.F95MECRDCN, NEW.F95MECRLCN, NEW.F95MECRPCN, "
            "NEW.F95MECRTCN, NEW.F95MECDHCN, NEW.F95MECDCCN, NEW.F95MECDDCN, NEW.F95MECDLCN, "
            "NEW.F95MECDPCN, NEW.F95MECDTCN, NEW.B95MECCC, NEW.F90_2ASLC, NEW.B90_2ASECP, "
            "NEW.F90_2ASRCN, NEW.F90_2ASRCT, NEW.F90_2ASDCN, NEW.F90_2ASDCT, NEW.FNYHERS, "
            "NEW.SRATENO, NEW.F09IERHCT, NEW.F09IERCCT, NEW.F09IERDCT, NEW.F09IERLACT, "
            "NEW.F09IERPVCT, NEW.F09IERSVCT, NEW.F09IERTCT, NEW.F09IEDHCT, NEW.F09IEDCCT, "
            "NEW.F09IEDDCT, NEW.F09IEDLACT, NEW.F09IEDPVCT, NEW.F09IEDSVCT, NEW.F09IEDTCT, "
            "NEW.F09IECCRUA, NEW.F09IECCDUA, NEW.B09IECCDUP, NEW.B09IECCUAP, NEW.FNVREBATE, "
            "NEW.BPASS04IECC, NEW.BPASS06IECC, NEW.BPASS09IECC, NEW.BPASS12IECC, NEW.BDOECHALL, "
            "NEW.FHERS130, NULL, NULL );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")

        self.write("    INSERT INTO axis.remrate_data_regionalcode")
        self.write(
            "      (`simulation_id`, `lBldgRunNo`, `SRATENO`, `fNVRebate`, `fNYECRHCn`, "
            "`fNYECRCCn`, `fNYECRDCN`, `fNYECRLACn`, `fNYECRPVCn`, `fNYECRTCn`, `fNYECDHCn`, "
            "`fNYECDCCn`, `fNYECDDCN`, `fNYECDLACn`, `fNYECDPVCn`, `fNYECDTCn`, `bNYECC`, "
            "`fNVECRHCn`, `fNVECRCCn`, `fNVECRDCN`, `fNVECRLACn`, `fNVECRPVCn`, `fNVECRTCn`, "
            "`fNVECDHCn`, `fNVECDCCn`, `fNVECDDCN`, `fNVECDLACn`, `fNVECDPVCn`, `fNVECDTCn`, "
            "`bNVECC`) VALUES"
        )
        self.write(
            "      ( sim_id, NEW.LBLDGRUNNO, NEW.SRATENO, NEW.FNVREBATE, NEW.FNYECRHCN, "
            "NEW.FNYECRCCN, NEW.FNYECRDCN, NEW.FNYECRLACN, NEW.FNYECRPVCN, NEW.FNYECRTCN, "
            "NEW.FNYECDHCN, NEW.FNYECDCCN, NEW.FNYECDDCN, NEW.FNYECDLACN, NEW.FNYECDPVCN, "
            "NEW.FNYECDTCN, NEW.BNYECC, NEW.FNVECRHCN, NEW.FNVECRCCN, NEW.FNVECRDCN, "
            "NEW.FNVECRLACN, NEW.FNVECRPVCN, NEW.FNVECRTCN, NEW.FNVECDHCN, NEW.FNVECDCCN, "
            "NEW.FNVECDDCN, NEW.FNVECDLACN, NEW.FNVECDPVCN, NEW.FNVECDTCN, NEW.BNVECC);"
        )

        self.write("    INSERT INTO axis.remrate_data_energystar")
        self.write(
            "      (`simulation_id`, "
            "`lBldgRunNo`, "
            "`SRATENO`, "
            "`BESTARV2`, "
            "`BESTARV25`, "
            "`BESTARV3`, "
            "`FV25HERSPV`, "
            "`FV25HERS`, "
            "`FV25HERSSA`, "
            "`FV25SZADJF`, "
            "`BESTARV3HI`, "
            "`BESTARV31`, "
            "`BDOEPROGRAM`, "
            "`FDOEHERS`, "
            "`FDOEHERSSA`) VALUES"
        )
        self.write(
            "      ( sim_id, "
            "NEW.LBLDGRUNNO, "
            "NEW.SRATENO, "
            "NEW.BESTARV2, "
            "NEW.BESTARV25, "
            "NEW.BESTARV3, "
            "NEW.FHERS_PV, "
            "NEW.FES_HERS, "
            "NEW.FES_HERSSA, "
            "NEW.FES_SZADJF, "
            "NEW.BESTARV3HI, "
            "NEW.BESTARV31, "
            "NEW.BDOECHALL, "
            "NEW.FDOE_HERS, "
            "NEW.FDOE_HersSA);"
        )

        self.write("    INSERT INTO axis.remrate_data_hers")
        self.write(
            "      (`simulation_id`, "
            "`lBldgRunNo`, "
            "`SRATENO`, "
            "`fHERSScor`, "
            "`fHERSCost`, "
            "`fHERSStars`, "
            "`fHERSRHCn`, "
            "`fHERSRCCn`, "
            "`fHERSRDCN`, "
            "`fHERSRLACn`, "
            "`fHERSRPVCn`, "
            "`fHERSRTCn`, "
            "`fHERSDHCn`, "
            "`fHERSDCCn`, "
            "`fHERSDDCN`, "
            "`fHERSDLACn`, "
            "`fHERSDPVCn`, "
            "`fHERSDTCn`, "
            "`FNYHERS`, "
            "`bTaxCredit`, "
            "`FHERS130`) VALUES"
        )
        self.write(
            "      ( sim_id, "
            "NEW.LBLDGRUNNO, "
            "NEW.SRATENO, "
            "NEW.FHERSSCOR, "
            "NEW.FHERSCOST, "
            "NEW.FHERSSTARS, "
            "NEW.FHERSRHCN, "
            "NEW.FHERSRCCN, "
            "NEW.FHERSRDCN, "
            "NEW.FHERSRLACN, "
            "NEW.FHERSRPVCN, "
            "NEW.FHERSRTCN, "
            "NEW.FHERSDHCN, "
            "NEW.FHERSDCCN, "
            "NEW.FHERSDDCN, "
            "NEW.FHERSDLACN, "
            "NEW.FHERSDPVCN, "
            "NEW.FHERSDTCN, "
            "NEW.FNYHERS, "
            "NEW.BTAXCREDIT, "
            "NEW.FHERS130);"
        )

        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Done lBldgRunNo: ',  lbldgrunno_id, ' Simulation: ', "
            "sim_id, ' Version: ', version_id)",
            quote_msg=False,
        )

        return keys, values

    def mandreq_task(self, source_model, destination_model, keys=None, values=None):
        non_flavor = ["12.5", "12.99A", "13.0", "14.0", "14.1", "14.2", "14.3"]
        self.write("    -- Do not push the Slab and Florida < 14.4")
        self.write("    IF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("       INSERT INTO axis.remrate_data_mandatoryrequirements")
        self.write(
            "         (`simulation_id`, `building_id`, `lBldgRunNo`, `lBldgNo`, `nMRIECC04`, "
            "`nMRIECC06`, `nMRIECC09`, `nMRESV2TBC`, `nMRESV2PRD`, `nMRESV3TEC`, `nMRESV3HC`, "
            "`nMRESV3HR`, `nMRESV3WM`, `nMRESV3AP`, `nMRESV3RF`, `nMRESV3CF`, `nMRESV3EF`, "
            "`nMRESV3DW`, `nMRESV3NRF`, `nMRESV3NCF`, `nMRESV3NEF`, `nMRESV3NDW`, `sMRRateNo`, "
            "`nMRIECCNY`, `nMRESV3SAF`, `fMRESV3BFA`, `nMRESV3NBB`, `nMRIECC12`, `NMRFLORIDA`, "
            "`NMRESV3SLAB`) VALUES"
        )
        self.write(
            "         ( sim_id, bldg_id, NEW.LBLDGRUNNO, NEW.LBLDGNO, NEW.NMRIECC04, "
            "NEW.NMRIECC06, NEW.NMRIECC09, NEW.NMRESV2TBC, NEW.NMRESV2PRD, NEW.NMRESV3TEC, "
            "NEW.NMRESV3HC, NEW.NMRESV3HR, NEW.NMRESV3WM, NEW.NMRESV3AP, NEW.NMRESV3RF, "
            "NEW.NMRESV3CF, NEW.NMRESV3EF, NEW.NMRESV3DW, NEW.NMRESV3NRF, NEW.NMRESV3NCF, "
            "NEW.NMRESV3NEF, NEW.NMRESV3NDW, NEW.SMRRATENO, NEW.NMRIECCNY, NEW.nMRESV3SAF, "
            "NEW.fMRESV3BFA, NEW.nMRESV3NBB, NEW.NMRIECC12, 0, 0 );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")

        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Done lBldgRunNo: ',  lbldgrunno_id, ' lBldgNo:', lbldgno_id, "
            "' Simulation: ', sim_id, ' Version: ', version_id)",
            quote_msg=False,
        )
        return keys, values

    def fuelsummary_task(self, source_model, destination_model, keys=None, values=None):
        non_flavor = ["12.5", "12.99A", "13.0"]
        self.write("    -- Do not push the fFSTotCons versions < 14.0")
        self.write("    IF version_id IN ('{}') THEN".format("', '".join(non_flavor)))
        self.write("       INSERT INTO axis.remrate_data_fuelsummary")
        self.write(
            "         (`simulation_id`, `lBldgRunNo`, `nFSFuel`, `nFSUnits`, `fFSHCons`, "
            "`fFSCCons`, `fFSWCons`, `fFSLACons`, `fFSTotCost`, `fFSPVCons`, `sRateNo`, "
            "`fFSTotCons` ) VALUES"
        )
        self.write(
            "         ( sim_id, NEW.LBLDGRUNNO, NEW.NFSFUEL, NEW.NFSUNITS, NEW.FFSHCONS, "
            "NEW.FFSCCONS, NEW.FFSWCONS, NEW.FFSLACONS, NEW.FFSTOTCOST, NEW.FFSPVCONS, "
            "NEW.SRATENO, NULL );"
        )
        self.write("    ELSE")
        keys, values = self.add_basic_insert(
            source_model, destination_model, keys, values, indent=4
        )
        self.write("    END IF;")

        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Done lBldgRunNo: ',  lbldgrunno_id, ' Simulation: ', sim_id, "
            "' Version: ', version_id)",
            quote_msg=False,
        )

        return keys, values

    def post_site_task(self, source_model, destination_model, keys, values):
        self.write("\n")
        self.write("    UPDATE axis.remrate_data_datatracker SET")
        self.write("      `status`=1, `last_update`=NOW() WHERE")
        self.write("      `lBldgRunNo`=NEW.lBldgRunNo AND `simulation_id`=sim_id AND `status`=0;")
        self.write("    UPDATE axis.remrate_data_building SET")
        self.write("      `sync_status`=1, `last_update`=NOW() WHERE")
        self.write("      `lBldgRunNo`=NEW.LBLDGRUNNO AND `simulation_id`=sim_id;\n")
        self.add_log(
            source_model._meta.model_name.lower(),
            "CONCAT('Fully Done lBldgRunNo: ',  lbldgrunno_id, ' Simulation: ', "
            "sim_id, ' Version: ', version_id)",
            quote_msg=False,
        )

    def build(self):
        self.write("\nDELIMITER $$")

        # These can be removed after the first round..

        for idx, (source_model_name, destination_model_name) in enumerate(TABLE_MAP):
            keys, values = [], []
            option_dict, t_option_dict = {}, {}
            if isinstance(destination_model_name, (list, tuple)):
                destination_model_name, t_option_dict = destination_model_name
                assert isinstance(option_dict, dict), "Expected a dictionary"

            SourceModelObj = self.get_source_model(source_model_name)
            DestinationModelObj = self.get_destination_model(destination_model_name)

            self.add_drop_trigger(SourceModelObj)
            self.add_create_trigger(SourceModelObj)
            self.write(
                "\n    -- Trigger #: {} of {} Source: {} Target: {} --\n".format(
                    idx + 1,
                    len(TABLE_MAP),
                    SourceModelObj._meta.db_table,
                    DestinationModelObj._meta.db_table,
                )
            )

            task = "pre_{}_task".format(SourceModelObj._meta.model_name.lower())
            if hasattr(self, task):
                keys, values = getattr(self, task)(SourceModelObj, DestinationModelObj)
            else:
                fks = [
                    x.name
                    for x in DestinationModelObj._meta.fields
                    if hasattr(x, "related_model") and x.related_model
                ]
                log.debug("%s Foreign Keys = %s", DestinationModelObj._meta.verbose_name, fks)
                if "simulation" in fks and "building" in fks:
                    keys, values = self.get_simulation_and_building(
                        SourceModelObj, DestinationModelObj
                    )
                elif "simulation" in fks:
                    keys, values = self.get_simulation(SourceModelObj, DestinationModelObj)
                elif "building" in fks:
                    keys, values = self.get_building(SourceModelObj, DestinationModelObj)

            task = "{}_task".format(SourceModelObj._meta.model_name.lower())
            if hasattr(self, task):
                keys, values = getattr(self, task)(
                    SourceModelObj, DestinationModelObj, keys, values
                )
            else:
                keys, values = self.add_basic_insert(
                    SourceModelObj, DestinationModelObj, keys, values
                )

            task = "post_{}_task".format(SourceModelObj._meta.model_name.lower())
            if hasattr(self, task):
                getattr(self, task)(SourceModelObj, DestinationModelObj, keys, values)

            self.write("\n    -- Done doing stuff.. --\n")
            self.add_end_trigger(SourceModelObj)
            self.source_models.pop(self.source_models.index(SourceModelObj))

        if len(self.source_models) > 1:
            for model in self.source_models:
                if model._meta.db_table.lower() == "version":
                    continue
                log.error("Missing Model %s", model._meta.verbose_name)

        self.write("DELIMITER ;")
