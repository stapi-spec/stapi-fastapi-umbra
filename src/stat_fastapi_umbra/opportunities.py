from geojson_pydantic import Point
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityProperties,
    OpportunityRequest,
)

# from stat_fastapi_umbra.products import SpotlightConstraints
from stat_fastapi_umbra.models import (
    FeasibilityRequest,
    FeasibilityResponse,
    ImagingMode,
    SpotlightConstraints,
)


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
    constraints = {}
    filter_args = opportunity_request.filter.get("args")
    for arg in filter_args:
        if arg["op"] == ">=":
            prefix = "min"
        elif arg["op"] == "<=":
            prefix = "max"

        inner_args = arg[0]["args"]
        key = inner_args[0]["property"]
        val = inner_args[1]
        constraints[f"{prefix}{key.upper()}"] = val

    return FeasibilityRequest(
        imagingMode=ImagingMode.SPOTLIGHT,
        spotlightConstraints=SpotlightConstraints(
            geometry=geometry,
            sceneSize=filter.get("sceneSize"),
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
