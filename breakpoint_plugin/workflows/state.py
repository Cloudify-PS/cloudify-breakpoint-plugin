# Third party imports
from cloudify.decorators import workflow
from cloudify.exceptions import NonRecoverableError

# Local imports
from breakpoint_plugin.utils import (
    get_node_instance,
    has_admin_role
)


def execution_creator_auth(users, execution_creator_username):
    """
    Raises NonRecoverableError when neither execution_creator_username is
    not in users parameter nor he does not have sys_admin role.
    :param users: list of allowed usernames
    :param execution_creator_username: user which executes the workflow
    """
    if execution_creator_username not in users and \
            not has_admin_role(execution_creator_username):
        raise NonRecoverableError(
            "User '{}' is not allowed to executed this workflow."
            .format(execution_creator_username))


@workflow
def set_breakpoint_state(node_ids=None,
                         node_instance_ids=None,
                         break_on_start=True,
                         break_on_stop=True,
                         permanent=False,
                         ctx=None):
    """
    Runs for`cloudify.nodes.breakpoint.Breakpoint` node type.
    Admin user is always implicitly the allowed.
    :param node_ids: list of IDs of `cloudify.nodes.breakpoint.Breakpoint`
    :param node_instance_ids: list of IDs of
           `cloudify.nodes.breakpoint.Breakpoint` node instance, node ID
           is used interchangeably
    :param break_on_start: specifies if the breakpoint should stop on
           `cloudify.interfaces.lifecycle.start` lifecycle operation
    :param break_on_stop: specifies if the breakpoint should stop on
           `cloudify.interfaces.lifecycle.stop` lifecycle operation
    :param permanent: specifies that this setting of the breakpoints is
           permanent, if false it will apply only to the next execution
    :param ctx: Cloudify context
    :return: returns True on successful execution
    """
    execution_creator_username = ctx.execution_creator_username
    _node_ids = node_ids or []
    _node_instance_ids = node_instance_ids or []
    for node_id in _node_ids:
        node = ctx.get_node(node_id)
        users = node.properties.get('authorization').get('users')
        execution_creator_auth(users, execution_creator_username)
    for node_instance_id in _node_instance_ids:
        node_instance = get_node_instance(node_instance_id)
        node = ctx.get_node(node_instance.node_id)
        users = node.properties.get('authorization').get('users')
        execution_creator_auth(users, execution_creator_username)
    return True
