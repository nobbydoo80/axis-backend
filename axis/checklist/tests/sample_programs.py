"""sample_programs.py - axis"""

__author__ = "Steven K"
__date__ = "4/21/22 10:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import enum
import logging
from axis.eep_program.program_builder import ProgramBuilder

from axis.customer_eto.eep_programs.eto_2019 import val
from axis.remrate_data import strings as rem_strings

log = logging.getLogger(__name__)


class YesNo(enum.Enum):
    YES = "yes"
    NO = "no"


class SuperSimpleProgramDefinition(ProgramBuilder):
    slug = "program"
    name = "Some Program"
    owner = "eep"

    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    manual_transition_on_certify = True

    require_home_relationships = {
        "builder": True,
        "rater": True,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": False,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
    }

    measures = {
        "rater": {
            "default": [
                "question-1",
                "question-2",
                "question-3",
            ],
        }
    }
    texts = {
        "default": {
            "question-1": "Why is the sky blue",
            "question-2": "Give me a number",
            "question-3": "Do you like mornings",
        },
    }
    instrument_types = {
        "float": [
            "question-2",
        ],
    }
    suggested_responses = {
        "default": {
            YesNo: ["question-3"],
        },
    }
    instrument_conditions = {"default": {}, "rater": {}}


class InstrumentConditionCaseProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "condition-case"
    name = "Condition Cases"
    owner = "eto"

    measures = {
        "rater": {
            "default": [
                "basic",
                "basic-alt",
                "condition-basic",
                "condition-rem-basic",
                "condition-rem",
                "condition-zero",
                "condition-ac",
            ],
        }
    }
    texts = {
        "default": {
            "basic": "Way to get to Conditional",
            "basic-alt": "Alt Way to get to Conditional",
            "condition-basic": "Conditional Based on Criteria",
            "condition-rem-basic": "Conditional Based on Single REM Criteria",
            "condition-rem": "Conditional Based on Multiple REM Criteria",
            "condition-zero": "Conditional with a Zero Value",
            "condition-ac": "Conditional that tests 'one' in.",
        },
    }
    instrument_types = {}
    suggested_responses = {
        "default": {
            ("No", "C1", "C2"): ["basic"],
            ("Nah", "CA"): ["basic-alt"],
            ("A", "B", "C"): ["condition-basic"],
            ("D", "E"): ["condition-rem-basic"],
            ("F", "G", "H"): ["condition-rem"],
        },
    }
    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "basic": {("one", ("C1", "C2")): ["condition-basic"]},
                "basic-alt": {
                    "CA": ["condition-basic"],
                },
            },
            "rem": {
                "floorplan.remrate_target.number_of_runs": {
                    (">", 2): [
                        "condition-rem-basic",
                    ],
                },
                "floorplan.remrate_target.export_type": {
                    0: [
                        "condition-zero",
                    ],
                    13: [
                        "condition-rem",
                    ],
                },
                "floorplan.remrate_target.version": {
                    "13.0": [
                        "condition-rem",
                    ],
                },
                "floorplan.remrate_target.airconditioner_set.type": {
                    ("one", val(rem_strings.COOLING_TYPES, "Air conditioner")): [
                        "condition-ac",
                    ],
                },
            },
        },
    }


class OptAns(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class InstrumentANDConditionCaseProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "condition-case"
    name = "Condition AND Cases"
    owner = "eto"

    measures = {
        "rater": {
            "default": [
                "seed-a",
                "seed-b",
                "logic-and",
            ],
        }
    }
    texts = {
        "default": {
            "seed-a": "Path A: Conditional to get to logic-and",
            "seed-b": "Path B: Conditional to get to logic-and",
            "logic-and": "Logical AND.",
        },
    }
    instrument_types = {}
    suggested_responses = {
        "default": {
            YesNo: [
                "seed-a",
                "seed-b",
                "logic-and",
            ],
        },
    }
    instrument_conditions = {
        "rater": {
            "instrument": {
                "seed-a": {
                    # Note either works here
                    YesNo.YES: [
                        "logic-and",
                    ],
                    # ("one", (YesNo.YES,)): [
                    #     "logic-or",
                    # ],
                },
                "seed-b": {
                    ("one", (YesNo.YES,)): ["logic-and"],
                },
            },
        },
    }


class InstrumentORConditionCaseProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "condition-case"
    name = "Condition OR Cases"
    owner = "eto"

    measures = {
        "rater": {
            "default": [
                "seed-a",
                "seed-b",
                "logic-or",
            ],
        }
    }
    texts = {
        "default": {
            "seed-a": "Path A: Conditional Setup to get to logic-or",
            "seed-b": "Path B: Conditional Setup to get to logic-or",
            "logic-or": "Logical OR.",
        },
    }
    instrument_types = {}
    suggested_responses = {
        "default": {
            YesNo: [
                "seed-a",
                "seed-b",
                "logic-or",
            ],
        },
    }
    instrument_condition_types = {"default": {"logic-or": "one-pass"}}

    instrument_conditions = {
        "rater": {
            "instrument": {
                "seed-a": {
                    YesNo.YES: ["logic-or"],
                },
                "seed-b": {
                    YesNo.YES: ["logic-or"],
                },
            },
        },
    }


class InstrumentORDeepConditionCaseProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "condition-case"
    name = "Condition Deep OR Cases"
    owner = "eto"

    measures = {
        "rater": {
            "default": [
                "top",
                "seed-a",
                "seed-b",
                "logic-or",
            ],
        }
    }
    texts = {
        "default": {
            "top": "Top level",
            "seed-a": "Path A: Conditional Setup to get to logic-or",
            "seed-b": "Path B: Conditional Setup to get to logic-or",
            "logic-or": "Logical OR.",
        },
    }
    instrument_types = {}
    suggested_responses = {
        "default": {
            YesNo: [
                "seed-a",
                "seed-b",
                "logic-or",
            ],
            OptAns: [
                "top",
            ],
        },
    }
    instrument_condition_types = {"default": {"logic-or": "one-pass"}}

    instrument_conditions = {
        "rater": {
            "instrument": {
                "top": {OptAns.A: ["seed-a"], OptAns.B: ["seed-b"]},
                "seed-a": {
                    YesNo.YES: ["logic-or"],
                },
                "seed-b": {
                    YesNo.YES: ["logic-or"],
                },
            },
        },
    }


class SimulationResolverProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "resolver"
    name = "Simulation Resolver"
    owner = "eto"

    simulation_type = "either"

    measures = {
        "rater": {
            "default": [
                "open-question",
                "equality",
                "more-than-2-bedroom-question",
                "m2m-one-of",
                "m2m-one-of-2",
                "m2m-one-of-function",
                "m2m-qs-exists",
                "equipment-dishwasher",
                "equipment-clothes-dryer",
            ],
        }
    }
    texts = {
        "default": {
            "open-question": "Nothing really",
            "equality": "If the simulation version == VERSION we should see this",
            "more-than-2-bedroom-question": "More than 2 bedrooms ask this question",
            "m2m-one-of": "One of many should fly through?",
            "m2m-one-of-2": "One of many when only one",
            "m2m-one-of-function": "One of many a function",
            "m2m-qs-exists": "Inspecting that a qs has any member",
            "equipment-dishwasher": "Dishwasher dishwasher_consumption < 276",
            "equipment-clothes-dryer": "Dryer efficiency > 2.62",
        },
    }
    instrument_types = {}
    suggested_responses = {}
    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {},
            "simulation": {
                # Verify that when we have an equality we get asked the question
                "floorplan.simulation.version": {"VERSION": ["equality"]},
                "floorplan.simulation.bedroom_count": {
                    (">", 2): [
                        "more-than-2-bedroom-question",
                    ],
                },
                "floorplan.simulation.water_heaters.style": {
                    ("one", ("ashp", "gshp")): [
                        "m2m-one-of",
                    ],
                },
                "floorplan.simulation.hvac_distribution_systems.system_type": {
                    ("one", "forced_air"): [
                        "m2m-one-of-2",
                    ],
                },
                "floorplan.simulation.water_heaters.is_conventional_gas": {
                    ("one", True): ["m2m-one-of-function"],
                },
                "floorplan.simulation.air_source_heat_pumps": {
                    ("any", None): [
                        "m2m-qs-exists",
                    ],
                },
                "floorplan.simulation.appliances.dishwasher_consumption": {
                    ("<", 270): [
                        "equipment-dishwasher",
                    ],
                },
                "floorplan.simulation.appliances.clothes_dryer_efficiency": {
                    (">", 2.62): [
                        "equipment-clothes-dryer",
                    ],
                },
            },
        },
    }
