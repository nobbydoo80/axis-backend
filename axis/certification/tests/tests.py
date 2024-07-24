import os.path
import logging

from django.test import TestCase

from django_states.machine import StateMachine

from ..api.serializers import WorkflowStatusSerializer
from ..models import Workflow, WorkflowStatus, CertifiableObject
from . import factories


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

#
# def NOT_IMPLEMENTED(self):
#     raise AssertionError("Not Implemented")
#
#
# class WorkflowTests(TestCase):
#     test_workflow_ignores_underscore_configs = NOT_IMPLEMENTED  # "_template.json" is not valid
#
#     def test_workflow_memoizes_config(self):
#         workflow = factories.workflow_factory()
#
#         # Check cached attribute doesn't exist
#         self.assertEqual(hasattr(workflow, '_config'), False)
#
#         # Load the config
#         config = workflow.get_config()
#         self.assertEqual(hasattr(workflow, '_config'), True)
#
#         # Check cached attribute prevents unwanted loading
#         config_again = workflow.get_config()
#         self.assertIs(config, config_again)
#
#     def test_workflow_config_reload_ignores_cached_attribute(self):
#         workflow = factories.workflow_factory()
#         config = workflow.get_config()
#
#         # Check cached attribute already exists
#         self.assertEqual(hasattr(workflow, '_config'), True)
#
#         # Check reload ignores cached attribute and rebuilds config from scratch
#         config_again = workflow.get_config(reload=True)
#         self.assertIsNot(config, config_again)
#
#
# class SerializerTests(TestCase):
#     def test_serializer_builds_data_fields(self):
#         workflow_status = factories.workflow_status_factory(**{
#             'certifiable_object': {
#                 'type': 'project',
#                 'settings': {
#                     'type': 'new_construction',
#                 },
#             },
#         })
#
#         # Get what fields should exist
#         # FIXME: broken detection of field_spec object_types
#         config = workflow_status.workflow.get_config()
#         data_spec = config.get_data_spec(object_type='project')
#         spec_field_names = [
#             name for name, field_spec in data_spec.items() \
#                  if 'project' in field_spec['settings']['object_types']
#         ]
#
#         # Get loaded fields
#         serializer = WorkflowStatusSerializer(instance=workflow_status)
#         loaded_field_names = serializer.fields['data'].fields.keys()
#
#         self.assertEqual(loaded_field_names, spec_field_names)
#
#
# class StateMachineTests(TestCase):
#     test_empty_child_state_machine_allows_advancement = NOT_IMPLEMENTED
#     test_child_state_machine_blocks_advancement = NOT_IMPLEMENTED
#     test_certifiable_object_model_uses_dynamic_state_machine = NOT_IMPLEMENTED
#
#     # Underpinnings of the dynamic state machine code
#     def test_workflow_status_object_configures_on_init(self):
#         workflow_status = factories.workflow_status_factory(**{
#             'certifiable_object': {
#                 'type': 'home',
#             },
#         })
#         self.assertEqual(hasattr(workflow_status, '_state_machine_configured'), True)
#
#     def test_certifiable_object_model_uses_dynamic_state_machine(self):
#         workflow_status = factories.workflow_status_factory(**{
#             'certifiable_object': {
#                 'type': 'home',
#             },
#         })
#
#         # Call on built-in django_states method to ensure we get the runtime-overriden value
#         machine = workflow_status.get_state_machine()
#         self.assertNotEqual(machine, StateMachine)
#
#         config_name = os.path.splitext(os.path.basename(workflow_status.workflow.config_path))[0]
#         self.assertEqual(machine.__name__, 'WorkflowStateMachine_%s' % (config_name,))
#
#     # State machine behaviors
#
#
# class ValuesSheetTests(TestCase):
#     test_values_sheet_refresh_pulls_from_json = NOT_IMPLEMENTED
#
#
# class CertificationTests(TestCase):
#     test_missing_required_values_blocks_certification = NOT_IMPLEMENTED
#     test_missing_optional_values_allows_certification = NOT_IMPLEMENTED
#     test_home_object_passes_generic_logic = NOT_IMPLEMENTED


class CertificationTests(TestCase):
    def test_true(self):
        self.assertTrue(True)
