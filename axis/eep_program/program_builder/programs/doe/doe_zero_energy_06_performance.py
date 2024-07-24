__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


import logging
import datetime

from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)


class DoeZeroEnergyReadyRev05PerformancePath(ProgramBuilder):
    name = "DOE Zero Energy Ready (Rev. 05) - Performance Path"
    slug = "doe-zero-energy-ready-rev-05-performance-path"
    owner = "us-doe"
    is_qa_program = False
    opt_in = True
    workflow_default_settings = {}
    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0
    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0
    enable_standard_disclosure = True
    require_floorplan_approval = False
    require_input_data = True
    require_rem_data = True
    require_model_file = True
    require_ekotrope_data = False
    require_rater_of_record = True
    manual_transition_on_certify = True
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = True
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2019, 4, 21)
    start_date = datetime.date(2019, 4, 21)

    comment = """<font size="2">

<p><h4>DOE Zero Energy Ready (Rev. 05) - Performance Path</h4></p>

<ins><b>   Program Information</b></ins>
<p>    For more information about the DOE Zero Energy Ready program, <a href="http://energy.gov/eere/buildings/zero-energy-ready-home" target="_blank">click here.</a></p>

<ins><b>   Program Requirements</b></ins>
<p>   For detailed program requirements, <a href="http://energy.gov/eere/buildings/guidelines-participating-doe-zero-energy-ready-home" target="_blank">click here.</a></p>

</font>"""

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": False,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "energy-star-for-homes-baseline-certified-under-e-0",
                "envelope-fenestration-shall-meet-or-exceed-energ-0",
                "envelope-ceiling-wall-floor-and-slab-insulatio-0",
                "duct-system-duct-distribution-systems-located-wi-0",
                "water-efficiency-hot-water-delivery-systems-shal-0",
                "lighting-appliances-all-installed-refrigerators-0",
                "lighting-appliances-80-of-lighting-fixtures-ar-0",
                "lighting-appliances-all-installed-bathroom-vent-0",
                "indoor-air-quality-certified-under-epa-indoor-ai-0",
                "renewable-ready-provisions-of-the-doe-zero-energ-0",
                "compliance-the-home-has-been-built-and-verified--0",
            ],
        },
    }
    texts = {
        "rater": {
            "energy-star-for-homes-baseline-certified-under-e-0": "ENERGY STAR for Homes Baseline: Certified under ENERGY STAR Qualified Homes Version 3 or 3.1",
            "envelope-fenestration-shall-meet-or-exceed-energ-0": "Envelope: Fenestration shall meet or exceed ENERGY STAR requirements",
            "envelope-ceiling-wall-floor-and-slab-insulatio-0": "Envelope: Ceiling, wall, floor, and slab insulation shall meet or exceed 2012 or 2015 IECC levels",
            "duct-system-duct-distribution-systems-located-wi-0": "Duct System: Duct distribution systems located within the home’s thermal and air barrier boundary or optimized to achieve comparable performance",
            "water-efficiency-hot-water-delivery-systems-shal-0": "Water Efficiency: Hot water delivery systems shall meet efficient design requirements",
            "lighting-appliances-all-installed-refrigerators-0": "Lighting & Appliances: All installed refrigerators, dishwashers, and clothes washers are ENERGY STAR qualified",
            "lighting-appliances-80-of-lighting-fixtures-ar-0": "Lighting & Appliances: 80% of lighting fixtures are ENERGY STAR qualified or ENERGY STAR lamps (bulbs) in minimum 80% of sockets",
            "lighting-appliances-all-installed-bathroom-vent-0": "Lighting & Appliances: All installed bathroom ventilation and ceiling fans are ENERGY STAR qualifie",
            "indoor-air-quality-certified-under-epa-indoor-ai-0": "Indoor Air Quality: Certified under EPA Indoor airPLUS",
            "renewable-ready-provisions-of-the-doe-zero-energ-0": "Renewable Ready: Provisions of the DOE Zero Energy Ready Home PV-Ready Checklist are Completed; (Solar Hot Water Ready provisions are encouraged but not required)",
            "compliance-the-home-has-been-built-and-verified--0": "Compliance: The home has been built and verified to meet or exceed the rigor of the DOE Zero Energy Ready Home Target Home specifications, as shown in Exhibit 2 of the DOE Zero Energy Ready Home National Program Requirements",
        },
    }
    descriptions = {
        "rater": {
            "energy-star-for-homes-baseline-certified-under-e-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "envelope-fenestration-shall-meet-or-exceed-energ-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "envelope-ceiling-wall-floor-and-slab-insulatio-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "duct-system-duct-distribution-systems-located-wi-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "water-efficiency-hot-water-delivery-systems-shal-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-all-installed-refrigerators-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-80-of-lighting-fixtures-ar-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-all-installed-bathroom-vent-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "indoor-air-quality-certified-under-epa-indoor-ai-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "renewable-ready-provisions-of-the-doe-zero-energ-0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "compliance-the-home-has-been-built-and-verified--0": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "energy-star-for-homes-baseline-certified-under-e-0",
                "envelope-fenestration-shall-meet-or-exceed-energ-0",
                "envelope-ceiling-wall-floor-and-slab-insulatio-0",
                "duct-system-duct-distribution-systems-located-wi-0",
                "water-efficiency-hot-water-delivery-systems-shal-0",
                "lighting-appliances-all-installed-refrigerators-0",
                "lighting-appliances-80-of-lighting-fixtures-ar-0",
                "lighting-appliances-all-installed-bathroom-vent-0",
                "indoor-air-quality-certified-under-epa-indoor-ai-0",
                "renewable-ready-provisions-of-the-doe-zero-energ-0",
                "compliance-the-home-has-been-built-and-verified--0",
            ],
        },
    }
