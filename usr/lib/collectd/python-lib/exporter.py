#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import re

class RequestHandler(BaseHTTPRequestHandler):
    
  
    def do_POST(self):
        
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        input_json_raw = self.rfile.read(length)
        print input_json_raw
        input_json = json.loads(input_json_raw)
        registry = CollectorRegistry()
               
        for metric in input_json:
            metric_name = metric['plugin']
            if 'plugin_instance' in metric and len(metric['plugin_instance']) > 0:
                metric_name = metric_name + "_" + metric['plugin_instance']
            
            if 'type_instance' in metric and len(metric['type_instance']) > 0:
                metric_name = metric_name + '_' + metric['type_instance']

            if 'type' in metric:
                metric_name = metric_name + '_' + metric['type']
            metric_name = re.sub(r'[^a-zA-Z0-9:_]', '_', metric_name)
            labels = []
            values = []
            if 'meta' in metric:
                keys = metric['meta'].keys()
                for key in keys:
                    labels.append(re.sub(r'[^a-zA-Z0-9:_]', '_', key))
                values = metric['meta'].values()
               
            if 'host' in metric:
                labels.append('instance')
                values.append(metric['host'])
            g = Gauge(metric_name, metric_name, labels, registry=registry)
            g.labels(*values).set(metric['values'][0])
            try:
                push_to_gateway('localhost:9103', job='collectd', registry=registry)
            except Exception as e:
                print str(e)
                print "failed to post to prom gateway {}".format(metric)
            
        self.send_response(200)

def main():
    port = 9102
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()
        
if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = ("Creates an http-server that will echo out any GET or POST parameters\n"
                    "Run:\n\n"
                    "   reflect")
    (options, args) = parser.parse_args()
    
    main()
