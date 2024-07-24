"""collection_responses.py: Django Analytics Collection Responses"""


import logging
from collections import OrderedDict

from django_input_collection.models import CollectionRequest

from axis.checklist.collection import ChecklistCollector

__author__ = "Steven K"
__date__ = "08/30/2019 10:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def get_generic_collection_responses(measures, collection_request_id, user_role="rater"):
    """Gathers the collection responses for a collection request for a user role"""

    try:
        collection_request = CollectionRequest.objects.get(id=collection_request_id)
    except CollectionRequest.DoesNotExist:
        return OrderedDict([(k, {"input": None}) for k in measures])

    collector = ChecklistCollector(collection_request, user_role=user_role)

    data = dict(collector.get_inputs(measure=measures).values_list("instrument__measure", "data"))
    text = dict(
        collector.get_inputs(measure=measures).values_list(
            "instrument__measure", "instrument__text"
        )
    )

    instruments = collector.get_instruments()
    instrument_lookup = {i.measure_id: i for i in instruments}

    result = OrderedDict()
    for key in measures:
        result[key] = data.get(key, {"input": None})
        result[key]["_question"] = text.get(key, None)
        result[key]["is_custom"] = data.get(key, {}).get("hints", {}).get("is_custom")
        try:
            result[key]["pretty"] = collector.get_data_display(instrument_lookup[key])
        except KeyError:
            result[key]["pretty"] = None
    return result


def get_collection_responses(rater_collection_request_id):
    """Gets the collection request responses"""

    measures = [
        "is-affordable-housing",  # Not in 2020
        "is-adu",
        "builder-payment-redirected",
        "solar",  # Not in 2020
        "has-solar-pv",  # Not in 2020
        "has-solar-water-heat",  # Not in 2020
        "has-battery-storage",  # Not used in 2022
        "applicable-solar-incentive",  # Not in 2020
        "smart-thermostat-brand",
        "primary-heating-equipment-type",
        "equipment-furnace",
        "equipment-heat-pump",
        "equipment-water-heater",
        "equipment-air-conditioner-brand",
        "equipment-air-conditioner-model-number-indoor",
        "equipment-air-conditioner-model-number-outdoor",
        "equipment-heat-pump-water-heater-serial-number",
        "equipment-gas-tank-water-heater-serial-number",
        "equipment-gas-tankless-water-heater-serial-number",
        "has-gas-fireplace",
        "equipment-refrigerator",
        "equipment-dishwasher",
        "equipment-clothes-washer",
        "equipment-clothes-dryer",
        "equipment-ventilation-balanced",
        "equipment-ventilation-exhaust",
        "equipment-ventilation-hrv-erv",
        "equipment-ventilation-spot-erv-count",
        "equipment-ventilation-supply-brand",
        "equipment-ventilation-supply-model",
        "ceiling-r-value",  # Not used in 2022
        "eto-additional-incentives",  # Not used in 2022
        "eto-electric-elements",
        "solar-elements",
        "grid-harmonization-elements",  # Not used in 2022
        "ets-annual-etsa-kwh",  # NOT USED 2020
        "non-ets-annual-pv-watt",  # NOT USED 2020
        "equipment-ventilation-system-type",
        "non-ets-annual-pv-watts",
        "non-ets-dc-capacity-installed",
    ]
    return get_generic_collection_responses(measures, rater_collection_request_id)


def get_qa_collection_responses(qa_collection_request_id):
    """Gets the QA Responses"""
    measures = [
        "is-affordable-housing",  # Not in 2020
        "is-adu",
        "builder-payment-redirected",
        "solar",  # Not in 2020
        "has-solar-pv",  # Not in 2020
        "has-battery-storage",
        "smart-thermostat-brand",
        "primary-heating-equipment-type",
        "equipment-furnace",
        "equipment-heat-pump",
        "equipment-water-heater",
        "equipment-air-conditioner-brand",
        "equipment-air-conditioner-model-number-indoor",
        "equipment-air-conditioner-model-number-outdoor",
        "equipment-refrigerator",
        "equipment-dishwasher",
        "equipment-clothes-washer",
        "equipment-clothes-dryer",
        "equipment-ventilation-balanced",
        "equipment-ventilation-exhaust",
        "ceiling-r-value",  # Not used in 2022
        "eto-additional-incentives",  # Not used in 2022
        "eto-electric-elements",
        "solar-elements",
        "grid-harmonization-elements",  # Not used in 2022
        "ets-annual-etsa-kwh",  # NOT USED 2020
        "non-ets-annual-pv-watt",  # NOT USED 2020
        "equipment-ventilation-system-type",
        "non-ets-annual-pv-watts",
        "non-ets-dc-capacity-installed",
    ]
    data = get_generic_collection_responses(measures, qa_collection_request_id, user_role="qa")
    return {"qa-responses": OrderedDict([(k, v) for k, v in data.items() if k in measures])}


def get_wcc_collection_responses(rater_collection_request_id, rater_collection_last_update):
    """Gathers the checklist responses for a home."""
    measures = [
        "wcc-conditioned_floor_area",
        "wcc-water_heating_fuel",
        "wcc-thermostat_type",
        "wcc-fireplace_efficiency",
        "wcc-wall_cavity_r_value",
        "wcc-wall_continuous_r_value",
        "wcc-framing_type",
        "wcc-window_u_value",
        "wcc-window_shgc",
        "wcc-floor_cavity_r_value",
        "wcc-slab_perimeter_r_value",
        "wcc-under_slab_r_value",
        "wcc-ceiling_r_value",
        "wcc-raised_heel",
        "wcc-total_ua_alternative",
        "wcc-air_leakage_ach",
        "wcc-ventilation_type",
        "wcc-ventilation_brand",
        "wcc-ventilation_model",
        "wcc-hrv_asre",
        "wcc-furnace_brand",
        "wcc-furnace_model",
        "wcc-furnace_afue",
        "wcc-furnace_location",
        "wcc-duct_location",
        "wcc-duct_leakage",
        "wcc-dwhr_installed",
        "wcc-water_heater_brand",
        "wcc-water_heater_model",
        "wcc-gas_water_heater_uef",
        "wcc-electric_water_heater_uef",
    ]
    data = get_generic_collection_responses(measures, rater_collection_request_id)
    return {k.replace("wcc-", ""): v["input"] for k, v in data.items()}
