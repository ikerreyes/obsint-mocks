# rhobs-mock

Run this program to have a mock of rhobs server that replies with a fixed response. Only one endpoint is implemented (will return a mock response)
`/api/metrics/v1/{tenant}/api/v1/query`.
The server matches [this](https://github.com/observatorium/api/tree/main/client) specification.

## Configuration

You can configure the number of alerts and focs that the RHOBS mock will return
by modifying the [responses.yaml](../server/responses.yaml) file:

```yaml
mock-responses:
  3a87e224-c878-4f54-91cf-3f1900609207:
    alerts: 2
    focs: 3
  a994b868-4878-477a-8f8d-dbddb3130ed3:
    alerts: 1
    focs: 0
```

## Usage
Running the mock server is pretty straight forward. Just launch:

```sh
cd server
uvicorn rhobs:app --reload --log-config=logging.yaml
```

or

```
podman build . -t rhobs-mock:latest
podman run --publish 8000:8000 rhobs-mock uvicorn rhobs:app --host 0.0.0.0 --port 8000 --log-config=logging.yaml
```

And the server will start listening on the port 8000, at this point use a
browser or curl and connect to an endpoint to inspect the mock response.
It is possible to specify a port with the `--port` flag.

You can query it using a query similar to the following examples using your
`CLUSTER_ID`:

- For single cluster:

```
curl "http://127.0.0.1:8080/api/metrics/v1/telemeter/api/v1/query?query=alerts%7B_id%3D%22${CLUSTER_ID}%22%7D"
```

- For multiple clusters:

```
curl "http://127.0.0.1:8080/api/metrics/v1/telemeter/api/v1/query?query=alerts%7B_~id%3D%22${CLUSTER_ID|OTHER_CLUSTER_ID|ANOTHER_CLUSTER_ID}%22%7D"
```


### Docker

You can also run it using docker

```
docker build -t rhobs-mock .
docker run -p 8000:8000 rhobs-mock
```

## Development

The generation of the mocked data is located in
[generate_rhobs_data.py](../server/generate_rhobs_data.py)
while the server logic can be found in [rhobs.py](../server/rhobs.py).
