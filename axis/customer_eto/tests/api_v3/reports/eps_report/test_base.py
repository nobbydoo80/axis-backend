"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.api_v3.serializers import EPS2021CalculatorSerializer
from axis.customer_eto.api_v3.serializers.reports.eps_report.base import (
    EPSReportBaseSerializer,
)
from axis.customer_eto.tests.program_checks.test_eto_2021 import (
    ETO2021ProgramCompleteTestMixin,
)

log = logging.getLogger(__name__)


class EPSReportBaseSerializerTests(ETO2021ProgramCompleteTestMixin, AxisTestCase):
    """Test EPS Report lowlevel stuff"""

    @classmethod
    def setUpTestData(cls):
        super(EPSReportBaseSerializerTests, cls).setUpTestData()
        serializer = EPS2021CalculatorSerializer(
            data={"home_status": cls.home_status.pk},
        )
        if serializer.is_valid(raise_exception=True):
            cls.calculator = serializer.calculator
            cls.project_tracker = serializer.save()

    def test_serializer_data(self):
        data = {
            "home_status": self.home_status.id,
            "user": self.get_admin_user().id,
            "street_line": "STREET_LINE",
            "city": "CITY",
            "state": "CA",
            "zipcode": "ZIPCODE",
            "floorplan_type": "PRELIMINARY",
            "rater": "RATER_DATA",
            "rater_ccb": "RATER_CCB_DATA",
            "estimated_monthly_energy_costs": "123.45",
            "estimated_average_annual_energy_cost": "234.56",
            "year": "1999",
            "square_footage": "2999",
            "eps_issue_date": "1999-12-24",
            "electric_utility": "ELECTRIC_UTILITY",
            "gas_utility": "GAS_UTILITY",
            "electric_per_month": "99.99",
            "natural_gas_per_month": "88.88",
            "kwh_cost": "77.771",
            "therm_cost": "66.778",
            "solar": "year",
            "energy_score": "11",
            "net_electric_kwhs": "55.55",
            "electric_kwhs": "44.44",
            "natural_gas_therms": "33.33",
            "total_electric_kwhs": "22.22",
            "total_natural_gas_therms": "11.11",
            "electric_tons_per_year": "67.67",
            "natural_gas_tons_per_year": "57.57",
            "insulated_ceiling": "insulated_ceiling",
            "insulated_walls": "insulated_walls",
            "insulated_floors": "insulated_floors",
            "efficient_windows": "efficient_windows",
            "efficient_lighting": "efficient_lighting",
            "water_heater": "water_heater",
            "space_heating": "space_heating",
            "envelope_tightness": "envelope_tightness",
            "energy_consumption_score": round(38.38, 0),
            "energy_consumption_similar_home": "48.0",
            "energy_consumption_to_code": "58.58",
            "carbon_footprint_score": "68.68",
            "carbon_footprint_similar_home": "78.78",
            "carbon_footprint_to_code": "89.89",
        }

        serializer = EPSReportBaseSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        data = serializer.data

        self.assertEqual(data["home_status"], self.home_status.id)
        self.assertEqual(data["street_line"], "STREET_LINE")
        self.assertEqual(data["city"], "CITY")
        self.assertEqual(data["state"], "CA")
        self.assertEqual(data["zipcode"], "ZIPCODE")
        self.assertEqual(data["floorplan_type"], "PRELIMINARY")
        self.assertEqual(data["rater"], "RATER_DATA")
        self.assertEqual(data["rater_ccb"], "RATER_CCB_DATA")
        self.assertEqual(data["estimated_monthly_energy_costs"], "123")
        self.assertEqual(data["estimated_average_annual_energy_cost"], "235")
        self.assertEqual(data["year"], 1999)
        self.assertEqual(data["square_footage"], "2,999")
        self.assertEqual(data["eps_issue_date"], str(datetime.date(1999, 12, 24)))
        self.assertEqual(data["electric_utility"], "ELECTRIC_UTILITY")
        self.assertEqual(data["gas_utility"], "GAS_UTILITY")
        self.assertEqual(data["electric_per_month"], "100")
        self.assertEqual(data["natural_gas_per_month"], "89")
        self.assertEqual(data["kwh_cost"], "$77.77")
        self.assertEqual(data["therm_cost"], "$66.78")
        self.assertEqual(data["solar"], "year")
        self.assertEqual(data["energy_score"], 11)
        self.assertEqual(data["net_electric_kwhs"], "56")
        self.assertEqual(data["electric_kwhs"], "44")
        self.assertEqual(data["natural_gas_therms"], "33")
        self.assertEqual(data["total_electric_kwhs"], "22")
        self.assertEqual(data["total_natural_gas_therms"], "11")
        self.assertEqual(data["electric_tons_per_year"], 67.7)
        self.assertEqual(data["natural_gas_tons_per_year"], 57.6)
        self.assertEqual(data["insulated_ceiling"], "insulated_ceiling")
        self.assertEqual(data["insulated_walls"], "insulated_walls")
        self.assertEqual(data["insulated_floors"], "insulated_floors")
        self.assertEqual(data["efficient_windows"], "efficient_windows")
        self.assertEqual(data["efficient_lighting"], "efficient_lighting")
        self.assertEqual(data["water_heater"], "water_heater")
        self.assertEqual(data["space_heating"], "space_heating")
        self.assertEqual(data["envelope_tightness"], "envelope_tightness")
        self.assertEqual(data["energy_consumption_score"], 38)
        self.assertEqual(data["energy_consumption_similar_home"], 48)
        self.assertEqual(data["energy_consumption_to_code"], 59)
        self.assertEqual(data["carbon_footprint_score"], 68.7)
        self.assertEqual(data["carbon_footprint_similar_home"], 78.8)
        self.assertEqual(data["carbon_footprint_to_code"], 89.9)
        self.assertEqual(data["state_long"], "California")
        self.assertEqual(data["cond_state"], "CA")
        self.assertEqual(data["cond_state_long"], "California")
