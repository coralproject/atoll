#!/bin/bash

# for testing:
# ansible all -i hosts.ini --module-name ping -u ubuntu

# deploy coral atoll instance
ansible-playbook -i hosts.ini playbooks/coral.yml

# deploy darwin (composer) instance
ansible-playbook -i hosts.ini playbooks/darwin.yml