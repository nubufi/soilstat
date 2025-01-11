from pydantic import BaseModel, Field
from typing import Optional


class Building(BaseModel):
    "Pydantic model for a building"

    foundation_depth: Optional[float] = Field(
        None,
        ge=0,
        description="The distance from bottom of the foundation to soil surface (m)",
    )
    foundation_length: Optional[float] = Field(
        None, gt=0, description="The longer side of the foundation (m)"
    )
    foundation_width: Optional[float] = Field(
        None, gt=0, description="The shorter side of the foundation (m)"
    )
    foundation_angle: Optional[float] = Field(
        None,
        ge=0,
        lt=90,
        description="Angle of the foundation to the soil surface (degrees)",
    )
    vertical_load: Optional[float] = Field(
        None, ge=0, description="The vertical load applied by the building (kN)"
    )
    horizontal_load_x: Optional[float] = Field(
        None,
        ge=0,
        description="The horizontal load applied to the building from the along the length of foundation (kN)",
    )
    horizontal_load_y: Optional[float] = Field(
        None,
        ge=0,
        description="The horizontal load applied to the building from the along the width of foundation (kN)",
    )
