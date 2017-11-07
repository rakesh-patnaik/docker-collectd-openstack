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

from functools import wraps
import json
import signal
import subprocess
import threading
import time
import traceback
import os

INTERVAL = 10


class CheckException(Exception):
    pass


class Base(object):
    """Base class for writing Python plugins."""

    FAIL = 0
    OK = 1
    UNKNOWN = 2

    MAX_IDENTIFIER_LENGTH = 63

    def __init__(self, collectd, service_name=None, local_check=True):
        self.debug = False
        self.timeout = 5
        self.max_retries = 3
        self.logger = collectd
        self.collectd = collectd
        self.plugin = None
        self.plugin_instance = ''
        self.service_name = service_name
        self.local_check = local_check
        self.polling_interval = 60

    def config_callback(self, conf):
        for node in conf.children:
            if node.key == "Debug":
                if node.values[0] in ['True', 'true']:
                    self.debug = True
            elif node.key == "Timeout":
                self.timeout = int(node.values[0])
            elif node.key == 'MaxRetries':
                self.max_retries = int(node.values[0])
            elif node.key == 'PollingInterval':
                self.polling_interval = int(node.values[0])

        self.polling_interval = int(os.getenv('OS_POLLING_INTERVAL', self.polling_interval))
        self.timeout = int(os.getenv('OS_TIMEOUT', self.timeout))
        
    def read_callback(self):
        try:
            for metric in self.itermetrics():
                self.dispatch_metric(metric)
        except CheckException as e:
            msg = '{}: {}'.format(self.plugin, e)
            self.logger.warning(msg)
            self.dispatch_check_metric(self.FAIL, msg)
        except Exception as e:
            msg = '{}: Failed to get metrics: {}'.format(self.plugin, e)
            self.logger.error('{}: {}'.format(msg, traceback.format_exc()))
            self.dispatch_check_metric(self.FAIL, msg)
        else:
            self.dispatch_check_metric(self.OK)

    def itermetrics(self):
        """Iterate over the collected metrics

        This class must be implemented by the subclass and should yield dict
        objects that represent the collected values. Each dict has 6 keys:
            - 'values', a scalar number or a list of numbers if the type
            defines several datasources.
            - 'type_instance' (optional)
            - 'plugin_instance' (optional)
            - 'type' (optional, default='gauge')
            - 'meta' (optional)
            - 'hostname' (optional)

        For example:

            {'type_instance':'foo', 'values': 1}
            {'type_instance':'bar', 'type': 'DERIVE', 'values': 1}
            {'type_instance':'bar', 'type': 'DERIVE', 'values': 1,
                'meta':   {'tagA': 'valA'}}
            {'type': 'dropped_bytes', 'values': [1,2]}
        """
        raise NotImplemented("Must be implemented by the subclass!")

    def dispatch_check_metric(self, check, failure=None):
        metric = {
            'plugin_instance': self.service_name or self.plugin,
            'meta': {'service_check': self.service_name or self.plugin,
                     'local_check': self.local_check},
            'values': check,
        }

        if failure is not None:
            metric['meta']['failure'] = failure

        self.dispatch_metric(metric)

    def dispatch_metric(self, metric):
        values = metric['values']
        if not isinstance(values, list) and not isinstance(values, tuple):
            values = (values,)

        type_instance = str(metric.get('type_instance', ''))
        if len(type_instance) > self.MAX_IDENTIFIER_LENGTH:
            self.logger.warning(
                '%s: Identifier "%s..." too long (length: %d, max limit: %d)' %
                (self.plugin, type_instance[:24], len(type_instance),
                 self.MAX_IDENTIFIER_LENGTH))

        plugin_instance = metric.get('plugin_instance', self.plugin_instance)
        v = self.collectd.Values(
            plugin=self.plugin,
            host=metric.get('hostname', ''),
            type=metric.get('type', 'gauge'),
            plugin_instance=plugin_instance,
            type_instance=type_instance,
            values=values,
            meta=metric.get('meta', {'0': True})
        )
        v.dispatch()

