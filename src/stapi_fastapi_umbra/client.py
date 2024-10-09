import asyncio
import json
import logging
from uuid import UUID

import httpx
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order

from stapi_fastapi_umbra.models import FeasibilityResponse, TaskResponse
from stapi_fastapi_umbra.opportunities import (
    feasibility_response_to_opportunity_list,
    opportunity_request_to_feasibility_request,
    opportunity_request_to_task_request,
    stac_item_to_opportunity,
    task_response_to_order,
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

    def create_order_from_opportunity_request(
        self, search: OpportunityRequest
    ) -> Order:
        if not self.canopy_token:
            raise AuthorizationError(
                "Time range requested includes future opportunities, canopy_token is required"
            )

        headers = {"Authorization": f"Bearer {self.canopy_token}"}

        payload = opportunity_request_to_task_request(search)
        payload_to_send = payload.model_dump_json()

        logger.info(f"submitting canopy task request: {payload_to_send}")

        tasking_url = f"{self.canopy_api_url}/tasking/tasks"
        response = httpx.post(
            url=tasking_url,
            json=json.loads(payload_to_send),
            headers=headers,
        )
        response.raise_for_status()

        print(response.json())

        task_response = TaskResponse.model_validate(response.json())

        return task_response_to_order(task_response, search.product_id)

    def get_order_by_id(self, order_id: str) -> Order:
        if not self.canopy_token:
            raise AuthorizationError(
                "Time range requested includes future opportunities, canopy_token is required"
            )

        headers = {"Authorization": f"Bearer {self.canopy_token}"}
        try:
            task_id = UUID(order_id)
        except Exception:
            raise ValueError("order_id must be a valid UUID")
        task_url = f"{settings.canopy_api_url}/tasking/tasks/{task_id}"
        response = httpx.get(
            url=task_url,
            headers=headers,
        )
        response.raise_for_status()
        task_response = TaskResponse.model_validate(response.json())
        return task_response_to_order(task_response, "unknown")
