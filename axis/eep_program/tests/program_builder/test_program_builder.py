"""unit test for program builder"""

import logging
from datetime import date

from django.core import management

from axis.core.tests.test_views import DevNull
from django_input_collection.models import (
    CollectionRequest,
    SuggestedResponse,
    CollectionInstrument,
)

from axis.checklist.models.input import AxisBoundSuggestedResponse
from axis.company.tests.factories import (
    general_organization_factory,
)
from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.client import AxisClient
from axis.eep_program.models import EEPProgram
from axis.eep_program.program_builder.base import ProgramBuilder

__author__ = "Johnny Fang"
__date__ = "13/11/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

log = logging.getLogger(__name__)

OWNER_SLUG = "test-company"
PROGRAM_NAME = "Regular Program 5"
ROLE = "rater"
SAMPLE_MEASURE = "is-affordable-housing"
RESOLVER_TYPE = "instrument"


class RegularProgram5(ProgramBuilder):
    """This is a Test program"""

    slug = "regular-program-5"
    name = PROGRAM_NAME
    comment = "This program is for testing purposes"
    owner = OWNER_SLUG

    visibility_date = date(year=2019, month=8, day=1)
    start_date = date(year=2019, month=8, day=1)
    close_date = date(year=2019, month=11, day=1)
    submit_date = date(year=2019, month=11, day=15)
    end_date = date(year=2020, month=1, day=1)

    require_floorplan_approval = True

    simulation_type = "either"

    require_home_relationships = ["builder", "utility", "provider"]
    require_provider_relationships = ["builder", "provider"]

    measures = {
        ROLE: {
            "default": [
                SAMPLE_MEASURE,
                "is-adu",
                "builder-payment-redirected",
                "is-this-a-test",
                # Solar
                "applicable-solar-incentive",
                "has-solar-pv",
                "ets-annual-etsa-kwh",
                # Notes
                "inspection-notes",
            ],
        },
        "some-other-role": {
            "segment": [
                "applicable-to-this-role-only",
            ]
        },
    }
    texts = {
        "rater": {
            SAMPLE_MEASURE: "Is this affordable housing?",
            "is-adu": "Is this an Accessory Dwelling Unit (ADU)?",
            "builder-payment-redirected": "Does the builder wish to re-direct its payment for the EPS Whole Home "
            "incentive? If so, enter the contact name and payee company for the "
            "redirect.",
            "ets-annual-etsa-kwh": "What is the annual kWh generation as per the Energy Trust Solar Application? (Check"
            " with builder/solar trade ally for 221R)",
            "inspection-notes": "Notes",
            "is-this-a-test": "Simple question",
            "applicable-solar-incentive": "Does this home applicable for solar incentive",
            "has-solar-pv": "?",
        },
        "some-other-role": {
            "applicable-to-this-role-only": "Is this question applicable to this role only?"
        },
    }
    descriptions = {
        "default": {
            "ets-annual-etsa-kwh": "If receiving solar incentive from Energy Trust",
            SAMPLE_MEASURE: "This is a sample description",
            "is-this-a-test": "This is a simple question",
        }
    }
    suggested_responses = {
        "rater": {
            ("Yes", "No"): [SAMPLE_MEASURE, "is-this-a-test"],
        }
    }
    suggested_response_flags = {
        "default": {},
        "rater": {
            SAMPLE_MEASURE: {
                "No": {"comment_required": True},
            }
        },
    }
    instrument_types = {
        "integer": [
            "ets-annual-etsa-kwh",
        ]
    }
    instrument_conditions = {
        "default": {
            RESOLVER_TYPE: {
                "is-this-a-test": {
                    "Yes": [
                        SAMPLE_MEASURE,
                    ]
                }
            }
        }
    }
    instrument_order = [
        SAMPLE_MEASURE,
    ]

    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0

    is_public = False
    viewable_by_company_type = "utility"


class ProgramBuilderTests(AxisTestCase):
    """Test for program builder"""

    client_class = AxisClient

    def test_build_program(self):
        """Test build program with all its attrs"""
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__slug=OWNER_SLUG, company__name="EEP3")
        initial_program_count = EEPProgram.objects.count()
        built_program = RegularProgram5().build()
        program = EEPProgram.objects.get(name=PROGRAM_NAME)

        self.assertEqual(built_program, program)

        self.assertEqual(EEPProgram.objects.count(), initial_program_count + 1)

    def test_get_measures(self):
        """Test ProgramBuilder get_measures()"""
        pb_instance = RegularProgram5()
        measures = pb_instance.get_measures(ROLE)
        self.assertIn("default", measures)
        self.assertIn(SAMPLE_MEASURE, pb_instance.get_measures(ROLE).get("default"))

    def test_get_text(self):
        """Test ProgramBuilder get_text()"""
        pb_instance = RegularProgram5()
        text = pb_instance.get_text(ROLE, SAMPLE_MEASURE)
        self.assertIn(SAMPLE_MEASURE, pb_instance.get_measures(ROLE).get("default"))
        self.assertEqual("Is this affordable housing?", text)

    def test_get_description(self):
        """Test ProgramBuilder get_description()"""
        pb_instance = RegularProgram5()
        description = pb_instance.get_description(ROLE, SAMPLE_MEASURE)
        self.assertEqual("This is a sample description", description)

    def test_get_suggested_responses(self):
        """Test ProgramBuilder get_suggested_responses()"""
        pb_instance = RegularProgram5()
        suggested_response = pb_instance.get_suggested_responses(ROLE, SAMPLE_MEASURE)
        self.assertEqual(suggested_response, ("Yes", "No"))

    def test_get_suggested_response_flags(self):
        """Test ProgramBuilder get_suggested_response_flags()"""
        pb_instance = RegularProgram5()
        suggested_response_flag = pb_instance.get_suggested_response_flags(ROLE, SAMPLE_MEASURE)
        self.assertEqual({"No"}, set(suggested_response_flag.keys()))
        self.assertIn("comment_required", suggested_response_flag["No"].keys())
        self.assertTrue(suggested_response_flag["No"]["comment_required"])

    def test_get_type_from_instrument_types(self):
        """
        Test ProgramBuilder get_type(). instrument_types were supplied and measure is in the instrument_types' type
        """
        pb_instance = RegularProgram5()
        measure = "ets-annual-etsa-kwh"
        instrument_type = "integer"
        measure_type = pb_instance.get_type(ROLE, measure)
        self.assertTrue(len(pb_instance.instrument_types))
        self.assertIn("ets-annual-etsa-kwh", pb_instance.instrument_types[instrument_type])
        self.assertEqual("integer", measure_type)

    def test_get_type_from_suggested_responses(self):
        """
        Test ProgramBuilder get_type(). measure is not in any of the instrument_types' types, but is in
        suggested_responses
        """
        pb_instance = RegularProgram5()
        measure_type = pb_instance.get_type(ROLE, SAMPLE_MEASURE)
        self.assertEqual("multiple-choice", measure_type)

    def test_get_type(self):
        """
        Test ProgramBuilder get_type(). measure is not in any of the instrument_types' types or suggested_responses
        """
        pb_instance = RegularProgram5()
        measure_type = pb_instance.get_type(ROLE, "inspection-notes")
        self.assertEqual("open", measure_type)

    def test_get_is_multiple(self):
        """Test ProgramBuilder get_type()"""
        pb_instance = RegularProgram5()
        is_multiple = pb_instance.get_is_multiple(ROLE, SAMPLE_MEASURE)
        self.assertFalse(is_multiple)

    def test_get_conditions(self):
        """
        Test ProgramBuilder get_conditions()
        For a given resolver_type(instrument, rem, etc) and lookup_spec (measure) find
        """
        pb_instance = RegularProgram5()
        conditions = pb_instance.get_conditions(ROLE, RESOLVER_TYPE, SAMPLE_MEASURE)
        self.assertIn("is-this-a-test", conditions.keys())
        self.assertIn("Yes", conditions["is-this-a-test"])

    def test_get_conditions_none_found(self):
        """
        Test ProgramBuilder get_conditions()
        For a given resolver_type(instrument, rem, etc) and lookup_spec (measure) find
        """
        pb_instance = RegularProgram5()
        conditions = pb_instance.get_conditions(ROLE, RESOLVER_TYPE, "ets-annual-etsa-kwh")
        self.assertFalse(conditions)

    def test_build_type(self):
        """Test ProgramBuilder get_type()"""
        pb_instance = RegularProgram5()
        pb_instance.role = ROLE
        measure = "ets-annual-etsa-kwh"
        instrument_type = "integer"
        built_type = pb_instance.build_type(measure)
        self.assertEqual(built_type.id, instrument_type)

    def test_build_response_policy(self):
        """Test ProgramBuilder build_response_policy()"""
        pb_instance = RegularProgram5()
        pb_instance.role = ROLE
        restrict = bool(pb_instance.get_suggested_responses(pb_instance.role, SAMPLE_MEASURE))
        multiple = pb_instance.get_is_multiple(pb_instance.role, SAMPLE_MEASURE)
        response_policy = pb_instance.build_response_policy(SAMPLE_MEASURE)
        self.assertIsNone(response_policy.nickname)
        self.assertEqual(
            response_policy.required, SAMPLE_MEASURE not in pb_instance.optional_measures
        )
        self.assertEqual(response_policy.restrict, restrict)
        self.assertEqual(response_policy.multiple, multiple)

    def test_build_instrument(self):
        """
        Test ProgramBuilder build_instrument().
        SAMPLE_MEASURE has two suggested responses Yes and No, and they will end up bound once the instrument is built
        """
        pb_instance = RegularProgram5()
        pb_instance.role = ROLE
        group_id = "first-order"
        segment_id = "elite"
        measure_type_id = pb_instance.get_type(ROLE, SAMPLE_MEASURE)
        measure_attrs = {
            "collection_request": CollectionRequest.objects.create(
                max_instrument_inputs_per_user=10, max_instrument_inputs=30
            ),
            "text": pb_instance.get_text(ROLE, SAMPLE_MEASURE),
            "description": pb_instance.get_description(ROLE, SAMPLE_MEASURE),
            "order": pb_instance.instrument_order.index(SAMPLE_MEASURE),
        }
        result = pb_instance.build_instrument(SAMPLE_MEASURE, group_id, segment_id, **measure_attrs)
        suggested_responses = list(SuggestedResponse.objects.values_list("data", flat=True))
        bound_suggested_resp = list(
            AxisBoundSuggestedResponse.objects.values_list("suggested_response__data", flat=True)
        )

        self.assertTrue(CollectionInstrument.objects.get(id=result.id))
        self.assertEqual(result.type.id, measure_type_id)
        self.assertEqual(result.group.id, group_id)
        self.assertEqual(result.segment.id, segment_id)
        self.assertEqual(result.text, measure_attrs["text"])
        self.assertEqual(result.description, measure_attrs["description"])
        self.assertEqual(result.collection_request, measure_attrs["collection_request"])
        self.assertEqual(result.order, measure_attrs["order"])
        self.assertEqual(["Yes", "No"], suggested_responses)
        self.assertEqual(suggested_responses, bound_suggested_resp)

    def test_build_instruments(self):
        """Test ProgramBuilder's build_instruments"""
        pb_instance = RegularProgram5()
        pb_instance.role = ROLE
        measures = [SAMPLE_MEASURE]
        group_id = "first-order"
        segment_id = "elite"
        start_order = 0
        attrs = {
            "collection_request": CollectionRequest.objects.create(
                max_instrument_inputs_per_user=10, max_instrument_inputs=30
            ),
            "group": group_id,
            "segment": segment_id,
        }
        instruments = pb_instance.build_instruments(measures, start_order, **attrs)

        for i, instrument in enumerate(instruments):
            self.assertTrue(CollectionInstrument.objects.get(id=instrument.id))
            measure_type_id = pb_instance.get_type(pb_instance.role, measures[i])
            self.assertEqual(instrument.text, pb_instance.get_text(pb_instance.role, measures[i]))
            self.assertEqual(
                instrument.description, pb_instance.get_description(pb_instance.role, measures[i])
            )
            self.assertEqual(instrument.order, start_order + i)

    def test_build_checklist(self):
        """Test ProgramBuilder's build_instruments"""
        pb_instance = RegularProgram5()
        pb_instance.role = ROLE
        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs_per_user=10, max_instrument_inputs=30
        )
        result = pb_instance.build_checklist(collection_request)
        measures_keys = pb_instance.measures[ROLE].keys()
        self.assertIsNotNone(result)
        for measure_key in measures_keys:
            self.assertIn(measure_key, result.keys())
            measures = pb_instance.measures[ROLE]["default"]
            for collection_instrument in result[measure_key]:
                self.assertIn(collection_instrument.measure_id, measures)

    def test_validate_checklist_measure_without_text(self):
        """Test for validate_checklist()"""
        pb_instance = RegularProgram5()
        pb_instance.measures[ROLE]["default"].append("measure-without-text")
        pb_instance.role = ROLE

        with self.assertRaises(Exception):
            pb_instance.validate_checklist()

    def test_validate_checklist_unused_suggested_response(self):
        """Test for validate_checklist()"""
        pb_instance = RegularProgram5()
        pb_instance.suggested_responses[ROLE][("Gregor", "Sandor")] = [
            "clegane-bowl-pick",
        ]
        pb_instance.role = ROLE

        with self.assertRaises(Exception):
            pb_instance.validate_checklist()

    def test_validate_checklist_suggested_response_for_measure_already_defined(self):
        """Test for validate_checklist()"""
        pb_instance = RegularProgram5()
        pb_instance.suggested_responses[ROLE][("Gregor", "Sandor", "N/A")] = [
            "is-this-a-test",
        ]
        pb_instance.role = ROLE

        with self.assertRaises(Exception):
            pb_instance.validate_checklist()


class ProgramSuggestedResponses(ProgramBuilder):
    """This is a Test program"""

    slug = "regular-program-7"
    name = "Regular Program 7"
    owner = OWNER_SLUG

    measures = {
        "rater": {
            "default": [
                "sr-response-policy-basic",
            ],
        },
        "qa": {
            "default": [
                "sr-response-policy-basic",
            ],
        },
    }
    texts = {
        "default": {
            "sr-response-policy-basic": "Test the response policy shared between rater",
        },
    }
    descriptions = {
        "default": {
            "sr-response-policy-basic": "BLAH BLAH BLAH",
        }
    }
    instrument_types = {}
    suggested_responses = {
        "default": {
            ("NOTHING", "Comment", "Photo", "Document", "FAIL", "All"): ["sr-response-policy-basic"]
        },
    }
    suggested_response_flags = {
        "default": {
            "sr-response-policy-basic": {
                "Comment": {"comment_required": True},
                "Photo": {"photo_required": True},
                "Document": {"document_required": True},
                "FAIL": {"is_considered_failure": True},
                "All": {
                    "document_required": True,
                    "photo_required": True,
                    "comment_required": True,
                    "is_considered_failure": True,
                },
            }
        },
    }


class TestProgramSuggestedResponses(AxisTestCase):
    """This will flex out the Suggested Response Policy for Programs (without QA)"""

    client_class = AxisClient

    def setUp(self):
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__slug=OWNER_SLUG, company__name="EEP3")
        self.assertEqual(EEPProgram.objects.count(), 0)
        self.assertEqual(CollectionRequest.objects.count(), 0)
        self.assertEqual(CollectionInstrument.objects.count(), 0)
        self.assertEqual(SuggestedResponse.objects.count(), 0)
        self.assertEqual(AxisBoundSuggestedResponse.objects.count(), 0)
        built_program = ProgramSuggestedResponses().build("rater")
        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 1)
        self.program = EEPProgram.objects.get(slug="regular-program-7")
        self.assertIsNotNone(self.program.collection_request)
        self.assertEqual(self.program.collection_request.collectioninstrument_set.count(), 1)
        self.is_qa = False

    def test_program_instrument_measures(self):
        """Test build program with all its attrs"""
        instruments = self.program.collection_request.collectioninstrument_set
        measures = set(instruments.all().values_list("measure", flat=True))
        self.assertEqual(measures, {"sr-response-policy-basic"})

    def test_rater_no_suggested_responses(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()
        self.assertEqual(suggested_responses.count(), 6)

    def test_rater_no_suggested_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        # Now look at our suggested responses.  Note A response policy is NOT shared so you
        # need to look at the failures.
        nothing = suggested_responses.get(data="NOTHING")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_rater_comment_required_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        nothing = suggested_responses.get(data="Comment")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertTrue(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_rater_photo_required_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        nothing = suggested_responses.get(data="Photo")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertTrue(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_rater_document_required_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        nothing = suggested_responses.get(data="Document")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertTrue(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_rater_failing_required_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        nothing = suggested_responses.get(data="FAIL")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertTrue(response_policy.is_considered_failure)

    def test_rater_all_required_response_policy(self):
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()

        nothing = suggested_responses.get(data="All")
        suggested_response_set = nothing.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertTrue(response_policy.comment_required)
        self.assertTrue(response_policy.photo_required)
        self.assertTrue(response_policy.document_required)
        self.assertTrue(response_policy.is_considered_failure)

    def test_update_text(self):
        """We need a way to update the texts."""
        if self.is_qa:
            return
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        self.assertEqual(instrument.text, "Test the response policy shared between rater")

        updated_program = ProgramSuggestedResponses()
        updated_program.texts = {
            "default": {
                "sr-response-policy-basic": "FOOBAR",
            },
        }
        updated_program.build("rater")
        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 1)
        self.program = EEPProgram.objects.get(slug="regular-program-7")

        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        self.assertEqual(instrument.text, "FOOBAR")

    def test_update_descriptions(self):
        """We need a way to update the texts."""
        if self.is_qa:
            return
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        self.assertEqual(instrument.description, "BLAH BLAH BLAH")

        updated_program = ProgramSuggestedResponses()
        updated_program.descriptions = {
            "default": {
                "sr-response-policy-basic": "Nada..",
            }
        }
        updated_program.build("rater")
        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 1)
        self.program = EEPProgram.objects.get(slug="regular-program-7")

        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        self.assertEqual(instrument.description, "Nada..")

    def test_update_responses(self):
        """We need a way to update suggested responses."""
        if self.is_qa:
            return
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()
        _responses = set(suggested_responses.values_list("data", flat=True))
        self.assertEqual(_responses, {"NOTHING", "Comment", "Photo", "Document", "FAIL", "All"})

        updated_program = ProgramSuggestedResponses()
        updated_program.suggested_responses = {
            "default": {
                ("SOMETHING", "Comment", "Photo", "Document", "FAIL", "All"): [
                    "sr-response-policy-basic"
                ]
            },
        }
        updated_program.build("rater")

        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 1)
        self.program = EEPProgram.objects.get(slug="regular-program-7")

        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()
        _responses = set(suggested_responses.values_list("data", flat=True))
        self.assertEqual(_responses, {"SOMETHING", "Comment", "Photo", "Document", "FAIL", "All"})

    def test_update_add_measures(self):
        """We need a way to add a measure."""
        if self.is_qa:
            return
        instruments = self.program.collection_request.collectioninstrument_set
        measures = instruments.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"sr-response-policy-basic"})

        updated_program = ProgramSuggestedResponses()
        updated_program.measures = {
            "rater": {
                "default": [
                    "sr-response-policy-basic",
                    "new",
                ],
            },
            "qa": {
                "default": [
                    "sr-response-policy-basic",
                ],
            },
        }
        updated_program.texts = {
            "default": {
                "sr-response-policy-basic": "Test the response policy shared between rater",
                "new": "New question",
            },
        }
        updated_program.build("rater")

        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 2)
        self.program = EEPProgram.objects.get(slug="regular-program-7")

        instruments = self.program.collection_request.collectioninstrument_set
        measures = instruments.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"sr-response-policy-basic", "new"})

    def test_update_remove_measures(self):
        """We need a way to add a measure."""
        if self.is_qa:
            return
        instruments = self.program.collection_request.collectioninstrument_set
        measures = instruments.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"sr-response-policy-basic"})

        updated_program = ProgramSuggestedResponses()
        updated_program.measures = {
            "rater": {
                "default": [
                    "new",
                ],
            },
            "qa": {
                "default": [
                    "new",
                ],
            },
        }
        updated_program.texts = {
            "default": {
                "new": "New question",
            },
        }
        updated_program.suggested_responses = {}
        updated_program.suggested_response_flags = {}
        updated_program.build("rater")

        self.assertEqual(EEPProgram.objects.count(), 1)
        self.assertEqual(CollectionRequest.objects.count(), 1)
        self.assertEqual(CollectionInstrument.objects.count(), 1)
        self.program = EEPProgram.objects.get(slug="regular-program-7")

        instruments = self.program.collection_request.collectioninstrument_set
        measures = instruments.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"new"})


class TestProgramSuggestedResponsesQA(TestProgramSuggestedResponses):
    """This will flex out the Suggested Response Policy for Programs with QA"""

    def setUp(self):
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__slug=OWNER_SLUG, company__name="EEP3")
        self.assertEqual(EEPProgram.objects.count(), 0)
        built_program = ProgramSuggestedResponses().build()
        self.assertEqual(EEPProgram.objects.count(), 2)
        self.program = EEPProgram.objects.get(slug="regular-program-7")
        self.assertIsNotNone(self.program.collection_request)
        self.assertEqual(self.program.collection_request.collectioninstrument_set.count(), 1)
        self.qa_program = EEPProgram.objects.get(slug="regular-program-7-qa")
        self.assertIsNotNone(self.qa_program.collection_request)
        self.assertEqual(self.qa_program.collection_request.collectioninstrument_set.count(), 1)
        self.is_qa = True


class FullProgramDefinition(ProgramBuilder):
    """This is a Test program"""

    slug = "regular-program-6"
    name = "Regular Program 6"
    comment = "This program is for testing purposes"
    owner = OWNER_SLUG

    measures = {
        "rater": {
            "default": ["sr-response-policy-basic", "sr-response-policy-rater"],
        },
        "qa": {"segment": ["sr-response-policy-basic", "sr-response-policy-qa"]},
    }
    texts = {
        "default": {
            "sr-response-policy-basic": "Test the response policy shared between rater",
        },
        "rater": {
            "sr-response-policy-rater": "Verify document / comment / photo requirements",
        },
        "qa": {
            "sr-response-policy-qa": "Verify document / comment / photo requirements",
        },
    }
    instrument_types = {}
    suggested_responses = {
        "default": {("Yes", "Comment"): ["sr-response-policy-basic"]},
        "rater": {("Yes", "No"): ["sr-response-policy-rater"]},
        "qa": {("Yes", "No"): ["sr-response-policy-basic"], ("A", "B"): ["sr-response-policy-qa"]},
    }
    suggested_response_flags = {
        "default": {
            "sr-response-policy-basic": {
                "Comment": {"comment_required": True},
            }
        },
        "rater": {
            "sr-response-policy-rater": {
                "Yes": {"document_required": True},
            }
        },
        "qa": {
            "sr-response-policy-basic": {
                "Yes": {"photo_required": True},
            },
            "sr-response-policy-qa": {"A": {"is_considered_failure": True}},
        },
    }


class FullProgramMixAndMatchQA(AxisTestCase):
    """This will flex out the Suggested Reponse Policy for Programs"""

    client_class = AxisClient

    def setUp(self):
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__slug=OWNER_SLUG, company__name="EEP3")
        self.assertEqual(EEPProgram.objects.count(), 0)
        self.assertEqual(CollectionRequest.objects.count(), 0)
        self.assertEqual(CollectionInstrument.objects.count(), 0)
        self.assertEqual(SuggestedResponse.objects.count(), 0)
        self.assertEqual(AxisBoundSuggestedResponse.objects.count(), 0)
        built_program = FullProgramDefinition().build()
        self.assertEqual(EEPProgram.objects.count(), 2)
        self.assertEqual(CollectionRequest.objects.count(), 2)
        self.assertEqual(CollectionInstrument.objects.count(), 4)
        self.assertEqual(SuggestedResponse.objects.count(), 5)
        self.program = EEPProgram.objects.get(slug="regular-program-6")
        self.qa_program = EEPProgram.objects.get(slug="regular-program-6-qa")

    def test_build_rater_program_instrument_measures(self):
        """Test that each program comes out with the right measures"""
        self.assertIsNotNone(self.program.collection_request)
        self.assertEqual(self.program.collection_request.collectioninstrument_set.count(), 2)
        instruments = self.program.collection_request.collectioninstrument_set
        measures = set(instruments.all().values_list("measure", flat=True))
        self.assertEqual(measures, {"sr-response-policy-basic", "sr-response-policy-rater"})

    def test_build_qa_program_instrument_measures(self):
        """Test that each program comes out with the right measures"""
        self.assertIsNotNone(self.qa_program.collection_request)
        self.assertEqual(self.qa_program.collection_request.collectioninstrument_set.count(), 2)
        instruments = self.qa_program.collection_request.collectioninstrument_set
        measures = set(instruments.all().values_list("measure", flat=True))
        self.assertEqual(measures, {"sr-response-policy-basic", "sr-response-policy-qa"})

    def test_shared_rater_facing_program_suggested_responses(self):
        """Test that rater comes with the right suggested responses for the same question"""

        self.assertIsNotNone(self.program.collection_request)
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()
        self.assertEqual(suggested_responses.count(), 2)

        response = suggested_responses.get(data="Yes")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

        response = suggested_responses.get(data="Comment")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertTrue(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_shared_qa_facing_program_suggested_responses(self):
        """Test that qa comes with the right suggested responses for the same question"""

        self.assertIsNotNone(self.qa_program.collection_request)
        instruments = self.qa_program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-basic")
        suggested_responses = instrument.suggested_responses.all()
        self.assertEqual(suggested_responses.count(), 2)

        response = suggested_responses.get(data="Yes")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertTrue(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

        suggested_responses = instrument.suggested_responses.all()
        from django.core.exceptions import ObjectDoesNotExist

        try:
            response = suggested_responses.get(data="No")
        except ObjectDoesNotExist:
            print(
                "Test -- test_shared_qa_facing_program_suggested_responses: %s "
                % suggested_responses.all().values_list("data", flat=True)
            )
            raise

        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()

        # NOTE WE DON'T CARRY FORWARD THE POLICY!!
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_rater_only_program_suggested_responses(self):
        """Test that rater only question has the right suggested responses"""

        self.assertIsNotNone(self.program.collection_request)
        instruments = self.program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-rater")
        suggested_responses = instrument.suggested_responses.all()
        self.assertEqual(suggested_responses.count(), 2)

        response = suggested_responses.get(data="Yes")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertTrue(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

        response = suggested_responses.get(data="No")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)

    def test_qa_only_program_suggested_responses(self):
        """Test that qa only question has the right suggested responses"""

        self.assertIsNotNone(self.qa_program.collection_request)
        instruments = self.qa_program.collection_request.collectioninstrument_set
        instrument = instruments.get(measure="sr-response-policy-qa")
        suggested_responses = instrument.suggested_responses.all()
        self.assertEqual(suggested_responses.count(), 2)

        response = suggested_responses.get(data="A")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertTrue(response_policy.is_considered_failure)

        response = suggested_responses.get(data="B")
        suggested_response_set = response.axisboundsuggestedresponse_set
        response_policies = suggested_response_set.filter(collection_instrument=instrument)
        self.assertEqual(response_policies.count(), 1)
        response_policy = response_policies.get()
        self.assertFalse(response_policy.comment_required)
        self.assertFalse(response_policy.photo_required)
        self.assertFalse(response_policy.document_required)
        self.assertFalse(response_policy.is_considered_failure)


class LegacyProgramBuilder(AxisTestCase):
    """Verify that we can build out these legacy programs."""

    client_class = AxisClient

    def _build_and_test(self, owner_slug: str, program_slug: str, has_qa: bool = False):
        company = general_organization_factory(slug=owner_slug)
        management.call_command("build_program", "-p", program_slug, stdout=DevNull())

        total = 2 if has_qa else 1
        self.assertEqual(EEPProgram.objects.count(), total)

        eep_program = EEPProgram.objects.get(is_qa_program=False)
        self.assertEqual(eep_program.owner.id, company.id)
        self.assertEqual(eep_program.required_checklists.count(), 0)
        self.assertIsNotNone(eep_program.collection_request)

        if has_qa:
            eep_program = EEPProgram.objects.get(is_qa_program=True)
            self.assertEqual(eep_program.owner.id, company.id)
            self.assertEqual(eep_program.required_checklists.count(), 0)
            self.assertIsNotNone(eep_program.collection_request)

    def test_built_green_king_sno(self):
        self._build_and_test(
            "provider-home-builders-association-of-tri-cities", "built-green-king-sno"
        )

    def test_built_green_wa_performance(self):
        self._build_and_test(
            "provider-home-builders-association-of-tri-cities", "built-green-wa-performance", True
        )

    def test_built_green_wa_prescriptive(self):
        self._build_and_test(
            "provider-home-builders-association-of-tri-cities", "built-green-wa-prescriptive", True
        )

    def test_bullseye_eri(self):
        self._build_and_test("provider-bullseye", "bullseye-eri-certification")

    def test_doe_zero_energy_ready_rev_05_performance_path(self):
        self._build_and_test("us-doe", "doe-zero-energy-ready-rev-05-performance-path")

    def test_earth_advantage(self):
        self._build_and_test("earth-advantage-institute", "earth-advantage-certified-home")

    def test_energy_star_version_3_rev_08(self):
        self._build_and_test("us-epa", "energy-star-version-3-rev-08")

    def test_energy_star_version_31_rev_08(self):
        self._build_and_test("us-epa", "energy-star-version-31-rev-08")

    def test_energy_star_version_32_rev_08(self):
        self._build_and_test("us-epa", "energy-star-version-32-rev-08")

    def test_indoor_airplus_version_1_rev_03(self):
        self._build_and_test("us-epa", "indoor-airplus-version-1-rev-03")

    def test_mass_code(self):
        self._build_and_test("advanced-building-analysis", "mass-code-testing")

    def test_phius(self):
        self._build_and_test("eep-passive-house-institute-us-phius", "phius")

    def test_wsu_hers_2020(self):
        self._build_and_test("provider-washington-state-university-extension-ene", "wsu-hers-2020")

    def test_2012_mass_new_homes_with_energy_star(self):
        self._build_and_test("advanced-building-analysis", "2012-mass-new-homes-with-energy-star")

    def test_mass_code_testing(self):
        self._build_and_test(
            "advanced-building-analysis",
            "mass-code-testing",
        )

    def test_bpca_monthly_reporting(self):
        self._build_and_test(
            "integral-building",
            "bpca-monthly-reporting",
        )

    def test_energy_star_version_3_rev_07(self):
        self._build_and_test("us-epa", "energy-star-version-3-rev-07")

    def test_energy_star_version_31_rev_05(self):
        self._build_and_test(
            "us-epa",
            "energy-star-version-31-rev-05",
        )

    def test_doe_zero_energy_ready_rev_05_prescriptive_pat(self):
        self._build_and_test("us-doe", "doe-zero-energy-ready-rev-05-prescriptive-pat")

    def test_built_green_tri_cities(self):
        self._build_and_test(
            "provider-home-builders-association-of-tri-cities",
            "built-green-tri-cities",
        )

    def test_leed(self):
        self._build_and_test("eep-us-green-building-council-usgbc", "leed")

    def test_energy_star_version_32_rev_09(self):
        self._build_and_test("us-epa", "energy-star-version-32-rev-09")

    def test_watersense_version_12(self):
        self._build_and_test("us-epa", "watersense-version-12")

    def test_bonded_builders_residential_energy_guarantee(self):
        self._build_and_test(
            "eep-bonded-builders-warranty-group", "bonded-builders-residential-energy-guarantee"
        )

    def test_nyserda_incentive_application_form(self):
        self._build_and_test("integral-building", "nyserda-incentive-application-form")

    def test_nyserda_qualification_form(self):
        self._build_and_test("integral-building", "nyserda-qualification-form")

    def test_stretch_code_2012(self):
        self._build_and_test("stretch-code", "2012-stretch-code")
