from dataclasses import dataclass, field
from typing import List

from soilstat.models.soil_profile import SoilLayer


@dataclass
class SptExp:
    """
    Represents an SPT (Standard Penetration Test) experiment with various parameters.
    """

    depth: float
    n: int
    n60: int = 0
    n90: int = 0
    n160: int = 0
    n160f: int = 0
    cr: float = 0
    cn: float = 0
    alpha: float = 0
    beta: float = 0


class SPT:
    """
    Represents a collection of SPT experiments and associated correction factors.
    """

    exps: List[SptExp] = field(default_factory=list)
    energy_correction_factor: float = 1.0
    diameter_correction_factor: float = 1.0
    sampler_correction_factor: float = 1.0
    average_n: int = 0

    def __init__(
        self,
        exps: List[SptExp],
        energy_correction_factor: float = 0,
        diameter_correction_factor: float = 0,
        sampler_correction_factor: float = 0,
    ):
        self.exps = exps
        self.energy_correction_factor = energy_correction_factor
        self.diameter_correction_factor = diameter_correction_factor
        self.sampler_correction_factor = sampler_correction_factor
        self.average_n = self.calc_average_n()

    def calc_average_n(self) -> int:
        """
        Calculates the average N value for the SPT experiments.
        """
        return int(sum(exp.n for exp in self.exps) / len(self.exps))

    def correct_n(self, n: int, depth: float, soil_layer: SoilLayer) -> int:
        """
        Corrects the N value based on correction factors and soil properties.
        """
        # Implement later
        return 0
