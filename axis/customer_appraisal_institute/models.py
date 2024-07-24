"""models.py: Django customer_appraisal_institute"""


import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from axis.remrate_data.models import Simulation, MULT_DESIGNATOR

__author__ = "Steven Klass"
__date__ = "6/2/13 9:03 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

MULTS_COMMENT = "{} Where multiples exist, the dominate value is shown.".format(MULT_DESIGNATOR)


class GEEAData(Simulation):
    """This is just a fake model we want to enable for use for GEEA Stuff"""

    class Meta:
        proxy = True

    def add_comment(self, comment=None):
        if not hasattr(self, "_comments"):
            self._comments = []
        if comment:
            if comment not in self._comments:
                self._comments.append(comment)

    def get_insulation(self):
        """Gets the insullation.

        ISSUES:
            -RR Gives multiple values
            -RR does not give you what type of insulation (blown / batt) except for the ceiling
                and then its ONLY blown / batt.
        """

        results = {
            "fiberglass_insulation": False,
            "blownin_insulation": False,
            "cellulose_insulation": False,
            "batt_insulation": False,
            "wall_r_value": None,
            "ceiling_r_value": None,
            "floor_r_value": None,
            "insulation_other": None,
            "hers_insulation_installed": False,
            "basement_describe": None,
            "basement_insulation": False,
        }
        other_str = []
        hers_inst_rating = set()
        try:
            objects = self.roof_set.all()
            for item in objects:
                hers_inst_rating.add(item.type.insulation_grade)
            results["ceiling_r_value"] = objects[0].get_r_value()
            if objects.count() > 1:
                results["ceiling_r_value"] = "{} {}".format(
                    results["ceiling_r_value"], MULT_DESIGNATOR
                )
            if 1 in objects.values_list("type__insulation_grade", flat=True):
                results["batt_insulation"] = True
            if 2 in objects.values_list("type__insulation_grade", flat=True):
                results["blownin_insulation"] = True
        except IndexError:
            pass

        try:
            objects = self.abovegradewall_set.all()
            for item in objects:
                hers_inst_rating.add(item.type.insulation_grade)
            results["wall_r_value"] = objects[0].get_r_value()
            if objects.count() > 1:
                results["wall_r_value"] = "{} {}".format(results["wall_r_value"], MULT_DESIGNATOR)
        except IndexError:
            pass

        try:
            objects = self.slab_set.all()
            for item in objects:
                hers_inst_rating.add(item.type.insulation_grade)
            results["floor_r_value"] = objects[0].type.perimeter_r_value
            if objects.count() > 1:
                results["floor_r_value"] = "{} {}".format(results["floor_r_value"], MULT_DESIGNATOR)
        except IndexError:
            try:
                objects = self.framefloor_set.all()
                for item in objects:
                    hers_inst_rating.add(item.type.insulation_grade)
                results["floor_r_value"] = objects[0].get_r_value()
                if objects.count() > 1:
                    results["floor_r_value"] = "{} {}".format(
                        results["floor_r_value"], MULT_DESIGNATOR
                    )
            except:
                pass

        try:
            objects = self.foundationwall_set.all()
            for item in objects:
                hers_inst_rating.add(item.type.insulation_grade)
            results["basement_describe"] = "{}{}".format(
                objects[0].type, MULT_DESIGNATOR if objects.count() > 1 else ""
            )
            results["basement_insulation"] = True
        except IndexError:
            pass

        for idx in hers_inst_rating:
            results["hers_insulation_installed"] = True
            results["hers_insulation_{}".format(str(idx))] = True

        self.add_comment(MULTS_COMMENT)
        return results

    def get_envelope(self):
        """
        Envelope - Pulling from the Infiltration data
        :return: dictionary

        ISSUES:
            Unclear what envelope tightness value should be or if its needed at all?

        """
        results = {"env_data": True}
        try:
            infiltration = self.infiltration
        except ObjectDoesNotExist:
            log.warning("No infiltration")
            return results
        if infiltration.units == 1:
            results["env_measure_cfm50"] = True
        elif infiltration.units == 2:
            results["env_measure_cfm25"] = True
        elif infiltration.units == 3:
            results["env_measure_ach50"] = True
        elif infiltration.units == 4:
            results["env_measure_achnatural"] = True
        if infiltration.testing_type == 4:
            results["env_blower_door_test"] = True
        results["env_value"] = "{} H / {} C".format(
            infiltration.heating_value, infiltration.cooling_value
        )
        return results

    def get_water_efficiency(self):
        """
        Water Efficency - We have limited data but we have DOE Challenge Home info.
        :return: dict()

        ISSUES:
            RR does not capture and Reclaimed H2O , Cistern data

        """
        results = {"use_watersense": False, "indoor_air_plus": False}

        try:
            doechallenge = self.doechallenge
        except ObjectDoesNotExist:
            return results

        results["use_watersense"] = doechallenge.optional_water_sense
        results["indoor_air_plus"] = doechallenge.optional_indoor_air_plus

        return results

    def get_estar_requirements(self):
        """
        The window data
        :return: dict()

        ISSUES:
            RR does not capture whether the window was low-e, high impact, storm, double/triple,
            tinted or whether it has a solar shade.
        """
        results = {}

        estar_requirements = self.energystarrequirements_set.all()
        if estar_requirements.count() == 0:
            return results
        estar_windows = estar_requirements.filter(has_energystar_windows__gt=0)
        results["estar_windows"] = True if estar_windows.count() > 0 else False
        estar_light_fixtures = estar_requirements.filter(has_energystar_fixtures__gt=0)
        results["estar_light_fixtures"] = True if estar_light_fixtures.count() > 0 else False
        estar_appliances = estar_requirements.filter(has_energystar_appliances__gt=0)
        results["estar_appliances"] = True if estar_appliances.count() > 0 else False
        self.add_comment("REM/Rate® does not distinguish appliance types")
        return results

    def get_day_lighting(self):
        """
        Sky Light data
        :return: dict()

        ISSUES:
            RR does not capture solar tubes.

        Note: Estar light fixtures is captured in get_estar_requirements.
        """
        results = {"qty_skylights": self.skylight_set.count()}
        return results

    def get_appliances(self):
        """
        Appliance Data - Some of this comes from get_estar_requirements
        :return: dict()

        ISSUES:
            AI does not provide for Integrated or GSHP, Water heater.
        """
        results = {
            "coil_water_heater": False,
            "tankless_water_heater": False,
            "heat_pump_water_heater": False,
            "propane_appliance_energy_source": False,
            "electric_appliance_energy_source": False,
            "natural_gas_appliance_energy_source": False,
            "other_appliance_energy_source": False,
        }
        hot_water_heaters = self.hotwaterheater_set.all()
        for item in hot_water_heaters.all():
            if "water_heater_size" not in results.keys():
                results["water_heater_size"] = item.tank_size
            if item.type == 1:
                results["coil_water_heater"] = True
            elif item.type == 2:
                results["tankless_water_heater"] = True
            elif item.type == 3:
                results["heat_pump_water_heater"] = True

            if item.fuel_type == 1:
                results["natural_gas_appliance_energy_source"] = True
            elif item.fuel_type == 2:
                results["propane_appliance_energy_source"] = True
            elif item.fuel_type == 3:
                results["other_appliance_energy_source"] = True
            elif item.fuel_type == 4:
                results["electric_appliance_energy_source"] = True
            else:
                results["other_appliance_energy_source"] = True
        for item in self.installedlightsandappliances_set.all():
            if item.fuel_type == 1:
                results["natural_gas_appliance_energy_source"] = True
            elif item.fuel_type == 2:
                results["propane_appliance_energy_source"] = True
            elif item.fuel_type == 3:
                results["other_appliance_energy_source"] = True
            elif item.fuel_type == 4:
                results["electric_appliance_energy_source"] = True
            else:
                results["other_appliance_energy_source"] = True
        try:
            if self.solarsystem.type in [1, 2]:
                results["solar_water_heater"] = True
        except ObjectDoesNotExist:
            results["solar_water_heater"] = False
        return results

    def get_hvac(self):
        """
        Get HVAC data
        :return: dict()

        ISSUES:
            Only the first HVAC unit (largest) is captured
            Only the first Heater unit (largest) is captured
            Heat Pumps COP / HSPF / SEER / EER are all system dependent.
            GSHP do not display COP / HSPF / SEER / EER
            ASHP Only shows One of COP/HSPF and SEER/EER
            DFHP ONly shows HSPF / EER
            Integrated Units are not captured for simplicity
            RR only has radiant floor info for slab floors.
        """

        results = {"high_efficiency_hvac": False}

        coolers = self.airconditioner_set.all()
        heaters = self.heater_set.all()
        ashps = self.airsourceheatpump_set.all()
        gshps = self.groundsourceheatpump_set.all()
        dfhps = self.dualfuelheatpump_set.all()
        if coolers.count() > 1 or heaters.count() > 1:
            self.add_comment(MULTS_COMMENT)

        cooler = coolers[0] if coolers.count() else None
        heater = heaters[0] if heaters.count() else None
        ashp = ashps[0] if ashps.count() else None
        gshp = gshps[0] if gshps.count() else None
        dfhp = dfhps[0] if dfhps.count() else None

        if heater or cooler:
            results["high_efficiency_hvac"] = True
        if cooler:
            results["hvac_seer_rating"] = cooler.efficiency
            if cooler.efficiency_unit != 1:
                results["hvac_seer_rating"] = "{} {}".format(
                    cooler.efficiency, cooler.get_efficiency_unit_display()
                )
            # results['hvac_efficiency_rating'] = cooler.efficiency
        if heater:
            results["hvac_afue"] = heater.efficiency
            if heater.efficiency_unit != 1:
                results["hvac_afue"] = "{} {}".format(
                    heater.efficiency, heater.get_efficiency_unit_display()
                )

        if ashp or gshp or dfhp:
            results["heat_pump"] = True

        if ashp:
            if ashp.heating_efficiency_units == 3:  # HSPF
                results["heat_pump_cop"] = ashp.heating_efficiency
            elif ashp.heating_efficiency_units == 4:  # COP
                results["heat_pump_hspf"] = ashp.heating_efficiency

            if ashp.cooling_efficiency_units == 1:  # SEER
                results["heat_pump_seer"] = ashp.cooling_efficiency
            elif ashp.cooling_efficiency_units == 2:  # EER
                results["heat_pump_eer"] = ashp.heating_efficiency

        if dfhp:
            results["heat_pump_seer"] = dfhp.cooling_seer
            results["heat_pump_hspf"] = dfhp.heating_hspf

        try:
            if self.solarsystem.type in [2, 3, 4]:
                results["passive_solar"] = True
        except ObjectDoesNotExist:
            results["passive_solar"] = False

        thermostats = self.generalmechanicalequipment_set.filter(
            Q(setback_thermostat=True) | Q(setup_thermostat=True)
        )
        if thermostats.count():
            results["programable_thermostat"] = True

        if self.slab_set.filter(type__radiant_floor=1).count() > 1:
            results["radiant_heating"] = True
        if self.heater_set.filter(type=5).count() > 1:
            results["radiant_heating"] = True

        return results

    def get_energy_rating(self):
        """Gets Energy Rating Data

        :return: dict()

        ISSUES
            - RR Does not Capture HES Score
        """
        results = {"estar_rated": False}
        if self.energystar.passes_energy_star_v2:
            results["estar_rated"] = True
            results["estar_version"] = "ENERGY STAR v2.0"
        if self.energystar.passes_energy_star_v2p5:
            results["estar_rated"] = True
            results["estar_version"] = "ENERGY STAR v2.5"
        if self.energystar.passes_energy_star_v3:
            results["estar_rated"] = True
            results["estar_version"] = "ENERGY STAR v3.0"
        if self.energystar.passes_energy_star_v3p1:
            results["estar_rated"] = True
            results["estar_version"] = "ENERGY STAR v3.1"
        if self.energystar.passes_energy_star_v3p2:
            results["estar_rated"] = True
            results["estar_version"] = "ENERGY STAR v3.2"
        others = []

        if self.iecc:
            if self.iecc.passes_iecc09_code:
                others.append("IECC 09 Code Compliant")
            if self.iecc.passes_iecc12_code:
                others.append("IECC 12 Code Compliant")
            if self.iecc.passes_iecc15_code:
                others.append("IECC 15 Code Compliant")
        if self.energystar:
            if self.energystar.passes_doe_zero:
                others.append("Passes DOE Zero Energy Rated Home")
        if self.hers:
            if self.hers.passes_2005_epact_tax_credit:
                others.append("Passes EPAAct Tax Credit")

        if len(others):
            results["estar_other"] = True
            results["estar_other_describe"] = ", ".join(others)

        return results

    def get_indoor_air_quality(self):
        """Indoor Air Quality

        Part of this comes from the energy star stuff.
        Whole building ventilation is there.


        """
        results = {}
        try:
            ventilation = self.infiltration
            if ventilation.mechanical_vent_type != 0 and ventilation.cooling_type == 1:
                results["whole_building_ventilation"] = True
        except ObjectDoesNotExist:
            results["whole_building_ventilation"] = False
        return results

    def get_hers_information(self):
        """HERS Information

        :return: dict()

        ISSUES:
            CostRate info is very RARELY used.

        """
        results = {}
        results["hers_score"] = self.hers.score
        self.add_comment("RESNET HERS Score")
        try:
            results["monthly_savings_on_rating"] = self.costrate.total_costs_savings
            results["date_rated"] = self.building.project.rating_date
        except ObjectDoesNotExist:
            pass
        return results

    def get_utility_costs(self):
        """Get the utility data

        ISSUES:
            - No idea what the cost basis is really on?
            - RR does not capture num of occupants
        """
        results = {}
        try:
            results["utility_cost_monthly"] = "{:.2f}".format(self.results.get_monthly_total_cost())
            results["cost_basis"] = "{:.2f} MMBT".format(self.results.get_monthly_consumption())
        except ObjectDoesNotExist:
            pass
        return results

    def get_energy_audit(self):
        """Energy Audit

        Issues:
            No data..
        """
        return {}

    def get_geea_data(self):
        """This returns a dictionary of data used for the Green Energy Efficiecy Addendum"""
        data = {}
        data.update(self.get_insulation())
        data.update(self.get_water_efficiency())
        data.update(self.get_envelope())
        data.update(self.get_estar_requirements())
        data.update(self.get_day_lighting())
        data.update(self.get_appliances())
        data.update(self.get_hvac())
        data.update(self.get_energy_rating())
        data.update(self.get_indoor_air_quality())
        data.update(self.get_hers_information())
        data.update(self.get_utility_costs())
        data.update(self.get_energy_audit())

        self.add_comment()
        data.update({"comments": self._comments})

        return data
