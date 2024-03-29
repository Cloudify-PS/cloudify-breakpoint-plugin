# Standard imports
from unittest.mock import patch, MagicMock
from collections import namedtuple

# Local imports
from breakpoint_plugin.tests.base import BreakpointTestBase
from breakpoint_plugin.workflows.state import set_breakpoint_state
from breakpoint_plugin.constants import BREAKPOINT_TYPE

from cloudify.exceptions import NonRecoverableError


class BreakpointWorkflowTest(BreakpointTestBase):
    def get_mock_rest_client(self,
                             execution_creator_role=None,
                             execution_creator_tenant_roles=None):
        mock_rest_client = MagicMock()
        node_instance = namedtuple('MockNodeInstance', 'node_id')
        if execution_creator_tenant_roles is None:
            execution_creator_tenant_roles = ['user']
        mock_rest_client.node_instances.get = MagicMock(
            return_value=node_instance('BreakpointTestCase'))
        mock_rest_client.users.get_self = MagicMock(
            return_value={
                'role': execution_creator_role,
                'tenants': {
                    'default_tenant': {
                        'roles': execution_creator_tenant_roles
                    }
                }})
        return mock_rest_client

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_admin_allowed(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='sys_admin')
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            type_hierarchy=['cloudify.nodes.Root', BREAKPOINT_TYPE],
            node_type=BREAKPOINT_TYPE,
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='admin')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])
        self._ctx.node_instances = MagicMock(
            return_value=[self._ctx.node.instances])

        result = set_breakpoint_state(node_instance_ids=['BreakpointTestCase'],
                                      ctx=self._ctx)

        self.assertTrue(result)

    def test_authorized_user(self):
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            type_hierarchy=['cloudify.nodes.Root', BREAKPOINT_TYPE],
            node_type=BREAKPOINT_TYPE,
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Alice')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])
        self._ctx.node_instances = MagicMock(
            return_value=[self._ctx.node.instances])

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
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            type_hierarchy=['cloudify.nodes.Root', BREAKPOINT_TYPE],
            node_type=BREAKPOINT_TYPE,
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Eve')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])
        self._ctx.node_instances = MagicMock(
            return_value=[self._ctx.node.instances])

        with self.assertRaises(NonRecoverableError):
            set_breakpoint_state(node_ids=['BreakpointTestCase'],
                                 ctx=self._ctx)

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_authorized_role(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='default',
            execution_creator_tenant_roles=['manager'])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': [],
                    'roles': ['manager']
                }
            },
            type_hierarchy=['cloudify.nodes.Root', BREAKPOINT_TYPE],
            node_type=BREAKPOINT_TYPE,
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Eve')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])
        self._ctx.node_instances = MagicMock(
            return_value=[self._ctx.node.instances])

        result = set_breakpoint_state(node_ids=['BreakpointTestCase'],
                                      ctx=self._ctx)

        self.assertTrue(result)

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_unauthorized_role(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='default',
            execution_creator_tenant_roles=['user'])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': [],
                    'roles': ['manager']
                }
            },
            type_hierarchy=['cloudify.nodes.Root', BREAKPOINT_TYPE],
            node_type=BREAKPOINT_TYPE,
            ctx_operation_name='set_breakpoint_state',
            ctx_execution_creator_username='Eve')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])
        self._ctx.node_instances = MagicMock(
            return_value=[self._ctx.node.instances])

        with self.assertRaises(NonRecoverableError):
            set_breakpoint_state(node_ids=['BreakpointTestCase'],
                                 ctx=self._ctx)

    def test_invalid_node_ids(self):
        expected_msg = 'node_ids/node_instance_ids parameter should be a list!'
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            ctx_operation_name='set_breakpoint_state')
        self._ctx.get_node = MagicMock(return_value=self._ctx.node)
        self._ctx.nodes = MagicMock(return_value=[self._ctx.node])

        with self.assertRaises(NonRecoverableError) as err:
            set_breakpoint_state(node_instance_ids="[]",
                                 ctx=self._ctx)
            self.assertEqual(str(err), expected_msg)
