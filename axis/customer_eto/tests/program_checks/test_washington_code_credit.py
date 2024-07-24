"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/9/21 08:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.contrib.auth.models import Permission
from django.core import management

from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.models import Company
from axis.company.tests.factories import (
    eep_organization_factory,
    utility_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
)
from axis.core.tests.factories import rater_user_factory
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.eep_programs import WashingtonCodeCreditProgram
from axis.customer_eto.eep_programs.washington_code_credit import (
    BuildingEnvelope,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
    WACCFuelType,
    ThermostatType,
    FireplaceType,
    FramingType,
    VentilationType,
    FurnaceLocation,
    DuctLocation,
    AirLeakageControl,
)
from axis.eep_program.models import EEPProgram
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import (
    custom_home_factory,
    eep_program_custom_home_status_factory,
)
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships
from ...enumerations import YesNo
from ...models import ETOAccount

log = logging.getLogger(__name__)


def washington_code_credit_default_data():
    data = {
        "envelope_option": BuildingEnvelope.OPTION_1p3b.value,
        "air_leakage_option": AirLeakageControl.OPTION_2p1.value,
        "hvac_option": HighEfficiencyHVAC.OPTION_3p1.value,
        "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2.value,
        "dwhr_option": DWHR.OPTION_5p1.value,
        "water_heating_option": EfficientWaterHeating.OPTION_5p4.value,
        "renewable_electric_option": RenewableEnergy.OPTION_6p1c.value,
        "appliance_option": Appliances.NONE.value,
        "conditioned_floor_area": 2000,
        "water_heating_fuel": WACCFuelType.ELECTRIC.value,
        "thermostat_type": ThermostatType.ECOBEE_VOICE.value,
        "fireplace_efficiency": FireplaceType.FP_LT70.value,
        "wall_cavity_r_value": 0,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.ADVANCED.value,
        "window_u_value": 0,
        "window_shgc": 0,
        "floor_cavity_r_value": 0,
        "slab_perimeter_r_value": 0,
        "under_slab_r_value": 0,
        "ceiling_r_value": 0,
        "raised_heel": YesNo.NO.value,
        "total_ua_alternative": 0,
        "air_leakage_ach": 0,
        "ventilation_type": VentilationType.HRV_ERV.value,
        "ventilation_brand": "string",
        "ventilation_model": "",
        "hrv_asre": 0,
        "furnace_brand": "furnace_brand",
        "furnace_model": "furnace_model",
        "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE.value,
        "furnace_afue": 92,
        "duct_leakage": 0,
        "duct_location": DuctLocation.UNCONDITIONED_SPACE.value,
        "dwhr_installed": YesNo.YES.value,
        "water_heater_brand": "string",
        "water_heater_model": "string",
        "gas_water_heater_uef": 0.92,
        "electric_water_heater_uef": 2.5,
    }
    return data.copy()


def washington_code_credit_max_program_data():
    data = {
        "envelope_option": BuildingEnvelope.OPTION_1p6a.value,
        "air_leakage_option": AirLeakageControl.OPTION_2p4.value,
        "hvac_option": HighEfficiencyHVAC.OPTION_3p1.value,
        "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2.value,
        "dwhr_option": DWHR.OPTION_5p1.value,
        "water_heating_option": EfficientWaterHeating.OPTION_5p6.value,
        "renewable_electric_option": RenewableEnergy.OPTION_6p1b.value,
        "appliance_option": Appliances.OPTION_7p1.value,
        "conditioned_floor_area": 2500,
        "water_heating_fuel": WACCFuelType.ELECTRIC.value,
        "thermostat_type": ThermostatType.ECOBEE4.value,
        "fireplace_efficiency": FireplaceType.FP_70_75.value,
        "wall_cavity_r_value": 22,
        "wall_continuous_r_value": 16,
        "framing_type": "Advanced",
        "window_u_value": 0.16,
        "window_shgc": 1.0,
        "floor_cavity_r_value": 49,
        "slab_perimeter_r_value": 21,
        "under_slab_r_value": 21,
        "ceiling_r_value": 61,
        "raised_heel": "Yes",
        "air_leakage_ach": 0.5,
        "ventilation_type": VentilationType.HRV_ERV.value,
        "ventilation_brand": "Brand",
        "ventilation_model": "Model",
        "hrv_asre": 85.0,
        "furnace_brand": "Brand",
        "furnace_model": "Model",
        "furnace_afue": 97,
        "furnace_location": FurnaceLocation.CONDITIONED_SPACE.value,
        "duct_location": DuctLocation.CONDITIONED_SPACE.value,
        "duct_leakage": 4,
        "dwhr_installed": YesNo.YES.value,
        "water_heater_brand": "Brand",
        "water_heater_model": "Model",
        "gas_water_heater_uef": 0.92,
        "electric_water_heater_uef": 2.95,
    }
    return data.copy()


def add_required_washington_code_credit_responses(home_status, data):
    _expected_annotations = WashingtonCodeCreditProgram().annotations.keys()
    expected_annotations = {k.replace("-", "_"): k for k in _expected_annotations}
    expected_annotations = {k.replace("wcc_", ""): v for k, v in expected_annotations.items()}

    _expected_measures = WashingtonCodeCreditProgram().texts["rater"].keys()
    expected_measures = {k.replace("wcc-", ""): k for k in _expected_measures}

    annotationMixin = AnnotationMixin()
    collectionMixin = CollectionRequestMixin()

    checklist_data = {}
    for key, value in data.items():
        if key in expected_annotations:
            annotationMixin.add_annotation(
                content=value,
                type_slug=expected_annotations[key],
                content_object=home_status,
            )
        elif key in expected_measures:
            checklist_data[expected_measures[key]] = value
    collectionMixin.add_bulk_answers(checklist_data, home_status=home_status)


class WashingtonCodeCreditTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Kennewick", "WA")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.pac_pwr = utility_organization_factory(
            slug="pacific-power",
            is_customer=True,
            name="Pacific Power",
            city=cls.city,
            gas_provider=False,
            electricity_provider=True,
        )
        cls.nw_nat = utility_organization_factory(
            slug="nw-natural-gas",
            is_customer=True,
            name="NW Natural Gas",
            city=cls.city,
            gas_provider=True,
            electricity_provider=False,
        )
        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        ETOAccount.objects.create(company=cls.rater_company, account_number="123")
        cls.rater = rater_user_factory(company=cls.rater_company)

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        management.call_command(
            "build_program",
            "-p",
            "washington-code-credit",
            "--warn_only",
            "--no_close_dates",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="washington-code-credit")
        cls.provider_company = Company.objects.filter(company_type="provider").get()
        cls.provider_company.update_permissions()

        companies = [
            cls.eto,
            cls.rater_company,
            cls.provider_company,
            cls.builder_company,
            cls.pac_pwr,
            cls.nw_nat,
        ]
        Relationship.objects.create_mutual_relationships(*companies)

        cls.provider_user = cls.provider_company.users.get()
        cls.provider_user.user_permissions.add(
            Permission.objects.get(codename="view_fasttracksubmission")
        )

        cls.home = custom_home_factory(
            street_line1="5803 W Metaline Ave",
            street_line2="# 606",
            city=cls.city,
            zipcode=99336,
            builder_org=cls.builder_company,
            is_multi_family=False,
        )

        rel_ele = create_or_update_spanning_relationships(cls.pac_pwr, cls.home)[0][0]
        rel_gas = create_or_update_spanning_relationships(cls.nw_nat, cls.home)[0][0]

        cls.home._generate_utility_type_hints(rel_gas, rel_ele)

        cls.home_status = eep_program_custom_home_status_factory(
            home=cls.home,
            skip_floorplan=True,
            eep_program=cls.eep_program,
            company=cls.rater_company,
        )
        create_or_update_spanning_relationships(None, cls.home_status)  # Auto add provider

    @property
    def default_program_data(self):
        return washington_code_credit_default_data()

    @property
    def max_program_data(self):
        return washington_code_credit_max_program_data()

    def add_required_responses(self, data, home_status=None):
        if home_status is None:
            home_status = self.home_status
        return add_required_washington_code_credit_responses(data=data, home_status=home_status)


class WashingtonCodeCreditProgramBase(
    WashingtonCodeCreditTestMixin,
    CollectionRequestMixin,
    AnnotationMixin,
    AxisTestCase,
):
    """Washington Code Credit Base - Don't really add checks to this"""

    def test_setup(self):
        """Make sure that our test data works."""
        from axis.geographic.models import City
        from axis.home.models import EEPProgramHomeStatus
        from axis.company.models import Company

        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(
            Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).count(), 1
        )
        self.assertEqual(Company.objects.filter(company_type=Company.RATER_COMPANY_TYPE).count(), 1)
        self.assertEqual(
            Company.objects.filter(company_type=Company.PROVIDER_COMPANY_TYPE).count(),
            1,
        )

        missing_checks = self.home_status.report_eligibility_for_certification()
        # print(
        #     f"** Warning! Failing {self.eep_program} Certification Requirements:\n  - "
        #     + "\n  - ".join(missing_checks)
        #     + "\n** End Warning\n"
        # )
        #
        # questions = self.home_status.get_unanswered_questions()
        # measures = questions.values_list("measure", flat=True)
        # if len(measures):
        #     print("Missing questions")
        # for measure in measures:
        #     print(" * %s" % measure)
        self.assertEqual(len(missing_checks), 2)
        self.assertIn("required checklist questions remaining", " ".join(missing_checks))
        self.assertIn("program sponsor requires 8 annotations", " ".join(missing_checks))


class WashingtonCodeCreditProgramChecks(WashingtonCodeCreditProgramBase):
    def test_auto_assignment(self):
        """Verify that our home was auto-assigned the provider"""
        provider = Company.objects.get(slug=WashingtonCodeCreditProgram.certifiable_by[0])
        relations = self.home.relationships.values_list("company__slug", flat=True)
        self.assertIn(provider.slug, list(relations))

    def test_passing_requirements(self):
        """Make sure that if you have everything you can get through this"""
        self.add_required_responses(self.default_program_data)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_missing_calculator(self):
        """Test to make sure the calculator incentive check works."""

        data = self.default_program_data
        data["hvac_option"] = HighEfficiencyHVAC.OPTION_3p4.value
        self.add_required_responses(data)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Project does not currently qualify for an incentive", missing_checks[0])

    def test_builder_eto_account(self):
        """Verify that we have to have a builder ETO Account"""
        self.add_required_responses(self.default_program_data)

        self.assertIsNotNone(self.builder_company.eto_account)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)
        ETOAccount.objects.filter(company_id=self.builder_company.id).delete()

        self.home_status.refresh_from_db()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Program requires the builder to have an ETO Account", missing_checks[0])

    def test_rater_eto_account(self):
        """Verify that we have to have a rater ETO Account"""
        self.add_required_responses(self.default_program_data)

        self.assertIsNotNone(self.rater_company.eto_account)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        ETOAccount.objects.filter(company_id=self.rater_company.id).delete()

        self.home_status.refresh_from_db()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Program requires the rater to have an ETO Account", missing_checks[0])

    def test_no_multi_family(self):
        """Program only eligible for single-family"""
        self.add_required_responses(self.default_program_data)

        self.assertIsNotNone(self.rater_company.eto_account)
        missing_checks = self.home_status.report_eligibility_for_certification()

        self.assertEqual(len(missing_checks), 0)
        self.home.is_multi_family = True
        self.home.save()

        self.home_status.refresh_from_db()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Only single family projects are allowed", missing_checks[0])

    def test_washington_only(self):
        """Program only eligible in WA"""
        self.add_required_responses(self.default_program_data)

        self.assertIsNotNone(self.rater_company.eto_account)
        missing_checks = self.home_status.report_eligibility_for_certification()

        self.assertEqual(len(missing_checks), 0)
        from axis.home.models import Home

        Home.objects.all().update(state="ID")

        self.home_status.refresh_from_db()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is only allowed in WA.", missing_checks[0])
