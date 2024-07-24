__author__ = "Benjamin S"
__date__ = "6/8/2022 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]


# TODO: Refactor enumerations to be Enums
NEW = "new"
STALE = "stale"
UPLOADED = "uploaded"
REPORTED = "reported"
ACTIVE = "active"
FAILED = "failed"

STATUS_CHOICES = (
    (NEW, "New (Not Dispatched for Simulation)"),
    (UPLOADED, "Uploaded HPXML to HES API"),
    (REPORTED, "Simulated (Reports available)"),
    (ACTIVE, "Active (Results obtained)"),
    (STALE, "Stale (updating pending)"),
    (FAILED, "Failed"),
)

NORTH = "north"
SOUTH = "south"
EAST = "east"
WEST = "west"
IN_PROGRESS = "in progress"
COMPLETE = "complete"
