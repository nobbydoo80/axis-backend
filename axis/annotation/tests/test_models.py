""" Tests for annotation models. """


from django.test import TestCase

from axis.annotation.tests.factories import type_factory, multiple_choice_type_factory
from axis.annotation.models import Type as AnnotationType

__author__ = "Autumn Valenta"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class TypeModelTestCase(TestCase):
    def test_clean_multiplechoices_values(self):
        """Verifies normalization of multiple-choice strings as a comma-separated list."""
        obj = multiple_choice_type_factory()
        values = AnnotationType().set_valid_multiplechoice_values("  1, 2  , 3,4 ".split(","))
        obj.valid_multiplechoice_values = values
        obj.save()
        self.assertEqual(obj.valid_multiplechoice_values, "1,2,3,4")

    def test_gains_unique_slug_when_created(self):
        """Verifies that an object with slug=None gains a unique one when saved."""
        from ..models import Type

        obj = type_factory(slug=None)
        self.assertNotIn(obj.slug, [None, ""])
        self.assertEqual(Type.objects.filter(slug=obj.slug).count(), 1)

    def test_set_valid_multiplechoice_values(self):
        values = ["Jack, the lead", "Joe - the coder extrodinaire", "Jon, cleanup;"]

        set_values = AnnotationType().set_valid_multiplechoice_values(values)
        self.assertEqual(
            set_values, '"Jack, the lead",Joe - the coder extrodinaire,"Jon, cleanup;"'
        )

        ann_type = AnnotationType.objects.create(
            name="Foo",
            description="Foo",
            data_type=AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
            valid_multiplechoice_values=set_values,
        )
        self.assertEqual(ann_type.valid_multiplechoice_values, set_values)
        self.assertEqual(ann_type.get_valid_multiplechoice_values(), values)

    def test_get_multiplechoice_value(self):
        values = ["Jack, the lead", "Joe – emdash coder", "Jon, cleanup;"]
        set_values = AnnotationType().set_valid_multiplechoice_values(values)

        ann_type = AnnotationType.objects.create(
            name="Foo",
            description="Foo",
            data_type=AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
            valid_multiplechoice_values=set_values,
        )

        choice = values[0].lower()
        result = ann_type.get_multiplechoice_value(choice)
        self.assertEqual(result, values[0])

        choice = "Joe - emdash coder"
        result = ann_type.get_multiplechoice_value(choice)
        self.assertEqual(result, values[1])

        choice = "JON, CleanuP;"
        result = ann_type.get_multiplechoice_value(choice)
        self.assertEqual(result, values[2])

        choice = "JON, CleanuP"
        result = ann_type.get_multiplechoice_value(choice)
        self.assertEqual(result, None)
