"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NeeaEnergyStarV3Qa(ProgramBuilder):
    name = "Northwest ENERGY STAR Version 3: QA"
    slug = "neea-energy-star-v3-qa"
    owner = "neea"
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
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2013, 3, 7)
    start_date = datetime.date(2013, 3, 7)

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": True,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": True,
    }
    measures = {
        "rater": {
            "default": [
                "nwes-qa-10-blower-door-test-flow",
                "nwes-qa-11-blower-door-test-verifier-recorded-fl",
                "nwes-qa-12-ach50pa",
                "nwes-qa-20-duct-total-leakage-test-flow",
                "nwes-qa-30-duct-leakage-to-outside-test-flow",
                "nwes-qa-31-duct-leakage-to-outside-test-ptcs-rec",
                "nwes-qa-32-ptcs-sticker",
                "nwes-qa-40-caz-test-location",
                "nwes-qa-41-caz-test-change-in-pressure",
                "nwes-qa-42-caz-test-windy-day",
                "nwes-qa-50-room-pressure-test-wrt-body",
                "nwes-qa-60-ventilation-type-supplyexhaustbala",
                "nwes-qa-61-ventilation-exhaust-cfm-measured",
                "nwes-qa-62-ventilation-supply-cfm-measured",
                "nwes-qa-63-ventilation-system-meets-622",
                "nwes-qa-70-furnace-manufacturer",
                "nwes-qa-71-furnace-model-number",
                "nwes-qa-72-furnace-afue",
                "nwes-qa-73-furnace-fan-motor-type",
                "nwes-qa-80-heat-pump-manufacturer",
                "nwes-qa-81-heat-pump-model-number",
                "nwes-qa-82-heat-pump-seer-seasonal-energy-effic",
                "nwes-qa-83-heat-pump-hspf-heating-seasonal-per",
                "nwes-qa-84-heat-pump-corrected-flow",
                "nwes-qa-90-water-heater-manufacturer",
                "nwes-qa-91-water-heater-model-number",
                "nwes-qa-92-water-heater-ef-energy-factor",
                "nwes-qa-93-water-heater-hp-tier-1-or-tier-2",
                "nwes-qa-100-air-conditioner-manufacturer",
                "nwes-qa-101-air-conditioner-model-number",
                "nwes-qa-102-air-conditioner-seer-rating",
                "nwes-qa-110-ductless-heat-pump-manufacturer",
                "nwes-qa-111-ductless-heat-pump-model-number",
                "nwes-qa-120-zonal-gas-manufacturer",
                "nwes-qa-121-zonal-gas-model-number",
                "nwes-qa-130-zonal-electric-manufacturer",
                "nwes-qa-131-zonal-gas-model-number",
                "nwes-qa-140-hydronic-manufacturer",
                "nwes-qa-141-hydronic-model-number",
                "nwes-qa-150-ducts-manufacturer",
                "nwes-qa-151-ducts-model-number",
                "nwes-qa-160-insulation-r-values-floor",
                "nwes-qa-161-insulation-r-values-walls",
                "nwes-qa-162-insulation-r-values-slab",
                "nwes-qa-163-insulation-r-values-rafter-vault",
                "nwes-qa-164-insulation-r-values-scissor-truss",
                "nwes-qa-165-insulation-r-values-ceiling",
                "nwes-qa-166-insulation-r-values-below-grade-wall",
                "nwes-qa-167-insulation-tec-met",
                "nwes-qa-170-home-size-number-of-bedrooms",
                "nwes-qa-171-home-size-home-volume",
                "nwes-qa-172-home-size-square-footage",
                "nwes-qa-173-home-size-meets-benchmark",
                "nwes-qa-174-home-size-window-to-floor-area",
                "nwes-qa-180-appliances-energy-star",
                "nwes-qa-190-lighting-percentage-of-efficiency-li",
                "nwes-qa-200-bath-fan-airflows-master-bath-measu",
                "nwes-qa-201-bath-fan-airflows-upstairs-guest-bat",
                "nwes-qa-202-bath-fan-airflows-upstairs-guest-bat",
                "nwes-qa-203-bath-fan-airflows-downstairs-guest-b",
                "nwes-qa-204-bath-fan-airflows-downstairs-guest-b",
                "nwes-qa-205-bath-fan-airflows-laundry-room-meas",
                "nwes-qa-210-room-airflow-measurements-do-the-roo",
                "nwes-qa-220-miscellaneous-window-u-value-meets-b",
                "nwes-qa-221-miscellaneous-shower-flow-rate",
                "nwes-qa-222-miscellaneous-bathroom-sink-flow-rat",
                "nwes-qa-223-miscellaneous-kitchen-sink-flow-rate",
                "nwes-qa-224-miscellaneous-energy-star-label-pre",
                "nwes-qa-225-miscellaneous-remediation-log",
                "nwes-qa-230-thermal-enclosure",
                "nwes-qa-231-water-management",
                "nwes-qa-232-hvac-verifier",
                "nwes-qa-233-hvac-contractor",
                "nwes-qa-240-hvac-contractor-partner-name",
                "nwes-qa-241-hvac-contractor-is-qualified-as-per-n",
                "nwes-qa-242-performance-tester-is-ptcs-qualified",
                "nwes-qa-243-notes",
                "nwes-qa-250-furnace-total-external-static-pressur",
            ],
        },
    }
    texts = {
        "rater": {
            "nwes-qa-10-blower-door-test-flow": "NWES-QA 1.0 Blower Door Test: Flow",
            "nwes-qa-11-blower-door-test-verifier-recorded-fl": "NWES-QA 1.1 Blower Door Test: Verifier Recorded Flow",
            "nwes-qa-12-ach50pa": "NWES-QA 1.2 ACH@50Pa",
            "nwes-qa-20-duct-total-leakage-test-flow": "NWES-QA 2.0 Duct Total Leakage Test: Flow",
            "nwes-qa-30-duct-leakage-to-outside-test-flow": "NWES-QA 3.0 Duct Leakage to Outside Test: Flow",
            "nwes-qa-31-duct-leakage-to-outside-test-ptcs-rec": "NWES-QA 3.1 Duct Leakage to Outside Test: PTCS Recorded Flow",
            "nwes-qa-32-ptcs-sticker": "NWES-QA 3.2 PTCS Sticker?",
            "nwes-qa-40-caz-test-location": 'NWES-QA 4.0 CAZ Test: Location. If not applicable, please enter "N/A".',
            "nwes-qa-41-caz-test-change-in-pressure": 'NWES-QA 4.1 CAZ Test: Change in Pressure. If not applicable, please enter "0".',
            "nwes-qa-42-caz-test-windy-day": "NWES-QA 4.2 CAZ Test: Windy Day?",
            "nwes-qa-50-room-pressure-test-wrt-body": "NWES-QA 5.0 Room Pressure Test WRT Body",
            "nwes-qa-60-ventilation-type-supplyexhaustbala": "NWES-QA 6.0 Ventilation: Type (Supply/Exhaust/Balanced/HRV/ERV)",
            "nwes-qa-61-ventilation-exhaust-cfm-measured": "NWES-QA 6.1 Ventilation: Exhaust CFM (Measured)",
            "nwes-qa-62-ventilation-supply-cfm-measured": "NWES-QA 6.2 Ventilation: Supply CFM (Measured)",
            "nwes-qa-63-ventilation-system-meets-622": "NWES-QA 6.3 Ventilation: System meets 62.2?",
            "nwes-qa-70-furnace-manufacturer": "NWES-QA 7.0 Furnace: Manufacturer",
            "nwes-qa-71-furnace-model-number": "NWES-QA 7.1 Furnace: Model Number",
            "nwes-qa-72-furnace-afue": "NWES-QA 7.2 Furnace: AFUE",
            "nwes-qa-73-furnace-fan-motor-type": "NWES-QA 7.3 Furnace: Fan Motor Type",
            "nwes-qa-80-heat-pump-manufacturer": "NWES-QA 8.0 Heat Pump: Manufacturer",
            "nwes-qa-81-heat-pump-model-number": "NWES-QA 8.1 Heat Pump: Model Number",
            "nwes-qa-82-heat-pump-seer-seasonal-energy-effic": "NWES-QA 8.2 Heat Pump: SEER (seasonal energy efficiency ratio)",
            "nwes-qa-83-heat-pump-hspf-heating-seasonal-per": "NWES-QA 8.3 Heat Pump: HSPF - heating seasonal performance factor",
            "nwes-qa-84-heat-pump-corrected-flow": "NWES-QA 8.4 Heat Pump: Corrected Flow",
            "nwes-qa-90-water-heater-manufacturer": "NWES-QA 9.0 Water Heater: Manufacturer",
            "nwes-qa-91-water-heater-model-number": "NWES-QA 9.1 Water Heater: Model Number",
            "nwes-qa-92-water-heater-ef-energy-factor": "NWES-QA 9.2 Water Heater: EF (energy factor)",
            "nwes-qa-93-water-heater-hp-tier-1-or-tier-2": "NWES-QA 9.3 Water Heater: HP: Tier 1 or Tier 2",
            "nwes-qa-100-air-conditioner-manufacturer": "NWES-QA 10.0 Air Conditioner: Manufacturer",
            "nwes-qa-101-air-conditioner-model-number": "NWES-QA 10.1 Air Conditioner: Model Number",
            "nwes-qa-102-air-conditioner-seer-rating": "NWES-QA 10.2 Air Conditioner: SEER Rating",
            "nwes-qa-110-ductless-heat-pump-manufacturer": "NWES-QA 11.0 Ductless Heat Pump: Manufacturer",
            "nwes-qa-111-ductless-heat-pump-model-number": "NWES-QA 11.1 Ductless Heat Pump: Model Number",
            "nwes-qa-120-zonal-gas-manufacturer": "NWES-QA 12.0 Zonal Gas: Manufacturer",
            "nwes-qa-121-zonal-gas-model-number": "NWES-QA 12.1 Zonal Gas: Model Number",
            "nwes-qa-130-zonal-electric-manufacturer": "NWES-QA 13.0 Zonal Electric: Manufacturer",
            "nwes-qa-131-zonal-gas-model-number": "NWES-QA 13.1 Zonal Gas: Model Number",
            "nwes-qa-140-hydronic-manufacturer": "NWES-QA 14.0 Hydronic: Manufacturer",
            "nwes-qa-141-hydronic-model-number": "NWES-QA 14.1 Hydronic: Model Number",
            "nwes-qa-150-ducts-manufacturer": "NWES-QA 15.0 Ducts: Manufacturer",
            "nwes-qa-151-ducts-model-number": "NWES-QA 15.1 Ducts: Model Number",
            "nwes-qa-160-insulation-r-values-floor": "NWES-QA 16.0 Insulation R-Values: Floor",
            "nwes-qa-161-insulation-r-values-walls": "NWES-QA 16.1 Insulation R-Values: Walls",
            "nwes-qa-162-insulation-r-values-slab": "NWES-QA 16.2 Insulation R-Values: Slab",
            "nwes-qa-163-insulation-r-values-rafter-vault": "NWES-QA 16.3 Insulation R-Values: Rafter Vault",
            "nwes-qa-164-insulation-r-values-scissor-truss": "NWES-QA 16.4 Insulation R-Values: Scissor Truss",
            "nwes-qa-165-insulation-r-values-ceiling": "NWES-QA 16.5 Insulation R-Values: Ceiling",
            "nwes-qa-166-insulation-r-values-below-grade-wall": "NWES-QA 16.6 Insulation R-Values: Below Grade Walls",
            "nwes-qa-167-insulation-tec-met": "NWES-QA 16.7 Insulation: TEC Met?",
            "nwes-qa-170-home-size-number-of-bedrooms": "NWES-QA 17.0 Home Size: Number of Bedrooms",
            "nwes-qa-171-home-size-home-volume": "NWES-QA 17.1 Home Size: Home Volume",
            "nwes-qa-172-home-size-square-footage": "NWES-QA 17.2 Home Size: Square Footage",
            "nwes-qa-173-home-size-meets-benchmark": "NWES-QA 17.3 Home Size: Meets Benchmark?",
            "nwes-qa-174-home-size-window-to-floor-area": "NWES-QA 17.4 Home Size: Window to Floor Area",
            "nwes-qa-180-appliances-energy-star": "NWES-QA 18.0 Appliances: ENERGY STAR®?",
            "nwes-qa-190-lighting-percentage-of-efficiency-li": "NWES-QA 19.0 Lighting: Percentage of Efficiency Light Sources",
            "nwes-qa-200-bath-fan-airflows-master-bath-measu": "NWES-QA 20.0 Bath Fan Airflows: Master Bath (measured)",
            "nwes-qa-201-bath-fan-airflows-upstairs-guest-bat": "NWES-QA 20.1 Bath Fan Airflows: Upstairs Guest Bath (measured)",
            "nwes-qa-202-bath-fan-airflows-upstairs-guest-bat": "NWES-QA 20.2 Bath Fan Airflows: Upstairs Guest Bath 2 (measured)",
            "nwes-qa-203-bath-fan-airflows-downstairs-guest-b": "NWES-QA 20.3 Bath Fan Airflows: Downstairs Guest Bath (measured)",
            "nwes-qa-204-bath-fan-airflows-downstairs-guest-b": "NWES-QA 20.4 Bath Fan Airflows: Downstairs Guest Bath 2 (measured)",
            "nwes-qa-205-bath-fan-airflows-laundry-room-meas": "NWES-QA 20.5 Bath Fan Airflows: Laundry Room (measured)",
            "nwes-qa-210-room-airflow-measurements-do-the-roo": "NWES-QA 21.0 Room Airflow Measurements: Do the room airflow measurements meet HVAC contractor checklist?",
            "nwes-qa-220-miscellaneous-window-u-value-meets-b": "NWES-QA 22.0 Miscellaneous: Window U-Value Meets BOP Requirement?",
            "nwes-qa-221-miscellaneous-shower-flow-rate": "NWES-QA 22.1 Miscellaneous: Shower Flow Rate",
            "nwes-qa-222-miscellaneous-bathroom-sink-flow-rat": "NWES-QA 22.2 Miscellaneous: Bathroom Sink Flow Rate",
            "nwes-qa-223-miscellaneous-kitchen-sink-flow-rate": "NWES-QA 22.3 Miscellaneous: Kitchen Sink Flow Rate",
            "nwes-qa-224-miscellaneous-energy-star-label-pre": "NWES-QA 22.4 Miscellaneous: ENERGY STAR® Label Present?",
            "nwes-qa-225-miscellaneous-remediation-log": "NWES-QA 22.5 Miscellaneous: Remediation Log",
            "nwes-qa-230-thermal-enclosure": "NWES-QA 23.0 Thermal Enclosure",
            "nwes-qa-231-water-management": "NWES-QA 23.1 Water Management",
            "nwes-qa-232-hvac-verifier": "NWES-QA 23.2 HVAC (Verifier)",
            "nwes-qa-233-hvac-contractor": "NWES-QA 23.3 HVAC (Contractor)",
            "nwes-qa-240-hvac-contractor-partner-name": "NWES-QA 24.0 HVAC Contractor Partner Name",
            "nwes-qa-241-hvac-contractor-is-qualified-as-per-n": "NWES-QA 24.1 HVAC contractor is qualified as per Northwest Approved HVAC Contractor List",
            "nwes-qa-242-performance-tester-is-ptcs-qualified": "NWES-QA 24.2 Performance Tester is PTCS Qualified?",
            "nwes-qa-243-notes": "NWES-QA 24.3 Notes",
            "nwes-qa-250-furnace-total-external-static-pressur": "NWES-QA 25.0 Furnace Total External Static Pressure measurements",
        },
    }
    descriptions = {
        "rater": {
            "nwes-qa-40-caz-test-location": """If not applicable, please enter "N/A".""",
            "nwes-qa-41-caz-test-change-in-pressure": """If not applicable, please enter "0".""",
            "nwes-qa-50-room-pressure-test-wrt-body": """Enter data as a comma-separated list of room/value pairs (e.g. Downstairs_NE 20.2, Downstairs_SW 18.6, Upstairs_SE 15.3, Upstairs_NW 17.8)""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "nwes-qa-32-ptcs-sticker",
                "nwes-qa-63-ventilation-system-meets-622",
                "nwes-qa-167-insulation-tec-met",
                "nwes-qa-173-home-size-meets-benchmark",
                "nwes-qa-180-appliances-energy-star",
                "nwes-qa-210-room-airflow-measurements-do-the-roo",
                "nwes-qa-220-miscellaneous-window-u-value-meets-b",
                "nwes-qa-224-miscellaneous-energy-star-label-pre",
                "nwes-qa-230-thermal-enclosure",
                "nwes-qa-231-water-management",
                "nwes-qa-232-hvac-verifier",
                "nwes-qa-233-hvac-contractor",
                "nwes-qa-241-hvac-contractor-is-qualified-as-per-n",
                "nwes-qa-242-performance-tester-is-ptcs-qualified",
            ],
            (
                "Yes",
                "No",
                "N/A",
            ): [
                "nwes-qa-42-caz-test-windy-day",
            ],
            (
                "Exhaust only",
                "Supply only",
                "Balanced: Supply with interlocked exhaust fan",
                "Balanced: Supply with exhaust fan on a timer",
                "Balanced: Spot ERV or HRV",
                "Standalone HRV",
                "Standalone ERV",
                "Conjoined HRV/ERV with central heating system",
            ): [
                "nwes-qa-60-ventilation-type-supplyexhaustbala",
            ],
            (
                "Permanent Split Capacitor (PSC)",
                "Electronically Commutated Motor (ECM)",
                "Variable Frequency Drive (VFD)",
            ): [
                "nwes-qa-73-furnace-fan-motor-type",
            ],
            (
                "Tier 1",
                "Tier 2",
                "N/A",
            ): [
                "nwes-qa-93-water-heater-hp-tier-1-or-tier-2",
            ],
            (
                "Pass",
                "Fail",
            ): [
                "nwes-qa-174-home-size-window-to-floor-area",
            ],
        },
    }
    instrument_types = {
        "float": [
            "nwes-qa-10-blower-door-test-flow",
            "nwes-qa-11-blower-door-test-verifier-recorded-fl",
            "nwes-qa-12-ach50pa",
            "nwes-qa-20-duct-total-leakage-test-flow",
            "nwes-qa-30-duct-leakage-to-outside-test-flow",
            "nwes-qa-31-duct-leakage-to-outside-test-ptcs-rec",
            "nwes-qa-41-caz-test-change-in-pressure",
            "nwes-qa-61-ventilation-exhaust-cfm-measured",
            "nwes-qa-62-ventilation-supply-cfm-measured",
            "nwes-qa-82-heat-pump-seer-seasonal-energy-effic",
            "nwes-qa-83-heat-pump-hspf-heating-seasonal-per",
            "nwes-qa-84-heat-pump-corrected-flow",
            "nwes-qa-92-water-heater-ef-energy-factor",
            "nwes-qa-171-home-size-home-volume",
            "nwes-qa-172-home-size-square-footage",
            "nwes-qa-190-lighting-percentage-of-efficiency-li",
            "nwes-qa-200-bath-fan-airflows-master-bath-measu",
            "nwes-qa-201-bath-fan-airflows-upstairs-guest-bat",
            "nwes-qa-202-bath-fan-airflows-upstairs-guest-bat",
            "nwes-qa-203-bath-fan-airflows-downstairs-guest-b",
            "nwes-qa-204-bath-fan-airflows-downstairs-guest-b",
            "nwes-qa-205-bath-fan-airflows-laundry-room-meas",
            "nwes-qa-221-miscellaneous-shower-flow-rate",
            "nwes-qa-222-miscellaneous-bathroom-sink-flow-rat",
            "nwes-qa-223-miscellaneous-kitchen-sink-flow-rate",
        ],
        "integer": [
            "nwes-qa-170-home-size-number-of-bedrooms",
        ],
    }
    suggested_response_flags = {
        "rater": {
            "nwes-qa-32-ptcs-sticker": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-42-caz-test-windy-day": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-63-ventilation-system-meets-622": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-167-insulation-tec-met": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-173-home-size-meets-benchmark": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-174-home-size-window-to-floor-area": {
                "Fail": {
                    "comment_required": True,
                },
            },
            "nwes-qa-180-appliances-energy-star": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-210-room-airflow-measurements-do-the-roo": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-220-miscellaneous-window-u-value-meets-b": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-224-miscellaneous-energy-star-label-pre": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-230-thermal-enclosure": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-231-water-management": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-232-hvac-verifier": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-233-hvac-contractor": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-241-hvac-contractor-is-qualified-as-per-n": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-qa-242-performance-tester-is-ptcs-qualified": {
                "No": {
                    "comment_required": True,
                },
            },
        },
    }
