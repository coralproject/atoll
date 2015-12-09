Setup local dependencies:

    ./setup.sh

To deploy the Coral Atoll instance:

    ./deploy.sh

**NOTE**: There are some issues with Ansible 1.9.4 and Docker >= 1.8.3.

In particular, the Docker API changed between Docker 1.8.2 and Docker 1.8.3.

You can either install a newer Ansible from source, wait until 1.9.5 is released,
or apply the patch manually by editing `/usr/lib/pymodules/python2.7/ansible/modules/core/cloud/docker/docker.py`
and applying the changes described here: <https://github.com/ansible/ansible-modules-core/pull/2258/files>.

Refer to:
- <https://github.com/ansible/ansible-modules-core/issues/2257>
- <https://github.com/ansible/ansible-modules-core/issues/2269>

Also, `docker-py` must be at version 1.2.3 to avoid the error:

    Docker API Error: client is newer than server (client API version: 1.21, server API version: 1.20)

Refer to <https://github.com/ansible/ansible-docker-base/issues/19>.