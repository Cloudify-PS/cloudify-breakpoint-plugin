# Third party imports
from cloudify.decorators import operation
from cloudify.manager import get_rest_client
from cloudify.exceptions import NonRecoverableError

# Local imports
from . import get_desired_value

BREAKPOINT_WORKFLOW_NAME = 'set_breakpoint_state'
BREAK_MSG = 'Breakpoint active. An allowed user must deactivate ' \
               'this breakpoint using the Set Breakpoint State ' \
               'workflow to continue.'


def get_active_breakpoint(ctx, node_id, instance_id):
    client = get_rest_client()
    executions = client.executions.list()
    # TODO (marrowne) sorting desc by date?
    bp_opens = list(
        filter(
            lambda x:
            x.get('workflow_id') == BREAKPOINT_WORKFLOW_NAME
            and x.get('status_display') == 'completed',
            executions))
    matching_opens = list(
        filter(
            lambda x:
            node_id in (x.get('parameters').get('node_ids') or [])
            or instance_id in (x.get('parameters').get('node_instance_ids') or [])
            or x.get('parameters').get('all_breakpoints'),
            bp_opens))
    permanent_opens = list(filter(lambda x: x.get('parameters').get('permanent'), matching_opens))
    if permanent_opens:
        # TODO (marrowne) info incorrect when break_on_X==True
        ctx.logger.info('Permanent permission from execution ID {}, by {}, at {}.'
                        .format(permanent_opens[-1].get('id'),
                                permanent_opens[-1].get('created_by'),
                                permanent_opens[-1].get('ended_at')))
        return permanent_opens[-1]


@operation
def start(ctx, **kwargs):
    break_error = NonRecoverableError(BREAK_MSG)

    default_break_on_start = \
        get_desired_value(
            'default_break_on_start',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))
    active_breakpoint = get_active_breakpoint(ctx,
                                              ctx.node.id,
                                              ctx.instance.id)
# TODO (marrowne) apply break_on_start
    if not active_breakpoint:
        if default_break_on_start:
            raise break_error
    if active_breakpoint.get('parameters').get('break_on_start'):
        raise break_error

    # No error raised so continue execution without any interruption
    ctx.logger.info('Breakpoint is inactive.')


@operation
def stop(ctx, **kwargs):
    default_break_on_stop = \
        get_desired_value(
            'default_break_on_stop',
            kwargs,
            ctx.instance.runtime_properties,
            ctx.node.properties.get('resource_config'))
