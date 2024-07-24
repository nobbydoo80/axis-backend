__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

FLOORPLAN_MODEL_NAME = """Enter the name of the floorplan."""
FLOORPLAN_MODEL_NUMBER = """Enter the numerical identifier for the floorplan."""
FLOORPLAN_MODEL_SQUARE_FOOTAGE = """Enter the square footage of the floorplan."""
FLOORPLAN_MODEL_BASE_FLOORPLAN = """Type the first few letters of the name of subdivision or base
floorplan name and select the correct base floorplan from the list presented.  If the correct base
floorplan is not available, add a base floorplan by editing an existing subdivision or create a
new subdivision and create a base floorplan."""
FLOORPLAN_MODEL_REM_RATE_TARGET = """Type the first few letters of the name of the REM/Rate data
set or subdivision and select the correct REM/Rate data set from the list presented."""
FLOORPLAN_MODEL_REM_RATE_DATA_FILE = """Click on "Select file" and select a file from the
file browser.  Once selected, click on "Change" to select a new file or "Remove" to delete
the file."""
FLOORPLAN_MODEL_COMMENT = """Enter a comment for the floorplan if desired and click
on "Submit" to save the comment."""

FLOORPLAN_FORM_HVAC_SYSTEM_COUNT = """Enter the number of HVAC systems present in the home."""
FLOORPLAN_FORM_VENTILATION_SYSTEM_COUNT = """Enter the number of vetilation sytems
present in the home."""
FLOORPLAN_FORM_COMPANIES = """Select the companies that should have access to the floorplan
data prior to home association.  Select multiple companies by holding the CTRL key down while
selecting companies in the list presented."""
FLOORPLAN_FORM_IS_REVIEWED = """Signifies that APS has reviewed this floorplan."""
FLOORPLAN_FORM_SUBDIVISION = """Select the subdivision where this floorplan is approved for use."""
FLOORPLAN_FORM_THERMOSTAT_QTY = """Number of thermostats this floorplan carries"""

FLOORPLAN_SUBDIVISION_MISMATCH = """Home belongs to subdivision '{subdivision}', which is not
allowed by this floorplan."""
FLOORPLAN_ALREADY_EXISTS_WITH_THIS_INFO = """Please provide a Name or Number as '{name} / {number}'
 already exists"""

# BULK Uploads
MISSING_FLOORPLAN = "No Floorplan provided"
UNKNOWN_FLOORPLAN = "Unknown floorplan {msg}"
FLOORPLAN_USED_CREATE = "{create} Floorplan <a href='{url}'>{floorplan}</a>"
FLOORPLAN_CREATE_MISSING_REMRATE = """Unable to automatically create Floorplan without
REM/Rate® data."""
FLOORPLAN_EXISTS_NO_RELATION = """Floorplan '{floorplan}' exists but you don't have a
association to them"""
MULTIPLE_FLOORPLAN_FOUND = "Multiple Floorplans ({qty}) [{links}] found {msg}"
FOUND_FLOORPLAN = "Using Floorplan <a href='{url}'>{floorplan}</a>"
FLOORPLAN_MISSING_REM_DATA = """Program '{program}' required REM/Rate Data for certification and
REM/Rate data is not attached to floorplan <a href='{url}'>{floorplan}</a>."""
FLOORPLAN_MISSING_REM_FILE = """Program {program} requires REMRate BLG File and it was not
provided in floorplan <a href='{url}'>{floorplan}</a>{msg}"""
FLOORPLAN_HERS_SCORE_TOO_HIGH = """HERs score of {hers} exceeds the maximum limits {max_hers}
for <a href='{url}'>{program}</a>"""
FLOORPLAN_HERS_SCORE_TOO_LOW = """HERs score of {hers} doesn't meet the minimum limits {min_hers}
for the for <a href='{url}'>{program}</a>"""
FLOORPLAN_APS_PROGRAM_AUTO_SET = """APS Program has been automatically updated to
<a href='{url}'>{program}</a> which reflects the optimal program based on HERS score of {hers}"""

APS_REMRATE_DATA_CHANGE = """{company} has changed the {data} for
<a href='{url}'>{floorplan}</a>.  Please review these changes."""
APS_REMRATE_DATA_ADD = """{company} has assigned {data} for <a href='{url}'>{floorplan}</a>.
Please review these changes."""
