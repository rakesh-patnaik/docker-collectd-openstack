<<<<<<< HEAD
collectd-openstack
============

Image for a collectd performing metric collection and checks on openstack API and infrastructure.

## Environment

check sample_env_file provided in the source. 

* OS_USERNAME 
  - username associated with the monitoring tenant/project in openstack, used for polling openstack API, **required**

* OS_PASSWORD
  - password for the username associated with the monitoring tenant/project in openstack, used for polling openstack API, **required**

* OS_PROJECT_NAME
  - monitoring tenant/project in openstack, used for polling openstack API, **required**

* OS_AUTH_URL
  - openstack keystone API endpoint, **required**

* WRITE_PROMETHEUS_PORT
  - port to bind collectd write_prometheus plugin. By default, 9103. Ref: https://collectd.org/wiki/index.php/Plugin:Write_Prometheus

==========sample_env_file==============
OS_USERNAME=admin
OS_PASSWORD=password
OS_AUTH_URL=https://identity.host.com:5000/v2.0
OS_PROJECT_NAME=admin1
WRITE_PROMETHEUS_PORT=9103
=======================================

## Docker Usage

docker run --env-file sample_env_file -it rakeshpatnaik/collectd-openstack

## sample test
docker exec \<instance-id\> curl http://localhost:9103 

\# HELP collectd_check_openstack_api_gauge write_prometheus plugin: 'check_openstack_api' Type: 'gauge', Dstype: 'gauge', Dsname: 'value'
\# TYPE collectd_check_openstack_api_gauge gauge
collectd_check_openstack_api_gauge{instance="40ad2d53a7dc"} 1 1507096549467
collectd_check_openstack_api_gauge{check_openstack_api="ceilometer-api",instance="40ad2d53a7dc"} 0 1507096547649
collectd_check_openstack_api_gauge{check_openstack_api="cinder-api",instance="40ad2d53a7dc"} 1 1507096548364
collectd_check_openstack_api_gauge{check_openstack_api="cinder-v2-api",instance="40ad2d53a7dc"} 1 1507096516430
collectd_check_openstack_api_gauge{check_openstack_api="glance-api",instance="40ad2d53a7dc"} 1 1507096516831
collectd_check_openstack_api_gauge{check_openstack_api="heat-api",instance="40ad2d53a7dc"} 1 1507096548677
collectd_check_openstack_api_gauge{check_openstack_api="heat-cfn-api",instance="40ad2d53a7dc"} 1 1507096547966
collectd_check_openstack_api_gauge{check_openstack_api="keystone-public-api",instance="40ad2d53a7dc"} 1 1507096549166
collectd_check_openstack_api_gauge{check_openstack_api="neutron-api",instance="40ad2d53a7dc"} 1 1507096549467
collectd_check_openstack_api_gauge{check_openstack_api="nova-api",instance="40ad2d53a7dc"} 1 1507096516087
collectd_check_openstack_api_gauge{check_openstack_api="swift-api",instance="40ad2d53a7dc"} 1 1507096548858
collectd_check_openstack_api_gauge{check_openstack_api="swift-s3-api",instance="40ad2d53a7dc"} 1 1507096516631


## Ports

* 9103 
  - Prometheus or other line protocol scrapers target. set using env var WRITE_PROMETHEUS_PORT
=======
# docker-collectd-openstack
>>>>>>> 49c055754fc6bafa79068a25ff7ffea8a37208d6
