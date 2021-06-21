from cloudify.manager import get_rest_client


def get_node_instance(node_instance_id):
    """
    Fetches node instance via REST
    :param node_instance_id: ID of node instance
    :return: node instance object
    """
    rest_client = get_rest_client()
    return rest_client.node_instances.get(node_instance_id=node_instance_id)


def has_admin_role(username):
    """
    Gets a role for the username and checks if it has sys_admin role
    :param username: string
    :return: True if user has sys_admin role, otherwise False
    """
    client = get_rest_client()
    role = client.users.get(username).get('role')
    if role == 'sys_admin':
        return True
    return False
