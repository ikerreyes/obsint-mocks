import logging
import os
import re
from typing import Dict

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from generate_rhobs_data import empty_response
from generate_rhobs_data import generate_mock_responses

logger = logging.getLogger(__name__)
app = FastAPI()
router = APIRouter()


class Server:
    """The server handles the response retrieval from the mocked responses."""

    def __init__(self):
        self.mock_responses = {}

    def mock_response_single_cluster(self, cluster_id):
        """Get the response from the mocked responses."""
        response = self.mock_responses.get(cluster_id)
        if response is None:
            return JSONResponse(content=empty_response, status_code=200)
        return JSONResponse(content=response, status_code=200)

    def mock_response_multi_cluster(self, cluster_ids):
        """Concatenate the single cluster responses for each cluster_id."""
        response = empty_response
        logger.info("got a request for %s clusters", cluster_ids)
        for cluster_id in cluster_ids:
            if cluster_id in self.mock_responses:
                response["data"]["result"].extend(self.mock_responses[cluster_id]["data"]["result"])
        return JSONResponse(content=response, status_code=200)

    def get_instant_query(self, tenant, query: str):
        """Return a single or multi cluster response."""
        cluster_ids = self.get_cluster_ids_from_query(query)

        if len(cluster_ids) == 0:
            return JSONResponse(content=empty_response, status_code=200)

        if len(cluster_ids) == 1:
            return self.mock_response_single_cluster(cluster_ids[0])

        return self.mock_response_multi_cluster(cluster_ids)

    def remove_duplicate(self, slice_list):
        """Remove the duplicates from the query.
        Because there could be queries asking for different metrics for the
        same cluster.
        """
        all_keys = set()
        list_unique = []
        for item in slice_list:
            if item not in all_keys:
                all_keys.add(item)
                list_unique.append(item)
        return list_unique

    def get_cluster_ids_from_query(self, query):
        """Get all the different UUIDs in the query."""
        pattern = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        return self.remove_duplicate(re.findall(pattern, query))


server = Server()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/api/metrics/v1/{tenant}/api/v1/query")
async def get_instant_query(tenant: str, query: str = Query(...)):
    """Mocks the /api/metrics/v1/{tenant}/api/v1/query endpoint"""
    return server.get_instant_query(tenant, query)


class ClusterResponse(BaseModel):
    focs: int
    alerts: int


class ClusterResponses(BaseModel):
    mock_responses: Dict[str, ClusterResponse]


@router.put("/rhobs_responses", status_code=204)
async def change_rhobs_responses(responses: ClusterResponses):
    logger.info("Changing mocked responses for RHOBS endpoint")
    server.mock_responses = generate_mock_responses(jsonable_encoder(responses))


# Include the same endpoints at the "root"
# and with a prefix. This is useful for exposing
# internal in the cluster and through and OpenShift route
# managed by Clowder with minimal changes in the configs
# See https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-in-another
route_prefix = os.getenv("SERVER_ROUTE_PREFIX")
if route_prefix is not None:
    app.include_router(router, prefix=route_prefix)
app.include_router(router, prefix="")
