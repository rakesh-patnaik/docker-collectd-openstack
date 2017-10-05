#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import dateutil.parser
import dateutil.tz
import requests
import simplejson as json

import collectd_base as base

from collections import defaultdict

INTERVAL = 180


class KeystoneException(Exception):
    pass

class OSClient(object):
    """ Base class for querying the OpenStack API endpoints.

    It uses the Keystone service catalog to discover the API endpoints.
    """
    EXPIRATION_TOKEN_DELTA = datetime.timedelta(0, 30)

    def __init__(self, username, password, tenant, keystone_url, timeout,
                 logger, max_retries):
        self.logger = logger
        self.username = username
        self.password = password
        self.tenant_name = tenant
        self.keystone_url = keystone_url
        self.service_catalog = []
        self.tenant_id = None
        self.timeout = timeout
        self.token = None
        self.valid_until = None
        self.session = requests.Session()
        self.session.mount(
            'http://', requests.adapters.HTTPAdapter(max_retries=max_retries))
        self.session.mount(
            'https://', requests.adapters.HTTPAdapter(max_retries=max_retries))

    def is_valid_token(self):
        now = datetime.datetime.now(tz=dateutil.tz.tzutc())
        return self.token and self.valid_until and self.valid_until > now

    def clear_token(self):
        self.token = None
        self.valid_until = None

    def get_token(self):
        self.clear_token()
        data = json.dumps({
            "auth":
            {
                'tenantName': self.tenant_name,
                'passwordCredentials':
                {
                    'username': self.username,
                    'password': self.password
                }
            }
        })
        self.logger.info("Trying to get token from '%s'" % self.keystone_url)
        r = self.make_request('post',
                              '%s/tokens' % self.keystone_url, data=data,
                              token_required=False)
        if not r:
            raise KeystoneException("Cannot get a valid token from %s" %
                                    self.keystone_url)

        if r.status_code < 200 or r.status_code > 299:
            raise KeystoneException("%s responded with code %d" %
                                    (self.keystone_url, r.status_code))

        data = r.json()
        self.logger.debug("Got response from Keystone: '%s'" % data)
        self.token = data['access']['token']['id']
        self.tenant_id = data['access']['token']['tenant']['id']
        self.valid_until = dateutil.parser.parse(
            data['access']['token']['expires']) - self.EXPIRATION_TOKEN_DELTA
        self.service_catalog = []
        for item in data['access']['serviceCatalog']:
            endpoint = item['endpoints'][0]
            if 'internalURL' not in endpoint and 'publicURL' not in endpoint:
                self.logger.warning(
                    "Service '{}' skipped because no URL can be found".format(
                        item['name']))
                continue
            self.service_catalog.append({
                'name': item['name'],
                'region': endpoint['region'],
                'service_type': item['type'],
                'url': endpoint.get('internalURL', endpoint.get('publicURL')),
                'admin_url': endpoint['adminURL'],
            })

        self.logger.debug("Got token '%s'" % self.token)
        return self.token

    def make_request(self, verb, url, data=None, token_required=True,
                     params=None):
        kwargs = {
            'url': url,
            'timeout': self.timeout,
            'headers': {'Content-type': 'application/json'}
        }
        if token_required and not self.is_valid_token() and \
           not self.get_token():
            self.logger.error("Aborting request, no valid token")
            return
        elif token_required:
            kwargs['headers']['X-Auth-Token'] = self.token

        if data is not None:
            kwargs['data'] = data

        if params is not None:
            kwargs['params'] = params

        func = getattr(self.session, verb.lower())

        try:
            r = func(**kwargs)
        except Exception as e:
            self.logger.error("Got exception for '%s': '%s'" %
                              (kwargs['url'], e))
            return

        self.logger.info("%s responded with status code %d" %
                         (kwargs['url'], r.status_code))
        if r.status_code == 401:
            # Clear token in case it is revoked or invalid
            self.clear_token()

        return r


class CollectdPlugin(base.Base):

    def __init__(self, *args, **kwargs):
        super(CollectdPlugin, self).__init__(*args, **kwargs)
        self.timeout = 20
        self.max_retries = 2
        self.os_client = None
        self.extra_config = {}
        self._threads = {}
        self.pagination_limit = None
        self._last_run = None
        self.changes_since = False

    def _build_url(self, service, resource):
        s = (self.get_service(service) or {})
        url = s.get('url')
        # v3 API must be used in order to obtain tenants in multi-domain envs
        if service == 'keystone' and (resource in ['projects',
                                                   'users', 'roles']):
            url = url.replace('v2.0', 'v3')

        if url:
            if url[-1] != '/':
                url += '/'
            url = "%s%s" % (url, resource)
        else:
            self.logger.error("Service '%s' not found in catalog" % service)
        return url

    def raw_get(self, url, token_required=False):
        return self.os_client.make_request('get', url,
                                           token_required=token_required)

    def get(self, service, resource, params=None):
        url = self._build_url(service, resource)
        if not url:
            return
        self.logger.info('GET({}) {}'.format(url, params))
        return self.os_client.make_request('get', url, params=params)

    @property
    def service_catalog(self):
        if not self.os_client.service_catalog:
            # In case the service catalog is empty (eg Keystone was down when
            # collectd started), we should try to get a new token
            self.os_client.get_token()
        return self.os_client.service_catalog

    def get_service(self, service_name):
        return next((x for x in self.service_catalog
                    if x['name'] == service_name), None)

    def config_callback(self, config):
        super(CollectdPlugin, self).config_callback(config)
        for node in config.children:
            if node.key == 'Username':
                username = node.values[0]
            elif node.key == 'Password':
                password = node.values[0]
            elif node.key == 'Tenant':
                tenant_name = node.values[0]
            elif node.key == 'KeystoneUrl':
                keystone_url = node.values[0]
            elif node.key == 'PaginationLimit':
                self.pagination_limit = int(node.values[0])

        self.os_client = OSClient(username, password, tenant_name,
                                  keystone_url, self.timeout, self.logger,
                                  self.max_retries)
