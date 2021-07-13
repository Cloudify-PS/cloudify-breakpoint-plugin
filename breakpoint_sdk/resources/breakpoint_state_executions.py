from cloudify.manager import get_rest_client

from itertools import dropwhile


PAGINATION_SIZE = 50


class BreakpointStateExecutions:
    def __init__(self, node_id, instance_id, workflow_id, deployment_id,
                 breakpoint_state_workflow_name, logger=None):
        self.node_id = node_id
        self.instance_id = instance_id
        self.workflow_id = workflow_id
        self.deployment_id = deployment_id
        self.breakpoint_state_workflow_name = breakpoint_state_workflow_name
        self.logger = logger

    def is_node_related(self, execution):
        node_ids = execution.get('parameters').get('node_ids') or []
        node_instance_ids = \
            execution.get('parameters').get('node_instance_ids') or []
        # apply to all nodes if both node_ids and node_instance_ids are empty
        if not (node_ids and node_instance_ids):
            return True
        return self.node_id in node_ids \
            or self.instance_id in node_instance_ids

    def is_valid_execution(self, execution):
        return execution.get('workflow_id') \
               == self.breakpoint_state_workflow_name \
               and execution.get('status_display') \
               == 'completed'

    def get_latest_execution(self, executions):
        drop_restarts = dropwhile(
            lambda x: x.get('deployment_id') == self.deployment_id
            and x.get('workflow_id') == self.workflow_id,
            executions)
        try:
            latest_execution = next(drop_restarts)
        except StopIteration:  # when iterator is empty
            return None
        if self.is_valid_execution(latest_execution) and \
                self.is_node_related(latest_execution):
            self.logger.debug('Applying the latest execution: ID {}, '
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
        self.logger.debug('Applying the permanent execution: ID {}, '
                          'by {}, at {}.'.format(
                            valid_execution.get('id'),
                            valid_execution.get('created_by'),
                            valid_execution.get('created_at')))
        return valid_execution

    def get_valid_execution(self):
        offset = 0
        client = get_rest_client()
        while True:
            executions = client.executions.list(
                sort='started_at',
                is_descending=True,
                _size=PAGINATION_SIZE,
                _offset=offset)
            if len(executions) == 0:
                return None
            latest_execution = self.get_latest_execution(executions)
            if latest_execution:
                return latest_execution
            permanent_execution = self.get_permanent_execution(executions)
            if permanent_execution:
                return permanent_execution

            offset += PAGINATION_SIZE
