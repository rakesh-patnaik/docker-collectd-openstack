#!/usr/bin/env bash

set -e

envtpl /etc/collectd/collectd.conf.tpl

/usr/bin/python /usr/lib/collectd/python-lib/exporter.py &
/usr/share/pushgateway-0.4.0.linux-amd64/pushgateway -web.listen-address "localhost:9103" &
exec /usr/sbin/collectd -f
