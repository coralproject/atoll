Setup local dependencies:

    ./setup.sh

To deploy the Coral Atoll instance:

    ./deploy.sh <ENV NAME>

Where `ENV NAME` is one of `[development, production]`.

After deploying, check the service is working correctly:

    python test.py

---

Deployment has been tested with Ansible 2.0.0.2.

Note that `docker-py` must be at version 1.2.3 to avoid the following error:

    Docker API Error: client is newer than server (client API version: 1.21, server API version: 1.20)

Note that this is already handled by the playbooks.

Refer to <https://github.com/ansible/ansible-docker-base/issues/19>.