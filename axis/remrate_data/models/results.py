"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from .simulation import Simulation, DESIGN_MODELS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Results(models.Model):
    """Results - Results"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    heating_system_efficiency = models.FloatField(
        db_column="FHTEFF", verbose_name="Heating system efficiency."
    )
    cooling_system_efficiency = models.FloatField(
        db_column="FCLGEFF", verbose_name="Cooling system efficiency."
    )
    hot_water_system_efficiency = models.FloatField(
        db_column="FHWEFF", verbose_name="Hot Water system efficiency"
    )
    roof_heating_load = models.FloatField(
        db_column="FLHROOF", verbose_name="Roof heating component load"
    )
    roof_cooling_load = models.FloatField(
        db_column="FLCROOF", verbose_name="Roof cooling component load"
    )
    joist_heating_load = models.FloatField(
        db_column="FLHJOIST", verbose_name="Joist heating component load"
    )
    joist_cooling_load = models.FloatField(
        db_column="FLCJOIST", verbose_name="Joist cooling component load"
    )
    above_ground_walls_heating_load = models.FloatField(
        db_column="FLHAGWALL", verbose_name="Above Grade Wall heating component load"
    )
    above_ground_walls_cooling_load = models.FloatField(
        db_column="FLCAGWALL", verbose_name="Above Grade Wall cooling component load"
    )
    foundation_wall_heating_load = models.FloatField(
        db_column="FLHFNDWALL", verbose_name="Foundation Wall heating component load"
    )
    foundation_wall_cooling_load = models.FloatField(
        db_column="FLCFNDWALL", verbose_name="Foundation Wall cooling component load"
    )
    windows_skylights_heating_load = models.FloatField(
        db_column="FLHWNDOSK", verbose_name="Windows/Skylight heating component load"
    )
    windows_skylights_cooling_load = models.FloatField(
        db_column="FLCWNDOSK", verbose_name="Windows/Skylight cooling component load"
    )
    frame_floor_heating_load = models.FloatField(
        db_column="FLHFFLR", verbose_name="Frame Floor heating component load"
    )
    frame_floor_cooling_load = models.FloatField(
        db_column="FLCFFLR", verbose_name="Frame Floor cooling component load"
    )
    crawl_heating_load = models.FloatField(
        db_column="FLHCRAWL", verbose_name="Crawl heating component load"
    )
    crawl_cooling_load = models.FloatField(
        db_column="FLCCRAWL", verbose_name="Crawl cooling component load"
    )
    slab_heating_load = models.FloatField(
        db_column="FLHSLAB", verbose_name="Slab heating component load"
    )
    slab_cooling_load = models.FloatField(
        db_column="FLCSLAB", verbose_name="Slab cooling component load"
    )
    infiltration_heating_load = models.FloatField(
        db_column="FLHINF", verbose_name="Infiltration heating component load"
    )
    infiltration_cooling_load = models.FloatField(
        db_column="FLCINF", verbose_name="Infiltration cooling component load"
    )
    mechanical_ventilation_heating_load = models.FloatField(
        db_column="FLHMECHVNT", verbose_name="Mechanical ventilation heating component load"
    )
    mechanical_ventilation_cooling_load = models.FloatField(
        db_column="FLCMECHVNT", verbose_name="Mechanical ventilation cooling component load"
    )
    duct_heating_load = models.FloatField(
        db_column="FLHDUCT", verbose_name="Duct heating component load"
    )
    duct_cooling_load = models.FloatField(
        db_column="FLCDUCT", verbose_name="Duct cooling component load"
    )
    active_solar_heating_load = models.FloatField(
        db_column="FLHASOL", verbose_name="Active Solar heating component load"
    )
    active_solar_cooling_load = models.FloatField(
        db_column="FLCASOL", verbose_name="Active Solar cooling component load"
    )
    sunspace_heating_load = models.FloatField(
        db_column="FLHSS", verbose_name="Sunspace heating component load"
    )
    sunspace_cooling_load = models.FloatField(
        db_column="FLCSS", verbose_name="Sunspace cooling component load"
    )
    internal_gains_heating_load = models.FloatField(
        db_column="FLHIGAIN", verbose_name="Internal gains heating component load"
    )
    internal_gains_cooling_load = models.FloatField(
        db_column="FLCIGAIN", verbose_name="Internal gains cooling component load"
    )
    whole_house_fan_heating_load = models.FloatField(
        db_column="FLHWHF", verbose_name="Whole house fan heating component load"
    )
    whole_house_fan_cooling_load = models.FloatField(
        db_column="FLCWHF", verbose_name="Whole house fan cooling component load"
    )
    door_heating_load = models.FloatField(
        db_column="FLHDOOR", verbose_name="Door heating component load"
    )
    door_cooling_load = models.FloatField(
        db_column="FLCDOOR", verbose_name="Door cooling component load"
    )
    total_heating_load = models.FloatField(db_column="FLHTOTAL", verbose_name="Total heating load")
    total_cooling_load = models.FloatField(db_column="FLCTOTAL", verbose_name="Total cooling load")
    hot_water_heating_consumption = models.FloatField(
        db_column="FTOTDHW", verbose_name="Total domestic hot water heating consumption"
    )
    hot_water_heating_consumption_no_loss = models.FloatField(
        db_column="fDHWNoLoss",
        null=True,
        blank=True,
        verbose_name="Total domestic hot water heating load w/out tank loss",
    )
    solar_savings = models.FloatField(
        db_column="FSOLSAVE", verbose_name="Savings due to active solar system"
    )
    heating_design_load = models.FloatField(db_column="FHTPEAK", verbose_name="Heating design load")
    calculated_sensible_cooling_load = models.FloatField(
        db_column="FACSPEAK", verbose_name="Calculated sensible cooling design load"
    )
    calculated_latent_cooling_load = models.FloatField(
        db_column="FACLPEAK", verbose_name="Calculated latent cooling design load"
    )
    calculated_sensible_latent_cooling_load = models.FloatField(
        db_column="FACTPEAK", verbose_name="Calculated sensible + latent cooling design load"
    )
    unit_heating_cost = models.FloatField(
        db_column="FHBUCK", verbose_name="Unit Heating Cost $/MBtu"
    )
    unit_cooling_cost = models.FloatField(
        db_column="FACBUCK", verbose_name="Unit cooling Cost $/MBtu"
    )
    unit_hot_water_cost = models.FloatField(db_column="FWBUCK", verbose_name="Unit DHW Cost $/MBtu")
    heating_consumption = models.FloatField(
        db_column="FHCONS", verbose_name="Annual Energy Consumption Heating (MBtu)"
    )
    cooling_consumption = models.FloatField(
        db_column="FCCONS", verbose_name="Annual Energy Consumption Cooling (MBtu)"
    )
    heating_cost = models.FloatField(db_column="FHCOST", verbose_name="Annual Energy Cost Heating")
    cooling_cost = models.FloatField(db_column="FCCOST", verbose_name="Annual Energy Cost Cooling")
    hot_water_consumption = models.FloatField(
        db_column="FWCONS", verbose_name="Annual Energy Consumption Water Heating (MBtu)"
    )
    hot_water_cost = models.FloatField(
        db_column="FWCOST", verbose_name="Annual Energy Cost Water Heating"
    )
    service_cost = models.FloatField(
        db_column="FSERVCOST", verbose_name="Annual Energy Cost Service Charges"
    )
    total_cost = models.FloatField(db_column="FTOTCOST", verbose_name="Annual Energy Cost Total")
    refrigerator_consumption = models.FloatField(
        db_column="FREFRCONS", verbose_name="Refrigerator consumption"
    )
    freezer_consumption = models.FloatField(
        db_column="FFRZCONS", verbose_name="Freezer consumption"
    )
    dryer_consumption = models.FloatField(db_column="FDRYCONS", verbose_name="Dryer consumption")
    oven_consumption = models.FloatField(db_column="FOVENCONS", verbose_name="Oven consumption")
    lights_and_appliances_consumption = models.FloatField(
        db_column="FLAOTHCONS", verbose_name="Light And Appliances Other consumption"
    )
    lights_hs_consumption = models.FloatField(
        db_column="FLIHSCONS", verbose_name="Light Hs consumption"
    )
    lights_cs_consumption = models.FloatField(
        db_column="FLICSCONS", verbose_name="Light Cs consumption"
    )
    refrigerator_cost = models.FloatField(db_column="FREFRCOST", verbose_name="Refrigerator cost")
    freezer_cost = models.FloatField(db_column="FFRZCOST", verbose_name="Freezer cost")
    dryer_cost = models.FloatField(db_column="FDRYCOST", verbose_name="Dryer Cost")
    oven_cost = models.FloatField(db_column="FOVENCOST", verbose_name="Oven Cost")
    lights_and_appliances_cost = models.FloatField(
        db_column="FLAOTHCOST", verbose_name="Light And Appliances Other cost"
    )
    lighting_cost = models.FloatField(db_column="FLIGHTCOST", verbose_name="Lighting cost")
    lights_and_appliances_total_consumption = models.FloatField(
        db_column="FLATOTCONS", verbose_name="Light And Appliances Total consumption"
    )
    lights_and_appliances_total_cost = models.FloatField(
        db_column="FLATOTCOST", verbose_name="Annual Energy Cost Lights & Appliances"
    )
    photo_voltaic_consumption = models.FloatField(
        db_column="FPVTOTCONS", verbose_name="Annual Energy Consumption Total Photovoltaics (MBtu)"
    )
    photo_voltaic_cost = models.FloatField(
        db_column="FPVTOTCOST", verbose_name="Annual Energy Cost Photovoltaics"
    )
    shell_area = models.FloatField(db_column="FSHELLAREA", verbose_name="Shell Area")
    heating_load_per_shell_area_hdd75 = models.FloatField(
        db_column="FHTGLDPHDD", verbose_name="Heating Load per shell area per HDD65"
    )
    cooling_load_per_shell_area_cdd74 = models.FloatField(
        db_column="FCLGLDPHDD", verbose_name="Cooling Load per shell area per CDD74"
    )
    heating_design_load_per_shell_area_hdd75 = models.FloatField(
        db_column="FHTGDDPHDD", verbose_name="Heating Design Load per shell area per HDD65"
    )
    cooling_design_load_per_shell_area_cdd74 = models.FloatField(
        db_column="FCLGDDPHDD", verbose_name="Cooling Design Load per shell area per CDD74"
    )
    heating_natural_ach = models.FloatField(
        db_column="FHTGACH", verbose_name="Heating Natural ACH, calculated from user inputs"
    )
    cooling_natural_ach = models.FloatField(
        db_column="FCLGACH", verbose_name="Cooling Natural ACH, calculated from user inputs"
    )
    rating_number = models.CharField(
        db_column="SRATENO", null=True, max_length=93, blank=True, verbose_name="Rating Number"
    )
    co2_total_emission = models.FloatField(
        db_column="FEMCO2TOT", verbose_name="Emission - Carbon Dioxide Total"
    )
    s02_total_emission = models.FloatField(
        db_column="FEMSO2TOT", verbose_name="Emission - Sulfur Dioxide Total"
    )
    nox_total_emission = models.FloatField(
        db_column="FEMNOXTOT", verbose_name="Emission - Nitrogen Oxides Total"
    )
    co2_heating_emission = models.FloatField(
        db_column="FEMCO2HTG", verbose_name="Emission - Carbon Dioxide Heating"
    )
    co2_cooling_emission = models.FloatField(
        db_column="FEMCO2CLG", verbose_name="Emission - Carbon Dioxide Cooling"
    )
    co2_hot_water_emission = models.FloatField(
        db_column="FEMCO2DHW", verbose_name="Emission - Carbon Dioxide Water Heating"
    )
    co2_lights_appliance_emission = models.FloatField(
        db_column="FEMCO2LA", verbose_name="Emission - Carbon Dioxide Lights and Appliances"
    )
    co2_photo_voltaic_emission = models.FloatField(
        db_column="FEMCO2PV", verbose_name="Emission - Carbon Dioxide Photovoltaics"
    )
    so2_heating_emission = models.FloatField(
        db_column="FEMSO2HTG", verbose_name="Emission - Sulfur Dioxide Heating"
    )
    so2_cooling_emission = models.FloatField(
        db_column="FEMSO2CLG", verbose_name="Emission - Sulfur Dioxide Cooling"
    )
    so2_hot_water_emission = models.FloatField(
        db_column="FEMSO2DHW", verbose_name="Emission - Sulfur Dioxide Water Heating"
    )
    so2_lights_appliance_emission = models.FloatField(
        db_column="FEMSO2LA", verbose_name="Emission - Sulfur Dioxide Lights and Appliances"
    )
    so2_photo_voltaic_emission = models.FloatField(
        db_column="FEMSO2PV", verbose_name="Emission - Sulfur Dioxide Photovoltaics"
    )
    nox_heating_emission = models.FloatField(
        db_column="FEMNOXHTG", verbose_name="Emission - Nitrogen Oxide Heating"
    )
    nox_cooling_emission = models.FloatField(
        db_column="FEMNOXCLG", verbose_name="Emission - Nitrogen Oxide Cooling"
    )
    nox_hot_water_emission = models.FloatField(
        db_column="FEMNOXDHW", verbose_name="Emission - Nitrogen Oxide Water Heating"
    )
    nox_lights_appliance_emission = models.FloatField(
        db_column="FEMNOXLA", verbose_name="Emission - Nitrogen Oxide Lights and Appliances"
    )
    nox_photo_voltaic_emission = models.FloatField(
        db_column="FEMNOXPV", verbose_name="Emission - Nitrogen Oxide Photovoltaics"
    )
    co2_hers_emission_savings = models.FloatField(
        db_column="FEMHERSCO2",
        verbose_name="HERS Emission Savings - Carbon Dioxide (Not in REM/Design)",
        null=True,
    )
    so2_hers_emission_savings = models.FloatField(
        db_column="FEMHERSSO2",
        verbose_name="HERS Emission Savings - Sulfur Dioxide (Not in REM/Design)",
        null=True,
    )
    nox_hers_emission_savings = models.FloatField(
        db_column="FEMHERSNOX",
        verbose_name="HERSEmission Savings - Nitrogen Oxides (Not in REM/Design)",
        null=True,
    )
    source_energy_heating = models.FloatField(
        db_column="FSRCEGYHTG", verbose_name="Source Energy - Heating (MBtu/year)"
    )
    source_energy_cooling = models.FloatField(
        db_column="FSRCEGYCLG", verbose_name="Source Energy - Cooling (MBtu/year)"
    )
    source_energy_hot_water = models.FloatField(
        db_column="FSRCEGYDHW", verbose_name="Source Energy - W ater Heating (MBtu/year)"
    )
    source_energy_lights_appliance = models.FloatField(
        db_column="FSRCEGYLA", verbose_name="Source Energy - Lights and Appliances (MBtu/year)"
    )
    source_energy_photo_voltaic = models.FloatField(
        db_column="FSRCEGYPV", verbose_name="Source Energy - Photovoltaics (MBtu/year)"
    )

    def get_heating_and_cooling_total_cost(self):  # pylint: disable=invalid-name
        """Return the combined heating and cooling costs"""
        return self.heating_cost + self.cooling_cost

    def get_monthly_total_cost(self):
        """Return the monthly total cost"""
        return self.total_cost / 12

    def get_monthly_consumption(self):
        """Return the monthly total heating / cooling consumption"""
        return (self.cooling_consumption + self.heating_consumption) / 12

    @property
    def total_consumption(self):
        """Return the total consumption"""
        return (
            self.heating_consumption
            + self.cooling_consumption
            + self.hot_water_consumption
            + self.lights_and_appliances_total_consumption
            + self.photo_voltaic_consumption
        )

    @property
    def total_consumption_without_pv(self):
        """Return the total consumption w/out pv"""
        return (
            self.heating_consumption
            + self.cooling_consumption
            + self.hot_water_consumption
            + self.lights_and_appliances_total_consumption
        )

    @property
    def reference_home(self):  # pylint: disable=inconsistent-return-statements
        """Return the REFERENCE HOME"""
        if self.simulation.export_type in DESIGN_MODELS and self.simulation.references.count():
            return self.simulation.references.last().results
        elif self.simulation.export_type == 1:
            # This follows the same pattern as calculator..
            _kw = {"similar__id": self.simulation.id, "export_type": 4}
            improved_data = Simulation.objects.filter(**_kw).last()
            if improved_data:
                return improved_data.references.last().results

    @property
    def udrh_percent_improvement(self):
        """Return the UDRH % improvement"""
        if self.simulation.export_type in DESIGN_MODELS and self.simulation.references.count():
            return (
                self.reference_home.total_consumption_without_pv - self.total_consumption_without_pv
            ) / self.reference_home.total_consumption_without_pv
        return 0.0

    @property
    def pretty_shell_area(self):
        """Return the shell area"""
        if self.shell_area:
            return int(round(self.shell_area))
        return "-"
