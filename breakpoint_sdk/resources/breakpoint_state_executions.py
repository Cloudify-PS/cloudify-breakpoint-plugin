from cloudify.manager import get_rest_client

from datetime import datetime
from itertools import dropwhile


EXECUTION_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class BreakpointStateExecutions:
    def __init__(self, node_id, instance_id,
                 workflow_name, deployment_id, logger=None):
        self.node_id = node_id
        self.instance_id = instance_id
        self.workflow_name = workflow_name
        self.deployment_id = deployment_id
        self.logger = logger

    def is_node_related(self, execution):
        return self.node_id in \
               (execution.get('parameters').get('node_ids') or []) \
               or self.instance_id in \
               (execution.get('parameters').get('node_instance_ids') or []) \
               or execution.get('parameters').get('all_breakpoints')

    def is_valid_execution(self, execution):
        return execution.get('workflow_id') == self.workflow_name \
               and execution.get('status_display') == 'completed'

    def get_latest_execution(self, executions):
        drop_restarts = dropwhile(
            lambda x: x.get('deployment_id') == self.deployment_id
            and x.get('workflow_id') == self.workflow_name,
            executions)
        try:
            latest_execution = next(drop_restarts)
        except StopIteration:  # when iterator is empty
            return None
        if self.is_valid_execution(latest_execution) and \
                self.is_node_related(latest_execution):
            self.logger.info('Applying the latest execution: ID {}, '
                             'by {}, at {}.'.format(
                                latest_execution.get('id'),
                                latest_execution.get('created_by'),
                                latest_execution.get('created_at')))
            return latest_execution

    def get_permanent_execution(self, executions):
        permanent_executions = filter(
            lambda x: self.is_valid_execution(x)
            and self.is_node_related(x)
            and x.get('parameters').get('permanent'),
            executions)
        try:
            valid_execution = next(permanent_executions)
        except StopIteration:  # when iterator is empty
            return None
        self.logger.info('Applying the permanent execution: ID {}, '
                         'by {}, at {}.'.format(
                            valid_execution.get('id'),
                            valid_execution.get('created_by'),
                            valid_execution.get('created_at')))
        return valid_execution

    def get_valid_execution(self):
        client = get_rest_client()
        executions = client.executions.list()
        executions.sort(
            reverse=True,
            key=lambda x: datetime.strptime(x.get('created_at'),
                                            EXECUTION_TIMESTAMP_FORMAT))
        latest_execution = self.get_latest_execution(executions)
        if latest_execution:
            return latest_execution
        return self.get_permanent_execution(executions)
