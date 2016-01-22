#!/bin/bash

apt-get install python python-pip

# setup ansible locally
pip2 install -U ansible
ansible-galaxy install angstwad.docker_ubuntu