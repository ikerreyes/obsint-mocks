import logging
import os
import random
import re
import string
from os import path
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)
app = FastAPI()

FOLDER = Path(path.dirname(path.realpath(__file__)))
DATA_FOLDER = FOLDER / "../data"
if os.getenv("MOCK_DATA"):
    DATA_FOLDER = Path(os.getenv("MOCK_DATA"))  # type: ignore[arg-type]

templates = Jinja2Templates(directory=DATA_FOLDER / "api", trim_blocks=True, lstrip_blocks=True)
templates.env.globals["random_string"] = lambda: "".join(
    random.choice(string.ascii_letters + string.digits) for i in range(16)
)

with open(FOLDER / "conf.yaml") as fd:
    CONF = yaml.safe_load(fd)


@app.get("/")
async def root():
    return {"message": "Hello World"}


org_id_query = re.compile(r"organization_id\s?(?:=|is)\s?['\"]?(\w*)")
external_cluster_id_query = re.compile(r"external_cluster_id\s?(?:=|is)\s?['\"]?([\w-]*)")


@app.get("/api/accounts_mgmt/v1/subscriptions", response_class=JSONResponse)
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
            clusters = CONF["organizations"].get(org, {}).get("clusters", [])
        else:
            logger.info("no org provided, getting all clusters")
            clusters = [
                c for org in CONF["organizations"] for c in CONF["organizations"][org]["clusters"]
            ]
        # TODO: what if cluster_match with 1 org and without org
        if cluster_match:
            logger.info("cluster match", cluster_match.group(1))
            clusters = [c for c in clusters if c["uuid"] == cluster_match.group(1)]
    return templates.TemplateResponse(
        "accounts_mgmt/v1/subscriptions.tpl",
        {"request": request, "clusters": clusters, "organization": org},
        media_type="application/json",
    )


org_external_id_query = re.compile(r"external_id\s?=\s?(\w*)")


@app.get("/api/accounts_mgmt/v1/organizations", response_class=JSONResponse)
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
        orgs = list(CONF["organizations"].keys())
    return templates.TemplateResponse(
        "accounts_mgmt/v1/organizations.tpl",
        {"request": request, "organizations": orgs},
        media_type="application/json",
    )


@app.api_route("/{path_name:path}", methods=["GET"], response_class=FileResponse)
async def catch_all(path_name: str):
    """Return the JSON associated with the request"""
    # TODO harden this for path traversal
    file = DATA_FOLDER / f"{path_name}.json"
    logger.info("fallback mechanism for %s", path_name)
    if file.exists():
        return file
    else:
        raise HTTPException(status_code=404, detail="Unfound response")
