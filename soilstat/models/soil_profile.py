import copy
from typing import List
from dataclasses import dataclass


@dataclass
class SoilLayer:
    thickness: float  # meter
    dry_unit_weight: float  # t/m^3
    saturated_unit_weight: float  # t/m^3
    soil_class: str = ""
    depth: float = 0  # meter
    center: float = 0  # meter
    is_cohesive: bool = False
    damping_ratio: float = 0.05  # percentage
    fine_content: float = 0  # percentage
    liquid_limit: float = 0  # percentage
    plastic_limit: float = 0  # percentage
    plasticity_index: float = 0  # percentage
    undrained_shear_strength: float = 0  # t/m^2
    cohesion: float = 0  # t/m^2
    friction_angle: float = 0  # degrees
    effective_friction_angle: float = 0  # degrees
    water_content: float = 0  # percentage
    poissons_ratio: float = 0
    elastic_modulus: float = 0  # t/m^2
    void_ratio: float = 0
    recompression_index: float = 0
    compression_index: float = 0
    preconsolidation_pressure: float = 0  # t/m^2
    volume_compressibility_coefficient: float = 0
    shear_wave_velocity: float = 0  # m/s
    spt_n: int = 0
    cone_resistance: float = 0
    rqd: float = 0
    is50: float = 0
    kp: float = 0


class SoilProfile:
    layers: List[SoilLayer]
    ground_water_level: float

    def __init__(self, layers: List[SoilLayer], ground_water_level: float):
        self.layers = layers
        self.ground_water_level = ground_water_level
        self.validate()
        self.calc_layer_depths()

    def validate(self) -> None:
        """
        Validates the SoilProfile object.
        """
        if not self.layers:
            raise ValueError("Soil profile must contain at least one layer.")

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

    def get_layer_at_depth(self, depth: float) -> SoilLayer:
        """
        Returns the soil layer at the specified depth.
        """
        return self.layers[self.get_layer_index(depth)]

    def calc_normal_stress(self, depth: float) -> float:
        """
        Calculates the normal stress at the specified depth.
        """
        # Get the index of the layer at the given depth

        layer_index = self.get_layer_index(depth)

        # Initialize total stress
        total_stress = 0.0

        # Iterate through layers up to the layer containing the specified depth
        previous_depth = 0.0
        for i, layer in enumerate(self.layers[: layer_index + 1]):
            if i == layer_index:
                # Adjust the depth for the last layer (partial thickness)
                layer_thickness = depth - previous_depth
            else:
                # Full thickness for earlier layers
                layer_thickness = layer.thickness

            # Calculate the contribution to stress
            if self.ground_water_level >= previous_depth + layer_thickness:
                # Entirely above groundwater table (dry unit weight applies)
                total_stress += layer.dry_unit_weight * layer_thickness
            elif self.ground_water_level <= previous_depth:
                # Entirely below groundwater table (saturated unit weight applies)
                total_stress += layer.saturated_unit_weight * layer_thickness
            else:
                # Partially submerged (both dry and saturated weights apply)
                dry_thickness = self.ground_water_level - previous_depth
                submerged_thickness = layer_thickness - dry_thickness
                total_stress += (
                    layer.dry_unit_weight * dry_thickness
                    + layer.saturated_unit_weight * submerged_thickness
                )

            # Update the previous depth
            previous_depth += layer_thickness

        return total_stress

    def calc_effective_stress(self, depth: float) -> float:
        """
        Calculates the effective stress at the specified depth.
        """
        # Calculate the total normal stress at the given depth
        normal_stress = self.calc_normal_stress(depth)

        # If the depth is above the groundwater table, effective stress equals normal stress
        if self.ground_water_level >= depth:
            return normal_stress
        else:
            # Subtract pore water pressure for depths below the groundwater table
            pore_pressure = (
                depth - self.ground_water_level
            ) * 0.981  # 0.981 t/m³ is the unit weight of water
            return normal_stress - pore_pressure

    def copy(self) -> "SoilProfile":
        """
        Creates a deep copy of the SoilProfile instance.
        """
        return SoilProfile(
            layers=[copy.deepcopy(layer) for layer in self.layers],
            ground_water_level=self.ground_water_level,
        )
