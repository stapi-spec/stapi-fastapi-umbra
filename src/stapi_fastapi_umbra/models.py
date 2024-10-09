from enum import Enum
from uuid import UUID

from geojson_pydantic import Point
from pydantic import AwareDatetime, BaseModel, Field


class ImagingMode(Enum):
    """ImagingMode Enum"""

    SPOTLIGHT = "SPOTLIGHT"


class Polarization(Enum):
    """Polarization Enum"""

    HH = "HH"
    VV = "VV"


class SpotlightConstraints(BaseModel):
    """SpotlightConstraints Model for Umbra API"""

    geometry: Point
    polarization: Polarization = Polarization.HH
    rangeResolutionMinMeters: float = Field(default=1, ge=0.25, le=2)
    multilookFactor: float = 1
    grazingAngleMinDegrees: float = 30
    grazingAngleMaxDegrees: float = 70
    targetAzimuthAngleStartDegrees: float = 0
    targetAzimuthAngleEndDegrees: float = 360
    sceneSize: str = "5x5_KM"


class FeasibilityRequest(BaseModel):
    """FeasibilityRequest model for Umbra"""

    imagingMode: ImagingMode = ImagingMode.SPOTLIGHT
    spotlightConstraints: SpotlightConstraints
    windowStartAt: AwareDatetime
    windowEndAt: AwareDatetime


class UmbraOpportunity(BaseModel):
    windowStartAt: AwareDatetime
    windowEndAt: AwareDatetime
    durationSec: float
    grazingAngleStartDegrees: float


class FeasibilityResponse(BaseModel):
    """FeasibilityResponse model for Umbra"""

    id: str
    createdAt: AwareDatetime
    updatedAt: AwareDatetime
    opportunities: list[UmbraOpportunity]
    feasibilityRequest: FeasibilityRequest


class TaskRequest(BaseModel):
    taskName: str
    imagingMode: ImagingMode
    spotlightConstraints: SpotlightConstraints
    windowStartAt: AwareDatetime
    windowEndAt: AwareDatetime
    deliveryConfigId: str | None
    userOrderId: str | None


class TaskResponseProperties(BaseModel):
    spotlightConstraints: SpotlightConstraints
    windowStartAt: AwareDatetime
    windowEndAt: AwareDatetime


class TaskResponse(BaseModel):
    id: UUID
    geometry: Point
    properties: TaskResponseProperties
