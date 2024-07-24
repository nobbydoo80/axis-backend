"""test_models.py: Django remrate_data"""

import datetime
import logging

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase

from axis.remrate_data.managers import SIMILAR_HOME_ALIGNMENT_DAYS, REFERENCE_HOME_ALIGNMENT_SECS
from axis.remrate_data.models import Simulation
from .factories import simulation_factory


__author__ = "Steven Klass"
__date__ = "7/2/18 7:49 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RemRateDataModelTests(AxisTestCase):
    """Test out the remrate user creation and deletion"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        simulation_factory(version="15.0", rating_number="Not Similar")
        created_on = datetime.datetime.now(datetime.timezone.utc)
        similar = simulation_factory(
            version="15.0",
            rating_number="Similar",
            building__created_on=created_on,
        )

        similar_kw = dict(
            company=similar.company,
            remrate_user=similar.remrate_user,
            rating_number=similar.rating_number,
            building__created_on=created_on + datetime.timedelta(hours=24 * 7),
            building_info__volume=similar.building.building_info.volume,
            building_info__conditioned_area=similar.building.building_info.conditioned_area,
            building_info__type=similar.building.building_info.type,
            building_info__house_level_type=similar.building.building_info.house_level_type,
            building_info__number_stories=similar.building.building_info.number_stories,
            building_info__foundation_type=similar.building.building_info.foundation_type,
            building_info__number_bedrooms=similar.building.building_info.number_bedrooms,
            building_info__num_units=similar.building.building_info.num_units,
            building_info__year_built=similar.building.building_info.year_built,
            building_info__thermal_boundary=similar.building.building_info.thermal_boundary,
        )
        similar_1 = simulation_factory(**similar_kw)

        assert similar.id != similar_1.id, "Same ID?"
        assert similar.company.id == similar_1.company.id, "Not same company"
        assert similar.remrate_user.id == similar_1.remrate_user.id, "Not same remrate_user"
        assert similar.rating_number == similar_1.rating_number, "Not same rating_number"
        assert (
            similar.building.building_info.volume == similar_1.building.building_info.volume
        ), "Not same Vol"
        assert (
            similar.building.building_info.conditioned_area
            == similar_1.building.building_info.conditioned_area
        ), "Not same Area"
        assert (
            similar.building.building_info.type == similar_1.building.building_info.type
        ), "Not same type"
        assert (
            similar.building.building_info.house_level_type
            == similar_1.building.building_info.house_level_type
        ), "Not same house_level_type"
        assert (
            similar.building.building_info.number_stories
            == similar_1.building.building_info.number_stories
        ), "Not same number_stories"
        assert (
            similar.building.building_info.foundation_type
            == similar_1.building.building_info.foundation_type
        ), "Not same foundation_type"
        assert (
            similar.building.building_info.number_bedrooms
            == similar_1.building.building_info.number_bedrooms
        ), "Not same number_bedrooms"
        assert (
            similar.building.building_info.num_units == similar_1.building.building_info.num_units
        ), "Not same num_units"
        assert (
            similar.building.building_info.year_built == similar_1.building.building_info.year_built
        ), "Not same year_built"
        assert (
            similar.building.building_info.thermal_boundary
            == similar_1.building.building_info.thermal_boundary
        ), "Not same thermal_boundary"

        dis_similar_kw = similar_kw.copy()
        dis_similar_kw["building__created_on"] = created_on + datetime.timedelta(
            hours=24 * SIMILAR_HOME_ALIGNMENT_DAYS, minutes=1
        )
        dis_similar_1 = simulation_factory(**dis_similar_kw)
        assert (
            dis_similar_1.building.created_on != similar_1.building.created_on
        ), "Same Created Time"

        # Reference

        reference_kw = similar_kw.copy()
        reference_kw.pop("building__created_on")

        reference_kw["version"] = "15.0"
        reference_kw["rating_number"] = "Reference"
        reference_kw["simulation_date"] = created_on - datetime.timedelta(days=100)

        reference = simulation_factory(
            building__created_on=created_on, export_type=4, **reference_kw
        )
        assert reference.export_type == 4, "Export Type?"
        assert reference.rating_number == reference_kw["rating_number"], "Not same rating_number"

        reference_1 = simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(seconds=REFERENCE_HOME_ALIGNMENT_SECS),
            export_type=5,
            **reference_kw,
        )
        assert reference_1.export_type == 5, "Export Type?"

        assert reference.id != reference_1.id, "Same ID?"
        assert reference.company.id == reference_1.company.id, "Not same company"
        assert reference.remrate_user.id == reference_1.remrate_user.id, "Not same remrate_user"
        assert reference.rating_number == reference_1.rating_number, "Not same rating_number"
        assert (
            reference.building.building_info.volume == reference_1.building.building_info.volume
        ), "Not same Vol"
        assert (
            reference.building.building_info.conditioned_area
            == reference_1.building.building_info.conditioned_area
        ), "Not same Area"
        assert (
            reference.building.building_info.type == reference_1.building.building_info.type
        ), "Not same type"
        assert (
            reference.building.building_info.house_level_type
            == reference_1.building.building_info.house_level_type
        ), "Not same house_level_type"
        assert (
            reference.building.building_info.number_stories
            == reference_1.building.building_info.number_stories
        ), "Not same number_stories"
        assert (
            reference.building.building_info.foundation_type
            == reference_1.building.building_info.foundation_type
        ), "Not same foundation_type"
        assert (
            reference.building.building_info.number_bedrooms
            == reference_1.building.building_info.number_bedrooms
        ), "Not same number_bedrooms"
        assert (
            reference.building.building_info.num_units
            == reference_1.building.building_info.num_units
        ), "Not same num_units"
        assert (
            reference.building.building_info.year_built
            == reference_1.building.building_info.year_built
        ), "Not same year_built"
        assert (
            reference.building.building_info.thermal_boundary
            == reference_1.building.building_info.thermal_boundary
        ), "Not same thermal_boundary"

        dis_reference = simulation_factory(
            building__created_on=created_on, export_type=6, **reference_kw
        )
        dis_reference = simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(seconds=REFERENCE_HOME_ALIGNMENT_SECS + 1),
            export_type=5,
            **reference_kw,
        )

        # Reference 15.7
        reference_kw["version"] = "15.7"
        reference_kw["simulation_date"] = created_on

        reference_kw["building__created_on"] = created_on + datetime.timedelta(days=12)
        reference = simulation_factory(export_type=4, **reference_kw)

        reference_kw["building__created_on"] = created_on - datetime.timedelta(days=12)
        reference = simulation_factory(export_type=5, **reference_kw)

        reference_kw["simulation_date"] = created_on
        reference_kw["simulation_date"] = created_on + datetime.timedelta(seconds=1)
        dis_reference = simulation_factory(export_type=6, **reference_kw)

        # Assign Refs and Similar

        assign_kw = similar_kw.copy()
        assign_kw.pop("building__created_on")

        assign_kw["version"] = "15.4"
        assign_kw["rating_number"] = "Assignment"
        assign_kw["simulation_date"] = created_on

        simulation_factory(building__created_on=created_on, export_type=1, **assign_kw)
        simulation_factory(
            building__created_on=created_on + datetime.timedelta(seconds=1),
            export_type=4,
            **assign_kw,
        )
        simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(seconds=REFERENCE_HOME_ALIGNMENT_SECS),
            export_type=5,
            **assign_kw,
        )

        assign_kw["rating_number"] = "Assignment_X"
        simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(hours=24 * SIMILAR_HOME_ALIGNMENT_DAYS),
            export_type=1,
            **assign_kw,
        )

        assign_kw["rating_number"] = "Assignment_REF"
        simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(seconds=REFERENCE_HOME_ALIGNMENT_SECS),
            export_type=4,
            **assign_kw,
        )
        simulation_factory(
            building__created_on=created_on
            + datetime.timedelta(seconds=REFERENCE_HOME_ALIGNMENT_SECS),
            export_type=5,
            **assign_kw,
        )

        # for s in Simulation.objects.all():
        #     print(s.id, s.export_type,  s.rating_number, s.building.created_on)

        assert Simulation.objects.count() == 17, "Simulation Counts %d" % Simulation.objects.count()

    def test_similar(self):
        """This tests the filter similar"""
        base = Simulation.objects.filter(rating_number="Similar").first()
        similar = Simulation.objects.filter_similar(base)
        self.assertEqual(similar.count(), 1)
        self.assertEqual(Simulation.objects.filter_similar(base, include_self=True).count(), 2)

    def test_similar_exclude_dates(self):
        """This tests the filter to grab the last related simulation"""
        base = Simulation.objects.filter(rating_number="Similar").first()
        similar = Simulation.objects.filter_similar(base)
        self.assertEqual(similar.count(), 1)
        similar = Simulation.objects.filter_similar(base, use_date_range=False)
        self.assertEqual(similar.count(), 2)

    def test_similar_end_date_filter(self):
        """This tests the end_date_filter to grab the last related simulation"""
        base = Simulation.objects.filter(rating_number="Similar").first()
        similar = Simulation.objects.filter_similar(base)
        self.assertEqual(similar.count(), 1)
        similar = Simulation.objects.filter_similar(
            base, end_date_filter=dict(hours=24 * 7, minutes=1)
        )
        self.assertEqual(similar.count(), 2)

    def test_similar_start_date_filter(self):
        """This tests the start_date_filter to grab the second related simulation"""
        base = Simulation.objects.filter(rating_number="Similar").last()
        similar = Simulation.objects.filter_similar(base)
        self.assertEqual(similar.count(), 1)
        similar = Simulation.objects.filter_similar(
            base, start_date_filter=dict(hours=24 * 7, minutes=1)
        )
        self.assertEqual(similar.count(), 2)

    def test_reference_on_related_filter(self):
        """This tests the filter to grab the second related simulation"""
        base = Simulation.objects.filter(rating_number="Similar").first()
        refs = Simulation.objects.filter_references(base)
        self.assertEqual(refs.count(), 0)

    def test_reference_filter(self):
        """Test the reference filter will correctly grab it's pair"""
        base = Simulation.objects.filter(rating_number="Reference").exclude(version="15.7").first()
        refs = Simulation.objects.filter_references(base)
        self.assertEqual(refs.count(), 1)

    def test_reference_15p7_filter(self):
        """Test the reference filter will correctly pair now that 15.7 aligns the simulation_date.."""
        base = Simulation.objects.filter(rating_number="Reference", version="15.7").first()
        refs = Simulation.objects.filter_references(base)
        self.assertEqual(refs.count(), 1)

    def test_assign_similar(self):
        """Test the assignment of similar homes"""
        similar = Simulation.objects.filter(rating_number="Similar").first()
        similar.assign_references_and_similar()

        self.assertEqual(Simulation.objects.get(id=similar.id).similar.count(), 1)
        self.assertEqual(Simulation.objects.get(id=similar.id).references.count(), 0)

    def test_assign_references(self):
        """Test the assignment of reference homes"""
        reference = Simulation.objects.filter(rating_number="Reference").first()
        reference.assign_references_and_similar()

        self.assertEqual(Simulation.objects.get(id=reference.id).similar.count(), 0)
        self.assertEqual(Simulation.objects.get(id=reference.id).references.count(), 1)

    def test_assign_similar_two(self):
        """Test the assignment of reference and similar"""
        for assignment in Simulation.objects.filter(rating_number="Assignment"):
            assignment.assign_references_and_similar()

        assignment = Simulation.objects.filter(rating_number="Assignment").first()
        self.assertEqual(Simulation.objects.get(id=assignment.id).similar.count(), 1)
        self.assertEqual(Simulation.objects.get(id=assignment.id).references.count(), 0)

        # Now we should have a two for our ref/des home birectionality should have bound them.
        ref_assignment = Simulation.objects.filter(
            rating_number="Assignment", export_type=4
        ).first()
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).similar.count(), 1)
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).references.count(), 1)

    def test_assign_similar_and_references_followup(self):
        """Test the followup of adding similar and reference home data"""
        for assignment in Simulation.objects.filter(rating_number="Assignment"):
            assignment.assign_references_and_similar()

        assignment = Simulation.objects.filter(rating_number="Assignment").first()
        self.assertEqual(Simulation.objects.get(id=assignment.id).similar.count(), 1)
        self.assertEqual(Simulation.objects.get(id=assignment.id).references.count(), 0)

        assignment_x = Simulation.objects.filter(rating_number="Assignment_X")
        assignment_x.update(rating_number="Assignment")

        assignment.assign_references_and_similar()

        self.assertEqual(Simulation.objects.get(id=assignment.id).similar.count(), 2)
        self.assertEqual(Simulation.objects.get(id=assignment.id).references.count(), 0)

        ref_assignment = Simulation.objects.filter(
            rating_number="Assignment", export_type=4
        ).first()
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).similar.count(), 2)
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).references.count(), 1)

        assignment_x = Simulation.objects.filter(rating_number="Assignment_REF")
        assignment_x.update(rating_number="Assignment")
        for assignment in Simulation.objects.filter(rating_number="Assignment"):
            assignment.assign_references_and_similar()

        assignment = Simulation.objects.filter(rating_number="Assignment").first()
        self.assertEqual(Simulation.objects.get(id=assignment.id).similar.count(), 3)
        self.assertEqual(Simulation.objects.get(id=assignment.id).references.count(), 0)

        ref_assignment = Simulation.objects.filter(
            rating_number="Assignment", export_type=4
        ).first()
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).similar.count(), 3)
        self.assertEqual(Simulation.objects.get(id=ref_assignment.id).references.count(), 2)

        # Ensure the bidirectionality happened.
        for item in Simulation.objects.get(id=assignment.id).similar.all():
            self.assertEqual(item.similar.count(), 3)
