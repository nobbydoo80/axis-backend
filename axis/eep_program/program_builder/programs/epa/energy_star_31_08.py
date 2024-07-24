__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


import logging

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime

log = logging.getLogger(__name__)


class EnergyStarVersion31Rev08(ProgramBuilder):
    name = "ENERGY STAR® Version 3.1 (Rev. 08)"
    slug = "energy-star-version-31-rev-08"
    owner = "us-epa"
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
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = True
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2019, 4, 21)
    start_date = datetime.date(2019, 4, 21)
    close_warning = ""
    close_date = datetime.date(2021, 11, 1)
    submit_date = datetime.date(2021, 11, 1)
    submit_warning = ""
    end_date = datetime.date(2021, 11, 1)

    comment = """<font size="2">

<p><h4>ENERGY STAR® Version 3.1 (Rev. 08)</h4></p>

<ins><b>Rationale for Version 3.1</b></ins>
<p>Version 3.1 of the ENERGY STAR Certified Homes National Program Requirements has been developed for homes in states that have adopted the 2012, or equivalent. The purpose of this new version is to ensure that the ENERGY STAR certified homes program will continue to deliver meaningful savings relative to non-certified homes in states with this more rigorous code.</p>

<ins><b>Overview of Version 3.1</b></ins>
<p>Version 3 of the program requirements is defined by two key components – an efficiency target and four inspection checklists - and Version 3.1 maintains this structure.</p>
<p>In Version 3.1, the efficiency target has been made more rigorous, designed to save on average 15% or more relative to the 2012 IECC. Key changes include lower infiltration values, better windows & doors, more efficiency HVAC equipment, the air handler and ducts in conditioned space, and more efficient lighting. Note that these core efficiency features are not mandatory for every certified homes. Instead, the use of these more efficient features are used to determine the ENERGY STAR HERS index target.</p>

<p>For example, a home would not be required to locate the air handler and ducts within conditioned space but, if this were not done, other upgrades would need to be selected to meet the ENERGY STAR HERS index target.</p>

<p>While the efficiency target has been made more rigorous in Version 3.1, the mandatory measures contained in the Rater Design Review Checklist, Rater Field Checklist, HVAC Design Report, HVAC Commissioning Checklist, and Water Management System Builder Requirements in Version 3 are identical in Version 3.1.</p>

<p>EPA believes that this more rigorous efficiency target is achievable using ‘off-the-shelf’ technologies, is cost-effective, and is already being achieved by some partners.</p>

<ins><b>Program Information</b></ins>
<p> For more information about the ENERGY STAR Version 3.1 program, <a href="https://www.energystar.gov/index.cfm?c=bldrs_lenders_raters.nh_v3_1" target="_blank">click here.</a></p>

<ins><b>Program Requirements</b></ins>
<p>For detailed program requirements, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/ES%20NPR%203.1%20v13%202015-12-03_clean_508.pdf?fecc-6293" target="_blank">click here.</a></p>

<ins><b>Inspection Checklists</b></ins>
<p>For fillable PDF Rater checklists, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/Rater_Checklists.pdf?8870-f020" target="_blank">click here.</a></p>
<p>For the fillable PDF HVAC Design Report checklist, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/HVAC_Design_Report_v100_2015-011-20_clean_fillable.pdf?2233-1ff7" target="_blank">click here.</a></p>
<p>For the fillable PDF HVAC Commissioning checklist, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/HVAC_Commissioning_Checklist_v99_nohighlight_2015-09-15_clean_fillable.pdf?4bd7-9078" target="_blank">click here.</a></p>
<p>For the Water Management System builder requirements, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/water_mgmt_sys_bldr_req.pdf?ec16-33ed" target="_blank">click here.</a></p>

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
                "for-this-home-upload-the-following-completed-ener",
                "this-home-complies-with-the-energy-star-version-3",
            ],
        },
    }
    texts = {
        "rater": {
            "for-this-home-upload-the-following-completed-ener": "For this home, upload the following completed ENERGY STAR® Version 3/3.1 (Rev. 08) documents: Rater Design Review Checklist, Rater Field Checklist, HVAC Design Report, and HVAC Commissioning Checklist.",
            "this-home-complies-with-the-energy-star-version-3": "This home complies with the ENERGY STAR® Version 3/3.1 (Rev. 08) mandatory Water Management System builder requirements.",
        },
    }
    descriptions = {
        "rater": {
            "for-this-home-upload-the-following-completed-ener": """<a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/Rater_Checklists.pdf?8870-f020" target="_blank">Click here</a> to view or download a fillable PDF version of the ENERGY STAR® Version 3/3.1 (Rev. 08) Rater checklists.""",
            "this-home-complies-with-the-energy-star-version-3": """<a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/water_mgmt_sys_bldr_req.pdf?ec16-33ed" target="_blank">Click here</a> to view or download a PDF version of the ENERGY STAR® Version 3/3.1 (Rev. 08) Water Management System builder requirements.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "for-this-home-upload-the-following-completed-ener",
            ],
            (
                "Not Applicable (comment required)",
                "Builder Verified",
            ): [
                "this-home-complies-with-the-energy-star-version-3",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "for-this-home-upload-the-following-completed-ener": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
            "this-home-complies-with-the-energy-star-version-3": {
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
