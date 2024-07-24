"""rtf_base.py: Django Base RTF calculator"""


import logging
import re

from django.core.exceptions import ObjectDoesNotExist

from axis.core.utils import enforce_order
from .. import constants
from ..base import RTFInputException

__author__ = "Steven K"
__date__ = "08/20/2019 07:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class RTFBaseCalculator(object):  # pylint: disable=too-many-instance-attributes
    """Base Object"""

    def __init__(self, **kwargs):  # noqa: MC001
        self._kwargs = kwargs.copy()
        _code_data, _improved_data = {}, {}
        for key, value in list(kwargs.items()):
            match = re.match(r"code_data_(.*)", key)
            if match and key != "code_data":
                _code_data[match.group(1)] = value
                kwargs.pop(key)
                continue
            match = re.match(r"improved_data_(.*)", key)
            if match and key != "improved_data":
                _improved_data[match.group(1)] = value
                kwargs.pop(key)
                continue

        kwargs["code_data"] = kwargs.get("code_data", {})
        kwargs["improved_data"] = kwargs.get("improved_data", {})

        if _code_data or _improved_data:
            kwargs["code_data"].update(_code_data)
            kwargs["improved_data"].update(_improved_data)

        self.constants = self.get_constants()
        self._warnings = []

        self.home_status_id = kwargs.get("home_status_id")
        self.force_rem_simulation = kwargs.pop("force_rem_simulation", False)
        self.using_rem_simulation = False
        from axis.home.models import EEPProgramHomeStatus

        self.home_status = None
        if self.home_status_id:
            self.home_status = EEPProgramHomeStatus.objects.get(id=self.home_status_id)

        self.electric_utility, self.gas_utility = None, None
        if self.home_status:
            electric_utility = self.home_status.get_electric_company()
            if electric_utility:
                self.electric_utility = self._kwargs["electric_utility"] = electric_utility.slug
            gas_utility = self.home_status.get_gas_company()
            if gas_utility:
                self.gas_utility = self._kwargs["gas_utility"] = gas_utility.slug
        else:
            self.electric_utility = kwargs.get("electric_utility")
            try:
                self.electric_utility = kwargs.get("electric_utility").slug
            except AttributeError:
                pass

            self.gas_utility = kwargs.get("gas_utility")
            try:
                self.gas_utility = kwargs.get("gas_utility").slug
            except AttributeError:
                pass

        self.input_us_state = kwargs.get("us_state")
        self.us_state = self.normalize_us_state(self.input_us_state, self.home_status)

        if not kwargs.get("simulation_id") and self.home_status:
            if self.home_status.floorplan is None:
                self.append_issue("Need a floorplan with Simulation data")
            elif self.home_status.floorplan.simulation and self.force_rem_simulation is False:
                kwargs["simulation_id"] = self.home_status.floorplan.simulation.id
                log.debug(
                    "Using Simulation %s from provided Home Status %s",
                    kwargs["simulation_id"],
                    self.home_status.id,
                )
            elif self.home_status.floorplan.remrate_target:
                kwargs["simulation_id"] = self.home_status.floorplan.remrate_target.id
                self.using_rem_simulation = True
                log.debug(
                    "Using REM Simulation %s from provided Project %s",
                    kwargs["simulation_id"],
                    self.home_status.id,
                )

        self.input_simulation = None
        if kwargs.get("simulation_id"):
            from simulation.models import Simulation
            from axis.remrate_data.models import Simulation as RemSimulation

            if not self.using_rem_simulation:
                self.input_simulation = Simulation.objects.get(id=kwargs.get("simulation_id"))
                self.using_simulation = True
                code_data_sim = improved_data_sim = self.input_simulation
                data_model_object = self.get_sim_modeled_input()
            else:
                self.input_simulation = RemSimulation.objects.get(id=kwargs.get("simulation_id"))
                self.using_simulation = True
                code_data_sim, improved_data_sim = self.set_code_inputs(kwargs.get("simulation_id"))
                data_model_object = self.get_rem_modeled_input()

        elif kwargs.get("code_data") and kwargs.get("improved_data"):
            code_data_sim, improved_data_sim = kwargs["code_data"], kwargs["improved_data"]
            data_model_object = self.get_simulated_input()
        else:
            msg = "Please provide code / improved data"
            if self.home_status:
                msg = "Please add a floorplan with UDRH REM/Rate® data"
            self.issues.append(msg)
            raise RTFInputException(*self.issues)

        if kwargs.get("simulation_id"):
            if None in [code_data_sim, improved_data_sim] and self.issues:
                raise RTFInputException(*self.issues)

        self.code_data = data_model_object(simulation=code_data_sim)
        self.improved_data = data_model_object(simulation=improved_data_sim, is_improved=True)

        self.input_heating_fuel = kwargs.get("heating_fuel")
        self.heating_fuel = self.normalize_heating_fuel(self.input_heating_fuel, improved_data_sim)

        self.input_heating_system_config = kwargs.get("heating_system_config")
        self.heating_system_config = self.normalize_input_heating_system_config(
            self.input_heating_system_config
        )

        self.input_home_size = kwargs.get("home_size")
        self.input_conditioned_area = kwargs.get("conditioned_area")

        self.home_size = self.normalize_input_home_size(
            self.input_home_size, self.improved_data, self.input_conditioned_area
        )

        self.input_heating_zone = kwargs.get("heating_zone")
        self.heating_zone = self.normalize_input_heating_zone(
            self.input_heating_zone, self.home_status
        )

        self.input_cfl_installed = kwargs.get("cfl_installed", 0)
        self.cfl_installed = self.normalize_integer(self.input_cfl_installed)

        self.input_led_installed = kwargs.get("led_installed", 0)
        self.led_installed = self.normalize_integer(self.input_led_installed)

        self.input_total_installed_lamps = kwargs.get("total_installed_lamps", 0)
        self.total_installed_lamps = self.normalize_integer(self.input_total_installed_lamps)

        self.input_smart_thermostat_installed = kwargs.get("smart_thermostat_installed", False)
        self.smart_thermostat_installed = self.normalize_boolean(
            self.input_smart_thermostat_installed
        )

        self.input_qty_shower_head_1p5 = kwargs.get("qty_shower_head_1p5", 0)
        self.qty_shower_head_1p5 = self.normalize_integer(self.input_qty_shower_head_1p5)

        self.input_qty_shower_head_1p75 = kwargs.get("qty_shower_head_1p75", 0)
        self.qty_shower_head_1p75 = self.normalize_integer(self.input_qty_shower_head_1p75)

        self.input_default_percent_improvement = kwargs.get("percent_improvement")
        self.default_percent_improvement = self.normalize_percent_improvement(
            self.input_default_percent_improvement, self.improved_data, self.code_data
        )

        self.electricity_adjustment_factor = self.constants.ELECTRICITY_ADJUSTMENT_FACTOR
        self.gas_adjustment_factor = self.constants.GAS_ADJUSTMENT_FACTOR

        self.pct_improvement_method = kwargs.get("pct_improvement_method")

        if self.issues and kwargs.get("raise_issues", True):
            raise RTFInputException(*self.issues)

        self._incentives = None

    def append_issue(self, issue, *args, **kwargs):
        """Add issue to the stack"""
        log.debug(issue, *args, **kwargs)
        self._warnings.append(issue % args)

    @property
    def issues(self):
        """Get the issues"""
        return self._warnings

    def get_constants(self):
        """Get constants"""
        return getattr(constants, "default")

    def normalize_boolean(self, input_name):
        """Normalize input to boolean"""
        if input_name is None:
            return False
        if isinstance(input_name, str):
            if input_name.lower() in ["true", "yes", "1"]:
                return True
            if input_name.lower() in ["false", "no", "0"]:
                return False
        return bool(input_name)

    # pylint: disable=inconsistent-return-statements
    def normalize_integer(self, input_name, max_value=None):
        """Normalize input to int"""
        if input_name is None:
            return 0
        if max_value is None:
            return int(input_name)
        if int(input_name) > max_value:
            self.append_issue("You can't have more than %s items", max_value)

    def normalize_float(self, input_name, lower_limit=None, upper_limit=None):
        """Normalize input to float"""
        if input_name is None:
            return 0.0
        input_name = float(input_name)
        if lower_limit and input_name < lower_limit:
            msg = "Input value provided %s is less than lower limit allowed %s"
            return self.append_issue(msg, input_name, lower_limit)
        if upper_limit and input_name > upper_limit:
            msg = "Input value provided %s is greater than upper limit allowed %s"
            return self.append_issue(msg, input_name, lower_limit)
        return input_name

    def normalize_us_state(self, input_name, home_status=None):
        """Normalize input to US State"""
        if input_name is None:
            if home_status:
                input_name = home_status.home.state
                log.debug("Using State from Project - %s", input_name)
            else:
                return self.append_issue("State was not provided")

        if input_name.lower() not in ["or", "wa", "id", "mt"]:
            return self.append_issue("State must be either 'OR', 'WA', 'ID', or 'MT'")
        return input_name.upper()

    def get_simulation_heating_fuel(self, simulation):
        """Get the dominant heating fuel"""
        if simulation is None or isinstance(simulation, dict):
            return
        if not self.using_rem_simulation:
            try:
                fuel = simulation.dominant_heating_equipment.fuel
            except AttributeError:
                return
        else:
            dominant = simulation.installedequipment_set.get_dominant_values(False)
            fuel = dominant.get("dominant_heating", {}).get("fuel", "Unknown")
        if "gas" in fuel.lower():
            return "gas"
        elif "electric" in fuel.lower():
            return "electric"
        log.warning("Heating fuels used for simulation %r %r", simulation.id, fuel)

    def normalize_heating_fuel(self, input_name, simulation=None):
        """Normalize the heating fuel"""
        if input_name is None:
            _input_name = self.get_simulation_heating_fuel(simulation)
            if _input_name:
                input_name = _input_name
                log.debug("Using Heating Fuel from Simulation - %s", input_name)
            else:
                return self.append_issue("Heating Fuel was not provided")

        input_name = input_name.lower().replace(" ", "")

        lower_list = [x.lower() for x in self.constants.ALLOWED_HEATING_FUELS]
        if input_name.lower() in lower_list:
            input_name = self.constants.ALLOWED_HEATING_FUELS[lower_list.index(input_name.lower())]

        if input_name not in self.constants.ALLOWED_HEATING_FUELS:
            msg = "Invalid heat type identified '%s' must be one of %s"
            return self.append_issue(
                msg, input_name, ", ".join(self.constants.ALLOWED_HEATING_FUELS)
            )
        return input_name

    def normalize_input_heating_system_config(self, input_name):
        """Normalize the input heating system config"""
        if input_name is None:
            return self.append_issue("Heating System Configuration was not provided")

        input_name = input_name.lower().replace(" ", "")

        lower_list = [x.lower() for x in self.constants.ALLOWED_HEATING_SYSTEM_TYPES]
        if input_name.lower() in lower_list:
            _idx = lower_list.index(input_name.lower())
            input_name = self.constants.ALLOWED_HEATING_SYSTEM_TYPES[_idx]

        if input_name not in self.constants.ALLOWED_HEATING_SYSTEM_TYPES:
            msg = "Invalid heating system config identified '%s' must be one of %s"
            return self.append_issue(
                msg, input_name, ", ".join(self.constants.ALLOWED_HEATING_SYSTEM_TYPES)
            )
        return input_name

    def normalize_input_home_size(self, input_name, simulation=None, conditioned_area=None):
        """Normalize the input home size"""

        def get_home_size(square_footage):
            """Gets the home size based on a number"""
            if square_footage < 1500.0:
                input_name = "small"
            elif square_footage < 5000.00:
                input_name = "medium"
            else:
                input_name = "large"
            log.debug(
                "Pre-setting home size (%s) based on square footage (%s) of home",
                input_name,
                square_footage,
            )
            return input_name

        if self.us_state in ["ID", "MT", "OR"]:
            log.debug("Pre-setting home size (all) based on state")
            input_name = "all"
        elif simulation.square_footage is not None:
            input_name = get_home_size(simulation.square_footage)
        elif conditioned_area is not None:
            input_name = get_home_size(conditioned_area)

        if input_name is None and simulation.square_footage is None:
            return self.append_issue("Home Size was not provided")

        input_name = input_name.lower().replace(" ", "")

        lower_list = [x.lower() for x in self.constants.ALLOWED_HOME_SIZE]
        if input_name.lower() in lower_list:
            input_name = self.constants.ALLOWED_HOME_SIZE[lower_list.index(input_name.lower())]

        if input_name not in self.constants.ALLOWED_HOME_SIZE:
            msg = "Invalid home size identified '%s' must be one of %s"
            return self.append_issue(msg, input_name, ", ".join(self.constants.ALLOWED_HOME_SIZE))

        if self.us_state == "WA" and input_name == "all":
            msg = "For Washington you MUST select a home size from small, medium, large"
            return self.append_issue(msg)

        return input_name

    def normalize_input_heating_zone(self, input_name, home_status):
        """Normalize the input input heating zone"""
        if input_name is None:
            if home_status:
                try:
                    input_name = home_status.home.county.pnwzone.get_heating_zone_display()
                    log.debug("Using Heating Zone from Project - %s", input_name)
                except (ObjectDoesNotExist, AttributeError):
                    return self.append_issue("Heating Zone was not found from home status")
            else:
                return self.append_issue("Heating Zone was not provided")

        input_name = input_name.lower().replace(" ", "")

        lower_list = [x.lower() for x in self.constants.ALLOWED_HEATING_ZONE]
        if input_name.lower() in lower_list:
            input_name = self.constants.ALLOWED_HEATING_ZONE[lower_list.index(input_name.lower())]

        if input_name not in self.constants.ALLOWED_HEATING_ZONE:
            msg = "Invalid Heating Zone identified '%s' must be one of %s"
            return self.append_issue(
                msg, input_name, ", ".join(self.constants.ALLOWED_HEATING_ZONE)
            )
        return input_name

    def normalize_percent_improvement(self, input_name, improved_data=None, code_data=None):
        """Normalize out the percent improvement"""
        if input_name is None:
            if hasattr(improved_data, "simulation"):
                try:
                    input_name = improved_data.get_udrh_percent_improvement()
                except AttributeError:
                    msg = "Unable to get the reference home from this simulation."
                    return self.append_issue(msg)
            elif improved_data and code_data:
                input_name = improved_data.get_udrh_percent_improvement(code_data)
        return self.normalize_float(max(0, input_name), 0)

    def set_code_inputs(self, improved_id):
        """
        Ensure that the improved and code information is correctly set up.
        It'll adjust it for you if necessary.
        """

        from axis.remrate_data.models import Simulation as RemSimulation

        improved_data = None
        input_sim = RemSimulation.objects.get(id=improved_id)
        if input_sim.export_type == 1:
            _kw = {"similar__id": improved_id, "export_type": 4, "solarsystem__type__in": [1, 2]}
            improved_data = RemSimulation.objects.filter(**_kw).last()
            if not improved_data:
                _kw = {"similar__id": improved_id, "export_type": 4, "solarsystem__type": 0}
                improved_data = RemSimulation.objects.filter(**_kw).last()
                if not improved_data:
                    msg = (
                        "Input simulation ID %s is the wrong type '%s'.  "
                        "Must be 'UDRH As Is Building'"
                    )
                    self.append_issue(msg, improved_id, input_sim.get_export_type_display())
                    return None, None
                else:
                    log.debug(
                        "Using similar non-solar 'UDRH As Is Building' in lieu "
                        "of provided 'Standard Building"
                    )
            else:
                log.debug(
                    "Using similar solar 'UDRH As Is Building' in lieu "
                    "of provided 'Standard Building"
                )

        elif input_sim.export_type == 4:
            if input_sim.solarsystem.type not in [1, 2]:
                _kw = {
                    "similar__id": improved_id,
                    "export_type": 4,
                    "solarsystem__type__in": [1, 2],
                }
                improved_data = RemSimulation.objects.filter(**_kw).last()
                if not improved_data:
                    improved_data = input_sim
                else:
                    log.debug(
                        "Using similar solar 'UDRH As Is Building' in lieu "
                        "of non-solar 'UDRH As Is Building'"
                    )
            else:
                improved_data = input_sim  # Typical Use Case

        elif input_sim.export_type == 5:
            _kw = {"references__id": improved_id, "export_type": 4, "solarsystem__type__in": [1, 2]}
            improved_data = RemSimulation.objects.filter(**_kw).last()
            if not improved_data:
                _kw = {"references__id": improved_id, "export_type": 4}
                improved_data = RemSimulation.objects.filter(**_kw)
                if not improved_data:
                    msg = (
                        "Input simulation ID %s is the wrong type '%s'.  "
                        "Must be 'UDRH As Is Building'"
                    )
                    self.append_issue(msg, improved_id, input_sim.get_export_type_display())
                    return None, None
                else:
                    log.debug(
                        "Using referenced non-solar 'UDRH As Is Building' in lieu "
                        "of provided 'UDRH Reference Building"
                    )
                    improved_data = improved_data.last()
            else:
                log.debug(
                    "Using referenced solar 'UDRH As Is Building' in lieu "
                    "of provided 'UDRH Reference Building"
                )

        assert improved_data.export_type == 4, "Wrong Input Type"
        log.info("Improved Data: [%r] %r", improved_data.id, improved_data)

        code_data = improved_data.references.all().last()

        try:
            assert code_data.export_type == 5, "Wrong Input Type"
        except AttributeError:
            msg = "Unable to associate 'Improved Simulation' %r ID: %s to a 'Code Simulation'."
            self.append_issue(msg, improved_data, improved_data.id)
            return None, None
        log.info("Code Data: [%r] %r", code_data.id, code_data)

        return code_data, improved_data

    @classmethod
    def set_manual_code_inputs(cls, input_1, input_2):
        """Set manual code inputs"""
        if "XXX???" in input_1:  # TODO How do I tell the difference
            improved = input_1
            code = input_2
        else:
            code = input_1
            improved = input_2

        return code, improved

    def report(self):
        """Report"""
        labels = [
            "Project",
            "Input Simulation",
            "State",
            "Heating Fuel",
            "Heating System Config",
            "Home Size",
            "Heating Zone",
            "Def. Percent Improvement",
        ]
        attrs = [
            self.home_status,
            self.input_simulation,
            self.us_state,
            self.heating_fuel,
            self.heating_system_config,
            self.home_size,
            self.heating_zone,
            self.default_percent_improvement,
        ]
        vdata = zip(labels, attrs)
        data = []
        data.append("\n--- Inputs ----")
        for k, v in vdata:
            data.append("{:24}{}".format(k, v if v is not None else "-"))

        data.append("\n--- Other Inputs ----")
        unwanted_items = [
            "heating_fuel",
            "heating_system_config",
            "heating_zone",
            "home_size",
            "default_percent_improvement",
            "us_state",
        ]
        priority_list = [
            # Misc identity information
            "home_status_id",
            "electric_utility",
            "gas_utility",
            # Checklist data (ordered as presented over there)
            "heating_source",
            "water_heater_tier",
            "estar_std_refrigerators_installed",
            "estar_dishwasher_installed",
            "estar_front_load_clothes_washer_installed",
            "clothes_dryer_tier",
            "cfl_installed",
            "led_installed",
            "total_installed_lamps",
            "smart_thermostat_installed",
            "qty_shower_head_1p5",
            "qty_shower_head_1p75",
            "major-load-equipment",
            "hvac-combo",
            "hvac-cooling-combo",
            "water-heater-combo",
            "ventilation-combo",
            "program_redirected",
        ]
        keys = [k for k in self._kwargs.keys() if k not in unwanted_items]
        for k in enforce_order(keys, priority_list):
            v = self._kwargs[k]
            data.append("{:40}{}".format(k, v if v is not None else "-"))
        return "\n".join(data)

    def get_sim_modeled_input(self):
        """Stub for modeled input"""
        raise NotImplementedError("Must be set from children")

    def get_rem_modeled_input(self):
        """Stub for modeled input"""
        raise NotImplementedError("Must be set from children")

    def get_simulated_input(self):
        """Stub for simulated input"""
        raise NotImplementedError("Must be set from children")

    @property
    def incentives(self):
        """Stub for incentives"""
        raise NotImplementedError("You need to do this later")
