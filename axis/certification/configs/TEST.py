import logging

from django_states.machine import StateMachine, StateDefinition, StateTransition

from .. import validators
from .base import ConfigStateMachineMixin, ConfigStateTransition

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# FIXME: Temp stuff until we have Axis powering these
city_choices = (("one", "FIXME"),)

contacts_choices = (
    ("one", "Contact A"),
    ("two", "Contact B"),
)

project_type_choices = (
    ("new_construction", "New Construction"),
    ("retrofit", "Retrofit"),
)

# Fancy types mapped to native types with accompanying validators
custom_field_types = {
    "year": {
        "native_type": "number",
        "validators": [validators.validate_year],
    }
}


# Shorthand for all of TRCs wide-open transition logic
ALL_STATES = [
    "lead",
    "pre_qual",
    "application",
    "technical_assistance",
    "incentive_reserved",
    "verification",
    "incentive_requested",
    "complete",
    "project_maintenance",
    "dropped",
    "waitlist",
]


class TRCStateMachine(ConfigStateMachineMixin, StateMachine):
    """State machine for both Project and Building types"""

    state_choices_order = (
        "to_lead",
        "to_pre_qual",
        "to_application",
        "to_technical_assistance",
        "to_incentive_reserved",
        "to_verification",
        "to_incentive_requested",
        "to_complete",
        "to_project_maintenance",
        "to_dropped",
        "to_waitlist",
    )

    # States
    class lead(StateDefinition):
        initial = True
        name = "Lead"
        description = "Lead"

    class pre_qual(StateDefinition):
        name = "Pre-qual"
        description = "Pre-qual"

    class application(StateDefinition):
        name = "Application"
        description = "Application"

    class technical_assistance(StateDefinition):
        name = "Technical assistance"
        description = "Technical assistance"

    class incentive_reserved(StateDefinition):
        name = "Incentive reserved"
        description = "Incentive reserved"

    class verification(StateDefinition):
        name = "Verification"
        description = "Verification"

    class incentive_requested(StateDefinition):
        name = "Incentive requested"
        description = "Incentive requested"

    class complete(StateDefinition):
        name = "Complete"
        description = "Complete"

    class project_maintenance(StateDefinition):
        name = "Project maintenance"
        description = "Project maintenance"

    class dropped(StateDefinition):
        name = "Dropped"
        description = "Dropped"

    class waitlist(StateDefinition):
        name = "Waitlist"
        description = "Waitlist"

    # Transitions
    class to_lead(ConfigStateTransition):
        description = "Lead"
        to_state = "lead"
        from_states = ALL_STATES

    class to_pre_qual(ConfigStateTransition):
        description = "Pre-Qual"
        to_state = "pre_qual"
        from_states = ALL_STATES

    class to_application(ConfigStateTransition):
        description = "Application"
        to_state = "application"
        from_states = ALL_STATES

    class to_technical_assistance(ConfigStateTransition):
        description = "Technical Assistance"
        to_state = "technical_assistance"
        from_states = ALL_STATES

    class to_incentive_reserved(ConfigStateTransition):
        description = "Incentive Reserved"
        to_state = "incentive_reserved"
        from_states = ALL_STATES

    class to_verification(ConfigStateTransition):
        description = "Verification"
        to_state = "verification"
        from_states = ALL_STATES

    class to_incentive_requested(ConfigStateTransition):
        description = "Incentive Requested"
        to_state = "incentive_requested"
        from_states = ALL_STATES

    class to_complete(ConfigStateTransition):
        description = "Complete"
        to_state = "complete"
        from_states = ALL_STATES

    class to_project_maintenance(ConfigStateTransition):
        description = "Project Maintenance"
        to_state = "project_maintenance"
        from_states = ALL_STATES

    class to_dropped(ConfigStateTransition):
        description = "Dropped"
        to_state = "dropped"
        from_states = ALL_STATES

    class to_waitlist(ConfigStateTransition):
        description = "Waitlist"
        to_state = "waitlist"
        from_states = ALL_STATES


# Data interface for outside inspection.
config = {
    "object_types": {
        "project": {
            "name": "Project",
            "state_machine": TRCStateMachine,
            "settings": {
                # CertifiableObject instance settings to filter which 'data' items appear
                "type": {
                    "label": "Type",
                    "type": "select",
                    "choices": project_type_choices,
                },
            },
            "data": {},  # filled in below
        },
        "building": {
            "name": "Building",
            "state_machine": None,  # spec sheet says no state field?  might be a mistake
            "settings": {},
            "data": {},  # filled in below
        },
        # 'unit' is pretty much left alone in the TRC workflow, but it does exist.
        "unit": {
            "name": "Unit",
            "state_machine": None,
            "settings": {},
            "data": {},
        },
    },
}

# Master directory of data fields they want, which get used multiple times in various combinations.
# We process this into the real config, but this is easy to manipulate based on how they gave us the
# information.
fields = {
    # This is promoted to a StateField on the model
    # "project_status": {
    #     "required": True,
    #     "category": "Participation Status",
    #     "label": "Project Status",
    #     "type": "Dropdown",
    #     "settings": {
    #         "type": ['new_construction', 'retrofit'],
    #         "object_types": ["project"],
    #     },
    # },
    "lead_contact_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Lead Contact Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "pre_qual_start_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Pre-qual Start Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_package_complete_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Application Package Complete Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_form_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Application Form Received",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "energy_model_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Energy Model Received",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "assessment_report_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Asssessment report received",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "photos_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Photos received",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "tech_assist_start_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Tech Assist Start Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "energy_advisor": {
        "required": True,
        "category": "Participation Status",
        "label": "Energy Advisor",
        "type": "select",
        "choices": contacts_choices,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_reserved": {
        "required": True,
        "category": "Participation Status",
        "label": "Date Reserved",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_scheduled": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Scheduled",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_performed": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Performed",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "trc_verifier": {
        "required": True,
        "category": "Participation Status",
        "label": "TRC Verifier",
        "type": "select",
        "choices": contacts_choices,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_forecast_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Incentive Forecast Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_request_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Incentive Request Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_delivered_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Incentive Delivered Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_complete_date": {
        "required": False,
        "category": "Participation Status",
        "label": "Project Complete Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "dropped_date": {
        "required": False,
        "category": "Participation Status",
        "label": "Dropped Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "dropped_reason": {
        "required": True,
        "category": "Participation Status",
        "label": "Dropped Reason",
        "type": "select",
        "choices": (
            ("withdrawal", "Voluntary Withdrawal"),
            ("no_compliance", "Did not comply with program requirements"),
            ("no_qualifying_measures", "Did not install qualifying measures"),
            ("no_verification", "Completed without verification"),
            ("expired", "Project expired"),
            ("other", "Other"),
        ),
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "waitlist_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Waitlist Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "trigger_dates": {
        "required": True,
        "category": "Participation Status",
        "label": "Trigger Dates",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_name": {
        "required": True,
        "category": "Project Data",
        "label": "Project Name",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_id": {
        "required": True,
        "category": "Project Data",
        "label": "Project ID",
        "type": "Open text , alpha-numeric",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_city": {
        "required": True,
        "category": "Project Data",
        "label": "Project City",
        "type": "select",
        "choices": city_choices,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_street1": {
        "required": True,
        "category": "Project Data",
        "label": "Project Street",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_zip": {
        "required": True,
        "category": "Project Data",
        "label": "Project Zip",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_county": {
        "required": True,
        "category": "Project Data",
        "label": "County",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "utility_electric": {
        "required": True,
        "category": "Project Data",
        "label": "Utility - Electric",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "utility_gas": {
        "required": True,
        "category": "Project Data",
        "label": "Utility - Gas",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "water_heater_fuel_type": {
        "required": True,
        "category": "Project Data",
        "label": "Water Heater - Fuel Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "space_heat_fuel_type": {
        "required": True,
        "category": "Project Data",
        "label": "Space Heat - Fuel Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "water_heater_distribution_type": {
        "required": True,
        "category": "Project Data",
        "label": "Water Heater - Distribution Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "space_heat_distribution_type": {
        "required": True,
        "category": "Project Data",
        "label": "Space Heat - Distribution Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "construction_type": {
        "required": True,
        "category": "Project Data",
        "label": "Construction Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "number_of_buildings": {
        "required": True,
        "category": "Project Data",
        "label": "Number of Buildings",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "number_of_floors": {
        "required": True,
        "category": "Project Data",
        "label": "Number of floors",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "number_of_units": {
        "required": True,
        "category": "Project Data",
        "label": "Number of Units",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "conditioned_floor_area": {
        "required": True,
        "category": "Project Data",
        "label": "Conditioned Floor Area",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "property_class": {
        "required": True,
        "category": "Project Data",
        "label": "Property Class",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "rise_type": {
        "required": True,
        "category": "Project Data",
        "label": "Rise Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "recruitment_method": {
        "required": True,
        "category": "Project Data",
        "label": "Recruitment Method",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "resident_type": {
        "required": True,
        "category": "Project Data",
        "label": "Resident Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_memo_field": {
        "required": True,
        "category": "Project Data",
        "label": "Project Memo field",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "expected_construction_start_date": {
        "required": True,
        "category": "Project Data",
        "label": "Expected Construction Start Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "expected_construction_completion_date": {
        "required": True,
        "category": "Project Data",
        "label": "Expected Construction Completion Date",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "energy_modeling_method": {
        "required": True,
        "category": "Project Data",
        "label": "Energy Modeling Method",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "retrofit_scope_of_work": {
        "required": True,
        "category": "Project Data",
        "label": "Retrofit Scope of Work",
        "type": "Dropdown",
        "settings": {
            "type": "retrofit",
            "object_type": ["project", "building"],
        },
    },
    "code_year": {
        "required": True,
        "category": "Project Data",
        "label": "Code year",
        "type": "Year",
        "settings": {
            "type": "new_construction",
            "object_type": ["project", "building"],
        },
    },
    "year_built": {
        "required": True,
        "category": "Project Data",
        "label": "Year Built",
        "type": "number",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "year_renovated": {
        "required": True,
        "category": "Project Data",
        "label": "Year Renovated",
        "type": "number",
        "settings": {
            "type": "retrofit",
            "object_type": ["project"],
        },
    },
    "payee_company": {
        "required": True,
        "category": "Project Contacts",
        "label": "Payee Company Name",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "customer_contact": {
        "required": True,
        "category": "Project Contacts",
        "label": "Primary Contact",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "customer_company": {
        "required": False,
        "category": "Project Contacts",
        "label": "Developer",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_package_coordinator": {
        "required": False,
        "category": "Project Contacts",
        "label": "Application Package Coordinator",
        "type": "Optional assignment",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "energy_modeler": {
        "required": True,
        "category": "Project Contacts",
        "label": "Energy Modeler",
        "type": "select",
        "choices": contacts_choices,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verifier": {
        "required": True,
        "category": "Project Contacts",
        "label": "Verifier",
        "type": "select",
        "choices": contacts_choices,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_review_started": {
        "required": True,
        "category": "Review Process",
        "label": "Date Review Started",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_review_complete": {
        "required": False,
        "category": "Review Process",
        "label": "Date Review Complete",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "review_memo_field": {
        "required": False,
        "category": "Review Process",
        "label": "Review Memo field",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_comments_sent": {
        "required": True,
        "category": "Review Process",
        "label": "Date Comments sent",
        "type": "date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "kwh_savings": {
        "required": True,
        "category": "Energy Data",
        "label": "kWh savings",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "therms_savings": {
        "required": True,
        "category": "Energy Data",
        "label": "therms savings",
        "type": "float",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "percent_improvement": {
        "required": True,
        "category": "Energy Data",
        "label": "Percent improvement",
        "type": "percent",
        "settings": {
            "type": "retrofit",
            "object_type": ["project", "building"],
        },
    },
    "percent_above_code": {
        "required": True,  # ?
        "category": "Energy Data",
        "label": "Percent above code",
        "type": "percent",
        "settings": {
            "type": "new_construction",
            "object_type": ["project", "building"],
        },
    },
    "prescriptive_measures_section": {
        "required": True,
        "category": "Prescriptive Details",
        "label": "Prescriptive Measures section",
        "type": "Check box",
        "settings": {
            "type": "Different subsets for each",  # ?
            "object_type": ["project", "building"],
        },
    },
    "incentive_type": {
        "required": True,
        "category": "Incentive Details",
        "label": "Incentive Type",
        "type": "Dropdown",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "total_incentive": {
        "required": True,
        "category": "Incentive Details",
        "label": "Total Incentive",
        "type": "Currency numeric",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "building_name": {
        "required": True,
        "category": "Building Data",
        "label": "Building Name",
        "type": "text",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["building"],
        },
    },
}


# Items to duplicate based on TRC's desire to have them answered more once at different points in
# their own process.
installed_doubling = set(
    [
        "kwh_savings",
        "therms_savings",
        "percent_improvement",
        "percent_above_code",
        "prescriptive_measures_section",
        "total_incentive",
    ]
)


# Copy the fields into their object_type slots in the main data dict.  Fields can end up in multiple
# places depending on their individual 'settings' entry.
for slug, field_spec in fields.items():
    if field_spec["type"] in custom_field_types:
        field_type_spec = custom_field_types[field_spec["type"]]
        field_spec["type"] = field_type_spec["native_type"]
        field_type.setdefault("validators", [])
        field_spec["validators"].extend(field_type_spec["validators"])

    for object_type in field_spec["settings"]["object_type"]:
        data = config["object_types"][object_type]["data"]
        data[slug] = field_spec

        # Clone the item so TRC can answer twice
        if slug in installed_doubling:
            data[slug + "_installed"] = dict(
                field_spec,
                **{
                    "label": field_spec["label"] + " (Installed)",
                },
            )
