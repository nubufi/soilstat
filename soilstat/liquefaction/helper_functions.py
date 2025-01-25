from typing import Union, List
from soilstat.models.soil_profile import SoilProfile
from soilstat.models.CPT import CPTLog
from soilstat.models.SPT import SPTLog
from soilstat.models.MASW import MASWLog


def calc_msf(Mw: float) -> float:
    """
    Calculate the magnitude scaling factor (MSF) from the given moment magnitude.

    Parameters:
    - Mw (float): The moment magnitude.

    Returns:
    - float: The calculated magnitude scaling factor (MSF).
    """
    return (10**2.24) / (Mw**2.56)


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


def calc_csr(pga: float, normal_stress: float, rd: float) -> float:
    """
    Calculate the cyclic stress ratio (CSR) based on the given parameters.

    Parameters:
    - pga (float): The peak ground acceleration.
    - normal_stress (float): The normal stress.
    - rd (float): The reduction factor.

    Returns:
    - float: The calculated cyclic stress ratio (CSR).
    """
    return 0.65 * pga * normal_stress * rd


def check_safety(
    soil_profile: SoilProfile,
    depth: float,
    safety_factor: float,
    limit_safety_factor: float,
) -> bool:
    """
    Check if the soil profile is safe at a given depth.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - depth (float): The depth (in meters).
    - safety_factor (float): The safety factor.
    - limit_safety_factor (float): The limit safety factor.

    Returns:
    - bool: True if there is no liquefaction risk in the layer, False otherwise.
    """
    gwt = soil_profile.ground_water_level
    layer = soil_profile.get_layer_at_depth(depth)
    plasticity = layer.plasticity_index

    is_safe = safety_factor >= limit_safety_factor or gwt > depth or plasticity > 12

    return is_safe


def get_all_depths(
    soil_profile: SoilProfile, exp_log: Union[SPTLog, MASWLog, CPTLog]
) -> List[float]:
    """
    Get all the depths from the soil profile and the experiment log.

    Parameters:
    - soil_profile (SoilProfile): The soil profile.
    - exp_log (Union[SPTLog, MASWLog, CPTLog]): The experiment log.

    Returns:
    - List[float]: A list of all the unique depths from the soil profile and the experiment log.
    """
    layer_depths = [layer.depth for layer in soil_profile.layers]
    exp_depths = [exp.depth for exp in exp_log.exps]

    return sorted(list(set(layer_depths + exp_depths)))
