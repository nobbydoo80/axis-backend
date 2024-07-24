"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class DoeZeroEnergyReadyRev05PrescriptivePat(ProgramBuilder):
    name = "DOE Zero Energy Ready (Rev. 05) - Prescriptive Path"
    slug = "doe-zero-energy-ready-rev-05-prescriptive-pat"
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
    require_input_data = False
    require_rem_data = False
    require_model_file = False
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

    visibility_date = datetime.date(2016, 1, 1)
    start_date = datetime.date(2016, 1, 1)

    comment = """<font size="2">

<p><h4>DOE Zero Energy Ready (Rev. 05) - Prescriptive Path</h4></p>

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
                "eligibility-based-on-the-homes-number-of-bedroom",
                "energy-star-for-homes-baseline-certified-under-en",
                "envelope-fenestration-shall-meet-or-exceed-energy",
                "envelope-ceiling-wall-floor-and-slab-insulatio",
                "duct-system-duct-distribution-systems-located-wit",
                "water-efficiency-hot-water-delivery-systems-shall",
                "lighting-appliances-all-installed-refrigerators",
                "lighting-appliances-80-of-lighting-fixtures-ar",
                "lighting-appliances-all-installed-bathroom-vent",
                "indoor-air-quality-certified-under-epa-indoor-air",
                "renewable-ready-provisions-of-the-doe-zero-energy",
                "compliance-the-home-has-been-built-and-verified-t",
            ],
        },
    }
    texts = {
        "rater": {
            "eligibility-based-on-the-homes-number-of-bedroom": "Eligibility: Based on the home’s number of bedrooms and its conditioned floor area (CFA), the home does not exceed the Benchmark Home Size, as defined in Exhibit 3 of the DOE Zero Energy Ready Home National Program Requirements",
            "energy-star-for-homes-baseline-certified-under-en": "ENERGY STAR for Homes Baseline: Certified under ENERGY STAR Qualified Homes Version 3 or 3.1",
            "envelope-fenestration-shall-meet-or-exceed-energy": "Envelope: Fenestration shall meet or exceed ENERGY STAR requirements",
            "envelope-ceiling-wall-floor-and-slab-insulatio": "Envelope: Ceiling, wall, floor, and slab insulation shall meet or exceed 2012 or 2015 IECC levels",
            "duct-system-duct-distribution-systems-located-wit": "Duct System: Duct distribution systems located within the home’s thermal and air barrier boundary or optimized to achieve comparable performance",
            "water-efficiency-hot-water-delivery-systems-shall": "Water Efficiency: Hot water delivery systems shall meet efficient design requirements",
            "lighting-appliances-all-installed-refrigerators": "Lighting & Appliances: All installed refrigerators, dishwashers, and clothes washers are ENERGY STAR qualified",
            "lighting-appliances-80-of-lighting-fixtures-ar": "Lighting & Appliances: 80% of lighting fixtures are ENERGY STAR qualified or ENERGY STAR lamps (bulbs) in minimum 80% of sockets",
            "lighting-appliances-all-installed-bathroom-vent": "Lighting & Appliances: All installed bathroom ventilation and ceiling fans are ENERGY STAR qualifie",
            "indoor-air-quality-certified-under-epa-indoor-air": "Indoor Air Quality: Certified under EPA Indoor airPLUS",
            "renewable-ready-provisions-of-the-doe-zero-energy": "Renewable Ready: Provisions of the DOE Zero Energy Ready Home PV-Ready Checklist are Completed; (Solar Hot Water Ready provisions are encouraged but not required)",
            "compliance-the-home-has-been-built-and-verified-t": "Compliance: The home has been built and verified to meet or exceed the rigor of the DOE Zero Energy Ready Home Target Home specifications, as shown in Exhibit 2 of the DOE Zero Energy Ready Home National Program Requirements",
        },
    }
    descriptions = {
        "rater": {
            "eligibility-based-on-the-homes-number-of-bedroom": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "energy-star-for-homes-baseline-certified-under-en": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "envelope-fenestration-shall-meet-or-exceed-energy": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "envelope-ceiling-wall-floor-and-slab-insulatio": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "duct-system-duct-distribution-systems-located-wit": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "water-efficiency-hot-water-delivery-systems-shall": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-all-installed-refrigerators": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-80-of-lighting-fixtures-ar": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "lighting-appliances-all-installed-bathroom-vent": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "indoor-air-quality-certified-under-epa-indoor-air": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "renewable-ready-provisions-of-the-doe-zero-energy": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
            "compliance-the-home-has-been-built-and-verified-t": """<a href="http://energy.gov/sites/prod/files/2015/05/f22/DOE%20Zero%20Energy%20Ready%20Home%20National%20Program%20Requirements%20Rev05%20-%20Final_0.pdf" target="_blank">Click here</a> to download the DOE Zero Energy Ready Home National Program Requirements.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "eligibility-based-on-the-homes-number-of-bedroom",
                "energy-star-for-homes-baseline-certified-under-en",
                "envelope-fenestration-shall-meet-or-exceed-energy",
                "envelope-ceiling-wall-floor-and-slab-insulatio",
                "duct-system-duct-distribution-systems-located-wit",
                "water-efficiency-hot-water-delivery-systems-shall",
                "lighting-appliances-all-installed-refrigerators",
                "lighting-appliances-80-of-lighting-fixtures-ar",
                "lighting-appliances-all-installed-bathroom-vent",
                "indoor-air-quality-certified-under-epa-indoor-air",
                "renewable-ready-provisions-of-the-doe-zero-energy",
                "compliance-the-home-has-been-built-and-verified-t",
            ],
        },
    }
