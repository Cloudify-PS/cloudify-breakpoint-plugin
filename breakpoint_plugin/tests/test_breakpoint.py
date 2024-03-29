# Third party imports
from unittest.mock import patch, MagicMock

# Local imports
from breakpoint_plugin.tests.base import BreakpointTestBase
from breakpoint_plugin.resources.breakpoint import start, delete, check
from cloudify.exceptions import NonRecoverableError, OperationRetry
from cloudify.state import current_ctx


class BreakpointNodeTest(BreakpointTestBase):
    expected_msg = 'Breakpoint active. An allowed user must deactivate ' \
                   'this breakpoint using the Set Breakpoint State ' \
                   'workflow to continue.'

    def setUp(self):
        super(BreakpointNodeTest, self).setUp()

    def get_mock_rest_client(self,
                             executions=None,
                             execution_creator_role=None,
                             execution_creator_tenant_roles=None):
        mock_rest_client = MagicMock()
        if execution_creator_tenant_roles is None:
            execution_creator_tenant_roles = ['user']
        mock_rest_client.executions.list = MagicMock(
            return_value=executions or [])
        mock_rest_client.users.get_self = MagicMock(
            return_value={
                'role': execution_creator_role,
                'tenants': {
                    'default_tenant': {
                        'roles': execution_creator_tenant_roles
                    }
                }})
        return mock_rest_client

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_start_permanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:23:26.975Z',
                'workflow_id': 'another_workflow',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:48:05.643Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_install': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_install': False
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
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(OperationRetry) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_start_nonpermanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_install': True
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
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(OperationRetry) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_restart_nonpermanent_open_breakpoint(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_install': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:23:26.975Z',
                'workflow_id': 'workflow',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
             }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_start_nonpermanent_open_breakpoint(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_install': False
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
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_default_break_on_install_false(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        start(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_delete_nonpermanent(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': ['BreakpointTestCase'],
                    'node_instance_ids': None,
                    'permanent': False,
                    'break_on_uninstall': True
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
                    'default_break_on_uninstall': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        with self.assertRaises(OperationRetry) as err:
            delete(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_delete_permanent_open_breakpoint(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_uninstall': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:23:26.975Z',
                'workflow_id': 'another_workflow',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_uninstall': True
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        delete(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_default_break_on_install_true(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': True
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(OperationRetry) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_default_break_on_uninstall_true(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_uninstall': True
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.delete')

        with self.assertRaises(OperationRetry) as err:
            delete(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_start_all_breakpoints(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': None,
                    'permanent': False,
                    'break_on_install': True
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
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(OperationRetry) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_start_latest_prioritized(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
                'created_at': '2021-06-17T10:23:26.975Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': False,
                    'break_on_install': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346acf',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase'],
                    'permanent': True,
                    'break_on_install': False
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
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(OperationRetry) as err:
            start(current_ctx.ctx)
            self.assertEqual(str(err), self.expected_msg)

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_check_executed_by_admin(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role="sys_admin")
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.breakpoint.check',
            ctx_execution_creator_username='admin')

        check(current_ctx.ctx)

        # assert
        # no error raised

    def test_check_executed_by_authorized_user(self):
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            ctx_operation_name='cloudify.interfaces.breakpoint.check',
            ctx_execution_creator_username='Bob')

        check(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_check_executed_by_authorized_role(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role="default",
            execution_creator_tenant_roles=['user'])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': [],
                    'roles': ['user']
                }
            },
            ctx_operation_name='cloudify.interfaces.breakpoint.check',
            ctx_execution_creator_username='Bob')

        check(current_ctx.ctx)

        # assert
        # no error raised

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_check_executed_by_unauthorized_user(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='default')
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice']
                }
            },
            ctx_operation_name='cloudify.interfaces.breakpoint.check',
            ctx_execution_creator_username='Eve')

        with self.assertRaises(NonRecoverableError):
            check(current_ctx.ctx)

    @patch('breakpoint_plugin.utils.get_rest_client')
    def test_check_executed_by_unauthorized_role(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(
            execution_creator_role='default',
            execution_creator_tenant_roles=['user'])
        self._prepare_context_for_operation(
            test_name='BreakpointTestCase',
            test_properties={
                'resource_config': {
                    'default_break_on_install': False
                },
                'authorization': {
                    'users': ['Alice'],
                    'roles': ['manager']
                }
            },
            ctx_operation_name='cloudify.interfaces.breakpoint.check',
            ctx_execution_creator_username='Eve')

        with self.assertRaises(NonRecoverableError):
            check(current_ctx.ctx)
