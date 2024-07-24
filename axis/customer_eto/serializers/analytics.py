"""analytics.py: Django Analaytics Serializer"""

import logging
from collections import OrderedDict

from analytics.models import AnalyticRollup
from analytics.serializers import AnalyticRollupSerializer
from rest_framework import serializers

__author__ = "Steven K"
__date__ = "08/29/2019 11:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class ETO2019AnalyticRollupSerializer(AnalyticRollupSerializer):
    """This is the Analytics Serializer"""

    status = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    home_analysis = serializers.SerializerMethodField()
    analytics = serializers.SerializerMethodField()

    _flat_results = None

    class Meta:
        """Meta Options"""

        model = AnalyticRollup
        fields = ("id", "date_modified", "program_name", "status", "home_analysis", "analytics")

    def get_status(self, obj):
        """Status"""
        return "%s" % obj.get_status_display() if obj.status != "READY" else ""

    def get_program_name(self, obj):
        """Get the program name"""
        return "%s" % obj.content_object.eep_program

    @property
    def results(self):
        """Pull the the data"""
        if self._flat_results is not None:
            return self._flat_results
        self._flat_results = self.instance.get_flattened_results()
        return self._flat_results

    def _is_string_similar(self, string1, string2):
        """Are two strings similar"""
        string_1 = "".join("{}".format(string1).split()).lower()
        string_2 = "".join("{}".format(string2).split()).lower()
        return string_1 == string_2

    def _get_answer(self, slug):
        """Are an answer"""
        ans = self.results.get(slug, {}).get("input", "")
        return "" if ans is None else ans

    def get_home_overview(self, obj):
        """Get the home overview"""
        rater_builder_completed_homes = self.results.get("rater_builder_completed_homes", 0)
        if rater_builder_completed_homes is None:
            rater_builder_completed_homes = 0
        url = None
        # TODO FIXME WHEN SIMULATION HAS A UI
        if self.results.get("remrate_simulation_id"):
            url = "/floorplan/input/remrate/%s/" % self.results.get("remrate_simulation_id")
        data = {
            "warnings": None,
            "fields": OrderedDict(
                [
                    (
                        "rating_company",
                        {
                            "label": "Rating Company",
                            "value": self.results.get("rem_rating_company"),
                            "warning": not self._is_string_similar(
                                self.results.get("rem_rating_company"), self.results.get("rater")
                            ),
                            "compared_to": self.results.get("rater"),
                        },
                    ),
                    (
                        "rater",
                        {
                            "label": "Rater",
                            "value": self.results.get("rem_rater_of_record"),
                            "warning": not self._is_string_similar(
                                self.results.get("rem_rater_of_record"),
                                self.results.get("rater_of_record"),
                            ),
                            "compared_to": self.results.get("rater_of_record"),
                        },
                    ),
                    (
                        "builder_company",
                        {
                            "label": "Builder Company",
                            "value": self.results.get("rem_builder"),
                            "warning": not self._is_string_similar(
                                self.results.get("rem_builder"), self.results.get("builder")
                            ),
                            "compared_to": self.results.get("builder"),
                        },
                    ),
                    (
                        "address",
                        {
                            "label": "Address",
                            "value": self.results.get("rem_property_address"),
                            "warning": not self._is_string_similar(
                                self.results.get("rem_property_address"),
                                self.results.get("addresss_long"),
                            ),
                            "compared_to": self.results.get("addresss_long"),
                        },
                    ),
                    (
                        "recent_homes",
                        {
                            "label": "Rater/Builder Homes Certified",
                            "value": rater_builder_completed_homes,
                            "warning": rater_builder_completed_homes < 5,
                            "compared_to": "Min 5 homes",
                        },
                    ),
                    (
                        "electric_utility",
                        {
                            "label": "Electric Utility",
                            "value": self.results.get("electric_utility_rates"),
                            "warning": None,
                            "compared_to": self.results.get("electric_utility"),
                        },
                    ),
                    (
                        "gas_utility",
                        {
                            "label": "Gas Utility",
                            "value": self.results.get("gas_utility_rates"),
                            "warning": None,
                            "compared_to": self.results.get("gas_utility"),
                        },
                    ),
                    (
                        "udrh",
                        {
                            "label": "UDRH",
                        },
                    ),
                    (
                        "climate_zone",
                        {
                            "label": "Climate Zone",
                            "value": self.results.get("rem_climate_zone", "")
                            + " %s" % self.results.get("rem_site_label", ""),
                            "warning": not self._is_string_similar(
                                self.results.get("rem_climate_zone"),
                                self.results.get("climate_zone"),
                            ),
                            "compared_to": self.results.get("climate_zone"),
                        },
                    ),
                    ("rem_url", {"label": "Simulation Link", "warning": None, "value": url}),
                ]
            ),
        }
        _warn = len([True for key in data["fields"] if data["fields"][key].get("warning")])
        data["warnings"] = _warn
        return data

    def get_eps_admin(self, obj):
        """pull the EPS Admin section"""
        label_map = {
            "is-affordable-housing": "Affordable Housing",
            "is-adu": "ADU",
            "builder-payment-redirected": "Payment Re-direct",
            "solar": "Has Solar (PV)",
            "has-solar-pv": "Has Solar (PV)",
            "has-battery-storage": "Has Battery Storage",
            "smart-thermostat-brand": "Smart Thermostat",
            "has-solar-water-heat": "Has Solar Water Heater",
            "applicable-solar-incentive": "Qualify for Solar-Ready",
        }
        data = {"warnings": None, "fields": OrderedDict([])}
        for measure_id in label_map:
            value = self._get_answer(measure_id)
            d = value.lower()
            include_measure = (
                measure_id in ["smart-thermostat-brand"] and d not in ["n/a", ""] or "yes" in d
            )
            if include_measure:
                data["fields"][measure_id] = {"label": label_map[measure_id], "value": value}

        data["warnings"] = len(data["fields"])
        data["fields"] = data["fields"].values()
        return data

    def get_model_complexity(self, obj):
        """Pull the modeling information"""
        label_map = OrderedDict(
            [
                ("qty_heating", "Number of heating systems"),
                ("qty_hot_water", "Number of water heaters"),
                ("has_hydronic_system", "Hydronic Radiant system"),
                ("qty_duct_system", "Number of duct systems"),
                ("foundation_type", "Foundation Type"),
                ("crawl_space_type", "Crawl Space Type"),
                ("has_dwhr", "Drain Water Heat Recovery"),
                ("recirculation_pump", "Re-Circulation Pumps"),
                ("fixture_max_length", "Farthest Fixture Length"),
                ("mechanical_ventilation_type", "Ventilation"),
                (
                    "duct_supply_unconditioned_avg_r_value",
                    "Unconditioned space avg duct R-Value (Supply)",
                ),
                (
                    "duct_return_unconditioned_avg_r_value",
                    "Unconditioned space avg duct R-Value (Return)",
                ),
                ("shelter_class", "Shelter Class"),
                ("range_fuel", "Range/Oven Fuel"),
                ("dryer_fuel", "Clothes Dryer Fuel"),
            ]
        )

        data = {
            "warnings": None,
            "fields": OrderedDict([]),
        }

        _ducts = ["duct_return_unconditioned_avg_r_value", "duct_supply_unconditioned_avg_r_value"]

        for key, label in label_map.items():
            value = self.results.get(key)
            value = value.get("value") if isinstance(value, dict) else value
            value = "N/A" if value is None else value

            if value == 0.0 and key in _ducts:
                value = "N/A"

            data["fields"][key] = {"label": label, "value": value}

        if data["fields"]["dryer_fuel"]["value"].lower() != "electric":
            data["fields"]["dryer_fuel"]["warning"] = "Bad Fuel"

        # Append the crawl space type
        if self.results.get("enclosed_crawl_space_type"):
            if data["fields"]["foundation_type"]["value"] != "N/A":
                value = self.results.get("enclosed_crawl_space_type")
                data["fields"]["foundation_type"]["value"] += " (%s)" % value

        data["warnings"] = len([True for item in data["fields"].values() if item.get("warning")])
        return data

    def get_model_inputs(self, obj):
        """Pull the modeling information"""
        data = {"warnings": None, "fields": [], "inputs": [], "heating_allocation": None}

        object = self.results.get("model_heater_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Heater Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_heat_pump_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Heat Pump Heating Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_heat_pump_cooling_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Heat Pump Cooling Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_water_heater_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Hot Water Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_ventilation_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Ventilation Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_refrigerator_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Refrigeration Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_dishwasher_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Dishwasher Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_clothes_washer_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Clothes Washer Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_clothes_dryer_characteristics", {})
        if object.get("rem") and object.get("checklist"):
            object["label"] = "Clothes Dryer Characteristics"
            data["fields"].append(object)

        data["warnings"] = len([True for item in data["fields"] if item.get("warning")])

        return data

    def get_heating_cooling_allocations(self, obj):
        """Pull the modeling information"""
        data = self.results.get("heating_load_allocations", {})
        if not data.get("values"):
            data["values"] = []
        data["warnings"] = 1 if data.get("warning") else 0
        cool_data = self.results.get("cooling_load_allocations", {})
        data["warnings"] += 1 if cool_data.get("warning") else 0
        data["values"] += cool_data.get("values", [])
        return data

    def get_field_qa(self, obj):
        """Get QA Stuff"""
        data = {"warnings": None, "fields": []}

        responses = self.results.get("qa-responses", {})
        for key, response_data in responses.items():
            response = response_data.get("input")
            response_pretty = response_data.get("pretty")
            label = response_data.get("_question")
            if response is not None:
                alt_response = self.results.get(key, {}).get("input", "N/A")
                alt_response_pretty = self.results.get(key, {}).get("pretty", "N/A")
                try:
                    __pretty = "{}".format(alt_response_pretty).lower()
                    _warning = "{}".format(response_pretty).lower() != __pretty
                except (UnicodeDecodeError, UnicodeEncodeError):
                    _warning = response != alt_response
                data["fields"].append(
                    {
                        "label": label,
                        "value": response_pretty,
                        "warning": _warning,
                        "compared_to": alt_response_pretty,
                    }
                )

        data["warnings"] = len([True for item in data["fields"] if item.get("warning")])

        return data

    def get_home_analysis(self, obj):
        """Fetch all the data"""
        data = {
            "home_overview": self.get_home_overview(obj),
            "eps_admin": self.get_eps_admin(obj),
            "model_complexity": self.get_model_complexity(obj),
            "model_inputs": self.get_model_inputs(obj),
            "heating_allocations": self.get_heating_cooling_allocations(obj),
            "field_qa": self.get_field_qa(obj),
        }
        data["warnings"] = sum([item.get("warnings", 0) for item in data.values()])
        return data

    def get_output_analysis(self, obj):
        """Pull the output analysis"""
        data = {
            "warnings": None,
            "fields": [
                [
                    self.results.get("heating_consumption_kwh"),
                    self.results.get("heating_consumption_therms"),
                ],
                [
                    self.results.get("cooling_consumption_kwh"),
                    self.results.get("lights_and_appliances_consumption_kwh"),
                ],
                [
                    self.results.get("hot_water_consumption_kwh"),
                    self.results.get("hot_water_consumption_therms"),
                ],
                [self.results.get("design_load_heating"), self.results.get("design_load_cooling")],
                [
                    self.results.get("total_consumption"),
                    self.results.get("total_consumption_no_pv"),
                ],
            ],
        }

        def divide_chunks(line, n):
            """Break it up."""
            for i in range(0, len(line), n):
                yield line[i : i + n]

        fields = []
        for item in [
            self.results.get("heating_consumption_kwh", {}),
            self.results.get("heating_consumption_therms", {}),
            self.results.get("cooling_consumption_kwh", {}),
            self.results.get("lights_and_appliances_consumption_kwh", {}),
            self.results.get("hot_water_consumption_kwh", {}),
            self.results.get("hot_water_consumption_therms", {}),
            self.results.get("design_load_heating", {}),
            self.results.get("design_load_cooling", {}),
            self.results.get("total_consumption", {}),
            self.results.get("total_consumption_no_pv", {}),
        ]:
            if item and item.get("value", -1) > 0:
                fields.append(item)
        data["fields"] = list(divide_chunks(fields, 2))
        warnings = []
        for table in data["fields"]:
            warnings += [True for col in table if col.get("warning")]
        data["warnings"] = len(warnings)
        return data

    def get_insulation_analysis(self, obj):
        """Pull the insulation analysis"""
        data = {"warnings": None, "fields": []}
        key = self.results.get("total_frame_floor_area", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("total_frame_floor_area"),
                    self.results.get("dominant_floor_insulation_r_value"),
                ],
            ]
        key = self.results.get("total_slab_floor_area", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("total_slab_floor_area"),
                    self.results.get("dominant_slab_insulation_r_value"),
                ],
            ]
        data["fields"] += [
            [
                self.results.get("total_above_grade_wall_area", {}),
                self.results.get("dominant_above_grade_wall_r_value", {}),
            ],
            [
                self.results.get("total_ceiling_area", {}),
                self.results.get("dominant_ceiling_r_value", {}),
            ],
            [
                self.results.get("dominant_window_u_value", {}),
                self.results.get("dominant_window_shgc_value", {}),
            ],
            [
                self.results.get("total_window_area", {}),
            ],
        ]

        warnings = []
        for table in data["fields"]:
            warnings += [True for col in table if col.get("warning")]
        data["warnings"] = len(warnings)
        return data

    def get_mechanical_analysis(self, obj):
        """Get Mechanical Analysis"""
        data = {"warnings": None, "fields": []}
        key = self.results.get("heater_heating_capacity", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("heater_heating_capacity"),
                    self.results.get("heater_heating_efficiency"),
                ],
            ]
        key = self.results.get("air_conditioner_cooling_capacity", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("air_conditioner_cooling_capacity"),
                    self.results.get("air_conditioner_cooling_efficiency"),
                ],
            ]

        key = self.results.get("ground_source_heat_pump_heating_capacity", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("ground_source_heat_pump_heating_capacity"),
                    self.results.get("ground_source_heat_pump_heating_efficiency"),
                ],
                [
                    self.results.get("ground_source_heat_pump_cooling_capacity"),
                    self.results.get("ground_source_heat_pump_cooling_efficiency"),
                ],
            ]
        key = self.results.get("air_source_heat_pump_heating_capacity", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("air_source_heat_pump_heating_capacity"),
                    self.results.get("air_source_heat_pump_heating_efficiency"),
                ],
                [
                    self.results.get("air_source_heat_pump_cooling_capacity"),
                    self.results.get("air_source_heat_pump_cooling_efficiency"),
                ],
            ]
        key = self.results.get("dual_fuel_heat_pump_heating_capacity", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("dual_fuel_heat_pump_heating_capacity"),
                    self.results.get("dual_fuel_heat_pump_heating_efficiency"),
                ],
                [
                    self.results.get("dual_fuel_heat_pump_cooling_capacity"),
                    self.results.get("dual_fuel_heat_pump_cooling_efficiency"),
                ],
            ]
        key = self.results.get("water_heater_energy_factor", {})
        if key.get("value", -1) > 0:
            data["fields"] += [
                [
                    self.results.get("water_heater_tank_size"),
                    self.results.get("water_heater_energy_factor"),
                ],
            ]

        warnings = []
        for table in data["fields"]:
            warnings += [True for col in table if col.get("warning")]
        data["warnings"] = len(warnings)
        return data

    def get_ducts_infiltration_analysis(self, obj):
        """Duct data"""
        data = {
            "warnings": None,
            "fields": [
                [
                    self.results.get("duct_system_total_leakage", {}),
                    self.results.get("duct_system_total_total_real_leakage", {}),
                ],
            ],
        }

        data["fields"] += [
            [
                self.results.get("annual_infiltration_value", {}),
            ],
            [self.results.get("ventilation_rate", {}), self.results.get("ventilation_watts", {})],
        ]
        warnings = []
        for table in data["fields"]:
            warnings += [True for col in table if col.get("warning")]
        data["warnings"] = len(warnings)
        return data

    def get_analytics(self, obj):
        """Pull the analytics together."""
        data = {
            "output_analysis": self.get_output_analysis(obj),
            "insulation_analysis": self.get_insulation_analysis(obj),
            "mechanical_analysis": self.get_mechanical_analysis(obj),
            "ducts_infiltration_analysis": self.get_ducts_infiltration_analysis(obj),
        }
        data["warnings"] = sum([item.get("warnings", 0) for item in data.values()])
        return data


class ETO2020AnalyticRollupSerializer(ETO2019AnalyticRollupSerializer):
    """Simular to the 2019 just a couple tweaks."""

    def get_home_overview(self, obj):
        """Get the home overview"""
        rater_builder_completed_homes = self.results.get("rater_builder_completed_homes", 0)
        if rater_builder_completed_homes is None:
            rater_builder_completed_homes = 0
        url = None
        # TODO FIXME WHEN SIMULATION HAS A UI
        if self.results.get("remrate_simulation_id"):
            url = "/floorplan/input/remrate/%s/" % self.results.get("remrate_simulation_id")
        data = {
            "warnings": None,
            "fields": OrderedDict(
                [
                    (
                        "rating_company",
                        {
                            "label": "Rating Company",
                            "value": self.results.get("simulation_rating_company"),
                            "warning": not self._is_string_similar(
                                self.results.get("simulation_rating_company"),
                                self.results.get("rater"),
                            ),
                            "compared_to": self.results.get("rater"),
                        },
                    ),
                    (
                        "rater",
                        {
                            "label": "Rater",
                            "value": self.results.get("simulation_rater_of_record"),
                            "warning": not self._is_string_similar(
                                self.results.get("simulation_rater_of_record"),
                                self.results.get("rater_of_record"),
                            ),
                            "compared_to": self.results.get("rater_of_record"),
                        },
                    ),
                    (
                        "builder_company",
                        {
                            "label": "Builder Company",
                            "value": self.results.get("simulation_builder"),
                            "warning": not self._is_string_similar(
                                self.results.get("simulation_builder"), self.results.get("builder")
                            ),
                            "compared_to": self.results.get("builder"),
                        },
                    ),
                    (
                        "address",
                        {
                            "label": "Address",
                            "value": self.results.get("simulation_property_address"),
                            "warning": not self._is_string_similar(
                                self.results.get("simulation_property_address"),
                                self.results.get("addresss_long"),
                            ),
                            "compared_to": self.results.get("addresss_long"),
                        },
                    ),
                    (
                        "recent_homes",
                        {
                            "label": "Rater/Builder Homes Certified",
                            "value": rater_builder_completed_homes,
                            "warning": rater_builder_completed_homes < 5,
                            "compared_to": "Min 5 homes",
                        },
                    ),
                    (
                        "electric_utility",
                        {
                            "label": "Electric Utility",
                            "value": self.results.get("electric_utility_rates"),
                            "warning": None,
                            "compared_to": self.results.get("electric_utility"),
                        },
                    ),
                    (
                        "gas_utility",
                        {
                            "label": "Gas Utility",
                            "value": self.results.get("gas_utility_rates"),
                            "warning": None,
                            "compared_to": self.results.get("gas_utility"),
                        },
                    ),
                    (
                        "udrh",
                        {
                            "label": "UDRH Reference",
                            "value": self.results.get("eto_reference_home_type"),
                            "warning": None,
                            "compared_to": self.results.get("eto_reference_home_type"),
                        },
                    ),
                    (
                        "climate_zone",
                        {
                            "label": "Climate Zone",
                            "value": self.results.get("simulation_climate_zone", "")
                            + " %s" % self.results.get("weather_station", ""),
                            "warning": not self._is_string_similar(
                                self.results.get("simulation_climate_zone"),
                                self.results.get("climate_zone"),
                            ),
                            "compared_to": self.results.get("climate_zone"),
                        },
                    ),
                    ("simulation_url", {"label": "Simulation Link", "warning": None, "value": url}),
                ]
            ),
        }
        _warn = len([True for key in data["fields"] if data["fields"][key].get("warning")])
        data["warnings"] = _warn
        return data

    def get_model_inputs(self, obj):
        """Pull the modeling information"""
        data = {"warnings": None, "fields": [], "inputs": [], "heating_allocation": None}

        object = self.results.get("model_heater_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heater Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_heat_pump_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heat Pump Heating Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_heat_pump_cooling_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heat Pump Cooling Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_water_heater_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Hot Water Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_ventilation_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Ventilation Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_refrigerator_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Refrigeration Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_dishwasher_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Dishwasher Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_clothes_washer_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Clothes Washer Characteristics"
            data["fields"].append(object)

        object = self.results.get("model_clothes_dryer_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Clothes Dryer Characteristics"
            data["fields"].append(object)

        data["warnings"] = len([True for item in data["fields"] if item.get("warning")])

        return data

    def get_eps_admin(self, obj):
        """pull the EPS Admin section"""
        label_map = OrderedDict(
            [
                ("is-affordable-housing", "Affordable Housing"),
                ("is-adu", "ADU"),
                ("builder-payment-redirected", "Payment Re-direct"),
                ("has-battery-storage", "Has Battery Storage"),
                ("smart-thermostat-brand", "Smart Thermostat"),
                ("has-solar-water-heat", "Has Solar Water Heater"),
                ("eto-additional-incentives", "Additional Incentives"),
                ("grid-harmonization-elements", "Energy Smart Home elements"),
                ("solar-elements", "Solar Elements"),
                ("equipment-heat-pump-water-heater-serial-number", "HPWH Serial Number"),
                (
                    "equipment-gas-tank-water-heater-serial-number",
                    "Gas Storage Water Heater Serial Number",
                ),
                (
                    "equipment-gas-tankless-water-heater-serial-number",
                    "Gas Tankless Water Heater Serial Number",
                ),
                ("has-gas-fireplace", "Fireplace Efficiency"),
            ]
        )

        data = {"warnings": None, "fields": OrderedDict([])}
        for measure_id in label_map:
            value = self._get_answer(measure_id)
            d = value.lower()
            if d in ["n/a", "", "no", "false", "no fireplace"]:
                continue
            data["fields"][measure_id] = {"label": label_map[measure_id], "value": value}

        sim_fields = OrderedDict(
            [
                ("propane-used", "Propane Utilized"),
                ("low_flow_fixtures_used", "Low Flow Fixtures Used"),
                ("pipes_fully_insulated", "Pipes fully insulated"),
            ]
        )

        if "propane" in self.results.get("fuels_used", []):
            data["fields"]["propane-used"] = {"label": sim_fields["propane-used"], "value": "Yes"}
        for item in ["low_flow_fixtures_used", "pipes_fully_insulated"]:
            value = self.results.get(item, "Not Provided")
            if value is True:
                continue
            if value is False:
                value = "No"
            data["fields"][item] = {"label": sim_fields[item], "value": value}

        data["warnings"] = len(data["fields"])
        data["fields"] = data["fields"].values()

        return data

    def get_model_complexity(self, obj):
        """Pull the modeling information"""
        label_map = OrderedDict(
            [
                ("qty_heating", "Number of heating systems"),
                ("qty_hot_water", "Number of water heaters"),
                ("has_hydronic_system", "Hydronic Radiant system"),
                ("foundation_type", "Foundation Type"),
                ("crawl_space_type", "Crawl Space Type"),
                ("has_dwhr", "Drain Water Heat Recovery"),
                ("recirculation_pump", "Re-Circulation Pumps"),
                ("fixture_max_length", "Farthest Fixture Length"),
                ("mechanical_ventilation_type", "Ventilation"),
                (
                    "duct_supply_unconditioned_avg_r_value",
                    "Unconditioned space avg duct R-Value (Supply)",
                ),
                (
                    "duct_return_unconditioned_avg_r_value",
                    "Unconditioned space avg duct R-Value (Return)",
                ),
                ("shelter_class", "Shelter Class"),
                ("range_fuel", "Range/Oven Fuel"),
                ("dryer_fuel", "Clothes Dryer Fuel"),
            ]
        )

        data = {
            "warnings": None,
            "fields": OrderedDict([]),
        }

        _ducts = ["duct_return_unconditioned_avg_r_value", "duct_supply_unconditioned_avg_r_value"]

        for key, label in label_map.items():
            value = self.results.get(key)
            value = value.get("value") if isinstance(value, dict) else value
            value = "N/A" if value is None else value

            if value == 0.0 and key in _ducts:
                value = "N/A"

            if isinstance(value, float):
                value = round(value, 1)

            data["fields"][key] = {"label": label, "value": value}

        if data["fields"]["dryer_fuel"]["value"].lower() != "electric":
            data["fields"]["dryer_fuel"]["warning"] = "Bad Fuel"

        if data["fields"]["shelter_class"]["value"] not in ["4", 4]:
            data["fields"]["shelter_class"]["warning"] = "Bad Shelter Class"

        # Append the crawl space type
        if self.results.get("enclosed_crawl_space_type"):
            if data["fields"]["foundation_type"]["value"] != "N/A":
                value = self.results.get("enclosed_crawl_space_type")
                data["fields"]["foundation_type"]["value"] += " (%s)" % value

        data["fields"]["distribution_systems"] = {"label": "No HVAC distribution", "value": "N/A"}
        if self.results.get("hvac_distribution_systems"):
            systems = self.results.get("hvac_distribution_systems")
            label = "%s Distribution Systems" % len(systems)
            value = [f'{d["source"]}: {d["display"]}' for d in systems]
            data["fields"]["distribution_systems"] = {"label": label, "value": value}

        data["warnings"] = len([True for item in data["fields"].values() if item.get("warning")])
        return data


class ETO2021AnalyticRollupSerializer(ETO2020AnalyticRollupSerializer):
    pass
