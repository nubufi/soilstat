import math
from typing import Tuple, Annotated
from pydantic import Field, validate_call


@validate_call
def calc_bearing_capacity_factors(
    phi: Annotated[float, Field(ge=0, le=90)],
) -> Tuple[float, float, float]:
    """
    Computes the bearing capacity factors Nc, Nq, and Ng based on the friction angle (phi).

    Parameters:
        phi (float): Friction angle in degrees.

    Returns:
        Tuple[float, float, float]: A tuple containing (Nc, Nq, Ng) bearing capacity factors.
    """
    phi_rad = math.radians(phi)

    nq = math.exp(math.pi * math.tan(phi_rad)) * math.pow(
        math.tan(math.radians(45 + phi / 2)), 2
    )

    if phi == 0:
        nc = 5.14
    else:
        nc = (nq - 1) / math.tan(phi_rad)

    ng = 2 * (nq - 1) * math.tan(phi_rad)

    return nc, nq, ng


@validate_call
def calc_shape_factors(
    foundation_width: Annotated[float, Field(gt=0)],
    foundation_length: Annotated[float, Field(gt=0)],
    nq: Annotated[float, Field(gt=0)],
    nc: Annotated[float, Field(gt=0)],
    phi: Annotated[float, Field(ge=0, le=90)],
) -> Tuple[float, float, float]:
    """
    Calculate the shape factors (Sc, Sq, and Sg) based on the provided inputs.

    Parameters:
        w (float): Width of the foundation (m).
        l (float): Length of the foundation (m).
        nq (float): Bearing capacity factor Nq.
        nc (float): Bearing capacity factor Nc.
        phi (float): Angle of internal friction in degrees.

    Returns:
        Tuple[float, float, float]: A tuple containing (Sc, Sq, Sg) shape factors.
    """
    if phi < 0 or phi > 90:
        raise ValueError("Phi must be between 0 and 90 degrees")
    # Calculate width / length ration
    w_l = foundation_width / foundation_length

    # Calculate Sc
    sc = 1 + w_l * (nq / nc)

    # Calculate Sq
    sq = 1 + w_l * math.tan(math.radians(phi))

    # Calculate Sg
    sg = 1 - 0.4 * w_l
    sg = max(sg, 0.6)  # Ensure Sg is not less than 0.6

    return sc, sq, sg


@validate_call
def calc_load_inclination_factors(
    phi: Annotated[float, Field(ge=0, le=90)],
    cohesion: Annotated[float, Field(ge=0)],
    foundation_width: Annotated[float, Field(gt=0)],
    foundation_length: Annotated[float, Field(gt=0)],
    foundation_base_angle: Annotated[float, Field(ge=0, le=90)],
    vertical_load: Annotated[float, Field(ge=0)],
    horizontal_load_x: Annotated[float, Field(ge=0)],
    horizontal_load_y: Annotated[float, Field(ge=0)],
) -> Tuple[float, float, float]:
    """
    Calculate the load inclination factors (ic, iq, ig).

    Parameters:
        phi (float): Angle of internal friction in degrees.
        cohesion (float): Soil cohesion (kPa).
        foundation_width (float): Width of the foundation (m).
        foundation_length (float): Length of the foundation (m).
        foundation_base_angle (float): Angle of the foundation base (degrees).
        vertical_load (float): Vertical load of the building (kN).
        horizontal_load_x (float): Horizontal load in the X direction (kN).
        horizontal_load_y (float): Horizontal load in the Y direction (kN).

    Returns:
        Tuple[float, float, float]: A tuple containing (ic, iq, ig) load inclination factors.
    """
    # Base angle, dimensions, and loads
    base_angle = foundation_base_angle
    w = foundation_width
    l = foundation_length
    f = vertical_load

    w_l = foundation_width / foundation_length
    vmax = max(horizontal_load_y, horizontal_load_x)

    # Calculate bearing capacity factors
    nc, nq, _ = calc_bearing_capacity_factors(phi)

    ic, iq, ig = 1.0, 1.0, 1.0

    if base_angle > 0:
        area = w * l
        ca = cohesion * 0.75
        m = (2 + w_l) / (1 + w_l)

        if phi == 0:
            ic = 1 - m * vmax / (area * ca * nc)
            iq = 1
            ig = 1
        else:
            tan_phi_inv = 1 / math.tan(math.radians(phi))
            iq = math.pow(1 - (vmax / (f + area * ca * tan_phi_inv)), m)
            ig = math.pow(1 - (vmax / (f + area * ca * tan_phi_inv)), m + 1)
            ic = iq - (1 - iq) / (nq - 1)

    return ic, iq, ig


@validate_call
def calc_base_factors(
    phi: Annotated[float, Field(ge=0, le=90)],
    slope_angle: Annotated[float, Field(ge=0, le=90)],
    base_angle: Annotated[float, Field(ge=0, le=90)],
) -> Tuple[float, float, float]:
    """
    Calculate the base factors (bc, bq, bg).

    Parameters:
        phi (float): Angle of internal friction in degrees.
        slope_angle (float): Slope angle in degrees.
        base_angle (float): Base angle in degrees.

    Returns:
        Tuple[float, float, float]: A tuple containing (bc, bq, bg) base factors.
    """
    if phi == 0:
        bc = 1 - math.radians(slope_angle) / 5.14
    else:
        bc = 1 - 2 * math.radians(slope_angle) / (5.14 * math.tan(math.radians(phi)))

    bq = math.pow(1 - math.radians(base_angle) * math.tan(math.radians(phi)), 2)
    bg = bq

    return bc, bq, bg


@validate_call
def calc_ground_factors(
    iq: Annotated[float, Field(ge=0)],
    slope_angle: Annotated[float, Field(ge=0, le=90)],
    phi: Annotated[float, Field(ge=0, le=90)],
) -> Tuple[float, float, float]:
    """
    Calculate the ground factors (gc, gq, gg).

    Parameters:
        iq (float): Load inclination factor (between 0 and 1).
        slope_angle (float): Slope angle in degrees.
        phi (float): Angle of internal friction in degrees.

    Returns:
        Tuple[float, float, float]: A tuple containing (gc, gq, gg) ground factors.
    """
    # Calculate gc
    if phi == 0:
        gc = 1 - math.radians(slope_angle) / 5.14
    else:
        gc = iq - (1 - iq) / (5.14 * math.tan(math.radians(phi)))

    # Calculate gq and gg
    gq = math.pow(1 - math.tan(math.radians(slope_angle)), 2)
    gg = gq

    return gc, gq, gg


@validate_call
def calc_depth_factors(
    foundation_depth: Annotated[float, Field(ge=0)],
    foundation_width: Annotated[float, Field(gt=0)],
    phi: Annotated[float, Field(ge=0, le=90)],
) -> Tuple[float, float, float]:
    """
    Calculate the depth factors (dc, dq, dg).

    Args:
        foundation_depth (float): Depth of the foundation (m).
        foundation_width (float): Width of the foundation (m).
        phi (float): Angle of internal friction in degrees.

    Returns:
        Tuple[float, float, float]: A tuple containing (dc, dq, dg) depth factors.
    """
    df = foundation_depth
    w = foundation_width

    if df / w <= 1:
        db = df / w
    else:
        db = math.atan(df / w)

    # Calculate depth factors
    dc = 1 + 0.4 * db
    dq = (
        1
        + 2
        * math.tan(math.radians(phi))
        * math.pow(1 - math.sin(math.radians(phi)), 2)
        * db
    )
    dg = 1

    return dc, dq, dg
