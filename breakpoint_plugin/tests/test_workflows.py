# Standard imports
from unittest.mock import patch, MagicMock
from collections import namedtuple

# Local imports
from breakpoint_plugin.tests.base import BreakpointTestBase
from breakpoint_plugin.workflows.state import set_breakpoint_state
from cloudify.exceptions import NonRecoverableError


class BreakpointWorkflowTest(BreakpointTestBase):
    def get_mock_rest_client(self, execution_creator_role=None):
        mock_rest_client = MagicMock()
        node_instance = namedtuple('MockNodeInstance', 'node_id')
        mock_rest_client.node_instances.get = MagicMock(
            return_value=node_instance('BreakpointTestCase'))
        mock_rest_client.users.get = MagicMock(
            return_value={'role': execution_creator_role})
        return mock_rest_client

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_admin_allowed(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='sys_admin')
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='admin')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        result = set_breakpoint_state(node_instance_ids=['BreakpointTestCase'],
                                      ctx=self._ctx)
        self.assertTrue(result)

    def test_authorized_user(self):
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Alice')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        result = set_breakpoint_state(node_ids=['BreakpointTestCase'],
                                      ctx=self._ctx)
        self.assertTrue(result)

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_unauthorized_user(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='default')
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Eve')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        with self.assertRaises(NonRecoverableError):
            set_breakpoint_state(node_ids=['BreakpointTestCase'],
                                 ctx=self._ctx)
