# Third party imports
from cloudify.decorators import operation
from cloudify.manager import get_rest_client
from cloudify.exceptions import NonRecoverableError, OperationRetry
from itertools import dropwhile

# Local imports
from . import get_desired_value

BREAKPOINT_WORKFLOW_NAME = 'set_breakpoint_state'
BREAK_MSG = 'Breakpoint active. An allowed user must deactivate ' \
               'this breakpoint using the Set Breakpoint State ' \
               'workflow to continue.'


def is_node_related(node_id, instance_id, execution):
    return node_id in (execution.get('parameters').get('node_ids') or []) \
           or instance_id in \
           (execution.get('parameters').get('node_instance_ids') or []) \
           or execution.get('parameters').get('all_breakpoints')


def is_valid_execution(latest_execution):
    return latest_execution.get('workflow_id') == BREAKPOINT_WORKFLOW_NAME \
           and latest_execution.get('status_display') == 'completed'


def get_latest_execution(ctx, node_id, instance_id, executions):
    drop_restarts = dropwhile(
            lambda x: x.get('deployment_id') == ctx.deployment.id
            and x.get('workflow_id') == ctx.workflow_id,
            executions[::-1])  # reversing executions
    try:
        latest_execution = next(drop_restarts)
    except StopIteration:  # when iterator is empty
        return None
    if is_valid_execution(latest_execution) and \
            is_node_related(node_id, instance_id, latest_execution):
        ctx.logger.info('Applying the latest execution: ID {}, '
                        'by {}, at {}.'.format(
                            latest_execution.get('id'),
                            latest_execution.get('created_by'),
                            latest_execution.get('ended_at')))
        return latest_execution


def get_permanent_execution(ctx, node_id, instance_id, executions):
    permanent_executions = filter(
        lambda x: is_valid_execution(x)
        and is_node_related(node_id, instance_id, x)
        and x.get('parameters').get('permanent'),
        executions)
    try:
        *_, valid_execution = permanent_executions
    except ValueError:  # when iterator is empty
        return None
    ctx.logger.info('Applying the permanent execution: ID {}, '
                    'by {}, at {}.'.format(
                        valid_execution.get('id'),
                        valid_execution.get('created_by'),
                        valid_execution.get('ended_at')))
    return valid_execution


def get_valid_execution(ctx, node_id, instance_id):
    client = get_rest_client()
    executions = client.executions.list()
    # TODO (marrowne) sorting desc by date?
    latest_execution = get_latest_execution(ctx, node_id, instance_id, executions)
    if latest_execution:
        return latest_execution
    return get_permanent_execution(ctx, node_id, instance_id, executions)


@operation
def start(ctx, **kwargs):
    break_error = NonRecoverableError(BREAK_MSG)

    default_break_on_start = \
        get_desired_value(
            'default_break_on_start',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))
    active_breakpoint = get_valid_execution(ctx,
                                            ctx.node.id,
                                            ctx.instance.id)
    if not active_breakpoint and default_break_on_start:
        raise break_error
    if active_breakpoint \
            and active_breakpoint.get('parameters').get('break_on_start'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def stop(ctx, **kwargs):
    break_error = OperationRetry(BREAK_MSG)

    default_break_on_stop = \
        get_desired_value(
            'default_break_on_stop',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))

    active_breakpoint = get_valid_execution(ctx,
                                            ctx.node.id,
                                            ctx.instance.id)
    if not active_breakpoint and default_break_on_stop:
        raise break_error
    if active_breakpoint and \
            active_breakpoint.get('parameters').get('break_on_stop'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def check(ctx, **kwargs):
    execution_creator_username = ctx.execution_creator_username
    if execution_creator_username == 'admin':
        ctx.logger.info('admin is authorized')
        return
    if execution_creator_username in \
            ctx.node.properties.get('authorization').get('users'):
        ctx.logger.info('{} is authorized.'
                        .format(execution_creator_username))
        return
    raise NonRecoverableError('{} is not authorized.'
                              .format(execution_creator_username))
