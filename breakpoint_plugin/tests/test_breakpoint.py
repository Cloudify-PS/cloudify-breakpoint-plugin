# Third party imports
from unittest.mock import patch, MagicMock

# Local imports
from base import BreakpointTestBase
from breakpoint_plugin.resources.breakpoint import start, stop
from cloudify.exceptions import NonRecoverableError


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
                    'break_on_start': True,
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
                    'default_break_on_start': True
                },
                'authorization': {
                    'users': [
                        'Alice',
                        'Bob'
                    ]
                }
            },
            ctx_operation_name='cloudify.interfaces.lifecycle.start')

        with self.assertRaises(NonRecoverableError) as err:
            start(self._ctx)
            self.assertEqual(str(err), self.expected_msg)

    def test_start_nonpermanent(self):
        with self.assertRaises(NonRecoverableError) as err:
            start(self._ctx)
            self.assertEqual(str(err), self.expected_msg)

    def test_restart_nonpermanent_open_breakpoint(self):
        self.assertTrue(False, msg='Not Implemented Yet')

    def test_nonpermanent_open_breakpoint(self):
        self.assertTrue(False, msg='Not Implemented Yet')

    def test_stop_nonpermanent(self):
        with self.assertRaises(NonRecoverableError) as err:
            stop(self._ctx)
            self.assertEqual(str(err), self.expected_msg)

    def test_default_break_on_start(self):
        with self.assertRaises(NonRecoverableError) as err:
            self.assertEqual(str(err), self.expected_msg)
        self.assertTrue(False, msg='Not Implemented Yet')

    def test_default_break_on_stop(self):
        with self.assertRaises(NonRecoverableError) as err:
            stop(self._ctx)
            self.assertEqual(str(err), self.expected_msg)

#     TODO (marrowne) permanent -> non_permanent seq, all_breakpoints==True
