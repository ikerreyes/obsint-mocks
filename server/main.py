import json
import logging
import os
import random
import re
import string
from os import path
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

logger = logging.getLogger(__name__)
app = FastAPI()
router = APIRouter()
app.state.service_log = {}

FOLDER = Path(path.dirname(path.realpath(__file__)))
DATA_FOLDER = FOLDER / "../data"
if os.getenv("MOCK_DATA"):
    DATA_FOLDER = Path(os.getenv("MOCK_DATA"))  # type: ignore[arg-type]

templates = Jinja2Templates(directory=DATA_FOLDER / "api", trim_blocks=True, lstrip_blocks=True)
templates.env.globals["random_string"] = lambda: "".join(
    random.choice(string.ascii_letters + string.digits) for i in range(16)
)

app.conf = {"organizations": {}}


@router.get("/")
async def root():
    return {"message": "Hello World"}


org_id_query = re.compile(r"organization_id\s?(?:=|is)\s?['\"]?(\w*)")
external_cluster_id_query = re.compile(r"external_cluster_id\s?(?:=|is)\s?['\"]?([\w-]*)")


@router.get("/api/accounts_mgmt/v1/subscriptions", response_class=JSONResponse)
async def subscriptions(
    request: Request, page: Optional[int] = None, search: str = Query(default="")
):
    """
    Cases:
    - more than 1 page, return empty
    - if org provided, all clusters for that org
    - if cluster provided, matching cluster if present
    - if org and cluster provided, matching cluster if within org
    """
    org = "".join(random.choice(string.digits) for i in range(8))
    logger.info("subscriptions")
    if page and page > 1:
        logger.info("page bigger than 1")
        clusters = []
    else:
        logger.info("searching for %s", search)
        org_match = org_id_query.search(search)
        cluster_match = external_cluster_id_query.search(search)
        if org_match:
            org = org_match.group(1)
            clusters = app.conf["organizations"].get(org, {}).get("clusters", [])
        else:
            logger.info("no org provided, getting all clusters")
            clusters = [
                c
                for org in app.conf["organizations"]
                for c in app.conf["organizations"][org]["clusters"]
            ]
        # TODO: what if cluster_match with 1 org and without org
        if cluster_match:
            logger.info("cluster match %s", cluster_match.group(1))
            clusters = [c for c in clusters if c["uuid"] == cluster_match.group(1)]
    return templates.TemplateResponse(
        "accounts_mgmt/v1/subscriptions.tpl",
        {"request": request, "clusters": clusters, "organization": org},
        media_type="application/json",
    )


org_external_id_query = re.compile(r"external_id\s?=\s?(\w*)")


@router.get("/api/accounts_mgmt/v1/organizations", response_class=JSONResponse)
async def organizations(request: Request, search: str = Query(default="")):
    """
    Cases:
    - org provided: return itself
    - no org provided: all orgs in file
    """
    logger.info("getting organizations")
    match = org_external_id_query.search(search)
    if match:
        orgs = [match.group(1)]
    else:
        orgs = list(app.conf["organizations"].keys())
    return templates.TemplateResponse(
        "accounts_mgmt/v1/organizations.tpl",
        {"request": request, "organizations": orgs},
        media_type="application/json",
    )


@router.get("/api/service_logs/v1/clusters/cluster_logs", response_class=JSONResponse)
async def service_log_events(request: Request):
    logger.info("received request for service log events")
    params = request.query_params

    if "cluster_id" in params:
        cluster_id = params["cluster_id"]
    elif "cluster_uuid" in params:
        cluster_id = params["cluster_uuid"]
    else:
        raise HTTPException(status_code=400, detail="Cluster ID missing")

    logs = []
    cluster_event = app.state.service_log.get(cluster_id, None)
    if cluster_event:
        logs = [cluster_event]
    response = {"kind": "ClusterLogList", "items": logs, "size": len(logs)}
    return response


@router.post("/api/service_logs/v1/cluster_logs", status_code=201)
async def service_log_create_event(request: Request):
    logger.info("got new service log event")
    body = await request.body()
    try:
        new_event = json.loads(body.decode("utf8"))
        logger.info("event successfully decoded")
        app.state.service_log[new_event["cluster_uuid"]] = new_event
        return {"Event received successfully"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=404, detail="Message is not valid JSON")


@router.api_route("/{path_name:path}", methods=["GET"], response_class=FileResponse)
async def catch_all(path_name: str):
    """Return the JSON associated with the request"""
    # TODO harden this for path traversal
    file = DATA_FOLDER / f"{path_name}.json"
    logger.info("fallback mechanism for %s", path_name)
    if file.exists():
        return file
    else:
        raise HTTPException(status_code=404, detail="Unfound response")


class Cluster(BaseModel):
    uuid: str
    name: Optional[str] = None
    managed: Optional[bool] = False


class ClusterList(BaseModel):
    clusters: list[Cluster]


class AMSMockConfiguration(BaseModel):
    organizations: dict[int, ClusterList]


@router.put("/ams_responses", status_code=204)
async def change_ams_responses(configuration: AMSMockConfiguration):
    """Configure the responses from AMS mock"""
    logger.info("Changing mocked responses for AMS")
    app.conf = jsonable_encoder(configuration, exclude_unset=True)


# Include the same endpoints at the "root"
# and with a prefix. This is useful for exposing
# internal in the cluster and through and OpenShift route
# managed by Clowder with minimal changes in the configs
# See https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-in-another
route_prefix = os.getenv("SERVER_ROUTE_PREFIX")
if route_prefix is not None:
    app.include_router(router, prefix=route_prefix)
app.include_router(router, prefix="")
