"""similar_homes.py - Axis"""

__author__ = "Steven K"
__date__ = "10/27/20 09:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from unittest import mock

from django.utils.timezone import now

from axis.gbr.tests.mocked_responses import gbr_mocked_response
from simulation.tests.factories import mechanical_equipment_factory

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import get_similar_homes
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import certify_single_home
from axis.home.tests.factories import eep_program_custom_home_status_factory, home_factory
from axis.relationship.utils import create_or_update_spanning_relationships

log = logging.getLogger(__name__)


class TestAnalyticsSimilarHomes(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.fastrack = FastTrackSubmission.objects.get(home_status=self.home_status)
        self.analysis = self.simulation.analyses.first().type

        self.args = (
            self.home_status.id,
            self.simulation.id,
            self.simulation.conditioned_area,
            self.simulation.location.climate_zone_id,
            self.fastrack.percent_improvement,
            self.analysis,
        )

    def test_get_similar_homes(self):
        values = get_similar_homes(*self.args)
        self.assertEqual(
            values["similar_total_simulation_ids"], [self.complete.floorplan.simulation_id]
        )
        self.assertEqual(
            values["similar_insulation_simulation_ids"], [self.complete.floorplan.simulation_id]
        )
        self.assertEqual(
            values["similar_heating_simulation_ids"], [self.complete.floorplan.simulation_id]
        )
        self.assertEqual(
            values["similar_hot_water_simulation_ids"], [self.complete.floorplan.simulation_id]
        )

    def test_get_similar_last_18mo_homes(self):
        """Test our 18 month window"""
        inside_18_mos = now() - datetime.timedelta(days=365 * 1.5) + datetime.timedelta(days=1)

        EEPProgramHomeStatus.objects.filter(id=self.complete.id).update(
            certification_date=inside_18_mos
        )
        values = get_similar_homes(*self.args)

        self.assertEqual(
            values["similar_total_simulation_last_18mo_ids"],
            [self.complete.floorplan.simulation_id],
        )
        self.assertEqual(
            values["similar_insulation_simulation_last_18mo_ids"],
            [self.complete.floorplan.simulation_id],
        )
        self.assertEqual(
            values["similar_heating_simulation_last_18mo_ids"],
            [self.complete.floorplan.simulation_id],
        )
        self.assertEqual(
            values["similar_hot_water_simulation_last_18mo_ids"],
            [self.complete.floorplan.simulation_id],
        )

        outside_18_mos = now() - datetime.timedelta(days=365 * 1.5) - datetime.timedelta(days=1)
        EEPProgramHomeStatus.objects.filter(id=self.complete.id).update(
            certification_date=outside_18_mos
        )
        values = get_similar_homes(*self.args)
        self.assertEqual(values["similar_total_simulation_last_18mo_ids"], [])
        self.assertEqual(values["similar_insulation_simulation_last_18mo_ids"], [])
        self.assertEqual(values["similar_heating_simulation_last_18mo_ids"], [])
        self.assertEqual(values["similar_hot_water_simulation_last_18mo_ids"], [])

    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def test_get_similar_heating_counts(self, _mock):
        """Carrie Bee found a bug where the number of compariative heating homes was giving us
        false data.  Analytic ID 8618 had a a home which had two heating systems one of which was
        throwing off the calculations."""
        initial_home_statuses = EEPProgramHomeStatus.objects.filter(state="complete").count()

        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_heating_simulation_last_18mo_ids"]), 1)
        self.assertEqual(
            self.simulation.mechanical_equipment.filter(heating_percent_served__gt=0).count(), 1
        )
        self.assertEqual(
            self.simulation.mechanical_equipment.filter(heater__isnull=False).count(), 1
        )

        # Create a new home status with a fresh simulation
        floorplan = floorplan_with_simulation_factory(name="3", **self.floorplan_factory_kwargs)
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(), city=self.city, zipcode=97229
        )
        home_status_3 = eep_program_custom_home_status_factory(
            home=home, floorplan=floorplan, eep_program=self.eep_program, company=self.rater_company
        )

        rel_ele = create_or_update_spanning_relationships(
            self.electric_utility, home_status_3.home
        )[0][0]
        rel_gas = create_or_update_spanning_relationships(self.gas_utility, home_status_3.home)[0][
            0
        ]
        create_or_update_spanning_relationships(self.qa_company, home_status_3.home)
        create_or_update_spanning_relationships(self.provider_company, home_status_3.home)
        home._generate_utility_type_hints(rel_gas, rel_ele)

        mixin = CollectionRequestMixin()
        mixin.add_bulk_answers(data=self.expected_answers, home_status=home_status_3)
        self.assertEqual(len(home_status_3.report_eligibility_for_certification()), 0)

        certify_single_home(
            self.provider_user,
            home_status_3,
            datetime.date.today() - datetime.timedelta(days=1),
            bypass_check=True,
        )
        # Verify that we now have 2 elements
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(state="complete").count(), initial_home_statuses + 1
        )

        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_heating_simulation_last_18mo_ids"]), 2)

        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(heating_percent_served__gt=0).count(),
            1,
        )
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(heater__isnull=False).count(),
            1,
        )
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(heater__isnull=False).count(),
            self.simulation.mechanical_equipment.filter(heater__isnull=False).count(),
        )

        # Add a another heater similar heater..
        kw = {
            k.replace("simulation__heater__", ""): v
            for k, v in self.floorplan_factory_kwargs.items()
            if k.startswith("simulation__heater__")
        }
        mechanical_equipment_factory(simulation=floorplan.simulation, equipment_type="heater", **kw)
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(heating_percent_served__gt=0).count(),
            2,
        )
        # We should no longer have it.
        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_heating_simulation_last_18mo_ids"]), 1)

    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def test_get_similar_water_heater_counts(self, _mock):
        """Carrie Bee found a bug where the number of compariative heating homes was giving us
        false data.  Analytic ID 8618 had a a home which had two heating systems one of which was
        throwing off the calculations."""
        initial_home_statuses = EEPProgramHomeStatus.objects.filter(state="complete").count()

        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_hot_water_simulation_ids"]), 1)
        self.assertEqual(
            self.simulation.mechanical_equipment.filter(water_heater_percent_served__gt=0).count(),
            1,
        )
        self.assertEqual(
            self.simulation.mechanical_equipment.filter(water_heater__isnull=False).count(), 1
        )

        # Create a new home status with a fresh simulation
        floorplan = floorplan_with_simulation_factory(name="3", **self.floorplan_factory_kwargs)
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(), city=self.city, zipcode=97229
        )
        home_status_3 = eep_program_custom_home_status_factory(
            home=home, floorplan=floorplan, eep_program=self.eep_program, company=self.rater_company
        )

        rel_ele = create_or_update_spanning_relationships(
            self.electric_utility, home_status_3.home
        )[0][0]
        rel_gas = create_or_update_spanning_relationships(self.gas_utility, home_status_3.home)[0][
            0
        ]
        create_or_update_spanning_relationships(self.qa_company, home_status_3.home)
        create_or_update_spanning_relationships(self.provider_company, home_status_3.home)
        home._generate_utility_type_hints(rel_gas, rel_ele)

        mixin = CollectionRequestMixin()
        mixin.add_bulk_answers(data=self.expected_answers, home_status=home_status_3)
        self.assertEqual(len(home_status_3.report_eligibility_for_certification()), 0)

        certify_single_home(
            self.provider_user,
            home_status_3,
            datetime.date.today() - datetime.timedelta(days=1),
            bypass_check=True,
        )
        # Verify that we now have 2 elements
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(state="complete").count(), initial_home_statuses + 1
        )

        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_hot_water_simulation_ids"]), 2)

        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(
                water_heater_percent_served__gt=0
            ).count(),
            1,
        )
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(water_heater__isnull=False).count(),
            1,
        )
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(water_heater__isnull=False).count(),
            self.simulation.mechanical_equipment.filter(water_heater__isnull=False).count(),
        )

        # Add a another water heater
        kw = {
            k.replace("simulation__water_heater__", ""): v
            for k, v in self.floorplan_factory_kwargs.items()
            if k.startswith("simulation__water_heater__")
        }
        mechanical_equipment_factory(
            simulation=floorplan.simulation, equipment_type="water_heater", **kw
        )
        self.assertEqual(
            floorplan.simulation.mechanical_equipment.filter(
                water_heater_percent_served__gt=0
            ).count(),
            2,
        )
        # We should no longer have it.
        values = get_similar_homes(*self.args)
        self.assertEqual(len(values["similar_hot_water_simulation_ids"]), 1)
