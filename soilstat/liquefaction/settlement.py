import math
import numpy as np


class LiquefactionSettlement:
    a0 = 0.3773
    a1 = -0.0337
    a2 = 1.5672
    a3 = -0.1833
    b0 = 28.45
    b1 = -9.3372
    b2 = 0.7975

    q_list = [33, 45, 60, 80, 147, 200]
    n90_list = [3, 6, 10, 14, 25, 30]
    relative_densities = [30, 40, 50, 60, 70, 80, 90]

    def n90_to_qci(self, n90: int) -> float:
        """
        Convert N90 to QCI.

        Parameters:
        - n90 (int): The N90 value.

        Returns:
        - float: The QCI value.
        """
        qci = np.interp(n90, self.n90_list, self.q_list)[0]
        return qci

    @staticmethod
    def calc_relative_density(vs1c: float) -> float:
        """
        Calculate the relative density based on the value of `VS1c`.

        Parameters:
        - vs1c (float): The value of `VS1c`.

        Returns:
        - float: The calculated relative density.
        """
        return 17.974 * (vs1c / 100) ** 1.976

    def dr_to_qci(self, relative_density: float) -> float:
        """
        Convert relative density to QCI.

        Parameters:
        - relative_density (float): The relative density.

        Returns:
        - float: The QCI value.
        """
        qci = np.interp(relative_density, self.relative_densities, self.q_list)[0]

        return qci

    def calc_volumetric_strain(
        self, corrected_tip_resistance: float, safety_factor: float
    ):
        """
        Calculate the volumetric strain.

        Parameters:
        - corrected_tip_resistance (float): The corrected tip resistance.
        - safety_factor (float): The safety factor.

        Returns:
        - float: The calculated volumetric strain.
        """

        if safety_factor > 2:
            unit_deformation = 0
        elif (
            (2 - 1 / (self.a2 + self.a3 * math.log(corrected_tip_resistance)))
            < safety_factor
            < 2
        ):
            s1 = (self.a0 + self.a1 * math.log(corrected_tip_resistance)) / (
                (1 / (2 - safety_factor))
                - (self.a2 + self.a3 * math.log(corrected_tip_resistance))
            )
            s2 = (
                self.b0
                + self.b1 * math.log(corrected_tip_resistance)
                + self.b2 * math.pow(math.log(corrected_tip_resistance), 2)
            )
            unit_deformation = min(s1, s2)
        else:
            unit_deformation = (
                self.b0
                + self.b1 * math.log(corrected_tip_resistance)
                + self.b2 * math.pow(math.log(corrected_tip_resistance), 2)
            )

        return unit_deformation

    def calc_settlement_via_n90(
        self, safety_factor: float, layer_thickness: float, n90: int
    ):
        """
        Calculate the settlement based on the N90 value.

        Parameters:
        - safety_factor (float): The safety factor.
        - layer_thickness (float): The thickness of the layer.
        - n90 (int): The N90 value.

        Returns:
        - float: The calculated settlement in meters.
        """

        n90 = int(min(max(n90, 3), 30))
        qci = self.n90_to_qci(n90)
        settlement = self.calc_volumetric_strain(qci, safety_factor)

        return settlement * layer_thickness

    def calc_settlement_via_vs1c(
        self, safety_factor: float, layer_thickness: float, vs1c: float
    ):
        """
        Calculate the settlement based on the VS1c value.

        Parameters:
        - safety_factor (float): The safety factor.
        - layer_thickness (float): The thickness of the layer.
        - vs1c (float): The value of `VS1c`.

        Returns:
        - float: The calculated settlement in meters.
        """
        relative_density = self.calc_relative_density(vs1c)
        relative_density = min(max(relative_density, 30), 90)

        qci = self.dr_to_qci(relative_density)
        settlement = self.calc_volumetric_strain(qci, safety_factor)

        return settlement * layer_thickness

    def calc_settlement_via_qci(
        self, safety_factor: float, layer_thickness: float, qci: float
    ):
        """
        Calculate the settlement based on the QCI value.

        Parameters:
        - safety_factor (float): The safety factor.
        - layer_thickness (float): The thickness of the layer.
        - qci (float): The QCI value.

        Returns:
        - float: The calculated settlement in meters.
        """
        settlement = self.calc_volumetric_strain(qci, safety_factor)

        return settlement * layer_thickness


settlement_obj = LiquefactionSettlement()
