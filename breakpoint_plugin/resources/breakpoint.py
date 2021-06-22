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
    """
    When break_on_start (or initially default_break_on_start) is enabled
    it raises NonRecoverableError.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
    break_error = NonRecoverableError(BREAK_MSG)

    default_break_on_start = \
        get_desired_value(
            'default_break_on_start',
            args=kwargs,
            instance_attr={},
            node_prop=ctx.node.properties.get('resource_config'))
    breakpoint_executions = BreakpointStateExecutions(
        node_id=ctx.node.id,
        instance_id=ctx.instance.id,
        workflow_id=ctx.workflow_id,
        deployment_id=ctx.deployment.id,
        breakpoint_state_workflow_name=set_breakpoint_state.__name__,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
    if not active_breakpoint:
        ctx.logger.debug('Applying default_break_on_start ({}).'
                         .format(default_break_on_start))
        if default_break_on_start:
            raise break_error
    if active_breakpoint \
            and active_breakpoint.get('parameters').get('break_on_start'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def stop(ctx, **kwargs):
    """
    When break_on_stop (or initially default_break_on_stop) is enabled
    it raises OperationRetry.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
    break_error = OperationRetry(BREAK_MSG)

    default_break_on_stop = \
        get_desired_value(
            'default_break_on_stop',
            args=kwargs,
            instance_attr={},
            node_prop=ctx.node.properties.get('resource_config'))
    breakpoint_executions = BreakpointStateExecutions(
        node_id=ctx.node.id,
        instance_id=ctx.instance.id,
        workflow_id=ctx.workflow_id,
        deployment_id=ctx.deployment.id,
        breakpoint_state_workflow_name=set_breakpoint_state.__name__,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
    if not active_breakpoint:
        ctx.logger.debug('Applying default_break_on_stop ({}).'
                         .format(default_break_on_stop))
        if default_break_on_stop:
            raise break_error
    if active_breakpoint and \
            active_breakpoint.get('parameters').get('break_on_stop'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def check(ctx, **kwargs):
    """
    If the user executing the operation is not in the nodes property
    authorization.users it raises NonRecoverableError.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
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
