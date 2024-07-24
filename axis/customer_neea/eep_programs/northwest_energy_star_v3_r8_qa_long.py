"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/27/2022 19:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NorthwestEnergyStarV3R8QaLong(ProgramBuilder):
    name = "ENERGY STAR Version 3, Rev 8 QA Checklist – Long"
    slug = "northwest-energy-star-v3-r8-qa-long"
    owner = "neea"
    is_qa_program = True
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
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2015, 7, 31)
    start_date = datetime.date(2015, 7, 31)

    comment = """This is the LONG QA program for ENERGY STAR Version 3, Rev 8 """
    role_settings = {}  # Dont swap names

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": False,
    }
    measures = {
        "qa": {
            "default": [
                "estar-qa-energy-star-action-itemssummary-of-qa-i",
                "estar-qa-rater-design-review-checklist-41-hvac",
                "estar-qa-rater-design-review-checklist-422-nu",
                "estar-qa-rater-design-review-checklist-423-co",
                "estar-qa-rater-design-review-checklist-424-wi",
                "estar-qa-rater-design-review-checklist-425-pr",
                "estar-qa-rater-field-checklist-12-insulation-m",
                "estar-qa-rater-field-checklist-13-all-insulati",
                "estar-qa-rater-field-checklist-23-at-attic-kne",
                "estar-qa-rater-field-checklist-31-for-insulate",
                "estar-qa-rater-field-checklist-33-insulation-b",
                "estar-qa-rater-field-checklist-41-bathroom-k",
                "estar-qa-rater-field-checklist-42-recessed-lig",
                "estar-qa-rater-field-checklist-49-doors-adjace",
                "estar-qa-rater-field-checklist-410-attic-acces",
                "estar-qa-rater-field-checklist-61-ductwork-ins",
                "estar-qa-rater-field-checklist-62-bedrooms-pre",
                "estar-qa-rater-field-checklist-63-all-supply-a",
                "estar-qa-rater-field-checklist-641-rater-measu",
                "estar-qa-rater-field-checklist-642-rater-measu",
                "estar-qa-rater-field-checklist-65-rater-measur",
                "estar-qa-rater-field-checklist-771-inlet-pulls",
                "estar-qa-rater-field-checklist-772-inlet-is",
                "estar-qa-rater-field-checklist-81-in-each-kitch",
                "estar-qa-rater-field-checklist-82-in-each-bathr",
                "estar-qa-rater-field-checklist-91-at-least-one",
                "estar-qa-rater-field-checklist-92-filter-access",
                "estar-qa-rater-field-checklist-93-all-return-ai",
                "estar-qa-rater-field-checklist-101-furnaces-bo",
                "estar-qa-rater-field-checklist-103-if-unvented",
                "estar-qa-misc-name-of-qa-designee",
                "estar-qa-misc-status-of-home-at-time-of-inspectio",
                "estar-qa-misc-date-of-inspection",
                "estar-qa-misc-additional-items-reviewed",
            ],
        },
    }
    texts = {
        "qa": {
            "estar-qa-energy-star-action-itemssummary-of-qa-i": 'ESTAR-QA Energy Star Action Items/Summary of QA: If any item marked "Must Correct", an action summary document shall be attached',
            "estar-qa-rater-design-review-checklist-41-hvac": "ESTAR-QA Rater Design Review Checklist - 4.1: HVAC Design Report collected for records, with no items left blank",
            "estar-qa-rater-design-review-checklist-422-nu": "ESTAR-QA Rater Design Review Checklist - 4.2.2: Number of occupants used in loads (3.4) is within +/- 2 of the home to be certified",
            "estar-qa-rater-design-review-checklist-423-co": "ESTAR-QA Rater Design Review Checklist - 4.2.3: Conditioned floor area used in loads (3.5) is between zero and 300 sq. ft. larger than the home to be certified",
            "estar-qa-rater-design-review-checklist-424-wi": "ESTAR-QA Rater Design Review Checklist - 4.2.4: Window area used in loads (3.6) is between zero and 60 sq. ft. larger than the home to be certified",
            "estar-qa-rater-design-review-checklist-425-pr": "ESTAR-QA Rater Design Review Checklist - 4.2.5: Predominant window SHGC (3.7) is within 0.1 of predominant value in the home to be certified",
            "estar-qa-rater-field-checklist-12-insulation-m": "ESTAR-QA Rater Field Checklist - 1.2: Insulation meets or exceeds levels specified in Item 3.1 of the Rater Design Review Checklist, where Item 3.1 requires that specified ceiling, wall, floor, and slab insulation levels comply with one of the following options:<br>\r\n   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.1.1 Meets or exceeds 2009 IECC levels <b>OR</b>;<br>\r\n   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.1.2 Achieves < or = 133% of the total UA resulting from the U-factors in 2009 IECC Table 402.1.3, per guidance in Footnote 4d, AND specified home infiltration does not exceed the following:<br>\r\n      <UL>\r\n      <LI>3 ACH50 in CZs 1,2\r\n      <LI>2.5 ACH50 in CZs 3,4\r\n      <LI>2 ACH50 in CZs 5,6,7\r\n      <LI>1.5 ACH50 in CZ 8\r\n      </UL>",
            "estar-qa-rater-field-checklist-13-all-insulati": "ESTAR-QA Rater Field Checklist - 1.3: All insulation achieves RESNET-defined Grade I installation, or alternative per Footnote 4 of Rater Field Checklist",
            "estar-qa-rater-field-checklist-23-at-attic-kne": "ESTAR-QA Rater Field Checklist - 2.3: At attic knee walls and skylight shaft walls, a complete air barrier provided that is fully aligned at exterior vertical surface of wall insulation in all climate zones; also at interior vertical surface of wall insulation in CZ 4-8",
            "estar-qa-rater-field-checklist-31-for-insulate": "ESTAR-QA Rater Field Checklist - 3.1: For Insulated ceilings with attic space above (i.e. non-cathedralized), Grade I insulation extends to the inside face of the exterior wall below and is ≤ R-21 in CZ 1-5; ≥ R-30 in CZ 6-8",
            "estar-qa-rater-field-checklist-33-insulation-b": "ESTAR-QA Rater Field Checklist - 3.3: Insulation beneath attic platforms (e.g., HVAC platforms, walkways) ≥ R-21 in CZ 1-5; ≥ R-30 in CZ 6-8",
            "estar-qa-rater-field-checklist-41-bathroom-k": "ESTAR-QA Rater Field Checklist - 4.1: Bathroom & kitchen exhaust fans that penetrate unconditioned space sealed, with blocking / flashing as needed",
            "estar-qa-rater-field-checklist-42-recessed-lig": "ESTAR-QA Rater Field Checklist - 4.2: Recessed lighting fixtures adjacent to unconditioned space ICAT labeled and gasketed. Also, if in insulated ceiling without attic above, exterior surface of fixture insulated to ≥ R-10 in CZ 4-8",
            "estar-qa-rater-field-checklist-49-doors-adjace": "ESTAR-QA Rater Field Checklist - 4.9: Doors adjacent to unconditioned space (e.g., attics, garages, basements) or ambient conditions made substantially air-tight with weatherstripping or equivalent gasket",
            "estar-qa-rater-field-checklist-410-attic-acces": "ESTAR-QA Rater Field Checklist - 4.10: Attic access panels, drop-down stairs, & whole-house fans equipped with durable ≥ R-10 cover that is gasketed (i.e., not caulked). Fan covers either installed on house side or mechanically operated.",
            "estar-qa-rater-field-checklist-61-ductwork-ins": "ESTAR-QA Rater Field Checklist - 6.1: Ductwork installed without kinks, sharp bends, or excessive coiled flexible ductwork.",
            "estar-qa-rater-field-checklist-62-bedrooms-pre": "ESTAR-QA Rater Field Checklist - 6.2: Bedrooms pressure-balanced using any combination of transfer grills, jump ducts, dedicated return ducts, and / or undercut doors to achieve Rater-measured pressure diff. ≤ 3 Pa with respect to main body of the house when all bedroom doors are closed & all air handlers are operating, or alternative Footnote 34 of Rater Field Checklist.",
            "estar-qa-rater-field-checklist-63-all-supply-a": "ESTAR-QA Rater Field Checklist - 6.3: All supply and return ducts in unconditioned space, including connections to trunk ducts, are insulated to ≥ R-6.",
            "estar-qa-rater-field-checklist-641-rater-measu": "ESTAR-QA Rater Field Checklist - 6.4.1 Rater-measured total duct leakage at Rough-in meets: The greater of  4 CFM25 per 100 sq. ft. of CFA or  40 CFM, with air handler & all ducts, building cavities used as ducts, & duct boots installed. In addition, all duct boots sealed to finished surface, Rater-verified at final, <b>OR</b>; <i>(see next question)</i>",
            "estar-qa-rater-field-checklist-642-rater-measu": "ESTAR-QA Rater Field Checklist - 6.4.2 Rater-measured total duct leakage at Final meets: The greater of  8 CFM25 per 100 sq. ft. of CFA or  80 CFM, with the air handler & all ducts, building cavities used as ducts, duct boots, & register grilles atop the finished surface (e.g., drywall, floor) installed.",
            "estar-qa-rater-field-checklist-65-rater-measur": "ESTAR-QA Rater Field Checklist - 6.5: Rater-measured duct leakage to outdoors the greater of  4 CFM25 per 100 sq. ft. of CFA or  40 CFM25.",
            "estar-qa-rater-field-checklist-771-inlet-pulls": "ESTAR-QA Rater Field Checklist - 7.7.1 Inlet pulls ventilation air directly from outdoors & not from attic, crawlspace, garage, or adjacent dwelling unit.  (Complete if ventilation air inlet location was specified (2.12, 2.13); otherwise check “N/A”)",
            "estar-qa-rater-field-checklist-772-inlet-is": "ESTAR-QA Rater Field Checklist - 7.7.2 Inlet is ≥ 10 ft. of stretched-string distance from known contamination sources (e.g., stack, vent, exhaust, vehicles) not exiting the roof, and ≥ 3 ft. from sources exiting the roof.  (Complete if ventilation air inlet location was specified (2.12, 2.13); otherwise check “N/A”)",
            "estar-qa-rater-field-checklist-81-in-each-kitch": "ESTAR-QA Rater Field Checklist - 8.1 In each kitchen, Local Mechanical Exhaust system is installed that exhausts directly to outdoors & meets one of the following Rater-measured airflow standards: 1) Continuous Rate: ≥ 5 ACH, based on kitchen volume; 2) Intermittent Rate: ≥ 100 CFM and, if not integrated with range, also ≥ 5 ACH based on kitchen volume",
            "estar-qa-rater-field-checklist-82-in-each-bathr": "ESTAR-QA Rater Field Checklist - 8.2 In each bathroom, Local Mechanical Exhaust system is installed that exhausts directly to outdoors & meets one of the following Rater-measured airflow standards: 1) Continuous Rate: ≥ 20 CFM; 2) Intermittent Rate: ≥ 50 CFM",
            "estar-qa-rater-field-checklist-91-at-least-one": "ESTAR-QA Rater Field Checklist - 9.1 At least one MERV 6 or higher filter installed in each ducted mechanical system in a location that facilitates access and regular service by the owner",
            "estar-qa-rater-field-checklist-92-filter-access": "ESTAR-QA Rater Field Checklist - 9.2 Filter access panel includes gasket or comparable sealing mechanism and fits snugly against the exposed edge of filter when closed to prevent bypass",
            "estar-qa-rater-field-checklist-93-all-return-ai": "ESTAR-QA Rater Field Checklist - 9.3 All return air and mechanically supplied outdoor air passes through filter prior to conditioning",
            "estar-qa-rater-field-checklist-101-furnaces-bo": "ESTAR-QA Rater Field Checklist - 10.1 Furnaces, boilers, and water heaters located within the home’s pressure boundary are mechanically drafted or direct-vented. See Footnote 56 of Rater Field Checklist for alternatives.",
            "estar-qa-rater-field-checklist-103-if-unvented": "ESTAR-QA Rater Field Checklist - 10.3 If unvented combustion appliances other than cooking ranges or ovens are located inside the home’s pressure boundary, the Rater has followed Section 805 of RESNET’s Standards, encompassing ANSI/ACCA 12 QH-2014, Appendix A, Section A3 (Carbon Monoxide Test), & verified the equipment meets the limits defined within.",
            "estar-qa-misc-name-of-qa-designee": "ESTAR-QA MISC: Name of QA Designee",
            "estar-qa-misc-status-of-home-at-time-of-inspectio": "ESTAR-QA MISC: Status of Home at time of Inspection",
            "estar-qa-misc-date-of-inspection": "ESTAR-QA MISC: Date of Inspection",
            "estar-qa-misc-additional-items-reviewed": "ESTAR-QA MISC: Additional Items Reviewed",
        },
    }
    descriptions = {
        "qa": {},
    }
    suggested_responses = {
        "qa": {
            (
                "Yes",
                "No",
            ): [
                "estar-qa-energy-star-action-itemssummary-of-qa-i",
            ],
            (
                "Passed",
                "Must Correct",
                "N/A",
            ): [
                "estar-qa-rater-design-review-checklist-41-hvac",
                "estar-qa-rater-design-review-checklist-422-nu",
                "estar-qa-rater-design-review-checklist-423-co",
                "estar-qa-rater-design-review-checklist-424-wi",
                "estar-qa-rater-design-review-checklist-425-pr",
            ],
            (
                "Passed",
                "Must Correct",
                "Not Visible",
                "N/A",
            ): [
                "estar-qa-rater-field-checklist-12-insulation-m",
                "estar-qa-rater-field-checklist-13-all-insulati",
                "estar-qa-rater-field-checklist-23-at-attic-kne",
                "estar-qa-rater-field-checklist-31-for-insulate",
                "estar-qa-rater-field-checklist-33-insulation-b",
                "estar-qa-rater-field-checklist-41-bathroom-k",
                "estar-qa-rater-field-checklist-42-recessed-lig",
                "estar-qa-rater-field-checklist-49-doors-adjace",
                "estar-qa-rater-field-checklist-410-attic-acces",
                "estar-qa-rater-field-checklist-61-ductwork-ins",
                "estar-qa-rater-field-checklist-62-bedrooms-pre",
                "estar-qa-rater-field-checklist-63-all-supply-a",
                "estar-qa-rater-field-checklist-641-rater-measu",
                "estar-qa-rater-field-checklist-642-rater-measu",
                "estar-qa-rater-field-checklist-65-rater-measur",
                "estar-qa-rater-field-checklist-771-inlet-pulls",
                "estar-qa-rater-field-checklist-772-inlet-is",
                "estar-qa-rater-field-checklist-81-in-each-kitch",
                "estar-qa-rater-field-checklist-82-in-each-bathr",
                "estar-qa-rater-field-checklist-91-at-least-one",
                "estar-qa-rater-field-checklist-92-filter-access",
                "estar-qa-rater-field-checklist-93-all-return-ai",
                "estar-qa-rater-field-checklist-101-furnaces-bo",
                "estar-qa-rater-field-checklist-103-if-unvented",
            ],
            (
                "Yes; details entered as comment",
                "Yes; details uploaded as separate document",
                "No",
            ): [
                "estar-qa-misc-additional-items-reviewed",
            ],
        },
    }
    instrument_types = {
        "date": [
            "estar-qa-misc-date-of-inspection",
        ],
    }
    suggested_response_flags = {
        "qa": {
            "estar-qa-misc-additional-items-reviewed": {
                "Yes; details entered as comment": {
                    "comment_required": True,
                },
                "Yes; details uploaded as separate document": {
                    "document_required": True,
                },
            },
        },
    }
