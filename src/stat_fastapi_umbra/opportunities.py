from stat_fastapi.models.opportunity import Opportunity, OpportunityProperties


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
