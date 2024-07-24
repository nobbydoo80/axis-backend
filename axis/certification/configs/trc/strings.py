__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


STATE_NAMES = {
    "initial": "[Initialization]",
    "pre_qual": "Pre-qual",
    "application": "Application",
    "technical_assistance": "Technical Assistance",
    "incentive_reserved": "Incentive Reserved",
    "verification": "Verification",
    "incentive_requested": "Incentive Requested",
    "complete": "Complete",
    "project_maintenance": "Project Maintenance",
    "dropped": "Dropped",
    "waitlist": "Waitlist",
}

SUBSTATE_NAMES = {
    "application": {
        "received": "Received",
        "notified": "Notification Sent",
    },
    "technical_assistance": {
        "assigned": "Assigned",
        "pending": "Pending Signature",
    },
    "verification": {
        "assigned": "Assigned",
        "scheduled": "Scheduled",
        "complete": "Verification Complete",
    },
    "incentive_requested": {
        "approved": "Approved - Pending Incentive & Notification",
    },
    "project_maintenance": {
        "assigned": "Assigned",
    },
}


# Note that a uniqueness token is apended to the end of these strings
TRANSITION_SUCCESSFUL_MESSAGE_STRINGS = {
    "application": """<a href="{project_url}">{project}</a> has been initiated; please send application documents""",
    "technical_assistance": """<a href="{project_url}">{project}</a> is ready for technical review and assignment of Energy Advisor""",
    "incentive_reserved": """<a href="{project_url}">{project}</a> has an incentive reserved; please monitor progress""",
    "verification": """<a href="{project_url}">{project}</a> is eligible for verification and assignment of Energy Advisor""",
    "incentive_requested": """Incentive requested for <a href="{project_url}">{project}</a>""",
    "project_maintenance": """<a href="{project_url}">{project}</a> is ready for project maintenance and assignment of Energy Advisor""",
    "dropped": """<a href="{project_url}">{project}</a> has been rejected; please review and take appropriate action""",
    "waitlist": """<a href="{project_url}">{project}</a> has been waitlisted; please review and take appropriate action""",
}

# Note that a uniqueness token is apended to the end of these strings
SUBSTATE_TRANSITION_MESSAGE_STRINGS = {
    "technical_assistance": {
        "assigned": """<a href="{project_url}">{project}</a> has been assigned to you for technical review""",
    },
    "verification": {
        "assigned": """<a href="{project_url}">{project}</a> has been assigned to you for verification review""",
    },
    "incentive_requested": {
        "approved": """<a href="{project_url}">{project}</a> has been approved and is pending incentive creation and approval letter""",
    },
    "project_maintenance": {
        "assigned": """<a href="{project_url}">{project}</a> has been assigned to you for project maintenance review""",
    },
}

PROJECT_ELEVATED_FOR_ADMIN = """<a href="{project_url}">{project}</a> (Status: {state_name}) has been elevated for admin attention."""

INCENTIVE_RESERVED_MONTHLY_MESSAGE = (
    """{days}-day reminder of the <a href="{project_url}">{project}</a> incentive reservation."""
)
INCENTIVE_RESERVED_CONSTRUCTION_REMINDER_MESSAGE = (
    """It is less than 30 days until <a href="{project_url}">{project}</a> construction begins."""
)
