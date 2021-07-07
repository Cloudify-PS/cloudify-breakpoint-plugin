# Third party imports
from unittest.mock import patch, MagicMock
from unittest import TestCase

# Local imports
from breakpoint_sdk.resources.breakpoint_state_executions import (
    BreakpointStateExecutions
)


class BreakpointStateExecutionsTest(TestCase):

    def setUp(self):
        super(BreakpointStateExecutionsTest, self).setUp()

    def get_mock_rest_client(self, executions=None):
        mock_rest_client = MagicMock()
        mock_rest_client.executions.list = MagicMock(
            return_value=executions or [])
        return mock_rest_client

    @patch('breakpoint_sdk.resources.breakpoint_state_executions'
           '.get_rest_client')
    def test_get_valid(self, get_rest_client):
        get_rest_client.return_value = self.get_mock_rest_client(executions=[
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
                'created_at': '2021-06-17T10:23:26.975Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase_123'],
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
                    'node_instance_ids': ['BreakpointTestCase_123'],
                    'permanent': True,
                    'break_on_install': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ])

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        valid_execution = breakpoint_executions.get_valid_execution()

        self.assertEqual(valid_execution.get('created_at'),
                         '2021-06-17T10:23:26.975Z')

    def test_get_latest_permanent(self):
        executions = [
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
                    'node_instance_ids': ['BreakpointTestCase_123'],
                    'permanent': True,
                    'break_on_install': True
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
                'created_at': '2021-06-16T14:45:55.592Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase_123'],
                    'permanent': True,
                    'break_on_install': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ]

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        valid_execution = \
            breakpoint_executions.get_permanent_execution(executions)

        self.assertEqual(valid_execution.get('created_at'),
                         '2021-06-16T14:48:05.643Z')

    def test_get_latest(self):
        executions = [
            {
                'id': 'a9b18e4d-f181-4fe0-89d5-a450330c2fff',
                'created_at': '2021-06-17T10:26:18.304Z',
                'workflow_id': 'install',
                'deployment_id': 'BreakpointTestCase',
                'status_display': 'completed',
                'created_by': 'admin'
            },
            {
                'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
                'created_at': '2021-06-17T10:23:26.975Z',
                'parameters': {
                    'node_ids': None,
                    'node_instance_ids': ['BreakpointTestCase_123'],
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
                    'node_instance_ids': ['BreakpointTestCase_123'],
                    'permanent': True,
                    'break_on_install': False
                },
                'workflow_id': 'set_breakpoint_state',
                'status_display': 'completed',
                'created_by': 'admin'
            }
        ]

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        valid_execution = \
            breakpoint_executions.get_latest_execution(executions)

        self.assertEqual(valid_execution.get('created_at'),
                         '2021-06-17T10:23:26.975Z')

    def test_node_related(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': ['BreakpointTestCase'],
                'node_instance_ids': None,
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_node_related(executions)

        self.assertTrue(result)

    def test_node_instance_related(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': None,
                'node_instance_ids': ['BreakpointTestCase_123'],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_node_related(executions)

        self.assertTrue(result)

    def test_all_breakpoints(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': [],
                'node_instance_ids': [],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_node_related(executions)

        self.assertTrue(result)

    def test_unrelated(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': ['AnotherTestCase'],
                'node_instance_ids': ['AnotherTestCase_123'],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_node_related(executions)

        self.assertFalse(result)

    def test_valid_execution(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': None,
                'node_instance_ids': ['BreakpointTestCase_123'],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_valid_execution(executions)

        self.assertTrue(result)

    def test_invalid_execution_status(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': None,
                'node_instance_ids': ['BreakpointTestCase_123'],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'set_breakpoint_state',
            'status_display': 'cancelled',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_valid_execution(executions)

        self.assertFalse(result)

    def test_invalid_execution_workflow_id(self):
        executions = {
            'id': 'ab7452fc-bdac-41f1-952b-5e1789346ad0',
            'created_at': '2021-06-17T10:23:26.975Z',
            'parameters': {
                'node_ids': None,
                'node_instance_ids': ['BreakpointTestCase_123'],
                'permanent': False,
                'break_on_install': True
            },
            'workflow_id': 'another_workflow',
            'status_display': 'completed',
            'created_by': 'admin'
        }

        breakpoint_executions = BreakpointStateExecutions(
            node_id='BreakpointTestCase',
            instance_id='BreakpointTestCase_123',
            workflow_id='install',
            deployment_id='BreakpointTestCase',
            breakpoint_state_workflow_name='set_breakpoint_state',
            logger=MagicMock())

        result = breakpoint_executions.is_valid_execution(executions)

        self.assertFalse(result)
