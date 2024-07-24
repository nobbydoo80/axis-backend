"""test_tasks.py - Axis"""
import datetime
import logging

from django_celery_beat.utils import now

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.floorplan.models import Floorplan
from axis.remrate_data.models import Building, Simulation
from axis.remrate_data.tasks import prune_failed_simulation_models
from axis.remrate_data.tests.factories import simulation_factory
from ...eep_program.tests.factories import basic_eep_program_factory
from ...floorplan.tests.factories import floorplan_factory
from ...home.models import EEPProgramHomeStatus
from ...home.tests.factories import custom_home_factory

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/3/21 14:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class RemRateDataTaskTests(AxisTestCase):
    """Test out our tasks"""

    client_class = AxisClient

    def setUp(self):
        Building.objects.update(last_update=now())
        self.time_window = now() - datetime.timedelta(days=8)
        self.too_soon_time_window = now() - datetime.timedelta(days=6)

    @classmethod
    def setUpTestData(cls):
        base_sim = simulation_factory(export_type=1, version=15.8, rating_number="standard")

        design = simulation_factory(
            company=base_sim.company,
            remrate_user=base_sim.remrate_user,
            building__sync_status=1,
            export_type=4,
            version=15.8,
            rating_number="ref_design",
        )
        similar_kw = dict(
            company=base_sim.company,
            remrate_user=base_sim.remrate_user,
            rating_number=design.rating_number,
            version=design.version,
            simulation_date=design.simulation_date,
            building__sync_status=design.building.sync_status,
            building__created_on=design.building.created_on,
            building_info__volume=design.building.building_info.volume,
            building_info__conditioned_area=design.building.building_info.conditioned_area,
            building_info__type=design.building.building_info.type,
            building_info__house_level_type=design.building.building_info.house_level_type,
            building_info__number_stories=design.building.building_info.number_stories,
            building_info__foundation_type=design.building.building_info.foundation_type,
            building_info__number_bedrooms=design.building.building_info.number_bedrooms,
            building_info__num_units=design.building.building_info.num_units,
            building_info__year_built=design.building.building_info.year_built,
            building_info__thermal_boundary=design.building.building_info.thermal_boundary,
        )
        simulation_factory(export_type=5, **similar_kw)

        multiple_design = simulation_factory(
            company=base_sim.company,
            remrate_user=base_sim.remrate_user,
            building__sync_status=1,
            export_type=5,
            version=15.6,
            rating_number="multiple_ref_design",
        )
        similar_kw = dict(
            company=base_sim.company,
            remrate_user=base_sim.remrate_user,
            rating_number=multiple_design.rating_number,
            version=multiple_design.version,
            building__sync_status=multiple_design.building.sync_status,
            building__created_on=multiple_design.building.created_on,
            building_info__volume=multiple_design.building.building_info.volume,
            building_info__conditioned_area=multiple_design.building.building_info.conditioned_area,
            building_info__type=multiple_design.building.building_info.type,
            building_info__house_level_type=multiple_design.building.building_info.house_level_type,
            building_info__number_stories=multiple_design.building.building_info.number_stories,
            building_info__foundation_type=multiple_design.building.building_info.foundation_type,
            building_info__number_bedrooms=multiple_design.building.building_info.number_bedrooms,
            building_info__num_units=multiple_design.building.building_info.num_units,
            building_info__year_built=multiple_design.building.building_info.year_built,
            building_info__thermal_boundary=multiple_design.building.building_info.thermal_boundary,
        )
        simulation_factory(
            export_type=4,
            simulation_date=multiple_design.simulation_date + datetime.timedelta(seconds=5),
            **similar_kw,
        )
        simulation_factory(
            export_type=5,
            simulation_date=multiple_design.simulation_date + datetime.timedelta(seconds=15),
            **similar_kw,
        )

        for sim in Simulation.objects.all():
            sim.assign_references_and_similar()

        eep = basic_eep_program_factory(owner=base_sim.company)
        floorplan = floorplan_factory(owner=base_sim.company)
        home = custom_home_factory(city=base_sim.company.city)
        EEPProgramHomeStatus.objects.get_or_create(
            company=base_sim.company, home=home, floorplan=floorplan, eep_program=eep
        )

    def test_basic_time_window_filtering(self):
        """Nothing should happen here."""
        Building.objects.update(last_update=self.too_soon_time_window)
        self.assertEqual(Simulation.objects.count(), 6)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 6)

        # None of these are attached to the home.
        # And we should validate that none of these have errors
        Building.objects.update(last_update=self.time_window)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 6)

    def test_time_window_missing_building(self):
        """If we don't have a building remove me"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        Simulation.objects.get(export_type=1).building.delete()
        self.assertEqual(Simulation.objects.count(), 6)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 5)
        self.assertEqual(Simulation.objects.filter(export_type=1).count(), 0)

    def test_time_window_missing_building_with_homestatus(self):
        """If we don't have a building but we are on a home keep it"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        Simulation.objects.get(export_type=1).building.delete()
        self.assertEqual(Simulation.objects.count(), 6)

        Floorplan.objects.update(remrate_target=Simulation.objects.get(export_type=1))
        floorplan = Floorplan.objects.get()
        self.assertIsNotNone(floorplan.remrate_target)
        self.assertEqual(floorplan.active_for_homestatuses.count(), 1)

        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 6)

        # Now check that if we add this as a floorplans we can't nuke it.
        EEPProgramHomeStatus.objects.update(floorplan=None)
        EEPProgramHomeStatus.objects.get().floorplans.add(floorplan)
        self.assertEqual(floorplan.homestatuses.count(), 1)
        prune_failed_simulation_models()

        self.assertEqual(Simulation.objects.count(), 6)

    def test_time_window_missing_reference(self):
        """If we don't have a reference remove me"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        sim = Simulation.objects.get(export_type=4, rating_number="ref_design")
        sim.references.filter(export_type=5).delete()
        self.assertEqual(Simulation.objects.count(), 5)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 4)
        self.assertEqual(Simulation.objects.filter(rating_number="ref_design").count(), 0)

    def test_time_window_missing_reference_with_homestatus(self):
        """If we don't have a reference but have it bound don't remove id"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        sim = Simulation.objects.get(export_type=4, rating_number="ref_design")
        sim.references.filter(export_type=5).delete()
        self.assertEqual(Simulation.objects.count(), 5)

        Floorplan.objects.update(
            remrate_target=Simulation.objects.get(export_type=4, rating_number="ref_design")
        )
        floorplan = Floorplan.objects.get()
        self.assertIsNotNone(floorplan.remrate_target)
        self.assertEqual(floorplan.active_for_homestatuses.count(), 1)

        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 5)

        EEPProgramHomeStatus.objects.update(floorplan=None)
        EEPProgramHomeStatus.objects.get().floorplans.add(floorplan)
        self.assertEqual(floorplan.homestatuses.count(), 1)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 5)

        self.assertEqual(Simulation.objects.filter(rating_number="ref_design").count(), 1)

    def test_time_window_missing_design(self):
        """If we don't have a design remove it if we have nothing bound to it"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        sim = Simulation.objects.get(export_type=5, rating_number="ref_design")
        sim.base_building.filter(export_type=4).delete()
        self.assertEqual(Simulation.objects.count(), 5)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 4)
        self.assertEqual(Simulation.objects.filter(rating_number="ref_design").count(), 0)

    def test_time_window_missing_design_with_homestatus(self):
        """If we don't have a design but have a homestatus keep it"""
        Building.objects.update(last_update=self.time_window)  # In time frame
        sim = Simulation.objects.get(export_type=5, rating_number="ref_design")
        sim.base_building.filter(export_type=4).delete()

        self.assertEqual(Simulation.objects.count(), 5)

        Floorplan.objects.update(
            remrate_target=Simulation.objects.get(export_type=5, rating_number="ref_design")
        )
        floorplan = Floorplan.objects.get()
        self.assertIsNotNone(floorplan.remrate_target)
        self.assertEqual(floorplan.active_for_homestatuses.count(), 1)

        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 5)

        EEPProgramHomeStatus.objects.update(floorplan=None)
        EEPProgramHomeStatus.objects.get().floorplans.add(floorplan)
        self.assertEqual(floorplan.homestatuses.count(), 1)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 5)

        self.assertEqual(Simulation.objects.filter(rating_number="ref_design").count(), 1)

    def test_time_window_multiple_references_with_home_status(self):
        """If we have multiple references / designs and they are bound to a home status keep em"""

        Building.objects.update(last_update=self.time_window)  # In time frame
        sim = Simulation.objects.get(export_type=4, rating_number="multiple_ref_design")

        self.assertEqual(sim.references.count(), 2)

        Floorplan.objects.update(remrate_target=sim)
        floorplan = Floorplan.objects.get()
        self.assertIsNotNone(floorplan.remrate_target)
        self.assertEqual(floorplan.active_for_homestatuses.count(), 1)

        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 6)

        # Add it to the floorplans
        EEPProgramHomeStatus.objects.update(floorplan=None)
        EEPProgramHomeStatus.objects.get().floorplans.add(floorplan)
        self.assertEqual(floorplan.homestatuses.count(), 1)
        prune_failed_simulation_models()
        self.assertEqual(Simulation.objects.count(), 6)

        self.assertEqual(Simulation.objects.filter(rating_number="multiple_ref_design").count(), 3)
