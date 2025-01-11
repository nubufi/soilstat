import pytest

from soilstat.liquefaction.spt import idriss


@pytest.mark.parametrize(
    "depth, expected",
    [
        (0, 1),
        (5, 0.96175),
        (9.15, 0.9301225),
        (10, 0.907),
        (15, 0.7735),
        (22.99, 0.560167),
        (23, 0.56),
        (25, 0.544),
        (29.99, 0.50408),
        (30, 0.5),
        (35, 0.5),
        (100, 0.5),
    ],
)
def test_calc_rd(depth, expected):
    assert pytest.approx(idriss.calc_rd(depth), 0.001) == expected


@pytest.mark.parametrize(
    "safety_factor, layer_thickness, n90, expected",
    [
        (2.5, 1.0, 10, 0),  # Safety factor > 2
        (1.5, 1.0, 10, 0.2022),  # Safety factor between 1 and 2
        (1.0, 1.0, 10, 1.3056),  # Safety factor < 1
        (1.5, 2.0, 10, 0.4044),  # Safety factor between 1 and 2, layer thickness 2m
        (1.0, 2.0, 10, 2.611),  # Safety factor < 1, layer thickness 2m
        (1.5, 1.0, 3, 0.2416),  # Safety factor between 1 and 2, n90 clamped to 3
        (1.5, 1.0, 30, 0.1415),  # Safety factor between 1 and 2, n90 clamped to 30
    ],
)
def test_calc_settlement(safety_factor, layer_thickness, n90, expected):
    assert (
        pytest.approx(
            idriss.calc_settlement(safety_factor, layer_thickness, n90), 0.001
        )
        == expected
    )


@pytest.mark.parametrize(
    "n160f, effective_stress, MSF, expected_crr75, expected_crr",
    [
        (10, 100, 7.5, 11.3118, 84.83914),
        (20, 150, 7.0, 32.3114, 226.18019),
        (30, 200, 8, 93.52846, 748.227683),
    ],
)
def test_calc_crr(n160f, effective_stress, MSF, expected_crr75, expected_crr):
    crr75, crr = idriss.calc_crr(n160f, effective_stress, MSF)
    assert pytest.approx(crr75, 0.001) == expected_crr75
    assert pytest.approx(crr, 0.001) == expected_crr


def test_calc_crr_value_error():
    with pytest.raises(
        ValueError, match="The corrected N160 value should be less than 34."
    ):
        idriss.calc_crr(34, 100, 1.0)


@pytest.mark.parametrize(
    "gwt, plasticity_index, safety_factor, limit_safety_factor, depth, n160, n160f, expected",
    [
        (5, 10, 1.2, 1.1, 10, 25, 20, True),  # safety_factor >= limit_safety_factor
        (5, 10, 1.0, 1.1, 10, 25, 20, False),  # safety_factor < limit_safety_factor
        (15, 10, 1.0, 1.1, 10, 25, 20, True),  # gwt > depth
        (5, 15, 1.0, 1.1, 10, 25, 20, True),  # plasticity_index > 12
        (5, 10, 1.0, 1.1, 10, 30, 20, True),  # n160 >= 30
        (5, 10, 1.0, 1.1, 10, 25, 34, True),  # n160f >= 34
        (5, 10, 1.0, 1.1, 10, 25, 20, False),  # None of the conditions met
    ],
)
def test_check_safety(
    gwt,
    plasticity_index,
    safety_factor,
    limit_safety_factor,
    depth,
    n160,
    n160f,
    expected,
):
    assert (
        idriss.check_safety(
            gwt,
            plasticity_index,
            safety_factor,
            limit_safety_factor,
            depth,
            n160,
            n160f,
        )
        == expected
    )
