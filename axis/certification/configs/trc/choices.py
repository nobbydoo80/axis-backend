import logging

from localflavor.us.us_states import US_STATES

from .utils import get_company

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Ajax version
# def get_company_user_widget():
#     from axis.company.fields import CompanyUserChoiceApiWidget
#     return CompanyUserChoiceApiWidget


# Static choices
def get_company_user_choices():
    company = get_company()
    return [
        (
            user.id,
            "{name}{title_area}".format(
                **{
                    "name": user.get_full_name(),
                    "title_area": (" ({})".format(user.title) if user.title else ""),
                }
            ),
        )
        for user in company.users.filter(is_active=True)
    ]


def get_company_contact_choices():
    company = get_company()
    return [
        (contact.id, "{}".format(contact)) for contact in company.contact_set.filter(type="company")
    ]


def get_person_contact_choices():
    company = get_company()
    return [
        (contact.id, "{}".format(contact)) for contact in company.contact_set.filter(type="person")
    ]


def get_city_widget():
    from axis.geographic.fields import CityChoiceWidget

    return CityChoiceWidget


def get_county_widget():
    from axis.geographic.fields import CountyChoiceWidget

    return CountyChoiceWidget


# Easy references for down in the big 'fields' dict
ajax_widgets = {
    "project_city": get_city_widget,
    "project_county": get_county_widget,
}
dynamic_choices = {
    "payee_company": get_company_contact_choices,
    "payee_contact": get_person_contact_choices,
    "customer_company": get_company_contact_choices,
    "customer_contact": get_person_contact_choices,
    "application_package_coordinator": get_person_contact_choices,
    "energy_modeler": get_person_contact_choices,
    "verifier": get_person_contact_choices,
    "energy_advisor": get_company_user_choices,
    "trc_verifier": get_company_user_choices,
}

static_choices = {
    "project_state": US_STATES,
    "dropped_reason": (
        ("noqual_type", "Non-qualifying building type"),
        ("noqual_scope", "Non-qualifying scope of work"),
        ("noqual_status", "Non-qualifying affordability status"),
        ("noqual_location", "Non-qualifying location"),
        ("advanced", "Construction advanced too far"),
        ("unresponsive", "Unresponsive"),
        ("cancelled", "Project cancelled"),
        ("low_incentives", "Participant lost interest – incentives too low"),
        ("too_intensive", "Participant lost interest – program is too time intensive"),
    ),
    "utility_electric": (
        ("Pacific Power", "Pacific Power"),
        ("Portland General Electric", "Portland General Electric"),
        ("other", "other"),
    ),
    "utility_gas": (
        ("Northwest Natural", "Northwest Natural"),
        ("Avista", "Avista"),
        ("Cascade Natural Gas", "Cascade Natural Gas"),
    ),
    "water_heater_fuel_type": (
        ("Natural Gas", "Natural Gas"),
        ("Oil", "Oil"),
        ("Electric - resistance", "Electric - resistance"),
        ("Electric-heat pump", "Electric-heat pump"),
        ("other", "other"),
    ),
    "space_heat_fuel_type": (
        ("Natural Gas", "Natural Gas"),
        ("Oil", "Oil"),
        ("Electric - resistance", "Electric - resistance"),
        ("Electric-heat pump", "Electric-heat pump"),
        ("Other", "Other"),
    ),
    "water_heater_distribution_type": (
        ("Central", "Central"),
        ("Unit", "Unit"),
        ("Mixed", "Mixed"),
    ),
    "space_heat_distribution_type": (
        ("Central", "Central"),
        ("Unit", "Unit"),
        ("Mixed", "Mixed"),
    ),
    "property_class": (
        ("Apartments", "Apartments"),
        ("Townhouse", "Townhouse"),
        ("SRO", "SRO"),
        ("Condo", "Condo"),
        ("Mixed", "Mixed"),
    ),
    "rise_type": (
        ("Mixed", "Mixed"),
        ("Low Rise (1-3)", "Low Rise (1-3)"),
        ("High Rise (4+)", "High Rise (4+)"),
    ),
    "resident_type": (
        ("Seniors/Assisted Living", "Seniors/Assisted Living"),
        ("Special Needs", "Special Needs"),
        ("Student", "Student"),
        ("Veterns", "Veterns"),
        ("non-specified", "non-specified"),
    ),
    "energy_modeling_method": (
        ("REM/Rate", "REM/Rate"),
        ("eQuest", "eQuest"),
        ("EnergyPro", "EnergyPro"),
        ("others TBD", "others TBD"),
    ),
    "retrofit_scope_of_work": (
        ("Comprehensive Rehab", "Comprehensive Rehab"),
        ("Partial retrofit/upgrades", "Partial retrofit/upgrades"),
        (
            "Upgrade dwelling unit at tenant turnover",
            "Upgrade dwelling unit at tenant turnover",
        ),
        ("upgrade common area/central system", "upgrade common area/central system"),
        (
            "undecided and/or no upgrades planned",
            "undecided and/or no upgrades planned",
        ),
    ),
    "code_year": (
        # Needs possible expansion
        (2017, "2017"),
        (2014, "2014"),
    ),
    "prescriptive_measures_section": (
        # {needs to be expanded}
    ),
    "incentive_type": (
        ("Menu", "Menu"),
        ("Bundled", "Bundled"),
        ("Whole Building ", "Whole Building "),
    ),
    "verification_type": (
        ("Desktop QC", "Desktop QC"),
        ("Field QC", "Field QC"),
    ),
    "bond_applicant": (
        ("LIFT", "LIFT"),
        ("9% LIHTC", "9% LIHTC"),
        ("4% LIHTC", "4% LIHTC"),
        ("HOME", "HOME"),
        ("Other OHCS", "Other OHCS"),
    ),
}
