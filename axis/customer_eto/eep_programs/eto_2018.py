"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "08/26/2021 22:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

#
# NOTE: The original program used checklists.  This is here for tests.
#

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class Eto2018(ProgramBuilder):
    name = "Energy Trust Oregon - 2018"
    slug = "eto-2018"
    owner = "eto"
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
    require_rem_data = True
    require_model_file = True
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = True
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2018, 1, 1)
    start_date = datetime.date(2018, 1, 1)
    end_date = datetime.date(2019, 1, 1)

    comment = """Energy Trust of Oregon 2018 Program"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": True,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "is-affordable-housing",
                "is-adu",
                "builder-payment-redirected",
                "applicable-solar-incentive",
                "solar-installer-company",
                "has-battery-storage",
                "has-solar-water-heat",
                "primary-heating-equipment-type",
                "hvac-combined-or-heating-only-brand",
                "hvac-combined-or-heating-only-model-number",
                "water-heater-brand",
                "water-heater-model-number",
                "smart-thermostat-brand",
                "ceiling-r-value",
                "heat-pump-outdoor-model-number",
                "heat-pump-number-indoor-heads",
                "air-conditioning-seer13-model-number",
                "hrverv-brand",
                "hrverv-model-number",
                "refrigerator691-model-number",
                "dishwasher270-model-number",
                "showerheads15-quantity",
                "showerheads16-quantity",
                "showerheads175-quantity",
                "showerwands15-quantity",
                "heat-pump-water-heater-serial-number",
            ],
        },
    }
    texts = {
        "rater": {
            "is-affordable-housing": "Is this affordable housing?",
            "is-adu": "Is this an accessory dwelling unit (ADU)?",
            "builder-payment-redirected": "Does the Builder wish to redirect payments for both its EPS Whole Home incentive and EPS Code Transition Payment? If so, enter the contact name and payee company for the redirect.",
            "applicable-solar-incentive": "Does this home qualify as solar-ready?",
            "solar-installer-company": "If this home has Solar Electric (PV) installed, enter the name of the Solar installer company and select whether this home is receiving an Energy Trust Solar Incentive. If it is not receiving a separate Solar Incentive through the Solar Program, attach the PV Watts report.",
            "has-battery-storage": "Does this home have battery storage?",
            "has-solar-water-heat": "Does this home have Solar water heat?",
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "hvac-combined-or-heating-only-brand": "Heating Equipment Brand",
            "hvac-combined-or-heating-only-model-number": "Heating Equipment Model Number",
            "water-heater-brand": "Water Heater Brand",
            "water-heater-model-number": "Water Heater model number",
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "ceiling-r-value": "Ceiling R-value",
            "heat-pump-outdoor-model-number": "If a heat pump is installed, enter the Outdoor Unit model number.",
            "heat-pump-number-indoor-heads": "If a heat pump is installed, enter the number of indoor heads.",
            "air-conditioning-seer13-model-number": "If Air Conditioning is installed and more efficient than 13 SEER, enter the model number.",
            "hrverv-brand": "If an HRV/ERV is installed, enter the brand.",
            "hrverv-model-number": "If an HRV/ERV is installed, enter the model number.",
            "refrigerator691-model-number": "If the installed refrigerator is more efficient than the default value (kWh), enter the model number",
            "dishwasher270-model-number": "If the installed dishwasher is more efficient than the default value (kWh), enter the model number.",
            "showerheads15-quantity": "Number of 1.5 gpm Showerheads",
            "showerheads16-quantity": "Number of 1.6 gpm Showerheads",
            "showerheads175-quantity": "Number of 1.75 gpm Showerheads",
            "showerwands15-quantity": "Number of 1.5 gpm Shower wands",
            "heat-pump-water-heater-serial-number": "Heat Pump Water Heater Serial Number",
        },
    }
    descriptions = {
        "rater": {
            "heat-pump-water-heater-serial-number": """Please enter the model / serial numbers""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "is-affordable-housing",
                "is-adu",
                "builder-payment-redirected",
                "applicable-solar-incentive",
                "has-battery-storage",
                "has-solar-water-heat",
            ],
            (
                "Solar Electric (PV) WITH Energy Trust Solar Incentives",
                "Solar Electric (PV) NO Energy Trust Solar Incentive",
                "N/A",
            ): [
                "solar-installer-company",
            ],
            (
                "Gas Fireplace",
                "Gas Unit Heater",
                "Gas Furnace",
                "Gas Boiler",
                "Electric Heat Pump – Air Source Ducted",
                "Electric Heat Pump – Mini Split Non-Ducted",
                "Electric Heat Pump – Mini Split Ducted",
                "Electric Heat Pump – Ground Source",
                "Electric Resistance",
                "Other Gas",
                "Other Electric",
            ): [
                "primary-heating-equipment-type",
            ],
            (
                "Aire-Flo",
                "American Standard",
                "Bryant",
                "Carrier",
                "Coleman",
                "Daikin",
                "Fujitsu",
                "Goodman",
                "Lennox",
                "Maytag",
                "Mitsubishi",
                "Rheem",
                "Rudd",
                "Trane",
                "Other (Enter name as comment)",
            ): [
                "hvac-combined-or-heating-only-brand",
            ],
            (
                "A.O. Smith",
                "Bradford White",
                "Navian",
                "Nortiz",
                "Rheem",
                "Rinnai",
                "Rudd",
                "State",
                "Takagi",
                "Other (Enter name as comment)",
            ): [
                "water-heater-brand",
            ],
            (
                "Bryant Housewise WiFi model T6-WEM01-A",
                "Carrier Cor WiFi model T6-WEM01-A",
                "Ecobee3 (not 'lite')",
                "Ecobee4",
                "NEST Learning Thermostat",
                "NEST Thermostat E",
                "N/A",
            ): [
                "smart-thermostat-brand",
            ],
            (
                "Broan",
                "Zehnder",
                "Panasonic",
                "Lifebreath",
                "Venmar",
                "Other (Enter name as comment)",
            ): [
                "hrverv-brand",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "showerheads15-quantity",
            "showerheads16-quantity",
            "showerheads175-quantity",
            "showerwands15-quantity",
        ],
    }
    optional_measures = [
        "heat-pump-outdoor-model-number",
        "heat-pump-number-indoor-heads",
        "air-conditioning-seer13-model-number",
        "hrverv-brand",
        "hrverv-model-number",
        "refrigerator691-model-number",
        "dishwasher270-model-number",
        "showerheads15-quantity",
        "showerheads16-quantity",
        "showerheads175-quantity",
        "showerwands15-quantity",
        "heat-pump-water-heater-serial-number",
    ]
    suggested_response_flags = {
        "rater": {
            "builder-payment-redirected": {
                "Yes": {
                    "comment_required": True,
                },
            },
            "solar-installer-company": {
                "Solar Electric (PV) WITH Energy Trust Solar Incentives": {
                    "comment_required": True,
                },
                "Solar Electric (PV) NO Energy Trust Solar Incentive": {
                    "document_required": True,
                    "comment_required": True,
                },
            },
            "hvac-combined-or-heating-only-brand": {
                "Other (Enter name as comment)": {
                    "comment_required": True,
                },
            },
            "water-heater-brand": {
                "Other (Enter name as comment)": {
                    "comment_required": True,
                },
            },
            "hrverv-brand": {
                "Other (Enter name as comment)": {
                    "comment_required": True,
                },
            },
        },
    }
