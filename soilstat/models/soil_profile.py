from pydantic import BaseModel
from typing import List, Optional


class SoilLayer(BaseModel):
    """
    Pydantic model representing a soil layer with various geotechnical properties.
    All fields are optional by default.
    """

    soil_class: Optional[str] = None
    depth: Optional[float] = None  # meter
    center: Optional[float] = None  # meter
    is_cohesive: Optional[bool] = None
    damping_ratio: Optional[float] = None  # percentage
    thickness: float  # meter
    dry_unit_weight: Optional[float] = None  # t/m^3
    saturated_unit_weight: Optional[float] = None  # t/m^3
    fine_content: Optional[float] = None  # percentage
    liquid_limit: Optional[float] = None  # percentage
    plastic_limit: Optional[float] = None  # percentage
    plasticity_index: Optional[float] = None  # percentage
    undrained_shear_strength: Optional[float] = None  # t/m^2
    cohesion: Optional[float] = None  # t/m^2
    friction_angle: Optional[float] = None  # degrees
    effective_friction_angle: Optional[float] = None  # degrees
    water_content: Optional[float] = None  # percentage
    poissons_ratio: Optional[float] = None
    elastic_modulus: Optional[float] = None  # t/m^2
    void_ratio: Optional[float] = None
    recompression_index: Optional[float] = None
    compression_index: Optional[float] = None
    preconsolidation_pressure: Optional[float] = None  # t/m^2
    volume_compressibility_coefficient: Optional[float] = None
    shear_wave_velocity: Optional[float] = None  # m/s
    spt_n: Optional[int] = None
    cone_resistance: Optional[float] = None
    rqd: Optional[float] = None
    is50: Optional[float] = None
    kp: Optional[float] = None


class SoilProfile:
    """
    Pydantic model representing a soil profile with multiple soil layers.
    """

    layers: List[SoilLayer]
    ground_water_level: float  # meter

    def __init__(self, layers: List[SoilLayer], ground_water_level: float):
        self.layers = layers
        self.ground_water_level = ground_water_level
        self.calc_layer_depths()

    def calc_layer_depths(self) -> None:
        """
        Calculates the center and bottom depth of each layer and updates the SoilLayer objects in the profile.
        """
        if not self.layers:
            return

        for layer in self.layers:
            if layer.thickness is None:
                raise ValueError("Thickness of soil layer must be specified.")

        if len(self.layers) == 1:
            self.layers[0].center = self.layers[0].thickness / 2
            self.layers[0].depth = self.layers[0].thickness
            return

        # Initialize the bottom depth and center for the first layer
        bottom = self.layers[0].thickness
        center = bottom / 2

        # Iterate through the layers to calculate center and bottom depth
        for i, layer in enumerate(self.layers):
            if i > 0:
                thickness = layer.thickness
                center = bottom + thickness / 2
                bottom += thickness

            self.layers[i].center = center
            self.layers[i].depth = bottom

    def get_layer_index(self, depth: float) -> int:
        """
        Returns the index of the soil layer at the specified depth.
        """
        for i, layer in enumerate(self.layers):
            if layer.depth >= depth:
                return i

        return len(self.layers) - 1
