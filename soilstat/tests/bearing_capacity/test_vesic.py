from pydantic import ValidationError
import pytest
from math import isclose
from soilstat.bearing_capacity.vesic import (
    calc_bearing_capacity_factors,
    calc_shape_factors,
    calc_load_inclination_factors,
    calc_base_factors,
    calc_ground_factors,
    calc_depth_factors,
)

"""Test calc_bearing_capacity_factors"""


@pytest.mark.parametrize(
    "phi, expected",
    [
        (0, (5.14, 1.0, 0.0)),
        (10, (8.345, 2.471, 0.519)),
        (30, (30.140, 18.401, 20.093)),
        (45, (133.874, 134.874, 267.748)),
    ],
)
def test_calc_bearing_capacity_factors(phi, expected):
    nc, nq, ng = calc_bearing_capacity_factors(phi)
    assert isclose(nc, expected[0], rel_tol=1e-3)
    assert isclose(nq, expected[1], rel_tol=1e-3)
    assert isclose(ng, expected[2], rel_tol=1e-3)


def test_calc_bearing_capacity_factors_invalid_input():
    with pytest.raises(ValidationError):
        calc_bearing_capacity_factors(-10)


"""Test calc_shape_factors"""


@pytest.mark.parametrize(
    "foundation_width, foundation_length, nq, nc, phi, expected",
    [
        (2, 4, 18.4, 30.1, 30, (1.306, 1.289, 0.8)),
        (3, 6, 10.0, 20.0, 20, (1.25, 1.182, 0.8)),
        (5, 5, 25.0, 40.0, 45, (1.625, 2, 0.6)),
        (4, 10, 15.0, 25.0, 35, (1.24, 1.28, 0.84)),
    ],
)
def test_calc_shape_factors(foundation_width, foundation_length, nq, nc, phi, expected):
    result = calc_shape_factors(foundation_width, foundation_length, nq, nc, phi)
    assert isclose(result[0], expected[0], rel_tol=1e-3)  # Sc
    assert isclose(result[1], expected[1], rel_tol=1e-3)  # Sq
    assert isclose(result[2], expected[2], rel_tol=1e-3)  # Sg


@pytest.mark.parametrize(
    "foundation_width, foundation_length, nq, nc, phi",
    [
        (-2, 4, 18.4, 30.1, 30),
        (3, -6, 10.0, 20.0, 20),
        (5, 5, -25.0, 40.0, 45),
        (4, 10, 15.0, -25.0, 35),
        (4, 10, 15.0, -25.0, -35),
    ],
)
def test_calc_shape_factors_invalid_input(
    foundation_width, foundation_length, nq, nc, phi
):
    with pytest.raises(ValidationError):
        calc_shape_factors(foundation_width, foundation_length, nq, nc, phi)


"""Test calc_shape_factors"""


@pytest.mark.parametrize(
    "phi, cohesion, foundation_width, foundation_length, foundation_base_angle, vertical_load, horizontal_load_x, horizontal_load_y, expected",
    [
        (0, 25, 4, 6, 10, 200, 15, 20, (0.986, 1, 1)),
        (30, 30, 5, 10, 15, 300, 20, 25, (0.98, 0.982, 0.971)),
        (45, 20, 3, 8, 20, 250, 30, 35, (0.902, 0.903, 0.851)),
        (0, 10, 3, 6, 0, 100, 5, 5, (1, 1, 1)),  # Case with base_angle == 0
    ],
)
def test_calc_load_inclination_factors(
    phi,
    cohesion,
    foundation_width,
    foundation_length,
    foundation_base_angle,
    vertical_load,
    horizontal_load_x,
    horizontal_load_y,
    expected,
):
    result = calc_load_inclination_factors(
        phi,
        cohesion,
        foundation_width,
        foundation_length,
        foundation_base_angle,
        vertical_load,
        horizontal_load_x,
        horizontal_load_y,
    )
    assert isclose(result[0], expected[0], rel_tol=1e-3)  # ic
    assert isclose(result[1], expected[1], rel_tol=1e-3)  # iq
    assert isclose(result[2], expected[2], rel_tol=1e-3)  # ig


@pytest.mark.parametrize(
    "phi, cohesion, foundation_width, foundation_length, foundation_base_angle, vertical_load, horizontal_load_x, horizontal_load_y",
    [
        (-1, 25, 4, 6, 10, 200, 15, 20),
        (30, -30, 5, 10, 15, 300, 20, 25),
        (45, 20, -3, 8, 20, 250, 30, 35),
        (0, 10, 3, -6, 0, 100, 5, 5),
        (0, 10, 3, -6, -5, 100, 5, 5),
        (0, 10, 3, -6, -5, -100, 5, 5),
        (0, 10, 3, -6, -5, -100, -5, 5),
        (0, 10, 3, -6, -5, -100, -5, -5),
    ],
)
def test_calc_load_inclination_factors_invalid_input(
    phi,
    cohesion,
    foundation_width,
    foundation_length,
    foundation_base_angle,
    vertical_load,
    horizontal_load_x,
    horizontal_load_y,
):
    with pytest.raises(ValidationError):
        calc_load_inclination_factors(
            phi,
            cohesion,
            foundation_width,
            foundation_length,
            foundation_base_angle,
            vertical_load,
            horizontal_load_x,
            horizontal_load_y,
        )


"""Test calc_base_factors"""


@pytest.mark.parametrize(
    "phi, slope_angle, base_angle, expected",
    [
        (0, 10, 5, (0.966, 1.0, 1.0)),  # Case when phi == 0
        (30, 10, 5, (0.882, 0.902, 0.902)),
        (45, 20, 10, (0.864, 0.681, 0.681)),
        (15, 5, 2, (0.873, 0.981, 0.981)),
    ],
)
def test_calc_base_factors(phi, slope_angle, base_angle, expected):
    result = calc_base_factors(phi, slope_angle, base_angle)
    assert isclose(result[0], expected[0], rel_tol=1e-3)  # bc
    assert isclose(result[1], expected[1], rel_tol=1e-3)  # bq
    assert isclose(result[2], expected[2], rel_tol=1e-3)  # bg


@pytest.mark.parametrize(
    "phi, slope_angle, base_angle",
    [
        (-4, 10, 5),  # Case when phi == 0
        (30, -10, 5),
        (45, 20, -10),
    ],
)
def test_calc_base_factors_invalid(phi, slope_angle, base_angle):
    with pytest.raises(ValidationError):
        calc_base_factors(phi, slope_angle, base_angle)


"""Test calc_ground_factors"""


@pytest.mark.parametrize(
    "iq, slope_angle, phi, expected",
    [
        (1, 10, 0, (0.966, 0.678, 0.678)),  # Case when phi == 0
        (0.9, 15, 30, (0.866, 0.536, 0.536)),
        (0.8, 20, 45, (0.7611, 0.4045, 0.4045)),
        (0.95, 5, 15, (0.914, 0.833, 0.833)),
    ],
)
def test_calc_ground_factors(iq, slope_angle, phi, expected):
    result = calc_ground_factors(iq, slope_angle, phi)
    assert isclose(result[0], expected[0], rel_tol=1e-3)  # gc
    assert isclose(result[1], expected[1], rel_tol=1e-3)  # gq
    assert isclose(result[2], expected[2], rel_tol=1e-3)  # gg


@pytest.mark.parametrize(
    "iq, slope_angle, phi",
    [
        (-11, 10, 0),
        (0.9, -15, 30),
        (0.8, 20, -45),
    ],
)
def test_calc_ground_factors_invalid_input(iq, slope_angle, phi):
    with pytest.raises(ValidationError):
        calc_ground_factors(iq, slope_angle, phi)


"""Test calc_depth_factors"""


@pytest.mark.parametrize(
    "foundation_depth, foundation_width, phi, expected",
    [
        (1, 2, 0, (1.2, 1.0, 1.0)),  # Case with phi = 0
        (1, 2, 30, (1.2, 1.144, 1.0)),  # Typical case with Df/B <= 1
        (3, 2, 45, (1.393, 1.169, 1.0)),  # Case with Df/B > 1
        (0, 2, 15, (1.0, 1.0, 1.0)),  # Edge case with Df = 0
    ],
)
def test_calc_depth_factors(foundation_depth, foundation_width, phi, expected):
    result = calc_depth_factors(foundation_depth, foundation_width, phi)
    assert isclose(result[0], expected[0], rel_tol=1e-3)  # dc
    assert isclose(result[1], expected[1], rel_tol=1e-3)  # dq
    assert isclose(result[2], expected[2], rel_tol=1e-3)  # dg


@pytest.mark.parametrize(
    "foundation_depth, foundation_width, phi",
    [
        (-1, 2, 0),  # Case with phi = 0
        (1, -2, 30),  # Typical case with Df/B <= 1
        (3, 2, -45),  # Case with Df/B > 1
    ],
)
def test_calc_depth_factors_invalid_input(foundation_depth, foundation_width, phi):
    with pytest.raises(ValidationError):
        calc_depth_factors(foundation_depth, foundation_width, phi)
