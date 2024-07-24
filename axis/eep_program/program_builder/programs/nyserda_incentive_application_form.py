"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/28/2022 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NyserdaIncentiveApplicationForm(ProgramBuilder):
    name = "NYSERDA Incentive Application Form"
    slug = "nyserda-incentive-application-form"
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
                "nyserda-iaf-10-po-number",
                "nyserda-iaf-11-confirmed-rating-type",
                "nyserda-iaf-12-of-units",
                "nyserda-iaf-13-eligible-for-the-500-per-dwelling",
                "nyserda-iaf-14-200-first-plan-review-incentive",
                "nyserda-iaf-15-pay-first-plan-review-incentive-to",
                "nyserda-iaf-16-300-first-confirmed-rating-incent",
                "nyserda-iaf-17-pay-first-confirmed-rating-incenti",
                "nyserda-iaf-18-bpi-accredited-company-with-certif",
                "nyserda-iaf-19-bpi-accredited-company-with-certif",
                "nyserda-iaf-110-bpi-accredited-company-with-certi",
                "nyserda-iaf-111-hvac-contractor-is-affiliated-wit",
            ],
        },
    }
    texts = {
        "rater": {
            "nyserda-iaf-10-po-number": "NYSERDA-IAF 1.0 PO Number",
            "nyserda-iaf-11-confirmed-rating-type": "NYSERDA-IAF 1.1 Confirmed Rating Type",
            "nyserda-iaf-12-of-units": "NYSERDA-IAF 1.2 # of Units",
            "nyserda-iaf-13-eligible-for-the-500-per-dwelling": "NYSERDA-IAF 1.3 Eligible for the $500 per dwelling unit affordable housing incentive?",
            "nyserda-iaf-14-200-first-plan-review-incentive": "NYSERDA-IAF 1.4 $200 First Plan Review Incentive?",
            "nyserda-iaf-15-pay-first-plan-review-incentive-to": "NYSERDA-IAF 1.5 Pay First Plan Review Incentive to Rater?",
            "nyserda-iaf-16-300-first-confirmed-rating-incent": "NYSERDA-IAF 1.6 $300 First Confirmed Rating Incentive?",
            "nyserda-iaf-17-pay-first-confirmed-rating-incenti": "NYSERDA-IAF 1.7 Pay First Confirmed Rating Incentive to Rater?",
            "nyserda-iaf-18-bpi-accredited-company-with-certif": "NYSERDA-IAF 1.8 BPI Accredited Company with Certified Envelope Technician?",
            "nyserda-iaf-19-bpi-accredited-company-with-certif": "NYSERDA-IAF 1.9 BPI Accredited Company with Certified Heating Technician?",
            "nyserda-iaf-110-bpi-accredited-company-with-certi": "NYSERDA-IAF 1.10 BPI Accredited Company with Certified A/C Heat Pump Technician?",
            "nyserda-iaf-111-hvac-contractor-is-affiliated-wit": "NYSERDA-IAF 1.11 HVAC contractor is affiliated with ACCA or NYSERDA as their H-QUITO for v3.0 projects?",
        },
    }
    descriptions = {
        "rater": {},
    }
    suggested_responses = {
        "rater": {
            (
                "Model $3000",
                "Display $3000",
                "NYESCH V3.0 2013 Upstate $1250",
                "NYESCH V3.0 2013 Downstate $1500",
            ): [
                "nyserda-iaf-11-confirmed-rating-type",
            ],
            (
                "Yes",
                "No",
            ): [
                "nyserda-iaf-13-eligible-for-the-500-per-dwelling",
                "nyserda-iaf-14-200-first-plan-review-incentive",
                "nyserda-iaf-15-pay-first-plan-review-incentive-to",
                "nyserda-iaf-16-300-first-confirmed-rating-incent",
                "nyserda-iaf-17-pay-first-confirmed-rating-incenti",
                "nyserda-iaf-111-hvac-contractor-is-affiliated-wit",
            ],
            (
                "Yes (enter company name as comment)",
                "No",
            ): [
                "nyserda-iaf-18-bpi-accredited-company-with-certif",
                "nyserda-iaf-19-bpi-accredited-company-with-certif",
                "nyserda-iaf-110-bpi-accredited-company-with-certi",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "nyserda-iaf-12-of-units",
        ],
    }
