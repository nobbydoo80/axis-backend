"""test_floorplan_filters.py: """


__author__ = "Rajesh Pethe"
__date__ = "02/10/2023 12:18:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


from axis.core.tests.testcases import ApiV3Tests
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.core.tests.factories import rater_admin_factory
from simulation.tests.factories import simulation_factory
from axis.floorplan.models import Floorplan
from axis.floorplan.api_v3.filters import FloorplanFilter
from simulation.enumerations import FuelType, WaterHeaterStyle, SourceType, CrawlspaceType, Location
from simulation.models import FrameFloor, FoundationWall


class TestFloorplanFilters(ApiV3Tests):
    def setUp(self):
        self.rater_admin = rater_admin_factory()

    def test_filter_heater_fuel_type(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            heater_count=1,
            heater__fuel=FuelType.NATURAL_GAS,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"heater_fuel_type": FuelType.NATURAL_GAS}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"heater_fuel_type": FuelType.ELECTRIC}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_water_heater_fuel_type(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            water_heater_count=1,
            water_heater__fuel=FuelType.ELECTRIC,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"water_heater_fuel_type": FuelType.NATURAL_GAS}, qs)
        self.assertEqual(filterset.qs.count(), 0)

        filterset = FloorplanFilter({"water_heater_fuel_type": FuelType.ELECTRIC}, qs)
        self.assertEqual(filterset.qs.count(), 1)

    def test_filter_water_heater_style(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            water_heater_count=1,
            water_heater__style=WaterHeaterStyle.TANKLESS,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"water_heater_style": WaterHeaterStyle.CONVENTIONAL}, qs)
        self.assertEqual(filterset.qs.count(), 0)

        filterset = FloorplanFilter({"water_heater_style": WaterHeaterStyle.TANKLESS}, qs)
        self.assertEqual(filterset.qs.count(), 1)

    def test_filter_air_conditioner(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            air_conditioner_count=0,
            skip_systems=True,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"air_conditioner": False}, qs)
        self.assertEqual(filterset.qs.count(), 0)

        filterset = FloorplanFilter({"air_conditioner": True}, qs)
        self.assertEqual(filterset.qs.count(), 1)

    def test_filter_ashp(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            air_source_heat_pump_count=1,
            heater_count=0,
            air_conditioner_count=0,
            water_heater_count=0,
            ground_source_heat_pump_count=0,
            mechanical_ventilation_count=0,
            photovoltaic_count=0,
            dehumidifier_count=0,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"ashp": False}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"ashp": True}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_gshp(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            ground_source_heat_pump_count=1,
            heater_count=0,
            air_conditioner_count=0,
            water_heater_count=0,
            air_source_heat_pump_count=0,
            mechanical_ventilation_count=0,
            photovoltaic_count=0,
            dehumidifier_count=0,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"gshp": False}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"gshp": True}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_dehumidifier(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            ground_source_heat_pump_count=0,
            heater_count=0,
            air_conditioner_count=0,
            water_heater_count=0,
            air_source_heat_pump_count=0,
            mechanical_ventilation_count=0,
            photovoltaic_count=0,
            dehumidifier_count=1,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"dehumidifier": False}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"dehumidifier": True}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_simulation_source(self):
        simulation = simulation_factory(
            company=self.rater_admin.company, source_type=SourceType.REMRATE_SQL
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"simulation_source": SourceType.REMRATE_SQL}, qs)
        self.assertEqual(filterset.qs.count(), 1)  # We created SQL simulation

        filterset = FloorplanFilter({"simulation_source": SourceType.REMRATE_BLG}, qs)
        self.assertEqual(filterset.qs.count(), 0)  # Not BLG

    def test_filter_simulation_version(self):
        simulation = simulation_factory(
            company=self.rater_admin.company, source_type=SourceType.REMRATE_SQL
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"simulation_version": simulation.version}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"simulation_version": "3.1.1"}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_crawl_space(self):
        FrameFloor.objects.all().delete()
        FoundationWall.objects.all().delete()

        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            slabs_count=0,
            frame_floor_count=1,
            frame_floor__exterior_location=Location.OPEN_CRAWL_SPACE,
            foundation_wall_count=1,
            foundation_wall__interior_location=Location.OPEN_CRAWL_SPACE,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filter_set_1 = FloorplanFilter({"crawl_space": CrawlspaceType.VENTED}, qs)
        self.assertEqual(filter_set_1.qs.count(), 1)

        filter_set_2 = FloorplanFilter({"crawl_space": CrawlspaceType.UNVENTED}, qs)
        self.assertEqual(filter_set_2.qs.count(), 0)

    def test_filter_has_slabs(self):
        simulation = simulation_factory(
            company=self.rater_admin.company, source_type=SourceType.REMRATE_SQL, slabs_count=1
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"has_slabs": False}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"has_slabs": True}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_num_stories(self):
        simulation = simulation_factory(
            company=self.rater_admin.company, source_type=SourceType.REMRATE_SQL
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"num_stories": simulation.floors_on_or_above_grade}, qs)
        self.assertEqual(filterset.qs.count(), 1)

    def test_filter_has_basement(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            foundation_wall_count=1,
            foundation_wall__interior_location=Location.CONDITIONED_BASEMENT,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"has_basement": True}, qs)
        self.assertEqual(filterset.qs.count(), 1)

    def test_filter_attic_type(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            skip_enclosure=False,
            roof_count=1,
            roof__interior_location=Location.ATTIC_VENTED,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"attic_type": "vented"}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"attic_type": Location.VAULTED_ROOF}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_vaulted_ceilings(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            skip_enclosure=False,
            roof_count=1,
            roof__interior_location=Location.VAULTED_ROOF,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"vaulted_ceilings": True}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"vaulted_ceilings": False}, qs)
        self.assertEqual(filterset.qs.count(), 0)

    def test_filter_has_photovoltaics(self):
        simulation = simulation_factory(
            company=self.rater_admin.company,
            source_type=SourceType.REMRATE_SQL,
            photovoltaic_count=1,
        )

        floorplan_with_simulation_factory(owner=simulation.company, simulation=simulation)

        qs = Floorplan.objects.all()
        filterset = FloorplanFilter({"has_photovoltaics": False}, qs)
        self.assertEqual(filterset.qs.count(), 1)

        filterset = FloorplanFilter({"has_photovoltaics": True}, qs)
        self.assertEqual(filterset.qs.count(), 0)
