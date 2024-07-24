"""strings.py: Django eep_program"""


import logging

__author__ = "Steven Klass"
__date__ = "6/23/14 10:44 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# Bulk upload
MISSING_PROGRAM = "No Program provided"
UNKNOWN_PROGRAM_BY_ID = "Unknown Program with id '{id}'"

MISSING_RATING_TYPE = "When specifying a program you must specify the rating type - it's missing."
PROGRAM_EXISTS_NO_RELATION = (
    "Program '{program}' exists but you don't have a association to the "
    "program owner {owner} or it is no longer active"
)

UNKNOWN_PROGRAM = "Unknown Program '{program}'"
MULTIPLE_PROGRAMS_FOUND = "Multiple Program found for '{program}'"
PROGRAM_ALREADY_IN_USE = "Program '{program}' is already being used by {company} in subdivision <a href='{url}'>{subdivision}</a>"
PROGRAM_DISALLOW_SAMPLING = "Program <a href='{url}'>{program}</a> does not allow sampling."


FOUND_PROGRAM = "Using Program <a href='url'>{program}</a>"

PROGRAM_SUBMIT_DATE_APPROACHING = (
    """{program_name} must be submitted on existing AXIS homes before {date}."""
)
PROGRAM_END_DATE_APPROACHING = (
    """{program_name} can be completed on existing AXIS homes before {date}."""
)

ETO_2018_IMPROVEMENT_FAILURE = """Home is below {min_pct}% improvement and cannot be certified."""
ETO_2018_IMPROVEMENT_QA_WARNING = """Home is below 10% improvement. QA will determine if home qualifies under Path 1 requirements."""
ETO_NO_MULTIFAMILY_HOME = """Home must not be designated as multifamily."""
ETO_NO_MULTIFAMILY_REM = """REM building type must not be designated as multifamily."""
ETO_2018_REM_FILE_VERSION = """REM file must be version 15.3 and flavor "rate" (national). """
ETO_2018_REM_DATA_VERSION = """REM data must be version 15.3 and flavor "rate" (national). """
ETO_2018_HEATING_FUEL_MISMATCH = """Primary heating fuel '{rem_fuel}' does not match checklist answer for primary heating fuel '{checklist_fuel}'"""
ETO_2018_DRYER_LOCATION_NOT_CONDITIONED = """Location must be conditioned"""
ETO_2018_DRYER_FUEL_MISMATCH = """Dryer fuel '{dryer_fuel}' must match checklist answer for primary heating fuel '{checklist_fuel}'"""
ETO_2018_DRYER_EF_NOT_3_01 = """EF must be 3.01"""
ETO_HEAT_PUMP_WATER_HEATER_SERIAL_NUMBER_REQUIRED = """A serial number must be provided as a checklist answer when a heat pump water heater is present."""

ETO_HEATING_FUEL_MISMATCH = """Primary heating fuel '{simulation_fuel}' does not align checklist answer for primary heating type '{checklist_fuel}'"""

ETO_REM_DATA_VERSION = """REM data must be version 15.7.1 and flavor "rate" (national)."""
ETO_ALLOWED_UTILITY_COMPANIES = """{company} is not an allowed {type} company"""

FAILING_UDRH_CHECKSUM = """Incorrect UDRH associated with as built home. Repeat the UDRH export from REM and attach to home"""
FAILING_UDRH_FILE = """Incorrect UDRH File used - expected {file}. This is verified via checksum"""

APS_2019_FAILING_REM_ESTAR = """REM/Rate Simulation Did NOT pass ENERGYSTAR V3 Requirements"""
APS_2019_FAILING_EKOTROPE_ESTAR = """Ekotrope Simulation Did NOT pass ENERGYSTAR V3 Requirements"""

# Program specific notes
# Format: {slug_uppercase}_PROGRAM_NOTE

NEEA_ENERGY_STAR_V3_PERFORMANCE_PROGRAM_NOTE = """It is highly recommended that Raters attach a copy of the NW Compliance report to home records in Axis and that Certification Organizations review the appropriate compliance report via NW REM/Rate or Axis to confirm the “Meets or Beats” annotation selected for the home."""
NEEA_PERFORMANCE_2015_PROGRAM_NOTE = NEEA_ENERGY_STAR_V3_PERFORMANCE_PROGRAM_NOTE
