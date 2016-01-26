#!/bin/bash

DEPLOY_ENV=$1

# for testing:
# ansible all -i hosts.ini --module-name ping -u ubuntu

# fix for <https://groups.google.com/forum/#!msg/ansible-project/CPSejzrgW18/f3veS6gqAwAJ>
export ANSIBLE_SQUASH_ACTIONS="pkgng"

# deploy coral atoll instance
ansible-playbook -i hosts.ini playbooks/coral.yml -e "env=${DEPLOY_ENV}" #-vvvv

# deploy darwin (composer) instance
#ansible-playbook -i hosts.ini playbooks/darwin.yml -e "env=${DEPLOY_ENV}" #-vvvv