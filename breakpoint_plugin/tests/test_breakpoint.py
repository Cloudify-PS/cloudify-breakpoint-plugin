# Third party imports
from unittest.mock import patch, MagicMock

# Local imports
from base import BreakpointTestBase
from breakpoint_plugin.resources.breakpoint import start, stop
from cloudify.exceptions import NonRecoverableError, OperationRetry
from cloudify.state import current_ctx


class BreakpointNodeTest(BreakpointTestBase):
    expected_msg = 'Breakpoint active. An allowed user must deactivate ' \
                   'this breakpoint using the Set Breakpoint State ' \
                   'workflow to continue.'

    def setUp(self):
        super(BreakpointNodeTest, self).setUp()

    def get_mock_rest_client(self, executions):
        mock_rest_client = MagicMock()
        mock_rest_client.executions.list = MagicMock(return_value=executions)
        return mock_rest_client

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_start_permanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_start': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_start': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:23:26.975Z',
                'ended_at': '2021-06-17T10:33:36.171Z',
                'workflow_id': 'another_workflow',
                'started_at': '2021-06-17T10:23:26.976Z',
                'blueprint_id': 'simple-breakpoint-blueprint',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_start_nonpermanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_start': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_restart_nonpermanent_open_breakpoint(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_start': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:23:26.975Z',
                'ended_at': '2021-06-17T10:33:36.171Z',
                'workflow_id': 'workflow',
                'started_at': '2021-06-17T10:23:26.976Z',
                'blueprint_id': 'simple-breakpoint-blueprint',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
             }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_start_nonpermanent_open_breakpoint(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_start': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_default_break_on_start_false(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_stop_nonpermanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': ['BreakpointTestCase'],
                    'node_instance_ids': None,
                    'permanent': False,
                    'break_on_stop': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_stop': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.stop')

        with self.assertRaises(OperationRetry) as err:
            stop(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_default_break_on_start_true(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': True
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_default_break_on_stop_true(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_stop': True
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.stop')

        with self.assertRaises(OperationRetry) as err:
            stop(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_start_all_breakpoints(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': None,
                    'permanent': False,
                    'break_on_start': True,
                    'all_breakpoints': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.resources.breakpoint.get_rest_client')
    def test_start_latest_prioritized(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'ended_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_start': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
                'ended_at': '2021-06-17T10:23:26.975Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_start': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_start': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)
