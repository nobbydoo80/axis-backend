import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.views.generic import FormView
from django.shortcuts import get_object_or_404

from axis.core.utils import fill_flatten_ea_pdf_template
from axis.core.models import User
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.models import Simulation as RemSimulation
from .config import AppraisalAddendumConfig as config
from . import forms

__author__ = "Michael Jeffrey"
__date__ = "8/9/17 2:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class HighPerformanceHomeAddendumView(LoginRequiredMixin, FormView):
    form_class = forms.HighPerformanceHomeAddendumForm

    def get(self, request, *args, **kwargs):
        if "home_status" not in kwargs:
            raise Http404()

        home_status = get_object_or_404(EEPProgramHomeStatus, id=kwargs["home_status"])
        return self.generate_report(home_status)

    def generate_report(self, home_status):
        data = HPHData(self.request.user, home_status).data
        attachment_name = "High_Performance_Home_Addendum_{}.pdf".format(
            home_status.home.street_line1
        )
        pdf_stream = fill_flatten_ea_pdf_template(config.FORM_FIELD_TEMPLATE, data)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename={}".format(attachment_name)
        response.write(pdf_stream.getvalue())

        return response


class HPHData(object):
    def __init__(self, user: User, home_status: EEPProgramHomeStatus):
        self.user = user
        self.home_status = home_status
        self.rem_simulation: RemSimulation = self.home_status.floorplan.remrate_target

    @property
    def data(self):
        data = {}
        data.update(self.page_one)
        data.update(self.page_two)
        data.update(self.page_three)
        return data

    @property
    def page_one(self):
        data = {}
        data.update(self.property_info)
        data.update(self.representative)
        data.update(self.performance_label)
        data.update(self.certification_information)
        return data

    @property
    def property_info(self):
        return {
            "Property Address": self.home_status.home.get_home_address_display(
                include_city_state_zip=True, include_lot_number=True, company=self.user.company
            ),
        }

    @property
    def representative(self):
        """We can't be sure about what makes someone a 'Representative Type'."""
        return {"Representative Type": None}

    @property
    def performance_label(self):
        if self.home_status.eep_program.slug not in [
            "eto",
            "eto-2016",
            "eto-2017",
            "eto-2018",
            "eto-2019",
            "eto-2020",
            "eto-2021",
            "eto-2022",
            "eto-fire-2021",
        ]:
            return {}

        try:
            fastrack = self.home_status.fasttracksubmission

        except (ObjectDoesNotExist, AttributeError):
            return {}

        if fastrack.eps_score is None or fastrack.similar_size_eps_score is None:
            return {}

        cert_date = self.home_status.certification_date
        label_date = cert_date and cert_date.strftime("%m/%d/%Y")

        return {
            "Performance Label": "EPS",
            "Performance Label Score": round(fastrack.eps_score),
            # estimated_monthly_energy_costs other option
            "Estimated Energy Costs": "${:.2f}".format(fastrack.estimated_annual_energy_costs),
            "Estimated Energy Costs Term": "Annual",
            "Performance Label Date": label_date,
            "Benchmark": "Same size built to code (EPS)",
            "Benchmark Score": round(fastrack.similar_size_eps_score, 0),
        }

    @property
    def certification_information(self):
        from axis.annotation.models import Annotation

        try:
            anno = Annotation.objects.get(
                type__slug="earth-advantage-certification-level", object_id=self.home_status.home.id
            )
        except Annotation.DoesNotExist:
            # These are all Non QA Energy Star programs from NEEA and US EPA.
            energy_star_program_ids = [65, 66, 67, 68, 21, 16, 30, 31]
            certified_home_stats = self.home_status.home.homestatuses.filter(
                eep_program__id__in=energy_star_program_ids, certification_date__isnull=False
            ).order_by("certification_date")

            try:
                home_stat = certified_home_stats[0]
            except IndexError:
                # There's nothing we can do here
                return {}
            else:
                return {
                    "Certification": home_stat.eep_program.name,
                    "Year": home_stat.certification_date.strftime("%Y"),
                }
        else:
            return {
                "Certification": "Earth Advantage Certified home",
                "Level": anno.content,
                "Year": anno.created_on.strftime("%Y"),
            }

    @property
    def page_two(self):
        data = {}
        data.update(self.heating_cooling)
        data.update(self.appliances)
        data.update(self.air_quality)
        return data

    @property
    def heating_cooling(self):
        # Option1 : Most load served solo
        # Option2 : Most load served of matching efficiency and unit type
        equipment = self.rem_simulation.installedequipment_set

        def get_air_conditioner():
            filters = {"system_type": 2, "air_conditioner__isnull": False}
            order_by = "-air_conditioner_load_served_pct"
            air_conditioning = equipment.filter(**filters).order_by(order_by).first()

            if air_conditioning:
                air_conditioning = air_conditioning.air_conditioner
                return "{} {}".format(
                    round(air_conditioning.efficiency, 1),
                    air_conditioning.get_efficiency_unit_display(),
                )

        def get_furnace():
            filters = {"system_type": 1, "heater__isnull": False, "heater__type": 1}
            order_by = "-heating_load_served_pct"
            furnace = equipment.filter(**filters).order_by(order_by).first()

            if furnace:
                furnace = furnace.heater
                return "{} {}".format(
                    round(furnace.efficiency, 1), furnace.get_efficiency_unit_display()
                )

        def get_heat_pump():
            """Electric Only"""
            filters = {"air_source_heat_pump__isnull": False, "air_source_heat_pump__fuel_type": 4}
            heat_pump = equipment.filter(**filters).first()

            if heat_pump:
                heat_pump = heat_pump.air_source_heat_pump
                return "{} {}, {} {}".format(
                    round(heat_pump.heating_efficiency, 1),
                    heat_pump.get_heating_efficiency_units_display(),
                    round(heat_pump.cooling_efficiency, 1),
                    heat_pump.get_cooling_efficiency_units_display(),
                )

        def get_secondary_heat_pump():
            filters = {"ground_source_heat_pump__isnull": False}
            secondary_heat_pump = equipment.filter(**filters).first()

            if secondary_heat_pump:
                secondary_heat_pump = secondary_heat_pump.ground_source_heat_pump
                return "{} EER, {} COP".format(
                    round(secondary_heat_pump.cooling_energy_efficiency_ratio_70f, 1),
                    round(secondary_heat_pump.heating_coefficient_of_performance_50f, 1),
                )

        def get_heating_system():
            filters = {"integrated_space_water_heater__isnull": False}
            heating_system = equipment.filter(**filters).first()

            if heating_system:
                heating_system = heating_system.integrated_space_water_heater
                return "Turbonic" if "air" in heating_system.distribution_type.lower() else None

        air_conditioner = get_air_conditioner()
        furnace = get_furnace()
        heat_pump = get_heat_pump()
        secondary_heat_pump = get_secondary_heat_pump()
        heating_system = get_heating_system()

        data = {
            "Air Conditioning Efficiency": air_conditioner,
            "Furnace Efficiency": furnace,
            "Heat Pump Efficiency": heat_pump,
            # 'Ductless Heat Pump System Efficiency': 'thirty five',  skipping for now
            "Secondary Heat Pump Type": None,
            # 'Secondary Heat Pump Type': ['Geothermal', 'Water Source'], don't think we can set in REMRATE
            "Secondary Heat Pump Efficiency": secondary_heat_pump,
            "Heating System": heating_system,
        }

        return {k: v for k, v in data.items() if v is not None}

    @property
    def appliances(self):
        data = {}

        tankless_water_heater = self.rem_simulation.hotwaterheater_set.filter(
            type=3
        ).first()  # Instance Water Heater
        if tankless_water_heater:
            data["Tankless Water Heater Efficiency"] = "{} EF".format(
                tankless_water_heater.energy_factor
            )

        conventional_water_heater = self.rem_simulation.hotwaterheater_set.filter(
            type=1
        ).first()  # Conventional1
        if conventional_water_heater:
            data["Water Heater Efficiency"] = "{} EF".format(
                conventional_water_heater.energy_factor
            )

        return data

    @property
    def air_quality(self):
        return {
            "Mechanical Ventilation Type": self.rem_simulation.infiltration.get_mechanical_vent_type_display()
        }

    @property
    def page_three(self):
        data = {}
        data.update(self.solar)
        return data

    @property
    def solar(self):
        data = {}

        # fuel_units 1 KWH
        # All consumption provided in negative floats
        fuel_summary = self.rem_simulation.fuelsummary_set.filter(
            fuel_units=1, photo_voltaics_consumption__lt=0
        ).first()
        if fuel_summary:
            annual_production = fuel_summary.photo_voltaics_consumption * -1
            data["Est Annual Production"] = "{:,.0f}".format(annual_production)

        tank_size = getattr(self.rem_simulation.solarsystem, "storage_volume", None)
        if tank_size:
            data["Storage Tank Size"] = tank_size

        data["Array location"] = None
        data["Array Ownership"] = None
        data["Solar Thermal Type"] = None
        data["Solar Thermal Backup System"] = None
        data["Solar Thermal Backup System Fuel"] = None

        return {k: v for k, v in data.items() if v is not None}
