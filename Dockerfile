FROM debian:9

MAINTAINER Daniele Melosi "daniele.melosi@dada.eu"

RUN apt-get update
RUN apt-get -y install python-pip
RUN apt-get -y upgrade
RUN pip install elasticsearch
RUN pip install pyvmomi
RUN apt-get -y install python-pycurl

RUN mkdir -p /usr/local/lhcp_server_provisioning
COPY auto_install.sh /usr/local/lhcp_server_provisioning/
COPY lhcp_server_provisioning.conf /usr/local/lhcp_server_provisioning/
COPY lhcp_server_provisioning_function.py /usr/local/lhcp_server_provisioning/
COPY lhcp_server_provisioning.py /usr/local/lhcp_server_provisioning/
COPY noc_api.php /usr/local/lhcp_server_provisioning/
COPY r1redirect.php /usr/local/lhcp_server_provisioning/
COPY soft2.php /usr/local/lhcp_server_provisioning/
COPY chiave_lhcp_provisioning /usr/local/lhcp_server_provisioning/
COPY chiave_lhcp_provisioning.pub /usr/local/lhcp_server_provisioning/

CMD ["/usr/local/lhcp_server_provisioning/lhcp_server_provisioning.py"]

