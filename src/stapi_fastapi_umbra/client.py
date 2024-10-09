import asyncio
import json
import logging

import httpx
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest

from stapi_fastapi_umbra.models import FeasibilityResponse
from stapi_fastapi_umbra.opportunities import (
    feasibility_response_to_opportunity_list,
    opportunity_request_to_feasibility_request,
    stac_item_to_opportunity,
)
from stapi_fastapi_umbra.settings import CANOPY_API_URL, Settings

settings = Settings.load()
logger = logging.getLogger()


class AuthorizationError(Exception):
    pass


class Client:
    def __init__(self, canopy_api_url: str, canopy_token: str | None) -> None:
        self.canopy_api_url = canopy_api_url
        self.canopy_token = canopy_token

    async def get_opportunities_from_archive(
        self,
        search: OpportunityRequest,
    ) -> list[Opportunity]:
        # Gets opportunities from the archive. Only point geometry searches
        # are supported for now.

        request_payload = {"filter-lang": "cql2-json", **search.model_dump()}

        # SearchOpportunity requires a `geometry` field, but the Canopy API archive/search
        # route uses an optional 'intersects' field.
        request_payload["intersects"] = request_payload.pop("geometry")

        archive_url = f"{CANOPY_API_URL}/archive/search"
        res = httpx.post(url=archive_url, json=request_payload)
        res.raise_for_status()
        opportunities = [
            stac_item_to_opportunity(o, product_id=search.product_id)
            for o in res.json()["features"]
        ]
        return opportunities

    async def get_opportunities_from_feasibility(
        self,
        search: OpportunityRequest,
    ) -> list[Opportunity]:
        # Gets opportunities from feasibility. Only point geometry searches
        # are supported.

        if not self.canopy_token:
            raise AuthorizationError(
                "Time range requested includes future opportunities, canopy_token is required"
            )

        headers = {"Authorization": f"Bearer {self.canopy_token}"}

        payload = opportunity_request_to_feasibility_request(search)
        payload_to_send = payload.model_dump_json()

        feasibility_url = f"{self.canopy_api_url}/tasking/feasibilities"
        feasibility_post = httpx.post(
            url=feasibility_url,
            json=json.loads(payload_to_send),
            headers=headers,
        )

        feasibility_post.raise_for_status()
        request_id = feasibility_post.json()["id"]
        i = 0
        while i <= settings.feasibility_timeout:
            feasibility_get = httpx.get(
                url=f"{feasibility_url}/{request_id}",
                headers=headers,
            )
            feasibility_get.raise_for_status()
            feasibility_status = feasibility_get.json()["status"]

            if feasibility_status == "COMPLETED":
                break
            await asyncio.sleep(1)

        feasibility_response = FeasibilityResponse.model_validate(
            feasibility_get.json()
        )
        opportunities = feasibility_response_to_opportunity_list(
            feasibility_response, product_id=search.product_id
        )

        return opportunities
