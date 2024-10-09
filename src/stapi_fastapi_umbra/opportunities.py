from datetime import datetime
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

settings = Settings()


def stac_item_to_opportunity(item: dict, product_id: str) -> Opportunity:
    item_props = item["properties"]
    start_datetime = datetime.fromisoformat(item_props['end_datetime'])
    end_datetime = datetime.fromisoformat(item_props['start_datetime'])
    duration_seconds = (end_datetime - start_datetime).total_seconds()
    return Opportunity(
        geometry=item["geometry"],
        properties=OpportunityProperties(
            # TODO: Add additional fields here if possible to add extra properties
            product_id=product_id,
            datetime=f'{item_props['start_datetime']}/{item_props['end_datetime']}',
            duration_seconds=duration_seconds,
            grazing_angle_degrees=[item_props['umbra:grazing_angle_degrees'], item_props['umbra:grazing_angle_degrees']],
            target_azimuth_angle_degrees=[item_props['umbra:target_azimuth_angle_degrees'], item_props['umbra:target_azimuth_angle_degrees']],
            satellite_id=item_props['platform'],
            imaging_mode="SPOTLIGHT_ARCHIVE"
        ),
        links=[Link(
            rel="create-order",
            href=f"{settings.fastapi_url}/orders",
            type="application/json",
            method="POST",
            body={
                "archive_id": item["id"],
            }
        )]
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
                duration_seconds=o.durationSec,
                grazing_angle_degrees=[o.grazingAngleStartDegrees, o.grazingAngleEndDegrees],
                target_azimuth_angle_degrees=[o.targetAzimuthAngleStartDegrees, o.targetAzimuthAngleEndDegrees],
                satellite_id=o.satelliteId,
                imaging_mode="SPOTLIGHT",
            ),
            geometry=geometry,
            links=[
                Link(
                    rel="create-order",
                    href=f"{settings.fastapi_url}/orders",
                    type="application/json",
                    method="POST",
                    # TODO: body from TaskRequest
                    body={
                        "geometry": geometry.model_dump(),
                        "datetime": f"{o.windowStartAt.isoformat()}/{o.windowEndAt.isoformat()}",
                        "product_id": "umbra_spotlight"
                    }
                )
            ]
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
        deliveryConfigId='09530dcb-eecb-4235-b409-0d6381b5e909',
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
