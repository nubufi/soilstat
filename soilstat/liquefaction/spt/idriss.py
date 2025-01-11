import math
from typing import Dict, List

import numpy as np

from soilstat.models.soil_profile import SoilLayer, SoilProfile
from soilstat.models.SPT import SPT, SptExp


def calc_rd(depth: float) -> float:
    """
    Calculates the reduction factor (rd) at a given depth.

    Parameters:
    - depth (float): The depth (in meters).

    Returns:
    - float: The reduction factor (rd) at the given depth.
    """
    if depth <= 9.15:
        return 1 - 0.00765 * depth
    elif 9.15 < depth < 23:
        return 1.174 - 0.0267 * depth
    elif 23 <= depth < 30:
        return 0.744 - 0.008 * depth
    else:
        return 0.5


def calc_settlement(safety_factor: float, layer_thickness: float, n90: int) -> float:
    """
    Calculates the settlement for a single soil layer in centimeters.

    Parameters:
    - safety_factor (float): The safety factor (FS).
    - layer_thickness (float): Thickness of the layer (in meters).
    - n90 (int): The corrected blow count (N90).

    Returns:
    - float: The calculated settlement (in cm).
    """

    # Step 1: Calculate N90
    n90 = int(min(max(n90, 3), 30))  # Clamp N90 to the range [3, 30]

    # Step 2: Define constants
    a0 = 0.3773
    a1 = -0.0337
    a2 = 1.5672
    a3 = -0.1833
    b0 = 28.45
    b1 = -9.3372
    b2 = 0.7975

    # Step 3: Interpolation for q based on N90
    n90_list = [3, 6, 10, 14, 25, 30]
    q_list = [33, 45, 60, 80, 147, 200]
    q = float(np.interp(n90, n90_list, q_list))  # Interpolated q value

    # Step 4: Calculate strain based on the safety factor (FS)
    if safety_factor > 2:
        strain = 0
    elif (2 - 1 / (a2 + a3 * math.log(q))) < safety_factor < 2:
        s1 = (a0 + a1 * math.log(q)) / (
            (1 / (2 - safety_factor)) - (a2 + a3 * math.log(q))
        )
        s2 = b0 + b1 * math.log(q) + b2 * math.pow(math.log(q), 2)
        strain = min(s1, s2)
    else:
        strain = b0 + b1 * math.log(q) + b2 * math.pow(math.log(q), 2)

    # Step 5: Return settlement adjusted for layer thickness
    return strain * layer_thickness


def calc_crr(n160f: int, effective_stress: float, MSF: float) -> float:
    """
    Calculates the cyclic resistance ratio (CRR).

    Parameters:
    - n160f (int): The corrected blow count (N160f).
    - effective_stress (float): The effective stress (in kPa).
    - MSF (float): The magnitude scaling factor.

    Returns:
    - float: The cyclic resistance ratio (CRR7.5).
    - float: The corrected cyclic resistance ratio (CRR).
    """
    if n160f >= 34:
        raise ValueError("The corrected N160 value should be less than 34.")

    crr75 = effective_stress * (
        (1 / (34 - n160f)) + (n160f / 135) + (50 / ((10 * n160f + 45) ** 2)) - 0.005
    )

    crr = crr75 * MSF

    return crr75, crr


def check_safety(
    gwt: float,
    plasticity_index: float,
    safety_factor: float,
    limit_safety_factor: float,
    depth: float,
    n160: int,
    n160f: int,
) -> bool:
    """
    Check if the soil profile is safe.

    Parameters:
    - gwt (float): The groundwater table (in meters).
    - plasticity_index (float): The plasticity index.
    - safety_factor (float): The safety factor.
    - limit_safety_factor (float): The safety factor limit.
    - depth (float): The depth (in meters).
    - n160 (int): The corrected blow count (N160).
    - n160f (int): The corrected blow count (N160f).

    Returns:
    - bool: True if there is no liquefaction at the given depth, False otherwise.
    """
    is_safe = (
        safety_factor >= limit_safety_factor
        or gwt > depth
        or plasticity_index > 12
        or n160 >= 30
        or n160f >= 34
    )
    return is_safe


def analyse_for_layer(
    gwt: float,
    effective_stress: float,
    normal_stress: float,
    soil_layer: SoilLayer,
    exp: SptExp,
    MSF: float,
    pga: float,
    limit_safety_factor=1.1,
) -> Dict[str, float]:
    """
    Analyse the the given layer for liquefaction.

    Parameters:
    - gwt (float): The groundwater table (in meters).
    - effective_stress (float): The effective stress (in t/m3).
    - normal_stress (float): The normal stress (in t/m3).
    - soil_layer (SoilLayer): The soil layer.
    - exp (SptExp): The SPT experiment.
    - MSF (float): The magnitude scaling factor.
    - pga (float): The peak ground acceleration (in g).
    - limit_safety_factor (float): The safety factor limit.

    Returns:
    - Dict[str, float]: A dictionary containing the following keys:
        - CSR: The cyclic stress ratio.
        - CRR75: The cyclic resistance ratio at 75% relative density.
        - CRR: The cyclic resistance ratio.
        - rd: The reduction factor.
        - normalStress: The normal stress.
        - effectiveStress: The effectiveStress.
        - safetyFactor: The safety factor.
        - settlement: The calculated settlement in cm.
    """
    depth = exp.depth
    n160f = exp.n160f
    n160 = exp.n160

    rd = calc_rd(depth)

    csr = 0.65 * pga * normal_stress * rd

    crr75, crr = calc_crr(n160f, effective_stress, MSF)

    safety_factor = crr / csr

    is_safe = check_safety(
        gwt,
        soil_layer.plasticity_index,
        safety_factor,
        limit_safety_factor,
        depth,
        n160,
        n160f,
    )
    settlement = calc_settlement(safety_factor, soil_layer.thickness, exp.n90)

    return {
        "CSR": csr,
        "CRR75": crr75,
        "CRR": crr,
        "rd": rd,
        "safetyFactor": safety_factor,
        "normalStress": normal_stress,
        "effectiveStress": effective_stress,
        "is_safe": is_safe,
        "settlement": settlement,
    }


def analyse_liquefaction(
    soil_profile: SoilProfile, spt_log: SPT, Mw: float, pga: float
) -> List:
    """
    Analyse the soil profile for liquefaction.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - spt_log (SPT): The corrected SPT log.
    - Mw (float): The moment magnitude.
    - pga (float): The peak ground acceleration (in g).

    Returns:
    - List: A list of dictionaries containing the following keys:
        - CSR: The cyclic stress ratio.
        - CRR75: The cyclic resistance ratio at 75% relative density.
        - CRR: The cyclic resistance ratio.
        - rd: The reduction factor.
        - normalStress: The normal stress.
        - effectiveStress: The effectiveStress.
        - safetyFactor: The safety factor.
        - settlement: The calculated settlement in cm.
    """
    MSF = (10**2.24) / (Mw**2.56)
    gwt = soil_profile.ground_water_table
    results = []
    for exp in spt_log.exps:
        soil_layer = soil_profile.get_layer_at_depth(exp.depth)
        effective_stress = soil_profile.calc_effective_stress(exp.depth)
        normal_stress = soil_profile.calc_normal_stress(exp.depth)
        layer_result = analyse_for_layer(
            gwt, effective_stress, normal_stress, soil_layer, exp, MSF, pga
        )
        results.append(layer_result)

    return results
