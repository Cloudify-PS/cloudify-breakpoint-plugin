# Third party imports
from cloudify.decorators import workflow
from cloudify.exceptions import NonRecoverableError

# Local imports
from breakpoint_plugin.utils import (
    get_node_instance,
    has_admin_role,
    has_authorized_role
)


def execution_creator_auth(users, roles, tenant, execution_creator_username):
    """
    Raises NonRecoverableError when neither execution_creator_username is
    not in users parameter nor he does not have any of authorized roles
    (defined in roles parameter or sys_admin role).
    :param users: list of allowed usernames
    :param roles: list of allowed tenant roles
    :param tenant: tenant in which deployment exists
    :param execution_creator_username: user which executes the workflow
    """
    if execution_creator_username not in users and \
            not has_admin_role(execution_creator_username) and \
            not has_authorized_role(execution_creator_username, tenant, roles):
        raise NonRecoverableError(
            "User '{}' is not allowed to executed this workflow."
            .format(execution_creator_username))


@workflow
def set_breakpoint_state(node_ids=None,
                         node_instance_ids=None,
                         break_on_install=False,
                         break_on_uninstall=False,
                         permanent=False,
                         ctx=None):
    """
    Runs for`cloudify.nodes.breakpoint.Breakpoint` node type.
    Admin user is always implicitly the allowed.
    :param node_ids: list of IDs of `cloudify.nodes.breakpoint.Breakpoint`
    :param node_instance_ids: list of IDs of
           `cloudify.nodes.breakpoint.Breakpoint` node instance, node ID
           is used interchangeably
    :param break_on_install: specifies if the breakpoint should stop on
           `cloudify.interfaces.lifecycle.start` lifecycle operation
    :param break_on_uninstall: specifies if the breakpoint should stop on
           `cloudify.interfaces.lifecycle.delete` lifecycle operation
    :param permanent: specifies that this setting of the breakpoints is
           permanent, if false it will apply only to the next execution
    :param ctx: Cloudify context
    :return: returns True on successful execution
    """
    execution_creator_username = ctx.execution_creator_username
    tenant = ctx.tenant_name
    _node_ids = node_ids or []
    _node_instance_ids = node_instance_ids or []
    if not isinstance(_node_ids, list) \
       or not isinstance(_node_instance_ids, list):
        raise NonRecoverableError(
            'node_ids/node_instance_ids parameter should be a list!')
    for node_id in _node_ids:
        node = ctx.get_node(node_id)
        users = node.properties.get('authorization').get('users')
        roles = node.properties.get('authorization').get('roles', [])
        execution_creator_auth(
            users, roles, tenant, execution_creator_username)
    for node_instance_id in _node_instance_ids:
        node_instance = get_node_instance(node_instance_id)
        node = ctx.get_node(node_instance.node_id)
        users = node.properties.get('authorization').get('users')
        roles = node.properties.get('authorization').get('roles', [])
        execution_creator_auth(
            users, roles, tenant, execution_creator_username)
    return True
