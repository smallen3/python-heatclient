# Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from heatclient.common import utils

from heatclient.v1 import resources

from mox3 import mox
import testtools


class ResourceManagerTest(testtools.TestCase):

    def setUp(self):
        super(ResourceManagerTest, self).setUp()
        self.m = mox.Mox()
        self.addCleanup(self.m.UnsetStubs)

    def _base_test(self, expect, key):

        class FakeAPI(object):
            """Fake API and ensure request url is correct."""

            def get(self, *args, **kwargs):
                assert ('GET', args[0]) == expect

            def json_request(self, *args, **kwargs):
                assert args == expect
                ret = key and {key: []} or {}
                return {}, {key: ret}

            def raw_request(self, *args, **kwargs):
                assert args == expect
                return {}

            def head(self, url, **kwargs):
                return self.json_request("HEAD", url, **kwargs)

            def post(self, url, **kwargs):
                return self.json_request("POST", url, **kwargs)

            def put(self, url, **kwargs):
                return self.json_request("PUT", url, **kwargs)

            def delete(self, url, **kwargs):
                return self.raw_request("DELETE", url, **kwargs)

            def patch(self, url, **kwargs):
                return self.json_request("PATCH", url, **kwargs)

        manager = resources.ResourceManager(FakeAPI())
        self.m.StubOutWithMock(manager, '_resolve_stack_id')
        self.m.StubOutWithMock(utils, 'get_response_body')
        utils.get_response_body(mox.IgnoreArg()).AndReturn(
            {key: key and {key: []} or {}})
        manager._resolve_stack_id('teststack').AndReturn('teststack/abcd1234')
        self.m.ReplayAll()

        return manager

    def test_get(self):
        fields = {'stack_id': 'teststack',
                  'resource_name': 'testresource'}
        expect = ('GET',
                  '/stacks/teststack%2Fabcd1234/resources'
                  '/testresource')
        key = 'resource'

        manager = self._base_test(expect, key)
        manager.get(**fields)
        self.m.VerifyAll()

    def test_get_with_unicode_resource_name(self):
        fields = {'stack_id': 'teststack',
                  'resource_name': u'\u5de5\u4f5c'}
        expect = ('GET',
                  '/stacks/teststack%2Fabcd1234/resources'
                  '/%E5%B7%A5%E4%BD%9C')
        key = 'resource'

        manager = self._base_test(expect, key)
        manager.get(**fields)
        self.m.VerifyAll()

    def test_list(self):
        fields = {'stack_id': 'teststack'}
        expect = ('/stacks/teststack/resources')
        key = 'resources'

        class FakeResponse(object):
            def json(self):
                return {key: {}}

        class FakeClient(object):
            def get(self, *args, **kwargs):
                assert args[0] == expect
                return FakeResponse()

        manager = resources.ResourceManager(FakeClient())
        manager.list(**fields)

    def test_list_nested(self):
        fields = {'stack_id': 'teststack', 'nested_depth': '99'}
        expect = ('/stacks/teststack/resources?nested_depth=99')
        key = 'resources'

        class FakeResponse(object):
            def json(self):
                return {key: {}}

        class FakeClient(object):
            def get(self, *args, **kwargs):
                assert args[0] == expect
                return FakeResponse()

        manager = resources.ResourceManager(FakeClient())
        manager.list(**fields)

    def test_metadata(self):
        fields = {'stack_id': 'teststack',
                  'resource_name': 'testresource'}
        expect = ('GET',
                  '/stacks/teststack%2Fabcd1234/resources'
                  '/testresource/metadata')
        key = 'metadata'

        manager = self._base_test(expect, key)
        manager.metadata(**fields)
        self.m.VerifyAll()

    def test_generate_template(self):
        fields = {'resource_name': 'testresource'}
        expect = ('GET', '/resource_types/testresource/template')
        key = None

        class FakeAPI(object):
            """Fake API and ensure request url is correct."""

            def get(self, *args, **kwargs):
                assert ('GET', args[0]) == expect

            def json_request(self, *args, **kwargs):
                assert args == expect
                ret = key and {key: []} or {}
                return {}, {key: ret}

        manager = resources.ResourceManager(FakeAPI())
        self.m.StubOutWithMock(utils, 'get_response_body')
        utils.get_response_body(mox.IgnoreArg()).AndReturn(
            {key: key and {key: []} or {}})
        self.m.ReplayAll()

        manager.generate_template(**fields)
        self.m.VerifyAll()

    def test_signal(self):
        fields = {'stack_id': 'teststack',
                  'resource_name': 'testresource',
                  'data': 'Some content'}
        expect = ('POST',
                  '/stacks/teststack%2Fabcd1234/resources'
                  '/testresource/signal')
        key = 'signal'

        manager = self._base_test(expect, key)
        manager.signal(**fields)
        self.m.VerifyAll()
