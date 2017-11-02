FROM          ubuntu:16.04
MAINTAINER    Rakesh Patnaik (rakesh.patnaik9@gmail.com)

RUN           apt-get -y update \
              && apt-get -y --allow-unauthenticated install collectd curl python-dateutil python-requests python-simplejson python-pip python-prometheus-client\
              && apt-get clean \
              && rm -rf /var/lib/apt/lists/*
RUN           pip install envtpl
RUN           mkdir /usr/lib/collectd/python-lib
RUN           curl -SL https://github.com/prometheus/pushgateway/releases/download/v0.4.0/pushgateway-0.4.0.linux-amd64.tar.gz | tar -xzC /usr/share

COPY          etc/collectd /etc/collectd
COPY          usr/lib/collectd/python-lib/* /usr/lib/collectd/python-lib/
COPY          config_and_run_collectd.sh /usr/bin
              
RUN           chmod +x /usr/bin/config_and_run_collectd.sh

EXPOSE        9103

CMD           ["/usr/bin/config_and_run_collectd.sh"]
