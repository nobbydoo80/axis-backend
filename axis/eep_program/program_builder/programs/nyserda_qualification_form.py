"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/28/2022 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NyserdaQualificationForm(ProgramBuilder):
    name = "NYSERDA Qualification Form"
    slug = "nyserda-qualification-form"
    owner = "integral-building"
    is_qa_program = False
    opt_in = False
    workflow_default_settings = {}
    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0
    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0
    enable_standard_disclosure = False
    require_floorplan_approval = False
    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = False
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2013, 5, 2)
    start_date = datetime.date(2013, 5, 2)

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": True,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "nyserda-qf-10-energy-star-method",
                "nyserda-qf-20-central-air-conditioner",
                "nyserda-qf-21-cac-quantity",
                "nyserda-qf-22-cac-sizes-in-tons-separate-list",
                "nyserda-qf-23-cac-seers-separate-list-by-comma",
                "nyserda-qf-23-cac-eers-separate-list-by-comma",
                "nyserda-qf-30-heat-pump-quantity",
                "nyserda-qf-31-heat-pump-seers-separate-list-by",
                "nyserda-qf-32-heat-pump-eers-separate-list-by",
                "nyserda-qf-33-heat-pump-hspf-air-source",
                "nyserda-qf-34-heat-pump-cop-ground-source",
                "nyserda-qf-40-duct-sealing",
                "nyserda-qf-41-all-ductwork-air-handlers-in-cond",
                "nyserda-qf-50-ventilation-rates-required",
                "nyserda-qf-51-ventilation-delivered",
                "nyserda-qf-60-residential-associated-common-area",
                "nyserda-qf-70-rater-thermal-enclosure-checklist",
                "nyserda-qf-71-rater-hvac-checklist-complete",
                "nyserda-qf-72-rater-combustion-safety-testing-co",
                "nyserda-qf-73-builder-water-management-checklist",
                "nyserda-qf-74-contractor-hvac-checklist-complete",
                "nyserda-qf-80-building-type-stated-on-building-pe",
                "nyserda-qf-81-permit-or-contract",
                "nyserda-qf-90-total-lamps-in-entire-dwelling",
                "nyserda-qf-91-total-lamps-in-high-use-areas",
                "nyserda-qf-92-minimum-code-required-high-efficacy",
                "nyserda-qf-100-cfls-in-livingdining",
                "nyserda-qf-101-cfls-in-bed-rooms",
                "nyserda-qf-102-cfls-in-baths",
                "nyserda-qf-103-cfls-kitchen",
                "nyserda-qf-104-cfls-in-other-high-use-interior",
                "nyserda-qf-105-cfls-in-garage",
                "nyserda-qf-106-cfls-high-use-exterior",
                "nyserda-qf-107-cfls-total-non-high-use",
                "nyserda-qf-110-leds-livingdining",
                "nyserda-qf-111-leds-bed-rooms",
                "nyserda-qf-112-leds-baths",
                "nyserda-qf-113-leds-kitchen",
                "nyserda-qf-114-leds-other-high-use-interior",
                "nyserda-qf-115-leds-garage",
                "nyserda-qf-116-leds-high-use-exterior",
                "nyserda-qf-117-leds-total-non-high-use",
                "nyserda-qf-120-pin-based-fixture-livingdining",
                "nyserda-qf-121-pin-based-fixture-bed-rooms",
                "nyserda-qf-122-pin-based-fixture-baths",
                "nyserda-qf-123-pin-based-fixture-kitchen",
                "nyserda-qf-124-pin-based-fixture-other-high-use-i",
                "nyserda-qf-125-pin-based-fixture-garage",
                "nyserda-qf-126-pin-based-fixture-high-use-exterio",
                "nyserda-qf-127-pin-based-fixture-total-non-high-u",
                "nyserda-qf-130-led-fixture-livingding",
                "nyserda-qf-131-led-fixture-bed-rooms",
                "nyserda-qf-132-led-fixture-baths",
                "nyserda-qf-133-led-fixture-kitchen",
                "nyserda-qf-134-led-fixture-other-high-use-interio",
                "nyserda-qf-135-led-fixture-garage",
                "nyserda-qf-136-led-fixture-high-use-exterior",
                "nyserda-qf-137-led-fixture-total-non-high-use",
                "nyserda-qf-140-refrigerator",
                "nyserda-qf-141-freezer",
                "nyserda-qf-142-dishwasher",
                "nyserda-qf-143-clothes-washer",
                "nyserda-qf-150-cac-16-seer-13-eer",
                "nyserda-qf-160-ecm-motors-refer-to-mps-for-re",
                "nyserda-qf-170-minimum-above-code-kwh-savings-req",
            ],
        },
    }
    texts = {
        "rater": {
            "nyserda-qf-10-energy-star-method": "NYSERDA-QF 1.0 ENERGY STAR Method",
            "nyserda-qf-20-central-air-conditioner": "NYSERDA-QF 2.0 Central Air Conditioner",
            "nyserda-qf-21-cac-quantity": "NYSERDA-QF 2.1 CAC Quantity",
            "nyserda-qf-22-cac-sizes-in-tons-separate-list": "NYSERDA-QF 2.2 CAC Size(s) in tons (separate list by comma)",
            "nyserda-qf-23-cac-seers-separate-list-by-comma": "NYSERDA-QF 2.3 CAC Seer(s) (separate list by comma)",
            "nyserda-qf-23-cac-eers-separate-list-by-comma": "NYSERDA-QF 2.3 CAC EER(s) (separate list by comma)",
            "nyserda-qf-30-heat-pump-quantity": "NYSERDA-QF 3.0 Heat Pump Quantity",
            "nyserda-qf-31-heat-pump-seers-separate-list-by": "NYSERDA-QF 3.1 Heat Pump SEER(s) (separate list by comma)",
            "nyserda-qf-32-heat-pump-eers-separate-list-by": "NYSERDA-QF 3.2 Heat Pump EER(s) (separate list by comma)",
            "nyserda-qf-33-heat-pump-hspf-air-source": "NYSERDA-QF 3.3 Heat Pump HSPF (air source)",
            "nyserda-qf-34-heat-pump-cop-ground-source": "NYSERDA-QF 3.4 Heat Pump COP (ground source)",
            "nyserda-qf-40-duct-sealing": "NYSERDA-QF 4.0 Duct Sealing?",
            "nyserda-qf-41-all-ductwork-air-handlers-in-cond": "NYSERDA-QF 4.1 All Ductwork & Air Handlers in Conditioned Space?",
            "nyserda-qf-50-ventilation-rates-required": "NYSERDA-QF 5.0 Ventilation Rates Required",
            "nyserda-qf-51-ventilation-delivered": "NYSERDA-QF 5.1 Ventilation Delivered",
            "nyserda-qf-60-residential-associated-common-area": "NYSERDA-QF 6.0 Residential Associated Common Area (SF)",
            "nyserda-qf-70-rater-thermal-enclosure-checklist": "NYSERDA-QF 7.0 Rater: Thermal Enclosure Checklist Complete?",
            "nyserda-qf-71-rater-hvac-checklist-complete": "NYSERDA-QF 7.1 Rater: HVAC Checklist Complete?",
            "nyserda-qf-72-rater-combustion-safety-testing-co": "NYSERDA-QF 7.2 Rater: Combustion Safety Testing Complete Checklist Complete?",
            "nyserda-qf-73-builder-water-management-checklist": "NYSERDA-QF 7.3 Builder: Water Management Checklist Complete?",
            "nyserda-qf-74-contractor-hvac-checklist-complete": "NYSERDA-QF 7.4 Contractor: HVAC Checklist Complete?",
            "nyserda-qf-80-building-type-stated-on-building-pe": "NYSERDA-QF 8.0 Building Type Stated on Building Permit",
            "nyserda-qf-81-permit-or-contract": "NYSERDA-QF 8.1 Permit or Contract?",
            "nyserda-qf-90-total-lamps-in-entire-dwelling": "NYSERDA-QF 9.0 Total Lamps in Entire Dwelling",
            "nyserda-qf-91-total-lamps-in-high-use-areas": "NYSERDA-QF 9.1 Total Lamps in High Use Areas",
            "nyserda-qf-92-minimum-code-required-high-efficacy": "NYSERDA-QF 9.2 Minimum Code-Required High Efficacy Lamps",
            "nyserda-qf-100-cfls-in-livingdining": "NYSERDA-QF 10.0 CFLs in Living/Dining",
            "nyserda-qf-101-cfls-in-bed-rooms": "NYSERDA-QF 10.1 CFLs in Bed Rooms",
            "nyserda-qf-102-cfls-in-baths": "NYSERDA-QF 10.2 CFLs in Baths",
            "nyserda-qf-103-cfls-kitchen": "NYSERDA-QF 10.3 CFLs Kitchen",
            "nyserda-qf-104-cfls-in-other-high-use-interior": "NYSERDA-QF 10.4 CFLs in Other High Use Interior",
            "nyserda-qf-105-cfls-in-garage": "NYSERDA-QF 10.5 CFLs in Garage",
            "nyserda-qf-106-cfls-high-use-exterior": "NYSERDA-QF 10.6 CFLs High Use Exterior",
            "nyserda-qf-107-cfls-total-non-high-use": "NYSERDA-QF 10.7 CFLs Total Non-High Use",
            "nyserda-qf-110-leds-livingdining": "NYSERDA-QF 11.0 LEDs Living/Dining",
            "nyserda-qf-111-leds-bed-rooms": "NYSERDA-QF 11.1 LEDs Bed Rooms",
            "nyserda-qf-112-leds-baths": "NYSERDA-QF 11.2 LEDs Baths",
            "nyserda-qf-113-leds-kitchen": "NYSERDA-QF 11.3 LEDs Kitchen",
            "nyserda-qf-114-leds-other-high-use-interior": "NYSERDA-QF 11.4 LEDs Other High Use Interior",
            "nyserda-qf-115-leds-garage": "NYSERDA-QF 11.5 LEDs Garage",
            "nyserda-qf-116-leds-high-use-exterior": "NYSERDA-QF 11.6 LEDs High Use Exterior",
            "nyserda-qf-117-leds-total-non-high-use": "NYSERDA-QF 11.7 LEDs Total Non-High Use",
            "nyserda-qf-120-pin-based-fixture-livingdining": "NYSERDA-QF 12.0 Pin-Based Fixture Living/Dining",
            "nyserda-qf-121-pin-based-fixture-bed-rooms": "NYSERDA-QF 12.1 Pin-Based Fixture Bed Rooms",
            "nyserda-qf-122-pin-based-fixture-baths": "NYSERDA-QF 12.2 Pin-Based Fixture Baths",
            "nyserda-qf-123-pin-based-fixture-kitchen": "NYSERDA-QF 12.3 Pin-Based Fixture Kitchen",
            "nyserda-qf-124-pin-based-fixture-other-high-use-i": "NYSERDA-QF 12.4 Pin-Based Fixture Other High Use Interior",
            "nyserda-qf-125-pin-based-fixture-garage": "NYSERDA-QF 12.5 Pin-Based Fixture Garage",
            "nyserda-qf-126-pin-based-fixture-high-use-exterio": "NYSERDA-QF 12.6 Pin-Based Fixture High Use Exterior",
            "nyserda-qf-127-pin-based-fixture-total-non-high-u": "NYSERDA-QF 12.7 Pin-Based Fixture Total Non-High Use",
            "nyserda-qf-130-led-fixture-livingding": "NYSERDA-QF 13.0 LED Fixture Living/Ding",
            "nyserda-qf-131-led-fixture-bed-rooms": "NYSERDA-QF 13.1 LED Fixture Bed Rooms",
            "nyserda-qf-132-led-fixture-baths": "NYSERDA-QF 13.2 LED Fixture Baths",
            "nyserda-qf-133-led-fixture-kitchen": "NYSERDA-QF 13.3 LED Fixture Kitchen",
            "nyserda-qf-134-led-fixture-other-high-use-interio": "NYSERDA-QF 13.4 LED Fixture Other High Use Interior",
            "nyserda-qf-135-led-fixture-garage": "NYSERDA-QF 13.5 LED Fixture Garage",
            "nyserda-qf-136-led-fixture-high-use-exterior": "NYSERDA-QF 13.6 LED Fixture High Use Exterior",
            "nyserda-qf-137-led-fixture-total-non-high-use": "NYSERDA-QF 13.7 LED Fixture Total Non-High Use",
            "nyserda-qf-140-refrigerator": "NYSERDA-QF 14.0 Refrigerator",
            "nyserda-qf-141-freezer": "NYSERDA-QF 14.1 Freezer",
            "nyserda-qf-142-dishwasher": "NYSERDA-QF 14.2 Dishwasher",
            "nyserda-qf-143-clothes-washer": "NYSERDA-QF 14.3 Clothes Washer",
            "nyserda-qf-150-cac-16-seer-13-eer": "NYSERDA-QF 15.0 CAC 16 SEER + 13 EER +",
            "nyserda-qf-160-ecm-motors-refer-to-mps-for-re": "NYSERDA-QF 16.0 ECM Motors (refer to M.P.S. for requirements)",
            "nyserda-qf-170-minimum-above-code-kwh-savings-req": "NYSERDA-QF 17.0 Minimum above-code kWh savings requirement does not apply because all appliances, lamps and permanently installed fixtures in high use locations as noted above are ENERGY STAR-qualified.",
        },
    }
    descriptions = {
        "rater": {},
    }
    suggested_responses = {
        "rater": {
            (
                "Reference Design Package",
                "Performance Path",
            ): [
                "nyserda-qf-10-energy-star-method",
            ],
            (
                "No CAC Installed",
                "ENERGY STAR CAC",
                "Non-ENERGY STAR CAC",
            ): [
                "nyserda-qf-20-central-air-conditioner",
            ],
            (
                "Yes",
                "N/A",
            ): [
                "nyserda-qf-40-duct-sealing",
            ],
            (
                "Yes",
                "No",
            ): [
                "nyserda-qf-41-all-ductwork-air-handlers-in-cond",
                "nyserda-qf-70-rater-thermal-enclosure-checklist",
                "nyserda-qf-71-rater-hvac-checklist-complete",
                "nyserda-qf-72-rater-combustion-safety-testing-co",
                "nyserda-qf-73-builder-water-management-checklist",
                "nyserda-qf-74-contractor-hvac-checklist-complete",
                "nyserda-qf-170-minimum-above-code-kwh-savings-req",
            ],
            (
                "Detached Single-Family",
                "Attached Single-Family (townhomes)",
                "Two-family (including duplexes)",
                "Multi-family with common entrance",
                "Multi-family with exterior entrance for each unit",
            ): [
                "nyserda-qf-80-building-type-stated-on-building-pe",
            ],
            (
                "Permit",
                "Contract",
            ): [
                "nyserda-qf-81-permit-or-contract",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "nyserda-qf-21-cac-quantity",
            "nyserda-qf-30-heat-pump-quantity",
            "nyserda-qf-60-residential-associated-common-area",
            "nyserda-qf-91-total-lamps-in-high-use-areas",
            "nyserda-qf-92-minimum-code-required-high-efficacy",
            "nyserda-qf-100-cfls-in-livingdining",
            "nyserda-qf-101-cfls-in-bed-rooms",
            "nyserda-qf-102-cfls-in-baths",
            "nyserda-qf-103-cfls-kitchen",
            "nyserda-qf-104-cfls-in-other-high-use-interior",
            "nyserda-qf-105-cfls-in-garage",
            "nyserda-qf-106-cfls-high-use-exterior",
            "nyserda-qf-107-cfls-total-non-high-use",
            "nyserda-qf-110-leds-livingdining",
            "nyserda-qf-111-leds-bed-rooms",
            "nyserda-qf-112-leds-baths",
            "nyserda-qf-113-leds-kitchen",
            "nyserda-qf-114-leds-other-high-use-interior",
            "nyserda-qf-115-leds-garage",
            "nyserda-qf-116-leds-high-use-exterior",
            "nyserda-qf-117-leds-total-non-high-use",
            "nyserda-qf-120-pin-based-fixture-livingdining",
            "nyserda-qf-121-pin-based-fixture-bed-rooms",
            "nyserda-qf-122-pin-based-fixture-baths",
            "nyserda-qf-123-pin-based-fixture-kitchen",
            "nyserda-qf-124-pin-based-fixture-other-high-use-i",
            "nyserda-qf-125-pin-based-fixture-garage",
            "nyserda-qf-126-pin-based-fixture-high-use-exterio",
            "nyserda-qf-127-pin-based-fixture-total-non-high-u",
            "nyserda-qf-130-led-fixture-livingding",
            "nyserda-qf-131-led-fixture-bed-rooms",
            "nyserda-qf-132-led-fixture-baths",
            "nyserda-qf-133-led-fixture-kitchen",
            "nyserda-qf-134-led-fixture-other-high-use-interio",
            "nyserda-qf-135-led-fixture-garage",
            "nyserda-qf-136-led-fixture-high-use-exterior",
            "nyserda-qf-137-led-fixture-total-non-high-use",
            "nyserda-qf-140-refrigerator",
            "nyserda-qf-141-freezer",
            "nyserda-qf-142-dishwasher",
            "nyserda-qf-143-clothes-washer",
            "nyserda-qf-150-cac-16-seer-13-eer",
            "nyserda-qf-160-ecm-motors-refer-to-mps-for-re",
        ],
        "float": [
            "nyserda-qf-50-ventilation-rates-required",
            "nyserda-qf-51-ventilation-delivered",
        ],
        "date": [
            "nyserda-qf-90-total-lamps-in-entire-dwelling",
        ],
    }
