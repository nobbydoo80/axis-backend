"""geea_data.py: """

from datetime import datetime, date
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfReader
from PyPDF2.generic import NameObject, NumberObject

from axis.annotation.models import Annotation
from axis.checklist.models import Answer
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.models import SolarSystem
from simulation.serializers.results.summary import SimulationSummarySerializer
from simulation.enumerations import (
    InfiltrationUnit,
    MechanicalVentilationType,
    WallCavityInsulationType,
    WaterHeaterStyle,
)
from axis.customer_appraisal_institute.sources.geea_form_fields import (
    all_geea_checkbox_form_fields as checkbox_fields,
)
from axis.customer_appraisal_institute.sources.geea_form_fields import repeating_fields
from axis.core.pypdf import AxisPdfFileReader, AxisPdfFileWriter

__author__ = "Artem Hruzd"
__date__ = "07/12/2019 16:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class GEEAData(object):
    checkbox_true = "\u2611"
    checkbox_false = "\u2610"

    def __init__(self, user, home_status):
        self.user = user
        self.home_status = home_status

        self.simulation = None
        if self.home_status.floorplan and self.home_status.floorplan.remrate_target:
            self.simulation = self.home_status.floorplan.remrate_target

        self.simulation_summary = None
        if self.home_status.floorplan and self.home_status.floorplan.simulation:
            self.simulation_summary = SimulationSummarySerializer(
                self.home_status.floorplan.simulation
            ).data

        self.annotations = Annotation.objects.filter_by_user(self.user).filter(
            object_id__in=list(self.home_status.home.homestatuses.values_list("id", flat=True))
        )
        self.answers = Answer.objects.filter_by_home(self.home_status.home)

    @property
    def data(self):
        data = self.base_information
        data.update(self.energy_label)
        data.update(self.green_certification)
        if self.simulation and self.simulation_summary:
            data.update(self.efficiency_features)
            data.update(self.solar_panels)
            data.update(self.solar_thermal_water_heating_system)

        for key, value in list(data.items()):
            if isinstance(value, bool):
                data[key] = self.checkbox_true if value else self.checkbox_false
            if value is None:
                data.pop(key)
        return data

    @property
    def base_information(self):
        data = {
            "Subject Property": self.home_status.home.get_home_address_display(),
            # 'Client': self.user.get_full_name(),
            # 'Completed By': self.user.get_full_name(),
            # 'Completed Title': 'What is this?',
            # 'Completed Date': datetime.today().strftime('%m/%d/%Y'),
            "City": self.home_status.home.city.name,
            "state": self.home_status.home.city.state,
            "zipcode": self.home_status.home.zipcode,
        }

        data.update(self.footer_information)
        return data

    @property
    def footer_information(self):
        today = datetime.today().strftime("%m/%d/%Y")
        data = {}
        for i in range(1, 5):
            data["ReportCreateDate_" + str(i)] = today
        return data

    @property
    def green_certification(self):
        data = {}
        data.update(self.leed)
        data.update(self.ngbs)
        data.update(self.hers_rating_type)
        data.update(self.energy_star)
        data.update(
            {
                # EPA
                "Indoor airPLUS": self.indoor_airplus,
                "WaterSense": self.water_sense,
                # DOE
                "Zero Energy Ready Home ZERH": self.zero_energy_ready_home,
                # Passive House
                "PHIUS 2015": self.phius_2015,
                "HERS Rating": str(self.hers_rating),
                "Green Certification Verification reviewed on site": True,
                # Do not have
                # 'Living Building Certified': self.living_building_certified,
                # 'Petal Certification': self.petal_certification,
                # 'PHI Low Energy': self.phi_low_energy,
                # 'Enerphit': self.enerphit,
                # 'Passive House': self.passive_house,
            }
        )
        data.update(self.ngbs)
        return data

    @property
    def indoor_airplus(self):
        try:
            self.home_status.home.homestatuses.get(
                eep_program__slug="indoor-airplus-version-1-rev-03"
            )
        except EEPProgramHomeStatus.DoesNotExist:
            pass
        else:
            return True

        try:
            annotation = self.annotations.get(type__slug="indoor-airplus")
        except Annotation.DoesNotExist:
            answers = self.answers.filter(question__question__icontains="nwes 1.4")
            if answers.exists():
                # Multiple answers could come from Sampling
                return "indoor airplus" in answers.last().answer.lower()
        else:
            if "yes" == annotation.content.lower() and annotation.last_update:
                return True
        return False

    @property
    def water_sense(self):
        try:
            self.home_status.home.homestatuses.get(eep_program__slug="watersense-version-12")
        except EEPProgramHomeStatus.DoesNotExist:
            pass
        else:
            return True

        try:
            annotation = self.annotations.get(type__slug="watersense")
        except Annotation.DoesNotExist:
            return False
        else:
            if "yes" == annotation.content.lower() and annotation.last_update:
                return True
        return False

    @property
    def energy_star(self):
        epa_stats = self.home_status.home.homestatuses.filter(eep_program__owner__slug="us-epa")

        aps_stats = self.home_status.home.homestatuses.filter(
            eep_program__owner__slug="aps", eep_program__name__icontains="energy star"
        )

        ncbpa_stats = self.home_status.home.homestatuses.filter(
            eep_program__owner__slug="buildingnc",
            eep_program__name__icontains="energy star",
        ).exclude(eep_program__name__icontains="qa")

        wsu_stats = self.home_status.home.homestatuses.filter(
            eep_program__owner__slug="provider-washington-state-university-extension-ene"
        )

        data = {}
        cert_obj = None
        if epa_stats.count():
            cert_obj = epa_stats

        if aps_stats.count():
            cert_obj = aps_stats

        if ncbpa_stats.count():
            cert_obj = ncbpa_stats

        if wsu_stats.count():
            cert_obj = wsu_stats

        if cert_obj and cert_obj.first().certification_date:
            data.update(
                {
                    "ENERGY STAR": True,
                    "Green Certification Date Verified Day": cert_obj.first().certification_date.strftime(
                        "%d"
                    ),
                    "Green Certification Date Verified Month": cert_obj.first().certification_date.strftime(
                        "%m"
                    ),
                    "Green Certification Date Verified Year": cert_obj.first().certification_date.strftime(
                        "%Y"
                    ),
                    "Green Certification Organization URL": cert_obj.first().eep_program.owner.home_page,
                }
            )
            return data

        try:
            anno = self.annotations.get(type__slug="certified-estar")
        except Annotation.DoesNotExist:
            return {}
        else:
            if "yes" == anno.content.lower() and anno.last_update:
                data.update(
                    {
                        "ENERGY STAR": True,
                        "Green Certification Date Verified Day": anno.last_update.strftime("%d"),
                        "Green Certification Date Verified Month": anno.last_update.strftime("%m"),
                        "Green Certification Date Verified Year": anno.last_update.strftime("%Y"),
                    }
                )
            return data

    @property
    def zero_energy_ready_home(self):
        """Zero Energy Ready Home ZERH"""
        zerh_program_slugs = [
            "doe-zero-energy-ready-rev-05-performance-path",
            "doe-zero-energy-ready-rev-05-prescriptive-pat",
        ]
        doe_stats = self.home_status.home.homestatuses.filter(
            eep_program__slug__in=zerh_program_slugs
        )
        if doe_stats.count():
            return True

        try:
            anno = self.annotations.get(type__slug="certified-doe-zero-ready")
        except Annotation.DoesNotExist:
            return False
        else:
            return "yes" == anno.content.lower()

    @property
    def phius_2015(self):
        try:
            anno = self.annotations.get(type__slug="certified-phius")
        except Annotation.DoesNotExist:
            return False
        else:
            return "yes" == anno.content.lower()

    @property
    def leed(self):
        try:
            # Only check for certified, because the option is LEED Certified.
            self.home_status.home.homestatuses.get(
                eep_program__slug="leed", certification_date__isnull=False
            )
        except EEPProgramHomeStatus.DoesNotExist:
            leed_certified = False
        else:
            leed_certified = True

        try:
            anno = self.annotations.get(type__slug="certified-leed")
        except Annotation.DoesNotExist:
            return {"Leed Certified": leed_certified}
        else:
            leed = anno.content.lower()
            return {
                "LEED Certified": leed_certified,
                "LEED Silver": "silver" == leed,
                "LEED Gold": "gold" == leed,
                "LEED Platinum": "platinum" == leed,
            }

    @property
    def ngbs(self):
        try:
            anno = self.annotations.get(type__slug="certified-nat-gbs")
        except Annotation.DoesNotExist:
            return {}
        else:
            ngbs = anno.content.lower()
            return {
                "NGBS Bronze": "bronze" == ngbs,
                "NGBS Silver": "silver" == ngbs,
                "NGBS Gold": "gold" == ngbs,
                "NGBS Emerald": "emerald" == ngbs,
            }

    # ===========================================================
    @property
    def energy_label(self):
        data = {"HERS Rating": str(self.hers_rating)}
        data.update(self.hers_rating_type)
        data.update(self.hers_estimated_energy_savings)
        # data.update(self.hers_etimated_energy_savings) skipping
        # data.update(self.doe_home_energy_score) don't have currently
        data.update(self.other_energy_score)
        return data

    def _get_hers_rating_home_stat(self):
        """
        Look up EPA, fall back to RESNET, fall back to APS.
        Don't fall back to any program.
        """
        epa_stats = self.home_status.home.homestatuses.filter(
            floorplan__remrate_target__isnull=False, eep_program__owner__slug="us-epa"
        )

        resnet_stats = self.home_status.home.homestatuses.filter(
            floorplan__remrate_target__isnull=False,
            eep_program__owner__slug="eep-resnet",
        )

        aps_stats = self.home_status.home.homestatuses.filter(
            floorplan__remrate_target__isnull=False, eep_program__owner__slug="aps"
        )

        ncbpa_stats = self.home_status.home.homestatuses.filter(
            floorplan__remrate_target__isnull=False,
            eep_program__owner__slug="buildingnc",
        ).exclude(eep_program__name__icontains="qa")

        wsu_stats = self.home_status.home.homestatuses.filter(
            eep_program__owner__slug="provider-washington-state-university-extension-ene"
        )

        if epa_stats.count():
            return epa_stats.first()
        elif resnet_stats.count():
            return resnet_stats.first()
        elif aps_stats.count():
            return aps_stats.first()
        elif ncbpa_stats.count():
            return ncbpa_stats.first()
        elif wsu_stats.count():
            return wsu_stats.first()
        else:
            return None

    @property
    def hers_rating(self):
        stat = self._get_hers_rating_home_stat()
        if stat:
            return stat.floorplan.get_hers_score_for_program(stat.eep_program)
        return "N/A"

    @property
    def hers_rating_type(self):
        """Pulled from ``axis.resnet.RESNET.data.RESNETDataBase.get_ratint_type``"""
        stat = self._get_hers_rating_home_stat()
        if not stat:
            return {}

        sampled = False
        projected = False
        confirmed = False

        if stat.certification_date:
            if stat.sampleset_set.exists():
                sampled = True
            else:
                confirmed = True
        else:
            projected = True

        return {
            "Sampling Rating": sampled,
            "Projected Rating": projected,
            "Confirmed Rating": confirmed,
            "Energy Label Organization URL RESNET": True,
            "Energy Label Verification reviewed on site": True,
        }

    @property
    def hers_estimated_energy_savings(self):
        stat = self._get_hers_rating_home_stat()
        if not stat or not stat.certification_date:
            return {}

        cert_date = stat.certification_date
        month = cert_date.strftime("%m")
        day = cert_date.strftime("%d")
        year = cert_date.strftime("%Y")

        energy_savings_per_year = self.simulation_summary["energy_cost_str"]
        energy_savings_per_kwh = self.simulation_summary["energy_consumption_str"]
        return {
            "HERS rate dated Month": month,
            "HERS rate dated Day": day,
            "HERS rate dated Year": year,
            "Energy Label Date Verified Month": month,
            "Energy Label Date Verified Day": day,
            "Energy Label Date Verified Year": year,
            "HERS Estimated energy savings per year": energy_savings_per_year,
            "HERS Estimated energy savings per kwh": energy_savings_per_kwh,
        }

    @property
    def other_energy_score(self):
        # from axis.customer_eto.fasttrack import get_calculation_data
        # calc_data = get_calculation_data(self.home_status)
        # try:
        #     eps_score = calc_data['eps_score']
        # except KeyError:
        #     eps_score = calc_data['result']['eps_score']
        # return {
        #     'Other Energy Score Range Start': '0',
        #     'Other Energy Score Range End': '',
        #     'Other Energy Score': eps_score,
        # }
        return {}

    # ===========================================================
    @property
    def efficiency_features(self):
        data = {}
        data.update(self.insulation)
        data.update(self.building_envelope)
        # data.update(self.windows)
        data.update(self.day_lighting)
        data.update(self.appliances)
        data.update(self.water_heater)
        data.update(self.hvac_related_equipment)
        data.update(self.indoor_environmental_quality)
        data.update(self.utility_costs)
        return data

    @property
    def insulation(self):
        """
        Partly lifted from .models.GEEAData.get_insulation.

        Assumptions:
            RValue exists if RValue Wall or RValue Ceiling
            Wall RValue
            Ceiling RValue
        """

        wall_r_value, ceiling_r_value = None, None
        wall_r_value_check = False
        if self.simulation_summary:
            wall_r_value = self.simulation_summary["wall_r_value_str"]
            ceiling_r_value = self.simulation_summary["ceiling_r_value_str"]

        if wall_r_value:
            wall_r_value_check = True

        insulation_types = self.simulation_summary["insulation_types"]

        return {
            # 'Fiberglass BlownIn': False,
            "Foam Insulation": WallCavityInsulationType.SPRAY_FOAM in insulation_types,
            "Cellulose": WallCavityInsulationType.CELLULOSE in insulation_types,
            "Fiberglass Batt Insulation": WallCavityInsulationType.BATT in insulation_types,
            "RValue": bool(wall_r_value or ceiling_r_value),
            "RValue Wall": wall_r_value,
            "RValue Ceiling": ceiling_r_value,
            "RValue Wall Check": wall_r_value_check,
        }

    @property
    def building_envelope(self):
        """
        Partly lifted from .models.GEEADATA.get_envelope
        """
        # cfm25 = cfm50 = ach50 = ach_natural = None
        units_map = {
            InfiltrationUnit.CFM50: "CFM50",
            InfiltrationUnit.CFM25: "CFM25",
            InfiltrationUnit.ACH50: "ACH50",
            InfiltrationUnit.NATURAL: "ACH NATURAL",
        }

        output = {
            # Possible keys
            # 'Envelope Tightness': None,
            # 'CFM25': False,
            # 'CFM25 Value': None,
            # 'CFM50': False,
            # 'CFM50 Value': None,
            # 'ACH50': False,
            # 'ACH50 Value': None,
            # 'ACH Natural': False,
            # 'ACH Natural Value': None
        }

        try:
            infiltration = self.simulation_summary["infiltration"]
        except KeyError:
            pass
        else:
            if infiltration and infiltration["infiltration_unit"] in units_map:
                unit_type = units_map[infiltration["infiltration_unit"]]
                output[unit_type] = True
                output["{} Value".format(unit_type)] = infiltration["infiltration_value_str"]
                output["Envelope Tightness"] = infiltration["envelope_tightness"]

        return output

    @property
    def windows(self):
        return {
            # 'Windows ENERGY STAR': False,
            # 'Windows Low E': False,
            # 'Windows High Impact': False,
            # 'Windows Storm': False,
            # 'Windows Double Pane': False,
            # 'Windows Triple Pane': False,
            # 'Windows Tinted': False,
            # 'Windows Solar Shades': False,
        }

    @property
    def day_lighting(self):
        return {
            "Num of Skylights": self.simulation_summary["skylight_count_str"],
            # 'Num of Solar Tubes': None,
            # 'Day Lighting Other': None,
            # 'Day Lighting LEDS': None
        }

    @property
    def appliances(self):
        """
        Partly lifted from .models.GEEAData.get_appliances
        """
        dishwashers = False
        refrigerators = False
        washer_dryer = False

        energy_star_dishwasher_question_slugs = [
            "manhes-629-energy-star-dishwasher-in-unit",
            "estar_dishwasher_installed",
            "eto-estar_dishwasher",
        ]
        energy_star_diswashers = self.answers.filter(
            question__slug__in=energy_star_dishwasher_question_slugs
        )
        if energy_star_diswashers.exists():
            dishwashers = energy_star_diswashers.last().answer.lower() == "yes"

        energy_star_appliances_question_slugs = [
            "lighting-appliances-all-installed-refrigerators",
            "lighting-appliances-all-installed-refrigerators-0",
        ]
        appliances = self.answers.filter(question__slug__in=energy_star_appliances_question_slugs)
        if appliances.exists():
            if appliances.last().answer.lower() == "yes":
                dishwashers = True
                refrigerators = True

        washer_dryer = self.simulation_summary["washer_energy_star_eligible"]
        return {
            "Appliances ENERGY STAR Dishwasher": dishwashers,
            "Appliances ENERGY STAR Refrigerator": refrigerators,
            "Appliances ENERGY STAR WasherDryer": washer_dryer,
            # 'Appliances ENERGY STAR Other': None,
            # 'Appliances ENERGY STAR Other Value': None,
            # 'Appliances Source Propane': None,
            # 'Appliances Source Electric': None,
            # 'Appliances Source Natural Gas': None,
            # 'Appliances Source Other': None,
            # 'Appliances Source Other Value': None,
        }

    @property
    def water_heater(self):
        output = {
            # 'Water Heater ENERGY STAR': None,
            # 'Water Heater Size': None,
            # 'Water Heater Tankless': None,
            # 'Water Heater Solar': None,
            # 'Water Heater Heat Pump': None,
            # 'Water Heater Coil': None,
        }

        key_map = {
            WaterHeaterStyle.CONVENTIONAL: "Coil",
            WaterHeaterStyle.TANKLESS: "Tankless",
            WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP: "Heat " "Pump",
        }

        output["Water Heater Size"] = self.simulation_summary["total_water_heater_size"]
        for wh_type in self.simulation_summary["water_heater_types"]:
            if wh_type == WaterHeaterStyle.TANKLESS:
                output["Water Heater Tankless"] = True
            try:
                key = "Water Heater {}".format(key_map[wh_type])
            except KeyError:
                pass
            else:
                output[key] = True

        # Simulation 15240 has two solarsystems
        # We don't have solar systems in new simulation models.
        # try:
        #     if self.simulation.solarsystem.type in [1, 2]:
        #         output['Water Heater Solar'] = True
        # except SolarSystem.DoesNotExist:
        #     pass

        return output

    @property
    def hvac_related_equipment(self):
        """
        If home has AC and Gas Furnace fill out High Efficiency HVAC
        If home has Heat Pump fill out Heat Pump Efficiency Rating

        Heat Pump [heating cooling]
            AirSource [HSPF SEER]
            GroundSource [COP EER]

        """
        output = {
            # 'High Efficiency HVAC': None,
            # 'High Efficiency HVAC SEER': None,
            # 'High Efficiency HVAC Efficiency Rating': None,
            # 'High Efficiency HVAC AFUE': None,
            # 'Heat Pump Efficiency Rating': None,
            # 'Heat Pump Efficiency Rating COP': None,
            # 'Heat Pump Efficiency Rating HSPF': None,
            # 'Heat Pump Efficiency Rating SEER': None,
            # 'Heat Pump Efficiency Rating EER': None,
            # 'Thermostat Controllers': None,
            # 'Programmable Thermostat': None,
            # 'Auxiliary heat source': None,
            # 'Radiant Floor Heat': None,
            # 'Geothermal': None,
            # 'Electric Vehicle Ready': None
            "Thermostat Controllers Absent": True,
            "Programmable Thermostat Absent": True,
            "Auxiliary heat source Absent": True,
            "Radiant Floor Heat Absent": True,
            "Geothermal Absent": True,
            "Electric Vehicle Ready Absent": True,
        }

        if self.simulation_summary["heater_efficiency"]:
            output["High Efficiency HVAC"] = self.simulation_summary["heater_hvac"]
            output["High Efficiency HVAC AFUE"] = self.simulation_summary["heater_efficiency_str"]

        if self.simulation_summary["ashp_heating_efficiency"]:
            output["Heat Pump Efficiency Rating"] = True
            output["Heat Pump Efficiency Rating HSPF"] = self.simulation_summary[
                "ashp_heating_efficiency_str"
            ]
            output["Heat Pump Efficiency Rating SEER"] = self.simulation_summary[
                "ashp_cooling_efficiency_str"
            ]

        if self.simulation_summary["ground_source_heat_pump"]:
            output["Heat Pump Efficiency Rating"] = True
            output["Heat Pump Efficiency Rating COP"] = self.simulation_summary[
                "gshp_efficiency_rating_cop"
            ]
            output["Heat Pump Efficiency Rating EER"] = self.simulation_summary[
                "gshp_efficiency_rating_eer"
            ]

        if self.simulation_summary["thermostat_controllers"]:
            output["Thermostat Controllers"] = self.simulation_summary["thermostat_controllers"]
            output["Programmable Thermostat"] = self.simulation_summary["programmable_thermostat"]
            output["Thermostat Controllers Absent"] = False
            output["Programmable Thermostat Absent"] = False

        return output

    @property
    def indoor_environmental_quality(self):
        """
        Couldn't find anything in Axis related to these keys.
        """
        output = {
            "Indoor Environmental Quality ERV or HRV": False,
            "Indoor Environmental Quality Other": False,
            # 'Indoor Environmental Quality Humudity Monitoring'
            # 'Non Toxic Pest Control'
            # 'Radon System'
            # 'Radon System Active'
            # 'Radon System Passive'
        }

        try:
            infiltration = self.simulation_summary["mechanical_ventilation_systems"][0]
        except (IndexError, KeyError):
            pass
        else:
            # Make sure type is not None
            if infiltration["type"]:
                if (
                    infiltration["type"] == MechanicalVentilationType.ERV
                    or infiltration["type"] == MechanicalVentilationType.HRV
                ):
                    output["Indoor Environmental Quality ERV or HRV"] = True
                else:
                    output["Indoor Environmental Quality Other"] = True

        return output

    @property
    def water_efficiency(self):
        """
        According to .models.GEEAData.get_appliances
        REM doesn't collect Reclaimed water data or information about
        Cisterns
        """
        return {
            # 'Reclaimed Water System'
            # 'Reclaimed Water System Describe'
            # 'Greywater reuse system'
            # 'Water Saving Fixtures'
            # 'Rain Barrels Used in Irrigration'
            # 'Cistern Size'
            # 'Locatino of cistern'
        }

    @property
    def utility_costs(self):
        # FIXME: How do we determine the Dates that the Costs were taken from?
        # As per Bob - we use current calendar year.
        year = str(date.today().year)
        return {
            "Utility Costs per year": self.simulation_summary["energy_cost_str"],
            "Utility Costs Start Month": "01",
            "Utility Costs Start Day": "01",
            "Utility Costs Start Year": year,
            "Utility Costs End Month": "12",
            "Utility Costs End Day": "31",
            "Utility Costs End Year": year,
        }

    @property
    def solar_panels(self):
        data = {
            # 'Array 1 System Size': panel.peak_power / 1000,
            # 'Array 1 Energy Production': fuel_summary.photo_voltaics_consumption * -1,
            # 'Array 1 Tilt Slope': panel.tilt,
            # 'Array 1 Azimuth': panel.get_orientation_display()
        }
        # FIXME: What is peak_power in simulaiton.models.photovoltaic ?
        # data['Array 1 System Size'] = panel.peak_power / 1000
        try:
            data["Array 1 Tilt Slope"] = self.simulation_summary["solar_panel_tilt_str"]
            data["Array 1 Azimuth"] = self.simulation_summary["solar_panel_azimuth_str"]
            data["Array 1 Energy Production"] = self.simulation_summary["solar_panel_capacity_str"]
        except KeyError:
            pass

        return data

    @property
    def solar_thermal_water_heating_system(self):
        # FIXME: How to get solar water heating system in new simulation models?
        try:
            solar = self.simulation.solarsystem
        except SolarSystem.DoesNotExist:
            return {}
        except SolarSystem.MultipleObjectsReturned:
            return {}
        else:
            if solar.type in [1, 4]:
                data = {"Storage Tank Size": solar.storage_volume}

                collector_spec = solar.get_specs_display().lower()
                if "flat black" in collector_spec:
                    data["Collector Type Flat-Plat"] = True
                elif "evacuated tube" in collector_spec:
                    data["Collector Type Evacuated-Tube Solar"] = True

                collector_loop_type = solar.get_collector_loop_type_display().lower()
                if "direct" in collector_loop_type:
                    data["Type of System Active Direct"] = True
                elif "indirect" in collector_loop_type:
                    data["Type of System Active Indirect"] = True

                return data

        return {}


def flatten_filled_values_in_pdf(pdf_form, data):
    # Make sure we have defaults setup for 'check' boxes.
    for field in checkbox_fields:
        if field not in data.keys():
            data[field] = "\u2610"

    # PyPDF2 doesn't work well with multiple fields with same name.
    for field in repeating_fields:
        if field in data.keys():
            for i in range(1, 6):
                additional_field = field + "_" + str(i)
                data[additional_field] = data[field]

    # log.debug(data)

    with io.open(pdf_form, "rb") as input_stream:
        packet = io.BytesIO()
        # New PDF to overlay custom text
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 7)
        can.drawCentredString(
            x=2.5 * inch, y=13.42 * inch, text="{}".format(data["Subject Property_3"])
        )

        # Disclaimer
        can.setFont("Helvetica", 6)
        can.drawCentredString(
            x=3.25 * inch, y=0.75 * inch, text="{}".format(data["ReportCreateDate_3"])
        )

        can.save()
        packet.seek(0)
        overt_pdf = PdfReader(packet)

        pdf_reader = AxisPdfFileReader(input_stream, strict=False)

        for i in (2, 3, 4):
            page = pdf_reader.pages[i]
            page.merge_page(overt_pdf.pages[0])

        pdf_writer = AxisPdfFileWriter()
        num_pages = len(pdf_reader.pages)

        for i in range(num_pages):
            pdf_writer.add_page(pdf_reader.pages[i])
            if i < num_pages - 1:
                page = pdf_writer.pages[i]
                pdf_writer.updatePageFormFieldValues(page, data)

        for i in range(num_pages - 1):
            page = pdf_writer.pages[i]
            for j in range(0, len(page["/Annots"])):
                writer_annot = page["/Annots"][j].get_object()
                for field in data:
                    if writer_annot.get("/T") == field:
                        writer_annot.update({NameObject("/Ff"): NumberObject(1)})

        output_stream = pdf_writer.get_pdf_stream()

    return output_stream
