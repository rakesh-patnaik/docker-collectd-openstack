TypesDB "/usr/share/collectd/types.db"
WriteQueueLimitHigh 10000
WriteQueueLimitLow 10000
Interval 30
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
    PollingInterval {{ OS_POLLING_INTERVAL | default(30) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>

  Import "openstack_cinder_services"

  <Module "openstack_cinder_services">
    KeystoneUrl "{{ OS_AUTH_URL }}"
    Password "{{ OS_PASSWORD }}"
    PollingInterval {{ OS_POLLING_INTERVAL | default(30) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>

  Import "openstack_neutron_agents"

  <Module "openstack_neutron_agents">
    KeystoneUrl "{{ OS_AUTH_URL }}"
    Password "{{ OS_PASSWORD }}"
    PollingInterval {{ OS_POLLING_INTERVAL | default(30) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>

</Plugin>

<LoadPlugin write_http>
  Globals false
</LoadPlugin>
<Plugin write_http>
  <Node "collectd_exporter">
    URL "http://localhost:9102/collectd-post"
    Format "JSON"
    StoreRates false
  </Node>
</Plugin>


Include "/etc/collectd/conf.d/*.conf"

