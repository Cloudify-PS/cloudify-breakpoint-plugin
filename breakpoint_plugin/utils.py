from cloudify.manager import get_rest_client


def get_node_instance(node_instance_id):
    rest_client = get_rest_client()
    return rest_client.node_instances.get(node_instance_id=node_instance_id)


def has_admin_role(execution_creator_username):
    client = get_rest_client()
    role = client.users.get(execution_creator_username).get('role')
    if role == 'sys_admin':
        return True
    return False
