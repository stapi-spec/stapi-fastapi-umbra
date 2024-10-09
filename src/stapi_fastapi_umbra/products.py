"""
Umbra Space Product Offerings
"""

from enum import Enum

from pydantic import BaseModel
from stapi_fastapi.models.product import Product, Provider, ProviderRole
from stapi_fastapi.models.shared import Link

from .parameters import UmbraSpotlightParameters


class SceneSizeConstraints(Enum):
    """Scene Size Contraints"""

    SCENE_5X5_KM = "5x5_KM"
    SCENE_10X10_KM = "10x10_KM"


class SpotlightConstraints(BaseModel):
    """Spotlight Constraints"""

    scene_size: SceneSizeConstraints


umbra_provider = Provider(
    name="Umbra",
    description="Global Omniscience",
    roles=[
        ProviderRole.licensor,
        ProviderRole.producer,
        ProviderRole.processor,
        ProviderRole.host,
    ],
    url="https://umbra.space",
)

canopy_docs_link = Link(
    href="https://docs.canopy.umbra.space",
    rel="documentation",
    type="docs",
    title="Canopy Documentation",
)


SPOTLIGHT_PRODUCT = Product(
    conformsTo=[
        "https://geojson.org/schema/Point.json",
    ],
    id="umbra_spotlight",
    title="Umbra Spotlight Task",
    description="Spotlight images served by creating new Orders or retrieving existing images from the archive.",
    keywords=["sar", "radar", "umbra", "spotlight"],
    license="CC-BY-4.0",
    providers=[umbra_provider],
    links=[canopy_docs_link],
    parameters=UmbraSpotlightParameters,
)

PRODUCTS = [SPOTLIGHT_PRODUCT]
