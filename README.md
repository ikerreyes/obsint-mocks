# mock-ams


`mock-ams` is aimed to act as a mock server to run test using
external data pipeline and other services relying on AMS.

It is a minimal server, not meant for production but for testing,
that tries to have as minimal code as possible to be able to respond
to the queries done by CCX services to AMS.

Additionaly, it also includes endpoints mimicking OCM Service Log
functionality (also used for testing).

As of 2022/11/29, it has only been used for external data pipeline.

## Local development

If you want to run the server locally:

```shell
python -m venv venv
source venv/bin/activate
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
3. run the image

   ```shell
   podman run --publish 8000:8000 mock-ams
   ```

## Usage

The main usage for this service is as a mock replaced
for compose files of CCX services relying on AMS
(e.g. smart-proxy) or OCM Service Log (notification service).

However, if you want to check its behavior
you can deploy the server and run queries directly using
`curl`. E.g.:

```shell
curl http://localhost:8000/api/accounts_mgmt/v1/organizations
```

Currently, 4 endpoints have been implemented:
- `[GET] /api/accounts_mgmt/v1/subscriptions`
- `[GET] /api/accounts_mgmt/v1/organizations`
- `[GET] /api/service_logs/v1/clusters/cluster_logs`
- `[POST] /api/service_logs/v1/cluster_logs/`
See `server/main.py` for more details.

If you want to add new endpoints you can explicitly implement them,
or just add the JSON you want to return on the appropriate path
under the `data` folder.

If you need to check how data should look like,
check api.openshift.com or the mock server in
[uhc-portal](https://gitlab.cee.redhat.com/service/uhc-portal).

## Configuration

### AMS

Some responses use a config file to make
some inferences about the data
(e.g. which clusters are linked to an org).
That file is in `server/conf.yaml`,
as it should be aligned with the data we expect in the tests.

Configuration can be changed via
`[PUT] /ams_responses` endpoint.
The endpoint receives JSON data that override current
configuration. Data are in the following format:

```
{
    "organizations": {
        "123456": [
            {
                "uuid": "c1e32880-417a-4226-be81-4d891cdf965e"
                "name": "Example cluster 1",
                "managed": "true"
            },
            {
                "uuid": "c2b778e0-5ac8-4cf4-8269-c6eaf0519fe4",
                "name": "Example cluster 2"
            }
        ]
    }
}
```

### RHOBS

RHOBS responses can be configured via
`[PUT] /rhobs_responses` endpoint.
The endpoint receives JSON data that override current
configuration. Data are in the following format:

```
{
    "mock_responses": {
        "c1e32880-417a-4226-be81-4d891cdf965e": {
            "focs": 4,
            "alerts" 5
        }
    }
}
```

## Token

This section is for external services willing to use this mock server.

Accessing AMS through the SDK provided by AMS maintainers
makes some checks.
A valid token is needed even if the mock server does
not validate it.
For example `INSIGHTS_RESULTS_SMART_PROXY__AMSCLIENT__TOKEN` variable
is defined for smart-proxy. If a new token is needed,
you can find the code to generate it in the `token` folder.
Execute it with:

```shell
cd token
go run generate_token.go
```
