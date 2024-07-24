"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class BpcaMonthlyReporting(ProgramBuilder):
    name = "BPCA Monthly Reporting"
    slug = "bpca-monthly-reporting"
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

    visibility_date = datetime.date(2013, 5, 1)
    start_date = datetime.date(2013, 5, 1)

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
        "provider": False,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "bpca-rmr-10-project-name",
                "bpca-rmr-11-rating-type",
                "bpca-rmr-12-energy-star-mandated-or-non-mandated",
                "bpca-rmr-13-building-type",
                "bpca-rmr-14-plan-review-date",
                "bpca-rmr-15-plan-review-pass-fail",
                "bpca-rmr-16-final-test-out-date",
                "bpca-rmr-17-test-out-pass-fail",
                "bpca-rmr-18-other-nyserda-programs",
                "bpca-rmr-19-primary-heating-fuel-type",
                "bpca-rmr-110-bhi-report-date",
                "bpca-rmr-111-nysbacsg-filing-date",
                "bpca-rmr-112-meets-federal-epact-tax-credit",
                "bpca-rmr-113-notes",
            ],
        },
    }
    texts = {
        "rater": {
            "bpca-rmr-10-project-name": "BPCA-RMR 1.0 Project Name",
            "bpca-rmr-11-rating-type": "BPCA-RMR 1.1 Rating Type",
            "bpca-rmr-12-energy-star-mandated-or-non-mandated": "BPCA-RMR 1.2 ENERGY STAR Mandated or Non-Mandated",
            "bpca-rmr-13-building-type": "BPCA-RMR 1.3 Building Type",
            "bpca-rmr-14-plan-review-date": "BPCA-RMR 1.4 Plan Review Date",
            "bpca-rmr-15-plan-review-pass-fail": "BPCA-RMR 1.5 Plan Review Pass / Fail",
            "bpca-rmr-16-final-test-out-date": "BPCA-RMR 1.6 Final Test-Out Date",
            "bpca-rmr-17-test-out-pass-fail": "BPCA-RMR 1.7 Test Out Pass / Fail",
            "bpca-rmr-18-other-nyserda-programs": "BPCA-RMR 1.8 Other NYSERDA Programs",
            "bpca-rmr-19-primary-heating-fuel-type": "BPCA-RMR 1.9 Primary Heating Fuel Type",
            "bpca-rmr-110-bhi-report-date": "BPCA-RMR 1.10 BHI Report Date",
            "bpca-rmr-111-nysbacsg-filing-date": "BPCA-RMR 1.11 NYSBA/CSG Filing Date",
            "bpca-rmr-112-meets-federal-epact-tax-credit": "BPCA-RMR 1.12 Meets Federal EPACT Tax Credit?",
            "bpca-rmr-113-notes": "BPCA-RMR 1.13 Notes",
        },
    }
    descriptions = {
        "rater": {},
    }
    suggested_responses = {
        "rater": {
            (
                "V 2.0",
                "V 2.5",
                "V 3.0",
                "HERS Index",
                "Code Compliance Only",
                "Other",
            ): [
                "bpca-rmr-11-rating-type",
            ],
            (
                "Mandated",
                "Non-Mandated",
            ): [
                "bpca-rmr-12-energy-star-mandated-or-non-mandated",
            ],
            (
                "Single Family Detached",
                "Single Family Attached",
                "Multi-Family",
                "TBD",
            ): [
                "bpca-rmr-13-building-type",
            ],
            (
                "Pass",
                "Fail",
            ): [
                "bpca-rmr-15-plan-review-pass-fail",
                "bpca-rmr-17-test-out-pass-fail",
            ],
            (
                "None",
                "GRBP",
            ): [
                "bpca-rmr-18-other-nyserda-programs",
            ],
            (
                "Gas",
                "Oil",
                "Propane",
                "Electric",
                "Wood/Pellet",
                "Other",
            ): [
                "bpca-rmr-19-primary-heating-fuel-type",
            ],
            (
                "Yes",
                "No",
                "TBD",
            ): [
                "bpca-rmr-112-meets-federal-epact-tax-credit",
            ],
        },
    }
    instrument_types = {
        "date": [
            "bpca-rmr-14-plan-review-date",
            "bpca-rmr-16-final-test-out-date",
            "bpca-rmr-110-bhi-report-date",
            "bpca-rmr-111-nysbacsg-filing-date",
        ],
    }
