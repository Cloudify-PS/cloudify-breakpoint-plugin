# Third party imports
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError, OperationRetry

# Local imports
from . import get_desired_value
from breakpoint_plugin.utils import (
    has_admin_role
)
from breakpoint_sdk.resources.breakpoint_state_executions import (
    BreakpointStateExecutions
)
from breakpoint_plugin.workflows.state import set_breakpoint_state

BREAK_MSG = 'Breakpoint active. An allowed user must deactivate ' \
               'this breakpoint using the Set Breakpoint State ' \
               'workflow to continue.'


@operation
def start(ctx, **kwargs):
    break_error = NonRecoverableError(BREAK_MSG)

    default_break_on_start = \
        get_desired_value(
            'default_break_on_start',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))
    breakpoint_executions = BreakpointStateExecutions(
        node_id=ctx.node.id,
        instance_id=ctx.instance.id,
        workflow_name=set_breakpoint_state.__name__,
        deployment_id=ctx.deployment.id,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
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
    breakpoint_executions = BreakpointStateExecutions(
        node_id=ctx.node.id,
        instance_id=ctx.instance.id,
        workflow_name=set_breakpoint_state.__name__,
        deployment_id=ctx.deployment.id,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
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
    if execution_creator_username in \
            ctx.node.properties.get('authorization').get('users'):
        ctx.logger.info('{} is authorized.'
                        .format(execution_creator_username))
        return
    if has_admin_role(execution_creator_username):
        ctx.logger.info('admin is authorized')
        return
    raise NonRecoverableError('{} is not authorized.'
                              .format(execution_creator_username))
