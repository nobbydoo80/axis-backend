"""strings.py: Django remrate_data"""


__author__ = "Steven Klass"
__date__ = "11/13/15 2:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

AUX_ELEC_UNITS = ((1, "Eae"), (2, "kWh/yr"), (3, "Watts"))
BASELINE_SAVINGS = (
    (1, "1993 MEC"),
    (2, "1995 MEC"),
    (3, "1998 IECC"),
    (4, "2000 IECC"),
    (9, "2001 IECC"),
    (10, "2003 IECC"),
    (12, "2004 IECC"),
    (14, "2006 IECC"),
    (15, "2009 IECC"),
    (16, "2012 IECC"),
    (17, "2015 IECC"),
    (18, "2018 IECC"),
    (11, "ECC of New York"),
    (5, "ASHRAE Standard 90.2"),
    (6, "HERS Reference Home"),
    (7, "User Defined Reference Home"),
    (8, "Another REM/Rate Building"),
)
BUILDING_INPUT_TYPES = ((0, "Undetermined"), (1, "Simplified Building"), (2, "Detailed Building"))
COLLECTOR_SPECS = (
    (0, "None"),
    (1, "Single glazing, flat black"),
    (2, "Single glazing, selective"),
    (3, "Double glazing, flat black"),
    (4, "Double glazing, selective"),
    (5, "Evacuated Tube"),
)
COLORS = (
    (0, "None"),  # Prior - Reflective
    (1, "Light"),
    (2, "Medium"),
    (3, "Dark"),
    (4, "Reflective"),
    (5, "Std140"),
    (6, "Std140-lowAbs"),
    (7, "White Comp. Shingles"),
    (8, "White Tile/Concrete"),
    (9, "White Metal/TPO"),
)
COOLING_EFF_UNITS = (
    (1, "SEER"),
    (2, "EER"),
    (3, "% EFF"),
    (4, "COP"),
)
COOLING_TYPES = (
    (1, "Air conditioner"),
    (2, "Air-source heat pump"),
    (3, "Ground-source heat pump"),
    (4, "Evaporative cooler"),
    (5, "None"),
)
CRAWL_SPACE_TYPES = (
    (0, "N/A"),
    (1, "Unvented"),
    (2, "Vented"),
    (3, "Operable vents"),
)
DOE_CHALLENGE_OPTIONAL = (
    (1, "Yes"),
    (2, "No"),
    (3, "Don't Know"),
)
DOOR_TYPES = (
    (1, "Storm Door"),
    (2, "No Storm Door"),
)
DUCT_LEAKAGE = (
    (1, "Leaky, uninsulated"),
    (2, "RESNET/HERS default"),
    (3, "Proposed reduced leakage"),
)
DUCT_SYSTEM_INPUT_LEAKAGE_TYPES = (
    (0, "Measured"),
    (1, "Threshold"),
    (2, "Qualitative Default")
    # (2, 'Old Defaults (View-Only)'),
)
DUCT_SYSTEM_LEAKAGE_TO_OUTSIDE_TYPES = ((2, "Total Leakage"), (3, "Supply and Return Leakage"))
DUCT_SYSTEM_LEAKAGE_TEST_TYPES = (
    (1, "Both Tested"),
    (2, "Leakage to Outside"),
    (3, "Total Duct Leakage"),
)
DUCT_LOCATIONS = (
    (1, "Open crawl/raised floor"),
    (2, "Enclosed crawl space"),
    (3, "Conditioned crawl space"),
    (4, "Unconditioned basement"),
    (5, "Conditioned basement"),
    (16, "Sealed Attic"),
    (6, "Attic, under insulation"),
    (7, "Attic, exposed"),
    (8, "Conditioned space"),
    (10, "Garage"),
    (14, "Floor cavity over garage"),
    (13, "Exterior wall"),
    (9, "Wall with no top plate Garage"),
    (15, "Under slab floor"),
    (12, "Mobile home belly"),
    (0, "None"),
)
DUCT_TYPES = ((1, "Supply"), (2, "Return"))
ECON_CALCULATION_METHODOLOGY = [(0, "RESNET"), (1, "DOE"), (2, "Oregon")]
ENERGYSTAR_REQ_CHOICES = (
    (0, "Verificaton Needed"),
    (1, "Rater"),
    (2, "Builder"),
    (3, "NA"),
    (4, "Needs Corrections"),
)
EXPORT_TYPES = (
    (1, "Standard Building"),
    (2, "IA Base Building"),  # NO LONGER USED 16.0
    (3, "IA Improved Building"),  # NO LONGER USED 16.0
    (4, "UDRH As Is Building"),
    (5, "UDRH Reference Building"),
    (6, "ASHRAE Code Reference Building"),  # NO LONGER USED 16.0
    (7, "ASHRAE Code Design Building"),  # NO LONGER USED 16.0
    (8, "HERS Code Reference Building"),
    (9, "HERS Code Design Building"),
    (10, "1998 IECC Code Reference Building"),
    (11, "1998 IECC Code Design Building"),
    (12, "2000 IECC Code Reference Building"),
    (13, "2000 IECC Code Design Building"),
    (14, "2001 IECC Code Reference Building"),
    (15, "2001 IECC Code Design Building"),
    (16, "2003 IECC Code Reference Building"),
    (17, "2003 IECC Code Design Building"),
    (18, "2004 IECC Code Reference Building"),
    (19, "2004 IECC Code Design Building"),
    (20, "ECC of NY Code Reference Building"),
    (21, "ECC of NY Code Design Building"),
    (22, "ECC of NV Code Reference Building"),  # NO LONGER USED 16.0
    (23, "ECC of NV Code Design Building"),  # NO LONGER USED 16.0
    (24, "1992 MEC Code Reference Building"),
    (25, "1992 MEC Code Design Building"),
    (26, "1993 MEC Code Reference Building"),
    (27, "1993 MEC Code Design Building"),
    (28, "1995 MEC Code Reference Building"),
    (29, "1995 MEC Code Design Building"),
    (30, "2006 IECC Code Reference Building"),
    (31, "2006 IECC Code Design Building"),
    (32, "2009 IECC Code Reference Building"),
    (33, "2009 IECC Code Design Building"),
    (34, "ENERGY STAR V2 Code Reference Building"),  # NO LONGER USED 16.0
    (35, "ENERGY STAR V2 Code Design Building"),  # NO LONGER USED 16.0
    (36, "ENERGY STAR V2.5 Code Reference Building"),  # NO LONGER USED 16.0
    (37, "ENERGY STAR V2.5 Code Design Building"),  # NO LONGER USED 16.0
    (38, "FE PA New Homes Qualification Reference Building"),
    (39, "FE PA New Homes Qualification Design Building"),
    (40, "FE PA Savings Reference Building"),
    (41, "FE PA Savings Design Building"),
    (42, "2012 IECC Code Reference Building"),
    (43, "2012 IECC Code Design Building"),
    (44, "ENERGY STAR V3 Code Reference Building"),
    (45, "ENERGY STAR V3 Code Design Building"),
    (46, "FE OH New Homes 2006 IECC Code Reference Building"),  # NO LONGER USED 16.0
    (47, "FE OH New Homes 2006 IECC Code Design Building"),  # NO LONGER USED 16.0
    (48, "FE OH Savings Reference Building"),  # NO LONGER USED 16.0
    (49, "FE OH Savings Design Building"),  # NO LONGER USED 16.0
    (50, "Canada Package A1 Reference Building"),  # NO LONGER USED 16.0
    (51, "Canada Package A1 Design Building"),  # NO LONGER USED 16.0
    (52, "DOE Zero Energy Challenge Reference Building"),
    (53, "DOE Zero Energy Challenge Design Building"),
    (56, "Texas NTCCOG 15 Code Reference Building"),
    (57, "Texas NTCCOG 15 Code Design Building"),
    (58, "LEED for Homes v4 Reference Building"),
    (59, "LEED for Homes v4 Design Building"),
    (60, "2012 Iowa Energy Code Reference Building"),
    (61, "2012 Iowa Energy Code Design Building"),
    (62, "ENERGY STAR V3 Pacific Reference Building"),
    (63, "ENERGY STAR V3 Pacific Design Building"),
    (64, "ENERGY STAR V3.1 Reference Building"),
    (65, "ENERGY STAR V3.1 Design Building"),
    (66, "2015 IECC Code Reference Building"),
    (67, "2015 IECC Code Design Building"),
    (68, "Illinois Energy Code Reference Building"),
    (69, "Illinois Energy Code Design Building"),
    (70, "Michigan Energy Code Reference Building"),
    (71, "Michigan Energy Code Design Building"),
    (72, "PPL New Homes Qualification Reference Building"),
    (73, "PPL New Homes Qualification Design Building"),
    (74, "PPL Savings Reference Building"),
    (75, "PPL Savings Design Building"),
    (76, "PECO New Home Qualification Reference Building"),
    (77, "PECO New Home Qualification Design Building"),
    (78, "PECO Savings Reference Building"),
    (79, "PECO Savings Design Building"),
    (80, "MN Xcel Reference Building"),
    (81, "MN Xcel Design Building"),
    (82, "Tax Credit Reference Building"),
    (83, "Tax Credit Design Building"),
    (84, "ENERGY STAR V3.2 WA, OR Reference Building"),
    (85, "ENERGY STAR V3.2 WA, OR Design Building"),
    (86, "IECC 2018 Reference Building"),
    (87, "IECC 2018 Design Building"),
    (88, "UGI New Homes Rating Reference Building"),
    (89, "UGI New Homes Rating Design Building"),
    (90, "UGI Savings Reference Building"),
    (91, "UGI Savings Design Building"),
    (92, "CT Eversource Reference Building"),
    (93, "CT Eversource Design Building"),
    (94, "ENERGY STAR V1.0 MF Reference Building"),
    (95, "ENERGY STAR V1.0 MF Design Building"),
    (96, "ENERGY STAR V1.1 MF Reference Building"),
    (97, "ENERGY STAR V1.1 MF Design Building"),
    (98, "ENERGY STAR V1.2 MF WA, OR Reference Building"),
    (99, "ENERGY STAR V1.2 MF WA, OR Design Building"),
    (100, "Texas NTCCOG 18 Code Reference Building"),
    (101, "Texas NTCCOG 18 Code Design Building"),
    (102, "2015 Pennsylvania Code Reference Building"),
    (103, "2015 Pennsylvania Code Design Building"),
    (104, "2018 Illinois Code Reference Building"),
    (105, "2018 Illinois Code Design Building"),
    (106, "Wisconsin UDC FE 2018 Reference Building"),  # NO LONGER USED 16.0
    (107, "Wisconsin UDC FE 2018 Design Building"),  # NO LONGER USED 16.0
    (108, "Wisconsin UDC FE Reference Building"),  # NO LONGER USED 16.0
    (109, "Wisconsin UDC FE Design Building"),  # NO LONGER USED 16.0
)

FAN_CONTROL_TYPES = ((1, "Single Speed"), (2, "Two Speed"), (3, "Variable Speed"))
FLOOR_COVERINGS = (
    (0, "None"),
    (1, "Carpet"),
    (2, "Tile"),
    (3, "Hardwood"),
    (4, "Vinyl"),
    (5, "Rigid R-3 Insul"),
    (6, "CodeRef Carpet"),
)
FLOOR_LOCATIONS = (
    (0, "None"),
    (201, "Between conditioned space and ambient conditions"),
    (202, "Between conditioned space and garage"),
    (203, "Between conditioned space and open crawl space"),
    (205, "Between conditioned space and unconditioned basement"),
    (206, "Between conditioned space and enclosed crawl space"),
    (213, "Between conditioned space and another (adiabatic)"),
)
FOUNDATION_WALL_LOCATIONS = (
    (0, "None"),
    (201, "Between conditioned space and ambient/ground"),
    (202, "Between conditioned space and garage/ground"),
    (203, "Between conditioned space and open crawl space/ground"),
    (205, "Between conditioned space and unconditioned basement/ground"),
    (206, "Between conditioned space and enclosed crawl space/ground"),
    (213, "Between cond and another cond unit (adiabatic)"),
    # New as of Remrate 16.1
    (229, "Bsmt (conditioned)---ambient/ground"),
    (230, "Bsmt (conditioned)---ambient/ground"),
    (231, "Bsmt (conditioned)---garage/ground"),
    (232, "Bsmt (conditioned)---crawl (conditioned)/ground"),
    (233, "Bsmt (conditioned)---unconditioned bsmt/ground"),
    (234, "Bsmt (conditioned)---enclosed crawl/ground"),
    (235, "Bsmt (conditioned)---open crawl/ground"),
    (236, "Bsmt (conditioned)---MF unrated cond space (adiabatic)/ground"),
    (237, "Bsmt (conditioned)---MF unrated heated/ground"),
    (238, "Bsmt (conditioned)---MF buffer/ground"),
    (239, "Bsmt (conditioned)---MF nonfreezing/ground"),
    (214, "Crawl (conditioned)---ambient/ground"),
    (215, "Crawl (conditioned)---garage/ground"),
    (216, "Crawl (conditioned)---open crawl/ground"),
    (239, "Crawl (conditioned)---unconditioned bsmt/ground"),
    (240, "Crawl (conditioned)---enclosed crawl/ground"),
    (241, "Crawl (conditioned)---MF unrated cond space (adiabatic)/ground"),
    (242, "Crawl (conditioned)---MF unrated heated/ground"),
    (243, "Crawl (conditioned)---MF buffer/ground"),
    (244, "Crawl (conditioned)---MF nonfreezing/ground"),
    (207, "Unconditioned bsmt---ambient/ground"),
    (208, "Unconditioned bsmt---garage/ground"),
    (209, "Unconditioned bsmt---open crawl/ground"),
    (245, "Unconditioned bsmt---MF unrated cond space/ground"),
    (246, "Unconditioned bsmt---MF unrated heated/ground"),
    (247, "Unconditioned bsmt---MF buffer/ground"),
    (248, "Unconditioned bsmt---MF nonfreezing/ground"),
    (210, "Enclosed crawl---ambient/ground"),
    (211, "Enclosed crawl---garage/ground"),
    (212, "Enclosed crawl---open crawl/ground"),
    (249, "Enclosed crawl---MF unrated cond space/ground"),
    (250, "Enclosed crawl---MF unrated heated/ground"),
    (251, "Enclosed crawl---MF buffer/ground"),
    (252, "Enclosed crawl---MF nonfreezing/ground"),
)
FOUNDATION_TYPE = (
    (1, "from top of wall"),
    (2, "from bottom of wall"),
    (3, "above grade"),
    (4, "below grade"),
)
FOUNDATION_TYPES = (
    (1, "Slab"),
    (2, "Open crawl space"),
    (3, "Enclosed crawl space"),
    (4, "Conditioned basement"),
    (5, "Unconditioned basement"),
    (6, "More than one type"),
    (7, "Apartment above conditioned space"),
    (8, "Conditioned crawl space"),
)
FOUNDATION_WALL_STUD_TYPES = (
    (0, "None"),
    (1, 'Wood, 2x4, 12" o.c.'),
    (2, 'Wood, 2x4, 16" o.c.'),
    (7, 'Wood, 2x4, 24" o.c.'),
    (3, 'Wood, 2x6, 16" o.c.'),
    (4, 'Wood, 2x6, 24" o.c.'),
    (5, 'Steel, 2x4, 16" o.c.'),
    (6, 'Steel, 2x6, 24" o.c.'),
)
FOUNDATION_WALL_TYPES = (
    (11, "Solid concrete or stone"),
    (12, "Block: uninsulated cores"),
    (13, "Block: foam cores"),
    (14, "Block: vermiculite cores"),
    (15, "All weather wood"),
    (16, "Double brick"),
    (17, "MH wood skirting"),
    (18, "MH Vinyl Skirting"),
    (19, "MH aluminum skirting"),
)
FUEL_TYPES = (
    (1, "Natural gas"),
    (2, "Propane"),
    (3, "Fuel oil"),
    (4, "Electric"),
    (5, "Kerosene"),
    (6, "Wood"),
    (98, "Water"),
)
GSHP_DISTRIBUTION_TYPES = ((0, "Hydronic"), (1, "Air Distribution"))
GSHP_PUMP_TYPES = ((1, "ARI 330/Closed Loop"), (2, "ARI 325/Open Loop"))
GS_PUMP_TYPES = ((1, "ARI 330/Closed Loop"), (2, "ARI 325/Open Loop"))
H2O_HEATER_TYPES = (
    (0, "None"),
    (1, "Conventional"),
    (3, "Instant water heater"),
    (4, "Heat pump"),
    (5, "Ground source heat pump"),
    (21, "Integrated"),
)
HEATER_TYPES = (
    (1, "Fuel-fired air distribution"),
    (2, "Fuel-fired hydronic distribution"),
    (3, "Fuel-fired unit heater"),
    (9, "Fuel-fired unvented unit heater"),
    (4, "Electric baseboard or radiant"),
    (5, "Electric air distribution"),
    (8, "Electric hydronic distribution"),
    (6, "Air-source heat pump"),
    (7, "Ground-source heat pump"),
    (0, "None"),
)
HEATING_EFF_UNITS = (
    (1, "AFUE"),
    (2, "% EFF"),
    (3, "HSPF"),
    (4, "COP"),
)
HOME_LEVEL_TYPES = ((0, "None"), (1, "Top floor"), (2, "Mid Level"), (3, "Lowest Level"))
HOME_STORY_TYPES = ((1, "Single"), (2, "Multi"))
HOME_TYPES = (
    (1, "Single-family detached"),
    (2, "Townhouse, end unit"),
    (3, "Townhouse, inside unit"),
    (4, "Apartment, end unit"),
    (5, "Apartment, inside unit"),
    (6, "Multi-family, whole building"),
    (7, "Duplex, single unit"),
    (8, "Mobile home"),
    (9, "Duplex, whole building"),
)
HOT_WATER_RECIRCULATION_TYPES = (
    (1, "None (standard system)"),
    (2, "Timer or Uncontroled"),
    (3, "Temperature control"),
    (4, "Demand (presence sensor)"),
    (5, "Demand (manual"),
)
IMPROVEMENT_CRITERIA = (
    (1, "Rank by SIR"),
    (2, "Rank by Net Present Value"),
    (3, "Rank by Simple Payback"),
    (4, "Rank by Rating"),
    (5, "Rank by Saving"),
)
INFILTRATION_COOLING_TYPES = (
    (1, "Whole House Fan"),
    (2, "No Ventilation"),
    (3, "Natural Ventilation"),
)
INFILTRATION_EST_TYPES = (
    (1, "User estimate"),
    (3, "Tracer gas test"),
    (4, "Blower door test"),
    (5, "Code default"),
    (6, "Threshold"),
)
INFILTRATION_TYPES = (
    (0, "None"),
    (1, "Balanced"),
    (2, "Exhaust Only"),
    (3, "Supply Only"),
    (4, "Air Cycler"),
)
INFILTRATION_UNITS = (
    (1, "CFM @ 50 Pascals"),
    (2, "CFM @ 25 Pascals"),
    (3, "ACH @ 50 Pascals"),
    (4, "Natural ACH"),
    (5, "Eff. Leakage Area (in²)"),
    (6, "ELA/100 sf shell"),
    (7, "Thermal Efficiency (%)"),
    (9, "Specific Leakage Area"),
    (10, "CFM per Std 152"),
    (11, "CFM25 / CFA"),
    (12, "CFM25 / CFMfan"),
)
INFILTRATION_VERIFICATIONS = ((1, "Visually Inspected"), (2, "Tested"))
INSTALLED_LAP_TYPES = (
    (1, "Light Fixture(s)"),
    (2, "Plug Load(s)"),
    (3, "Refrigerator"),
    (4, "Freezer"),
    (5, "Dishwasher"),
    (6, "Microwave"),
    (7, "Oven/Range"),
    (8, "Clothes Washer"),
    (9, "Clothes Dryer"),
    (10, "Shower/Bath"),
    (11, "Miscellaneous"),
    (12, "Fluorescent Fixture(s)"),
    (13, "Non-Fluorescent Fixture(s)"),
    (14, "Ceiling Fan(s)"),
    (15, "Exterior Light Fixture(s)"),
    (16, "Garage Light Fixture(s)"),
)

INSTALLED_LAP_UNITS = (
    (1, "kBtuh"),
    (2, "Watts"),
    (3, "KW"),
    (4, "kWh/use"),
    (5, "Gallons/use"),
    (6, "kBtu/use"),
    (7, "MMBtu/use"),
)

INSTALLED_LAP_USE_UNITS = (
    (1, "Hours/Day"),
    (2, "Hours/Week"),
    (3, "Hours/Month"),
    (4, "Hours/Year"),
    (5, "Uses/Day"),
    (6, "Uses/Week"),
    (7, "Uses/Month "),
    (8, "Uses/Year"),
)
INSTALLED_LAP_FUEL = (
    (1, "Natural Gas"),
    (2, "Propane"),
    (3, "Fuel oil"),
    (4, "Electricity"),
    (5, "Kerosene"),
    (6, "Wood"),
    (98, "Water"),
)
INSTALL_LAP_EFFICIENCY = (
    (1, "ENERGY STAR"),
    (2, "High Efficiency"),
    (3, "Standard"),
    (4, "Inefficient"),
)
INSULATION_GRADES = ((1, "I"), (2, "II"), (3, "III"))
INS_TYPES = ((1, "Batt"), (2, "Blown"))
INSULATION_LOCATIONS = (
    (1, "Batt in cavities"),
    (2, "Blanket, compressed"),
    (3, "Blanket uncompressed"),
    (4, "Batt with compressed blanket"),
    (5, "Batt with uncompressed blanket"),
)
ISWH_TYPES = (
    (1, "Combined Appliance"),
    (2, "Boiler w/tankless coil"),
    (3, "Hot Water System for space heating"),
)
ISWH_DIST_TYPES = ((1, "Hydronic only"), (2, "Hydronic w/air"))
JOIST_ABOVE_GRADE_WALL_LOCATIONS = (
    (0, "None"),
    (201, "Between conditioned space and ambient"),
    (202, "Between conditioned space and garage"),
    (203, "Between conditioned space and open crawl"),
    (204, "Between conditioned space and attic"),
    (205, "Between conditioned space and uncond bsmnt"),
    (206, "Between conditioned space and enclosed crawl"),
    (214, "Between conditioned crawl and ambient"),
    (215, "Between conditioned crawl and garage"),
    (216, "Between conditioned crawl and open crawl"),
    (207, "Between unconditioned bsmnt and ambient"),
    (208, "Between unconditioned bsmnt and garage"),
    (209, "Between unconditioned bsmnt and open crawl"),
    (210, "Between enclosed crawl and ambient"),
    (211, "Between enclosed crawl and garage"),
    (212, "Between enclosed crawl and open crawl"),
    (213, "Between cond and another cond unit (adiabatic)"),
    (217, "Between sealed attic and ambient"),
)
LEAKAGE_ESTIMATE_TYPES = (
    (1, "Leaky, uninsulated"),
    (2, "RESNET/HERS default"),
    (3, "Proposed Reduced Leakage"),
)
LEAKAGE_TIGHTNESS_TESTS = (
    (1, "Postconstruction Test"),
    (2, "Rough-In Test - w/ Air Handler"),
    (3, "Rough-In Test - w/o Air Handler"),
    (4, "Duct Leakage Exemption"),
)
LEAKAGE_TYPES = ((1, "Qualitative Default"), (2, "Total Leakage"), (3, "Supply and Return Leakage"))
LEAKAGE_UNITS = (
    (1, "CFM@50 Pascals"),
    (2, "CFM@25 Pascals"),
    (5, "Eff. Leakage Area"),
    (7, "Thermal Efficiency (%)"),
    (10, "CFM per Std 152"),
    (11, "CFM25 / CFA"),
    (12, "CFM25 / CFMfan"),
)
LIGHT_APP_LOCATIONS = (
    (0, "None (ERI Default)"),
    (1, "Conditioned"),
    (2, "Unconditioned"),
    (3, "MF Shared Space"),
)
LIGHT_APP_WASHER_EFFICIENCY_PRESETS = (
    (1, "RESNET Default"),
    (2, "Med Efficiency"),
    (3, "High Efficiency"),
    (4, "ENERGY STAR"),
    (5, "ENERGY STAR 2018"),
)
LIGHT_APP_WASHER_PRESETS = (
    (1, "ERI Ref 2006"),
    (2, "Standard 2008-2017"),
    (3, "ENERGY STAR, Std Capacity"),
    (4, "ENERGY STAR, Compact"),
    (5, "Specific EnergyGuide label"),
)
LIGHT_APP_WASHER_PRESETS_LEGACY = (
    (1, "RESNET Default"),
    (2, "Med Efficiency"),
    (3, "High Efficiency"),
    (4, "ENERGY STAR"),
    (5, "ENERGY STAR 2018"),
)
LIGHT_APP_DISHWASHER_PRESETS = (
    (1, "ERI Reference"),
    (2, "Federal Minimum"),
    (3, "ENERGY STAR, Std Capacity"),
    (4, "ENERGY STAR, Compact"),
    (5, "Specific EnergyGuide label"),
)

LOOP_TYPES = (
    (0, "None"),
    (1, "Air, direct"),
    (2, "Air, indirect"),
    (3, "Liquid, direct"),
    (4, "Liquid, indirect"),
    (5, "Batch heater"),
)
SEEKING_CERTS_FOR = (
    (22, "ENERGY STAR V 3.0"),
    (2, "ENERGY STAR V 3.0 Tropics w/Nat'l Checklist"),
    (51, "ENERGY STAR V 3.0 Tropics w/Tropics Checklist"),
    (50, "ENERGY STAR V 3.1"),
    (61, "ENERGY STAR V 3.2 WA, OR"),
    (66, "ENERGY STAR v1.1 Multi-Family"),
    (67, "ENERGY STAR v1.0 Multi-Family"),
    (68, "ENERGY STAR v1.2 MF WA, OR"),
    (0, "None"),
)
MASS_LOCATIONS = (
    (1, "Sunlit floor"),
    (2, "Shaded floor"),
    (3, "Wall in sunlit room"),
    (4, "Wall in remote room"),
)
MASS_TYPES = ((0, "None"), (1, "Concrete"), (2, "Brick/Tile"), (3, "Water"))
MECHANICAL_EQUIP_LOCATIONS = (
    (1, "Conditioned area"),
    (6, "Conditioned Crawlspace"),
    (2, "Uncond bsmnt/enclosed crawl"),
    (3, "Garage or open crawl space"),
    (4, "Vented Attic"),
    (7, "Sealed Attic"),
    (5, "Ambient"),
    (8, "Garage"),
    (9, "MF unrated conditioned"),
    (10, "MF unrated heated"),
    (11, "MF buffer space"),
    (12, "MF nonfreezing space"),
    (0, "None"),
)
MONTHS = (
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
)
ORIENTATION_CHOICES = (
    (5, "North"),
    (4, "Northeast"),
    (3, "East"),
    (2, "Southeast"),
    (1, "South"),
    (7, "Southwest"),
    (8, "West"),
    (9, "Northwest"),
    (0, "None"),
)
PUMP_ENERGY_UNITS = ((0, "kWh/yr"), (1, "Watts"))
PV_ORIENTATION = (
    (0, "None"),
    (1, "South"),
    (2, "Southeast/Southwest"),
    (3, "East/West"),
    (4, "Northeast/Northwest"),
    (5, "North"),
)
PV_TYPES = (
    (1, "Monocrystalline Silicon"),
    (2, "Polycrystalline Silicon"),
    (3, "Amorphous Silicon"),
    (4, "Copper Indium Diselenide"),
    (6, "Cadmium Telluride"),
    (0, "None"),
)
QUALITATIVE_TYPE = ((1, "Qualitative"), (2, "Quantitative"))
QUICKFILL_TYPES = ((0, "Site Built"), (2, "Mobile Home"))
REJECTION_REASONS = (
    (1, "Failed Criteria"),
    (2, "Exceeded available funds"),
    (3, "Redundant w/ accepted measure"),
    (4, "Caused a building error"),
)
RESNET_CHOICES = ((1, "Employer"), (2, "Rater"), (3, "N/A"))
ROOF_STYLE = ((1, "Vaulted"), (2, "Attic"))
SEEP_HEAT_UNITS = ((1, "AFUE"), (2, "% EFF"), (3, "HSPF"), (4, "COP"))
SEEP_UNITS = ((1, "SEER"), (2, "EER"), (3, "% EFF"), (4, "COP"))
SHADING_FACTOR = ((1.0, "None"), (0.70, "Some"), (0.40, "Most"), (0.10, "Complete"))
SIMPLIFIED_INPUT_HOUSE_TYPES = (
    (1, "1 Story"),
    (2, "1-1/2 Story"),
    (3, "2 Story"),
    (4, "2-1/2 Story"),
    (5, "3 Story"),
    (6, "Bi-Level"),
    (7, "Tri-Level"),
)
SIMPLIFIED_INPUT_FOUNDATION_TYPES = (
    (0, "Slab"),
    (1, "Open Crawl Space"),
    (2, "Enclosed Crawl Space"),
    (3, "Conditioned Crawl Space"),
    (4, "Un-Conditioned Full Basement"),
    (5, "Conditioned Full Basement"),
    (6, "Unconditioned Walkout Basement"),
    (7, "Conditioned Walkout Basement"),
    (8, "Mixed"),
)
SOLAR_ORIENTATION = ((0, "None"), (1, "South"), (2, "SE/SW"), (3, "East/West"))
SOLAR_TYPES = (
    (1, "DHW heating only"),
    (2, "DHW & Space heating"),
    (3, "Space heating only"),
    (4, "Hybrid"),
    (0, "None"),
)
STYLE = ((1, "Vaulted"), (2, "Attic"), (3, "Sealed Attic"), (4, "Adiabatic"))
SYSTEM_TYPES = (
    (1, "Space Heating"),
    (2, "Space Cooling"),
    (3, "Water Heating"),
    (4, "Air-Source Heat Pump"),
    (5, "Ground Source Heat Pump"),
    (6, "Dual Fuel Heat Pump"),
    (7, "Integrated Space/Water Heating"),
    (8, "Shared Equipment"),
    (9, "Dehumidifier Equipment"),
)
THERMAL_BOUNDARY_TYPES = (
    (0, "N/A"),
    (1, "Floor"),
    (2, "Foundation Wall"),
    (3, "REM Default"),
)
TRUE_FALSE = ((1, True), (2, False))
UTILITY_UNITS = (
    (0, "MMBtu"),
    (1, "kWh"),
    (2, "Gallons"),
    (3, "CCF"),
    (4, "Therms"),
    (5, "Cords"),
    (6, "MCF"),
    (7, "kW_Htg"),
    (8, "kW_Clg"),
)
UTILITY_BILL_DHW_SETPOINTS = (
    (0, "100"),
    (1, "115"),
    (2, "120"),
    (3, "125"),
    (4, "130"),
    (5, "135"),
    (6, "140"),
)
UTILITY_BILL_COOKING_FREQUENCY = (
    (0, "0 - 25%"),
    (1, "26 - 50%"),
    (2, "51 - 75%"),
    (3, "76 - 100%"),
)
UTILITY_BILL_HOT_WATER_EF = ((0, "Regular"), (1, "High"))
VENT_TYPES = ((1, "Whole House Fan"), (2, "No Ventilation"), (3, "Natural Ventilation"))
WALL_TYPES = (
    (1, "Standard Wood Frame"),
    (2, "Double Stud Wood Frame"),
    (7, "Standard Steel Frame"),
    (3, "Std Frame w/Brick Veneer"),
    (4, "Solid Concrete or Stone"),
    (5, "Double Brick"),
    (6, "Hollow-Core Concrete Block"),
    (8, "Structual Insulated Panel"),
    (9, "Insulated Concrete Form"),
    (10, "Adobe"),
)
WELL_TYPES = ((0, "Vertical"), (1, "Horizontal"))

HUMIDIFIER_TYPES = ((1, "Portable"), (2, "Whole-home"))

SHARED_EQUIPMENT_TYPES = (
    (1, "Boiler"),
    (2, "Chiller"),
    (3, "Cooling Tower"),
    (4, "GSHP Loop"),
)

SHARED_EFFICIENCY_UNITS = ((1, "AFUE"), (2, "kW/ton"))

SHARED_DISTRIBUTION_TYPES = (
    (1, "Hydronic → Radiator"),
    (2, "Hydronic → Baseboard"),
    (3, "Hydronic → Radiant floor"),
    (4, "Hydronic → Radiant ceiling"),
    (5, "Air → Fan Coil"),
    (6, "Air → WLHP"),
    (7, "Air → GSHP"),
    (8, "Air → GSHP (Htg and Clg)"),
)

SLAB_LOCATIONS = (
    (0, "None"),
    (1, "Mainfloor conditioned space"),
    (2, "Conditioned basement"),
    (3, "Conditioned crawlspace"),
    (4, "Attached Garage"),
)

WINDOW_OPERATES = (
    (1, "Yes"),
    (2, "No"),
)
