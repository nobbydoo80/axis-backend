"""measures.py - Axis"""

__author__ = "Steven K"
__date__ = "8/25/21 12:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from simulation.models import GroundSourceHeatPump, Heater
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    HeatingEfficiencyUnit,
    DistributionSystemType,
    CoolingEfficiencyUnit,
    HeatingCoolingCapacityUnit,
)

from axis.customer_eto.eep_programs.washington_code_credit import (
    WACCFuelType,
    EfficientWaterHeating,
)
from axis.customer_eto.enumerations import HeatType, YesNo
from .base import BaseXMLSerializer

log = logging.getLogger(__name__)


class MeasureSerializer(BaseXMLSerializer):
    """This will wrangle out the mesasures"""

    def get_eps_hot_water_measure(self, instance, install_date=None):
        DHW_MAP = {
            WaterHeaterStyle.CONVENTIONAL: "Storage",
            WaterHeaterStyle.TANKLESS: "Tankless",
            WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP: "Heat Pump",
            WaterHeaterStyle.GROUND_SOURCE_HEAT_PUMP: "Heat Pump",
            WaterHeaterStyle.INTEGRATED: "Integrated",
        }

        try:
            mechanical = instance.home_status.floorplan.simulation.mechanical_equipment
            equipment = mechanical.dominant_water_heating_equipment
            hot_water = equipment.equipment
        except AttributeError:
            return

        sn, fuel = "", hot_water.get_fuel_display()
        if hot_water.is_heat_pump():
            fuel = "Electric"
            sn = self.context.get("water_heater_heat_pump_sn", "")
        elif hot_water.fuel == FuelType.NATURAL_GAS:
            fuel = "Gas"
            sn = self.context.get("water_heater_gas_sn", "")
            if hot_water.style == WaterHeaterStyle.TANKLESS:
                sn = self.context.get("water_heater_tankless_sn", "")

        attributes = [
            ("ENFACT", hot_water.efficiency),
            ("MANUFACTURER", self.context.get("water_heater_brand", "")),
            ("MODEL", self.context.get("water_heater_model", "")),
            ("SN", sn),
            ("DHWTYPE", DHW_MAP[hot_water.style]),
            ("FUELTYPE", fuel),
            ("LOCATION", equipment.get_location_display()),
            ("TANKSIZE", hot_water.tank_size),
        ]
        return self.add_measure_element(
            code="WHEPS",
            install_date=install_date,
            electric_load_profile=self.context.get("electric_load_profile"),
            gas_load_profile=self.context.get("gas_load_profile"),
            **dict(attributes),
        )

    def get_gas_furnace(self, instance, install_date=None):
        try:
            mechanical = instance.home_status.floorplan.simulation.mechanical_equipment
            equipment = mechanical.dominant_heating_equipment
            heater = equipment.equipment
        except AttributeError:
            return

        if heater is None:
            return

        attributes = [
            (
                "AFUE",
                heater.efficiency if heater.efficiency_unit == HeatingEfficiencyUnit.AFUE else "",
            ),
            ("MANUFACTURER", self.context.get("furnace_brand", "")),
            ("MODEL", self.context.get("furnace_model", "")),
        ]
        return self.add_measure_element(
            code="GASFFURNEPS", install_date=install_date, **dict(attributes)
        )

    def get_heat_pump(self, instance, install_date=None):
        try:
            mechanical = instance.home_status.floorplan.simulation.mechanical_equipment
            equipment = mechanical.dominant_heating_equipment
            heater = equipment.equipment
        except AttributeError:
            return

        if heater is None or isinstance(heater, Heater):
            return

        heating_efficiency, heating_capacity = "", ""
        if heater.heating_efficiency_unit == HeatingEfficiencyUnit.HSPF:
            heating_efficiency = heater.heating_efficiency
        if heater.capacity_unit == HeatingCoolingCapacityUnit.KBTUH:
            heating_capacity = heater.heating_capacity

        try:
            cooling = mechanical.dominant_cooling_equipment
            cooling = cooling.equipment
        except AttributeError:
            cooling = None

        cooling_efficiency = ""
        if cooling and cooling.cooling_efficiency_unit == CoolingEfficiencyUnit.SEER:
            cooling_efficiency = cooling.cooling_efficiency

        hp_type = "Ducted"
        duct_type = equipment.heating_distribution_systems.first().system_type
        if duct_type == DistributionSystemType.DUCTLESS:
            hp_type = "DHP"
        if heater and isinstance(heater, GroundSourceHeatPump):
            hp_type = "Geothermal"

        attributes = [
            ("HPTYPE", hp_type),
            ("HSPF", heating_efficiency),
            ("MANUFACTURER", self.context.get("heat_pump_brand", "")),
            ("MODEL", self.context.get("heat_pump_model", "")),
            ("SEER", cooling_efficiency),
            ("BACKUPHEAT", "Electric"),
            ("HEATCAP", heating_capacity),
            ("SN", self.context.get("heat_pump_sn", "")),
        ]
        return self.add_measure_element(code="HPEPS", install_date=install_date, **dict(attributes))

    def get_fireplace(self, instance, install_date=None):
        try:
            mechanical = instance.home_status.floorplan.simulation.mechanical_equipment
            equipment = mechanical.dominant_heating_equipment
            heater = equipment.equipment
        except AttributeError:
            return

        if heater is None:
            return

        other_heater_type = self.context.get("other_heater_type", "") or ""
        if "fireplace" in other_heater_type.lower():
            attributes = [
                (
                    "AFUE",
                    heater.efficiency
                    if heater.efficiency_unit == HeatingEfficiencyUnit.AFUE
                    else "",
                ),
                ("MANUFACTURER", self.context.get("other_heater_brand", "")),
                ("MODEL", self.context.get("other_heater_model", "")),
            ]
            return self.add_measure_element(
                code="NHFIREPLEPS", install_date=install_date, **dict(attributes)
            )

    def get_generic_heater(self, instance, heating_type, install_date=None):
        try:
            mechanical = instance.home_status.floorplan.simulation.mechanical_equipment
            equipment = mechanical.dominant_heating_equipment
            heater = equipment.equipment
        except AttributeError:
            return

        if heater is None:
            return

        attributes = [
            ("MANUFACTURER", self.context.get("other_heater_brand", "")),
            ("MODEL", self.context.get("other_heater_model", "")),
            ("EFFRATE", heater.efficiency),
            ("FUELTYPE", heater.get_fuel_display()),
            ("HEATCAP", heater.capacity),
            ("HEATTYPE", heating_type),
        ]
        return self.add_measure_element(
            code="HEATSYSEPS", install_date=install_date, **dict(attributes)
        )

    def get_eps_heater_measure(self, instance, install_date=None):
        heating_type = self.context.get("primary_heating_type")

        if heating_type is None:
            return

        if heating_type.lower() in ["gas furnace", "other gas"]:
            return self.get_gas_furnace(instance, install_date)
        elif "heat pump" in heating_type.lower():
            return self.get_heat_pump(instance, install_date)
        elif "fireplace" in heating_type.lower():
            return self.get_fireplace(instance, install_date)
        return self.get_generic_heater(instance, heating_type, install_date)

    def get_eps_solar_measure(self, instance, install_date):
        try:
            has_solar = instance.home_status.floorplan.simulation.has_solar_generation
        except AttributeError:
            has_solar = False

        if not has_solar:
            return

        pv = instance.home_status.floorplan.simulation.photovoltaics.order_by("-capacity").first()

        solar_kw_capacity = ""
        if not self.context.get("solar_kw_capacity"):
            solar_kw_capacity = sum(
                instance.home_status.floorplan.simulation.photovoltaics.values_list(
                    "capacity", flat=True
                )
            )

        attributes = [
            ("ESTPRO", pv.capacity),
            ("ORIENTATION", pv.orientation or ""),
            ("TILT", pv.tilt),
            ("BATTERY", self.context.get("has_battery_storage", "No")),
            ("TOTALDCCAP", self.context.get("solar_kw_capacity", solar_kw_capacity)),
        ]
        return self.add_measure_element(
            code="EPSSOLPV", install_date=install_date, **dict(attributes)
        )

    def get_eps_net_zero_measure(self, instance, install_date):
        """SLE Measure"""
        if not self.context.get("net_zero_eps_incentive"):
            return

        generation = self.context.get("percentage_generation_kwh", 0)
        gas_improvement = self.context.get("percentage_therm_improvement", 0)
        incentive = self.context.get("net_zero_eps_incentive")
        attributes = [
            ("PERCENTGENERATION", round(max([0, generation]), 2)),
            ("GASIMPROV", max([0, min([gas_improvement, 100])])),
        ]
        return self.add_measure_element(
            code="EPSNZ",
            install_date=install_date,
            incentive=incentive,
            **dict(attributes),
        )

    def get_eps_solar_ready_measure(self, instance, install_date=datetime.date) -> list:
        """SLE Measure"""
        attributes = [
            ("PGROSS", None),  # TODO request this info
            ("PFOOT", None),  # TODO request this info
            ("RATIO", None),  # TODO request this info
            ("CAPAC", None),  # TODO request this info
            ("FEAS", None),  # TODO request this info
        ]
        data = []
        incentive = self.context.get("solar_ready_builder_incentive") or 0.0
        if incentive:
            data.append(
                self.add_measure_element(
                    code="SOLRDYCON",
                    install_date=install_date,
                    incentive=incentive,
                    trade_ally="BUILDER",
                    **dict(attributes),
                )
            )
        incentive = self.context.get("solar_ready_verifier_incentive") or 0.0
        if incentive:
            data.append(
                self.add_measure_element(
                    code="SOLRDYCON",
                    install_date=install_date,
                    incentive=incentive,
                    trade_ally="VERIFIER",
                    **dict(attributes),
                )
            )
        return data

    def get_eps_smart_homes_measure(self, instance, install_date):
        if not any(
            [
                self.context.get("energy_smart_homes_eps_incentive"),
                self.context.get("solar_storage_builder_incentive"),
                self.context.get("ev_ready_builder_incentive"),
            ]
        ):
            return

        elements = self.context.get("grid_harmonization_elements", None)
        if elements and elements.startswith("Energy smart homes – "):
            elements = elements[21:]
        if elements is None:
            elements = self.context.get("electric_elements", "")

        solar_elements = self.context.get("solar_elements", "")
        incentive = self.context.get("energy_smart_homes_eps_incentive")

        project_type = self.context.get("project_type")

        if incentive is None:
            if project_type == "SLE":
                incentive = self.context.get("solar_storage_builder_incentive")
                if incentive in [0.0, None]:
                    return
            else:
                incentive = self.context.get("ev_ready_builder_incentive")
                if incentive in [0.0, None]:
                    return

        attributes = [
            ("ESHTYPE", elements),
            ("SOLARTYPE", solar_elements),
        ]
        return self.add_measure_element(
            code="EPSESH",
            install_date=install_date,
            incentive=incentive,
            **dict(attributes),
        )

    def get_cobid_builder_measure(self, instance, install_date):
        if not self.context.get("cobid_builder_measure"):
            return

        incentive = self.context.get("cobid_builder_measure")

        return self.add_measure_element(
            code="DEIBONUSBUILDER", install_date=install_date, incentive=incentive
        )

    def get_cobid_verifier_measure(self, instance, install_date):
        if not self.context.get("cobid_verifier_incentive"):
            return

        incentive = self.context.get("cobid_verifier_incentive")

        return self.add_measure_element(
            code="DEIBONUSVERIFIER", install_date=install_date, incentive=incentive
        )

    def get_eps_smart_thermostats(self, instance, install_date):
        """Get the smart thermostat measure"""
        if self.context.get("thermostat_brand", "N/A") in [None, "N/A"]:
            return

        attributes = [
            ("MANUFACTURER", self.context.get("thermostat_brand")),
        ]

        return self.add_measure_element(
            code="SMARTTHERMOEPS",
            install_date=install_date,
            incentive=self.context.get("thermostat_incentive", 0),
            **dict(attributes),
        )

    def get_eps_verifier_electric_measure(self, instance, install_date):
        if not self.context.get("verifier_electric_incentive"):
            return

        return self.add_measure_element(
            code="CUSTEPSVERFELE",
            life=self.context["electric_life"],
            incentive=self.context["verifier_electric_incentive"],
            gas_load_profile="None - gas",
            electric_load_profile=self.context["electric_load_profile"],
            install_date=install_date,
        )

    def get_eps_verifier_gas_measure(self, instance, install_date):
        if not self.context.get("verifier_gas_incentive"):
            return

        return self.add_measure_element(
            code="CUSTEPSVERFGAS",
            life=self.context["gas_life"],
            incentive=self.context["verifier_gas_incentive"],
            electric_load_profile="None - ele",
            gas_load_profile=self.context["gas_load_profile"],
            install_date=install_date,
        )

    def get_additional_incentive_measure(self, instance, install_date, code="SPIFELE"):
        if self.context.get("eto_additional_incentives", "No") in [None, "No"]:
            return

        return self.add_measure_element(code=code, install_date=install_date)

    def get_eps_builder_electric_measure(self, instance, install_date, code="EPSENHELE"):
        if not self.context.get("builder_electric_incentive"):
            return

        return self.add_measure_element(
            code=code,
            life=self.context["electric_life"],
            savings_kwh=max([0, self.context["kwh_savings"]]),
            savings_therm=0,
            incentive=self.context["builder_electric_incentive"],
            gas_load_profile="None - gas",
            electric_load_profile=self.context["electric_load_profile"],
            install_date=install_date,
        )

    def get_eps_builder_gas_measure(self, instance, install_date, code="EPSENHGAS"):
        if not self.context.get("builder_gas_incentive"):
            return

        return self.add_measure_element(
            code=code,
            life=self.context["gas_life"],
            savings_kwh=0,
            savings_therm=max([0, self.context["therm_savings"]]),
            incentive=self.context["builder_gas_incentive"],
            electric_load_profile="None - ele",
            gas_load_profile=self.context["gas_load_profile"],
            install_date=install_date,
        )

    def get_wcc_hot_water_measure(self, instance, install_date=None):
        # Return nothing is water heater is None
        if not self.context.get("water_heater_brand"):
            return

        # Return nothing is water heating option is 5.2
        if self.context.get("water_heating_option") in [
            EfficientWaterHeating.OPTION_5p2.value,
            EfficientWaterHeating.NONE.value,
        ]:
            return

        hot_water_type = None
        fuel = efficiency = None
        if self.context.get("water_heating_option") == EfficientWaterHeating.OPTION_5p3.value:
            hot_water_type = "Tankless"
            fuel = "Gas"
            efficiency = self.context.get("water_heater_gas_uef")

        if self.context.get("water_heating_option") in [
            EfficientWaterHeating.OPTION_5p4.value,
            EfficientWaterHeating.OPTION_5p5.value,
            EfficientWaterHeating.OPTION_5p6.value,
        ]:
            hot_water_type = "Tank"
            fuel = "Ele"
            efficiency = self.context["water_heater_electric_uef"]

        attributes = [
            ("ENFACT", efficiency),
            ("MANUFACTURER", self.context.get("water_heater_brand", "")),
            ("MODEL", self.context.get("water_heater_model", "")),
        ]
        if fuel:
            attributes.append(("FUELTYPE", fuel))
        if hot_water_type:
            attributes.append(("DHWTYPE", hot_water_type))
        return self.add_measure_element(
            code="WHEPS",
            install_date=install_date,
            electric_load_profile=self.context.get("electric_load_profile"),
            gas_load_profile=self.context.get("gas_load_profile"),
            **dict(attributes),
        )

    def get_wcc_heater_measure(self, instance, install_date=None):
        if self.context.get("furnace_brand") is None:
            return

        attributes = [
            ("AFUE", self.context.get("furnace_afue", "")),
            ("MANUFACTURER", self.context.get("furnace_brand", "")),
            ("MODEL", self.context.get("furnace_model", "")),
        ]
        return self.add_measure_element(
            code="GASFFURNEPS", install_date=install_date, **dict(attributes)
        )

    def get_fireplace_incentive_measure(self, instance, install_date=None):
        """WA Code Credits: Efficient Fireplace"""
        if not self.context.get("fireplace_incentive"):
            return

        # TODO: Updates tests when we fill in these holes
        return self.add_measure_element(
            code="WACODECREDTSEF",
            life=15,
            savings_kwh=0,
            savings_therm=max([0, self.context.get("fireplace_therm_savings", 0)]),
            incentive=self.context.get("fireplace_incentive"),
            electric_load_profile="None-ele",
            gas_load_profile="Hearth",
            install_date=install_date,
        )

    def get_thermostat_incentive_measure(self, instance, install_date=None):
        """WA Code Credits: Smart Thermostat"""
        if not self.context.get("thermostat_incentive"):
            return

        return self.add_measure_element(
            code="WACODECREDTSST",
            life=11,
            savings_kwh=0,
            savings_therm=max([0, self.context.get("thermostat_therm_savings", 0)]),
            incentive=self.context.get("thermostat_incentive"),
            electric_load_profile="None-ele",
            gas_load_profile="Res Heating",
            install_date=install_date,
        )

    def get_code_credit_incentive_measure(self, instance, install_date=None):
        """WA Code Credits: Half Credit Above Code"""
        if not self.context.get("code_credit_incentive"):
            return

        return self.add_measure_element(
            code="WACODECREDT",
            life=44,
            savings_kwh=0,
            savings_therm=max([0, self.context.get("code_based_therm_savings", 0)]),
            incentive=self.context.get("code_credit_incentive"),
            electric_load_profile="None-ele",
            gas_load_profile="Res Heating",
            install_date=install_date,
        )

    def get_wcc_verifier_measure(self, instance, install_date):
        if not self.context.get("verifier_incentive"):
            return

        return self.add_measure_element(
            code="CUSTEPSVERFGAS",
            life=34,
            incentive=self.context["verifier_incentive"],
            electric_load_profile="None - ele",
            gas_load_profile="Res Heating",  # TODO FIX ME
            install_date=install_date,
        )

    def get_eps_fire_triple_pane_windows_measure(self, instance, install_date):
        if self.context.get("has_triple_pane_windows") in [None, False]:
            return
        return self.add_measure_element(
            code="EPSFRFRTW",
            incentive=instance.triple_pane_window_incentive,
            install_date=install_date,
        )

    def get_eps_fire_rigid_insulation_measure(self, instance, install_date):
        if self.context.get("has_rigid_insulation") in [None, False]:
            return
        return self.add_measure_element(
            code="EPSFRFREI",
            incentive=instance.rigid_insulation_incentive,
            install_date=install_date,
        )

    def get_eps_fire_sealed_attic_measure(self, instance, install_date):
        if self.context.get("has_sealed_attic") in [None, False]:
            return
        return self.add_measure_element(
            code="EPSFRFRSA",
            incentive=instance.sealed_attic_incentive,
            install_date=install_date,
        )

    def to_representation_washington_code_credit(self, instance):
        install_date = instance.home_status.certification_date
        if install_date is None:
            install_date = self.context.get(
                "install_date", datetime.datetime.now() + datetime.timedelta(days=30)
            )

        data = [
            self.get_wcc_hot_water_measure(instance, install_date),
            self.get_wcc_heater_measure(instance, install_date),
            self.get_fireplace_incentive_measure(instance, install_date),
            self.get_thermostat_incentive_measure(instance, install_date),
            self.get_code_credit_incentive_measure(instance, install_date),
            self.get_wcc_verifier_measure(instance, install_date),
        ]
        return [x for x in data if x is not None]

    # def to_representation_eto_fire_2021(self, instance):
    #     install_date = instance.home_status.certification_date
    #     if install_date is None:
    #         install_date = self.context.get(
    #             "install_date", datetime.datetime.now() + datetime.timedelta(days=180)
    #         )
    #
    #     data = [
    #         self.get_eps_hot_water_measure(instance, install_date),
    #         self.get_eps_heater_measure(instance, install_date),
    #         self.get_eps_solar_measure(instance, install_date),
    #         self.get_eps_net_zero_measure(instance, install_date),
    #         self.get_eps_smart_homes_measure(instance, install_date),
    #         self.get_eps_smart_thermostats(instance, install_date),
    #         self.get_eps_verifier_electric_measure(instance, install_date),
    #         self.get_eps_verifier_gas_measure(instance, install_date),
    #         # self.get_additional_incentive_measure(instance, install_date, code="SPIFELE"),
    #         self.get_eps_builder_electric_measure(instance, install_date, code="EPSFRELE"),
    #         self.get_eps_builder_gas_measure(instance, install_date, code="EPSFRGAS"),
    #         self.get_additional_incentive_measure(instance, install_date, code="EPSSLRRDYPV"),
    #         self.get_eps_fire_triple_pane_windows_measure(instance, install_date),
    #         self.get_eps_fire_rigid_insulation_measure(instance, install_date),
    #         self.get_eps_fire_sealed_attic_measure(instance, install_date),
    #     ]
    #     return [x for x in data if x is not None]

    def to_representation_default(self, instance):
        install_date = instance.home_status.certification_date
        if install_date is None:
            install_date = self.context.get(
                "install_date", datetime.datetime.now() + datetime.timedelta(days=180)
            )

        data = [
            self.get_eps_hot_water_measure(instance, install_date),
            self.get_eps_heater_measure(instance, install_date),
            self.get_eps_solar_measure(instance, install_date),
            self.get_eps_smart_homes_measure(instance, install_date),
            self.get_eps_smart_thermostats(instance, install_date),
            self.get_eps_verifier_electric_measure(instance, install_date),
            self.get_eps_verifier_gas_measure(instance, install_date),
            # self.get_additional_incentive_measure(instance, install_date, code="SPIFELE"),
        ]

        # If any fire stuff we need to push this in lieu of regular
        if any(
            [
                self.context.get("fire_rebuild_qualification") in [YesNo.YES.value, YesNo.YES],
                self.context.get("has_triple_pane_windows"),
                self.context.get("has_rigid_insulation"),
                self.context.get("has_sealed_attic"),
            ]
        ):
            data += [
                self.get_eps_builder_electric_measure(instance, install_date, code="EPSFRELE"),
                self.get_eps_builder_gas_measure(instance, install_date, code="EPSFRGAS"),
            ]
        else:
            data += [
                self.get_eps_builder_electric_measure(instance, install_date),
                self.get_eps_builder_gas_measure(instance, install_date),
            ]

        data += [
            self.get_additional_incentive_measure(instance, install_date, code="EPSSLRRDYPV"),
            self.get_cobid_builder_measure(instance, install_date),
            self.get_cobid_verifier_measure(instance, install_date),
            self.get_eps_fire_triple_pane_windows_measure(instance, install_date),
            self.get_eps_fire_rigid_insulation_measure(instance, install_date),
            self.get_eps_fire_sealed_attic_measure(instance, install_date),
        ]

        if self.context.get("project_type") == "SLE":
            data = [
                self.get_eps_net_zero_measure(instance, install_date),
                self.get_eps_smart_homes_measure(instance, install_date),
            ]
            data += self.get_eps_solar_ready_measure(instance, install_date)

        return [x for x in data if x is not None]

    def to_representation(self, instance):
        """Notes:
        - Duct Measures were removed 2020
        - Insulation Measures (incl. Flat Ceiling, AGW, Slab) were remvoed in 2020
        - ACH Measures were removed in 2020
        - PCT CFL Measures were removed in 2020
        * Hot Water was retained and shifted to simulation model in 2020
        * Heater was retained and shifted to simulation model in 2020
        - Vents were removed in 2020
        - Windows were removed in 2020
        * Solar was retained and shifted to simulation model in 2020
        * Net Zero was added in 2020
        - Shower Measures were removed in 2020
        * Thermostat Measures were updated in 2020
        * Verifier Measures were updated in 2020
        * Builder Measures were updated in 2020
        """
        measures = super(MeasureSerializer, self).to_representation(instance)
        measures = [_m for _m in measures if _m is not None]
        for idx, measure in enumerate(measures):
            measure["@ID"] = idx + 1
        return {"Measures": {"Measure": measures}}
