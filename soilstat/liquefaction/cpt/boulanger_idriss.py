import math
from soilstat.models.CPT import CPTLog, CPTExp
from soilstat.models.soil_profile import SoilProfile
from typing import Dict, Tuple, List
import soilstat.liquefaction.helper_functions as hf
from soilstat.liquefaction.settlement import settlement_obj


def calc_cn(
    m: float, qcn: float, effective_stress: float, fine_content: float
) -> float:
    """
    Calculate the Cn value iteratively based on the given parameters.

    Parameters::
    - m (float): Initial m value.
    - qcn (float): Normalized cone tip resistance.
    - effective_stress (float): Effective stress (in kPa).
    - fine_content (float): Fines content percentage.

    Returns:
    - float: The calculated Cn value.
    """
    effective_stress = max(
        effective_stress, 0.1
    )  # Ensure effective stress is at least 0.1
    cn = math.pow(10.132 / effective_stress, m)
    qc1n0 = qcn * cn
    dqc1n0 = (11.9 + qc1n0 / 14.6) * math.exp(
        1.63 - (9.7 / (fine_content + 2)) - math.pow(15.7 / (fine_content + 2), 2)
    )

    qc1ncs0 = qc1n0 + dqc1n0
    m_new = 1.338 - 0.249 * math.pow(qc1ncs0, 0.264)

    # Recursive convergence check
    if abs(m_new - m) > 0.001:
        return calc_cn(m_new, qcn, effective_stress, fine_content)
    else:
        return min(1.7, math.pow(100 / effective_stress, m))


def calc_qc1ncs(qcn: float, fine_content: float, cn: float) -> float:
    """
    Calculate qc1ncs value based on qcn, fine content, and Cn.

    Parameters::
    - qcn (float): Normalized cone tip resistance.
    - fine_content (float): Fines content percentage.
    - cn (float): Normalized correction factor.

    Returns:
    - float: The calculated qc1ncs value.
    """
    qc1n = cn * qcn
    dqc1n = (11.9 + qc1n / 14.6) * math.exp(
        1.63 - (9.7 / (fine_content + 2)) - math.pow(15.7 / (fine_content + 2), 2)
    )
    return max(min(qc1n + dqc1n, 254), 21)


def calc_rd(depth: float, mw: float) -> float:
    """
    Calculate rd at a given depth and moment magnitude (Mw).

    Parameters::
    - depth (float): Depth in meters.
    - mw (float): Moment magnitude (Mw).

    Returns:
    - float: The calculated rd value.
    """
    if depth <= 34:
        az = -1.012 - 1.126 * math.sin((depth / 11.73) + 5.133)
        bz = 0.106 + 0.118 * math.sin((depth / 11.28) + 5.142)
        return math.exp(az + bz * mw)
    else:
        return 0.12 * math.exp(0.22 * mw)


def calc_msf(mw: float, qc1ncs: float) -> float:
    """
    Calculate MSF (Magnitude Scaling Factor).

    Parameters::
    - mw (float): Moment magnitude (Mw).
    - qc1ncs (float): Normalized cone resistance corrected for fine content.

    Returns:
    - float: The calculated MSF value.
    """
    msf_max = min(2.2, 1.09 + math.pow(qc1ncs / 180, 3))
    return 1 + (msf_max - 1) * (8.64 * math.exp(-mw / 4) - 1.325)


def calc_cg(qc1ncs: float) -> float:
    """
    Calculate the Cyclic Stress Ratio (CSR) from qc1ncs value.

    Parameters:
    - qc1ncs (float): Normalized cone resistance corrected for fine content.

    Returns:
    - float: The calculated CSR value.
    """
    cg = 1 / (37.3 - 8.27 * qc1ncs**0.264)
    return min(0.3, cg)


def calc_kg(cg: float, effective_stress: float) -> float:
    """
    Calculate the stress correction factor (Kg) from effective stress.

    Parameters:
    - effective_stress (float): Effective stress (in kPa).

    Returns:
    - float: The calculated Kg value.
    """

    kg = 1 - cg * math.log(effective_stress / 101.32)
    return min(1.1, kg)


def calc_crr(
    kg: float, qc1ncs: float, msf: float, effective_stress
) -> Tuple[float, float]:
    """
    Calculate the Cyclic Resistance Ratio (CRR) from Kg and qc1ncs value.

    Parameters:
    - kg (float): Stress correction factor.
    - qc1ncs (float): Normalized cone resistance corrected for fine content.
    - msf (float): Magnitude scaling factor.
    - effective_stress (float): Effective stress (in kPa).

    Returns:
    - float: The calculated CRR value.
    """
    crr75 = (
        kg
        * math.exp(
            qc1ncs / 113
            + (qc1ncs / 1000) ** 2
            - (qc1ncs / 140) ** 3
            + (qc1ncs / 137) ** 4
            - 2.8
        )
        * effective_stress
    )
    crr = msf * crr75

    return crr75, crr


def analyse_for_layer(
    soil_profile: SoilProfile,
    exp: CPTExp,
    depth: float,
    MSF: float,
    pga: float,
    Mw: float,
    limit_safety_factor=1.1,
) -> Dict[str, float]:
    """
    Analyse the soil profile for a given layer.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - exp (CPTExp): The CPT experiment.
    - depth (float): The depth of the layer.
    - MSF (float): The magnitude scaling factor.
    - pga (float): The peak ground acceleration (in g).
    - Mw (float): The moment magnitude.
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
    rd = calc_rd(depth, Mw)
    effective_stress = soil_profile.calc_effective_stress(depth)
    normal_stress = soil_profile.calc_normal_stress(depth)

    soil_layer = soil_profile.get_layer_at_depth(depth)

    cn = calc_cn(0.5, exp.cone_resistance, effective_stress, soil_layer.fine_content)

    qc1ncs = calc_qc1ncs(exp.cone_resistance, soil_layer.fine_content, cn)
    cg = calc_cg(qc1ncs)
    kg = calc_kg(cg, effective_stress)

    csr = hf.calc_csr(pga, normal_stress, rd)
    crr75, crr = calc_crr(kg, qc1ncs, MSF, effective_stress)

    safety_factor = csr / crr

    is_safe = hf.check_safety(soil_profile, depth, safety_factor, limit_safety_factor)

    settlement = settlement_obj.calc_settlement_via_qci(
        safety_factor, soil_layer.thickness, qc1ncs
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
    soil_profile: SoilProfile, cpt_log: CPTLog, Mw: float, pga: float
) -> List:
    """
    Analyse the soil profile for liquefaction.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - cpt_log (CPTLog): The CPT log.
    - Mw (float): The moment magnitude.
    - pga (float): The peak ground acceleration (in g).

    Returns:
    - Dict: A dictionary containing the following keys:
        - safetyFactor: The safety factor.
        - settlement: The calculated settlement.
    """
    MSF = hf.calc_msf(Mw)
    unique_depths = hf.get_all_depths(soil_profile, cpt_log)
    results = []
    for depth in unique_depths:
        exp = cpt_log.get_exp_at_depth(depth)
        layer_result = analyse_for_layer(soil_profile, exp, depth, MSF, pga, Mw)
        results.append(layer_result)

    return results
