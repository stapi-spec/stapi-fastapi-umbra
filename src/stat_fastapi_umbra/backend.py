"""Umbra Backend Module"""

import json

import httpx
from fastapi import HTTPException, Request
from stat_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product

from stat_fastapi_umbra.products import PRODUCTS
from stat_fastapi_umbra.settings import Settings

settings = Settings.load()


class UmbraBackend:
    """Umbra STAT Backend"""

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
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
        if search.product_id == "UMBRA:SPOTLIGHT_TASK":
            raise HTTPException(status_code=404, detail="Not Implemented")
        elif search.product_id == "umbra_archive_catalog":
            request_payload = {
                "filter-lang": "cql2json",
                "filter": search.filter or {},
            }

            request_payload_json = json.dumps(request_payload)
            print(f"{request_payload_json=}")
            res = httpx.post(url=settings.stac_url, json=request_payload_json)
            res.raise_for_status()
            features = res.json()["features"]
            return features
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
