"""forms.py: Django customer_eto"""
import datetime
import logging
import re

from django import forms
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelChoiceField
from django.utils.timezone import now
from simulation.models import (
    get_or_import_rem_simulation,
    get_or_import_ekotrope_simulation,
    Simulation,
)

from axis.company.models import Company
from axis.company.utils import can_view_or_edit_eto_account, can_edit_eto_ccb_number
from axis.eep_program.models import EEPProgram
from axis.ekotrope.models import Project
from axis.filehandling.forms import AsynchronousProcessedDocumentForm
from axis.remrate_data.models import Simulation as RemSimulation
from . import models
from axis.customer_eto.calculator.eps import ETO_GEN2
from .calculator.eps.base import EPSInputException
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from .enumerations import (
    Fireplace2020,
    ETO_2020_PRIMARY_HEATING_EQUIPMENT_TYPE_CHOICES,
    ETO_2020_GRID_HARMONIZATION_ELEMENT_CHOICES,
    ETO_2020_SMART_THERMOSTAT_BRAND_CHOICES,
    ETO_2020_ADDITIONAL_INCENTIVE_CHOICES,
    ETO_2020_SOLAR_ELEMENTS_CHOICES,
    ETO_2020_BUILDER_CHOICES,
    ProjectTrackerSubmissionStatus,
)

TIME_FILTER = now() - datetime.timedelta(days=60)

__author__ = "Steven Klass"
__date__ = "9/17/13 11:21 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


class EPSCalculatorBasicForm(forms.Form):
    """Basic EPS Calculator"""

    choices = [
        ("astoria", "Astoria"),
        ("burns", "Burns"),
        ("eugene", "Eugene"),
        ("medford", "Medford"),
        ("northbend", "North Bend"),
        ("pendleton", "Pendleton"),
        ("portland", "Portland"),
        ("redmond", "Redmond"),
        ("salem", "Salem"),
    ]
    location = forms.ChoiceField(choices=choices, required=True)

    us_state = forms.ChoiceField(
        choices=[("OR", "Oregon"), ("WA", "Washington")], required=True, label="US State"
    )

    choices = [
        ("path 1", "Path 1"),
        ("path 2", "Path 2"),
        ("path 3", "Path 3"),
        ("path 4", "Path 4"),
        ("path 5", "Path 5"),
        ("pct", "Percentage Improvement"),
    ]
    pathway = forms.ChoiceField(choices=choices, required=False)

    primary_heating_equipment_type = forms.ChoiceField(
        choices=ETO_2020_PRIMARY_HEATING_EQUIPMENT_TYPE_CHOICES,
        required=True,
        label="Primary Heat Equipment",
    )

    hot_water_ef = forms.FloatField(initial=0, label="Hot Water EF", required=False)

    choices = [("Storage", "Storage"), ("Tankless", "Tankless")]
    hot_water_type = forms.ChoiceField(choices=choices, required=True)

    choices = [
        ("pacific power", "Pacific Power"),
        ("portland general", "Portland General"),
        ("other/none", "Other/None"),
    ]
    electric_utility = forms.ChoiceField(choices=choices, required=True)

    choices = [
        ("nw natural", "NW Natural"),
        ("cascade", "Cascade"),
        ("avista", "Avista"),
        ("other/none", "Other/None"),
    ]
    gas_utility = forms.ChoiceField(choices=choices, required=True)

    builder = forms.ChoiceField(choices=ETO_2020_BUILDER_CHOICES, required=False)

    conditioned_area = forms.FloatField(required=True)

    program = forms.ModelChoiceField(
        queryset=EEPProgram.objects.filter(owner__slug="eto", is_qa_program=False),
        required=True,
        label="Program",
    )

    choices = [
        ("no qualifying smart thermostat", "No Qualifying Smart Thermostat"),
        ("yes-ducted gas furnace", "Yes-Ducted Gas Furnace"),
        ("yes-ducted air source heat pump", "Yes-Ducted Air Source Heat Pump"),
    ]
    qualifying_thermostat = forms.ChoiceField(choices=choices, required=False)
    qty_shower_head_1p5 = forms.IntegerField(
        required=False, initial=0, label="Qty 1.5 GPM Showerhead"
    )
    qty_shower_head_1p6 = forms.IntegerField(
        required=False, initial=0, label="Qty 1.6 GPM Showerhead"
    )
    qty_shower_head_1p75 = forms.IntegerField(
        required=False, initial=0, label="Qty 1.75 GPM Showerhead"
    )
    qty_shower_wand_1p5 = forms.IntegerField(
        required=False, initial=0, label="Qty 1.5 GPM Showerwand"
    )

    code_heating_therms = forms.FloatField(required=True, initial=0, label="Heating thm")
    code_heating_kwh = forms.FloatField(required=True, initial=0, label="Heating kWh")
    code_cooling_kwh = forms.FloatField(required=True, initial=0, label="Cooling kWh")
    code_hot_water_therms = forms.FloatField(required=True, initial=0, label="Hot Wtr thm")
    code_hot_water_kwh = forms.FloatField(required=False, initial=0, label="Hot Water kWh")
    code_lights_and_appliances_therms = forms.FloatField(
        required=True, initial=0, label="Lht & App thm"
    )
    code_lights_and_appliances_kwh = forms.FloatField(
        required=True, initial=0, label="Lht & App kWh"
    )
    code_electric_cost = forms.FloatField(required=True, initial=0, label="Electric Cost")
    code_gas_cost = forms.FloatField(required=True, initial=0, label="Gas Cost")

    improved_heating_therms = forms.FloatField(required=False, label="Heating thm")
    improved_heating_kwh = forms.FloatField(required=False, label="Heating kWh")
    improved_cooling_kwh = forms.FloatField(required=False, label="Cooling kWh")
    improved_hot_water_therms = forms.FloatField(required=False, label="Hot Water thm")
    improved_hot_water_kwh = forms.FloatField(required=False, label="Hot Wtr kWh")
    improved_lights_and_appliances_therms = forms.FloatField(required=False, label="Lht & App thm")
    improved_lights_and_appliances_kwh = forms.FloatField(required=False, label="Lht & App kWh")
    improved_electric_cost = forms.FloatField(required=False, label="Electric Cost")
    improved_gas_cost = forms.FloatField(required=False, label="Gas Cost")
    improved_solar_hot_water_therms = forms.FloatField(required=False, label="Solar Wtr thm")
    improved_solar_hot_water_kwh = forms.FloatField(required=False, label="Solar Wtr kWh")
    improved_pv_kwh = forms.FloatField(required=False, label="PV kWh")

    generated_solar_pv_kwh = forms.FloatField(
        required=False, initial=0, label="Annual PV generated kWh"
    )

    has_gas_fireplace = forms.ChoiceField(
        choices=((x.value, x.value) for x in Fireplace2020), required=False
    )

    grid_harmonization_elements = forms.ChoiceField(
        choices=ETO_2020_GRID_HARMONIZATION_ELEMENT_CHOICES,
        required=False,
        label="Energy smart homes elements",
    )

    smart_thermostat_brand = forms.ChoiceField(
        choices=ETO_2020_SMART_THERMOSTAT_BRAND_CHOICES, required=False
    )

    eps_additional_incentives = forms.ChoiceField(
        choices=ETO_2020_ADDITIONAL_INCENTIVE_CHOICES,
        required=False,
        label="EPS Additional Incentives",
    )

    solar_elements = forms.ChoiceField(
        choices=ETO_2020_SOLAR_ELEMENTS_CHOICES,
        required=False,
        label="Solar Elements",
    )

    def clean_heat_type(self):
        """Simplify the name"""
        heat_type = self.cleaned_data["heat_type"]
        if "gas" in heat_type.lower():
            return "gas heat"
        return "heat pump"

    def clean(self):
        """Validated"""
        cleaned_data = super(EPSCalculatorBasicForm, self).clean()
        if self.is_valid():
            from django.forms.utils import ErrorList

            errors = []
            if cleaned_data["program"].slug not in ETO_GEN2:
                if not cleaned_data.get("pathway"):
                    errors.append(
                        "Energy Trust Pathway: This field is required for program selected"
                    )
                if not cleaned_data.get("hot_water_type"):
                    errors.append("Hot Water Type: This field is required for program selected")
            else:
                if not cleaned_data.get("qualifying_thermostat"):
                    errors.append(
                        "Qualifying Thermostat: This field is required for program selected"
                    )
                if cleaned_data.get("heat_type") == "heat pump":
                    cleaned_data["has_ashp"] = True
            try:
                EPSCalculator(**cleaned_data)
            except EPSInputException as err:
                if err.args and len(err.args) == 2:
                    log.error(err.args[1])
                    errors.append(err.args[1])
                else:
                    log.error(err)
                    errors.append("%r" % err)
            except Exception as err:  # pylint: disable=broad-except
                log.exception(err)
                errors.append(err)

            if errors:
                for item in errors:
                    log.warning(item)
                self._errors["__all__"] = ErrorList(errors)
        return cleaned_data


class EPSCalculatorForm(forms.Form):
    """EPS Calculator Form"""

    simulation = ModelChoiceField(
        required=False,
        queryset=Simulation.objects.filter(modified_date__gte=TIME_FILTER),
        label="Simulation data",
    )
    rem_simulation = ModelChoiceField(
        required=False,
        queryset=RemSimulation.objects.filter(
            export_type__in=[4], building__last_update__gte=TIME_FILTER
        ),
        label="REM/Rate® data",
        help_text="Enter name, development or builder name.",
    )

    eko_simulation = ModelChoiceField(
        required=False,
        queryset=Project.objects.filter(modified_date__gte=TIME_FILTER),
        label="Ekotrope® data",
        help_text="Enter name, development or builder name.",
    )
    use_legacy_simulation = forms.BooleanField(
        initial=app.USE_LEGACY_SIMULATION, help_text="Use legacy REM Simulation", required=False
    )

    us_state = forms.ChoiceField(
        choices=[("OR", "Oregon"), ("WA", "Washington")], required=True, label="US State"
    )
    choices = [
        ("path 1", "Path 1"),
        ("path 2", "Path 2"),
        ("path 3", "Path 3"),
        ("path 4", "Path 4"),
        ("path 5", "Path 5"),
        ("pct", "Percentage Improvement"),
    ]
    pathway = forms.ChoiceField(choices=choices, required=False, label="Energy Trust Pathway")

    primary_heating_equipment_type = forms.CharField(
        required=False,
        label="Primary Heat Equipment",
    )

    hot_water_ef = forms.FloatField(initial=0, label="Hot Water EF", required=False)

    choices = [("Storage", "Storage"), ("Tankless", "Tankless")]
    hot_water_type = forms.ChoiceField(choices=choices, required=False)

    electric_slugs = ["pacific-power", "portland-electric"]
    electric_utility = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE), required=False
    )

    gas_slugs = ["nw-natural-gas", "cascade-gas", "avista"]
    gas_utility = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE), required=False
    )

    builder = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).all(),
        required=False,
    )

    program = forms.ModelChoiceField(
        queryset=EEPProgram.objects.filter(owner__slug="eto", is_qa_program=False), required=True
    )

    qty_shower_wand_1p5 = forms.IntegerField(required=False, initial=0)
    qty_shower_head_1p5 = forms.IntegerField(required=False, initial=0)
    qty_shower_head_1p6 = forms.IntegerField(required=False, initial=0)
    qty_shower_head_1p75 = forms.IntegerField(required=False, initial=0)

    generated_solar_pv_kwh = forms.FloatField(
        required=False, initial=0, label="Annual PV generated kWh"
    )

    has_gas_fireplace = forms.ChoiceField(
        choices=((x.value, x.value) for x in Fireplace2020), required=False
    )

    grid_harmonization_elements = forms.ChoiceField(
        choices=ETO_2020_GRID_HARMONIZATION_ELEMENT_CHOICES,
        required=False,
        label="Energy smart homes elements",
    )

    smart_thermostat_brand = forms.ChoiceField(
        choices=ETO_2020_SMART_THERMOSTAT_BRAND_CHOICES, required=False
    )

    eps_additional_incentives = forms.ChoiceField(
        choices=ETO_2020_ADDITIONAL_INCENTIVE_CHOICES,
        required=False,
        label="EPS Additional Incentives",
    )

    solar_elements = forms.ChoiceField(
        choices=ETO_2020_SOLAR_ELEMENTS_CHOICES,
        required=False,
        label="Solar Elements",
    )

    def __init__(self, data=None, *args, **kwargs):
        company = kwargs.pop("company", None)
        if data and "company" in data:
            company = data.pop("company", None)
        super(EPSCalculatorForm, self).__init__(data, *args, **kwargs)
        if data:
            self.home_status = data.get("home_status")
        if company:
            companies = [company]
            if company.company_type == "provider":
                raters = Company.objects.filter_by_company(company).filter(company_type="rater")
                companies = [company] + list(raters)

            # This queryset get large x3 so we do some inspection and trim it so we focus on our
            # our target or a narrow 60 day window.
            has_simulation, has_rem, has_eko = False, False, False
            if data and "simulation" in data and data["simulation"]:
                has_simulation = True
            if data and "rem_simulation" in data and data["rem_simulation"]:
                has_rem = True
            if data and "eko_simulation" in data and data["eko_simulation"]:
                has_eko = True

            if has_simulation:
                ids = data["simulation"]
                if isinstance(data["simulation"], (int, str)):
                    ids = [data["simulation"]]
                simulations = Simulation.objects.filter(id__in=ids, company__in=companies)
            else:
                if has_rem is False and has_eko is False:
                    simulations = Simulation.objects.filter(
                        company__in=companies, modified_date__gte=TIME_FILTER
                    )
                else:
                    simulations = Simulation.objects.none()

            self.fields["simulation"].queryset = simulations

            if has_rem:
                ids = data["rem_simulation"]
                if isinstance(data["rem_simulation"], (int, str)):
                    ids = [data["rem_simulation"]]
                rem_sims = RemSimulation.objects.filter_by_company(company).filter(
                    export_type__in=[4], id__in=ids
                )
            else:
                if has_simulation is False and has_eko is False:
                    rem_sims = RemSimulation.objects.filter_by_company(company).filter(
                        export_type__in=[4], building__last_update__gte=TIME_FILTER
                    )
                else:
                    rem_sims = RemSimulation.objects.none()
            self.fields["rem_simulation"].queryset = rem_sims

            if has_eko:
                ids = data["eko_simulation"]
                if isinstance(data["eko_simulation"], (int, str)):
                    ids = [data["eko_simulation"]]
                ekotrope_hps = Project.objects.filter_by_company(company).filter(id__in=ids)
            else:
                if has_simulation is False and has_rem is False:
                    ekotrope_hps = Project.objects.filter_by_company(company).filter(
                        modified_date__gte=TIME_FILTER
                    )
                else:
                    ekotrope_hps = Project.objects.none()

            self.fields["eko_simulation"].queryset = ekotrope_hps

    def clean_primary_heating_equipment_type(self):
        data = self.cleaned_data["primary_heating_equipment_type"]
        cleaned_data = re.sub("Pump - ", "Pump \u2013 ", data)
        # print("Out ", data == cleaned_data)
        return cleaned_data

    def clean_gas_utility(
        self,
    ):
        """Get the utility slug"""
        data = self.cleaned_data["gas_utility"]
        if data and data.slug not in self.gas_slugs:
            log.info("Non-default Gas Company %s - Setting None", data)
            return None
        return data

    def clean_electric_utility(
        self,
    ):
        """Get the utility slug"""
        data = self.cleaned_data["electric_utility"]
        if data and data.slug not in self.electric_slugs:
            log.info("Non-default Electric Company %s - Setting None", data)
            return None
        return data

    def clean_simulation_data(self, data, errors):
        """Clean off the REM/Rate data and Ekotrope data and push to simulation"""
        if data.get("rem_simulation", None) and data.get("eko_simulation", None):
            errors.append("REM/Rate® data AND Ekotrope® data not supported use one or the other")

        old_slugs = ["eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]
        if data["program"].slug in old_slugs:
            data["use_legacy_simulation"] = True

        no_convert = data.get("use_legacy_simulation")
        if data.get("eko_simulation") and no_convert:
            errors.append("You must convert an ekotrope model to axis model")

        sim = data.pop("simulation", None)
        rem = data.pop("rem_simulation", None)
        eko = data.pop("eko_simulation", None)

        if rem is None and eko is None and sim is None:
            errors.append("Simulation Data is required")

        if no_convert:
            if sim:
                data["simulation"] = (
                    sim.floorplan.remrate_target or sim.floorplan.ekotrope_houseplan
                )
            else:
                data["simulation"] = rem or eko
        else:
            if sim:
                data["simulation"] = sim
            elif rem:
                data["simulation"] = get_or_import_rem_simulation(
                    simulation_id=rem.pk, use_tasks=False
                )
            elif eko:
                _kwargs = {"houseplan_id": eko.pk, "use_tasks": False}
                if isinstance(eko, Project):
                    if eko.data == {}:
                        # Note this may happen if we only have a stubbed list.
                        # On save this will get updated.
                        log.info("Ekotrope project data is missing")
                    else:
                        _kwargs = {"project_id": eko.pk, "use_tasks": False}
                        data["simulation"] = get_or_import_ekotrope_simulation(**_kwargs)

    def clean(self):
        """Verify everything is oK."""
        cleaned_data = super(EPSCalculatorForm, self).clean()
        if self.is_valid():
            from django.forms.utils import ErrorList

            errors = []
            self.clean_simulation_data(data=cleaned_data, errors=errors)
            if cleaned_data["program"].slug not in ETO_GEN2:
                if not cleaned_data.get("pathway"):
                    errors.append(
                        "Energy Trust Pathway: This field is required for program selected"
                    )
                if not cleaned_data.get("hot_water_type"):
                    errors.append("Hot Water Type: This field is required for program selected")
            #
            old_slugs = ["eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]
            if cleaned_data["program"].slug not in old_slugs:
                cleaned_data.pop("heat_type", None)
                cleaned_data.pop("qualifying_thermostat", None)

            try:
                EPSCalculator(**cleaned_data)
            except EPSInputException as err:
                if err.args and len(err.args) == 2:
                    errors.append(err.args[1])
                else:
                    errors.append("%r" % err)
            except Exception as err:  # pylint: disable=broad-except
                log.exception(err)
                errors.append("%r" % err)

            if errors:
                for item in errors:
                    log.info(item)
                self._errors["__all__"] = ErrorList(errors)
        return cleaned_data


class ETOAccountForm(forms.ModelForm):
    """ETO Account Number form"""

    account_number = forms.CharField(max_length=32, required=False, label="ETO Account Number")
    ccb_number = forms.CharField(max_length=32, required=False, label="CCB Number")

    class Meta(object):
        """Meta"""

        model = models.ETOAccount
        fields = ("account_number", "ccb_number")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        company = kwargs.pop("company")
        company_type = kwargs.pop("company_type")

        try:
            instance = models.ETOAccount.objects.get(company=company)
            kwargs["instance"] = kwargs.get("instance", instance)
        except ObjectDoesNotExist:
            pass

        super(ETOAccountForm, self).__init__(*args, **kwargs)
        if not can_view_or_edit_eto_account(user, company_type):
            del self.fields["account_number"]
        if not can_edit_eto_ccb_number(user, company_type):
            del self.fields["ccb_number"]


class PermitAndOccupancySettingsForm(forms.ModelForm):
    """Validation form required for render and validation."""

    # NOTE: Don't specify special widgets, the rendering scenario is too
    # specialized to make use of them.

    class Meta:
        model = models.PermitAndOccupancySettings
        fields = (
            "reeds_crossing_compliance_option",
            "rosedale_parks_compliance_option",
        )
        labels = {
            "reeds_crossing_compliance_option": "Reed's Crossing compliance option",
            "rosedale_parks_compliance_option": "Rosedale Parks compliance option",
        }
        widgets = {
            "reeds_crossing_compliance_option": forms.RadioSelect,
            "rosedale_parks_compliance_option": forms.RadioSelect,
        }

    def __init__(self, company, instance, *args, **kwargs):
        from axis.company.models import Company
        from axis.subdivision.models import Subdivision
        from axis.home.models import Home

        settings = instance.permitandoccupancysettings_set.get_for_company(company)
        super(PermitAndOccupancySettingsForm, self).__init__(instance=settings, *args, **kwargs)

        community = False  # invalid logic tree for a community context
        if not instance or not instance.pk:
            community = False
        elif isinstance(instance, Home) and instance.subdivision_id:
            community = instance.subdivision.community
        elif isinstance(instance, Subdivision):
            community = instance.community
        elif (
            isinstance(self.instance, Company)
            and self.instance.slug in app.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS
        ):
            community = None  # selectable but no preference specified

        valid_community = community is None or (
            community and community.slug in app.CITY_OF_HILLSBORO_COMMUNITY_SLUGS
        )

        for name, field in list(self.fields.items()):
            if (
                valid_community
                and community
                and name != app.CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS[community.slug]
            ):
                del self.fields[name]
                continue

            if hasattr(field, "choices") and field.choices and field.choices[0][0] in (None, ""):
                field.choices = field.choices[1:]  # Remove the passive 'None' choice.


class EPSPaymentUpdateForm(forms.ModelForm):
    """Form for updating payment info"""

    project_id = forms.CharField(required=False, label="ENH Project ID")
    solar_project_id = forms.CharField(required=False, label="SLE Project ID")

    submit_status = forms.ChoiceField(
        required=False, label="ENH Submit Status", choices=ProjectTrackerSubmissionStatus.choices
    )
    solar_submit_status = forms.ChoiceField(
        required=False, label="SLE Submit Status", choices=ProjectTrackerSubmissionStatus.choices
    )

    baseline_builder_electric_incentive = forms.DecimalField(
        label="Current Builder Electric Incentive", max_digits=8, decimal_places=2, required=False
    )
    baseline_builder_gas_incentive = forms.DecimalField(
        label="Current Builder Gas Incentive", max_digits=8, decimal_places=2, required=False
    )

    baseline_rater_electric_incentive = forms.DecimalField(
        label="Current Rater Electric Incentive", max_digits=8, decimal_places=2, required=False
    )
    baseline_rater_gas_incentive = forms.DecimalField(
        label="Current Rater Gas Incentive", max_digits=8, decimal_places=2, required=False
    )

    baseline_net_zero_eps_incentive = forms.DecimalField(
        label="Current Net Zero EPS Incentive", max_digits=8, decimal_places=2, required=False
    )
    baseline_energy_smart_homes_eps_incentive = forms.DecimalField(
        label="Current Energy Smart Homes EPS Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
    )

    baseline_net_zero_solar_incentive = forms.DecimalField(
        label="Current Net Zero Solar Incentive", max_digits=8, decimal_places=2, required=False
    )
    baseline_energy_smart_homes_solar_incentive = forms.DecimalField(
        label="Current Energy Smart Homes Solar Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
    )

    baseline_therm_savings = forms.FloatField(label="Current Therm Savings", required=False)
    baseline_kwh_savings = forms.FloatField(label="Current kWh Savings", required=False)
    baseline_mbtu_savings = forms.FloatField(label="Current MBtu Savings", required=False)

    revised_builder_electric_incentive = forms.DecimalField(
        label="Modified Builder Electric Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )
    revised_builder_gas_incentive = forms.DecimalField(
        label="Modified Builder Gas Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )

    revised_rater_electric_incentive = forms.DecimalField(
        label="Modified Rater Electric Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )
    revised_rater_gas_incentive = forms.DecimalField(
        label="Modified Rater Gas Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )

    revised_net_zero_eps_incentive = forms.DecimalField(
        label="Modified Net Zero EPS Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )
    revised_energy_smart_homes_eps_incentive = forms.DecimalField(
        label="Modified Energy Smart Homes EPS Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )

    revised_net_zero_solar_incentive = forms.DecimalField(
        label="Modified Net Zero Solar Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )
    revised_energy_smart_homes_solar_incentive = forms.DecimalField(
        label="Modified Energy Smart Homes Solar Incentive",
        max_digits=8,
        decimal_places=2,
        required=False,
        min_value=0.00,
        max_value=10000.00,
    )

    revised_therm_savings = forms.FloatField(label="Modified Therm Savings", required=False)
    revised_kwh_savings = forms.FloatField(label="Modified kWh Savings", required=False)
    revised_mbtu_savings = forms.FloatField(label="Modified MBtu Savings", required=False)

    class Meta(object):
        """Meta"""

        model = models.FastTrackSubmission
        fields = (
            "project_id",
            "submit_status",
            "solar_project_id",
            "solar_submit_status",
            "baseline_builder_electric_incentive",
            "baseline_builder_gas_incentive",
            "baseline_rater_electric_incentive",
            "baseline_rater_gas_incentive",
            "baseline_net_zero_eps_incentive",
            "baseline_energy_smart_homes_eps_incentive",
            "baseline_net_zero_solar_incentive",
            "baseline_energy_smart_homes_solar_incentive",
            "baseline_therm_savings",
            "baseline_kwh_savings",
            "baseline_mbtu_savings",
            "revised_builder_electric_incentive",
            "revised_builder_gas_incentive",
            "revised_rater_electric_incentive",
            "revised_rater_gas_incentive",
            "revised_net_zero_eps_incentive",
            "revised_energy_smart_homes_eps_incentive",
            "revised_net_zero_solar_incentive",
            "revised_energy_smart_homes_solar_incentive",
            "revised_therm_savings",
            "revised_kwh_savings",
            "revised_mbtu_savings",
            "payment_revision_comment",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(EPSPaymentUpdateForm, self).__init__(*args, **kwargs)

        self.fields["payment_revision_comment"].required = True

        if kwargs["instance"]:
            instance = kwargs["instance"]
            for f in self.fields:
                if f in [
                    "submit_status",
                    "solar_submit_status",
                    "project_id",
                    "solar_project_id",
                ]:
                    self.fields[f].initial = getattr(instance, f)
                    continue

                if f in [
                    "payment_revision_comment",
                ] or f.startswith("revised_"):
                    continue

                base = f.replace("baseline_", "")

                self.fields[f].widget.attrs["readonly"] = True
                self.fields[f].initial = getattr(instance, base)
                if getattr(instance, f"original_{base}"):
                    self.fields[f"baseline_{base}"].initial = getattr(instance, f"original_{base}")
                    self.fields[f"revised_{base}"].initial = getattr(instance, base)

            non_net_zero = [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]
            slug = self.instance.home_status.eep_program.slug
            if slug.startswith("eto") and slug in non_net_zero:
                net_zero_fields = [
                    "revised_net_zero_eps_incentive",
                    "revised_energy_smart_homes_eps_incentive",
                    "revised_net_zero_solar_incentive",
                    "revised_energy_smart_homes_solar_incentive",
                    "revised_therm_savings",
                    "revised_kwh_savings",
                    "revised_mbtu_savings",
                ]
                for f in net_zero_fields:
                    self.fields[f].widget.attrs["readonly"] = True

    def save(self, commit=True):
        """Save swap in the new values and changeout the originals"""
        super(EPSPaymentUpdateForm, self).save(commit=False)
        if commit:
            has_changes = False
            baseline_builder_incentive = self.instance.builder_incentive
            if self.instance.original_builder_incentive:
                baseline_builder_incentive = self.instance.original_builder_incentive
            baseline_rater_incentive = self.instance.rater_incentive
            if self.instance.original_rater_incentive:
                baseline_rater_incentive = self.instance.original_rater_incentive

            for field, value in self.cleaned_data.items():
                if field.startswith("revised_") and value is not None:
                    has_changes = True
                    base = field.replace("revised_", "")
                    prior_original_incentive = getattr(self.instance, f"original_{base}")
                    if prior_original_incentive in [None, 0.0]:
                        incentive = getattr(self.instance, base)
                        setattr(self.instance, f"original_{base}", incentive)

                    setattr(self.instance, base, value)
                if field == "project_id":
                    if getattr(self.instance, field) != self.cleaned_data[field]:
                        has_changes = True
                        setattr(self.instance, field, self.cleaned_data[field])
                        if self.cleaned_data[field] in ["", None]:
                            setattr(self.instance, "submit_status", None)
                            setattr(self.instance, "submit_user", None)
                if field == "solar_project_id":
                    if getattr(self.instance, field) != self.cleaned_data[field]:
                        has_changes = True
                        setattr(self.instance, field, self.cleaned_data[field])
                        if self.cleaned_data[field] in ["", None]:
                            setattr(self.instance, "solar_submit_status", None)
                            setattr(self.instance, "submit_user", None)

            if has_changes:
                self.instance.payment_revision_comment = self.cleaned_data[
                    "payment_revision_comment"
                ]

                updated_rater_incentive = self.instance.rater_gas_incentive
                updated_rater_incentive += self.instance.rater_electric_incentive

                if updated_rater_incentive != baseline_rater_incentive:
                    self.instance.original_rater_incentive = baseline_rater_incentive
                    self.instance.rater_incentive = updated_rater_incentive

                updated_builder_incentive = self.instance.builder_gas_incentive
                updated_builder_incentive += self.instance.builder_electric_incentive
                non_net_zero = [None, "eto", "eto-2016", "eto-2017", "eto-2018", "eto-2019"]
                slug = self.instance.home_status.eep_program.slug
                if slug.startswith("eto") and slug not in non_net_zero:
                    updated_builder_incentive += self.instance.net_zero_eps_incentive
                    updated_builder_incentive += self.instance.energy_smart_homes_eps_incentive
                    updated_builder_incentive += self.instance.net_zero_solar_incentive
                    updated_builder_incentive += self.instance.energy_smart_homes_solar_incentive
                if slug in ["eto-fire-2021", "eto-2022"]:
                    updated_builder_incentive += self.instance.triple_pane_window_incentive
                    updated_builder_incentive += self.instance.rigid_insulation_incentive
                    updated_builder_incentive += self.instance.sealed_attic_incentive

                if updated_builder_incentive != baseline_builder_incentive:
                    self.instance.original_builder_incentive = baseline_builder_incentive
                    self.instance.builder_incentive = updated_builder_incentive

                self.instance.payment_change_user = self.user
                self.instance.payment_change_datetime = now()

            self.instance.save()
            self._save_m2m()
        return self.instance


class WashingtonCodeCreditProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    def clean_task_name(self):
        from axis.customer_eto.tasks.washington_code_credit import WashingtonCodeCreditUploadTask

        return WashingtonCodeCreditUploadTask

    def clean(self):
        cleaned_data = super(AsynchronousProcessedDocumentForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data
