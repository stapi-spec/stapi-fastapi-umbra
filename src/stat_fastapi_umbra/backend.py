"""Umbra Backend Module"""

import asyncio
import json

import httpx
from fastapi import HTTPException, Request
from stat_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product

from stat_fastapi_umbra.models import FeasibilityResponse
from stat_fastapi_umbra.opportunities import (
    feasibility_response_to_opportunity_list,
    opportunity_request_to_feasibility_request,
    stac_item_to_opportunity,
)
from stat_fastapi_umbra.products import PRODUCTS
from stat_fastapi_umbra.settings import Settings

settings = Settings.load()


class UmbraBackend:
    """Umbra STAT Backend"""

    async def get_products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    async def get_product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        filtered_products = [p for p in PRODUCTS if p.id == product_id]
        if filtered_products:
            return filtered_products[0]
        raise HTTPException(status_code=404, detail="Product not found")

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the  given search parameters.

        Backends must validate search constraints and raise
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        if search.product_id == "umbra_spotlight":
            authorization = request.headers.get("authorization")
            headers = {"Authorization": authorization}

            payload = opportunity_request_to_feasibility_request(search)
            payload_to_send = payload.model_dump_json()

            feasibility_post = httpx.post(
                url=settings.feasibility_url,
                json=json.loads(payload_to_send),
                headers=headers,
            )

            feasibility_post.raise_for_status()
            request_id = feasibility_post.json()["id"]
            i = 0
            while i <= settings.feasibility_timeout:
                feasibility_get = httpx.get(
                    url=f"{settings.feasibility_url}/{request_id}",
                    headers=headers,
                )
                feasibility_get.raise_for_status()
                status = feasibility_get.json()["status"]

                if status == "COMPLETED":
                    break
                await asyncio.sleep(1)

            feasibility_response = FeasibilityResponse.model_validate(
                feasibility_get.json()
            )
            opportunities = feasibility_response_to_opportunity_list(
                feasibility_response, product_id=search.product_id
            )

            return opportunities

        elif search.product_id == "umbra_archive_catalog":
            request_payload = {"filter-lang": "cql2-json", **search.model_dump()}
            res = httpx.post(url=settings.stac_url, json=request_payload)
            res.raise_for_status()
            opportunities = [
                stac_item_to_opportunity(o, product_id=search.product_id)
                for o in res.json()["features"]
            ]

            return opportunities
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No available products matching id {search.product_id}",
            )

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stat_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        raise HTTPException(status_code=400, detail="Not Yet Implemented")

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stat_fastapi.backend.exceptions.NotFoundException`
        if not found or access denied.
        """
        raise HTTPException(status_code=400, detail="Not Yet Implemented")
