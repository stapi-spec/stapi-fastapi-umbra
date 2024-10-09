# STAT-FASTAPI Umbra
An implementation of `stapi-fastapi` for Umbra Space proxying to the [Canopy API](https://docs.canopy.umbra.space/reference).

## Examples

### Start the server locally

```
poetry run umbra
```

### Get all products

```
curl http://127.0.0.1:8001/products
```

### Search opportunities by product

#### Archive

No authorization is required to search the public [Umbra Archive](https://docs.canopy.umbra.space/docs/archive-catalog-searching-via-stac-api).

```
curl -H "Content-Type: application/json" \
-d '{
    "geometry": {
        "type": "Point",
        "coordinates": [-112.146,40.522]
    },
    "filter": {
        "op": "=",
        "args": [
        true,
        {
            "property": "umbra:open-data-catalog"
        }
        ]
    },
    "product_id": "umbra_archive_catalog",
    "datetime": "2024-08-01T00:00:00Z/2024-09-01T00:00:00Z"
}' -X POST http://127.0.0.1:8001/opportunities
```