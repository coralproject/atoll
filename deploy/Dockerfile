FROM ubuntu:14.04
MAINTAINER francis <f@frnsys.com>

# setup
RUN apt-get update
RUN apt-get upgrade -yq
RUN apt-get install -yq --no-install-recommends git python python-pip python-dev gcc

# setup ansible locally
RUN pip2 install -U ansible
RUN pip2 install markupsafe # bug? on some deploys doesn't install properly with ansible.
RUN ansible-galaxy install angstwad.docker_ubuntu

# fix for <https://groups.google.com/forum/#!msg/ansible-project/CPSejzrgW18/f3veS6gqAwAJ>
ENV ANSIBLE_SQUASH_ACTIONS "pkgng"

# clone atoll repo
RUN git clone https://github.com/coralproject/atoll /tmp/atoll

# self-provision
RUN ansible-playbook -i /tmp/atoll/deploy/hosts.ini /tmp/atoll/deploy/playbooks/docker.yml -e "env=docker"

# clean up
RUN service supervisor stop
RUN rm -rf /tmp/atoll

# expose ports 22->ssh 8181->atoll
EXPOSE 22 8181

CMD ["supervisord", "-n"]