{% macro make_cluster(cluster, org=None, has_next=false) %}
{% set subscription_id = random_string() %}
{% set creator_id = random_string() %}
{% set org_id = org or random_string() %}
{
  "id": "{{subscription_id}}",
  "kind": "Subscription",
  "href": "/api/accounts_mgmt/v1/subscriptions/{{subscription_id}}",
  "plan": {
    "id": "OCP",
    "kind": "Plan",
    "href": "/api/accounts_mgmt/v1/plans/OCP"
  },
  "cluster_id": "{{random_string()}}",
  "external_cluster_id": "{{cluster.uuid}}",
  "organization_id": "{{org_id}}",
  "last_telemetry_date": "2019-09-17T07:29:55.491319Z",
  "created_at": "2019-09-15T11:24:10.934349Z",
  "updated_at": "2019-12-22T09:45:57.161735Z",
  "display_name": "{{cluster.name | default(cluster.uuid)}}",
  "creator": {
    "id": "{{creator_id}}",
    "kind": "Account",
    "href": "/api/accounts_mgmt/v1/accounts/{{creator_id}}",
    "name": "QE account",
    "username": "ccx-qe@redhat.com"
  },
  "managed": {{cluster.managed|default(false)|tojson}},
  "status": "Disconnected",
  "last_reconcile_date": "2019-12-22T09:45:57.158566Z",
  "consumer_uuid": "290a2d7b-fb92-4ccf-a3c3-1e6001c60524"
}{% if has_next %},{% endif %}
{% endmacro %}
{
  "kind": "SubscriptionList",
  "page": 1,
  "size": {{ clusters | length }},
  "total": {{ clusters | length }},
  "items": [
    {% for cluster in clusters %}
    {{ make_cluster(cluster, organization, has_next=loop.nextitem is defined) | indent }}
    {% endfor %}
  ]
}
