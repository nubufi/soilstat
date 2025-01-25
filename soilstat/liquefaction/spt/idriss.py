from soilstat.models.SPT import SPTLog, SPTExp
from soilstat.models.soil_profile import SoilProfile
from typing import Dict, List
import soilstat.liquefaction.helper_functions as hf
from soilstat.liquefaction.settlement import settlement_obj


def calc_crr(effective_stress: float, n160f: float, MSF: float):
    """
    Calculate the cyclic resistance ratio.

    Parameters:
    - effective_stress (float): The effective stress.
    - n160f (float): The corrected N160 value.
    - MSF (float): The magnitude scaling factor.

    Returns:
    - Tuple[float, float]: A tuple containing the following values:
        - crr75: The cyclic resistance ratio for 7.5 Magnitude of earthquake.
        - crr: The cyclic resistance ratio.
    """
    crr75 = effective_stress * (
        (1 / (34 - n160f)) + (n160f / 135) + (50 / ((10 * n160f + 45) ** 2)) - 0.005
    )

    crr = crr75 * MSF

    return crr75, crr


def analyse_for_layer(
    soil_profile: SoilProfile,
    exp: SPTExp,
    depth: float,
    MSF: float,
    pga: float,
    limit_safety_factor=1.1,
) -> Dict[str, float]:
    """
    Analyse the soil profile for a given layer.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - exp (SptExp): The SPT experiment.
    - depth (float): The depth of the layer.
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

    rd = hf.calc_rd(depth)
    effective_stress = soil_profile.calc_effective_stress(depth)
    normal_stress = soil_profile.calc_normal_stress(depth)

    csr = hf.calc_csr(pga, normal_stress, rd)

    if n160f >= 34:
        raise ValueError("The corrected N160 value should be less than 34.")

    crr75, crr = calc_crr(effective_stress, n160f, MSF)

    safety_factor = crr / csr

    layer = soil_profile.get_layer_at_depth(depth)

    is_safe = (
        hf.check_safety(soil_profile, depth, safety_factor, limit_safety_factor)
        or n160 >= 30
        or n160f >= 34
    )

    settlement = settlement_obj.calc_settlement_via_n90(
        safety_factor, layer.thickness, exp.n90
    )

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
    soil_profile: SoilProfile, spt_log: SPTLog, Mw: float, pga: float
) -> List:
    """
    Analyse the soil profile for liquefaction.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - spt_log (SPTLog): The corrected SPT log.
    - Mw (float): The moment magnitude.
    - pga (float): The peak ground acceleration (in g).

    Returns:
    - Dict: A dictionary containing the following keys:
        - safetyFactor: The safety factor.
        - settlement: The calculated settlement.
    """
    MSF = hf.calc_msf(Mw)
    unique_depths = hf.get_all_depths(soil_profile, spt_log)
    results = []
    for depth in unique_depths:
        exp = spt_log.get_exp_at_depth(depth)
        layer_result = analyse_for_layer(soil_profile, exp, depth, MSF, pga)
        results.append(layer_result)

    return results
