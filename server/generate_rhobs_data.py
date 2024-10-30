default_metric_value = [1674659551.037, "1"]
empty_response = {"status": "success", "data": {"resultType": "vector", "result": []}}


def generate_mock_responses(config):
    """Populates the mock_responses dictionary with generated data."""
    mock_responses = {}

    for cluster_id, alerts_and_focs in config["mock_responses"].items():
        mock_responses[cluster_id] = {
            "status": "success",
            "data": {"resultType": "vector", "result": []},
        }

        mock_responses[cluster_id] = add_console_url(
            mock_responses[cluster_id],
            cluster_id,
            f"https://console-openshift-console.{cluster_id}.com",
        )

        for i in range(alerts_and_focs["alerts"]):
            mock_responses[cluster_id] = add_alert(mock_responses[cluster_id], cluster_id, i)
        for i in range(alerts_and_focs["focs"]):
            mock_responses[cluster_id] = add_foc(mock_responses[cluster_id], cluster_id, i)
    return mock_responses


def add_console_url(response, cluster_id, console_url):
    metric = {"__name__": "console_url", "_id": cluster_id, "url": console_url}

    response["data"]["result"].append({"metric": metric, "value": default_metric_value})
    return response


def add_alert(response, cluster_id, i):
    alert = {
        "__name__": "alerts",
        "_id": cluster_id,
        "alertname": f"ClusterNotUpgradeable-{i}",
        "alertstate": "firing",
        "condition": "Upgradeable",
        "endpoint": "metrics",
        "name": "version",
        "namespace": f"openshift-test-namespace-{i}",
        "prometheus": "openshift-monitoring/k8s",
        "receive": "true",
        "severity": "critical",
        "tenant_id": cluster_id.upper(),
    }

    response["data"]["result"].append({"metric": alert, "value": default_metric_value})
    return response


def add_foc(response, cluster_id, i):
    foc = {
        "__name__": "cluster_operator_conditions",
        "_id": cluster_id,
        "condition": "Available",
        "endpoint": "metrics",
        "instance": "1.2.3.4:9099",
        "job": "cluster-version-operator",
        "name": f"authentication-{i}",
        "namespace": "openshift-cluster-version",
        "pod": "cluster-version-operator-cc6d9c75-ssgb6",
        "prometheus": "openshift-monitoring/k8s",
        "reason": "AsExpected",
        "receive": "true",
        "service": "cluster-version-operator",
        "tenant_id": cluster_id.upper(),
    }

    response["data"]["result"].append({"metric": foc, "value": default_metric_value})
    return response
