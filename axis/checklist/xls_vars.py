"""xls_vars.py: Django checklist"""


import datetime

__author__ = "Steven Klass"
__date__ = "9/5/13 9:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


HOME_MAP = {
    "object_type": "home.Home",
    "provides_for": [("home_object", "self")],
    "form_class": "axis.home.forms.XLSHomeForm",
    "required": True,
    "attrs": [
        {
            "object_attribute": "id",
            "slug": "home_id",
            "name": "Axis ID",
            "required": False,
            "input_validator": int,
        },
        {
            "object_attribute": "lot_number",
            "slug": "lot_number",
            "name": "Lot #",
            "aliases": ["lot", "lot_number"],
            "required": True,
            "input_validator": str,
        },
        {
            "object_attribute": "street_line1",
            "slug": "street_line1",
            "name": "Street Address",
            "aliases": ["Street Line 1"],
            "required": True,
            "input_validator": str,
        },
        {
            "object_attribute": "street_line2",
            "slug": "street_line2",
            "name": "Street Line 2",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
        {
            "provided_by": "city_object",
            "object_attribute": "city",
            "slug": "city_name",
            "name": "City",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
        {
            "provided_by": "state_object",
            "object_attribute": "state",
            "slug": "state",
            "name": "State",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
        {
            "object_attribute": "zipcode",
            "slug": "zipcode",
            "name": "ZIP Code",
            "aliases": ["ZIP"],
            "required": True,
            "input_validator": str,
        },
        {
            "object_attribute": "subdivision",
            "provided_by": "subdivision_object",
            "slug": "subdivision_name",
            "name": "Subdivision",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
    ],
}

CITY_MAP = {
    "object_type": "geographic.City",
    "provides_for": [
        ("city_object", "self"),
        ("county_object", "county"),
        ("state_object", "state"),
    ],
    "form_class": False,
    "required": True,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "city_name",
            "name": "City",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
        {
            "object_attribute": "county__state",
            "slug": "city_state",
            "name": "State",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
        {
            "object_attribute": "county__name",
            "provided_by": "county_obj",
            "slug": "city_county_name",
            "name": "County",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
    ],
}

COUNTY_MAP = {
    "object_type": "geographic.County",
    "provides_for": [("county_object", "self")],
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "county_name",
            "name": "County",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
    ],
}

SUBDIVISION_MAP = {
    "object_type": "subdivision.Subdivision",
    "provides_for": [("subdivision_object", "self"), ("city_object", "city")],
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "subdivision_name",
            "name": "Subdivision",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
        {
            "object_attribute": "builder_name",
            "slug": "subdivision_builder_name",
            "name": "Subdivision Builder Name",
            "aliases": ["subdivision_builder_name"],
            "required": False,
            "input_validator": str,
        },
        {
            "object_attribute": "city",
            "provided_by": "city_object",
            "slug": "subdivision_city",
            "name": "Subdivision City",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
        {
            "object_attribute": "community",
            "provided_by": "community_object",
            "slug": "subdivision_community",
            "name": "Subdivision Community",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
    ],
}

COMMUNITY_MAP = {
    "object_type": "community.Community",
    "provides_for": "community_object",
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "community_name",
            "name": "Community",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
    ],
}

BUILDER_MAP = {
    "object_type": "company.BuilderOrganization",
    "provides_for": [("builder_object", "self")],
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "builder_name",
            "name": "Builder Name",
            "aliases": ["builder_org"],
            "required": False,
            "input_validator": str,
        },
    ],
}


FLOORPLAN_MAP = {
    "object_type": "floorplan.Floorplan",
    "provides_for": "floorplan_object",
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "name",
            "slug": "floorplan_name",
            "name": "Floorplan",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
    ],
}

PROGRAM_MAP = {
    "object_type": "eep_program.EEPProgram",
    "provides_for": "program_object",
    "form_class": False,
    "attrs": [
        {
            "object_attribute": "id",
            "slug": "eep_program_id",
            "name": "Program ID",
            "aliases": [],
            "required": False,
            "input_validator": int,
        },
        {
            "object_attribute": "name",
            "slug": "eep_program_name",
            "name": "Program",
            "aliases": [],
            "required": True,
            "input_validator": str,
        },
    ],
}


EEPPROGRAMHOMESTATUS_DATA_MAP = {
    "object_type": "home.EEPProgramHomeStatus",
    "attrs": [
        {
            "object_type": "floorplan.Floorplan",
            "object_attribute": "name",
            "slug": "floorplan_name",
            "name": "Floorplan",
            "aliases": ["lot", "lot_number"],
            "required": True,
            "input_validator": str,
        },
        {
            "object_type": "eep_program.EEPProgram",
            "object_attribute": "name",
            "slug": "program_name",
            "name": "Program",
            "aliases": ["EEP Program", "eep_program"],
            "required": True,
            "input_validator": str,
        },
        # BRANCHNOTE: FIXMEEEEEE
        # {'object_type': 'sampling.SampleSet',
        #  'object_attribute': 'alt_name',
        #  'slug': 'sample_set_name',
        #  'name': 'Sample Set',
        #  'aliases': ['SampleSet', 'sample_set'],
        #  'required': False,
        #  'input_validator': str},
        # {'object_type': 'home.EEPProgramHomeStatus',
        #  'object_attribute': 'rating_type',
        #  'slug': 'rating_type',
        #  'name': 'Type',
        #  'aliases': ['Rating Type'],
        #  'required': False,
        #  'input_validator': str},
        {
            "object_type": "home.EEPProgramHomeStatus",
            "object_attribute": "certification_date",
            "slug": "certification_date",
            "name": "Certification Date",
            "required": False,
            "input_validator": datetime.date,
        },
    ],
}

USER_MAP = {
    "object_type": "core.User",
    "provides_for": [("user_object", "self")],
    "form_class": False,
    "required": True,
    "attrs": [
        {
            "object_attribute": "username",
            "slug": "username",
            "name": "User",
            "aliases": [],
            "required": False,
            "input_validator": str,
        },
    ],
}
