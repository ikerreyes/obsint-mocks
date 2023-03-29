# mock-ams

`mock-ams` is aimed to act as a mock server to run test using
external data pipeline and other services relying on AMS.

It is a minimal server, not meant for production but for testing,
that tries to have as minimal code as possible to be able to respond
to the queries done by CCX services to AMS.

As of 2022/11/29, it has only been used for external data pipeline.

## Local development

If you want to run the server locally:

```shell
pip install -r server/requirements.txt
uvicorn server.main:app --reload --log-config=server/logging.yaml
```

Exposed port is 8000 by default.

## Container build

1. Log into registry.redhat.io
2. Build the image

   ```shell
   podman build . -t mock-ams:latest
   ```

## Usage

The main usage for this service is as a mock replaced
for compose files of CCX services relying on AMS
(e.g. smart-proxy).

However, if you want to check its behavior
you can deploy the server and run queries directly using
`curl`. E.g.:

```shell
curl http://localhost:8000/api/accounts_mgmt/v1/organizations
```

Currently, only 2 endpoints have been implemented
(`/api/accounts_mgmt/v1/subscriptions` and `/api/accounts_mgmt/v1/organizations`).
See `server/main.py` for more details.

If you want to add new endpoints you can explicitly implement them,
or just add the JSON you want to return on the appropriate path
under the `data` folder.

If you need to check how data should look like,
check api.openshift.com or the mock server in
[uhc-portal](https://gitlab.cee.redhat.com/service/uhc-portal).

## Configuration

Some responses use a config file to make
some inferences about the data
(e.g. which clusters are linked to an org).
That file is in `server/conf.yaml`,
as it should be aligned with the data we expect in the tests.

## Token

Accessing AMS through the SDK makes some checks.
A valid token is needed even if the mock server does
not validate it.
Thus `INSIGHTS_RESULTS_SMART_PROXY__AMSCLIENT__TOKEN` variable
is defined for smart-proxy. If a new token is needed,
you can find the code to generate it in the `token` folder.
Execute it with:

```shell
cd token
go run generate_token.go
```
