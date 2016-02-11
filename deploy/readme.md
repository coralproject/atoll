## Setup the local machine

The deployment system uses Ansible, so your local system needs to be setup for that first.

If you are using Ubuntu, you can just run the `setup.sh` script:

    ./setup.sh

## Setting up HTTPS/SSL

Our deployment here sets up https access only (http redirects to https).

If you do not have proper signed certificates, you can self-sign a certificate. [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-create-a-ssl-certificate-on-nginx-for-ubuntu-12-04) has a good guide on that, but to briefly summarize:

    # make note of your pass phrase
    sudo openssl genrsa -des3 -out cert.key 2048

    # make the certificate signing request
    # for the following, you only need to fill in "Common Name" with your hostname or IP
    sudo openssl req -new -key cert.key -out cert.csr

    # remove the pass phrase
    sudo cp cert.key cert.key.org
    sudo openssl rsa -in cert.key.org -out cert.key

    # sign the cert
    sudo openssl x509 -req -days 365 -in cert.csr -signkey cert.key -out cert.crt

The deployment system expects your cert and key to be at `ssl/cert.crt` and `ssl/cert.key` respectively.

## Configuration

You will probably need to configure the host IPs/hostnames for your deployment environments, as well as environment-specific variables. You can edit these in `hosts.ini`.

To see which variables can be overridden, refer to `playbooks/group_vars/all.yml`.

## Deploying

To deploy the Coral Atoll instance:

    ./deploy.sh <ENV NAME>

Where `ENV NAME` is one of `[development, production]`.

After deploying, check the service is working correctly:

    python test.py <SERVER IP OR HOSTNAME>

## Notes

Deployment has been tested with Ansible 2.0.0.2.

Note that `docker-py` must be at version 1.2.3 to avoid the following error:

    Docker API Error: client is newer than server (client API version: 1.21, server API version: 1.20)

Note that this is already handled by the playbooks.

Refer to <https://github.com/ansible/ansible-docker-base/issues/19>.
