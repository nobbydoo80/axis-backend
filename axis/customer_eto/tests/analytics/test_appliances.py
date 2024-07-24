"""appliances.py - Axis"""

__author__ = "Steven K"
__date__ = "10/28/20 11:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import datetime
from unittest import mock

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import (
    eto_simulation_clothes_dryer_model_characteristics,
    eto_simulation_refrigerator_model_characteristics,
)
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.customer_eto.tests.program_checks.test_eto_2022 import ETO2022ProgramCompleteTestMixin
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.gbr.tests.mocked_responses import gbr_mocked_response
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import certify_single_home
from axis.home.tests.factories import home_factory, eep_program_custom_home_status_factory
from axis.relationship.utils import create_or_update_spanning_relationships

log = logging.getLogger(__name__)


class ETO2022ProgramAnalyticsTestMixin(ETO2022ProgramCompleteTestMixin):
    @classmethod
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def setUpTestData(cls, _mock):
        super(ETO2022ProgramAnalyticsTestMixin, cls).setUpTestData()

        certify_single_home(
            cls.provider_user,
            cls.home_status,
            datetime.date.today() - datetime.timedelta(days=1),
            bypass_check=True,
        )  # Gating QA.

        floorplan = floorplan_with_simulation_factory(name="2", **cls.floorplan_factory_kwargs)
        assert str(floorplan.simulation.location.climate_zone) == "4C"
        assert str(floorplan.simulation.climate_zone) == "4C"
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(), city=cls.city, zipcode=97229
        )
        cls.home_status_2 = eep_program_custom_home_status_factory(
            home=home, floorplan=floorplan, eep_program=cls.eep_program, company=cls.rater_company
        )

        rel_ele = create_or_update_spanning_relationships(
            cls.electric_utility, cls.home_status_2.home
        )[0][0]
        rel_gas = create_or_update_spanning_relationships(cls.gas_utility, cls.home_status_2.home)[
            0
        ][0]
        create_or_update_spanning_relationships(cls.qa_company, cls.home_status_2.home)
        create_or_update_spanning_relationships(cls.provider_company, cls.home_status_2.home)

        home._generate_utility_type_hints(rel_gas, rel_ele)

        assert cls.home_status_2.get_electric_company().id == cls.electric_utility.pk
        assert cls.home_status_2.get_gas_company().id == cls.gas_utility.pk

        collection_request = CollectionRequestMixin()
        collection_request.add_bulk_answers(cls.expected_answers, home_status=cls.home_status_2)
        missing_checks = cls.home_status_2.report_eligibility_for_certification()
        assert len(missing_checks) == 0, "Missing checks %r" % missing_checks


class AnalyticsAppliancesTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation

    def test_eto_simulation_clothes_dryer_model_characteristics(self):
        # Incorrect CEF
        input_data = {
            "input": {
                "brand_name": "Whirlpool",
                "model_number": "WGD6620H**",
                "combined_energy_factor": "3.48",
            }
        }

        result = eto_simulation_clothes_dryer_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_clothes_dryer_characteristics"]["warnings"]), 1)

        # Custom
        input_data = {
            "hints": {
                "is_custom": True,
                "model_number": {"is_custom": True},
                "characteristics": {"is_custom": True},
            },
            "input": {
                "brand_name": "Whirlpool",
                "model_number": "WHD8620HC2",
                "combined_energy_factor": "2.5",
            },
        }
        result = eto_simulation_clothes_dryer_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_clothes_dryer_characteristics"]["warnings"]), 1)

        # Correct
        input_data = {
            "input": {
                "brand_name": "Whirlpool",
                "model_number": "WGD6620H**",
                "combined_energy_factor": "2.5",
            }
        }
        result = eto_simulation_clothes_dryer_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_clothes_dryer_characteristics"]["warnings"]), 0)

    def test_eto_simulation_refrigerator_model_characteristics(self):
        # Incorrect annual energy use
        input_data = {
            "input": {
                "brand_name": "Samsung",
                "model_number": "RF23M8070**",
                "annual_energy_use_kwh_yr": "633",
            }
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 1)

        # Custom
        input_data = {
            "hints": {
                "is_custom": True,
                "model_number": {"is_custom": True},
                "characteristics": {"is_custom": True},
            },
            "input": {
                "brand_name": "Frigidaire",
                "model_number": "fpru19f8rff",
                "annual_energy_use_kwh_yr": "700",
            },
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 1)

        # Correct
        input_data = {
            "input": {
                "brand_name": "Samsung",
                "model_number": "RF23M8070**",
                "annual_energy_use_kwh_yr": "700",
            }
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 0)

    def test_eto_simulation_diswasher_model_characteristics(self):
        input_data = {
            "raw": {
                "brand_name": "Frigidaire",
                "model_number": "LFID2426***A",
                "annual_energy_use_kwh_yr": "256",
            },
            "hints": {"SPECULATIVE": True},
            "input": {
                "brand_name": "Frigidaire",
                "model_number": "LFID2426***A",
                "annual_energy_use_kwh_yr": "256",
            },
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 1)

        # Custom
        input_data = {
            "hints": {
                "is_custom": True,
                "model_number": {"is_custom": True},
                "characteristics": {"is_custom": True},
            },
            "input": {
                "brand_name": "Samsung",
                "model_number": "dw80r7060us",
                "annual_energy_use_kwh_yr": None,
            },
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 1)

        # Correct
        input_data = {
            "raw": {
                "brand_name": "Electrolux",
                "model_number": "EI24CD35***A",
                "annual_energy_use_kwh_yr": "260",
            },
            "hints": {"SPECULATIVE": True},
            "input": {
                "brand_name": "Electrolux",
                "model_number": "EI24CD35***A",
                "annual_energy_use_kwh_yr": "700",
            },
        }
        result = eto_simulation_refrigerator_model_characteristics(self.simulation.id, input_data)
        self.assertEqual(len(result["model_refrigerator_characteristics"]["warnings"]), 0)
