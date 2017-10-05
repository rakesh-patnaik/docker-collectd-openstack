#!/usr/bin/env bash

set -e

envtpl /etc/collectd/collectd.conf.tpl

/usr/sbin/collectd -f
