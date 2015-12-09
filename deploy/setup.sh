#!/bin/bash

# setup ansible locally
apt-get install software-properties-common
apt-add-repository ppa:ansible/ansible
apt-get update
apt-get install ansible
ansible-galaxy install angstwad.docker_ubuntu