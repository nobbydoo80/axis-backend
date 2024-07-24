"""analytics.py: Django analytics"""


import logging

from axis.company.models import Company

__author__ = "Steven Klass"
__date__ = "4/10/19 8:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def get_home_status_associations(home_status_id, associated_company_ids):
    associated_companies = associated_company_ids[:]
    from axis.home.models import EEPProgramHomeStatus

    data = {
        "rater": "N/A",
        "rater_id": None,
        "provider": "N/A",
        "provider_id": None,
        "builder": "N/A",
        "builder_id": None,
        "electric_utility": "N/A",
        "electric_utility_id": None,
        "gas_utility": "N/A",
        "gas_utility_id": None,
        "program_sponsor": "N/A",
        "program_sponsor_id": None,
        "qa_organization": "N/A",
        "qa_organization_id": None,
        "other_companies": [],
    }

    try:
        home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
    except EEPProgramHomeStatus.DoesNotExist:
        return data

    data["rater"] = "%s" % home_status.company
    data["rater_id"] = home_status.company_id
    try:
        associated_companies.remove(home_status.company_id)
    except ValueError:
        pass

    builder = home_status.home.get_builder()
    if builder:
        data["builder"] = "%s" % builder
        data["builder_id"] = builder.id
        try:
            associated_companies.remove(builder.id)
        except ValueError:
            pass

    provider = home_status.get_provider()
    if provider:
        data["provider"] = "%s" % provider
        data["provider_id"] = provider.id
        try:
            associated_companies.remove(provider.id)
        except ValueError:
            pass

    electric = home_status.get_electric_company()
    if electric:
        data["electric_utility"] = "%s" % electric
        data["electric_utility_id"] = electric.id
        try:
            associated_companies.remove(electric.id)
        except ValueError:
            pass

    gas = home_status.get_gas_company()
    if gas:
        data["gas_utility"] = "%s" % gas
        data["gas_utility_id"] = gas.id
        try:
            associated_companies.remove(gas.id)
        except ValueError:
            pass

    sponsor = home_status.eep_program.owner
    if sponsor:
        data["program_sponsor"] = "%s" % sponsor
        data["program_sponsor_id"] = sponsor.id
        try:
            associated_companies.remove(sponsor.id)
        except ValueError:
            pass

    for company_id in associated_companies:
        company = Company.objects.get(id=company_id)
        data["other_companies"].append("%s" % company)

    return data
