"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NorthwestEnergyStarVersion32014FullQa(ProgramBuilder):
    name = "Northwest ENERGY STAR Version 3: 2014 Full QA"
    slug = "northwest-energy-star-version-3-2014-full-qa"
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
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2014, 4, 1)
    start_date = datetime.date(2014, 4, 1)
    role_settings = {}  # Dont swap names

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
        "qa": {
            "default": [
                "if-any-item-is-marked-must-correct-an-action-su",
                "nwes-qa-te-11-ceiling-wall-floor-and-slab-insu",
                "nwes-qa-te-12-all-ceiling-wall-floor-and-slab",
                "nwes-qa-te-21-at-each-location-noted-below-a-co",
                "nwes-qa-te-31-for-insulated-ceilings-with-attic-s",
                "nwes-qa-te-32-insulation-beneath-attic-platforms",
                "nwes-qa-te-411-penetrations-to-unconditioned-spa",
                "nwes-qa-te-412-penetrations-to-unconditioned-spa",
                "nwes-qa-te-413-penetrations-to-unconditioned-spa",
                "nwes-qa-te-421-other-openings-doors-adjacent-to",
                "nwes-qa-te-422-other-openings-attic-access-pane",
                "nwes-qa-te-423-other-openings-whole-house-fans",
                "nwes-qa-hvac-11-hvac-system-quality-installation",
                "nwes-qa-hvac-121-outdoor-design-temperatures-are",
                "nwes-qa-hvac-122-home-orientation-matches-orient",
                "nwes-qa-hvac-123-number-of-occupants-equals-numb",
                "nwes-qa-hvac-124-conditioned-floor-area-is-withi",
                "nwes-qa-hvac-125-window-area-is-within-10-of-c",
                "nwes-qa-hvac-126-predominant-window-shgc-is-with",
                "nwes-qa-hvac-127-hvac-manufacturer-and-model-num",
                "nwes-qa-hvac-128-completed-nwesh-central-ac-comm",
                "nwes-qa-hvac-13-rater-verified-supply-return-du",
                "nwes-qa-hvac-141-contractor-prepared-balancing-r",
                "nwes-qa-hvac-142-contractor-prepared-balancing-r",
                "nwes-qa-hvac-15-for-cooling-only-equipment-liste",
                "nwes-qa-hvac-16-heat-pump-output-heating-capacity",
                "nwes-qa-hvac-21-connections-and-routing-of-ductwo",
                "nwes-qa-hvac-22-no-excessive-coiled-or-looped-fle",
                "nwes-qa-hvac-23-flexible-ducts-supported-at-inter",
                "nwes-qa-hvac-24-building-cavities-not-used-as-sup",
                "nwes-qa-hvac-25-quantity-location-of-supply-and",
                "nwes-qa-hvac-26-bedrooms-pressure-balanced-using",
                "nwes-qa-hvac-31-all-connections-to-trunk-ducts-in",
                "nwes-qa-hvac-32-all-other-supply-ducts-and-all-re",
                "nwes-qa-hvac-41-total-rater-measured-duct-leakage",
                "nwes-qa-hvac-51-rater-measured-ventilation-rate-i",
                "nwes-qa-hvac-52-continuously-operating-ventilatio",
                "nwes-qa-hvac-53-all-ventilation-air-inlets-locate",
                "nwes-qa-hvac-54-ventilation-air-inlets-4-ft-ab",
                "nwes-qa-hvac-55-ventilation-air-inlets-provided-w",
                "nwes-qa-hvac-56-ventilation-air-comes-directly-fr",
                "nwes-qa-hvac-57-building-tightness-requirements-a",
                "nwes-qa-hvac-58-section-provided-to-record-blower",
                "nwes-qa-hvac-61-in-each-kitchen-bathroom-exhau",
                "nwes-qa-hvac-62-clothes-dryers-vented-directly-to",
                "nwes-qa-hvac-71-furnaces-boilers-and-water-heat",
                "nwes-qa-hvac-72-in-homes-with-fireplaces-that-are",
                "nwes-qa-hvac-81-all-return-air-and-mechanically-s",
                "nwes-qa-hvac-82-merv-6-10-filter-located-and-in",
                "nwes-qa-hvac-83-filter-access-panel-includes-gask",
                "nwes-qa-misc-11-name-of-qa-designee",
                "nwes-qa-misc-12-status-of-home-at-time-of-inspect",
                "nwes-qa-misc-13-rater-rtin",
                "nwes-qa-misc-14-date-of-inspection",
                "nwes-qa-misc-15-date-of-raters-pre-drywall-inspe",
                "nwes-qa-misc-16-date-of-raters-final-inspection",
                "nwes-qa-misc-17-data-entry-into-axis-did-the-rat",
                "nwes-qa-misc-18-performance-tests-did-the-home",
                "nwes-qa-misc-19-remrate-if-this-is-a-single-fa",
                "nwes-qa-misc-110-remrate-does-the-home-meet-or",
            ],
        },
    }
    texts = {
        "qa": {
            "if-any-item-is-marked-must-correct-an-action-su": "If any item is marked “Must Correct,” an action summary document shall be attached. In order to complete this checklist in its entirety, the following reference documents should be obtained: All checklists, ventilation documentation, AHRI certificate, and HVAC design documents including heating and cooling room by room loads.",
            "nwes-qa-te-11-ceiling-wall-floor-and-slab-insu": "NWES-QA-TE 1.1 Ceiling, wall, floor, and slab insulation levels shall meet or exceed Northwest ENERGY STAR Homes BOP Prescriptive Path, NW Thermal Enclosure Checklist or Reference Design Home",
            "nwes-qa-te-12-all-ceiling-wall-floor-and-slab": "NWES-QA-TE 1.2 All ceiling, wall, floor, and slab insulation shall be installed to manufacturers specs or, alternatively, Grade II for surfaces that contain a layer of continuous, air impermeable insulation ≥ R-3 in Climate Zone 4, ≥ R-5 in Climate Zones 5 and 6",
            "nwes-qa-te-21-at-each-location-noted-below-a-co": "NWES-QA-TE  2.1 At each location noted below, a complete air barrier shall be provided that is fully aligned with the insulation as follows:\n• At interior surface of ceilings. Also, include barrier at interior edge of attic eave using a wind baffle that extends to the full height of the insulation. Include a baffle in every bay or a tabbed baffle in each bay with a soffit vent that will also prevent wind washing of insulation in adjacent bays.\n• At exterior surface and interior surface of walls\n• At interior surface of floors, including supports to ensure permanent contact and blocking at exposed edges",
            "nwes-qa-te-31-for-insulated-ceilings-with-attic-s": "NWES-QA-TE 3.1 For insulated ceilings with attic space above (i.e., non-cathedralized ceilings), Grade I insulation at the inside face of the exterior wall below meets or exceeds Northwest ENERGY STAR Homes Reference Design Home or ≥ R-21 as outlined in footnotes.",
            "nwes-qa-te-32-insulation-beneath-attic-platforms": "NWES-QA-TE 3.2 Insulation beneath attic platforms (e.g., HVAC platforms, walkways) ≥ R-21 in CZ 4 and 5; ≥ R-30 in CZ 6",
            "nwes-qa-te-411-penetrations-to-unconditioned-spa": "NWES-QA-TE 4.1.1 Penetrations to unconditioned space fully sealed with solid blocking or flashing as needed and gaps sealed with caulk or foam; Bathroom and kitchen exhaust fans",
            "nwes-qa-te-412-penetrations-to-unconditioned-spa": "NWES-QA-TE 4.1.2 Penetrations to unconditioned space fully sealed with solid blocking or flashing as needed and gaps sealed with caulk or foam; Recessed lighting fixtures adjacent to unconditioned space ICAT labeled and fully gasketed. Also, if in insulated ceiling without attic above, exterior surface of fixture insulated to ≥ R-10 in CZ 4 and higher to minimize condensation potential.",
            "nwes-qa-te-413-penetrations-to-unconditioned-spa": "NWES-QA-TE 4.1.3 Penetrations to unconditioned space fully sealed with solid blocking or flashing as needed and gaps sealed with caulk or foam; Light tubes adjacent to unconditioned space include lens separating unconditioned and conditioned space and are fully gasketed",
            "nwes-qa-te-421-other-openings-doors-adjacent-to": "NWES-QA-TE 4.2.1 Other openings; Doors adjacent to unconditioned space (e.g., attics, garages, basements) or ambient conditions gasketed or made substantially air-tight",
            "nwes-qa-te-422-other-openings-attic-access-pane": "NWES-QA-TE 4.2.2 Other openings; Attic access panels and drop-down stairs equipped with a durable ≥ R-10 insulated cover that is gasketed (i.e., not caulked) to produce continuous air seal when occupant is not accessing the attic",
            "nwes-qa-te-423-other-openings-whole-house-fans": "NWES-QA-TE 4.2.3 Other openings; Whole-house fans equipped with a durable ≥ R-10 insulated cover that is gasketed and either installed on the house side or mechanically operated",
            "nwes-qa-hvac-11-hvac-system-quality-installation": "NWES-QA-HVAC 1.1 HVAC System Quality Installation Contractor Checklist completed in its entirety and collected for records, along with documentation on ventilation system, full load calculations, and AHRI certificate",
            "nwes-qa-hvac-121-outdoor-design-temperatures-are": "NWES-QA-HVAC 1.2.1 Outdoor design temperatures are equal to the 1% and 99% ACCA Manual J design temperatures for contractor-designated design location",
            "nwes-qa-hvac-122-home-orientation-matches-orient": "NWES-QA-HVAC 1.2.2 Home orientation matches orientation of rated home",
            "nwes-qa-hvac-123-number-of-occupants-equals-numb": "NWES-QA-HVAC 1.2.3 Number of occupants equals number of occupants in rated home",
            "nwes-qa-hvac-124-conditioned-floor-area-is-withi": "NWES-QA-HVAC 1.2.4 Conditioned floor area is within ±10% of conditioned floor area of rated home",
            "nwes-qa-hvac-125-window-area-is-within-10-of-c": "NWES-QA-HVAC 1.2.5 Window area is within ±10% of calculated window area of rated home",
            "nwes-qa-hvac-126-predominant-window-shgc-is-with": "NWES-QA-HVAC 1.2.6 Predominant window SHGC is within 0.1 of predominant value in rated home",
            "nwes-qa-hvac-127-hvac-manufacturer-and-model-num": "NWES-QA-HVAC 1.2.7 HVAC manufacturer and model numbers on installed equipment, Contractor Checklist, and AHRI certificate or OEM catalog data all match",
            "nwes-qa-hvac-128-completed-nwesh-central-ac-comm": "NWES-QA-HVAC 1.2.8 Completed NWESH Central AC Commissioning & Startup Form is attached ONLY on homes with greater than 600 CDD",
            "nwes-qa-hvac-13-rater-verified-supply-return-du": "NWES-QA-HVAC 1.3 Rater-verified supply & return duct static pressure ≤ 110% of contractor values",
            "nwes-qa-hvac-141-contractor-prepared-balancing-r": "NWES-QA-HVAC 1.4.1 Contractor-prepared balancing report indicating the room name and design airflow for each supply and return register collected by Rater for records. In addition, final individual room airflows measured and documented on balancing report by contractor",
            "nwes-qa-hvac-142-contractor-prepared-balancing-r": "NWES-QA-HVAC 1.4.2 Contractor-prepared balancing report indicating the room name and design airflow for each supply and return register collected by Rater for records. In addition, final individual room airflows measured and documented on balancing report by Rater using Section 804.2 of the Mortgage Industry National HERS Standard, documented by Rater, & verified by Rater. Individual room air flows shall be verified and must be within 20% or ± 25 CFM of design requirements. In spaces where design air flow is less than 40 CFM, up to 40 CFM is allowable.",
            "nwes-qa-hvac-15-for-cooling-only-equipment-liste": "NWES-QA-HVAC 1.5 For cooling-only equipment, Listed Output Cooling Capacity is 95-115% of design load or next nominal size. A larger air handler is permitted to be used to achieve a friction rate ≥ 0.06 IWC",
            "nwes-qa-hvac-16-heat-pump-output-heating-capacity": "NWES-QA-HVAC 1.6 Heat Pump Output Heating Capacity at 35˚F meets or exceeds design heat loss at 35˚F",
            "nwes-qa-hvac-21-connections-and-routing-of-ductwo": "NWES-QA-HVAC 2.1 Connections and routing of ductwork completed without kinks or sharp bends",
            "nwes-qa-hvac-22-no-excessive-coiled-or-looped-fle": "NWES-QA-HVAC 2.2 No excessive coiled or looped flexible ductwork",
            "nwes-qa-hvac-23-flexible-ducts-supported-at-inter": "NWES-QA-HVAC 2.3 Flexible ducts supported at intervals as recommended by mfr. but at a distance ≤ 5 ft",
            "nwes-qa-hvac-24-building-cavities-not-used-as-sup": "NWES-QA-HVAC 2.4 Building cavities not used as supply or return ducts",
            "nwes-qa-hvac-25-quantity-location-of-supply-and": "NWES-QA-HVAC 2.5 Quantity & location of supply and return duct terminals match room-level design in HVAC design documentation",
            "nwes-qa-hvac-26-bedrooms-pressure-balanced-using": "NWES-QA-HVAC 2.6 Bedrooms pressure-balanced using any combination of transfer grills, jump ducts, dedicated return ducts, and / or undercut doors to either: a) provide 1 sq. in. of free area opening per 1 CFM of supply air, as reported by the contractor in the room by room airflow design; OR b) achieve a Rater-measured pressure differential ≤ 3 Pa (0.012 in. w.c.) with respect to the main body of the house when all bedroom doors are closed and all air handlers are operating",
            "nwes-qa-hvac-31-all-connections-to-trunk-ducts-in": "NWES-QA-HVAC 3.1 All connections to trunk ducts in unconditioned space are insulated",
            "nwes-qa-hvac-32-all-other-supply-ducts-and-all-re": "NWES-QA-HVAC 3.2 All other supply ducts and all return ducts in unconditioned space have insulation ≥ R-8",
            "nwes-qa-hvac-41-total-rater-measured-duct-leakage": "NWES-QA-HVAC 4.1 Total Rater-measured duct leakage ≤ 0.06 CFM50 per sq. ft. of conditioned floor area or 75 CFM50 total, whichever is greater",
            "nwes-qa-hvac-51-rater-measured-ventilation-rate-i": "NWES-QA-HVAC 5.1 Rater-measured ventilation rate is 100-120% of design value and ENERGY STAR qualified or equivalent (this ENERGY STAR requirement also applies to bathroom exhaust fans)",
            "nwes-qa-hvac-52-continuously-operating-ventilatio": "NWES-QA-HVAC 5.2 Continuously operating ventilation and exhaust fans include readily accessible override controls and function is obvious or, if not, controls have been labeled and homeowner has proper documentation regarding operation",
            "nwes-qa-hvac-53-all-ventilation-air-inlets-locate": "NWES-QA-HVAC 5.3 All ventilation air inlets located ≥10 ft. of stretched-string distance from known contamination sources such as stack, vent, exhaust hood, or vehicle exhaust. Exception: ventilation air inlets in the wall ≥ 3 ft. from dryer exhausts and contamination sources exiting through the roof",
            "nwes-qa-hvac-54-ventilation-air-inlets-4-ft-ab": "NWES-QA-HVAC 5.4 Ventilation air inlets ≥ 4 ft. above grade or roof deck and not obstructed by snow, plantings, condensing units or other material at time of inspection",
            "nwes-qa-hvac-55-ventilation-air-inlets-provided-w": "NWES-QA-HVAC 5.5 Ventilation air inlets provided with rodent / insect screen with ≤ 0.5 inch mesh",
            "nwes-qa-hvac-56-ventilation-air-comes-directly-fr": "NWES-QA-HVAC 5.6 Ventilation air comes directly from outdoors, not from adjacent dwelling units, garages, crawlspaces, or attics",
            "nwes-qa-hvac-57-building-tightness-requirements-a": "NWES-QA-HVAC 5.7 Building tightness requirements are met based on Prescriptive Path or Modeled Value",
            "nwes-qa-hvac-58-section-provided-to-record-blower": "NWES-QA-HVAC 5.8 Section provided to record blower door or any other performance testing results:",
            "nwes-qa-hvac-61-in-each-kitchen-bathroom-exhau": "NWES-QA-HVAC 6.1 In each kitchen & bathroom, exhaust fan is installed that exhausts directly to the outdoors and not into an attic, crawlspace, or garage. Fan airflow rate and operation meet local code or ASHRAE 62.2-2010 requirements, whichever is more stringent. Kitchen fans with rated flow ≥ 300 CFM must be capable of operating at multiple speeds",
            "nwes-qa-hvac-62-clothes-dryers-vented-directly-to": "NWES-QA-HVAC 6.2 Clothes dryers vented directly to outdoors, except for ventless dryers equipped with a condensate drain",
            "nwes-qa-hvac-71-furnaces-boilers-and-water-heat": "NWES-QA-HVAC 7.1 Furnaces, boilers, and water heaters located within the home’s pressure boundary shall be mechanically drafted or direct-vented (NFPA 54 class III or IV). Unvented combustion space or water heating appliances shall not be permitted within the home’s pressure boundary",
            "nwes-qa-hvac-72-in-homes-with-fireplaces-that-are": "NWES-QA-HVAC 7.2 In homes with fireplaces that are not mechanically drafted or direct-vented, total rated flow of the home’s two largest exhaust fans is ≤ 15 CFM per 100 sq. ft. of conditioned floor area OR the Rater-measured pressure differential is ≤ -5 Pa using BPI’s or RESNET’s worst-case depressurization test procedure",
            "nwes-qa-hvac-81-all-return-air-and-mechanically-s": "NWES-QA-HVAC 8.1 All return air and mechanically supplied outdoor air pass through filter prior to conditioning",
            "nwes-qa-hvac-82-merv-6-10-filter-located-and-in": "NWES-QA-HVAC 8.2 Merv 6 – 10 filter located and installed so as to facilitate access and regular service by the owner",
            "nwes-qa-hvac-83-filter-access-panel-includes-gask": "NWES-QA-HVAC 8.3 Filter access panel includes gasket or comparable sealing mechanism and fits snugly against the exposed edge of filter when closed to prevent bypass",
            "nwes-qa-misc-11-name-of-qa-designee": "NWES-QA-MISC 1.1 Name of QA Designee",
            "nwes-qa-misc-12-status-of-home-at-time-of-inspect": "NWES-QA-MISC 1.2 Status of home at time of inspection (e.g., under construction, occupied)",
            "nwes-qa-misc-13-rater-rtin": "NWES-QA-MISC 1.3 Rater RTIN #",
            "nwes-qa-misc-14-date-of-inspection": "NWES-QA-MISC 1.4 Date of Inspection",
            "nwes-qa-misc-15-date-of-raters-pre-drywall-inspe": "NWES-QA-MISC 1.5 Date of Rater's Pre-Drywall Inspection",
            "nwes-qa-misc-16-date-of-raters-final-inspection": "NWES-QA-MISC 1.6 Date of Rater's Final Inspection",
            "nwes-qa-misc-17-data-entry-into-axis-did-the-rat": "NWES-QA-MISC 1.7 Data Entry into Axis: Did the Rater enter all necessary home information accurately?  ",
            "nwes-qa-misc-18-performance-tests-did-the-home": "NWES-QA-MISC 1.8 Performance Tests:  Did the home meet building tightness and whole home ventilation requirements?",
            "nwes-qa-misc-19-remrate-if-this-is-a-single-fa": "NWES-QA-MISC 1.9 REM/Rate:  If this is a single family home, did the Rater complete the proper modeling of the home in the correct version of NW REM/Rate? ",
            "nwes-qa-misc-110-remrate-does-the-home-meet-or": "NWES-QA-MISC 1.10 REM/Rate:  Does the home meet or beat annual fuel usage? ",
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
                "if-any-item-is-marked-must-correct-an-action-su",
                "nwes-qa-misc-17-data-entry-into-axis-did-the-rat",
                "nwes-qa-misc-18-performance-tests-did-the-home",
            ],
            (
                "Passed",
                "Must Correct",
                "Not Visible",
                "N/A",
            ): [
                "nwes-qa-te-11-ceiling-wall-floor-and-slab-insu",
                "nwes-qa-te-12-all-ceiling-wall-floor-and-slab",
                "nwes-qa-te-21-at-each-location-noted-below-a-co",
                "nwes-qa-te-31-for-insulated-ceilings-with-attic-s",
                "nwes-qa-te-32-insulation-beneath-attic-platforms",
                "nwes-qa-te-411-penetrations-to-unconditioned-spa",
                "nwes-qa-te-412-penetrations-to-unconditioned-spa",
                "nwes-qa-te-413-penetrations-to-unconditioned-spa",
                "nwes-qa-te-421-other-openings-doors-adjacent-to",
                "nwes-qa-te-422-other-openings-attic-access-pane",
                "nwes-qa-te-423-other-openings-whole-house-fans",
                "nwes-qa-hvac-11-hvac-system-quality-installation",
                "nwes-qa-hvac-121-outdoor-design-temperatures-are",
                "nwes-qa-hvac-122-home-orientation-matches-orient",
                "nwes-qa-hvac-123-number-of-occupants-equals-numb",
                "nwes-qa-hvac-124-conditioned-floor-area-is-withi",
                "nwes-qa-hvac-125-window-area-is-within-10-of-c",
                "nwes-qa-hvac-126-predominant-window-shgc-is-with",
                "nwes-qa-hvac-127-hvac-manufacturer-and-model-num",
                "nwes-qa-hvac-128-completed-nwesh-central-ac-comm",
                "nwes-qa-hvac-13-rater-verified-supply-return-du",
                "nwes-qa-hvac-141-contractor-prepared-balancing-r",
                "nwes-qa-hvac-142-contractor-prepared-balancing-r",
                "nwes-qa-hvac-15-for-cooling-only-equipment-liste",
                "nwes-qa-hvac-16-heat-pump-output-heating-capacity",
                "nwes-qa-hvac-21-connections-and-routing-of-ductwo",
                "nwes-qa-hvac-22-no-excessive-coiled-or-looped-fle",
                "nwes-qa-hvac-23-flexible-ducts-supported-at-inter",
                "nwes-qa-hvac-24-building-cavities-not-used-as-sup",
                "nwes-qa-hvac-25-quantity-location-of-supply-and",
                "nwes-qa-hvac-26-bedrooms-pressure-balanced-using",
                "nwes-qa-hvac-31-all-connections-to-trunk-ducts-in",
                "nwes-qa-hvac-32-all-other-supply-ducts-and-all-re",
                "nwes-qa-hvac-41-total-rater-measured-duct-leakage",
                "nwes-qa-hvac-51-rater-measured-ventilation-rate-i",
                "nwes-qa-hvac-52-continuously-operating-ventilatio",
                "nwes-qa-hvac-53-all-ventilation-air-inlets-locate",
                "nwes-qa-hvac-54-ventilation-air-inlets-4-ft-ab",
                "nwes-qa-hvac-55-ventilation-air-inlets-provided-w",
                "nwes-qa-hvac-56-ventilation-air-comes-directly-fr",
                "nwes-qa-hvac-57-building-tightness-requirements-a",
                "nwes-qa-hvac-58-section-provided-to-record-blower",
                "nwes-qa-hvac-61-in-each-kitchen-bathroom-exhau",
                "nwes-qa-hvac-62-clothes-dryers-vented-directly-to",
                "nwes-qa-hvac-71-furnaces-boilers-and-water-heat",
                "nwes-qa-hvac-72-in-homes-with-fireplaces-that-are",
                "nwes-qa-hvac-81-all-return-air-and-mechanically-s",
                "nwes-qa-hvac-82-merv-6-10-filter-located-and-in",
                "nwes-qa-hvac-83-filter-access-panel-includes-gask",
            ],
            (
                "Yes",
                "No",
                "N/A",
            ): [
                "nwes-qa-misc-19-remrate-if-this-is-a-single-fa",
                "nwes-qa-misc-110-remrate-does-the-home-meet-or",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "nwes-qa-misc-13-rater-rtin",
        ],
        "date": [
            "nwes-qa-misc-14-date-of-inspection",
            "nwes-qa-misc-15-date-of-raters-pre-drywall-inspe",
            "nwes-qa-misc-16-date-of-raters-final-inspection",
        ],
    }
