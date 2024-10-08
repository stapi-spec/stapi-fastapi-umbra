from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ProductType(StrEnum):
    GEC = "GEC"
    SIDD = "SIDD"
    SICD = "SICD"


DEFAULT_PRODUCT_TYPES: list[ProductType] = [ProductType.GEC, ProductType.SICD]


class SceneSize(StrEnum):
    FIVE_BY_FIVE = "5x5_KM"
    TEN_BY_TEN = "10x10_KM"


class SatelliteID(StrEnum):
    UMBRA_04 = "Umbra-04"
    UMBRA_05 = "Umbra-05"
    UMBRA_07 = "Umbra-07"
    UMBRA_08 = "Umbra-08"


DEFAULT_SATELLITE_IDS = [e.value for e in SatelliteID]


class UmbraSpotlightParameters(BaseModel):
    """Umbra Spotlight Parameters JSON Schema"""

    sceneSize: SceneSize = Field(
        title="Scene Size",
        default=SceneSize.FIVE_BY_FIVE,
        description="The scene size of the Spotlight image.",
    )
    grazingAngleDegrees: int = Field(
        title="Grazing Angle in Degrees",
        description="The minimum angle between the local tangent plane at the target location and the line of sight vector between the satellite and the target.",
        default=45,
        ge=40,
        le=70,
    )
    satelliteIds: list[SatelliteID] = Field(
        title="Satellite ID",
        description="The satellites to consider for this Opportunity. See https://docs.canopy.umbra.space/docs/umbra-satellites",
        default=DEFAULT_SATELLITE_IDS,
    )
    deliveryConfigId: UUID | None = Field(
        title="Delivery Config ID",
        description="https://docs.canopy.umbra.space/docs/delivery-configs",
        default=None,
    )
    productTypes: list[ProductType] = Field(
        title="Product Types",
        description="https://docs.canopy.umbra.space/docs/delivered-product-types",
        default=DEFAULT_PRODUCT_TYPES,
    )


class UmbraArchiveParameters(BaseModel):
    sar_resolution_range: float = Field(
        alias="sar:resolution_range",
        title="Range Resolution in Meters",
        description="",
        default=1,
        ge=0.25,
        le=2,
    )
    sar_azimuth_looks: int = Field(
        alias="sar:azimuth_looks",
        title="Azimuth Looks",
        description="",
        default=1,
        ge=1,
        le=8,
    )
    platform: list[SatelliteID] = Field(
        title="Satellite ID",
        description="The satellites to consider for this Opportunity. See https://docs.canopy.umbra.space/docs/umbra-satellites",
        default=DEFAULT_SATELLITE_IDS,
    )
