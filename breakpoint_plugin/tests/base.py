# Standard imports
import copy
import unittest

# Third party imports
from cloudify.manager import DirtyTrackingDict
from cloudify.state import current_ctx
from cloudify.mocks import (
    MockCloudifyContext,
    MockNodeContext,
)


class CustomMockCloudifyContext(MockCloudifyContext):
    def __init__(self, execution_creator_username=None, *args, **kwargs):
        super(CustomMockCloudifyContext, self).__init__(*args, **kwargs)
        self._execution_creator_username = \
            execution_creator_username or 'admin'

    @property
    def workflow_id(self):
        return 'workflow'

    @property
    def execution_creator_username(self):
        return self._execution_creator_username

    @property
    def tenant_name(self):
        return 'default_tenant'


class CustomMockNodeContext(MockNodeContext):
    def __init__(self,
                 id=None,
                 properties=None,
                 type=None,
                 type_hierarchy=['cloudify.nodes.Root']):
        super(CustomMockNodeContext, self).__init__(id=id,
                                                    properties=properties)
        self._type = type
        self._type_hierarchy = type_hierarchy

    @property
    def type(self):
        return self._type

    @property
    def type_hierarchy(self):
        return self._type_hierarchy


class BreakpointTestBase(unittest.TestCase):
    def _to_DirtyTrackingDict(self, origin):
        if not origin:
            origin = {}
        dirty_dict = DirtyTrackingDict()
        for k in origin:
            dirty_dict[k] = copy.deepcopy(origin[k])
        return dirty_dict

    @property
    def resource_config(self):
        return {
            'name': 'foo',
            'description': 'foo'
        }

    @property
    def node_properties(self):
        return {
            'resource_config': self.resource_config
        }

    @property
    def runtime_properties(self):
        return {}

    def get_mock_ctx(self,
                     test_name,
                     test_properties={},
                     test_runtime_properties={},
                     test_relationships=None,
                     type_hierarchy=['cloudify.nodes.Root'],
                     node_type='cloudify.nodes.Root',
                     test_source=None,
                     test_target=None,
                     ctx_operation_name=None,
                     ctx_execution_creator_username=None):

        operation_ctx = {
            'retry_number': 0, 'name': 'cloudify.interfaces.lifecycle.'
        } if not ctx_operation_name else {
            'retry_number': 0, 'name': ctx_operation_name
        }

        prop = copy.deepcopy(test_properties or self.node_properties)
        ctx = CustomMockCloudifyContext(
            node_id=test_name,
            node_name=test_name,
            deployment_id=test_name,
            properties=prop,
            runtime_properties=self._to_DirtyTrackingDict(
                test_runtime_properties or self.runtime_properties
            ),
            source=test_source,
            target=test_target,
            relationships=test_relationships,
            operation=operation_ctx,
            execution_creator_username=ctx_execution_creator_username
        )

        ctx._node = CustomMockNodeContext(test_name, prop)
        # In order to set type for the node, we need to set it using _node
        # instance
        ctx._node._type = node_type
        ctx._node._type_hierarchy = type_hierarchy
        return ctx

    def _prepare_context_for_operation(self,
                                       test_name,
                                       test_properties={},
                                       test_runtime_properties={},
                                       test_relationships=None,
                                       type_hierarchy=['cloudify.nodes.Root'],
                                       test_source=None,
                                       test_target=None,
                                       ctx_operation_name=None,
                                       ctx_execution_creator_username=None):
        self._ctx = self.get_mock_ctx(
            test_name=test_name,
            test_properties=test_properties,
            test_runtime_properties=test_runtime_properties,
            test_relationships=test_relationships,
            type_hierarchy=type_hierarchy,
            test_source=test_source,
            test_target=test_target,
            ctx_operation_name=ctx_operation_name,
            ctx_execution_creator_username=ctx_execution_creator_username)
        current_ctx.set(self._ctx)
