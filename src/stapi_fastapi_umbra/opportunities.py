from uuid import uuid4

from geojson_pydantic import Point
from stapi_fastapi.models.opportunity import (Opportunity,
                                              OpportunityProperties,
                                              OpportunityRequest)
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.shared import Link

# from stapi_fastapi_umbra.products import SpotlightConstraints
from stapi_fastapi_umbra.models import (FeasibilityRequest,
                                        FeasibilityResponse, ImagingMode,
                                        SpotlightConstraints, TaskRequest,
                                        TaskResponse)
from stapi_fastapi_umbra.settings import Settings

settings = Settings.load()

def stac_item_to_opportunity(item: dict, product_id: str) -> Opportunity:
    item_props = item["properties"]
    return Opportunity(
        geometry=item["geometry"],
        properties=OpportunityProperties(
            # TODO: Add additional fields here if possible to add extra properties
            product_id=product_id,
            datetime=f'{item_props['start_datetime']}/{item_props['end_datetime']}',
        ),
    )


def opportunity_request_to_feasibility_request(
    opportunity_request: OpportunityRequest,
) -> FeasibilityRequest:
    start_time, end_time = opportunity_request.datetime
    geometry = opportunity_request.geometry
    if not isinstance(geometry, Point):
        raise ValueError(
            "OpportunityRequest.geometry is restricted to a Point for this product"
        )

    return FeasibilityRequest(
        imagingMode=ImagingMode.SPOTLIGHT,
        spotlightConstraints=SpotlightConstraints(
            geometry=geometry,
        ),
        windowStartAt=start_time,
        windowEndAt=end_time,
    )


def feasibility_response_to_opportunity_list(
    feasibility_response: FeasibilityResponse, product_id: str
) -> list[Opportunity]:
    geometry = feasibility_response.feasibilityRequest.spotlightConstraints.geometry
    return [
        Opportunity(
            properties=OpportunityProperties(
                product_id=product_id,
                datetime=f"{o.windowStartAt.isoformat()}/{o.windowEndAt.isoformat()}",
            ),
            geometry=geometry,
        )
        for o in feasibility_response.opportunities
    ]


def opportunity_request_to_task_request(opportunity_request: OpportunityRequest) -> TaskRequest:
    start_time, end_time = opportunity_request.datetime
    geometry = opportunity_request.geometry
    if not isinstance(geometry, Point):
        raise ValueError(
            "OpportunityRequest.geometry is restricted to a Point for this product"
        )

    return TaskRequest(
        taskName=f"stapi-sprint-{uuid4()}",
        imagingMode=ImagingMode.SPOTLIGHT,
        spotlightConstraints=SpotlightConstraints(
            geometry=geometry,
        ),
        windowStartAt=start_time,
        windowEndAt=end_time,
        deliveryConfigId=None,  # set for live environment
        userOrderId="stapi-sprint"
    )


def task_response_to_order(task_response: TaskResponse, product_id: str) -> Order:
    task_url = f"{settings.canopy_url}/tasks/{task_response.id}"
    return Order(
        id=str(task_response.id),
        geometry=task_response.properties.spotlightConstraints.geometry,
        properties=OpportunityProperties(
            product_id=product_id,
            datetime=f"{task_response.properties.windowStartAt.isoformat()}/{task_response.properties.windowEndAt.isoformat()}",
        ),
        links=[Link(
            href=task_url,
            rel="task"
        )]
    )
