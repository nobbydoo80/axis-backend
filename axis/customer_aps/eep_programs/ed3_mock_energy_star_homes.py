"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class Ed3MockEnergyStarHomes(ProgramBuilder):
    name = "ED3 Mock ENERGY STAR Homes"
    slug = "ed3-mock-energy-star-homes"
    owner = "electrical-district-3"
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
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2012, 10, 25)
    start_date = datetime.date(2012, 10, 25)
    close_date = datetime.date(2017, 9, 30)
    end_date = datetime.date(2017, 10, 1)

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
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
                "cc-r-11-has-a-completed-energy-star-version-3-hv",
                "cc-r-12-has-an-energy-star-version-3-hvac-system",
                "cc-r-13-has-a-completed-energy-star-version-3-wa",
                "te-r-5-fd1-measured-blower-door-value",
                "hvac-r-28-fd1-measured-dominant-duct-leakage-pre",
                "hvac-r-28-fd2-measured-pressure-in-each-bedroom",
                "hvac-r-41-fd1-total-measured-duct-leakage-value",
                "hvac-r-42-fd1-measured-duct-leakage-values-to",
            ],
        },
    }
    texts = {
        "rater": {
            "te-r-11-prescriptive-path-fenestration-shall-mee": "TE-R 1.1 Prescriptive Path: Fenestration shall meet or exceed ENERGY STAR® requirements",
            "te-r-12-performance-path-fenestration-shall-meet": "TE-R 1.2 Performance Path: Fenestration shall meet or exceed 2009 IECC requirements",
            "te-r-211-ceiling-wall-floor-and-slab-insulat": "TE-R 2.1.1  Ceiling, wall, floor, and slab insulation levels shall comply with one of the following options: Meet or exceed 2009 IECC levels OR; (see next question)",
            "te-r-212-achieve-133-of-the-total-ua-result": "TE-R 2.1.2  Achieve <= 133% of the total UA resulting from the U-factors in the 2009 IECC Table 402.1.3, excluding fenestration and per guidance in Footnote 3d, AND home shall achieve <= 50% of the infiltration rate in Exhibit 1 of the National Program Requirements",
            "te-r-22-all-ceiling-wall-floor-and-slab-insul": "TE-R 2.2  All ceiling, wall, floor, and slab insulation shall achieve RESNET-defined Grade I installation or, alternatively, Grade II for surfaces with insulated sheathing (see checklist item 4.4.1 for required insulation levels)",
            "te-r-311-walls-behind-showers-and-tubs": "TE-R 3.1.1   Walls behind showers and tubs",
            "te-r-312-walls-behind-fireplaces": "TE-R 3.1.2   Walls behind fireplaces",
            "te-r-313-attic-knee-walls": "TE-R 3.1.3   Attic knee walls",
            "te-r-314-skylight-shaft-walls": "TE-R 3.1.4   Skylight shaft walls",
            "te-r-315-wall-adjoining-porch-roof": "TE-R 3.1.5   Wall adjoining porch roof",
            "te-r-316-staircase-walls": "TE-R 3.1.6   Staircase walls",
            "te-r-317-double-walls": "TE-R 3.1.7   Double walls",
            "te-r-318-garage-rim-band-joist-adjoining-con": "TE-R 3.1.8   Garage rim / band joist adjoining conditioned space",
            "te-r-319-all-other-exterior-walls": "TE-R 3.1.9   All other exterior walls",
            "te-r-321-floor-above-garage": "TE-R 3.2.1   Floor above garage",
            "te-r-322-cantilevered-floor": "TE-R 3.2.2   Cantilevered floor",
            "te-r-323-floor-above-unconditioned-basement-or": "TE-R 3.2.3   Floor above unconditioned basement or unconditioned crawlspace",
            "te-r-331-dropped-ceiling-soffit-below-uncond": "TE-R 3.3.1   Dropped ceiling / soffit below unconditioned attic",
            "te-r-332-all-other-ceilings": "TE-R 3.3.2   All other ceilings",
            "te-r-41-for-insulated-ceilings-with-attic-space": "TE-R 4.1  For insulated ceilings with attic space above (i.e., non-cathedralized ceilings), Grade I insulation extends to the inside face of the exterior wall below at the following levels: CZ 1 to 5: >= R-21; CZ 6 to 8: >= R-30",
            "te-r-42-for-slabs-on-grade-in-cz-4-and-higher-1": "TE-R 4.2  For slabs on grade in CZ 4 and higher, 100% of slab edge insulated to >= R-5 at the depth specified by the 2009 IECC and aligned with thermal boundary of the walls",
            "te-r-43-insulation-beneath-attic-platforms-eg": "TE-R 4.3  Insulation beneath attic platforms  (e.g., HVAC platforms, walkways) >= R-21 in CZ 1 to 5 &#8805 R-30 in CZ 6 to 8",
            "te-r-441-reduced-thermal-bridging-at-above-grade": "TE-R 4.4.1 Reduced thermal bridging at above-grade walls separating conditioned from unconditioned space (rim / band joists exempted) using one of the following options: Continuous rigid insulation, insulated siding, or combination of the two; >= R-3 in Climate Zones 1 to 4, >= R-5 in Climate Zones 5 to 8, OR; (see next question)",
            "te-r-442-structural-insulated-panels-sips-or": "TE-R 4.4.2 Structural Insulated Panels (SIPs), OR; (see next question)",
            "te-r-443-insulated-concrete-forms-icfs-or-s": "TE-R 4.4.3 Insulated Concrete Forms (ICFs), OR; (see next question)",
            "te-r-444-double-wall-framing-or-see-next-ques": "TE-R 4.4.4 Double-wall framing, OR; (see next question)",
            "te-r-445a-all-corners-insulated-r-6-to-edge": "TE-R 4.4.5a All corners insulated >= R-6 to edge, AND; (see next question)",
            "te-r-445b-all-headers-above-windows-doors-insu": "TE-R 4.4.5b All headers above windows & doors insulated, AND; (see next question)",
            "te-r-445c-framing-limited-at-all-windows-doors": "TE-R 4.4.5c Framing limited at all windows & doors, AND; (see next question)",
            "te-r-445d-all-interior-exterior-wall-intersect": "TE-R 4.4.5d All interior / exterior wall intersections insulated to the same R-value as the rest of the exterior wall, AND; (see next question)",
            "te-r-445e-minimum-stud-spacing-of-16-in-oc-fo": "TE-R 4.4.5e Minimum stud spacing of 16 in. o.c. for 2x4 framing in all Climate Zones and, in Climate Zones 5 through 8, 24 in. o.c. for 2x6 framing unless construction documents specify other spacing is structurally required",
            "te-r-511-duct-flue-shaft": "TE-R 5.1.1 Duct / flue shaft",
            "te-r-512-plumbing-piping": "TE-R 5.1.2 Plumbing / piping",
            "te-r-513-electrical-wiring": "TE-R 5.1.3 Electrical wiring",
            "te-r-514-bathroom-and-kitchen-exhaust-fans": "TE-R 5.1.4 Bathroom and kitchen exhaust fans",
            "te-r-515-recessed-lighting-fixtures-adjacent-to": "TE-R 5.1.5 Recessed lighting fixtures adjacent to unconditioned space ICAT labeled and fully gasketed. Also, if in insulated ceiling without attic above, exterior surface of fixture insulated to >= R-10 in CZ 4 and higher to minimize condensation potential.",
            "te-r-516-light-tubes-adjacent-to-unconditioned-s": "TE-R 5.1.6 Light tubes adjacent to unconditioned space include lens separating unconditioned and conditioned space and are fully gasketed",
            "te-r-521-all-sill-plates-adjacent-to-conditioned": "TE-R 5.2.1 All sill plates adjacent to conditioned space sealed to foundation or sub-floor with caulk. Foam gasket also placed beneath sill plate if resting atop concrete or masonry and adjacent to conditioned space.",
            "te-r-522-at-top-of-walls-adjoining-unconditione": "TE-R 5.2.2  At top of walls adjoining unconditioned spaces, continuous top plates or sealed blocking using caulk, foam, or equivalent material",
            "te-r-523-drywall-sealed-to-top-plate-at-all-unc": "TE-R 5.2.3  Drywall sealed to top plate at all unconditioned attic / wall interfaces using caulk, foam, drywall adhesive (but not other construction adhesives), or equivalent material. Either apply sealant directly between drywall and top plate or to the seam between the two from the attic above.",
            "te-r-524-rough-opening-around-windows-exterior": "TE-R 5.2.4 Rough opening around windows & exterior doors sealed with caulk or foam",
            "te-r-525-marriage-joints-between-modular-home-mo": "TE-R 5.2.5 Marriage joints between modular home modules at all exterior boundary conditions fully sealed with gasket and foam",
            "te-r-526-all-seams-between-structural-insulated": "TE-R 5.2.6 All seams between Structural Insulated Panels (SIPs) foamed and /or taped per manufacturer's instructions",
            "te-r-527-in-multi-family-buildings-the-gap-bet": "TE-R 5.2.7  In multi-family buildings, the gap between the drywall shaft wall (i.e. common wall) and the structural framing between units fully sealed at all exterior boundaries",
            "te-r-531-doors-adjacent-to-unconditioned-space": "TE-R 5.3.1 Doors adjacent to unconditioned space (e.g., attics, garages, basements) or ambient conditions gasketed or made substantially air-tight",
            "te-r-532-attic-access-panels-and-drop-down-stair": "TE-R 5.3.2 Attic access panels and drop-down stairs equipped with a durable >= R-10 insulated cover that is gasketed (i.e., not caulked) to produce continuous air seal when occupant is not accessing the attic",
            "te-r-533-whole-house-fans-equipped-with-a-durabl": "TE-R 5.3.3 Whole-house fans equipped with a durable >= R-10 insulated cover that is gasketed and either installed on the house side or mechanically operated",
            "cc-r-11-has-a-completed-energy-star-version-3-hv": "CC-R 1.1  Has a completed ENERGY STAR Version 3 HVAC System Quality Installation Contractor Checklist been received from this home's HVAC contractor?",
            "cc-r-12-has-an-energy-star-version-3-hvac-system": "CC-R 1.2  Has an ENERGY STAR Version 3 HVAC System Quality Installation Rater Checklist been completed for this home?  If sampling, has a completed checklist been received for each tested home in the sample set?",
            "cc-r-13-has-a-completed-energy-star-version-3-wa": "CC-R 1.3  Has a completed ENERGY STAR Version 3 Water Management System Builder Checklist OR Indoor airPLUS Verification Checklist been received from this home's builder?",
            "te-r-5-fd1-measured-blower-door-value": "TE-R 5-FD1  Measured Blower Door value",
            "hvac-r-28-fd1-measured-dominant-duct-leakage-pre": "HVAC-R 2.8-FD1  Measured dominant duct leakage pressure of main body of home referenced to outside",
            "hvac-r-28-fd2-measured-pressure-in-each-bedroom": "HVAC-R 2.8-FD2  Measured pressure in each bedroom with respect to the main body of the home",
            "hvac-r-41-fd1-total-measured-duct-leakage-value": "HVAC-R 4.1-FD1  Total measured duct leakage value(s) for each installed unit present at the home",
            "hvac-r-42-fd1-measured-duct-leakage-values-to": "HVAC-R 4.2-FD1  Measured duct leakage value(s) to outdoors for each installed unit present at the home",
        },
    }
    descriptions = {
        "rater": {
            "te-r-11-prescriptive-path-fenestration-shall-mee": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 1.1 <sup>2</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Prescriptive Path: Fenestration shall meet or exceed ENERGY STAR requirements</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Select windows, doors, and skylights to meet ENERGY STAR program requirements for windows, doors, and skylights. </li> <li style="margin-left:0pt">Note that the U-value and the Solar Heat Gain Coefficient (SHGC) for doors apply to the whole door, not just the glazing portion. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>2. For Prescriptive Path: All windows, doors, and skylights shall meet or exceed ENERGY STAR Program Requirements for Residential Windows, Doors, and Skylights - Version 5.0 as outlined at <a href="http://www.energystar.gov/windows" target="_blank"><span><span style="text-decoration:underline">www.energystar .gov/windows</span></span></a>. For Performance Path: All windows, doors, and skylights shall meet or exceed the component U-factor and SHGC requirements specified in the 2009 IECC - Table 402.1.1. If no NFRC rating is noted on the window or in product literature (e.g., for site-built fenestration), select the U-factor and SHGC value from tables 4 and 14, respectively, in 2005 ASHRAE Fundamentals, Chapter 31. Select the highest U-factor and SHGC value among the values listed for the known window characteristics (e.g., frame type, number of panes, glass color, and presence of low-e coating). Note that the U-factor requirement applies to all fenestration while the SHGC only applies to the glazed portion. The following exceptions apply: </p> <p> </p> <p>a. An area-weighted average of fenestration products shall be permitted to satisfy the U-factor requirements; </p> <p>b. An area-weighted average of fenestration products &gt; 50% glazed shall be permitted to satisfy the SHGC requirements; </p> <p>c. 15 square feet of glazed fenestration per dwelling unit shall be exempt from the U-factor and SHGC requirements, and shall be excluded from area-weighted averages calculated using a) and b), above; </p> <p>d. One side-hinged opaque door assembly up to 24 square feet in area shall be exempt from the U-factor requirements and shall be excluded from area-weighted averages calculated using a) and b), above; </p> <p>e. Fenestration utilized as part of a passive solar design shall be exempt from the U-factor and SHGC requirements, and shall be excluded from area-weighted averages calculated using a) and </p> <p>b), above. Exempt windows shall be facing within 45 degrees of true south and directly coupled to thermal storage mass that has a heat capacity &gt; 20 btu/ft<sup>3</sup>xo<sup>F</sup> and provided in a ratio of at least 3 sq. ft. per sq. ft. of south facing fenestration. Generally, thermal mass materials will be at least 2" thick. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-12-performance-path-fenestration-shall-meet": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 1.2 <sup>2</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Performance Path: Fenestration shall meet or exceed 2009 IECC requirements</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Select windows, doors, and skylights to meet 2009 IECC standards for windows, doors, and skylights, except fenestration utilized as part of a passive solar design. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>2. For Prescriptive Path: All windows, doors, and skylights shall meet or exceed ENERGY STAR Program Requirements for Residential Windows, Doors, and Skylights ñ Version 5.0 as outlined at </p> <p><a href="http://www.energystar.gov/windows" target="_blank"><span><span style="text-decoration:underline">www.energystar.gov/windows</span></span></a>. For Performance Path: All windows, doors, and skylights shall meet or exceed the component U-factor and SHGC requirements specified in the 2009 IECC ñ Table 402.1.1. If no NFRC rating is noted on the window or in product literature (e.g., for site-built fenestration), select the U-factor and SHGC value from tables 4 and 14, respectively, in 2005 ASHRAE Fundamentals, Chapter 31. Select the highest U-factor and SHGC value among the values listed for the known window characteristics (e.g., frame type, number of panes, glass color, and presence of low-e coating). Note that the U-factor requirement applies to all fenestration while the SHGC only applies to the glazed portion. The following exceptions apply: </p> <p> </p> <p>a. An area-weighted average of fenestration products shall be permitted to satisfy the U-factor requirements; </p> <p>b. An area-weighted average of fenestration products &gt; 50% glazed shall be permitted to satisfy the SHGC requirements; </p> <p>c. 15 square feet of glazed fenestration per dwelling unit shall be exempt from the U-factor and SHGC requirements, and shall be excluded from area-weighted averages calculated using a) and b), above; </p> <p>d. One side-hinged opaque door assembly up to 24 square feet in area shall be exempt from the U-factor requirements and shall be excluded from area-weighted averages calculated using a) and b), above; </p> <p>e. Fenestration utilized as part of a passive solar design shall be exempt from the U-factor and SHGC requirements, and shall be excluded from area-weighted averages calculated using a) and b), above. Exempt windows shall be facing within 45 degrees of true south and directly coupled to thermal storage mass that has a heat capacity &gt; 20 btu/ft3xoF and provided in a ratio of at least 3 sq. ft. per sq. ft. of south facing fenestration. Generally, thermal mass materials will be at least 2î thick. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-211-ceiling-wall-floor-and-slab-insulat": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 2.1.1 <sup>3 , 4, 5</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Ceiling, wall, floor, and slab insulation levels shall meet or exceed 2009 IECC levels</span></p> <p> </p> <p>Install insulation in a home to meet or exceed the levels specified in the 2009 IECC and located on the back of this page. </p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Verify insulation meets standards by utilizing the guide below, looking at printed R-values on the insulation product or consulting the insulator. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold">COMMON INSULATION MATERIALS</span></p> <a name="0.1_table01"></a> <div style="text-align:center"> <table width="425" style="border-collapse:collapse"> <tr valign="top"><td width="179"><p style="text-align:center"><span style="font-weight:bold">MATERIAL</span></p></td> <td width="139"><p style="text-align:center"><span style="font-weight:bold">APPROX. R-VALUE PER INCH</span></p></td></tr> <tr valign="top"><td><p style="text-align:center">Cellulose</p></td> <td><p style="text-align:center">R-3.5</p></td></tr> <tr valign="top"><td><p style="text-align:center">Fiberglass (Batts)</p></td> <td><p style="text-align:center">R-3.5</p></td></tr> <tr valign="top"><td><p style="text-align:center">Fiberglass (Blown)</p></td> <td><p style="text-align:center">R-3</p></td></tr> <tr valign="top"><td><p style="text-align:center">Polyurethane Rigid Board</p></td> <td><p style="text-align:center">R-6.8</p></td></tr> <tr valign="top"><td><p style="text-align:center">EPS Insulated Concrete Forms (ICF)</p></td> <td><p style="text-align:center">R-4.25</p></td></tr> <tr valign="top"><td><p style="text-align:center">XPS Insulated Concrete Forms (ICF)</p></td> <td><p style="text-align:center">R-5.0</p></td></tr> <tr valign="top"><td><p style="text-align:center">EPS Structurally Insulated Panels (SIP)</p></td> <td><p style="text-align:center">R-3.1</p></td></tr> <tr valign="top"><td><p style="text-align:center">XPS Structurally Insulated Panels (SIP)</p></td> <td><p style="text-align:center">R-4.3</p></td></tr> <tr valign="top"><td><p style="text-align:center">Spray Foam (Closed Cell) </p></td> <td><p style="text-align:center">R-6</p></td></tr> <tr valign="top"><td><p style="text-align:center">Spray Foam (Open Cell) </p></td> <td><p style="text-align:center">R-3.6</p></td></tr> </table> </div> <p> <br></p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>3. Insulation levels in a home shall meet or exceed the component insulation requirements in the 2009 IECC -Table 402.1.1. The following exceptions apply: </p> <p> </p> <ol style="list-style:lower-alpha"> <li style="margin-left:0pt">Steel-frame ceilings, walls, and floors shall meet the insulation requirements of the 2009 IECC ñ Table 402.2.5. In CZ 1 and 2, the continuous insulation requirements in this table shall be permitted to be reduced to R-3 for steel-frame wall assemblies with studs spaced at 24î on center. This exception shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">For ceilings with attic spaces, R-30 shall satisfy the requirement for R-38 and R-38 shall satisfy the requirement for R-49 wherever the full height of uncompressed insulation at the lower R-value extends over the wall top plate at the eaves. This exemption shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">For ceilings without attic spaces, R-30 shall satisfy the requirement for any required value above R-30 if the design of the roof/ceiling assembly does not provide sufficient space for the required insulation value. This exemption shall be limited to 500 square ft. or 20% of the total insulated ceiling area, whichever is less. This exemption shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">An alternative equivalent U-factor or total UA calculation may also be used to demonstrate compliance, as follows: </li> </ol> <p> </p> <ul> <ol style="list-style:lower-roman"> <li style="margin-left:0pt">An assembly with a U-factor equal or less than specified in 2009 IECC Table 402.1.3 complies. </li> </ol> </ul> <p> </p> <ul> <ol style="list-style:lower-roman" start="2"> <li style="margin-left:0pt">A total building thermal envelope UA that is less than or equal to the total UA resulting from the U-factors in Table 402.1.3 also complies. The insulation levels of all non-fenestration components (i.e., ceilings, walls, floors, and slabs) can be traded off using the UA approach under both the Prescriptive and the Performance Path. Note that fenestration products (i.e., windows, skylights, doors) shall not be included in this calculation. Also, note that while ceiling and slab insulation can be included in trade-off calculations, the R-value must meet or exceed the minimum values listed in Items 4.1 through 4.3 of the Checklist to provide an effective thermal break, regardless of the UA tradeoffs calculated. The UA calculation shall be done using a method consistent with the ASHRAE Handbook of Fundamentals and shall include the thermal bridging effects of framing materials. The calculation for a steel-frame envelope assembly shall use the ASHRAE zone method or a method providing equivalent results, and not a series-parallel path calculation method. </li> </ol> </ul> <p> </p> <p>4. Consistent with the 2009 IECC, slab edge insulation is only required for slab-ongrade floors with a floor surface less than 12 inches below grade. Slab insulation shall extend to the top of the slab to provide a complete thermal break. If the top edge of the insulation is installed between the exterior wall and the edge of the interior slab, it shall be permitted to be cut at a 45-degree angle away from the exterior wall. </p> <p>5. Where an insulated wall separates a garage, patio, porch, or other unconditioned space from the conditioned space of the house, slab insulation shall also be installed at this interface to provide a thermal break between the conditioned and unconditioned slab. Where specific details cannot meet this requirement, partners shall provide the detail to EPA to request an exemption prior to the homeís qualification. EPA will compile exempted details and work with industry to develop feasible details for use in future revisions to the program. A list of currently exempted details is available at: <a href="http://www.energystar.gov/slabedge" target="_blank"><span><span style="text-decoration:underline">www.energystar .gov/slabedge</span></span></a>.</p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-212-achieve-133-of-the-total-ua-result": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 2.1.2 <sup>3 , 4, 5</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Ceiling, wall, floor, and slab insulation levels shall meet or exceed 2009 IECC levels</span></p> <p> </p> <p>Install insulation in a home to meet or exceed the levels specified in the 2009 IECC and located on the back of this page. </p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Verify insulation meets standards by utilizing the guide below, looking at printed R-values on the insulation product or consulting the insulator. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold">COMMON INSULATION MATERIALS</span></p> <a name="0.1_table01"></a> <div style="text-align:center"> <table width="425" style="border-collapse:collapse"> <tr valign="top"><td width="179"><p style="text-align:center"><span style="font-weight:bold">MATERIAL</span></p></td> <td width="139"><p style="text-align:center"><span style="font-weight:bold">APPROX. R-VALUE PER INCH</span></p></td></tr> <tr valign="top"><td><p style="text-align:center">Cellulose</p></td> <td><p style="text-align:center">R-3.5</p></td></tr> <tr valign="top"><td><p style="text-align:center">Fiberglass (Batts)</p></td> <td><p style="text-align:center">R-3.5</p></td></tr> <tr valign="top"><td><p style="text-align:center">Fiberglass (Blown)</p></td> <td><p style="text-align:center">R-3</p></td></tr> <tr valign="top"><td><p style="text-align:center">Polyurethane Rigid Board</p></td> <td><p style="text-align:center">R-6.8</p></td></tr> <tr valign="top"><td><p style="text-align:center">EPS Insulated Concrete Forms (ICF)</p></td> <td><p style="text-align:center">R-4.25</p></td></tr> <tr valign="top"><td><p style="text-align:center">XPS Insulated Concrete Forms (ICF)</p></td> <td><p style="text-align:center">R-5.0</p></td></tr> <tr valign="top"><td><p style="text-align:center">EPS Structurally Insulated Panels (SIP)</p></td> <td><p style="text-align:center">R-3.1</p></td></tr> <tr valign="top"><td><p style="text-align:center">XPS Structurally Insulated Panels (SIP)</p></td> <td><p style="text-align:center">R-4.3</p></td></tr> <tr valign="top"><td><p style="text-align:center">Spray Foam (Closed Cell) </p></td> <td><p style="text-align:center">R-6</p></td></tr> <tr valign="top"><td><p style="text-align:center">Spray Foam (Open Cell) </p></td> <td><p style="text-align:center">R-3.6</p></td></tr> </table> </div> <p> <br></p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>3. Insulation levels in a home shall meet or exceed the component insulation requirements in the 2009 IECC -Table 402.1.1. The following exceptions apply: </p> <p> </p> <ol style="list-style:lower-alpha"> <li style="margin-left:0pt">Steel-frame ceilings, walls, and floors shall meet the insulation requirements of the 2009 IECC ñ Table 402.2.5. In CZ 1 and 2, the continuous insulation requirements in this table shall be permitted to be reduced to R-3 for steel-frame wall assemblies with studs spaced at 24î on center. This exception shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">For ceilings with attic spaces, R-30 shall satisfy the requirement for R-38 and R-38 shall satisfy the requirement for R-49 wherever the full height of uncompressed insulation at the lower R-value extends over the wall top plate at the eaves. This exemption shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">For ceilings without attic spaces, R-30 shall satisfy the requirement for any required value above R-30 if the design of the roof/ceiling assembly does not provide sufficient space for the required insulation value. This exemption shall be limited to 500 square ft. or 20% of the total insulated ceiling area, whichever is less. This exemption shall not apply if the alternative calculations in d) are used; </li> <li style="margin-left:0pt">An alternative equivalent U-factor or total UA calculation may also be used to demonstrate compliance, as follows: </li> </ol> <p> </p> <ul> <ol style="list-style:lower-roman"> <li style="margin-left:0pt">An assembly with a U-factor equal or less than specified in 2009 IECC Table 402.1.3 complies. </li> </ol> </ul> <p> </p> <ul> <ol style="list-style:lower-roman" start="2"> <li style="margin-left:0pt">A total building thermal envelope UA that is less than or equal to the total UA resulting from the U-factors in Table 402.1.3 also complies. The insulation levels of all non-fenestration components (i.e., ceilings, walls, floors, and slabs) can be traded off using the UA approach under both the Prescriptive and the Performance Path. Note that fenestration products (i.e., windows, skylights, doors) shall not be included in this calculation. Also, note that while ceiling and slab insulation can be included in trade-off calculations, the R-value must meet or exceed the minimum values listed in Items 4.1 through 4.3 of the Checklist to provide an effective thermal break, regardless of the UA tradeoffs calculated. The UA calculation shall be done using a method consistent with the ASHRAE Handbook of Fundamentals and shall include the thermal bridging effects of framing materials. The calculation for a steel-frame envelope assembly shall use the ASHRAE zone method or a method providing equivalent results, and not a series-parallel path calculation method. </li> </ol> </ul> <p> </p> <p>4. Consistent with the 2009 IECC, slab edge insulation is only required for slab-ongrade floors with a floor surface less than 12 inches below grade. Slab insulation shall extend to the top of the slab to provide a complete thermal break. If the top edge of the insulation is installed between the exterior wall and the edge of the interior slab, it shall be permitted to be cut at a 45-degree angle away from the exterior wall. </p> <p>5. Where an insulated wall separates a garage, patio, porch, or other unconditioned space from the conditioned space of the house, slab insulation shall also be installed at this interface to provide a thermal break between the conditioned and unconditioned slab. Where specific details cannot meet this requirement, partners shall provide the detail to EPA to request an exemption prior to the homeís qualification. EPA will compile exempted details and work with industry to develop feasible details for use in future revisions to the program. A list of currently exempted details is available at: <a href="http://www.energystar.gov/slabedge" target="_blank"><span><span style="text-decoration:underline">www.energystar .gov/slabedge</span></span></a>.</p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-22-all-ceiling-wall-floor-and-slab-insul": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 2.2</span></p> <p style="text-align:center"><span style="font-weight:bold">All ceiling, wall, floor, and slab insulation shall achieve RESNET-defined Grade I installation or, alternatively, Grade II for surfaces with insulated sheathing (see Checklist Item 4.4.1 for required insulation levels)</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all wall cavities along the thermal barrier of the house. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">WHAT IS GRADE I INSTALLATION?</span></p> <p>Grade I installation requires that the insulation material uniformly fill each cavity side-to-side and top-to-bottom, without substantial gaps, or voids around obstructions (such as blocking or bridging), and be split, installed, and/or fitted tightly around wiring and other services in the cavity. </p> <p> </p> <p>To attain a rating of Grade I, wall insulation shall be enclosed on all six sides, and shall be in substantial contact with the sheathing material on at least one side (interior or exterior) of the cavity. </p> <p> </p> <p>For faced batt insulation, Grade I can be designated for side-stapled tabs, provided the tabs are stapled neatly (no buckling), and provided the batt is only compressed at the edges of each cavity, to the depth of the tab itself, and provided the batt meets the other requirements of Grade I. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">HOW DO RATERS INSPECT INSULATION?</span></p> <p>Raters are required to inspect and probe in, around, or through the insulation and/ or vapor retarder in several places to see whether these requirements are met. </p> <p> </p> <p>During inspection, insulation and vapor retarders may be cut or pulled away so Raters can see installation details. The Raters should replace or repair the vapor retarder and insulation as necessary. During inspection (typically before drywall is installed), if the exterior sheathing is visible from the building interior through gaps in the cavity insulation material, it is not considered a Grade I installation. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">IDEAL INSTALLATION OF INSULATION</span></p> <p>Properly installed insulation consists of insulation framed on all six sides, including top and bottom plates, rigid backing, and sheathing. The insulator should ensure that framing is correctly installed before the start of insulation. </p> <p style="margin-left:36pt"><span style="font-weight:bold">Progression from least ideal to best design:</span></p> <p style="margin-left:36pt">1. No top or bottom plate and no backing</p> <p style="margin-left:36pt">2. Bottom plate, but no top plate or backing</p> <p style="margin-left:36pt">3. Top and bottom plate, but no backing</p> <p style="margin-left:36pt">4. Insulation surrounded on six sides, including a top and bottom plate and backing</p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-311-walls-behind-showers-and-tubs": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.1 <sup>6, 7, 10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Walls behind showers and tubs</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all exterior wall cavities behind all tubs and showers. </li> <li style="margin-left:0pt">Back with a rigid air barrier or other supporting material to prevent insulation from sagging and create a continuous thermal barrier.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam before tub/shower installation. </li> </ol> <p>* EPA recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-312-walls-behind-fireplaces": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.2 <sup>6, 7, 10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Walls behind fireplaces</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all exterior wall cavities behind all fireplaces. </li> <li style="margin-left:0pt">Back with a fire-proof rigid air barrier or other supporting material to create a continuous thermal barrier and prevent a fire hazard.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with fire-rated caulk or foam before fireplace installation. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-313-attic-knee-walls": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.3 <sup>6, 7, 10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Attic knee walls</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a top and bottom plate or blocking at the top and bottom of all knee wall cavities. </li> <li style="margin-left:0pt">Back attic knee walls with a rigid air barrier or other supporting material to prevent insulation from sagging and create a continuous thermal barrier .* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all knee wall cavities. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-314-skylight-shaft-walls": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.4 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Skylight shaft walls</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">If non-rigid insulation is used, install a rigid air barrier to prevent insulation from sagging and create a continuous thermal barrier.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam. </li> <li style="margin-left:0pt">Install the insulation without any misalignments, compressions, gaps, or voids so that it acts as both the air barrier and thermal boundary. Examples include foam board, spray foam or dense pack insulation. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-315-wall-adjoining-porch-roof": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.5 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Wall adjoining porch roof</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a rigid air barrier or other supporting material to separate the porch attic from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam before building wrap installation. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-316-staircase-walls": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.6 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Staircase walls</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all exterior wall cavities underneath all staircases. </li> <li style="margin-left:0pt">Install a rigid air barrier to prevent insulation from sagging and create a continuous thermal barrier.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-317-double-walls": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.8 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Garage rim/band joist adjoining conditioned space</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to separate the garage from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam and complete before installing the insulation. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all band joist cavities. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-318-garage-rim-band-joist-adjoining-con": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.8 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Garage rim/band joist adjoining conditioned space</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to separate the garage from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam and complete before installing the insulation. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all band joist cavities. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-319-all-other-exterior-walls": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.1.9 <sup>6, 7,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">All other exterior walls</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to separate the exterior from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam and complete before installing the insulation. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all exterior walls. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement.</p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>7. EPA highly recommends, but does not require, inclusion of an interior air barrier at band joists in Climate Zone 4 through 8. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-321-floor-above-garage": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.2.1 <sup>6, 8, 9</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Floor above garage</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to separate the garage from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam and complete before insulation installation. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in all floors above garage. </li> <li style="margin-left:0pt">Install supports for insulation to remain in contact with the air barrier. </li> </ol> <p><span style="font-style:italic">Examples of supports include staves for batt insulation or netting for blown-in insulation. </span></p> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>8. Examples of supports necessary for permanent contact include staves for batt insulation or netting for blown-in insulation. Batts that completely fill a cavity enclosed on all six sides may be used to meet this requirement without the need for supports, even though some compression will occur due to the excess insulation, as long as the compressed value meets or exceeds the required insulation level. Specifically, the following batts may be used in six-sided floor cavities: R-19 batts in 2x6 cavities, R-30 batts in 2x8 cavities, R-38 batts in 2x10 cavities, and R-49 batts in 2x12 cavities. For example, in a home that requires R-19 floor insulation, an R-30 batt may be used in a six-sided 2x8 floor cavity. </p> <p>9. Fully-aligned air barriers may be installed at the exterior surface of the floor cavity in all Climate Zones if the insulation is installed in contact with this exterior air barrier and the perimeter rim and band joists of the floor cavity are also sealed and insulated to comply with the fully-aligned air barrier requirements for walls. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-322-cantilevered-floor": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.2.2 <sup>6, 8, 9</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Cantilevered floor</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a rigid air barrier or other supporting blocking to separate the cantilever from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids and align it with the sub-floor, the rigid air barrier (A), and the exterior face of the cavity. </li> <li style="margin-left:0pt">Once insulated, enclose the cavity with a rigid air barrier material. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>8. Examples of supports necessary for permanent contact include staves for batt insulation or netting for blown-in insulation. Batts that completely fill a cavity enclosed on all six sides may be used to meet this requirement without the need for supports, even though some compression will occur due to the excess insulation, as long as the compressed value meets or exceeds the required insulation level. Specifically, the following batts may be used in six-sided floor cavities: R-19 batts in 2x6 cavities, R-30 batts in 2x8 cavities, R-38 batts in 2x10 cavities, and R-49 batts in 2x12 cavities. For example, in a home that requires R-19 floor insulation, an R-30 batt may be used in a six-sided 2x8 floor cavity. </p> <p>9. Fully-aligned air barriers may be installed at the exterior surface of the floor cavity in all Climate Zones if the insulation is installed in contact with this exterior air barrier and the perimeter rim and band joists of the floor cavity are also sealed and insulated to comply with the fully-aligned air barrier requirements for walls. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-323-floor-above-unconditioned-basement-or": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.2.3 <sup>6, 8, 9</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Floor above unconditioned basement or unconditioned crawlspace</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to separate the exterior from the conditioned space.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam. </li> <li style="margin-left:0pt">Install insulation without misalignments, compressions, gaps, or voids in floors above the unconditioned basement or unconditioned crawlspace. </li> <li style="margin-left:0pt">Install supports for insulation to remain in contact with the air barrier. Examples include metal support rods for batt insulation or netting for blown insulation. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>8. Examples of supports necessary for permanent contact include staves for batt insulation or netting for blown-in insulation. Batts that completely fill a cavity enclosed on all six sides may be used to meet this requirement without the need for supports, even though some compression will occur due to the excess insulation, as long as the compressed value meets or exceeds the required insulation level. Specifically, the following batts may be used in six-sided floor cavities: R-19 batts in 2x6 cavities, R-30 batts in 2x8 cavities, R-38 batts in 2x10 cavities, and R-49 batts in 2x12 cavities. For example, in a home that requires R-19 floor insulation, an R-30 batt may be used in a six-sided 2x8 floor cavity. </p> <p>9. Fully-aligned air barriers may be installed at the exterior surface of the floor cavity in all Climate Zones if the insulation is installed in contact with this exterior air barrier and the perimeter rim and band joists of the floor cavity are also sealed and insulated to comply with the fully-aligned air barrier requirements for walls. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-331-dropped-ceiling-soffit-below-uncond": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.3.1 <sup>6,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">Dropped ceiling/soffit below unconditioned attic</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install a continuous rigid air barrier or other supporting material to cap the dropped ceiling and soffits.* </li> <li style="margin-left:0pt">Seal all seams, gaps, and holes of the air barrier with caulk or foam before installation of attic insulation. </li> </ol> <p>* EPA highly recommends using a rigid air barrier, but it is not a requirement. </p> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-332-all-other-ceilings": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 3.3.2 <sup>6,10</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">All other ceilings</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">At interior or exterior surface of ceilings in Climate Zones 1-3; at interior surface of ceilings in Climate Zones 4-8. Also, include barrier at interior edge of attic eave in all climate zones using a wind baffle that extends to the full height of the insulation. Include a baffle in every bay or a tabbed baffle in each bay with a soffit vent that will also prevent wind washing of insulation in adjacent bays. </li> <li style="margin-left:0pt">Install wind baffles with the minimum code required clearance between baffle and roof deck.</li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>6. For purposes of this checklist, an air barrier is defined as any durable solid material that blocks air flow between conditioned space and unconditioned space, including necessary sealing to block excessive air flow at edges and seams and adequate support to resist positive and negative pressures without displacement or damage. EPA recommends, but does not require, rigid air barriers. Open-cell or closed-cell foam shall have a finished thickness = 5.5î or 1.5î, respectively, to qualify as an air barrier unless the manufacturer indicates otherwise. If flexible air barriers such as house wrap are used, they shall be fully sealed at all seams and edges and supported using fasteners with caps or heads = 1î diameter unless otherwise indicated by the manufacturer. Flexible air barriers shall not be made of kraft paper, paper-based products, or other materials that are easily torn. If polyethylene is used, its thickness shall be = 6 mil. </p> <p>10. All insulated vertical surfaces are considered walls (e.g., exterior walls, knee walls) and must meet the air barrier requirements for walls. All insulated ceiling surfaces, regardless of slope (e.g., cathedral ceilings, tray ceilings, conditioned attic roof decks, flat ceilings, sloped ceilings), must meet the requirements for ceilings. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-41-for-insulated-ceilings-with-attic-space": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 4.1 <sup>11</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">For insulated ceilings with attic space above (i.e., non-cathedralized ceilings), Grade I insulation extends to the inside face of the exterior wall below at the following levels: CZ 1 to 5: = R-21; CZ 6 to 8: = R-30</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install raised-heel trusses or equivalent framing method to allow the specified attic insulation R-value to be installed at the inside face of the exterior wall below (extending over the top plate). </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>11. The minimum designated R-values must be achieved regardless of the trade-offs determined using an equivalent U-factor or UA alternative calculation. Note that if the minimum designated values are used, they must be compensated with higher values elsewhere using an equivalent U-factor or UA alternative calculation in order to meet the overall insulation requirements of the 2009 IECC. Also, note that these requirements can be met by using any available strategy, such as a raised-heel truss, alternate framing that provides adequate space, and/or high-density insulation. In Climate Zones 1 through 3, one option that will work for most homes is to use 2x6 framing, an R-21 high-density batt, and a wind baffle that only requires 0.5î of clearance. </p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-42-for-slabs-on-grade-in-cz-4-and-higher-1": """<p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">DETAIL 4.2 <sup>4, 5</sup></span> </p> <p style="text-align:center"><span style="font-weight:bold">For slabs on grade in CZ 4 and higher, 100% of slab edge insulated to = R-5 at the depth specified by the 2009 IECC and aligned with thermal boundary of the walls</span></p> <ol style="list-style:upper-alpha"> <li style="margin-left:0pt">Install slab edge insulation to extend to the top of the slab so it provides a complete thermal break. </li> </ol> <p> </p> <p style="text-align:center"><span style="font-weight:bold; text-decoration:underline">FOOTNOTES</span></p> <p>4. Consistent with the 2009 IECC, slab edge insulation is only required for slab-on-grade floors with a floor surface less than 12 inches below grade. Slab insulation shall extend to the top of the slab to provide a complete thermal break. If the top edge of the insulation is installed between the exterior wall and the edge of the interior slab, it shall be permitted to be cut at a 45-degree angle away from the exterior wall. </p> <p>5. Where an insulated wall separates a garage, patio, porch, or other unconditioned space from the conditioned space of the house, slab insulation shall also be installed at this interface to provide a thermal break between the conditioned and unconditioned slab. Where specific details cannot meet this requirement, partners shall provide the detail to EPA to request an exemption prior to the homeís qualification. EPA will compile exempted details and work with industry to develop feasible details for use in future revisions to the program. A list of currently exempted details is available at: <a href="http://www.enegystar.gov/slabedge" target="_blank"><span><span style="text-decoration:underline">www.enegystar .gov/slabedge</span></span></a>.</p> <p> </p> <p style="text-align:center"></p>""",
            "te-r-43-insulation-beneath-attic-platforms-eg": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.3</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Insulation
            beneath attic platforms (e.g., HVAC platforms, walkways)
            = R-21 in CZ 1 to 5; &ge; R-30 in CZ 6 to 8</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Increase
              the height of the storage or HVAC platform in the attic to allow for
              proper depth of the insulation beneath the platform without compressing
              the insulation. </li>
              <li style="margin-left:0pt">Install
              insulation without misalignments, compressions, gaps, or voids underneath
              all attic platforms. </li>

              <li style="margin-left:0pt">Install
              insulation so that it is in contact with the air barrier (e.g., drywall
              ceiling) </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-441-reduced-thermal-bridging-at-above-grade": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.1 <sup>12,13,14,15</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">Continuous rigid
            insulation, insulated siding, or i.e., 1 to 4 combination
            of the two; &ge; R-3 in Climate Zones 1 to 4, &ge; R-5 in Climate Zones
            5 to 8*</span></p>

            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">If utilizing
              insulated siding that is not water-resistant barrier,
              install a water-resistant
              barrier before installing siding. </li>
              <li style="margin-left:0pt">If using
              steel studs, install continuous rigid insulation of &ge; R-3 in CZ 1
              to 4 or &ge; R-5 in CZ 5 to 8. </li>
              <li style="margin-left:0pt">Tape
              and seal all seams of continuous rigid insulation if it is being utilized
              as a water-resistant barrier. </li>
            </ol>
            <p>* Only one item of 4.4.1-4.4.5 must be installed
            to comply with ENERGY STAR. If the building utilizes steel framing,
            this requirement must be met. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>

            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>
            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p>14. If used, insulated siding shall be attached
            directly over a water-resistive barrier and sheathing. In addition,
            it shall provide the required R-value as demonstrated through either
            testing in accordance with ASTM C 1363 or by attaining the required
            R-value at its minimum thickness. Insulated sheathing rated for water
            protection can be used as a water resistant barrier if all seams are
            taped and sealed. If non-insulated structural sheathing is used at corners,
            advanced framing details listed under Item 4.4.5 shall be met for those
            wall sections. </p>

            <p>15. Steel framing shall meet the reduced thermal
            bridging requirements by complying with Item 4.4.1 of the Checklist. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-442-structural-insulated-panels-sips-or": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.2 <sup>12,13</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">Structural
            insulated panels (SIPs)*</span></p>
            <ol style="list-style:upper-alpha">

              <li style="margin-left:0pt">Install
              SIPs according to manufacturer specifications to create a continuous
              air barrier and thermal boundary. </li>
              <li style="margin-left:0pt">All
              seams between Structural Insulated Panels (SIPs) foamed and/or taped
              per manufacturer&#39;s specifications. </li>
            </ol>
            <p>* Only one item of 4.4.1-4.4.5 must be installed
            to comply with ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>

            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-443-insulated-concrete-forms-icfs-or-s": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.3 <sup>12,13</sup></span>
            </p>

            <p style="text-align:center"><span style="font-weight:bold">Insulated
            concrete forms (ICFs)*</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              ICFs according to manufacturer specifications to create a continuous
              air barrier and thermal boundary. </li>
            </ol>
            <p>* Only one item of 4.4.1-4.4.5 must be installed
            to comply with ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>

            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-444-double-wall-framing-or-see-next-ques": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.4 <sup>12,13,16</sup></span>
            </p>

            <p style="text-align:center"><span style="font-weight:bold">Double-wall
            framing*</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a continuous air barrier on the exterior of the interior wall. </li>
              <li style="margin-left:0pt">Seal
              all seams, gaps, and holes of the air barrier with caulk or foam. </li>
              <li style="margin-left:0pt">Install
              insulation without misalignments, compressions, gaps, or voids. </li>
            </ol>
            <p style="margin-left:36pt"><span style="font-weight:bold">OR</span></p>
            <ol style="list-style:upper-alpha" start="4">
              <li style="margin-left:0pt">Completely
              fill entire cavity of the double wall assembly without misalignments,
              compressions, gaps, or voids. </li>

            </ol>
            <p>* Only one item of 4.4.1-4.4.5 must be installed
            to comply with ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>
            <p> </p>

            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p>16. Double-wall framing is defined as any
            framing method that ensures a continuous layer of insulation covering
            the studs to at least the R-value required in Section 4.4.1 of the Checklist,
            such as offset double-stud walls, aligned double-stud walls with continuous
            insulation between the adjacent stud faces, or single-stud walls with
            2x2 or 2x3 cross-framing. In all cases, insulation shall fill the entire
            wall cavity from the interior to exterior sheathing except at windows,
            doors, and other penetrations. </p>
            <p> </p>
            <p style="text-align:center">/p>""",
            "te-r-445a-all-corners-insulated-r-6-to-edge": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.5a <sup>12,13,17</sup></span>

            </p>
            <p style="text-align:center"><span style="font-weight:bold">All corners
            insulated &ge; R-6 to edge*</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Utilize
              recessed corners or an equivalent framing technique that uses no more
              than three studs per corner to allow access to insulate the cavity to
              &ge; R-6. </li>
              <li style="margin-left:0pt">If the
              corner is conventionally framed, drill a hole and fill the cavity with
              insulation. </li>
            </ol>
            <p>* All items of 4.4.5a-4.4.5e must be installed
            to comply with 4.4.5 and ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>

            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>
            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge; 50% of the applicable
            component insulation requirement in the 2009 IECC - Table 402.1.1. </p>
            <p> </p>

            <p>17. All exterior corners shall be constructed
            to allow access for the installation of &ge; R-6 insulation that extends
            to the exterior wall sheathing. Examples of compliance options include
            standard-density insulation with alternative framing techniques, such
            as using three studs per corner, or high-density insulation (e.g., spray
            foam) with standard framing techniques. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-445b-all-headers-above-windows-doors-insu": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.5b <sup>12,13,18</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">All headers above
             windows and doors insulated*</span></p>

            <p>Install headers with a minimum R-3 insulation
            value in wall assemblies with 2x4 framing, or equivalent width, and
            R-5 for all other assemblies (e.g., with 2x6 framing). Use one of the
            methods listed below or an equivalent assembly: </p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Continuous
              rigid insulation sheathing. </li>
              <li style="margin-left:0pt">SIP
              headers. </li>
              <li style="margin-left:0pt">Two-member
              headers with insulation in between. </li>
              <li style="margin-left:0pt">Single-member
              headers with insulation on one side. </li>
            </ol>
            <p>* All items of 4.4.5a-4.4.5e must be installed
            to comply with 4.4.5 and ENERGY STAR. </p>

            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>
            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>

            <p> </p>
            <p>18. Header insulation shall be &ge; R-3 for
            wall assemblies with 2x4 framing, or equivalent cavity width, and &ge;
            R-5 for all other assemblies (e.g., with 2x6 framing). Compliance options
            include continuous rigid insulation sheathing, SIP headers, other prefabricated
            insulated headers, single-member or two-member headers with insulation
            either in between or on one side, or an equivalent assembly, except
            where a framing plan provided by the builder, architect, designer, or
            engineer indicates that full-depth solid headers are the only acceptable
            option. The Rater need not evaluate the structural necessity of the
            details in the framing plan to qualify the home. Also, the framing plan
            need only encompass the details in question and not necessarily the
            entire home. R-value requirement refers to manufacturer's nominal
            insulation value. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-445c-framing-limited-at-all-windows-doors": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.5c <sup>12,13,19</sup></span>

            </p>
            <p style="text-align:center"><span style="font-weight:bold">Framing limited
            at all windows and doors*</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Limit
              framing to a maximum of one pair of king studs per window opening. </li>
              <li style="margin-left:0pt">Limit
              framing to a maximum of one pair of jack studs per window opening to
              support the header and window sill. </li>
              <li style="margin-left:0pt">Install
              additional jack studs only as needed for structural support and cripple
              studs only as needed to maintain on-center spacing of studs. </li>
              <li style="margin-left:0pt">Limit
              framing to necessary structural requirements for each door opening. </li>
            </ol>

            <p>* All items of 4.4.5a-4.4.5e must be installed
            to comply with 4.4.5 and ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>.</p>
            <p> </p>

            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p>19. Framing at windows shall be limited to
            a maximum of one pair of king studs and one pair jack studs per window
            opening to support the header and window sill. Additional jack studs
            shall be used only as needed for structural support and cripple studs
            only as needed to maintain on-center spacing of studs. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-445d-all-interior-exterior-wall-intersect": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.5d <sup>12,13,20</sup></span>

            </p>
            <p style="text-align:center"><span style="font-weight:bold">All
            interior/exterior wall intersections insulated to the same R-value
            as the rest of the exterior wall*</span></p>
            <p>Install insulation to run continuously behind
            interior/exterior wall intersections. Use one of the methods listed
            below or an equivalent assembly: </p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Ladder
              blocking. </li>
              <li style="margin-left:0pt">Full
              length 2 x 6 or 1 x 6 nailer behind the first partition stud. </li>
            </ol>
            <p>* All items of 4.4.5a-4.4.5e must be installed
            to comply with 4.4.5 and ENERGY STAR. </p>
            <p> </p>

            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>. </p>
            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>

            <p>20. Insulation shall run behind interior/exterior
            wall intersections using ladder blocking, full length 2"x6"
            or 1"x6" furring behind the first partition stud, drywall clips,
            or other equivalent alternative. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-445e-minimum-stud-spacing-of-16-in-oc-fo": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 4.4.5e <sup>12,13,21</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">Minimum stud
            spacing of 16&quot; o.c. for 2 x 4 walls in all Climate
            Zones and, in Climate Zones 5 through 8, 24&quot; o.c. for 2 x 6 framing
            unless construction documents specify other spacing is structurally
            required</span></p>

            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">16"
              for 2 x 4 framing on center in all Climate Zones. </li>
              <li style="margin-left:0pt">24"
              for 2 x 6 framing on center in Climate Zones 5 to 8. </li>
            </ol>
            <p>* All items of 4.4.5a-4.4.5e must be installed
            to comply with 4.4.5 and ENERGY STAR. </p>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>12. Up to 10% of the total exterior wall surface
            area is exempted from the reduced thermal bridging requirements to accommodate
            intentional designed details (e.g., architectural details such as thermal
            fins, wing walls, or masonry fireplaces; structural details, such as
            steel columns). It shall be apparent to the Rater that the exempted
            areas are intentional designed details or the exempted area shall be
            documented in a plan provided by the builder, architect, designer, or
            engineer. The Rater need not evaluate the necessity of the designed
            detail to qualify the home. </p>
            <p>13. Mass walls utilized as the thermal mass
            component of a passive solar design (e.g., a Trombe wall) are exempt
            from this item. To be eligible for this exemption, the passive solar
            design shall be comprised of the following five components: an aperture
            or collector, an absorber, thermal mass, a distribution system, and
            a control system. For more information, see: <a href="http://www.energysavers
            .gov/your_home/designing_remodeling/index.cfm/mytopic=10270"
            target="_blank"><span><span style="text-decoration:underline">http://www
            .energysavers.gov/<WBR>your_home/designing_<WBR>remodeling/index
            .cfm/mytopic=<WBR>10270</span></span></a>. </p>

            <p> </p>
            <p>Mass walls that are not part of a passive
            solar design (e.g., CMU block or log home enclosure) shall either utilize
            the strategies outlined in Section 4.4 or the pathway in the assembly
            with the least thermal resistance shall provide &ge;50% of the applicable
            component insulation requirement in the 2009 IECC -Table 402.1.1. </p>
            <p> </p>
            <p>21. Vertical framing members shall either
            be on-center or have an alternative structural purpose (e.g., framing
            members at the edge of pre-fabricated panels) that is apparent to the
            Rater or documented in a framing plan provided by the builder, architect,
            designer, or engineer. The Rater need not evaluate the structural necessity
            of the details in the framing plan to qualify the home. Also, the framing
            plan need only encompass the details in question and not necessarily
            the entire home. No more than 5% of studs may lack an apparent or documented
            structural purpose, which is equivalent to one vertical stud for every
            30 linear feet of wall, assuming 16" o.c. stud spacing. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-511-duct-flue-shaft": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.1.1</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Duct / flue
            shaft</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a continuous rigid air barrier material to separate the exterior from
              the conditioned space.* </li>
              <li style="margin-left:0pt">Using
              a saw or drill, cleanly cut all penetrating holes no more than 1 inch
              larger in diameter than the penetrating object to allow for proper air
              sealing. </li>

              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. Fibrous
              insulation is not an air barrier and cannot be used for sealing gaps. </li>
              <li style="margin-left:0pt">Use
              high temperature caulking along with flashing or UL-rated collars. Install
              them continuously around all combustion flues while maintaining proper
              clearance from combustion materials. </li>
            </ol>
            <p>* EPA recommends using a rigid air barrier,
            but it is not a requirement. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-512-plumbing-piping": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.1.2</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Plumbing /
            piping</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Using
              a saw or drill, cleanly cut all penetrating holes no more than 1 inch
              larger in diameter than the penetrating object to allow for proper air
              sealing. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. Fibrous
              insulation is not an air barrier and cannot be used for sealing gaps. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-513-electrical-wiring": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.1.3</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Electrical
            wiring</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Using
              a saw or drill, cleanly cut all penetrating holes no more than 1 inch
              larger in diameter than the penetrating object to allow for proper air
              sealing. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. Fibrous
              insulation is not an air barrier and cannot be used for sealing gaps. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-514-bathroom-and-kitchen-exhaust-fans": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.1.4</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Bathroom and
            kitchen exhaust fans</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Using
              a saw or drill, cleanly cut all penetrating holes no more than 1 inch
              larger in diameter than the penetrating object to allow for proper air
              sealing. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. Fibrous
              insulation is not an air barrier and cannot be used for sealing gaps. </li>
            </ol>
            <p> </p>

            <p style="text-align:center"></p>""",
            "te-r-515-recessed-lighting-fixtures-adjacent-to": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL  5.1.5</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Recessed lighting
             fixtures adjacent to unconditioned space ICAT labeled
            and fully gasketed. Also, if in insulated ceiling without attic above,
            exterior surface of fixture insulated to &ge; R-10 in CZ 4 and higher
            to minimize condensation potential.</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              ICAT labeled recessed lighting fixtures. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. </li>

              <li style="margin-left:0pt">Install
              a proper trim kit with a gasket. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-516-light-tubes-adjacent-to-unconditioned-s": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.1.6 <sup>22</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">Light tubes
            adjacent to unconditioned space include lens separating
            unconditioned and conditioned space and are fully gasketed</span></p>

            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. </li>
              <li style="margin-left:0pt">Install
              a proper lens kit with a gasket. </li>
              <li style="margin-left:0pt">If the
              light tube does not have a lens kit with a gasket, install a light tube
              with at least R-6 insulation around the length of the tube. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>22. Light tubes that do not include a gasketed
            lens are required to be sealed and insulated &ge; R-6 for the length
            of the tube. </p>

            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-521-all-sill-plates-adjacent-to-conditioned": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.1</span></p>
            <p style="text-align:center"><span style="font-weight:bold">All sill plates
            adjacent to conditioned space sealed to foundation
            or sub-floor with caulk. Foam gasket also placed beneath sill plate
            if resting atop concrete or masonry and adjacent to conditioned
            space</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Locate
              all sill plates of all exterior walls, common walls, and vertical members
              at foundation step downs. </li>
              <li style="margin-left:0pt">Install
              a gasket to prevent air leakage and seal all exterior wall sill plates
              to the sub-floor or foundation to prevent air leakage.</li>

            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-522-at-top-of-walls-adjoining-unconditione": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL  5.2.2</span></p>
            <p style="text-align:center"><span style="font-weight:bold">At top of walls
            adjoining unconditioned spaces, continuous top plates
            or sealed blocking using caulk, foam, or equivalent material</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a continuous top plate at all full height walls. </li>

              <li style="margin-left:0pt">Where
              there is no continuous top plate, install blocking and seal. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-523-drywall-sealed-to-top-plate-at-all-unc": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.3</span></p>
            <p style="text-align:center"><span style="font-weight:bold">Drywall sealed
            to top plate at all unconditioned attic / wall interfaces using caulk,
            foam, drywall adhesive (but not other construction adhesives), or equivalent material. Either apply sealant directly between
            drywall and top plate or to the seam between the two from the attic
            above.</span></p>
            <ol style="list-style:upper-alpha">

              <li style="margin-left:0pt">Before
              insulating the attic, seal all top plate to interior cladding connections
              with latex foam or caulk to stop air leakage between conditioned and
              unconditioned space. </li>
            </ol>
            <p style="margin-left:36pt"><span style="font-weight:bold">OR </span></p>
            <ol style="list-style:upper-alpha" start="2">
              <li style="margin-left:0pt">Before
              installing drywall, use spray foam sealant or gasket product on top
              plate to air seal once drywall is installed. If this method is used,
              make sure foam/gasket remains intact during drywall installation. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-524-rough-opening-around-windows-exterior": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.4 <sup>23</sup></span>
            </p>
            <p style="text-align:center"><span style="font-weight:bold">Rough opening
            around windows and exterior doors sealed with caulk
            or foam</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              backer rod or low-expansion foam in openings around windows and doors. </li>
              <li style="margin-left:0pt">Fibrous
              insulation is not an air barrier and cannot be used for sealing gaps. </li>
              <li style="margin-left:0pt">Avoid
              using typical expansion foam as it might interfere with the functioning
              of the window or door.</li>

            </ol>
            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>23. In Climate Zones 1 through 3, stucco over
            rigid insulation tightly sealed to windows and doors shall be considered
            equivalent to sealing rough openings with caulk or foam. </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-525-marriage-joints-between-modular-home-mo": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.5</span></p>

            <p style="text-align:center"><span style="font-weight:bold">Marriage joints
            between modular home modules at all exterior boundary
            conditions fully sealed with gasket and foam</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a gasket along the entire seam of the exterior boundary where modules
              are attached together. </li>
              <li style="margin-left:0pt">When
              modules are in place, seal the edge of the gasket to the module. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-526-all-seams-between-structural-insulated": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.6</span></p>
            <p style="text-align:center"><span style="font-weight:bold">All seams between
             structural insulated Panels (SIPs) foamed and/or
            taped per manufacturer's instructions</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Apply
              manufacturer-approved sealant inside the joints of all panels and at
              sub-floor or foundation connections. </li>
              <li style="margin-left:0pt">When
              applying tape to walls, center on joints and provide overlap of tape
              to meet manufacturer's specifications. </li>
              <li style="margin-left:0pt">When
              applying tape to roof panels, start from the lowest point of the panel
              and continue upward. </li>
            </ol>
            <p> </p>

            <p style="text-align:center"></p>""",
            "te-r-527-in-multi-family-buildings-the-gap-bet": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.2.7</span></p>
            <p style="text-align:center"><span style="font-weight:bold">In multifamily
            buildings, the gap between the drywall shaft wall (i.e.
            common wall) and the structural framing between units fully sealed at
            all exterior boundaries</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">The
              gap between walls must be declared an approved assembly before being
              air sealed. </li>
              <li style="margin-left:0pt">Seal
              the bottom plate to sub-floor. </li>

              <li style="margin-left:0pt">Seal
              the bottom plate to sheathing connection. </li>
              <li style="margin-left:0pt">Seal
              gap between units from exterior at all common wall locations with caulk,
              foam, or equivalent material. (Typically fire rated foam is required
              by code). </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-531-doors-adjacent-to-unconditioned-space": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.3.1</span></p>

            <p style="text-align:center"><span style="font-weight:bold">Doors adjacent to
             unconditioned space (e.g., attics, garages, basements)
            or ambient conditions gasketed or made substantially air-tight</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a continuous gasket, such as weather stripping, around all exterior
              door openings. </li>
            </ol>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-532-attic-access-panels-and-drop-down-stair": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.3.2 <sup>24</sup></span>

            </p>
            <p style="text-align:center"><span style="font-weight:bold">Attic access
            panels and drop-down stairs equipped with a durable &ge;
            R-10 insulated cover that is gasketed (i.e., not caulked) to produce
            continuous air seal when occupant is not accessing the attic</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">If installing
              ceiling access to the attic, building science experts recommend installing
              additional blocking to create insulation dams. </li>
              <li style="margin-left:0pt">Install
              an attic access panel that is equipped with an insulated cover to meet
              or exceed R-10. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. </li>
              <li style="margin-left:0pt">Install
              a continuous gasket around the attic access panel. </li>
            </ol>

            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>24. Examples of durable covers include, but
            are not limited to, prefabricated covers with integral insulation, rigid
            foam adhered to cover with adhesive, or batt insulation mechanically
            fastened to the cover (e.g., using bolts, metal wire, or metal strapping). </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "te-r-533-whole-house-fans-equipped-with-a-durabl": """<p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">DETAIL 5.3.3<sup> 24</sup></span>

            </p>
            <p style="text-align:center"><span style="font-weight:bold">Whole-house fans
            equipped with a durable &ge; R-10 insulated cover
            that is gasketed and either installed on the house side or mechanically
            operated</span></p>
            <ol style="list-style:upper-alpha">
              <li style="margin-left:0pt">Install
              a whole-house fan that is equipped with an insulated cover to meet or
              exceed R-10. </li>
              <li style="margin-left:0pt">Install
              an insulated and gasketed cover on the house side or install one that
              is mechanically operated. </li>
              <li style="margin-left:0pt">Seal
              all gaps, and holes to unconditioned space with caulk or foam. </li>
              <li style="margin-left:0pt">Whole-house
              fans are most effective in climates with hot days, cool nights and relatively
              low humidity. </li>
            </ol>

            <p> </p>
            <p style="text-align:center"><span style="font-weight:bold;
            text-decoration:underline">FOOTNOTES</span></p>
            <p>24. Examples of durable covers include, but
            are not limited to, prefabricated covers with integral insulation, rigid
            foam adhered to cover with adhesive, or batt insulation mechanically
            fastened to the cover (e.g., using bolts, metal wire, or metal strapping). </p>
            <p> </p>
            <p style="text-align:center"></p>""",
            "cc-r-11-has-a-completed-energy-star-version-3-hv": """By answering "Yes", you are acknowledging that you have in your possession a copy of this checklist for this home and are willing to provide a copy of the checklist to APS if requested to validate your certification of this home.""",
            "cc-r-12-has-an-energy-star-version-3-hvac-system": """By answering "Yes", you are acknowledging that you have in your posession a copy of this checklist for this home (or, if sampling, for each tested home in the sample set) and are willing to provide a copy of the checklist to APS if requested to validate your certification of this home.""",
            "cc-r-13-has-a-completed-energy-star-version-3-wa": """By answering "Yes", you are acknowledging that you have in your possession a copy of this checklist for this home and are willing to provide a copy of the checklist to APS if requested to validate your certification of this home.""",
            "te-r-5-fd1-measured-blower-door-value": """Enter data as a single value""",
            "hvac-r-28-fd1-measured-dominant-duct-leakage-pre": """Enter data as single value""",
            "hvac-r-28-fd2-measured-pressure-in-each-bedroom": """Enter data as a comma-separated list of room/value pairs (e.g. Master:20.2, BR1:18.6, BR2:15.3, BR3:17.8)""",
            "hvac-r-41-fd1-total-measured-duct-leakage-value": """Enter data as a comma-separated list of unit/value pairs in the format "unit_# total_leakage" (e.g. 1 20.2, 2 18.6, 3 15.3)""",
            "hvac-r-42-fd1-measured-duct-leakage-values-to": """Enter data as a comma-separated list of unit/value pairs in the format "unit_# leakage_to_outside" (e.g. 1 30.5, 2 22.1, 3 16.7)""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Rater Verified",
                "Builder Verified",
                "Must Correct",
                "Not Applicable",
            ): [
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
            ],
            (
                "Yes",
                "No",
            ): [
                "cc-r-11-has-a-completed-energy-star-version-3-hv",
                "cc-r-12-has-an-energy-star-version-3-hvac-system",
                "cc-r-13-has-a-completed-energy-star-version-3-wa",
            ],
        },
    }
    instrument_types = {
        "float": [
            "te-r-5-fd1-measured-blower-door-value",
            "hvac-r-28-fd1-measured-dominant-duct-leakage-pre",
        ],
    }
    suggested_response_flags = {
        "rater": {
            "te-r-11-prescriptive-path-fenestration-shall-mee": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-12-performance-path-fenestration-shall-meet": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-211-ceiling-wall-floor-and-slab-insulat": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-212-achieve-133-of-the-total-ua-result": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-22-all-ceiling-wall-floor-and-slab-insul": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-311-walls-behind-showers-and-tubs": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-312-walls-behind-fireplaces": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-313-attic-knee-walls": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-314-skylight-shaft-walls": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-315-wall-adjoining-porch-roof": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-316-staircase-walls": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-317-double-walls": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-318-garage-rim-band-joist-adjoining-con": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-319-all-other-exterior-walls": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-321-floor-above-garage": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-322-cantilevered-floor": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-323-floor-above-unconditioned-basement-or": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-331-dropped-ceiling-soffit-below-uncond": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-332-all-other-ceilings": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-41-for-insulated-ceilings-with-attic-space": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-42-for-slabs-on-grade-in-cz-4-and-higher-1": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-43-insulation-beneath-attic-platforms-eg": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-441-reduced-thermal-bridging-at-above-grade": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-442-structural-insulated-panels-sips-or": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-443-insulated-concrete-forms-icfs-or-s": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-444-double-wall-framing-or-see-next-ques": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-445a-all-corners-insulated-r-6-to-edge": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-445b-all-headers-above-windows-doors-insu": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-445c-framing-limited-at-all-windows-doors": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-445d-all-interior-exterior-wall-intersect": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-445e-minimum-stud-spacing-of-16-in-oc-fo": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-511-duct-flue-shaft": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-512-plumbing-piping": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-513-electrical-wiring": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-514-bathroom-and-kitchen-exhaust-fans": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-515-recessed-lighting-fixtures-adjacent-to": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-516-light-tubes-adjacent-to-unconditioned-s": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-521-all-sill-plates-adjacent-to-conditioned": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-522-at-top-of-walls-adjoining-unconditione": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-523-drywall-sealed-to-top-plate-at-all-unc": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-524-rough-opening-around-windows-exterior": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-525-marriage-joints-between-modular-home-mo": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-526-all-seams-between-structural-insulated": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-527-in-multi-family-buildings-the-gap-bet": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-531-doors-adjacent-to-unconditioned-space": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-532-attic-access-panels-and-drop-down-stair": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "te-r-533-whole-house-fans-equipped-with-a-durabl": {
                "Must Correct": {
                    "comment_required": True,
                },
            },
            "cc-r-11-has-a-completed-energy-star-version-3-hv": {
                "No": {
                    "comment_required": True,
                },
            },
            "cc-r-12-has-an-energy-star-version-3-hvac-system": {
                "No": {
                    "comment_required": True,
                },
            },
            "cc-r-13-has-a-completed-energy-star-version-3-wa": {
                "No": {
                    "comment_required": True,
                },
            },
        },
    }
