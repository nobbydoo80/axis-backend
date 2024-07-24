"""base.py: Django Base Calculator"""

import logging
import re
from collections import OrderedDict

from django.apps import apps
from simulation.models import Simulation

from .. import constants, ETO_GEN2
from ..base import EPSInputException
from ..data_models import ModeledInput, SimulatedInput, SimulationInput

__author__ = "Steven K"
__date__ = "08/21/2019 16:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


class BaseEPSCalculator(object):  # pylint: disable=too-many-instance-attributes
    """Base EPS Calculator"""

    def __init__(self, **kwargs):  # pylint: disable=too-many-statements  # noqa: MC0001
        # Move things to the way we want them if providing a straight dictionary.
        _code_data, _improved_data = {}, {}
        for key, value in list(kwargs.items()):
            match = re.match(r"code_(.*)", key)
            if match and key != "code_data":
                _code_data[match.group(1)] = value
                kwargs.pop(key)
                continue
            match = re.match(r"improved_(.*)", key)
            if match and key != "improved_data":
                _improved_data[match.group(1)] = value
                kwargs.pop(key)
                continue

        if _code_data or _improved_data:
            kwargs["code_data"] = kwargs.get("code_data", {})
            kwargs["improved_data"] = kwargs.get("improved_data", {})
            kwargs["code_data"].update(_code_data)
            kwargs["improved_data"].update(_improved_data)

        self.input_site_address = self.site_address = kwargs.get("site_address")  # Not really used.

        self.input_mode = kwargs.get("mode")

        self.input_us_state = kwargs.get("us_state")
        self.us_state = self.normalize_us_state(self.input_us_state)

        self.input_program = kwargs.get("program")
        self.program = self.normalize_program(self.input_program)

        self.constants = self.get_constants(program=self.program, us_state=self.us_state)

        self.primary_heat_type = None
        self.input_primary_heat_type = kwargs.get("primary_heating_equipment_type")
        if self.input_primary_heat_type is not None:
            self.primary_heat_type = self.normalize_primary_heat_type(self.input_primary_heat_type)
            self.heat_type = self.normalize_heat_type_from_primary(self.primary_heat_type)
        else:
            if self.program not in [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
                if kwargs.get("heat_type"):
                    msg = "No longer supported for use `primary_heating_equipment_type`"
                    raise DeprecationWarning(msg)
            self.input_heat_type = kwargs.get("heat_type")
            self.heat_type = self.normalize_heat_type(self.input_heat_type)

        self.input_pathway = kwargs.get("pathway")
        self.pathway = self.normalize_pathway(self.input_pathway)

        self.input_electric_utility = kwargs.get("electric_utility")
        self.electric_utility = self.normalize_electric_utility(self.input_electric_utility)

        self.input_gas_utility = kwargs.get("gas_utility")
        self.gas_utility = self.normalize_gas_utility(self.input_gas_utility)

        if self.input_electric_utility is None and self.input_gas_utility is None:
            log.info("No Gas or Electricity Utility was provided")

        self.input_builder = kwargs.get("builder")
        self.builder = self.normalize_builder(self.input_builder)
        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            if self.builder is None:
                log.info("No builder was provided")

        self.input_generated_solar_pv_kwh = kwargs.get("generated_solar_pv_kwh", 0)
        self.generated_solar_pv_kwh = self.normalize_generated_solar_pv_kwh(
            self.input_generated_solar_pv_kwh
        )

        _gen_solar_pv_kwh = None
        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018"]:
            _gen_solar_pv_kwh = self.generated_solar_pv_kwh
        modeling_data = {"generated_solar_pv_kwh": _gen_solar_pv_kwh}

        if kwargs.get("simulation"):
            kwargs["simulation_id"] = kwargs.pop("simulation").id

        self.legacy_simulation = kwargs.get("use_legacy_simulation", app.USE_LEGACY_SIMULATION)
        if kwargs.get("simulation_id"):
            self.using_simulation = True
            non_solar_data_sim = None
            if not self.legacy_simulation:
                code_data_sim = improved_data_sim = Simulation.objects.get(
                    id=kwargs.get("simulation_id")
                )
                data_model = SimulationInput
            else:
                pre_2020 = ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]
                if self.program not in pre_2020:
                    log.warning(
                        "EPS Calculator found to be running legacy REM Simulation Model (%s)"
                        % kwargs["simulation_id"]
                    )
                _improved = kwargs.get("simulation_id")
                input_data = self.set_code_inputs(_improved, kwargs.get("code_simulation_id"))
                code_data_sim, improved_data_sim, non_solar_data_sim = input_data
                data_model = ModeledInput

            solar_data = {}
            if non_solar_data_sim:
                solar_data = self.normalize_solar_data(
                    data_model(simulation=non_solar_data_sim),
                    data_model(simulation=improved_data_sim),
                )
        elif kwargs.get("code_data") and kwargs.get("improved_data"):
            self.using_simulation = False
            input_data = self.set_manual_code_inputs(
                kwargs.get("code_data"), kwargs.get("improved_data")
            )
            code_data_sim, improved_data_sim, solar_data = input_data

            # These are keys we will provide as they are provided by REM/Rate®.
            # Only pass in what the simulation components actually need.
            update_keys = ["has_ashp", "gas_furnace_afue"]
            modeling_data.update({k: kwargs.get(k) for k in update_keys if kwargs.get(k)})
            data_model = SimulatedInput
        else:
            msg = "You must provide either an improved_simulation_id or code_data / improved_data"
            raise EPSInputException(msg)

        modeling_data.update(solar_data)

        self.code_data = data_model(simulation=code_data_sim, **modeling_data)
        self.improved_data = data_model(
            simulation=improved_data_sim, is_improved=True, **modeling_data
        )
        self.has_solar_hot_water = self.improved_data.has_solar_hot_water
        self.has_gas_hot_water = self.improved_data.has_gas_hot_water

        try:
            self.input_location = self.improved_data.location
        except AttributeError:
            self.input_location = kwargs.get("location")
        self.location = self.normalize_location(self.input_location, kwargs.get("location"))

        try:
            self.input_has_tankless_water_heater = self.improved_data.has_tankless_water_heater
        except AttributeError:
            self.input_has_tankless_water_heater = kwargs.get("has_tankless_water_heater", False)
        self.has_tankless_water_heater = self.normalize_tankless_water_heater(
            self.input_has_tankless_water_heater, kwargs.get("has_tankless_water_heater")
        )

        try:
            self.input_has_heat_pump_water_heater = self.improved_data.has_heat_pump_water_heater
        except AttributeError:
            self.input_has_heat_pump_water_heater = kwargs.get("has_heat_pump_water_heater", False)
        self.has_heat_pump_water_heater = self.normalize_tankless_water_heater(
            self.input_has_heat_pump_water_heater, kwargs.get("has_heat_pump_water_heater")
        )

        try:
            self.input_hot_water_ef = self.improved_data.hot_water_ef
        except AttributeError:
            self.input_hot_water_ef = float(kwargs.get("hot_water_ef") or 0.0)
        self.hot_water_ef = self.normalize_hot_water_ef(
            self.input_hot_water_ef, kwargs.get("hot_water_ef")
        )

        try:
            self.input_conditioned_area = self.improved_data.conditioned_area
        except AttributeError:
            self.input_conditioned_area = float(kwargs.get("conditioned_area", 0.0))
        self.conditioned_area = self.normalize_conditioned_area(
            self.input_conditioned_area, kwargs.get("conditioned_area")
        )

        self.input_smart_thermostat_brand = kwargs.get("smart_thermostat_brand")
        self.smart_thermostat_brand = self.normalize_smart_thermostat_brand(
            self.input_smart_thermostat_brand
        )

        self.input_qualifying_thermostat = kwargs.get("qualifying_thermostat", False)
        if self.input_smart_thermostat_brand:
            # Override what was put in.
            self.input_qualifying_thermostat = self.normalize_qualifying_thermostat_from_brand(
                self.smart_thermostat_brand, self.primary_heat_type
            )

        tstat_info = self.normalize_smart_thermostat(self.input_qualifying_thermostat)
        self.smart_thermostat, self.smart_thermostat_furnace_type = tstat_info

        if self.smart_thermostat:
            self.validate_furnace_type(self.smart_thermostat_furnace_type)

        self.input_qty_shower_head_1p5 = kwargs.get("qty_shower_head_1p5", 0)
        self.qty_shower_head_1p5 = self.normalize_shower_head(self.input_qty_shower_head_1p5)

        self.input_qty_shower_head_1p6 = kwargs.get("qty_shower_head_1p6", 0)
        self.qty_shower_head_1p6 = self.normalize_shower_head(self.input_qty_shower_head_1p6)

        self.input_qty_shower_head_1p75 = kwargs.get("qty_shower_head_1p75", 0)
        self.qty_shower_head_1p75 = self.normalize_shower_head(self.input_qty_shower_head_1p75)

        self.input_qty_shower_wand_1p5 = kwargs.get("qty_shower_wand_1p5", 0)
        self.qty_shower_wand_1p5 = self.normalize_shower_head(self.input_qty_shower_wand_1p5)

        self.input_has_gas_fireplace = kwargs.get("has_gas_fireplace", "No fireplace")
        self.has_gas_fireplace = self.normalize_has_gas_fireplace(self.input_has_gas_fireplace)

        self.input_grid_harmonization_elements = kwargs.get("grid_harmonization_elements")
        self.grid_harmonization_elements = self.normalize_grid_harmonization_elements(
            self.input_grid_harmonization_elements
        )

        self.input_eps_additional_incentives = kwargs.get("eps_additional_incentives", "No")
        self.eps_additional_incentives = self.normalize_eps_additional_incentives(
            self.input_eps_additional_incentives
        )
        self.input_solar_elements = kwargs.get("solar_elements", "None")
        self.solar_elements = self.normalize_solar_elements(self.input_solar_elements)

    def normalize_us_state(self, input_name):
        """Normalize a US State"""
        if input_name is None:
            if self.input_mode == "swwa":
                return "WA"
            log.info("State was not provided")
            return None
        if input_name.lower() not in ["or", "wa"]:
            raise EPSInputException("State must be either 'OR' or 'WA'")
        return input_name.upper()

    def normalize_program(self, input_name):
        """Normalize EEP Program to it's slug."""
        from axis.eep_program.models import EEPProgram

        if input_name is None:
            log.debug("Program was not provided")
            return None

        if isinstance(input_name, EEPProgram):
            if input_name.owner.slug != "eto":
                raise KeyError("Only valid programs are ETO programs")
            return input_name.slug

        try:
            return EEPProgram.objects.get(owner__slug="eto", slug__iexact=input_name).slug
        except EEPProgram.DoesNotExist:
            return input_name

    # pylint: disable=too-many-return-statements
    def get_constants(self, program=None, us_state="OR"):
        """Get the constants"""
        if program is None:
            if us_state == "WA":
                return getattr(constants, "swwa")
            log.debug("Program was not provided using default constants")
            return getattr(constants, "original")
        if program == "eto-2020":
            return getattr(constants, "eto_2020")
        if program == "eto-2019":
            return getattr(constants, "eto_2019")
        elif program == "eto-2018":
            return getattr(constants, "eto_2018")
        elif program == "eto-2017":
            return getattr(constants, "eto_2017")
        else:
            if us_state == "WA":
                return getattr(constants, "swwa")
            return getattr(constants, "original")

    def normalize_primary_heat_type(self, input_name):
        """Normalize out the primary heat type"""
        if input_name is None or input_name.lower() in ["n/a", "none", ""]:
            if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
                msg = "`Primary heating` is required"
                raise EPSInputException(msg)
        from axis.customer_eto.enumerations import PrimaryHeatingEquipment2020

        valid_choices = [x.value for x in PrimaryHeatingEquipment2020]
        if input_name.lower() not in [x.lower() for x in valid_choices]:
            msg = "Invalid Primary heating type of %r is invalid - %s"
            raise EPSInputException(msg % (input_name, ", ".join(valid_choices)))
        return input_name

    def normalize_heat_type_from_primary(self, input_name):
        """Back out the heat type"""
        if input_name is None or input_name.lower() in ["n/a", "none"]:
            return None
        if "gas" in input_name.lower():
            return "gas heat"
        return "heat pump"

    def normalize_heat_type(self, input_name):
        """Normalize the heat type"""
        if input_name is None:
            log.warning("Heat Type was not provided")
            return None

        lower_list = [x.lower() for x in self.constants.ALLOWED_HEAT_TYPES]
        if input_name.lower() in lower_list:
            input_name = self.constants.ALLOWED_HEAT_TYPES[lower_list.index(input_name.lower())]

        if input_name not in self.constants.ALLOWED_HEAT_TYPES:
            msg = "Invalid heat type identified '{}' must be one of {}".format(
                input_name, self.constants.ALLOWED_HEAT_TYPES
            )
            raise EPSInputException(msg)
        return input_name

    def normalize_pathway(self, input_name):
        """Normalize the pathway"""
        if input_name in [None, ""]:
            if self.program not in ETO_GEN2:
                log.warning("Pathway was not provided")
            return None

        lower_list = [x.lower() for x in self.constants.EPS_VALID_PATHWAYS]
        if input_name.lower() in lower_list:
            input_name = self.constants.EPS_VALID_PATHWAYS[lower_list.index(input_name.lower())]

        if input_name not in self.constants.EPS_VALID_PATHWAYS:
            msg = "Invalid pathway identified '{}' must be one of {}".format(
                input_name, self.constants.EPS_VALID_PATHWAYS
            )
            raise EPSInputException(msg)
        return input_name

    def normalize_electric_utility(self, input_name):
        """Normalize the electric utility"""
        from axis.company.models import Company

        if isinstance(input_name, (Company,)):
            if input_name.slug == "pacific-power":
                electric_utility = "pacific power"
            elif input_name.slug == "portland-electric":
                electric_utility = "portland general"
            else:
                log.info("Electric Utility '{}' is not recognized - using other/None")
                electric_utility = "other/none"
        elif input_name is None:
            log.info("Electric Utility was not provided")
            electric_utility = "other/none"
        else:
            electric_utility = input_name

            lower_list = [x.lower() for x in self.constants.ALLOWED_ELECTRIC_UTILITY_NAMES]
            if electric_utility.lower() in lower_list:
                _idx = lower_list.index(electric_utility.lower())
                electric_utility = self.constants.ALLOWED_ELECTRIC_UTILITY_NAMES[_idx]

        if electric_utility not in self.constants.ALLOWED_ELECTRIC_UTILITY_NAMES:
            msg = "Invalid electric utility '%r' must be one of %r"
            log.error(msg, input_name, self.constants.ALLOWED_ELECTRIC_UTILITY_NAMES)
            electric_utility = "other/none"
        return electric_utility

    def normalize_gas_utility(self, input_name):
        """Normalize the gas utility"""
        from axis.company.models import Company

        if isinstance(input_name, (Company,)):
            if input_name.slug == "nw-natural-gas":
                gas_utility = "nw natural"
            elif input_name.slug == "cascade-gas":
                gas_utility = "cascade"
            elif input_name.slug == "avista":
                gas_utility = "avista"
            else:
                log.info("Gas Utility '%r' is not recognized - using other/None", input_name)
                gas_utility = "other/none"
        elif input_name is None:
            log.info("Gas Utility was not provided")
            gas_utility = "other/none"
        else:
            gas_utility = input_name

            lower_list = [x.lower() for x in self.constants.ALLOWED_GAS_UTILITY_NAMES]
            if gas_utility.lower() in lower_list:
                _idx = lower_list.index(gas_utility.lower())
                gas_utility = self.constants.ALLOWED_GAS_UTILITY_NAMES[_idx]

        if gas_utility not in self.constants.ALLOWED_GAS_UTILITY_NAMES:
            msg = "Invalid gas utility '%s' must be one of %s"
            log.info(msg, input_name, self.constants.ALLOWED_GAS_UTILITY_NAMES)
            gas_utility = "other/none"
        return gas_utility

    def normalize_builder(self, input_name):
        from axis.company.models import Company

        if isinstance(input_name, (Company,)):
            return input_name.slug
        if input_name in ["", "other/none"]:
            return None
        return input_name

    def normalize_location(self, input_name, direct_name):
        """Normalize the location"""
        if input_name is None:
            log.warning("Location was not provided")
            return None

        data = {
            "astoria, or": "astoria",
            "burns, or": "burns",
            "eugene, or": "eugene",
            "medford, or": "medford",
            "north bend, or": "northbend",
            "pendleton, or": "pendleton",
            "portland, or": "portland",
            "redmond, or": "redmond",
            "salem, or": "salem",
            "astoria regional airport, or": "astoria",
            "aurora state, or": "portland",
            "baker municipal ap, or": "pendleton",
            "burns municipal arpt [uo], or": "burns",
            "corvallis muni, or": "eugene",
            "eugene mahlon sweet arpt [uo], or": "eugene",
            "klamath falls intl ap [uo], or": "medford",
            "la grande muni ap, or": "pendleton",
            "lakeview (awos), or": "burns",
            "medford rogue valley intl ap [ashland - uo], or": "medford",
            "north bend muni airport, or": "northbend",
            "pendleton e or regional ap, or": "pendleton",
            "portland international ap, or": "portland",
            "portland/hillsboro, or": "portland",
            "portland/troutdale, or": "portland",
            "redmond roberts field, or": "redmond",
            "roseburg regional ap, or": "northbend",
            "salem mcnary field, or": "salem",
            "sexton summit, or": "medford",
        }

        input_name = data.get(input_name.lower(), input_name)

        lower_list = [x.lower() for x in self.constants.EPS_VALID_LOCATIONS]
        if input_name.lower() in lower_list:
            input_name = self.constants.EPS_VALID_LOCATIONS[lower_list.index(input_name.lower())]

        if input_name not in self.constants.EPS_VALID_LOCATIONS:
            msg = "Invalid location identified '{}' must be one of {}".format(
                input_name, self.constants.EPS_VALID_LOCATIONS
            )
            raise EPSInputException(msg)

        if self.using_simulation:
            if direct_name and direct_name.lower() != input_name.lower():
                msg = "Using location %r from REM/Rate® in lieu of provided %r"
                log.info(msg, input_name, direct_name)
        return input_name

    def normalize_tankless_water_heater(self, input_name, direct_name):
        """Normalize the tankless water heater"""
        if self.using_simulation:
            if direct_name and direct_name != input_name:
                msg = "Using tankless water heater %r from REM/Rate® in lieu of provided %r"
                log.info(msg, input_name, direct_name)
        return input_name

    def normalize_hot_water_ef(self, input_name, direct_name):
        """Normalize the hot water EF"""
        if self.using_simulation:
            if direct_name is not None and direct_name != input_name:
                msg = "Using hot water EF %r from REM/Rate® in lieu of provided %r"
                log.info(msg, input_name, direct_name)
        return input_name

    def normalize_conditioned_area(self, input_name, direct_name):
        """Normalize the conditioned area"""
        input_name = float(input_name)
        if self.using_simulation and direct_name is not None:
            msg = "Using conditioned area %r from REM/Rate® in lieu of provided %r"
            if input_name > float(direct_name):
                if (float(direct_name) / input_name) < 0.9:
                    log.info(msg, input_name, direct_name)
            elif (input_name / float(direct_name)) < 0.9:
                log.info(msg, input_name, direct_name)
        return input_name

    def normalize_qualifying_thermostat_from_brand(self, input_name, heat_type):
        value = "no qualifying smart thermostat"
        if input_name in [None, False] or heat_type in [None, False]:
            return value
        if input_name.lower() in ["n/a", "other, add comment"]:
            return value
        if "mini" in heat_type.lower() and "split" in heat_type.lower():
            return value
        if "gas" in heat_type.lower():
            return "yes-ducted gas furnace"
        elif "electric" in heat_type.lower():
            return "yes-ducted air source heat pump"
        return value

    def normalize_smart_thermostat(self, input_name):
        """Normalize the smart Thermostat"""
        if self.program not in ETO_GEN2:
            return False, None

        if input_name in [None, False, True]:
            if input_name is True:
                msg = "Invalid smart thermostat choice identified '{}' must be one of {}".format(
                    input_name, self.constants.EPS_VALID_SMART_THERMOMETER_CHOICES.keys()
                )
                raise EPSInputException(msg)
            return False, None

        if input_name.lower() not in self.constants.EPS_VALID_SMART_THERMOMETER_CHOICES.keys():
            msg = "Invalid smart thermostat choice identified '{}' must be one of {}".format(
                input_name, self.constants.EPS_VALID_SMART_THERMOMETER_CHOICES.keys()
            )
            raise EPSInputException(msg)

        return self.constants.EPS_VALID_SMART_THERMOMETER_CHOICES[input_name.lower()]

    def validate_furnace_type(self, input_name):
        """Normalize the furnace type"""
        if input_name == "GAS" and not self.improved_data.has_gas_heater:
            msg = "Gas Heater not present however smart thermostat provided was '{}'"
            raise EPSInputException(msg.format(self.input_qualifying_thermostat))
        elif input_name == "ASHP" and not self.improved_data.has_ashp:
            msg = "ASHP not present however smart thermostat provided was '{}'"
            raise EPSInputException(msg.format(self.input_qualifying_thermostat))

    def normalize_shower_head(self, input_value):
        """Normalize the shower heads"""

        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018"]:
            return 0

        if isinstance(input_value, type(None)):
            return 0

        if not isinstance(input_value, int):
            msg = "Input Showerheads must be an integer - you provided '{}'".format(input_value)
            raise EPSInputException(msg)
        return input_value

    def normalize_has_gas_fireplace(self, input_name):
        """Normalize out the fireplace stuff."""

        if self.program in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            return False

        if isinstance(input_name, type(None)):
            return False

        if input_name.lower() == "No fireplace".lower() or input_name == "":
            input_name = False
        elif input_name.lower() == "<=49FE".lower():
            input_name = "<=49FE"
        elif input_name.lower() == "50-59FE".lower():
            input_name = "50-59FE"
        elif input_name.lower() == "60-69FE".lower():
            input_name = "60-69FE"
        elif input_name.lower() == ">=70FE".lower():
            input_name = ">=70FE"
        else:
            msg = (
                "Input has fire place does not appear to come from valid checklist responses "
                " - you provided '{}'".format(input_name)
            )
            raise EPSInputException(msg)
        return input_name

    def normalize_grid_harmonization_elements(self, input_name):
        """Return Energy Smart Choices"""
        if input_name is None or input_name.lower() in ["n/a", "none", ""]:
            return None
        from axis.customer_eto.enumerations import GridHarmonization2020

        valid_choices = [x.value for x in GridHarmonization2020]
        if input_name.lower() not in [x.lower() for x in valid_choices]:
            msg = "Energy Smart Home choice %r is invalid - %s"
            raise EPSInputException(msg % (input_name, ", ".join(valid_choices)))
        return input_name

    def normalize_smart_thermostat_brand(self, input_name):
        """Return Net Zero valid smart thermostat"""
        if input_name is None or input_name.lower() in ["n/a", "none", ""]:
            return None
        from axis.customer_eto.enumerations import SmartThermostatBrands2020

        valid_choices = [x.value for x in SmartThermostatBrands2020]
        if input_name.lower() not in [x.lower() for x in valid_choices]:
            msg = "Smart thermmostat choice %r is invalid - %s"
            raise EPSInputException(msg % (input_name, ", ".join(valid_choices)))
        return input_name

    def normalize_eps_additional_incentives(self, input_name):
        """Return Smart Thermostat"""
        if input_name is None or input_name.lower() in ["no", "none", ""]:
            return None
        from axis.customer_eto.enumerations import AdditionalIncentives2020

        valid_choices = [x.value for x in AdditionalIncentives2020]
        if input_name.lower() not in [x.lower() for x in valid_choices]:
            msg = "Additional Incentive choice %r is invalid - %s"
            raise EPSInputException(msg % (input_name, ", ".join(valid_choices)))
        return input_name

    def normalize_solar_elements(self, input_name):
        if input_name is None or input_name.lower() in ["no", "none", ""]:
            return None
        from axis.customer_eto.enumerations import SolarElements2020

        valid_choices = [x.value for x in SolarElements2020]
        if input_name.lower() not in [x.lower() for x in valid_choices]:
            msg = "Additional solar element choice %r is invalid - %s"
            raise EPSInputException(msg % (input_name, ", ".join(valid_choices)))
        return input_name

    def normalize_generated_solar_pv_kwh(self, input_value):
        """Normalize the solar PV kwh"""
        if isinstance(input_value, type(None)):
            return 0

        if not isinstance(input_value, (float, int)):
            msg = "Input Generated Solar must be a number you provided '{}'".format(input_value)
            raise EPSInputException(msg)
        return input_value

    def normalize_solar_data(self, non_solar_simulation, with_solar_simulation):
        """Negates out solar components.  Since we know what the resulting consumption
        is we need to determine the solar effects.
        """

        s_therms = non_solar_simulation.hot_water_therms - with_solar_simulation.hot_water_therms
        s_kwh = non_solar_simulation.hot_water_kwh - with_solar_simulation.hot_water_kwh
        has_solar = s_therms > 0 or s_kwh > 0
        data = {
            "non_solar_hot_water_therms": s_therms,
            "non_solar_hot_water_kwh": s_kwh,
            "solar_hot_water_therms": with_solar_simulation.hot_water_therms,
            "solar_hot_water_kwh": with_solar_simulation.hot_water_kwh,
            "has_solar_hot_water": has_solar,
            "_reference_non_solar_hot_water_therms": non_solar_simulation.hot_water_therms,
            "_reference_non_solar_hot_water_kwh": non_solar_simulation.hot_water_kwh,
        }
        return data

    @classmethod
    def set_manual_code_inputs(cls, input_1, input_2):
        """Set code inputs"""
        if "solar_hot_water_therms" in input_1:
            improved = input_1
            code = input_2
        else:
            code = input_1
            improved = input_2
        solar = {}

        if "solar_hot_water_therms" in improved or "solar_hot_water_kwh" in improved:
            hot_water_therms = 0.0
            if improved.get("hot_water_therms"):
                hot_water_therms = float(improved.get("hot_water_therms"))

            hot_water_kwh = 0.0
            if improved.get("hot_water_kwh"):
                hot_water_kwh = float(improved.get("hot_water_kwh"))

            solar_hot_water_therms = 0.0
            if improved.get("solar_hot_water_therms"):
                solar_hot_water_therms = float(improved.get("solar_hot_water_therms"))

            solar_hot_water_kwh = 0.0
            if improved.get("solar_hot_water_kwh"):
                solar_hot_water_kwh = float(improved.get("solar_hot_water_kwh"))

            solar = {
                "non_solar_hot_water_therms": hot_water_therms,
                "non_solar_hot_water_kwh": hot_water_kwh,
                "solar_hot_water_therms": solar_hot_water_therms,
                "solar_hot_water_kwh": solar_hot_water_kwh,
                "has_solar_hot_water": True,
            }

        return code, improved, solar

    @classmethod  # noqa: MC0001
    def set_code_inputs(cls, improved_id, code_id=None):
        """Ensure that the improved and code information is correctly set up.
        It'll adjust it for you if necessary.
        """

        from axis.remrate_data.models import Simulation

        input_sim = Simulation.objects.get(id=improved_id)
        if input_sim.export_type == 1:
            _kw = {"similar__id": improved_id, "export_type": 4, "solarsystem__type__in": [1, 2]}
            improved_data = Simulation.objects.filter(**_kw).last()
            if not improved_data:
                _kw = {"similar__id": improved_id, "export_type": 4, "solarsystem__type": 0}
                improved_data = Simulation.objects.filter(**_kw).last()
                if not improved_data:
                    msg = (
                        "Input simulation ID {} is the wrong type '{}'.  "
                        "Must be 'UDRH As Is Building'"
                    )
                    raise EPSInputException(
                        msg.format(improved_id, input_sim.get_export_type_display())
                    )
                else:
                    log.info(
                        "Using similar non-solar 'UDRH As Is Building' "
                        "in lieu of provided 'Standard Building"
                    )
            else:
                log.info(
                    "Using similar solar 'UDRH As Is Building' "
                    "in lieu of provided 'Standard Building"
                )

        elif input_sim.export_type == 4:
            if input_sim.solarsystem.type not in [1, 2]:
                _kw = {
                    "similar__id": improved_id,
                    "export_type": 4,
                    "solarsystem__type__in": [1, 2],
                }
                improved_data = Simulation.objects.filter(**_kw).last()
                if not improved_data:
                    improved_data = input_sim
                else:
                    log.info(
                        "Using similar solar 'UDRH As Is Building' "
                        "in lieu of non-solar 'UDRH As Is Building'"
                    )
            else:
                improved_data = input_sim  # Typical Use Case

        elif input_sim.export_type == 5:
            _kw = {"references__id": improved_id, "export_type": 4, "solarsystem__type__in": [1, 2]}
            improved_data = Simulation.objects.filter(**_kw).last()
            if not improved_data:
                _kw = {"references__id": improved_id, "export_type": 4}
                improved_data = Simulation.objects.filter(**_kw)
                if not improved_data:
                    msg = (
                        "Input simulation ID {} is the wrong type '{}'.  "
                        "Must be 'UDRH As Is Building'"
                    )
                    raise EPSInputException(
                        msg.format(improved_id, input_sim.get_export_type_display())
                    )
                else:
                    log.info(
                        "Using referenced non-solar 'UDRH As Is Building' "
                        "in lieu of provided 'UDRH Reference Building"
                    )
                    improved_data = improved_data.last()
            else:
                log.info(
                    "Using referenced solar 'UDRH As Is Building' "
                    "in lieu of provided 'UDRH Reference Building"
                )

        assert improved_data.export_type == 4, "Wrong Input Type"
        # log.info('Improved Data: [%r] %r', improved_data.id, improved_data)

        code_data = improved_data.references.all().last()
        if code_id:
            try:
                code_data = improved_data.references.get(id=code_id)
            except Simulation.DoesNotExist:
                msg = (
                    "Unable to get code reference using provided "
                    "Simulation ID {}.  Improved Home: ({}) {}"
                )
                raise EPSInputException(msg.format(code_id, improved_data.id, improved_data))
        try:
            assert code_data.export_type == 5, "Wrong Input Type"
        except AttributeError:
            msg = "Unable to associate 'Improved Simulation' %r ID: %s to a 'Code Simulation'."
            raise EPSInputException(msg, improved_data, improved_data.id)
        # log.info('Code Data: [%r] %r', code_data.id, code_data)

        non_solar = None
        if improved_data.solarsystem.type in [1, 2]:
            try:
                non_solar = improved_data.similar.filter(
                    solarsystem__type=0, export_type__in=[1, 4]
                ).last()
                assert non_solar is not None, "Doh."
                log.info("Non-Solar: [%r] %r", non_solar.id, non_solar)
            except (Simulation.DoesNotExist, AssertionError):
                msg = (
                    "When using a Solar System you must define the "
                    "non-solar counterpart.  Re-Run REMRate export with "
                    "the Active Solar System set to None."
                )
                raise EPSInputException(msg)

        return code_data, improved_data, non_solar

    def report(self):
        """Report"""
        msg = "{:24}{}"
        labels = [
            "Address",
            "State",
            "Location",
            "Heat Type",
            "Primary Heating Type",
            "Pathway",
            "Program",
            "Conditioned Area",
            "Electric Utility",
            "Gas Utility",
            "Builder",
            "Has Solar Hot H2O",
            "Has Gas Hot H20",
        ]
        attrs = [
            self.site_address,
            self.us_state,
            self.location,
            self.heat_type,
            self.primary_heat_type,
            self.pathway,
            self.program,
            self.conditioned_area,
            self.electric_utility,
            self.gas_utility,
            self.builder,
            self.has_solar_hot_water,
            self.has_gas_hot_water,
        ]
        vdata = zip(labels, attrs)
        data = []
        data.append("\n--- Inputs ----")
        for k, v in vdata:
            if k == "Heat Type":
                if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
                    continue
            if k == "Primary Heating Type":
                if self.program in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
                    continue
            data.append(msg.format(k, v if v is not None else "-"))
        if self.program not in ETO_GEN2:
            data.append(msg.format("Has Tankless H20", self.has_tankless_water_heater))
            data.append(msg.format("Hot water EF", self.hot_water_ef))
        if self.program in ["eto-2015", "eto-2016", "eto-2017", "eto-2018"]:
            data.append(msg.format("Shower Head 1.75", self.qty_shower_head_1p75))
            data.append(msg.format("Shower Head 1.6", self.qty_shower_head_1p6))
            data.append(msg.format("Shower Head 1.5", self.qty_shower_head_1p5))
            data.append(msg.format("Shower Wand 1.5", self.qty_shower_wand_1p5))
        else:
            data.append(msg.format("Qualifying Thermostat", self.input_qualifying_thermostat))
            data.append(msg.format("Annual PV kWh", self.generated_solar_pv_kwh))
            data.append(msg.format("Has HPWH", self.has_heat_pump_water_heater))
        if self.program not in ["eto-2015", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]:
            data.append(msg.format("Grid Harmonization", self.input_grid_harmonization_elements))
            data.append(msg.format("Smart Thermostat", self.input_smart_thermostat_brand))
            data.append(msg.format("EPS Addtl", self.input_eps_additional_incentives))
            data.append(msg.format("Solar Elements", self.input_solar_elements))
            data.append(msg.format("Has Gas Fireplace", self.input_has_gas_fireplace))
            data.append(msg.format("Using NEW Sim model", not self.legacy_simulation))
            data.append(self.net_zero.input_report)

        return "\n".join(data)

    @property
    def input_report_data(self):
        """Report"""
        return OrderedDict(
            [
                ("site_address", self.site_address),
                ("location", self.location),
                ("us_state", self.us_state),
                ("heat_type", self.heat_type),
                ("primary_heat_type", self.primary_heat_type),
                ("pathway", self.pathway),
                ("conditioned_area", self.conditioned_area),
                ("electric_utility", self.electric_utility),
                ("gas_utility", self.gas_utility),
                ("builder", self.builder),
                ("has_solar_hot_water", self.has_solar_hot_water),
                ("has_gas_hot_water", self.has_gas_hot_water),
                ("has_tankless_water_heater", self.has_tankless_water_heater),
                ("hot_water_ef", self.hot_water_ef),
                ("qualifying_thermostat", self.input_qualifying_thermostat),
                ("qty_shower_head_1p5", self.qty_shower_head_1p5),
                ("qty_shower_head_1p6", self.qty_shower_head_1p6),
                ("qty_shower_head_1p75", self.qty_shower_head_1p75),
                ("qty_shower_wand_1p5", self.qty_shower_wand_1p5),
                ("generated_solar_pv_kwh", self.generated_solar_pv_kwh),
                ("has_gas_fireplace", self.has_gas_fireplace),
                ("grid_harmonization_elements", self.input_grid_harmonization_elements),
                ("smart_thermostat_brand", self.input_smart_thermostat_brand),
                ("eps_additional_incentives", self.input_eps_additional_incentives),
                ("solar_elements", self.input_solar_elements),
                ("use_legacy_simulation", self.legacy_simulation),
            ]
        )
