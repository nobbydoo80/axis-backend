__author__ = "Johnny Fang"
__date__ = "6/6/19 11:40 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import logging

from axis.core.tests.factories import (
    basic_user_factory,
    general_super_user_factory,
    provider_user_factory,
)
from django.contrib.auth import get_user_model
from axis.company.models import BuilderOrganization, Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.geographic.models import City
from axis.subdivision.models import Subdivision, EEPProgramSubdivisionStatus, FloorplanApproval
from axis.subdivision.tests.mixins import SubdivisionManagerTestsMixin

log = logging.getLogger(__name__)

User = get_user_model()


class SubdivisionModelTests(SubdivisionManagerTestsMixin, AxisTestCase):
    client_class = AxisClient

    def test_subdivision_save(self):
        """Tests saving a Subdivision using its save()"""
        builder = User.objects.get(username="noperm_builderadmin")
        builder_name = builder.company.name
        builder_org = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).first()
        city = City.objects.first()

        subdivision = Subdivision(
            name="subdivision-1", builder_name=builder_name, builder_org=builder_org, city=city
        )
        subdivision.save()
        result_sub = Subdivision.objects.get(name="subdivision-1")
        self.assertEqual(subdivision, result_sub)
        self.assertEqual(result_sub.county, city.county)
        self.assertEqual(result_sub.metro, city.county.metro)
        self.assertEqual(result_sub.state, city.county.state)
        self.assertIsNotNone(result_sub.slug)

    # def test_user_with_permission_relationship_can_edit(self):
    #     """Test whether a user with relationship can edit subdivision"""
    #     builder = User.objects.get(username="noperm_builderadmin")
    #     subdivision = Subdivision.objects.first()
    #     is_editable_by_user = subdivision.can_be_edited(builder)
    #     self.assertTrue(is_editable_by_user)

    def test_user_with_permission_can_edit(self):
        """Test that a user with permission to change a subdivision can do so"""
        user = self.get_admin_user()
        self.assertTrue(user.has_perm("subdivision.change_subdivision"))
        user = User
        subdivision = Subdivision.objects.first()
        is_editable_by_user = subdivision.can_be_edited(user)
        self.assertTrue(is_editable_by_user)

    def test_user_with_no_perm_can_not_edit(self):
        """Test that a user with no permission to edit a subdivision can't"""
        user = basic_user_factory()
        self.assertFalse(user.has_perm("subdivision.change_subdivision"))
        subdivision = Subdivision.objects.first()
        is_editable_by_user = subdivision.can_be_edited(user)
        self.assertFalse(is_editable_by_user)

    def test_superuser_can_edit(self):
        """Test that a superuser can edit subdivision"""
        user = general_super_user_factory()
        self.assertTrue(user.has_perm("subdivision.change_subdivision"))
        subdivision = Subdivision.objects.first()
        is_editable_by_user = subdivision.can_be_edited(user)
        self.assertTrue(is_editable_by_user)

    def test_model_can_be_added(self):
        """Test model's can_be_added method"""
        user = general_super_user_factory()
        self.assertTrue(user.has_perm("subdivision.add_subdivision"))
        can_be_added = Subdivision.can_be_added(user)
        self.assertTrue(can_be_added)

    def test_model_can_be_added_user_with_no_perms(self):
        """Test model's can_be_added method"""
        user = basic_user_factory()
        self.assertFalse(user.has_perm("subdivision.add_subdivision"))
        can_be_added = Subdivision.can_be_added(user)
        self.assertFalse(can_be_added)

    def test_get_id(self):
        """Test model's get_id method"""
        subdivision = Subdivision.objects.first()
        padded_id = subdivision.get_id()
        self.assertEqual(padded_id, "{:06}".format(subdivision.id))

    def test_get_sample_eligibility_subdivision_level(self):
        """Test model's det_id method"""
        provider = provider_user_factory(username="provideradmin")
        subdivision = Subdivision.objects.first()
        subdivision.use_sampling = True
        subdivision.save()
        result = subdivision.get_sample_eligibility(provider.company)
        self.assertEqual(result, "subdivision")

    def test_get_sample_eligibility_metro_level(self):
        """Test model's det_id method"""
        provider = provider_user_factory(username="provideradmin")
        subdivision = Subdivision.objects.first()
        subdivision.use_sampling = True
        subdivision.use_metro_sampling = True
        subdivision.save()
        result = subdivision.get_sample_eligibility(provider.company)
        self.assertEqual(result, "metro")

    def test_get_sample_eligibility_none(self):
        """Test model's det_id method for company with no sampling eligibility"""
        user = User.objects.get(username="noperm_builderadmin")
        subdivision = Subdivision.objects.first()
        result = subdivision.get_sample_eligibility(user.company)
        self.assertIsNone(result)

    def test_get_fuel_types(self):
        """Test model's get_fuel_types

        simulation_kwargs contains keys with fuel_type for the three equipments
        (heater, hot_water, and air_conditioning)
        this are passed to their respective factories
        (heating_factory, hot_water_factory, air_conditioning_factory)

        """
        from axis.remrate_data.strings import FUEL_TYPES
        from axis.floorplan.tests.factories import floorplan_factory
        from axis.remrate_data.tests.factories import simulation_factory

        user = User.objects.get(username="noperm_builderadmin")
        subdivision = Subdivision.objects.first()

        simulation_kwargs = {
            "heating__fuel_type": 1,
            "hot_water__fuel_type": 1,
            "air_conditioning__fuel_type": 2,
            "dehumidifier_count": 0,
            "shared_equipment_count": 0,
        }

        rem_rate = simulation_factory(**simulation_kwargs)

        floorplan = floorplan_factory(owner=user.company)
        floorplan.floorplanapproval_set.create(subdivision=subdivision)
        floorplan.remrate_target = rem_rate
        floorplan.save()

        result = subdivision.get_fuel_types(user)
        self.assertIsNotNone(result)
        fuel_types = result.split(", ")
        self.assertEqual(fuel_types[0], FUEL_TYPES[0][1])
        self.assertEqual(fuel_types[1], FUEL_TYPES[1][1])

    def test_set_builder(self):
        """Test model's get_builder()"""
        user = User.objects.get(username="noperm_builderadmin")
        subdivision = Subdivision.objects.first()
        builder_org = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).last()
        subdivision.set_builder(builder_org, user)

        self.assertEqual(subdivision.builder_org, builder_org)


class EEPProgramSubdivisionStatusTests(SubdivisionManagerTestsMixin, AxisTestCase):
    def test_creation(self):
        subdivision = Subdivision.objects.first()
        eep_program = EEPProgram.objects.first()
        company = Company.objects.first()

        eep_program_sub_status, created = EEPProgramSubdivisionStatus.objects.get_or_create(
            subdivision=subdivision, eep_program=eep_program, company=company
        )

        self.assertEqual(eep_program_sub_status.subdivision, subdivision)
        self.assertEqual(eep_program_sub_status.eep_program, eep_program)
        self.assertEqual(eep_program_sub_status.company, company)


class FloorplanApprovalTests(SubdivisionManagerTestsMixin, AxisTestCase):
    def test_creation(self):
        from axis.floorplan.tests.factories import floorplan_factory

        subdivision = Subdivision.objects.first()
        floorplan = floorplan_factory()

        floorplan_approval, created = FloorplanApproval.objects.get_or_create(
            subdivision=subdivision, floorplan=floorplan
        )

        self.assertEqual(floorplan_approval.subdivision, subdivision)
        self.assertEqual(floorplan_approval.floorplan, floorplan)
