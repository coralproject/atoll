#!/bin/bash

apt-get install python python-pip python-dev

# setup ansible locally
pip2 install -U ansible
pip2 install markupsafe # bug? on some deploys doesn't install properly with ansible.
ansible-galaxy install angstwad.docker_ubuntu