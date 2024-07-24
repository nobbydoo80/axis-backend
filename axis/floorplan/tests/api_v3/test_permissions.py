"""test_permissions.py - Axis"""

__author__ = "Steven K"
__date__ = "3/9/22 13:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import RequestFactory, TestCase
from axis.core.models import User
from axis.core.tests.factories import eep_admin_factory, rater_admin_factory
from axis.floorplan.api_v3.permissions import (
    SimulationCreatePermission,
    SimulationUpdatePermission,
    SimulationDeletePermission,
)
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from simulation.tests.factories import simulation_factory

log = logging.getLogger(__name__)


class SimulationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rater_admin = rater_admin_factory()
        cls.simulation = simulation_factory(company=cls.rater_admin.company)

    def test_simulation_create_non_company(self):
        """Verify that if you don't have a company you can't see it"""
        admin_user = User.objects.create(username="foo", is_staff=True)
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = admin_user

        permission_check = SimulationCreatePermission()

        permission = permission_check.has_permission(request, None)

        self.assertFalse(permission)

    def test_simulation_create_non_rater_company(self):
        """Verify that if you aren't a rater / provider you can't create"""
        admin_user = eep_admin_factory()
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = admin_user

        permission_check = SimulationCreatePermission()

        permission = permission_check.has_permission(request, None)

        self.assertFalse(permission)

    def test_simulation_create_rater_company(self):
        """Verify that if you are a rater / provider you can create"""
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = self.rater_admin

        permission_check = SimulationCreatePermission()

        permission = permission_check.has_permission(request, None)

        self.assertTrue(permission)

    def test_update_for_staff_and_supers(self):
        """Verify that if you are the staff or super you can update"""
        admin_user = eep_admin_factory(is_superuser=True)
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = admin_user

        permission_check = SimulationUpdatePermission()

        permission = permission_check.has_object_permission(request, None, self.simulation)

        self.assertTrue(permission)

    def test_update_owner(self):
        """Verify that if you are the owner you can update"""
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = self.rater_admin

        permission_check = SimulationUpdatePermission()

        permission = permission_check.has_object_permission(request, None, self.simulation)

        self.assertTrue(permission)

    def test_delete_for_staff_and_supers(self):
        """Verify that if you are the staff or super you can delete"""
        admin_user = eep_admin_factory(is_superuser=True)
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = admin_user

        permission_check = SimulationDeletePermission()

        permission = permission_check.has_object_permission(request, None, self.simulation)

        self.assertTrue(permission)

    def test_delete_owner(self):
        """Verify that if you are the owner you can delete"""
        factory = RequestFactory()

        request = factory.delete("/")
        request.user = self.rater_admin

        permission_check = SimulationDeletePermission()

        permission = permission_check.has_object_permission(request, None, self.simulation)

        self.assertTrue(permission)

    def test_usage_owner(self):
        """If we have a floorplan"""
        factory = RequestFactory()
        floorplan_with_simulation_factory(owner=self.simulation.company, simulation=self.simulation)

        request = factory.delete("/")
        request.user = self.rater_admin

        permission_check = SimulationDeletePermission()

        permission = permission_check.has_object_permission(request, None, self.simulation)

        self.assertTrue(permission)
