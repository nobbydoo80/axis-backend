"""analytics.py - Axis"""

__author__ = "Steven K"
__date__ = "3/16/22 13:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from analytics.models import AnalyticRollup
from rest_framework import serializers

from axis.company.managers import build_company_aliases, get_company_aliases

log = logging.getLogger(__name__)


def get_flat_analytic_rollup_results(instance):
    results = {}
    analytics = list(instance.analytics.all().values_list("name", flat=True))
    for analytic_name in analytics:
        for k, v in instance.references.get(analytic_name, {}).get("output", {}).items():
            if k not in results:
                results[k] = v
            else:
                if results[k] != v:
                    if k in ["errors", "error", "warning", "warnings"]:
                        results[k] += ", %s" % v
                    else:
                        log.warning(
                            f"Overwriting {k!r} on analytic {instance.id} of "
                            f"{results[k]!r} with {v!r}"
                        )
    return results


class AnalyticsBaseMixin:
    def divide_chunks(self, line: list, n: int) -> list:
        """Break it up."""
        for i in range(0, len(line), n):
            yield line[i : i + n]

    def to_representation(self, instance: AnalyticRollup) -> dict:
        """This will simply ferret out warning and error counts"""
        data = super(AnalyticsBaseMixin, self).to_representation(instance)

        def get_field_counts(search_dict, field="warning"):
            counter = 0
            if isinstance(search_dict, dict):
                if f"{field}s" in search_dict and search_dict[f"{field}s"]:
                    if isinstance(search_dict[f"{field}s"], list):
                        counter += len(search_dict[f"{field}s"])
                    elif isinstance(search_dict[f"{field}s"], int):
                        counter += search_dict[f"{field}s"]
                    return counter
                elif f"{field}" in search_dict and search_dict[f"{field}"]:
                    counter += 1
                    return counter
                for key in search_dict:
                    counter += get_field_counts(search_dict[key], field)
            elif isinstance(search_dict, list):
                for item in search_dict:
                    counter += get_field_counts(item, field)
            return counter

        # Rollup our errors and warnings appropriately
        if "warnings" in data:
            for k, v in data.items():
                if k in ["warnings", "errors"]:
                    continue
                data["warnings"] += get_field_counts(v, "warning")
            if "errors" not in data:  # Add
                data["warnings"] += get_field_counts(v, "error")
        if "errors" in data:
            for k, v in data.items():
                if k in ["errors"]:
                    continue
                data["errors"] += get_field_counts(v, "errors")

        return data

    class Meta:
        """Meta Options"""

        model = AnalyticRollup
        fields = ("output_analysis",)


class HomeOverViewSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance):
        aliases = build_company_aliases(company=instance.content_object.company)

        def company_similar(value1, value2):
            val1 = get_company_aliases(f"{value1 if value1 is not None else ''}")
            val2 = get_company_aliases(f"{value2 if value2 is not None else ''}")
            if any(item in val1 for item in val2):
                return True
            for name1 in val1:
                if name1 in aliases.keys():
                    for name2 in val2:
                        if name2 in aliases.keys():
                            if aliases[name1] == aliases[name2]:
                                return True
            return False

        def string_similar(value1, value2):
            """This uses the same method of removing punctuation"""
            val1 = get_company_aliases(f"{value1 if value1 is not None else ''}")
            val2 = get_company_aliases(f"{value2 if value2 is not None else ''}")
            return any(item in val1 for item in val2)

        rater_builder_completed_homes = self.context.get("rater_builder_completed_homes", 0) or 0

        return {
            "rating_company": {
                "label": "Rating Company",
                "value": self.context.get("simulation_rating_company"),
                "warning": not company_similar(
                    self.context.get("simulation_rating_company"),
                    self.context.get("rater"),
                ),
                "compared_to": self.context.get("rater"),
            },
            "rater": {
                "label": "Rater",
                "value": self.context.get("simulation_rater_of_record"),
                "warning": not string_similar(
                    self.context.get("simulation_rater_of_record"),
                    self.context.get("rater_of_record"),
                ),
                "compared_to": self.context.get("rater_of_record"),
            },
            "builder_company": {
                "label": "Builder Company",
                "value": self.context.get("simulation_builder"),
                "warning": not company_similar(
                    self.context.get("simulation_builder"), self.context.get("builder")
                ),
                "compared_to": self.context.get("builder"),
            },
            "address": {
                "label": "Address",
                "value": self.context.get("simulation_property_address"),
                "warning": not string_similar(
                    self.context.get("simulation_property_address"),
                    self.context.get("addresss_long"),
                ),
                "compared_to": self.context.get("addresss_long"),
            },
            "recent_homes": {
                "label": "Rater/Builder Homes Certified",
                "value": rater_builder_completed_homes,
                "warning": rater_builder_completed_homes < 5,
                "compared_to": "Min 5 homes",
            },
            "electric_utility": {
                "label": "Electric Utility",
                "value": self.context.get("electric_utility_rates"),
                "warning": self.context.get("electric_utility")
                and self.context.get("electric_utility_rates") in ["N/A", None],
                "compared_to": self.context.get("electric_utility"),
            },
            "gas_utility": {
                "label": "Gas Utility",
                "value": self.context.get("gas_utility_rates"),
                "warning": self.context.get("gas_utility")
                and self.context.get("gas_utility_rates") in ["N/A", None],
                "compared_to": self.context.get("gas_utility"),
            },
            "udrh": {
                "label": "UDRH",
                "value": self.context.get("eto_reference_home_type"),
                "warning": None,
                "compared_to": self.context.get("eto_reference_home_type"),
            },
            "climate_zone": {
                "label": "Climate Zone",
                "value": self.context.get("simulation_climate_zone", "")
                + " %s" % self.context.get("weather_station", ""),
                "warning": not string_similar(
                    self.context.get("simulation_climate_zone"),
                    self.context.get("climate_zone"),
                ),
                "compared_to": self.context.get("climate_zone"),
            },
            "simulation_url": {
                "label": self.context.get("source_type", "N/A"),
                "warning": None,
                "value": self.context.get("simulation_url"),
                "external_url": self.context.get("simulation_external_url"),
            },
        }


class EPSAdminSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance):
        measure_map = {
            "is-affordable-housing": "Affordable Housing",
            "is-adu": "ADU",
            "builder-payment-redirected": "Payment Re-direct",
            "smart-thermostat-brand": "Smart Thermostat",
            # 2021 Stuff
            "has-battery-storage": "Has Battery Storage",
            "has-solar-water-heat": "Has Solar Water Heater",
            "eto-additional-incentives": "Additional Incentives",
            "grid-harmonization-elements": "Energy Smart Home elements",
            "solar-elements": "Solar Elements",
            # 2022
            "eto-electric-elements": "Solar/EV/Storage Elements",
            "fire-rebuild-qualification": "Fire Rebuild",
            # Misc
            "equipment-heat-pump-water-heater-serial-number": "HPWH Serial Number",
            "equipment-gas-tank-water-heater-serial-number": "Gas Storage Water Heater Serial Number",
            "equipment-gas-tankless-water-heater-serial-number": "Gas Tankless Water Heater Serial Number",
            "has-gas-fireplace": "Fireplace Efficiency",
        }

        result = {}
        for measure_id in measure_map:
            value = self.context.get(measure_id, {}).get("input", "")
            value = "" if value is None else value
            d = value.lower()
            if d in ["n/a", "", "no", "false", "no fireplace"]:
                continue
            result[measure_id] = {"label": measure_map[measure_id], "value": value}

        sim_fields = {
            "propane-used": "Propane Utilized",
            "low_flow_fixtures_used": "Low Flow Fixtures Used",
            "pipes_fully_insulated": "Pipes fully insulated",
        }

        if "propane" in self.context.get("fuels_used", []):
            result["propane-used"] = {"label": sim_fields["propane-used"], "value": "Yes"}
        for item in ["low_flow_fixtures_used", "pipes_fully_insulated"]:
            value = self.context.get(item, "Not Provided")
            if value is True:
                continue
            if value is False:
                value = "No"
            result[item] = {"label": sim_fields[item], "value": value}

        for k, v in result.items():
            result[k]["warning"] = True
        return list(result.values())


class ModelComplexitySerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance):
        """Pull the modeling information"""
        label_map = {
            "qty_heating": "Number of heating systems",
            "qty_hot_water": "Number of water heaters",
            "has_hydronic_system": "Hydronic Radiant system",
            "foundation_type": "Foundation Type",
            "crawl_space_type": "Crawl Space Type",
            "has_dwhr": "Drain Water Heat Recovery",
            "recirculation_pump": "Re-Circulation Pumps",
            "fixture_max_length": "Farthest Fixture Length",
            "mechanical_ventilation_type": "Ventilation",
            "duct_supply_unconditioned_avg_r_value": "Unconditioned space avg duct R-Value (Supply)",
            "duct_return_unconditioned_avg_r_value": "Unconditioned space avg duct R-Value (Return)",
            "shelter_class": "Shelter Class",
            "range_fuel": "Range/Oven Fuel",
            "dryer_fuel": "Clothes Dryer Fuel",
        }

        _ducts = ["duct_return_unconditioned_avg_r_value", "duct_supply_unconditioned_avg_r_value"]

        result = {}

        for key, label in label_map.items():
            value = self.context.get(key)
            value = value.get("value") if isinstance(value, dict) else value
            value = "N/A" if value is None else value

            if value == 0.0 and key in _ducts:
                value = "N/A"

            if isinstance(value, float):
                value = round(value, 1)

            result[key] = {"label": label, "value": value}

        if result["dryer_fuel"]["value"].lower() != "electric":
            result["dryer_fuel"]["warning"] = "Bad Fuel"

        if result["shelter_class"]["value"] not in ["4", 4]:
            result["shelter_class"]["warning"] = "Bad Shelter Class"

        # Append the crawl space type
        if self.context.get("enclosed_crawl_space_type"):
            if result["foundation_type"]["value"] != "N/A":
                value = self.context.get("enclosed_crawl_space_type")
                result["foundation_type"]["value"] += " (%s)" % value

        result["distribution_systems"] = {"label": "No HVAC distribution", "value": "N/A"}
        if self.context.get("hvac_distribution_systems"):
            systems = self.context.get("hvac_distribution_systems")
            label = "%s Distribution Systems" % len(systems)
            value = [f'{d["source"]}: {d["display"]}' for d in systems]
            result["distribution_systems"] = {"label": label, "value": value}

        return result


class ModelInputsSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance):
        """Pull the modeling information"""
        results = []
        object = self.context.get("model_heater_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heater Characteristics"
            results.append(object)

        object = self.context.get("model_heat_pump_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heat Pump Heating Characteristics"
            results.append(object)

        object = self.context.get("model_heat_pump_cooling_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Heat Pump Cooling Characteristics"
            results.append(object)

        object = self.context.get("model_water_heater_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Hot Water Characteristics"
            results.append(object)

        # Legacy
        object = self.context.get("model_ventilation_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Ventilation Characteristics"
            results.append(object)

        # New Breakout style
        object = self.context.get("model_exhaust_ventilation_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Exhaust Ventilation Characteristics"
            results.append(object)

        object = self.context.get("model_supply_ventilation_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Supply Ventilation Characteristics"
            results.append(object)

        object = self.context.get("model_balanced_ventilation_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Balanced Ventilation Characteristics"
            results.append(object)

        object = self.context.get("model_refrigerator_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Refrigeration Characteristics"
            results.append(object)

        object = self.context.get("model_dishwasher_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Dishwasher Characteristics"
            results.append(object)

        object = self.context.get("model_clothes_washer_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Clothes Washer Characteristics"
            results.append(object)

        object = self.context.get("model_clothes_dryer_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Clothes Dryer Characteristics"
            results.append(object)

        object = self.context.get("model_pv_characteristics", {})
        if object.get("simulation") and object.get("checklist"):
            object["label"] = "Photovoltaic Characteristics"
            results.append(object)

        return results


class HeatingAllocationSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warning = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("values", "warning", "warnings")

    def get_field_data(self, instance):
        result = []
        data = self.context.get("heating_load_allocations", {})
        result += data.get("values", [])
        data = self.context.get("cooling_load_allocations", {})
        result += data.get("values", [])
        return result

    @cached_property
    def _warning_data(self):
        result = []
        data = self.context.get("heating_load_allocations", {})
        if data.get("warning"):
            result.append(data.get("warning"))
        data = self.context.get("cooling_load_allocations", {})
        if data.get("warning"):
            result.append(data.get("warning"))
        return result

    def get_warnings(self, instance):
        return len(self._warning_data)

    def get_warning(self, instance):
        if len(self._warning_data):
            return ", ".join(self._warning_data)


class FieldQASerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    fields = serializers.SerializerMethodField(method_name="get_field_data")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = ("warnings", "fields")

    def get_field_data(self, instance):
        """Pull the modeling information"""
        results = []
        responses = self.context.get("qa-responses", {})
        for key, response_data in responses.items():
            response = response_data.get("input")
            response_pretty = response_data.get("pretty")
            label = response_data.get("_question")
            if response is not None:
                alt_response_pretty = self.context.get(key, {}).get("pretty", "N/A")
                _warning = f"{response_pretty}".lower() != f"{alt_response_pretty}".lower()

                results.append(
                    {
                        "label": label,
                        "value": response_pretty,
                        "warning": _warning,
                        "compared_to": alt_response_pretty,
                    }
                )
        return results


class ETOHomeAnalysisSerializer(AnalyticsBaseMixin, serializers.ModelSerializer):
    warnings = serializers.IntegerField(default=0)
    home_overview = HomeOverViewSerializer(source="*")
    eps_admin = EPSAdminSerializer(source="*")
    model_complexity = ModelComplexitySerializer(source="*")
    model_inputs = ModelInputsSerializer(source="*")
    heating_allocations = HeatingAllocationSerializer(source="*")
    field_qa = HeatingAllocationSerializer(source="*")

    class Meta(AnalyticsBaseMixin.Meta):
        fields = (
            "warnings",
            "home_overview",
            "eps_admin",
            "model_complexity",
            "model_inputs",
            "heating_allocations",
            "field_qa",
        )
