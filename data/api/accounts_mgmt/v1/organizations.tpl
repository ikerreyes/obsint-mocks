{% macro make_org(org, has_next=false) %}
{
  "created_at": "2019-03-27T16:55:52.862631Z",
  "ebs_account_id": "6089719",
  "external_id": "{{org}}",
  "href": "/api/accounts_mgmt/v1/organizations/{{org}}",
  "id": "{{org}}",
  "kind": "Organization",
  "name": "Jeff Needle",
  "updated_at": "2022-11-16T05:19:21.208194Z"
}{% if has_next %},{% endif %}
{% endmacro %}
{
  "items": [
    {% for org in organizations %}
    {{ make_org(org, has_next=loop.nextitem is defined) | indent }}
    {% endfor %}
  ],
  "kind": "OrganizationList",
  "page": 1,
  "size": {{ organizations | length }},
  "total": {{ organizations | length }}
}
