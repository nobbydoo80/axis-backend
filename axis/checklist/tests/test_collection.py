"""test_collection.py - Axis"""
import csv
import enum
import logging

from django.forms import model_to_dict
from django.test import TestCase
from django_input_collection.models import (
    CollectionInstrument,
    SuggestedResponse,
    ResponsePolicy,
    Case,
    CollectionGroup,
    Measure,
    CollectionInstrumentType,
    CollectionRequest,
    ConditionGroup,
    Condition,
)

from axis.checklist.admin import CollectedInput
from axis.checklist.collection.methods.trc_eps import (
    CascadingClothesDryerPickerMethod,
    CascadingClothesWasherPickerMethod,
    CascadingFurnacePickerMethod,
    CascadingDishwasherPickerMethod,
    CascadingHeatPumpPickerMethod,
    CascadingRefrigeratorPickerMethod,
    CascadingBalancedVentilationPickerMethod,
    CascadingExhaustVentilationPickerMethod,
    CascadingWaterHeaterPickerMethod,
)
from axis.checklist.collection.methods.trc_eps.lookups import (
    CLOTHES_DRYER_LOOKUPS,
    CLOTHES_WASHER_LOOKUPS,
    FURNACE_LOOKUPS,
    DISHWASHER_LOOKUPS,
    HEAT_PUMP_LOOKUPS,
    REFRIGERATOR_LOOKUPS,
    VENTILATION_BALANCED_LOOKUPS,
    VENTILATION_EXHAUST_LOOKUPS,
    WATER_HEATER_LOOKUPS,
)
from axis.checklist.tests.mixins import CollectedInputMixin
from axis.checklist.tests.sample_programs import (
    InstrumentConditionCaseProgramDefinition,
    YesNo,
    SimulationResolverProgramDefinition,
    InstrumentANDConditionCaseProgramDefinition,
    InstrumentORConditionCaseProgramDefinition,
    OptAns,
    InstrumentORDeepConditionCaseProgramDefinition,
)
from axis.company.models import Company
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import custom_home_factory, eep_program_custom_home_status_factory

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/17/20 10:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class InstrumentConditionCaseTests(CollectedInputMixin, AxisTestCase):
    """This will flex out the Suggested Reponse Policy for Programs"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import (
            eep_admin_factory,
            rater_admin_factory,
            builder_admin_factory,
        )
        from axis.home.tests.factories import (
            custom_home_factory,
            eep_program_custom_home_status_factory,
        )
        from axis.relationship.models import Relationship
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory
        from axis.remrate_data.tests.factories import simulation_factory

        # users
        base_kwargs = {}

        eep_admin = eep_admin_factory(company__slug="eto", **base_kwargs)
        rater_admin = rater_admin_factory(
            company__slug="rater", company__city=eep_admin.company.city, **base_kwargs
        )
        builder_admin = builder_admin_factory(
            company__slug="builder", company__city=eep_admin.company.city, **base_kwargs
        )
        Relationship.objects.create_mutual_relationships(
            eep_admin.company, rater_admin.company, builder_admin.company
        )

        program = InstrumentConditionCaseProgramDefinition().build()
        home = custom_home_factory(
            city=eep_admin.company.city, builder_org=builder_admin.company, **base_kwargs
        )
        for company in [eep_admin.company, rater_admin.company, builder_admin.company]:
            Relationship.objects.validate_or_create_relations_to_entity(home, company)

        floorplan = basic_custom_home_floorplan_factory(owner=rater_admin.company, **base_kwargs)
        simulation = simulation_factory(
            company=rater_admin.company,
            export_type=1,
            version="16.0",
            air_conditioning_count=0,
            **base_kwargs,
        )
        floorplan.remrate_target = simulation
        floorplan.save()

        home_status = eep_program_custom_home_status_factory(
            home=home, eep_program=program, floorplan=floorplan, company=company
        )

    def setUp(self):
        super(InstrumentConditionCaseTests, self).setUp()
        from axis.home.models import EEPProgramHomeStatus

        self.program = EEPProgram.objects.get(slug="condition-case")
        self.home_status = EEPProgramHomeStatus.objects.get()

    def test_conditional_ANDing_instrument_answering(self):
        """Need to verify that initially wh have two questions.  Then we need to answer one and
        we have an additional question"""
        self.assertTrue(self.home_status.floorplan.remrate_target.export_type)
        self.assertNotEqual(self.home_status.floorplan.remrate_target.version, "13.0")

        collector = self.home_status.get_collector(user_role="rater")

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        # Verify we don't have any answers up till now..
        answered_measures = collector.get_inputs(cooperative_requests=True)
        answered_measures = answered_measures.values_list("instrument__measure", flat=True)
        self.assertEqual(set([]), set(answered_measures))

        # We are going to answer as question where it should flag a conditional.
        self.add_collected_input(self.home_status, "basic", "C1")
        # collector = self.home_status.get_collector(user_role='rater')
        answered_measures = collector.get_inputs(cooperative_requests=True)
        answered_measures = answered_measures.values_list("instrument__measure", flat=True)
        self.assertEqual(set(answered_measures), {"basic"})

        # This is a walkthrough of EEPProgramHomeStatus.get_answer_for_home..
        collector = self.home_status.get_collector(user_role="rater")
        answered_measures = collector.get_inputs(cooperative_requests=True)
        answered_measures = answered_measures.values_list("instrument__measure", flat=True)
        self.assertEqual(set(answered_measures.distinct()), {"basic"})

        # Verify this aligns directly with get_answers_for_home
        answers = self.home_status.get_answers_for_home()
        answers = answers.values_list("instrument__measure", flat=True)
        self.assertEqual(set(answered_measures), set(answers))

        # We have now verified the answered questions match..

        # NOTE:  When you have multiple instruments affecting a single conditional
        # it's an AND operation.  All conditions must be satisfied..

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic-alt"}, set(questions))

        # Verify the answers are there and now our new question shows up..
        self.add_collected_input(self.home_status, "basic-alt", "CA")
        answers = self.home_status.get_answers_for_home()
        answers = answers.values_list("instrument__measure", flat=True)
        self.assertEqual(set(answers), {"basic-alt", "basic"})

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"condition-basic"}, set(questions))

        instrument = self.home_status.get_answers_for_home().last().instrument
        conditionals = collector.get_active_conditional_instruments(instrument)
        conditionals = [x.measure.pk for x in conditionals]
        self.assertEqual({"condition-basic"}, set(conditionals))

    def test_conditional_rem_data(self):
        """Need to verify that when the rem data meets the criteria it adds a question IFF
        condition is met."""
        from axis.remrate_data.models import Simulation
        from axis.home.models import EEPProgramHomeStatus

        self.assertLessEqual(self.home_status.floorplan.remrate_target.number_of_runs, 2)

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        Simulation.objects.update(**{"number_of_runs": 3})
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.remrate_target.number_of_runs, 3)
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt", "condition-rem-basic"}, set(questions))

    def test_conditional_ANDing_rem_data(self):
        """Need to verify that when a number of conditionals apply to REM they are AND'd and
        ask the appropriate question IFF all conditions are met"""
        from axis.remrate_data.models import Simulation
        from axis.home.models import EEPProgramHomeStatus

        self.assertTrue(self.home_status.floorplan.remrate_target.export_type)
        self.assertNotEqual(self.home_status.floorplan.remrate_target.version, "13.0")

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        Simulation.objects.update(**{"export_type": 13})
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.remrate_target.export_type, 13)
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        Simulation.objects.update(**{"export_type": 1, "version": "16.0"})
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.remrate_target.export_type, 1)
        self.assertEqual(self.home_status.floorplan.remrate_target.version, "16.0")
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        Simulation.objects.update(**{"export_type": 13, "version": "13.0"})
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.remrate_target.export_type, 13)
        self.assertEqual(self.home_status.floorplan.remrate_target.version, "13.0")

        # With everything updated it should add our rem question
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt", "condition-rem"}, set(questions))

    def test_conditional_zero_value_rem_data(self):
        """Need to verify that if the value requested is zero it's allowed through"""
        from axis.remrate_data.models import Simulation
        from axis.home.models import EEPProgramHomeStatus

        self.assertTrue(self.home_status.floorplan.remrate_target.export_type)
        self.assertNotEqual(self.home_status.floorplan.remrate_target.version, "13.0")

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        Simulation.objects.update(**{"export_type": 0})
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.remrate_target.export_type, 0)

        # With everything updated it should add our rem question
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt", "condition-zero"}, set(questions))

    def test_condition_one_in_set(self):
        """Verifies that 'one' works for remrate data"""
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))

        from axis.remrate_data.models import Simulation, AirConditioner

        simulation = Simulation.objects.get()
        self.assertEqual(simulation.airconditioner_set.count(), 0)

        AirConditioner.objects.create(
            type=1, simulation=simulation, _result_number=20, _source_air_conditioner_number=2
        )
        self.assertEqual(list(simulation.airconditioner_set.values_list("type", flat=True)), [1])

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt", "condition-ac"}, set(questions))

        simulation.airconditioner_set.update(type=2)
        self.assertEqual(list(simulation.airconditioner_set.values_list("type", flat=True)), [2])

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"basic", "basic-alt"}, set(questions))


class InstrumentEnumConditionTests(CompaniesAndUsersTestMixin, AxisTestCase, CollectedInputMixin):
    include_company_types = ["builder", "rater", "utility", "eep"]
    include_superuser = False
    include_unrelated_companies = False
    include_noperms_user = False

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        cls.build_company_relationships(city=cls.city, eep__company__slug="eto")
        cls.eep_program = InstrumentANDConditionCaseProgramDefinition().build()
        eep = Company.objects.get(company_type="eep")
        builder = Company.objects.get(company_type="builder")
        rater = Company.objects.get(company_type="rater")
        home = custom_home_factory(
            street_line1="256 W Oxford ln",
            zipcode="85233",
            city=eep.city,
            builder_org=builder,
        )
        cls.home_status = eep_program_custom_home_status_factory(
            home=home, eep_program=cls.eep_program, company=rater
        )

    def test_integrated_enums(self):
        """This verifies that our stuff all ended up in there."""
        instruments = CollectionInstrument.objects.filter(
            collection_request=self.eep_program.collection_request
        )
        self.assertEqual(instruments.count(), 3)
        instrument = instruments.get(measure="seed-a")

        self.assertEqual(instrument.get_choices(), [YesNo.YES.value, YesNo.NO.value])

        instrument = instruments.get(measure="seed-b")
        self.assertEqual(instrument.get_choices(), [YesNo.YES.value, YesNo.NO.value])

        instrument = instruments.get(measure="logic-and")
        self.assertEqual(instrument.get_choices(), [YesNo.YES.value, YesNo.NO.value])

        # Verify that we have one response policy forall of these
        self.assertEqual(ResponsePolicy.objects.count(), 1)
        self.assertTrue(instrument.response_policy.restrict)
        self.assertTrue(instrument.response_policy.required)
        self.assertFalse(instrument.response_policy.multiple)

        # Check out our cases
        self.assertEqual(Case.objects.count(), 2)
        case = Case.objects.get(match_type="match")
        self.assertEqual(case.match_data, YesNo.YES.value)
        case = Case.objects.get(match_type="one")
        self.assertEqual(case.match_data, f"({YesNo.YES.value!r},)")

        # Now add an enum answer.
        self.add_collected_input(self.home_status, "seed-b", YesNo.NO)
        result = CollectedInput.objects.get()
        self.assertEqual(result.data["input"], YesNo.NO.value)

    def test_logical_AND(self):
        """This tests the OR'ing response  We have two questions where both need to be 'yes` to
        get to the logical or question"""
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 2)

        self.add_collected_input(self.home_status, "seed-a", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 1)

        self.add_collected_input(self.home_status, "seed-b", YesNo.NO)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 0)

        # Replace b with yes
        self.add_collected_input(self.home_status, "seed-b", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 1)

        self.assertEqual(self.get_unanswered_measures(self.home_status), ["logic-and"])


class InstrumentOrConditionTests(CompaniesAndUsersTestMixin, AxisTestCase, CollectedInputMixin):
    include_company_types = ["builder", "rater", "utility", "eep"]
    include_superuser = False
    include_unrelated_companies = False
    include_noperms_user = False

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        cls.build_company_relationships(city=cls.city, eep__company__slug="eto")
        cls.eep_program = InstrumentORConditionCaseProgramDefinition().build()

        eep = Company.objects.get(company_type="eep")
        builder = Company.objects.get(company_type="builder")
        rater = Company.objects.get(company_type="rater")
        home = custom_home_factory(city=eep.city, builder_org=builder)
        cls.home_status = eep_program_custom_home_status_factory(
            home=home, eep_program=cls.eep_program, company=rater
        )

    def test_logical_OR_A(self):
        self.add_collected_input(self.home_status, "seed-a", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 2)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))

    def test_logical_OR_B(self):
        self.add_collected_input(self.home_status, "seed-b", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 2)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))

    def test_logical_OR(self):
        """This tests the OR'ing response  We have two questions where one need to be 'yes` to
        get to the logical or question"""
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 2)

        # We have two que
        self.add_collected_input(self.home_status, "seed-a", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 2)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "seed-a", YesNo.NO)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 1)
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "seed-b", YesNo.YES)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 1)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "seed-b", YesNo.NO)
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 0)


class InstrumentOrDeepConditionTests(CompaniesAndUsersTestMixin, AxisTestCase, CollectedInputMixin):
    include_company_types = ["builder", "rater", "utility", "eep"]
    include_superuser = False
    include_unrelated_companies = False
    include_noperms_user = False

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")
        cls.build_company_relationships(city=cls.city, eep__company__slug="eto")
        cls.eep_program = InstrumentORDeepConditionCaseProgramDefinition().build()

        eep = Company.objects.get(company_type="eep")
        builder = Company.objects.get(company_type="builder")
        rater = Company.objects.get(company_type="rater")
        home = custom_home_factory(city=eep.city, builder_org=builder)
        cls.home_status = eep_program_custom_home_status_factory(
            home=home, eep_program=cls.eep_program, company=rater
        )

    def test_deep_logical_OR(self):
        """This tests the OR'ing response  We have two questions where one need to be 'yes` to
        get to the logical or question"""
        self.assertEqual(self.home_status.get_unanswered_questions().count(), 1)

        self.add_collected_input(self.home_status, "top", OptAns.A)
        self.assertIn("seed-a", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("seed-b", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "top", OptAns.B)
        self.assertNotIn("seed-a", self.get_unanswered_measures(self.home_status))
        self.assertIn("seed-b", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "top", OptAns.D)
        self.assertNotIn("seed-a", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("seed-b", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "top", OptAns.A)
        self.assertIn("seed-a", self.get_unanswered_measures(self.home_status))
        self.assertNotIn("seed-b", self.get_unanswered_measures(self.home_status))
        self.add_collected_input(self.home_status, "seed-a", YesNo.YES)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))
        self.add_collected_input(self.home_status, "seed-a", YesNo.NO)
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))

        self.add_collected_input(self.home_status, "top", OptAns.B)
        self.assertNotIn("seed-a", self.get_unanswered_measures(self.home_status))
        self.assertIn("seed-b", self.get_unanswered_measures(self.home_status))
        self.add_collected_input(self.home_status, "seed-b", YesNo.YES)
        self.assertIn("logic-or", self.get_unanswered_measures(self.home_status))
        self.add_collected_input(self.home_status, "seed-b", YesNo.NO)
        self.assertNotIn("logic-or", self.get_unanswered_measures(self.home_status))


class SimulationResolverConditionCaseTests(AxisTestCase):
    """This will flex out the Simulation Resolver"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import (
            eep_admin_factory,
            rater_admin_factory,
            builder_admin_factory,
        )
        from axis.home.tests.factories import (
            custom_home_factory,
            eep_program_custom_home_status_factory,
        )
        from axis.relationship.models import Relationship
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory
        from simulation.tests.factories import simulation_factory

        # users
        base_kwargs = {}

        eep_admin = eep_admin_factory(company__slug="eto", **base_kwargs)
        rater_admin = rater_admin_factory(
            company__slug="rater", company__city=eep_admin.company.city, **base_kwargs
        )
        builder_admin = builder_admin_factory(
            company__slug="builder", company__city=eep_admin.company.city, **base_kwargs
        )
        Relationship.objects.create_mutual_relationships(
            eep_admin.company, rater_admin.company, builder_admin.company
        )

        program = SimulationResolverProgramDefinition().build()
        home = custom_home_factory(
            city=eep_admin.company.city, builder_org=builder_admin.company, **base_kwargs
        )
        for company in [eep_admin.company, rater_admin.company, builder_admin.company]:
            Relationship.objects.validate_or_create_relations_to_entity(home, company)

        floorplan = basic_custom_home_floorplan_factory(owner=rater_admin.company, **base_kwargs)
        simulation = simulation_factory(
            company=rater_admin.company,
            version="VERSIONX",
            bedroom_count=1,
            water_heater_count=2,
            water_heater__fuel="natural_gas",
            water_heater__style="tankless",
            heater_count=1,
            distribution_system__system_type="hydronic",
            appliances__clothes_dryer_efficiency=2.61,
            appliances__dishwasher_consumption=271,
        )

        floorplan.simulation = simulation
        floorplan.save()

        home_status = eep_program_custom_home_status_factory(
            home=home, eep_program=program, floorplan=floorplan, company=company
        )

    def setUp(self):
        super(SimulationResolverConditionCaseTests, self).setUp()
        from axis.home.models import EEPProgramHomeStatus

        self.program = EEPProgram.objects.get()
        self.home_status = EEPProgramHomeStatus.objects.get()

    def test_equality(self):
        """Show that when you have an instrument condition where equality matters it will get
        caught.
            'simulation': {
                    'floorplan.simulation.version': {
                        'VERSION': [
                            'equality'
                        ]
                    },
            }
        """
        # With everything updated it should add our rem question
        self.assertEqual(self.home_status.floorplan.simulation.version, "VERSIONX")
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        simulation.version = "VERSION"
        simulation.save()

        self.assertEqual(self.home_status.floorplan.simulation.version, "VERSION")

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "equality"}, set(questions))

    def test_greater_than(self):
        """Show that when you have an instrument condition where greater than matters it will get
        caught.
            'simulation': {
                    'floorplan.simulation.bedroom_count': {
                        ('>', 2): [
                            'more-than-2-bedroom-question',
                        ],
                    }
            }
        """

        self.assertEqual(self.home_status.floorplan.simulation.bedroom_count, 1)
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        simulation.bedroom_count = 3
        simulation.save()

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "more-than-2-bedroom-question"}, set(questions))

    def test_m2m_one_of(self):
        """Show that when you have an instrument condition where one must match to get flagged.
        'simulation': {
                'floorplan.simulation.water_heaters.style': {
                    ('one', ('ashp', 'gshp')): [
                        'm2m-one-of',
                    ],
                },
        }
        """

        self.assertEqual(self.home_status.floorplan.simulation.water_heaters.count(), 2)
        styles = self.home_status.floorplan.simulation.water_heaters.values_list("style", flat=True)
        self.assertEqual(set(styles), {"tankless"})

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        mechnanical = simulation.water_heaters.first()
        mechnanical.style = "ashp"
        mechnanical.save()

        styles = self.home_status.floorplan.simulation.water_heaters.values_list("style", flat=True)
        self.assertEqual(set(styles), {"tankless", "ashp"})

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "m2m-one-of"}, set(questions))

    def test_m2m_one_of_for_singleton(self):
        """Show that when you have an instrument condition where one must match to get flagged.
            'simulation': {
                    'floorplan.simulation.heaters.distribution_type': {
                        ('one', ('forced_air',)): [
                            'm2m-one-of-2',
                        ],
                    },
            }
        This differs from the prior as there is ONLY one response.
        """
        self.assertEqual(self.home_status.floorplan.simulation.heaters.count(), 1)
        distribution_systems = self.home_status.floorplan.simulation.hvac_distribution_systems.all()
        distribution_types = distribution_systems.values_list("system_type", flat=True)
        self.assertEqual(set(distribution_types), {"hydronic"})

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        distribution_systems.update(system_type="forced_air")
        distribution_systems = self.home_status.floorplan.simulation.hvac_distribution_systems.all()
        distribution_types = distribution_systems.values_list("system_type", flat=True)
        self.assertEqual(set(distribution_types), {"forced_air"})

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "m2m-one-of-2"}, set(questions))

    def test_m2m_with_function_call(self):
        """Show that when you have an instrument condition where one must match to get flagged.
            'simulation': {
                'floorplan.simulation.water_heaters.is_conventional_gas': {
                    ('one', True): [
                        'm2m-one-of-exists'
                    ],
                },
            }
        This differs from the prior as this calls a function and not a an attribute
        """
        self.assertEqual(self.home_status.floorplan.simulation.water_heaters.count(), 2)
        styles = self.home_status.floorplan.simulation.water_heaters.values_list("style", flat=True)
        self.assertEqual(set(styles), {"tankless"})
        fuels = self.home_status.floorplan.simulation.water_heaters.values_list("fuel", flat=True)
        self.assertEqual(set(fuels), {"natural_gas"})

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        mechnanical = simulation.water_heaters.first()
        mechnanical.style = "conventional"
        mechnanical.save()

        styles = self.home_status.floorplan.simulation.water_heaters.values_list("style", flat=True)
        self.assertEqual(set(styles), {"conventional", "tankless"})

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "m2m-one-of-function"}, set(questions))

    def test_m2m_with_qs_exists(self):
        """Show that when you have an instrument condition where any of the QS needs to be there..
            'simulation': {
                'floorplan.simulation.air_source_heat_pumps': {
                    ('any', None): [
                        'm2m-qs-exists',
                    ],
                },
            }
        This differs in that we just care that one exists.
        """
        self.assertEqual(self.home_status.floorplan.simulation.air_source_heat_pumps.count(), 0)

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        from simulation.tests.factories import mechanical_equipment_factory

        mechanical_equipment_factory(simulation, "air_source_heat_pump")

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.floorplan.simulation.air_source_heat_pumps.count(), 1)

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question", "m2m-qs-exists"}, set(questions))

    def test_appliances_less_than_greater(self):
        """Show that when you have an instrument condition where any of the QS needs to be there..
            'simulation': {
                'floorplan.simulation.air_source_heat_pumps': {
                    ('any', None): [
                        'm2m-qs-exists',
                    ],
                },
            }
        This differs in that we just care that one exists.
        """
        self.assertEqual(self.home_status.floorplan.simulation.air_source_heat_pumps.count(), 0)

        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual({"open-question"}, set(questions))

        simulation = self.home_status.floorplan.simulation
        self.assertGreater(simulation.appliances.dishwasher_consumption, 270)
        self.assertLessEqual(simulation.appliances.clothes_dryer_efficiency, 2.62)

        appliances = simulation.appliances
        appliances.dishwasher_consumption = 269
        appliances.save()

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual(simulation.appliances.dishwasher_consumption, 269)
        self.assertEqual({"open-question", "equipment-dishwasher"}, set(questions))

        appliances.dishwasher_consumption = 271
        appliances.clothes_dryer_efficiency = 2.63
        appliances.save()

        from axis.home.models import EEPProgramHomeStatus  # Cached Property we need to refresh

        self.home_status = EEPProgramHomeStatus.objects.get()
        questions = self.home_status.get_unanswered_questions()
        questions = questions.values_list("measure", flat=True)
        self.assertEqual(simulation.appliances.dishwasher_consumption, 271)
        self.assertEqual(simulation.appliances.clothes_dryer_efficiency, 2.63)
        self.assertEqual({"open-question", "equipment-clothes-dryer"}, set(questions))


class EquipmentListTests(TestCase):
    def test_clothes_dryer_equipment_lists(self):
        data = CLOTHES_DRYER_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Combined Energy Factor"])
        select = CascadingClothesDryerPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_clothes_washer_equipment_lists(self):
        data = CLOTHES_WASHER_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Annual Energy Use (kWh/yr)"])
                self.assertIsNotNone(row["Integrated Modified Energy Factor"])
                self.assertIsNotNone(row["Volume (cu. ft.)"])
                self.assertIsNotNone(row["Electric Rate"])
                self.assertIsNotNone(row["Gas Rate"])
                self.assertIsNotNone(row["Annual Cost"])
        select = CascadingClothesWasherPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_dishwasher_equipment_lists(self):
        data = DISHWASHER_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Annual Energy Use (kWh/yr)"])
        select = CascadingDishwasherPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_furnace_equipment_lists(self):
        data = FURNACE_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Capacity (MBtuh)"])
                self.assertIsNotNone(row["AFUE (%)"])
                self.assertIsNotNone(row["Eae (kWh/yr)"])
                self.assertIsNotNone(row["ECM?"])
                self.assertIsNotNone(row["Motor HP"])
                self.assertIsNotNone(row["Ventilation Fan Watts"])
        select = CascadingFurnacePickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_heat_pumps_equipment_lists(self):
        data = HEAT_PUMP_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Outdoor Model Number"])
                self.assertIsNotNone(row["Indoor Model Number"])
                self.assertIsNotNone(row["Capacity 17F (kBtuh)"])
                self.assertIsNotNone(row["Capacity 47F (kBtuh)"])
                self.assertIsNotNone(row["HSPF"])
                self.assertIsNotNone(row["Cooling Capacity (kBtuh)"])
                self.assertIsNotNone(row["SEER"])
                self.assertIsNotNone(row["Motor HP"])
                self.assertIsNotNone(row["Ventilation Fan Watts"])
        select = CascadingHeatPumpPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_refrigerators_equipment_lists(self):
        data = REFRIGERATOR_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Annual Energy Use (kWh/yr)"])
        select = CascadingRefrigeratorPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_balanced_ventilation_equipment_lists(self):
        data = VENTILATION_BALANCED_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Net Airflow (CFM)"])
                self.assertIsNotNone(row["Power Consumption (Watts)"])
        select = CascadingBalancedVentilationPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_exhaust_ventilation_equipment_lists(self):
        data = VENTILATION_EXHAUST_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["SP"])
                self.assertIsNotNone(row["Speed (CFM)"])
                self.assertIsNotNone(row["Input power (watts)"])
        select = CascadingExhaustVentilationPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)

    def test_water_heater_equipment_lists(self):
        data = WATER_HEATER_LOOKUPS
        reader = csv.DictReader(data.split("\n"))
        for row in reader:
            with self.subTest(f"Row {row}"):
                self.assertIsNotNone(row["\ufeffBrand Name"])
                self.assertIsNotNone(row["Model Number"])
                self.assertIsNotNone(row["Capacity"])
                self.assertIsNotNone(row["Energy Factor"])
                self.assertIsNotNone(row["UEF/CCE"])
                self.assertIsNotNone(row["Converted EF"])
        select = CascadingWaterHeaterPickerMethod()
        self.assertIsNotNone(select.data)
        self.assertIsNotNone(select.source)
        self.assertIsNotNone(select.source_structured)
