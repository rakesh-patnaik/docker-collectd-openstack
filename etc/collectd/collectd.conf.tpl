TypesDB "/usr/share/collectd/types.db"
WriteQueueLimitHigh 10000
WriteQueueLimitLow 10000
Interval 180
Timeout 2
ReadThreads 10

<LoadPlugin processes>
  Globals false
</LoadPlugin>
<LoadPlugin python>
  Globals true
</LoadPlugin>
<Plugin processes>
Process "collectd"
</Plugin>

<Plugin "python">
  ModulePath "/usr/lib/collectd/python-lib"
  LogTraces false
  Interactive false

  Import "check_openstack_api"

  <Module "check_openstack_api">
    KeystoneUrl "{{ OS_AUTH_URL }}"
    Password "{{ OS_PASSWORD }}"
    PollingInterval {{ OS_POLLING_INTERVAL | default(180) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>

</Plugin>
<LoadPlugin "write_prometheus">
  Globals false
</LoadPlugin>

<Plugin "write_prometheus">
  Port "{{ WRITE_PROMETHEUS_PORT | default(9103) }}"
</Plugin>

Include "/etc/collectd/conf.d/*.conf"

