"""fixturecompilers.py: Django company"""


__author__ = "Steven Klass"
__date__ = "9/18/14 1:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from axis.company.tests.factories import rater_organization_factory, provider_organization_factory
from axis.core.tests.factories import (
    general_super_user_factory,
    provider_admin_factory,
    rater_admin_factory,
)
from axis.eep_program.models import EEPProgram
from axis.equipment.states import EquipmentSponsorStatusStates
from axis.relationship.models import Relationship
from axis.geographic.tests.factories import real_city_factory

from .factories import equipment_factory, equipment_sponsor_status_factory

log = logging.getLogger(__name__)


class EquipmentFixtureMixin:
    @classmethod
    def setUpTestData(cls):
        city = real_city_factory("Fayetteville", "NC")
        general_super_user_factory(company__city=city)
        momentum_company = rater_organization_factory(name="momentum", city=city)
        rater_admin_factory(company=momentum_company)
        neea_company = provider_organization_factory(
            name="neea", slug="neea", is_customer=True, city=city
        )
        provider_admin = provider_admin_factory(
            company=neea_company, username="neea_provider_admin"
        )

        eep_program = EEPProgram.objects.create(
            **{
                "name": "NEEA",
                "owner": neea_company,
                "is_legacy": False,
                "is_public": True,
                "is_active": True,
                "is_qa_program": False,
                "slug": "wa-code-study",
            }
        )
        eep_program.certifiable_by.add(neea_company)

        Relationship.objects.create_mutual_relationships(momentum_company, neea_company)

        equipment = equipment_factory(owner_company=momentum_company)
        equipment_sponsor_status_factory(
            equipment=equipment, state=EquipmentSponsorStatusStates.NEW, company=neea_company
        )

        equipment = equipment_factory(owner_company=momentum_company)
        equipment_sponsor_status_factory(
            equipment=equipment,
            state=EquipmentSponsorStatusStates.ACTIVE,
            company=neea_company,
            approver=provider_admin,
        )

        equipment = equipment_factory(owner_company=momentum_company)
        equipment_sponsor_status_factory(
            equipment=equipment,
            state=EquipmentSponsorStatusStates.REJECTED,
            company=neea_company,
            approver=provider_admin,
        )

        equipment = equipment_factory(owner_company=momentum_company)
        equipment_sponsor_status_factory(
            equipment=equipment,
            state=EquipmentSponsorStatusStates.EXPIRED,
            company=neea_company,
            approver=provider_admin,
        )
