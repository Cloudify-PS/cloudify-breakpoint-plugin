

def get_desired_value(key,
                      args,
                      instance_attr,
                      node_prop):

    return args.get(key) \
        or instance_attr.get(key) \
        or node_prop.get(key)
