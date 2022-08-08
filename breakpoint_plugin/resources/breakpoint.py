# Third party imports
from cloudify import context
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError, OperationRetry

# Local imports
from . import get_desired_value
from breakpoint_plugin.utils import (
    has_admin_role,
    has_authorized_role
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
    When break_on_install (or initially default_break_on_install) is enabled
    it raises OperationRetry.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
    break_error = OperationRetry(BREAK_MSG)
    node = None
    instance = None
    if ctx.type == context.RELATIONSHIP_INSTANCE:
        node = ctx.target.node
        instance = ctx.target.instance
    else:
        node = ctx.node
        instance = ctx.instance

    default_break_on_install = \
        get_desired_value(
            'default_break_on_install',
            args=kwargs,
            instance_attr={},
            node_prop=node.properties.get('resource_config'))
    breakpoint_executions = BreakpointStateExecutions(
        node_id=node.id,
        instance_id=instance.id,
        workflow_id=ctx.workflow_id,
        deployment_id=ctx.deployment.id,
        breakpoint_state_workflow_name=set_breakpoint_state.__name__,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
    if not active_breakpoint:
        ctx.logger.debug('Applying default_break_on_install ({}).'
                         .format(default_break_on_install))
        if default_break_on_install:
            raise break_error
    if active_breakpoint \
            and active_breakpoint.get('parameters').get('break_on_install'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def delete(ctx, **kwargs):
    """
    When break_on_uninstall (or initially default_break_on_uninstall)
    is enabled it raises OperationRetry.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
    break_error = OperationRetry(BREAK_MSG)
    node = None
    instance = None
    if ctx.type == context.RELATIONSHIP_INSTANCE:
        node = ctx.target.node
        instance = ctx.target.instance
    else:
        node = ctx.node
        instance = ctx.instance

    default_break_on_uninstall = \
        get_desired_value(
            'default_break_on_uninstall',
            args=kwargs,
            instance_attr={},
            node_prop=node.properties.get('resource_config'))
    breakpoint_executions = BreakpointStateExecutions(
        node_id=node.id,
        instance_id=instance.id,
        workflow_id=ctx.workflow_id,
        deployment_id=ctx.deployment.id,
        breakpoint_state_workflow_name=set_breakpoint_state.__name__,
        logger=ctx.logger)
    active_breakpoint = breakpoint_executions.get_valid_execution()
    if not active_breakpoint:
        ctx.logger.debug('Applying default_break_on_uninstall ({}).'
                         .format(default_break_on_uninstall))
        if default_break_on_uninstall:
            raise break_error
    if active_breakpoint and \
            active_breakpoint.get('parameters').get('break_on_uninstall'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('The breakpoint is inactive.')


@operation
def check(ctx, **kwargs):
    """
    If the user executing the operation is not in the nodes property
    authorization.users or his role is not in the nodes property
    authorization.roles it raises NonRecoverableError.
    :param ctx: Cloudify context
    :param kwargs: The parameters given from the user
    """
    execution_creator_username = ctx.execution_creator_username
    if execution_creator_username in \
            ctx.node.properties.get('authorization').get('users') or \
            has_authorized_role(
                execution_creator_username,
                ctx.tenant_name,
                ctx.node.properties.get('authorization').get('roles', [])):
        ctx.logger.info('{} is authorized.'
                        .format(execution_creator_username))
        return
    if has_admin_role(execution_creator_username):
        ctx.logger.info('admin is authorized')
        return
    raise NonRecoverableError('{} is not authorized.'
                              .format(execution_creator_username))
