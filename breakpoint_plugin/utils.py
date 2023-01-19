from cloudify.manager import get_rest_client
from cloudify.workflows import ctx


def get_node_instance(node_instance_id):
    """
    Fetches node instance via REST
    :param node_instance_id: ID of node instance
    :return: node instance object
    """
    rest_client = get_rest_client()
    return rest_client.node_instances.get(node_instance_id=node_instance_id)


def has_admin_role():
    """
    Gets a role for the username and checks if it has sys_admin role
    :param username: string
    :return: True if user has sys_admin role, otherwise False
    """
    client = get_rest_client()
    role = None
    try:
        role = client.users.get_self().get('role')
    finally:
        if role == 'sys_admin':
            return True
        return False


def has_authorized_role(tenant, authorized_roles):
    """
    Gets a tenant role for the username and checks if it is authorized
    :param username: string
    :return: True if user has authorized tenant role, otherwise False
    """
    client = get_rest_client()
    user_roles = None
    try:
        user_roles = client.users.get_self(_get_data=True).get(
            'tenants').get(tenant).get('roles')
    finally:
        if set(user_roles).intersection(authorized_roles):
            return True
        return False


def is_authorized_group_member(user_name, user_groups=None):
    """
        Check if user is members any of user_groups
        :param user_groups: list of user groups
        :param user_name: name of user
    """
    if not user_groups:
        return False
    client = get_rest_client()
    for user_group in user_groups:
        members = client.user_groups.get(user_group, _get_data=True).users
        ctx.logger.info(f'Members of {user_group} group: {members}')
        if user_name in members:
            ctx.logger.info(f'User {user_name} is member of {user_group}')
            return True
    return False
