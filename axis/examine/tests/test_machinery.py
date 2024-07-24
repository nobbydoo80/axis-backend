""" ExamineMachinery functionality tests. """


import logging

from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from ..machinery import ExamineMachinery, REGION_FIELD_NAMES

__author__ = "Autumn Valenta"
__date__ = "05/12/14 11:08 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

from axis.home.models import Home as TestModel
from axis.home.api import HomeViewSet as TestAPIProvider

TEST_TYPE_NAME = "home"


class TestMachinery(ExamineMachinery):
    model = TestModel
    type_name = TEST_TYPE_NAME
    api_provider = TestAPIProvider

    def can_delete_object(self, instance, user=None):
        return True

    def can_edit_object(self, instance, user=None):
        return True


class ExamineMachineryUtilsTests(TestCase):
    def test_Region_factory(self):
        """
        Accept only kwargs, and raises exceptions for kwargs not available in the Region tuple.
        """
        valid_kwargs = REGION_FIELD_NAMES
        invalid_kwargs = ["asdf"]

        region = TestMachinery.Region(**{k: None for k in valid_kwargs})
        msg = "Unknown keys for region configuration: ['asdf']"
        self.assertRaisesMessage(
            ValueError, msg, TestMachinery.Region, **{k: None for k in invalid_kwargs}
        )

    def test_ActionGroup_factory(self):
        """Accept positional arguments (since there are only a couple of them)."""
        actiongroup = TestMachinery.ActionGroup("Name", range(5))

    def test_Action_factory(self):
        """Accept positional argument for instruction and default values for others."""
        action = TestMachinery.Action("Name", "instruction")
        self.assertEqual(action["attrs"], {})  # Automatically set if not given


class ExamineMachinerySummaryTests(TestCase):
    """Tests for summary object the machinery sends to the View's template context."""

    def test_get_summary(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        required_keys = {
            "type_name",
            "type_name_slug",
            "verbose_name",
            "verbose_name_plural",
            "visible_fields",
            "new_region_url",
            "object_endpoint_pattern",
            "region_endpoint_pattern",
            "regionset_template_url",
            "region_dependencies",
        }
        self.assertEqual(True, required_keys.issubset(set(summary.keys())))

    def test_get_verbose_name(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["verbose_name"], machinery.model._meta.verbose_name)

    def test_get_verbose_name_plural(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["verbose_name_plural"], machinery.model._meta.verbose_name_plural)

    def test_get_new_regionendpoint(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["new_region_url"], machinery.get_new_region_endpoint())

    def test_get_regionset_template_url(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["regionset_template_url"], machinery.get_regionset_template_url())

    def test_summary_endpoints(self):
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(len(summary["endpoints"]), len(machinery.get_objects()))
        self.assertEqual(
            summary["endpoints"],
            [machinery.get_region_endpoint(o) for o in machinery.get_objects()],
        )


class ExamineMachineryNoDataTests(TestCase):
    """Tests that can be run without any data loaded via fixtures."""

    # These tests want to run without fixtures so that things just move faster.

    def test_init_requires_kwargs(self):
        """ExamineMachinery construction requires at least one mode configuration kwarg."""
        msg = (
            "TestMachinery requires one of the following init kwargs: instance, objects, create_new"
        )
        self.assertRaisesMessage(ValueError, msg, TestMachinery)

    def test_init_context_is_copy(self):
        """ExamineMachinery construction copies the value of "context"."""
        context = {"a": 1, "b": 2}
        machinery = TestMachinery(create_new=True, context=context)

        # They will be value-equal, but not identity-equal
        self.assertEqual(machinery.context, context)
        self.assertIsNot(machinery.context, context)

    def test_init_single_object(self):
        """machinery.instance is set to the supplied object."""
        obj = object()
        machinery = TestMachinery(instance=obj)

        self.assertEqual(machinery.instance, obj)
        self.assertEqual(machinery.objects, [obj])
        self.assertEqual(machinery.get_objects(), [obj])
        self.assertEqual(machinery.create_new, False)
        self.assertEqual(machinery.context, {})

    def test_init_multi_object(self):
        """machinery.instance is set to the supplied object."""
        object_list = [object(), object()]
        machinery = TestMachinery(objects=object_list)

        self.assertEqual(machinery.instance, None)
        self.assertEqual(machinery.objects, object_list)
        self.assertEqual(machinery.get_objects(), object_list)
        self.assertEqual(machinery.create_new, False)
        self.assertEqual(machinery.context, {})

    def test_init_new_object(self):
        """machinery.instance is set to the supplied object."""
        machinery = TestMachinery(create_new=True)

        self.assertNotEqual(machinery.instance, None)
        self.assertEqual(machinery.instance.pk, None)
        self.assertEqual(machinery.objects, [machinery.instance])
        self.assertEqual(machinery.get_objects(), [machinery.instance])
        self.assertEqual(machinery.create_new, True)
        self.assertEqual(machinery.context, {})

    def test_get_new_endpoint(self):
        """Endpoint should be 'apiv2:{model}-new-region'"""
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["new_region_url"].split("?")[0], reverse("apiv2:home-new-region"))

    def test_get_new_endpoint_customized(self):
        """Endpoint can be set to arbitrary url name."""

        class M(TestMachinery):
            new_region_endpoint = ""  # valid url name

        machinery = M(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["new_region_url"], None)

    def test_get_new_endpoint_disabled(self):
        """Endpoint can be set to None to avoid having one reversed."""

        class M(TestMachinery):
            new_region_endpoint = None

        machinery = M(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["new_region_url"], None)

    def test_get_action_groups(self):
        """Equal to the three core groups 'static', 'default', and 'edit'."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        action_group_names = set(regions[0]["actions"].keys())
        self.assertEqual(action_group_names, {"static", "default", "edit"})
        self.assertEqual(action_group_names, set(machinery.get_action_groups(machinery.instance)))

    def test_get_actions_callback(self):
        """
        Group names specified by get_actions_groups() are treated as callback names on the machinery
        and used to fetch lists.
        """

        class M(TestMachinery):
            def get_action_groups(self, instance):
                return ["custom_group"] + super(M, self).get_action_groups(instance)

            def get_custom_group_actions(self, instance):
                return ["this is invalid but will be treated as an action definition"]

        machinery = M(create_new=True)
        regions = machinery.get_regions()
        custom_group = regions[0]["actions"]["custom_group"]
        self.assertEqual(
            custom_group["actions"], ["this is invalid but will be treated as an action definition"]
        )

    def test_get_actions(self):
        """region.actions is a dict of group names to ActionGroup tuples."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        actions = regions[0]["actions"]
        self.assertIsInstance(actions, dict)
        self.assertIsInstance(actions["edit"], dict)

    def test_get_static_actions(self):
        """The 'static' actions group should be empty, but present."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["actions"]["static"]["actions"], [])

    def test_get_default_actions(self):
        """The 'default' actions group contains Delete and Edit actions (according to perms)."""
        obj = TestModel(pk=0)
        machinery = TestMachinery(instance=obj)
        regions = machinery.get_regions()
        self.assertEqual(len(regions[0]["actions"]["default"]["actions"]), 2)
        self.assertEqual(regions[0]["actions"]["default"]["actions"][0]["instruction"], "delete")
        self.assertEqual(regions[0]["actions"]["default"]["actions"][1]["instruction"], "edit")

    def test_get_default_actions_no_delete(self):
        """The 'default' actions group contains only an Edit action (according to perms)."""

        class M(TestMachinery):
            def can_delete_object(self, instance, user=None):
                return False

        obj = TestModel(pk=0)
        machinery = M(instance=obj)
        regions = machinery.get_regions()
        self.assertEqual(len(regions[0]["actions"]["default"]["actions"]), 1)
        self.assertEqual(regions[0]["actions"]["default"]["actions"][0]["instruction"], "edit")

    def test_get_default_actions_no_edit(self):
        """The 'default' actions group contains only a Delete action (according to perms)."""

        class M(TestMachinery):
            def can_edit_object(self, instance, user=None):
                return False

        obj = TestModel(pk=0)
        machinery = M(instance=obj)
        regions = machinery.get_regions()
        self.assertEqual(len(regions[0]["actions"]["default"]["actions"]), 1)
        self.assertEqual(regions[0]["actions"]["default"]["actions"][0]["instruction"], "delete")

    def test_get_edit_actions(self):
        """The 'edit' actions group contains a Cancel and Save action."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(len(regions[0]["actions"]["edit"]["actions"]), 2)

        self.assertEqual(regions[0]["actions"]["edit"]["actions"][0]["name"], "Cancel")
        self.assertEqual(
            regions[0]["actions"]["edit"]["actions"][0]["instruction"],
            machinery.create_new_cancel_action,
        )
        self.assertEqual(regions[0]["actions"]["edit"]["actions"][0]["style"], "default")

        self.assertEqual(regions[0]["actions"]["edit"]["actions"][1]["name"], "Save")
        self.assertEqual(regions[0]["actions"]["edit"]["actions"][1]["instruction"], "save")
        self.assertEqual(regions[0]["actions"]["edit"]["actions"][1]["style"], "primary")

    def test_cancel_action_instruction_varies_with_createnew(self):
        """Machinery.create_new toggles a different Cancel instruction."""
        existing_machinery = TestMachinery(
            instance=TestModel(id=1)
        )  # fudging, but shouldn't matter
        existing_cancel = existing_machinery.get_regions()[0]["actions"]["edit"]["actions"][0]

        new_machinery = TestMachinery(create_new=True)
        new_cancel = new_machinery.get_regions()[0]["actions"]["edit"]["actions"][0]

        self.assertEqual(existing_cancel["name"], "Cancel")
        self.assertEqual(existing_cancel["instruction"], "cancel")
        self.assertEqual(existing_cancel["style"], "default")

        self.assertEqual(new_cancel["name"], "Cancel")
        self.assertEqual(new_cancel["instruction"], new_machinery.create_new_cancel_action)
        self.assertEqual(new_cancel["style"], "default")

    def test_get_id(self):
        """Machinery.get_id() returns a "{typename}_{pk}" string."""
        machinery = TestMachinery(instance=TestModel(id=1))  # fudging, but shouldn't matter
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["id"], machinery.get_id(machinery.instance))
        self.assertEqual(regions[0]["id"], "home_1")

    def test_get_id_substitute_when_new_object(self):
        """Machinery.get_id() returns a "{typename}__{timestamp}" string."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        try:
            self.assertEqual(regions[0]["id"], machinery.get_id(machinery.instance))
        except AssertionError:
            # This may actually end-up one off.
            _id = regions[0]["id"][:-1] + "%s" % (int(regions[0]["id"][-1]) + 1)
            self.assertEqual(_id, machinery.get_id(machinery.instance))

        self.assertRegex(regions[0]["id"], r"^home__\d+$")

    def test_get_type_name(self):
        """Machinery.get_type_name() returns back the Machinery.type_name"""
        machinery = TestMachinery(create_new=True)
        self.assertEqual(machinery.type_name, machinery.get_type_name(machinery.instance))

    def test_get_object_name(self):
        """Machinery.get_object_name() returns the str() of the given instance."""
        machinery = TestMachinery(instance=TestModel(id=1))  # fudging, but shouldn't matter
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["object_name"], machinery.get_object_name(machinery.instance))
        self.assertEqual(regions[0]["object_name"], "{}".format(machinery.instance))

    def test_get_object_name_generic_string_when_new_object(self):
        """Machinery.get_object_name() returns a string like "New {verbosename}"."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["object_name"], machinery.get_object_name(machinery.instance))
        self.assertEqual(regions[0]["object_name"], "New Project")

    def test_get_default_instruction(self):
        """Machinery.get_default_instruction() returns None."""
        machinery = TestMachinery(instance=TestModel(id=1))  # fudging, but shouldn't matter
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["default_instruction"], machinery.get_default_instruction(machinery.instance)
        )
        self.assertEqual(regions[0]["default_instruction"], None)

    def test_get_default_instruction_edit_when_new_object(self):
        """Machinery.get_default_instruction() returns "edit"."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["default_instruction"], machinery.get_default_instruction(machinery.instance)
        )
        self.assertEqual(regions[0]["default_instruction"], "edit")

    def test_get_region_template(self):
        """Machinery.get_region_template() returns Machinery.region_template"""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["region_template_url"], machinery.get_region_template_url(machinery.instance)
        )

    def test_get_object_endpoint_substituted_when_new_object(self):
        """Machinery.get_object_endpoint() returns reversed Machinery.new_object_endpoint."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["object_endpoint"], machinery.get_object_endpoint(machinery.instance)
        )
        self.assertEqual(
            regions[0]["object_endpoint"].split("?")[0],
            reverse(machinery.new_object_endpoint.format(model="home")),
        )
        self.assertEqual(regions[0]["object_endpoint"].split("?")[0], reverse("apiv2:home-list"))

    def test_get_object_endpoint_unavailable_when_new_object_and_endpoint_blanked(self):
        """Machinery.get_object_endpoint() returns None."""

        class M(TestMachinery):
            new_object_endpoint = None

        machinery = M(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["object_endpoint"], None)

    def test_get_delete_endpoint(self):
        """Machinery.get_delete_endpoint() returns None."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["delete_endpoint"], machinery.get_delete_endpoint(machinery.instance)
        )
        self.assertEqual(regions[0]["delete_endpoint"], None)

    def test_get_region_endpoint_substituted_when_new_object(self):
        """Machinery.get_region_endpoint() returns reversed Machinery.new_region_endpoint."""
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(len(summary["endpoints"]), 1)
        self.assertEqual(summary["endpoints"][0], machinery.get_region_endpoint(machinery.instance))
        self.assertEqual(
            summary["endpoints"][0].split("?")[0],
            reverse(machinery.new_region_endpoint.format(model="home")),
        )
        self.assertEqual(summary["endpoints"][0].split("?")[0], reverse("apiv2:home-new-region"))

    def test_get_helpers(self):
        """Machinery.get_helpers() returns a reference to the verbose_name and the machinery."""
        machinery = TestMachinery(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["helpers"],
            {
                "verbose_name": machinery.model._meta.verbose_name,
                # 'machinery': machinery,
            },
        )

    def test_get_region_dependencies(self):
        """Machinery.get_region_dependencies() returns an empty spec by default."""
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(summary["region_dependencies"], {})

    def test_get_verbose_names(self):
        """Machinery form can declare a custom label and it appears as the verbose name."""
        from django.forms import ModelForm

        class F(ModelForm):
            class Meta:
                model = TestModel
                labels = {
                    "street_line1": "Custom Verbose Name",
                }
                exclude = []

        class M(TestMachinery):
            form_class = F

        machinery = M(create_new=True)
        regions = machinery.get_regions()
        self.assertEqual(regions[0]["verbose_names"]["street_line1"], "Custom Verbose Name")

    def test_kwargs_getter_runs_before_value_getter(self):
        class M(TestMachinery):
            def get_object_name_kwargs(self, instance):
                raise Exception("kwargs getter called")

            def get_object_name(self, instance):
                raise Exception("value getter called")

        machinery = M(create_new=True)
        with self.assertRaisesRegex(Exception, r"^kwargs getter called$"):
            machinery.get_regions()

    def test_get_absolute_url(self):
        instance = TestModel(id=1)  # fudging a real instance, get_absolute_url won't care
        machinery = TestMachinery(instance=instance)
        self.assertEqual(machinery.get_regions()[0]["absolute_url"], instance.get_absolute_url())

    def test_get_object_endpoint(self):
        """Machinery.get_object_endpoint() returns reversed Machinery.object_endpoint."""
        instance = TestModel(id=1)
        machinery = TestMachinery(instance=instance)
        regions = machinery.get_regions()
        self.assertEqual(
            regions[0]["object_endpoint"], machinery.get_object_endpoint(machinery.instance)
        )
        self.assertEqual(
            regions[0]["object_endpoint"].split("?")[0],
            reverse("apiv2:home-detail", kwargs={"pk": instance.pk}),
        )

    def test_get_region_endpoint(self):
        """Machinery.get_region_endpoint() returns reversed Machinery.region_endpoint."""
        instance = TestModel(id=1)
        machinery = TestMachinery(instance=instance)
        summary = machinery.get_summary()
        self.assertEqual(summary["endpoints"][0], machinery.get_region_endpoint(machinery.instance))
        self.assertEqual(
            summary["endpoints"][0].split("?")[0],
            reverse("apiv2:home-region", kwargs={"pk": instance.pk}),
        )

    def test_get_region_endpoint_for_future_object(self):
        """
        Machinery.get_region_endpoint() returns reversed Machinery.region_endpoint where 'pk' is
        replaced with '__id__' for client-side dependency resolution once "save" is complete.
        """
        machinery = TestMachinery(create_new=True)
        summary = machinery.get_summary()
        self.assertEqual(
            summary["region_endpoint_pattern"], machinery.get_region_endpoint_pattern()
        )
        self.assertEqual(
            summary["region_endpoint_pattern"].split("?")[0],
            reverse("apiv2:home-region", kwargs={"pk": "__id__"}),
        )

    def test_parameterize_context_includes_machinery_name(self):
        """Machinery GET parameter generation includes the machinery class name by default."""
        machinery = TestMachinery(create_new=True)
        parameters_string = machinery.parameterize_context()
        q = QueryDict(parameters_string[1:])  # Don't want leading '?' in this simulated event
        self.assertEqual(q.get("machinery"), machinery.__class__.__name__)

    def test_parameterize_context_always_starts_with_questionmark(self):
        """Machinery GET parameter generation always starts with "?" for safe calls to super()."""

        class M(TestMachinery):
            def parameterize_context(self, **kwargs):
                s = super(M, self).parameterize_context(**kwargs)
                s += "&foo=bar"
                return s

        machinery = M(create_new=True)
        parameters_string = machinery.parameterize_context()
        q = QueryDict(parameters_string[1:])  # Don't want leading '?' in this simulated event
        self.assertEqual(len(parameters_string) > 0, True)
        self.assertEqual(parameters_string[0], "?")
        self.assertEqual(parameters_string.endswith("&foo=bar"), True)
        self.assertIn("foo", q)
        self.assertEqual(q["foo"], "bar")

    def test_parameterize_context_excludes_special_reserved_values(self):
        """
        Machinery GET parameter generation omits 'request' and 'lightweight' keys from original
        context.
        """

        context = {"request": "fake", "lightweight": True, "extra": "valid"}
        machinery = TestMachinery(create_new=True, context=context)
        parameters_string = machinery.parameterize_context()
        q = QueryDict(parameters_string[1:])  # Don't want leading '?' in this simulated event
        self.assertNotIn("request", q)
        self.assertNotIn("lightweight", q)

    def test_parameterize_context_includes_abitrary_extra_values(self):
        """
        Machinery GET parameter generation will serialize anything found in ``self.context`` to a
        simple JSON-like representation.
        """

        context = {
            "extra": "valid",
            "model": TestModel(id=1),
            "bool": True,
            "none": None,
            "float": 3.14,
        }
        machinery = TestMachinery(create_new=True, context=context)
        parameters_string = machinery.parameterize_context()
        q = QueryDict(parameters_string[1:])  # Don't want leading '?' in this simulated event
        self.assertIn("extra", q)
        self.assertEqual(q["extra"], "valid")
        self.assertIn("model", q)
        self.assertEqual(q["model"], "1")
        self.assertIn("bool", q)
        self.assertEqual(q["bool"], "true")
        self.assertIn("none", q)
        self.assertEqual(q["none"], "null")
        self.assertIn("float", q)
        self.assertEqual(q["float"], "3.14")

    def test_parameterize_context_kwargs_trump_context(self):
        """
        Machinery GET parameter generation will add extra ``kwargs`` last, making them available as
        the default values when accessing a constructed request.GET.
        """
        context = {"extra": 1}
        trump_kwargs = {"extra": 2}
        machinery = TestMachinery(create_new=True, context=context)
        parameters_string = machinery.parameterize_context(**trump_kwargs)
        q = QueryDict(parameters_string[1:])  # Don't want leading '?' in this simulated event
        self.assertIn("extra", q)
        self.assertEqual(q["extra"], "2")
        self.assertEqual(q.getlist("extra"), ["1", "2"])


class GeocodedExamineTests(TestCase):
    """Verifies that a GeocodedMachineryMixin subclass overrides the Save action."""

    def test_get_commit_instruction(self):
        machinery = TestMachinery(create_new=True)
        self.assertEqual(machinery.get_regions()[0]["commit_instruction"], "save")

        from axis.core.views.machinery import AxisGeocodedMachineryMixin

        class M(AxisGeocodedMachineryMixin, TestMachinery):
            pass

        machinery = M(create_new=True)
        self.assertEqual(machinery.get_regions()[0]["commit_instruction"], "geocode")

    def test_geocoded_version_hijacks_Save_action(self):
        from axis.core.views.machinery import AxisGeocodedMachineryMixin

        class M(AxisGeocodedMachineryMixin, TestMachinery):
            pass

        machinery = M(create_new=True)
        regions = machinery.get_regions()
        save_action = regions[0]["actions"]["edit"]["actions"][1]
        self.assertEqual(save_action["name"], "Save")
        self.assertEqual(save_action["instruction"], "geocode")
        self.assertEqual(save_action["style"], "primary")
