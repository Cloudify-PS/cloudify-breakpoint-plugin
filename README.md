# cloudify-breakpoint-plugin
#### Breakpoint, Semaphore, confirmed execution, manual intervention

A Cloudify plugin for confirming an execution, which is defined as a stop in workflow execution that needs to be acknowledged by a user (may be any or specific user).

## Usage

### Node type:

cloudify.nodes.breakpoint.**Breakpoint**

The node acting as a breakpoint. 

Properties:
- authorization
    - **users** - list of usernames that can change breakpoint state
- resource_config
    - **default_break_on_install** - initial flag applied in `cloudify.interfaces.lifecycle.start`, used when there was not any execution of _set_breakpoint_state_ workflow that is related to this node (neither the latest execution nor with permanent flag)
    - **default_break_on_uninstall** - initial flag applied in `cloudify.interfaces.lifecycle.delete`, analogous to _default_break_on_install_

Operations:
- `cloudify.interfaces.lifecycle.start`- when _break_on_install_ (or initially _default_break_on_install_) is enabled it raises `NonRecoverableError`; this operation is executed on install (see [Cloudify Built-in Workflows](https://docs.cloudify.co/latest/working_with/workflows/built-in-workflows/))
- `cloudify.interfaces.lifecycle.delete` - when _break_on_uninstall_ (or initially _default_break_on_uninstall_) is enabled it raises `OperationRetry`; this operation is executed on uninstall (see [Cloudify Built-in Workflows](https://docs.cloudify.co/latest/working_with/workflows/built-in-workflows/))
- `cloudify.interfaces.breakpoint.check` - If the user executing the operation is not in the nodes property authorization.users raise `NonRecoverableError`

### Workflow:

**set_breakpoint_state** 

Runs for the node type defined above. Admin user is **always** implicitly the allowed (does not need to be included in the list).

Parameters:

- **node_ids** - list of IDs of `cloudify.nodes.breakpoint.Breakpoint`
- **node_instance_ids** - list of IDs of `cloudify.nodes.breakpoint.Breakpoint` node instance, node ID is used interchangeably
- **break_on_install**  (default: true) - specifies if the breakpoint should stop on `cloudify.interfaces.lifecycle.start` lifecycle operation
- **break_on_uninstall** (default: true) - specifies if the breakpoint should stop on `cloudify.interfaces.lifecycle.delete` lifecycle operation
- **permanent** (default: false) - specifies that this setting of the breakpoints is permanent, if false it will apply only to the next execution


## Runtime properties
There is no runtime properties, authorized users are provided on blueprint upload.

# Requirements

# Examples
A blueprint with breakpoint is located in examples directory.

For other official blueprint examples using this Cloudify plugin, please see [Cloudify Community Blueprints Examples](https://github.com/cloudify-community/blueprint-examples/).
