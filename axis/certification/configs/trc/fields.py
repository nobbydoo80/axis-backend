from decimal import Decimal
import logging

from django.urls import reverse

from ... import validators
from .utils import get_company
from . import choices

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def populate_config_data_fields(config):
    """Modifies the given config using the field spec dicts in this module."""
    batches = {
        # slot where sorted to -> applicable field spec dict
        "settings": settings,
        "data": fields,
    }
    for data_slot, spec_info in batches.items():
        for slug, field_spec in spec_info.items():
            # Unpack custom type settings into the field that referenced it
            if field_spec["type"] in custom_field_types:
                field_type_spec = custom_field_types[field_spec["type"]]
                field_spec["specialized_type"] = field_spec["type"]
                field_spec["type"] = field_type_spec["native_type"]

                # Add custom form field attrs
                field_spec.setdefault("attrs", {}).update(field_type_spec.get("attrs", {}))

                # Add custom validators
                field_spec.setdefault("validators", []).extend(
                    field_type_spec.setdefault("validators", [])
                )

            # Copy the fields into their object_type slots in the main config dict.  Fields can end
            # up in multiple places depending on their individual 'settings' entry.
            for object_type in field_spec["settings"]["object_type"]:
                object_type_spec = config["object_types"][object_type]

                # Target for processed specs (either 'data' or 'settings') for the applicable
                # object_type.  Specs that want to go into both Project and Building, for example,
                # will have the loop run once for each, populating each type's spec list.
                data_spec = object_type_spec[data_slot]

                # Run transforms on the source spec for the current object_type
                result_specs = {
                    slug: field_spec.copy(),  # Don't want accidents between object_type loops
                }
                for f in field_spec.get("transforms", []):
                    result_specs = f(result_specs, slug, object_type, object_type_spec)

                data_spec.update(result_specs)


# Transform functions that take the existing specs for a field and modify it.  These functions may
# return multiple new specs.  All such created specs are passed via the ``field_specs`` argument.
# If two transforms are applied to a data field and the first one turns the original spec into two
# buddy specs, then the second transform will receive the dict of both for ``field_specs``.
def transform_add_object_type_name(field_specs, slug, object_type, object_type_spec):
    for _, field_spec in field_specs.items():
        field_spec["label"] += " - {name}".format(**object_type_spec)
    return field_specs


def transform_double_for_installed(field_specs, slug, object_type, object_type_spec):
    original_spec = field_specs[slug]

    # Overwrite original with suffix
    field_specs[slug] = dict(
        original_spec,
        **{
            "label": original_spec["label"] + " (Enrolled)",
        },
    )

    # Add separate spec for 'installed' version of the same field
    field_specs[slug + "_installed"] = dict(
        original_spec,
        **{
            "label": original_spec["label"] + " (Installed)",
        },
    )

    return field_specs


# Lazy callable utils for field values
def get_contact_add_url(type):
    def lazy_getter(field_name, instance=None):
        return reverse("apiv2:contacts-list") + "?type=" + type

    return lazy_getter


def get_contact_view_url(type):
    def lazy_getter(field_name, instance):
        pk = instance.data.get(field_name, None)
        if pk is None:
            return None
        return reverse("apiv2:contacts-detail", kwargs={"pk": pk}) + "?type=" + type

    return lazy_getter


# Fancy types mapped to native types with accompanying validators
custom_field_types = {
    "reasonable_date": {
        "native_type": "date",
        "validators": [validators.reasonable_date],
    },
    "reasonable_year": {
        "native_type": "number",
        "validators": [validators.reasonable_year],
    },
    "dollar": {
        "native_type": "text",
        "validators": [validators.currency],
        "attrs": {
            "data-addon-start": "$",
        },
    },
    "percent": {
        "native_type": "decimal",
        "validators": [validators.percent],
        "attrs": {
            "data-addon-end": "%",
        },
    },
    "rich_decimal": {
        "native_type": "text",
        "validators": [validators.rich_decimal],
    },
    # introspection flags for build_serializer_field_from_spec()
    "new_or_existing_model_select": {
        "native_type": "select",
    },
    "model_select": {
        "native_type": "select",
    },
}


# Stuff that will live on the Project but be pushed down to the WorkflowStatus
settings = {
    "project_id": {
        "required": True,
        "label": "Project ID",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_number": {
        "required": True,
        "label": "Project Number",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_name": {
        "required": True,
        "label": "Project Name",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_street1": {
        "required": True,
        "label": "Street1",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_street2": {
        "required": False,
        "label": "Street2",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_city": {
        "required": True,
        "label": "City",
        "type": "select",
        "api_widget": choices.ajax_widgets["project_city"],
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_state": {
        "required": True,
        "label": "State",
        "type": "select",
        "choices": choices.static_choices["project_state"],
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_county": {
        "required": True,
        "label": "County",
        "type": "select",
        "model": "geographic.County",
        "api_widget": choices.ajax_widgets["project_county"],
        "settings": {
            "object_type": ["project"],
        },
    },
    "project_zip": {
        "required": True,
        "label": "Zipcode",
        "type": "text",
        "settings": {
            "object_type": ["project"],
        },
    },
    "building_name": {
        "required": True,
        "label": "Building Name",
        "type": "text",
        "settings": {
            "object_type": ["building"],
        },
    },
    # "type": {
    #     "required": True,
    #     "label": "Type",
    #     "type": "select",
    #     "choices": choices.static_choices['project_type'],
    #     "settings": {
    #         "object_type": ["project"],
    #     },
    # },
}


# Calculation functions for fields with computed values
def weighted(f):  # Decorator
    def weight_specifier(weight_field_name):
        def get_value(*args, **kwargs):
            kwargs["weight_field_name"] = weight_field_name
            return f(*args, **kwargs)

        return get_value

    return weight_specifier


def target_field_name(f):  # Decorator
    """Locks the target field for computation to the one provided."""

    def value_getter(target_field_name=None, *outer_args, **outer_kwargs):
        def proxy(*args, **kwargs):
            if target_field_name is not None:
                kwargs["field_name"] = target_field_name
            return f(*args, **kwargs)

        if target_field_name:
            return proxy
        return proxy(*outer_args, **outer_kwargs)

    return value_getter


def _get_values_from_buildings(project, field_name, default=None):
    """Returns the named data point from each building, missing items filled with the default."""
    # If you don't want blanks coming through, run the returned list through a filter
    # such as filter(None, values)
    buildings = project.certifiable_object.children.all()
    return list(
        buildingstatus.data.get(field_name, default)
        for building in buildings
        for buildingstatus in building.workflowstatus_set.all()
    )


@target_field_name
def sum_building_values(instance, field_name, item_spec, context):
    values = list(filter(None, _get_values_from_buildings(instance, field_name, default=None)))
    if len(values):
        values = [Decimal(value) for value in values]
        return sum(values)


def count_buildings(instance, field_name, item_spec, context):
    return instance.certifiable_object.children.count()


@weighted
def average_building_values(instance, field_name, item_spec, context, weight_field_name=None):
    values = _get_values_from_buildings(instance, field_name, default=None)
    weights = [1] * len(values)
    if weight_field_name:
        weights = _get_values_from_buildings(instance, weight_field_name, default=None)

    # Strip away items lacking a weight or value
    dataset = filter((lambda entry: all(entry)), zip(values, weights))

    # Coerce so we're not going to find raw unicode data values
    dataset = [(Decimal(value), Decimal(weight)) for value, weight in dataset]

    # Get pruned weights list
    total_weight = sum(weight for value, weight in dataset)

    if len(dataset):
        return sum(value * weight for value, weight in dataset) / total_weight
    return None


# Master directory of data fields they want, which get used multiple times in various combinations.
# We process this into the real config, but this is easy to manipulate based on how they gave us the
# information.
fields = {
    "lead_contact_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Lead Contact Date",
        "type": "reasonable_date",
        "attrs": {
            "disabled": True,
        },
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "pre_qual_start_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Pre-qual Start Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_package_complete_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Application Package Complete Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_form_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Application Form Received",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "energy_model_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Energy Model Received",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "assessment_report_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Energy Efficiency Plan Received",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "photos_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Photos Received",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    # "tech_assist_start_date": {
    #     "required": True,
    #     "category": "Participation Status",
    #     "label": "Tech Assist Start Date",
    #     "type": "reasonable_date",
    #     "settings": {
    #         "type": ['new_construction', 'retrofit'],
    #         "object_type": ["project"],
    #     },
    # },
    "energy_advisor": {
        "required": True,
        "category": "Participation Status",
        "label": "Energy Advisor",
        "model": "core.User",
        "type": "model_select",
        "choices": choices.dynamic_choices["energy_advisor"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_reserved": {
        "required": True,
        "category": "Incentive Details",
        "label": "Date Reserved",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_scheduled": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Scheduled",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_performed": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Performed",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "trc_verifier": {
        "required": True,
        "category": "Participation Status",
        "label": "TRC Verifier",
        "model": "core.User",
        "type": "model_select",
        "choices": choices.dynamic_choices["trc_verifier"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "bond_applicant": {
        "required": False,
        "category": "Participation Status",
        "label": "OHCS NOFA/Bond Applicant",
        "type": "select",
        "choices": choices.static_choices["bond_applicant"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_reservation_sent": {
        "required": True,
        "category": "Incentive Details",
        "label": "Date Reservation Sent",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_forecast_date": {
        "required": True,
        "category": "Incentive Details",
        "label": "Incentive Forecast Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_request_date": {
        "required": True,
        "category": "Incentive Details",
        "label": "Incentive Request Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "incentive_delivered_date": {
        "required": True,
        "category": "Incentive Details",
        "label": "Incentive Delivered Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    # "project_complete_date": {
    #     "required": False,
    #     "category": "Participation Status",
    #     "label": "Project Review Complete Date",
    #     "type": "reasonable_date",
    #     "settings": {
    #         "type": ['new_construction', 'retrofit'],
    #         "object_type": ["project"],
    #     },
    # },
    "dropped_date": {
        "required": False,
        "category": "Participation Status",
        "label": "Dropped Date",
        "type": "reasonable_date",
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
        "choices": choices.static_choices["dropped_reason"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "waitlist_date": {
        "required": True,
        "category": "Participation Status",
        "label": "Waitlist Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "utility_electric": {
        "required": True,
        "category": "Project Data",
        "label": "Utility - Electric",
        "type": "select",
        "choices": choices.static_choices["utility_electric"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "utility_gas": {
        "required": True,
        "category": "Project Data",
        "label": "Utility - Gas",
        "type": "select",
        "choices": choices.static_choices["utility_gas"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "water_heater_fuel_type": {
        "required": True,
        "category": "Project Data",
        "label": "Water Heater - Fuel Type",
        "type": "select",
        "choices": choices.static_choices["water_heater_fuel_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "space_heat_fuel_type": {
        "required": True,
        "category": "Project Data",
        "label": "Space Heat - Fuel Type",
        "type": "select",
        "choices": choices.static_choices["space_heat_fuel_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "water_heater_distribution_type": {
        "required": True,
        "category": "Project Data",
        "label": "Water Heater - Distribution Type",
        "type": "select",
        "choices": choices.static_choices["water_heater_distribution_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "space_heat_distribution_type": {
        "required": True,
        "category": "Project Data",
        "label": "Space Heat - Distribution Type",
        "type": "select",
        "choices": choices.static_choices["space_heat_distribution_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "number_of_buildings": {
        "required": True,
        "category": "Project Data",
        "label": "Est. Number of Buildings",
        "type": "number",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "number_of_floors": {
        "required": True,
        "category": "Project Data",
        "label": "Number of Floors",
        "type": "number",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["building"],
        },
    },
    "number_of_units": {
        "required": True,
        "category": "Project Data",
        "label": "Est. Number of Units",
        "type": "number",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name],
    },
    "conditioned_floor_area": {
        "required": True,
        "category": "Project Data",
        "label": "Conditioned Floor Area",
        "type": "rich_decimal",
        # "value": {'project': sum_building_values},
        # "attrs": {
        #     "project": {"disabled": True},
        # },
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["building"],  # ["project", "building"]
        },
    },
    "property_class": {
        "required": True,
        "category": "Project Data",
        "label": "Property Class",
        "type": "select",
        "choices": choices.static_choices["property_class"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "rise_type": {
        "required": True,
        "category": "Project Data",
        "label": "Rise Type",
        "type": "select",
        "choices": choices.static_choices["rise_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "resident_type": {
        "required": True,
        "category": "Project Data",
        "label": "Resident Type",
        "type": "select",
        "choices": choices.static_choices["resident_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "project_memo_field": {
        "required": True,
        "category": "Project Data",
        "label": "Project Memo Field",
        "type": "text",
        "widget_type": "textarea",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "expected_construction_start_date": {
        "required": True,
        "category": "Project Data",
        "label": "Expected Construction Start Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "expected_construction_completion_date": {
        "required": True,
        "category": "Project Data",
        "label": "Expected Construction Completion Date",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "energy_modeling_method": {
        "required": True,
        "category": "Project Data",
        "label": "Energy Modeling Method",
        "type": "select",
        "choices": choices.static_choices["energy_modeling_method"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "retrofit_scope_of_work": {
        "required": True,
        "category": "Project Data",
        "label": "Retrofit Scope of Work",
        "type": "select",
        "choices": choices.static_choices["retrofit_scope_of_work"],
        "settings": {
            "type": "retrofit",
            "object_type": ["project", "building"],
        },
    },
    "code_year": {
        "required": True,
        "category": "Project Data",
        "label": "Code Year",
        "type": "select",
        "choices": choices.static_choices["code_year"],
        "settings": {
            "type": "new_construction",
            "object_type": ["project", "building"],
        },
    },
    "year_built": {
        "required": True,
        "category": "Project Data",
        "label": "Year Built",
        "type": "reasonable_year",
        "settings": {
            "type": ["retrofit"],
            "object_type": ["project"],
        },
    },
    "year_renovated": {
        "required": True,
        "category": "Project Data",
        "label": "Year Renovated",
        "type": "reasonable_year",
        "settings": {
            "type": "retrofit",
            "object_type": ["project"],
        },
    },
    "payee_company": {
        "required": True,
        "category": "Project Contacts",
        "label": "Payee Company",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="company"),
            "data-add-new-scope": {"type": "company"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="company"),
        },
        "choices": choices.dynamic_choices["payee_company"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "payee_contact": {
        "required": True,
        "category": "Project Contacts",
        "label": "Payee Contact",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="person"),
            "data-add-new-scope": {"type": "person"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="person"),
        },
        "choices": choices.dynamic_choices["payee_contact"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "customer_company": {
        "required": False,
        "category": "Project Contacts",
        "label": "Customer Company",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="company"),
            "data-add-new-scope": {"type": "company"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="company"),
        },
        "choices": choices.dynamic_choices["customer_company"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "customer_contact": {
        "required": True,
        "category": "Project Contacts",
        "label": "Customer Contact",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="person"),
            "data-add-new-scope": {"type": "person"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="person"),
        },
        "choices": choices.dynamic_choices["customer_contact"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "application_package_coordinator": {
        "required": False,
        "category": "Project Contacts",
        "label": "Application Package Coordinator",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="person"),
            "data-add-new-scope": {"type": "person"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="person"),
        },
        "choices": choices.dynamic_choices["application_package_coordinator"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "energy_modeler": {
        "required": True,
        "category": "Project Contacts",
        "label": "Energy Modeler",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="person"),
            "data-add-new-scope": {"type": "person"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="person"),
        },
        "choices": choices.dynamic_choices["energy_modeler"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verifier": {
        "required": True,
        "category": "Project Contacts",
        "label": "Verifier",
        "model": "company.Contact",
        "type": "new_or_existing_model_select",
        "attrs": {
            "data-add-new-template-url": "/examine/certification/trc/contact_form.html",
            "data-add-new-url": get_contact_add_url(type="person"),
            "data-add-new-scope": {"type": "person"},
            "data-view-template-url": "/examine/certification/trc/contact_detail.html",
            "data-view-url": get_contact_view_url(type="person"),
        },
        "choices": choices.dynamic_choices["verifier"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_review_started": {
        "required": True,
        "category": "Participation Status",
        "label": "Date Review Started",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_review_complete": {
        "required": False,
        "category": "Participation Status",
        "label": "Date Review Complete",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "review_memo_field": {
        "required": False,
        "category": "Participation Status",
        "label": "Review Memo Field",
        "type": "text",
        "widget_type": "textarea",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "date_comments_sent": {
        "required": True,
        "category": "Participation Status",
        "label": "Date Comments Sent",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "kwh_savings": {
        "required": True,
        "category": "Energy Data",
        "label": "kWh Savings",
        "type": "rich_decimal",
        "value": {"project": sum_building_values},
        "attrs": {
            "project": {"disabled": True},
        },
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "therms_savings": {
        "required": True,
        "category": "Energy Data",
        "label": "therms Savings",
        "type": "rich_decimal",
        "value": {"project": sum_building_values},
        "attrs": {
            "project": {"disabled": True},
        },
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "percent_improvement": {
        "required": True,
        "category": "Energy Data",
        "label": "Percent Improvement",
        "type": "percent",
        "value": {"project": average_building_values(weight_field_name="conditioned_floor_area")},
        "attrs": {
            "project": {"disabled": True},
        },
        "settings": {
            "type": "retrofit",
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "percent_above_code": {
        "required": True,  # ?
        "category": "Energy Data",
        "label": "Percent Above Code",
        "type": "percent",
        "value": {"project": average_building_values(weight_field_name="conditioned_floor_area")},
        "attrs": {
            "project": {"disabled": True},
        },
        "settings": {
            "type": "new_construction",
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "prescriptive_measures_section": {
        "required": True,
        "category": "Prescriptive Details",
        "label": "Prescriptive Measures Section",
        "type": "selectmultiple",
        "choices": choices.static_choices["prescriptive_measures_section"],
        "settings": {
            "type": "Different subsets for each",  # ?
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "incentive_type": {
        "required": True,
        "category": "Incentive Details",
        "label": "Program Pathway",
        "type": "select",
        "choices": choices.static_choices["incentive_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
    },
    "total_incentive": {
        "required": True,
        "category": "Incentive Details",
        "label": "Total Incentive",
        "type": "dollar",
        "value": {"project": sum_building_values},
        "attrs": {
            "project": {"disabled": True},
        },
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project", "building"],
        },
        "transforms": [transform_add_object_type_name, transform_double_for_installed],
    },
    "verification_memo_field": {
        "required": False,
        "category": "Participation Status",
        "label": "Verification Memo Field",
        "type": "text",
        "widget_type": "textarea",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_type": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Type",
        "type": "select",
        "choices": choices.static_choices["verification_type"],
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_documents_received": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Documents Received",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "verification_complete": {
        "required": True,
        "category": "Participation Status",
        "label": "Verification Complete",
        "type": "reasonable_date",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "stat__number_of_buildings": {
        "required": False,
        "category": "calculation",
        "label": "Number of Buildings",
        "type": "number",
        "value": count_buildings,
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    "stat__number_of_units": {
        "required": False,
        "category": "calculation",
        "label": "Number of Units",
        "type": "number",
        "value": sum_building_values("number_of_units"),
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
    # "stat__conditioned_floor_area": {
    #     "required": False,
    #     "category": "[Computed]",
    #     "label": "Conditioned Floor Area",
    #     "type": "number",
    #     "value": sum_building_values,
    #     "settings": {
    #         "type": ['new_construction', 'retrofit'],
    #         "object_type": ["project"],
    #     },
    # },
    "escalated": {
        "required": False,
        "category": "admin",
        "label": "Is Elevated",
        "type": "boolean",
        "settings": {
            "type": ["new_construction", "retrofit"],
            "object_type": ["project"],
        },
    },
}
