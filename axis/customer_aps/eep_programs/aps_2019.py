"""ETO 2019 checklist builder"""


import logging
from datetime import date
from decimal import Decimal


__author__ = "Steven Klass"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.eep_program.program_builder.base import ProgramCloner
from axis.eep_program.program_builder import utils

log = logging.getLogger(__name__)


class Aps2019(ProgramCloner):
    base_program = "aps-energy-star-v3-2018"
    convert_to_collection = True

    name = "APS 2019 Program"

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    rules = [
        utils.StringReplace("*", "2018", "2019"),
    ]

    manual_transition_on_certify = False
    require_home_relationships = {
        "builder": True,
        "utility": True,
        "provider": True,
        "hvac": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "utility": False,
        "provider": True,
        "hvac": False,
        "qa": False,
    }
    visibility_date = date(year=2018, month=11, day=1)
    start_date = date(year=2018, month=10, day=1)
    close_date = date(year=2019, month=11, day=1)
    submit_date = date(year=2019, month=11, day=15)
    end_date = date(year=2020, month=1, day=1)
    builder_incentive_dollar_value = Decimal("200.00")

    hers_range = (0, 100)

    exclude_measures = [
        "cc-r-11-has-a-completed-energy-star-version-3-hv",
        "cc-r-12-has-an-energy-star-version-3-hvac-system",
        "cc-r-13-has-a-completed-energy-star-version-3-wa",
        "aps-smart-thermostat",
        "hvac-r-28-fd1-measured-dominant-duct-leakage-pre",
        "hvac-r-28-fd2-measured-pressure-in-each-bedroom",
        "hvac-r-41-fd1-total-measured-duct-leakage-value",
        "hvac-r-42-fd1-measured-duct-leakage-values-to",
        "te-r-11-prescriptive-path-fenestration-shall-mee",
        "te-r-12-performance-path-fenestration-shall-meet",
        "te-r-211-ceiling-wall-floor-and-slab-insulat",
        "te-r-212-achieve-133-of-the-total-ua-result",
        "te-r-22-all-ceiling-wall-floor-and-slab-insul",
        "te-r-311-walls-behind-showers-and-tubs",
        "te-r-312-walls-behind-fireplaces",
        "te-r-313-attic-knee-walls",
        "te-r-314-skylight-shaft-walls",
        "te-r-315-wall-adjoining-porch-roof",
        "te-r-316-staircase-walls",
        "te-r-317-double-walls",
        "te-r-318-garage-rim-band-joist-adjoining-con",
        "te-r-319-all-other-exterior-walls",
        "te-r-321-floor-above-garage",
        "te-r-322-cantilevered-floor",
        "te-r-323-floor-above-unconditioned-basement-or",
        "te-r-331-dropped-ceiling-soffit-below-uncond",
        "te-r-332-all-other-ceilings",
        "te-r-41-for-insulated-ceilings-with-attic-space",
        "te-r-42-for-slabs-on-grade-in-cz-4-and-higher-1",
        "te-r-43-insulation-beneath-attic-platforms-eg",
        "te-r-441-reduced-thermal-bridging-at-above-grade",
        "te-r-442-structural-insulated-panels-sips-or",
        "te-r-443-insulated-concrete-forms-icfs-or-s",
        "te-r-444-double-wall-framing-or-see-next-ques",
        "te-r-445a-all-corners-insulated-r-6-to-edge",
        "te-r-445b-all-headers-above-windows-doors-insu",
        "te-r-445c-framing-limited-at-all-windows-doors",
        "te-r-445d-all-interior-exterior-wall-intersect",
        "te-r-445e-minimum-stud-spacing-of-16-in-oc-fo",
        "te-r-5-fd1-measured-blower-door-value",
        "te-r-511-duct-flue-shaft",
        "te-r-512-plumbing-piping",
        "te-r-513-electrical-wiring",
        "te-r-514-bathroom-and-kitchen-exhaust-fans",
        "te-r-515-recessed-lighting-fixtures-adjacent-to",
        "te-r-516-light-tubes-adjacent-to-unconditioned-s",
        "te-r-521-all-sill-plates-adjacent-to-conditioned",
        "te-r-522-at-top-of-walls-adjoining-unconditione",
        "te-r-523-drywall-sealed-to-top-plate-at-all-unc",
        "te-r-524-rough-opening-around-windows-exterior",
        "te-r-525-marriage-joints-between-modular-home-mo",
        "te-r-526-all-seams-between-structural-insulated",
        "te-r-527-in-multi-family-buildings-the-gap-bet",
        "te-r-531-doors-adjacent-to-unconditioned-space",
        "te-r-532-attic-access-panels-and-drop-down-stair",
        "te-r-533-whole-house-fans-equipped-with-a-durabl",
        "aps-permit-date",
        "aps-ev-installed",
    ]

    instruments = []
    descriptions = {}
    suggested_responses = {}
    suggested_response_flags = {}
    instrument_types = {}
    instrument_conditions = {}
    optional_measures = []
    instrument_response_policies = {}
