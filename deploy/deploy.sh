#!/bin/bash

# for testing:
# ansible all -i hosts.ini --module-name ping -u ubuntu

# deploy coral atoll instance
ansible-playbook -i hosts.ini coral.yml