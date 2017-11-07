TypesDB "/usr/share/collectd/types.db"
WriteQueueLimitHigh 10000
WriteQueueLimitLow 10000
Interval 30
Timeout 2
ReadThreads 10

<LoadPlugin processes>
  Globals false
</LoadPlugin>

<Plugin processes>
  Process "collectd"
</Plugin>

<LoadPlugin python>
  Globals true
</LoadPlugin>

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
    UserDomain "{{ OS_USER_DOMAIN_NAME }}"
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>
  Import "openstack_cinder_services"

  <Module "openstack_cinder_services">
    KeystoneUrl "{{ OS_AUTH_URL }}"
    Password "{{ OS_PASSWORD }}"
    PollingInterval {{ OS_POLLING_INTERVAL | default(30) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    UserDomain "{{ OS_USER_DOMAIN_NAME }}"    
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
  
  Import "hypervisor_stats"

  <Module "hypervisor_stats">
    CpuAllocationRatio "8.0"
    KeystoneUrl "{{ OS_AUTH_URL }}"
    Password "{{ OS_PASSWORD }}"
    PollingInterval {{ OS_POLLING_INTERVAL | default(30) }}
    Tenant "{{ OS_PROJECT_NAME }}"
    UserDomain "{{ OS_USER_DOMAIN_NAME }}"    
    Timeout {{ OS_TIMEOUT | default(10) }}
    Username "{{ OS_USERNAME }}"
  </Module>
  
</Plugin>

<LoadPlugin "ntpd">
  Globals false
</LoadPlugin>

<Plugin "ntpd">
  Host "localhost"
  Port "123"
  ReverseLookups false
</Plugin>

<LoadPlugin "virt">
  Globals false
</LoadPlugin>

<Plugin "virt">
  Connection "qemu:///system"
  RefreshInterval 60
  HostnameFormat "uuid"
</Plugin>

<LoadPlugin "load">
  Globals false
</LoadPlugin>

<LoadPlugin "memory">
  Globals false
</LoadPlugin>

<LoadPlugin "vmem">
  Globals false
</LoadPlugin>

<Plugin "vmem">
  Verbose false
</Plugin>

<LoadPlugin "cpu">
  Globals false
</LoadPlugin>

<LoadPlugin "disk">
  Globals false
</LoadPlugin>

<Plugin "disk">
  Disk "/^loop\d+$/"
  Disk "/^dm-\d+$/"
  IgnoreSelected "true"
</Plugin>

<LoadPlugin "df">
  Globals false
</LoadPlugin>

<Plugin "df">
  FSType "ext2"
  FSType "ext3"
  FSType "ext4"
  FSType "xfs"
  FSType "tmpfs"
  IgnoreSelected false
  ReportByDevice false
  ReportInodes true
  ReportReserved true
  ValuesAbsolute true
  ValuesPercentage true
</Plugin>

<LoadPlugin "netlink">
  Globals false
</LoadPlugin>

<Plugin "netlink">
  VerboseInterface "eth0"
  VerboseInterface "eth1"
  IgnoreSelected false
</Plugin>

<LoadPlugin "interface">
  Globals false
</LoadPlugin>

<Plugin "interface">
  Interface "/^lo\d*$/"
  Interface "/^docker.*/"
  Interface "/^t(un|ap)\d*$/"
  Interface "/^veth.*$/"
  IgnoreSelected "true"
</Plugin>

<LoadPlugin "uptime">
  Globals false
</LoadPlugin>

<LoadPlugin "write_prometheus">
  Globals false
</LoadPlugin>

<Plugin "write_prometheus">
  Port "{{ WRITE_PROMETHEUS_PORT | default(9103) }}"
</Plugin>

Include "/etc/collectd/conf.d/*.conf"

