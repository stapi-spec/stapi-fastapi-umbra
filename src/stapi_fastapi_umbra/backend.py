"""Umbra Backend Module"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from stapi_fastapi.models.opportunity import Opportunity, OpportunityRequest
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product

from stapi_fastapi_umbra.client import AuthorizationError, Client
from stapi_fastapi_umbra.products import PRODUCTS
from stapi_fastapi_umbra.settings import Settings

settings = Settings.load()

logger = logging.getLogger(__name__)


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
        Search for ordering opportunities for the given search parameters.
        Opportunities might include existing images from the archive or
        new opportunities from feasibility.

        Backends must validate search constraints and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        if search.product_id != "umbra_spotlight":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No available products matching id {search.product_id}",
            )

        start_time, end_time = search.datetime

        now_utc = datetime.now(tz=timezone.utc)

        archive_included = start_time < now_utc
        archive_only = end_time < now_utc

        settings = Settings()
        client = Client(
            canopy_api_url=settings.canopy_api_url,
            canopy_token=settings.canopy_token,
        )

        try:
            opportunities_from_archive = (
                await client.get_opportunities_from_archive(search)
                if archive_included
                else []
            )
        except Exception:
            logger.exception("Failed to retrieve opportunities from archive")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve opportunities from archive",
            )

        try:
            opportunities_from_feasibility = (
                (await client.get_opportunities_from_feasibility(search))
                if not archive_only
                else []
            )
        except AuthorizationError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(err),
            )
        except Exception:
            logger.exception("Failed to retrieve opportunities from feasibility")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve opportunities from feasibility",
            )

        return opportunities_from_archive + opportunities_from_feasibility

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.

        Backends must validate order payload and raise
        `stapi_fastapi.backend.exceptions.ConstraintsException` if not valid.
        """
        if search.product_id != "umbra_spotlight":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No available products matching id {search.product_id}",
            )

        client = Client(
            canopy_api_url=settings.canopy_api_url,
            canopy_token=settings.canopy_token,
        )

        order = client.create_order_from_opportunity_request(search)

        return order

    async def get_order(self, order_id: str, request: Request) -> Order:
        """
        Get details for order with `order_id`.

        Backends must raise `stapi_fastapi.backend.exceptions.NotFoundException`
        if not found or access denied.
        """

        client = Client(
            canopy_api_url=settings.canopy_api_url,
            canopy_token=settings.canopy_token,
        )

        order = client.get_order_by_id(order_id)

        return order
