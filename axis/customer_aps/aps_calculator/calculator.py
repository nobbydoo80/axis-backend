"""calculator.py: Django aps"""


import json
import logging

from . import constants
from .base import APSInputException
from .data_models import SimulatedInputBase, RemRateSimulation, EkotropeSimulation
from .incentives import APSIncentive, APSIncentive2019Tstat, APSIncentive2019Addon

__author__ = "Steven Klass"
__date__ = "4/6/18 12:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..messages import ApsUpdatedMetersetMessage

log = logging.getLogger(__name__)


class APSBaseCalculator(object):
    """Base Calculator.  This allows us to reuse it year after year."""

    def __init__(self, **kwargs):
        self._kwargs = kwargs.copy()

        self.constants = self.get_constants()
        self._warnings = []
        self._errors = []

        self.home_status_id = kwargs.get("home_status_id")
        from axis.home.models import EEPProgramHomeStatus

        self.home_status = (
            EEPProgramHomeStatus.objects.get(id=self.home_status_id)
            if self.home_status_id
            else None
        )

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
            self.gas_utility = kwargs.get("gas_utility")

        if self.electric_utility != "aps":
            msg = "APS is not the utility defined."
            if self.home_status:
                msg = "APS is not the utility defined on home %r." % self.home_status.home
            self.append_issue(msg)

        self.input_us_state = kwargs.get("us_state")
        self.us_state = self.normalize_us_state(self.input_us_state, self.home_status)

        self.input_program = kwargs.get("program")
        program = self.normalize_program(self.input_program, self.home_status, skip_swap=True)

        if (self.home_status and self.home_status.floorplan) or kwargs.get("floorplan"):
            floorplan = kwargs.get(
                "floorplan", self.home_status.floorplan if self.home_status else None
            )
            self.simulation = self.get_simulation_data_model(floorplan)
        elif kwargs.get("simulation"):
            self.simulation = self.get_default_data_model(simulation=kwargs.get("simulation"))
        else:
            if self.get_eep_program(program).require_input_data:
                msg = "Missing simulation data"
                if self.home_status:
                    msg = "Please a floorplan which contains either REM/Rate or Ekotrope data"
                self.append_issue(msg)
                return
            self.simulation = None

        self.input_climate_zone = kwargs.get("climate_zone")
        self.climate_zone = self.normalize_climate_zone(
            self.input_climate_zone, self.home_status, self.simulation
        )

        if self.errors and self.simulation is None:  # We need simulation data moving forward
            if kwargs.get("raise_issues", True):
                raise APSInputException(*self.errors)
            return

        self.program = self.normalize_program(program, self.home_status)

        self.input_thermostat_option = kwargs.get("thermostat_option")
        self.thermostat_option = self.normalize_thermostat_option(
            self.input_thermostat_option, self.home_status
        )

        self.input_thermostat_qty = kwargs.get("thermostat_qty")
        self.thermostat_qty = self.normalize_thermostat_qty(
            self.input_thermostat_qty, self.home_status
        )

        self.notify_on_program_change = kwargs.get("notify_on_program_change", True)

        if self.home_status and self.program:
            self.update_program()

        if self.errors and kwargs.get("raise_issues", True):
            raise APSInputException(*self.errors)

    def report(self):
        """Provide a nice pretty report"""
        msg = "{:24}{}"
        labels = [
            "Project",
            "Electric Utility",
            "Gas Utility",
            "US State",
            "Floorplan",
            "Climate Zone",
            "HERS",
            "Program",
        ]
        attrs = [
            self.home_status,
            self.electric_utility,
            self.gas_utility,
            self.us_state,
            getattr(self.home_status, "floorplan", None),
            self.climate_zone,
            getattr(self.simulation, "non_pv_hers_score", None),
            self.program,
        ]
        vdata = zip(labels, attrs)
        data = []
        data.append("\n--- Inputs ----")
        for k, v in vdata:
            data.append(msg.format(k, v if v is not None else "-"))
        data.append("\n--- Other Inputs ----")
        msg = "{:40}{}"
        keys = sorted(self._kwargs.keys())

        ignore_keys = [
            "climate_zone",
            "gas_utility",
            "electric_utility",
            "home_status_id",
            "simulation",
            "us_state",
            "program",
        ]
        for k in keys:
            if k in ignore_keys:
                continue
            v = self._kwargs[k]
            data.append(msg.format(k, v if v is not None else "-"))
        return "\n".join(data)

    def append_issue(self, issue, issue_type="error", *args, **kwargs):
        """Append an issue to the stack"""
        log.debug(issue, *args, **kwargs)
        if issue_type == "error":
            self._errors.append(issue % args)
        else:
            self._warnings.append(issue % args)

    @property
    def errors(self):
        """Return any errors"""
        return self._errors

    @property
    def warnings(self):
        """Return any warnings"""
        return self._warnings

    def get_constants(self):
        """Return the constants"""
        return getattr(constants, "default")

    def get_eep_program(self, slug):
        """Get an EEP Program"""
        from axis.eep_program.models import EEPProgram

        return EEPProgram.objects.get(slug=slug)

    @property
    def eep_program(self):
        """Get the EEP Program"""
        return self.get_eep_program(self.program)

    def normalize_us_state(self, input_name, home_status=None):
        """Return the US State"""
        if input_name is None:
            if home_status:
                input_name = home_status.home.state
                log.debug("Using State from Project - %s", input_name)
            else:
                return self.append_issue("State was not provided")

        if input_name.lower() not in ["az"]:
            return self.append_issue("State must be either 'AZ'")
        return input_name.upper()

    def normalize_climate_zone(self, input_name, home_status=None, simulation=None):
        """Return the Climate Zone"""
        if input_name is None:
            if home_status and home_status.home.climate_zone:
                input_name = home_status.home.climate_zone.zone
            elif simulation:
                input_name = simulation.climate_zone

        if input_name is None:
            msg = "Climate zone was not defined by either the home address or simulation data"
            return self.append_issue(msg)

        if int(input_name) not in [2, 4, 5]:
            return self.append_issue("Climate zone must be one of 2, 4, or 5")

        if home_status and simulation:
            if int(home_status.home.climate_zone.zone) != int(simulation.climate_zone):
                msg = "Climate zone on home (%s) does not agree with simulation climate zone (%s)"
                return self.append_issue(
                    msg % (home_status.home.climate_zone.zone, simulation.climate_zone),
                    issue_type="warning",
                )
        return int(input_name)

    def normalize_program(self, input_name, home_status=None, skip_swap=False):
        """Normalize out the program we can swap these out for pre-2019 programs"""
        if input_name is None:
            if home_status:
                input_name = home_status.eep_program.slug
                if home_status.eep_program.owner.slug != "aps":
                    return self.append_issue("This base program is not APS owned.")
            else:
                input_name = next((x for x in self.constants.VALID_PROGRAM_SLUGS if "2019" in x))

        if input_name.lower() not in self.constants.VALID_PROGRAM_SLUGS:
            return self.append_issue("This is not an APS recognized valid active program")

        if "2019" in input_name:
            if input_name in self.constants.VALID_PROGRAM_SLUGS:
                return input_name
            return next((x for x in self.constants.VALID_PROGRAM_SLUGS if "2019" in x))

        if skip_swap:
            return input_name

        hers = self.simulation.non_pv_hers_score
        if hers <= 60:
            program_slug = next((x for x in self.constants.VALID_PROGRAM_SLUGS if "60" in x))
        else:
            program_slug = next((x for x in self.constants.VALID_PROGRAM_SLUGS if "60" not in x))
        return program_slug

    def normalize_thermostat_option(self, input_name, home_status=None):
        """Normalize out the thermostat options"""
        if input_name is None:
            if home_status:
                if not hasattr(home_status.home, "subdivision"):
                    return None
                if home_status.home.subdivision:
                    return home_status.home.subdivision.get_aps_thermostat_option()
            return None
        from axis.customer_aps.models import SMART_TSTAT_ELIGIBILITY

        if input_name and input_name not in dict(SMART_TSTAT_ELIGIBILITY).keys():
            return self.append_issue("Thermostat option %s is not valid" % input_name)
        return input_name

    def normalize_thermostat_qty(self, input_name, home_status=None):
        """Normalize out the thermostat options"""
        if input_name is None:
            if home_status:
                if not hasattr(home_status.home, "subdivision"):
                    return None
                if home_status.home.subdivision:
                    status = home_status.floorplan.get_approved_status(home_status.home.subdivision)
                    return status.thermostat_qty
            input_name = 0
        if not isinstance(input_name, int):
            return self.append_issue("Thermostat qty %s is not valid" % input_name)
        return max(0, min(input_name, 3))

    # pylint: disable=inconsistent-return-statements
    def get_simulation_data_model(self, floorplan):
        """Get the simulation data model"""
        err = "Floorplan does not contain any simulation result data from REM/Rate or Ekotrope."
        if floorplan.input_data_type == "remrate":
            return RemRateSimulation(simulation_id=floorplan.remrate_target.id)
        elif floorplan.input_data_type == "ekotrope":
            return EkotropeSimulation(house_plan_id=floorplan.ekotrope_houseplan.id)
        else:
            self.append_issue(err)

    def get_default_data_model(self, simulation):
        """Overrideable method to get the simulation model"""
        return SimulatedInputBase(simulation=simulation)

    def notify_program_changes(self, home_status):
        """Notify anyone if the program changes."""
        companies = [home_status.company]
        try:
            companies.append(home_status.home.get_builder())
        except AttributeError:
            log.info("No builder found for %s", home_status)

        context = {
            "home_url": home_status.home.get_absolute_url(),
            "home": "{}".format(home_status.home),
            "program": "{}".format(self.eep_program),
            "hers": self.simulation.non_pv_hers_score,
            "climate_zone": self.climate_zone,
        }
        for company in companies:
            ApsUpdatedMetersetMessage().send(context=context, company=company)

    def update_program(self):
        """Update the program based on the swap if needed"""
        # At this point we are clean we have climate zone, simulation, and optionally home_status
        msg = "Unable to update program as this program is complete or Incentive Records exist."
        if self.home_status and self.home_status.eep_program.slug != self.program:
            if self.home_status.state != "complete" and not self.home_status.ippitem_set.exists():
                from axis.eep_program.models import EEPProgram

                try:
                    program = EEPProgram.objects.get(slug=self.program)
                except EEPProgram.DoesNotExist:
                    raise
                self.home_status.eep_program = program
                self.home_status.save()
                log.debug("Updated home status %r to use program %r", self.home_status, program)
                if self.notify_on_program_change:
                    self.notify_program_changes(self.home_status)
            else:
                self.append_issue(msg)

    @property
    def incentives(self):
        """Get the Incentive model to use"""
        from axis.eep_program.models import EEPProgram

        kwargs = {
            "program_slug": self.program,
            "thermostat_option": self.thermostat_option,
            "thermostat_qty": self.thermostat_qty,
        }

        if self.program == "aps-energy-star-2019-tstat":
            return APSIncentive2019Tstat(**kwargs)
        elif self.program == "aps-energy-star-2019-tstat-addon":
            return APSIncentive2019Addon(**kwargs)
        try:
            return APSIncentive(**kwargs)
        except EEPProgram.DoesNotExist:
            self.append_issue("No 2018/2019 program!")

    def dump_simulation(self, as_dict=False):
        """Provide a way to dump the data so we can use it in a test case."""
        kwargs = {
            "us_state": self.us_state,
            "climate_zone": self.climate_zone,
            "electric_utility": self.electric_utility,
            "gas_utility": self.gas_utility,
            "program": self.program,
            "simulation": self.simulation.data,
            "thermostat_option": self.thermostat_option,
            "thermostat_qty": self.thermostat_qty,
        }

        if as_dict:
            return kwargs
        return "kwargs = " + json.dumps(kwargs, indent=4)

    def result_data(self, include_reports=True):
        """Here for use later on similar to the NEEA / ETO methods"""
        return self.incentives.data


class APSCalculator(APSBaseCalculator):
    """The 2019 Calculator"""
