from soilstat.models.MASW import MASWExp, MASWLog
from soilstat.models.soil_profile import SoilProfile, SoilLayer
from typing import Dict, Tuple, List
import soilstat.liquefaction.helper_functions as hf
from soilstat.liquefaction.settlement import settlement_obj


def calc_crr(
    vs1: float, vs1c: float, effective_stress: float, MSF: float
) -> Tuple[float, float]:
    """
    Calculate the cyclic resistance ratio.

    Parameters:
    - vs1 (float): The shear wave velocity.
    - vs1c (float): The shear wave velocity at 1m depth.
    - effective_stress (float): The effective stress.

    Returns:
    - Tuple[float, float]: A tuple containing the following values:
        - crr75: The cyclic resistance ratio for 7.5 Magnitude of earthquake.
        - crr: The cyclic resistance ratio.
    """
    crr75 = effective_stress * (
        0.03 * (vs1 / 100) ** 2 + 0.09 * (vs1c - vs1) - 0.09 / vs1c
    )
    crr = crr75 * MSF

    return crr75, crr


def calc_vs1c(fine_content: float) -> float:
    """
    Calculate the value of `VS1c` based on the fine content percentage.

    The calculation is based on predefined conditions for different ranges of fine content:
    - If fine_content <= 5: `VS1c = 215`
    - If 5 < fine_content <= 35: `VS1c = 215 - 0.5 * (fine_content - 5)`
    - If fine_content > 35: `VS1c = 200`

    Args:
        fine_content (Union[int, float]): The percentage of fine content.

    Returns:
        float: The calculated `VS1c` value.
    """
    if fine_content <= 5:
        return 215
    elif 5 < fine_content <= 35:
        return 215 - 0.5 * (fine_content - 5)
    else:
        return 200


def calc_cn(effective_stress: float) -> float:
    """
    Calculate the value of `CN` based on the effective stress.

    Parameters:
    - effective_stress (float): The effective stress.

    Returns:
    - float: The calculated value of `CN`.
    """
    return min(1.7, 3.16 * (1 / effective_stress) ** 0.5)


def analyse_for_layer(
    soil_profile: SoilProfile,
    exp: MASWExp,
    depth: float,
    MSF: float,
    pga: float,
    limit_safety_factor=1.1,
) -> Dict[str, float]:
    """
    Analyse the soil profile for a given layer.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - exp (MASWExp): The MASW experiment.
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
    soil_layer = soil_profile.get_layer_at_depth(depth)
    fine_content = soil_layer.fine_content
    vs = exp.shear_wave_velocity

    rd = hf.calc_rd(soil_layer.depth)

    effective_stress = soil_profile.calc_effective_stress(depth)
    normal_stress = soil_profile.calc_normal_stress(depth)

    cn = calc_cn(effective_stress)
    vs1c = calc_vs1c(fine_content)

    vs1 = vs * cn

    csr = hf.calc_csr(pga, normal_stress, rd)

    if vs1 >= vs1c:
        return {
            "CSR": csr,
            "CRR75": 0,
            "CRR": 0,
            "rd": rd,
            "normalStress": normal_stress,
            "effectiveStress": effective_stress,
            "safetyFactor": 0,
            "settlement": 0,
            "is_safe": True,
        }

    crr75, crr = calc_crr(vs1, vs1c, effective_stress, MSF)
    safety_factor = crr / csr

    is_safe = hf.check_safety(soil_profile, depth, safety_factor, limit_safety_factor)
    settlement = settlement_obj.calc_settlement_via_vs1c(
        safety_factor, soil_layer.thickness, vs1c
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
    soil_profile: SoilProfile, masw_log: MASWLog, Mw: float, pga: float
) -> List:
    """
    Analyse the soil profile for liquefaction.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - masw_log (MASWLog): The MASW log.
    - Mw (float): The moment magnitude.
    - pga (float): The peak ground acceleration (in g).

    Returns:
    - Dict: A dictionary containing the following keys:
        - safetyFactor: The safety factor.
        - settlement: The calculated settlement.
    """
    MSF = hf.calc_msf(Mw)
    unique_depths = hf.get_all_depths(soil_profile, masw_log)
    results = []
    for depth in unique_depths:
        exp = masw_log.get_exp_at_depth(depth)
        layer_result = analyse_for_layer(soil_profile, exp, depth, MSF, pga)
        results.append(layer_result)

    return results
