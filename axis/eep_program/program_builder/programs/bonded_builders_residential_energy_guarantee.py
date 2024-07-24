"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/28/2022 17:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class BondedBuildersResidentialEnergyGuarantee(ProgramBuilder):
    name = "Bonded Builders Residential Energy Guarantee"
    slug = "bonded-builders-residential-energy-guarantee"
    owner = "eep-bonded-builders-warranty-group"
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
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = False
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2014, 9, 16)
    start_date = datetime.date(2014, 9, 16)

    comment = """<p><b>Don’t just say your homes are energy efficient…</b></P>

<p><b>Guarantee it with a Residential Energy Guarantee from Bonded Builders Warranty Group</b><p>

<p><b><em>The RESIDENTIAL ENERGY GUARANTEE® from Bonded Builders Warranty Group</em></b></p>

<p>How it works:</p>

<ul>
   <li> You build a new home and have its energy performance rated and certified according to one of the industry standard programs such as HERS®, Energy Star, LEED or National Green Building Standard. </li>
   <li> At closing, you enroll the home in our Residential Energy Guarantee program. We’ll handle all the paperwork and communication with your homebuyer so you won’t have to. </li>
   <li> At the end of each year*, if the homebuyer’s actual energy usage (gas and electric) exceeds the projected usage listed on the HERS certificate by more than 15%, we’ll reimburse the homeowner for the cost of the overage. </li>

*Guarantee available for terms of 2, 3 or 5 years.</ul>

<p><em>For more information, <a href="http://bondedbuilders.com/builders/products/residential-energy-guarantee" >click here.</a>    </em></p>"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": True,
        "provider": False,
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
                "bbwg-11-enrollment-date",
                "bbwg-12-builder-account-name",
                "bbwg-13-bbwg-member",
                "bbwg-14-builder-contact-name",
                "bbwg-15-builder-contact-number",
                "bbwg-21-closing-date-of-the-home",
                "bbwg-22-homeowners-name",
                "bbwg-23-was-a-pool-included-in-construction",
                "bbwg-24-homeowner-email-address-preferred-green",
                "bbwg-25-homeowner-phone-number",
            ],
        },
    }
    texts = {
        "rater": {
            "bbwg-11-enrollment-date": "Enrollment Date",
            "bbwg-12-builder-account-name": "Builder Account Name",
            "bbwg-13-bbwg-member": "BBWG Member #",
            "bbwg-14-builder-contact-name": "Builder Contact Name",
            "bbwg-15-builder-contact-number": "Builder Contact Number",
            "bbwg-21-closing-date-of-the-home": "Closing Date of the Home",
            "bbwg-22-homeowners-name": "Homeowner(s) Name",
            "bbwg-23-was-a-pool-included-in-construction": "Was a Pool included in Construction?",
            "bbwg-24-homeowner-email-address-preferred-green": "Homeowner Email Address (Preferred ‘Green’ communication method if available)",
            "bbwg-25-homeowner-phone-number": "Homeowner Phone Number",
        },
    }
    descriptions = {
        "rater": {},
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "bbwg-23-was-a-pool-included-in-construction",
            ],
        },
    }
    instrument_types = {
        "date": [
            "bbwg-11-enrollment-date",
            "bbwg-21-closing-date-of-the-home",
        ],
    }
