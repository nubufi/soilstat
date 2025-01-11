import pytest
from soilstat.tests.test_data.soil_profile import soil_profile
from soilstat.models.soil_profile import SoilLayer, SoilProfile


def test_calc_layer_depths():
    """
    Test the calc_layer_depths() method to ensure it correctly calculates layer depths and centers.
    """
    # Create sample layers
    # Assert calculated values for each layer
    assert soil_profile.layers[0].center == 1.0
    assert soil_profile.layers[0].depth == 2.0

    assert soil_profile.layers[1].center == 4.5
    assert soil_profile.layers[1].depth == 7.0

    assert soil_profile.layers[2].center == 14.5
    assert soil_profile.layers[2].depth == 22


def test_get_layer_index():
    """
    Test the get_layer_index() method to ensure it returns the correct layer index for a given depth.
    """
    # Test depths within each layer
    assert soil_profile.get_layer_index(1.0) == 0  # Depth in first layer
    assert soil_profile.get_layer_index(2.5) == 1  # Depth in second layer
    assert soil_profile.get_layer_index(8.0) == 2  # Depth in third layer

    # Test depth exactly at layer boundaries
    assert soil_profile.get_layer_index(2.0) == 0  # Exact bottom of first layer
    assert soil_profile.get_layer_index(7.0) == 1  # Exact bottom of second layer
    assert soil_profile.get_layer_index(22) == 2  # Exact bottom of third layer

    # Test depth beyond all layers
    assert (
        soil_profile.get_layer_index(30.0) == 2
    )  # Beyond all layers, should return last layer


def test_calc_normal_stress_single_layer():
    """
    Test normal stress calculation for a soil profile with a single layer.
    """
    # Define a single soil layer
    layer = SoilLayer(
        depth=3.0, dry_unit_weight=2.0, saturated_unit_weight=2.5, thickness=3.0
    )

    # Create a soil profile with GWT at 2.0 meters
    soil_profile = SoilProfile(layers=[layer], ground_water_level=2.0)

    # Test stress at different depths
    assert soil_profile.calc_normal_stress(1.0) == pytest.approx(
        2.0, rel=1e-3
    )  # Above GWT
    assert soil_profile.calc_normal_stress(2.0) == pytest.approx(
        4.0, rel=1e-3
    )  # At GWT
    assert soil_profile.calc_normal_stress(3.0) == pytest.approx(
        6.5, rel=1e-3
    )  # Below GWT


def test_calc_normal_stress_multiple_layers():
    """
    Test normal stress calculation for a soil profile with multiple layers.
    """
    # Define multiple soil layers
    layer1 = SoilLayer(dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0)
    layer2 = SoilLayer(dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0)
    layer3 = SoilLayer(dry_unit_weight=2.0, saturated_unit_weight=2.2, thickness=1.5)

    # Create a soil profile with GWT at 3.0 meters
    soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=3.0)

    # Test stress at different depths
    assert soil_profile.calc_normal_stress(1.0) == pytest.approx(
        1.8, rel=1e-3
    )  # In layer 1, above GWT
    assert soil_profile.calc_normal_stress(3.0) == pytest.approx(
        5.5, rel=1e-3
    )  # At GWT, end of layer 1
    assert soil_profile.calc_normal_stress(4.0) == pytest.approx(
        7.6, rel=1e-3
    )  # In layer 2, below GWT
    assert soil_profile.calc_normal_stress(6.0) == pytest.approx(
        11.9, rel=1e-3
    )  # In layer 3, below GWT


def test_calc_normal_stress_full_saturation():
    """
    Test normal stress calculation when the GWT is below all layers (fully saturated profile).
    """
    # Define multiple soil layers
    layer1 = SoilLayer(dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0)
    layer2 = SoilLayer(dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0)

    # Create a soil profile with GWT at 0.0 (fully saturated profile)
    soil_profile = SoilProfile(layers=[layer1, layer2], ground_water_level=0.0)

    # Test stress at different depths
    assert soil_profile.calc_normal_stress(2.0) == pytest.approx(
        4.0, rel=1e-3
    )  # Layer 1, fully saturated
    assert soil_profile.calc_normal_stress(5.0) == pytest.approx(
        10.3, rel=1e-3
    )  # Layer 2, fully saturated


def test_calc_normal_stress_full_dry():
    """
    Test normal stress calculation when the GWT is above all layers (fully dry profile).
    """
    # Define multiple soil layers
    layer1 = SoilLayer(dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0)
    layer2 = SoilLayer(dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0)

    # Create a soil profile with GWT above all layers
    soil_profile = SoilProfile(layers=[layer1, layer2], ground_water_level=10.0)

    # Test stress at different depths
    assert soil_profile.calc_normal_stress(2.0) == pytest.approx(
        3.6, rel=1e-3
    )  # Layer 1, fully dry
    assert soil_profile.calc_normal_stress(5.0) == pytest.approx(
        9.3, rel=1e-3
    )  # Layer 2, fully dry


def test_calc_normal_stress_at_boundary():
    """
    Test normal stress calculation at layer boundaries and GWT boundaries.
    """
    # Define multiple soil layers
    layer1 = SoilLayer(dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0)
    layer2 = SoilLayer(dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0)

    # Create a soil profile with GWT at 2.0 meters (boundary of layer 1 and GWT)
    soil_profile = SoilProfile(layers=[layer1, layer2], ground_water_level=2.0)

    # Test stress at the boundary between layers and at GWT
    assert soil_profile.calc_normal_stress(2.0) == pytest.approx(
        3.6, rel=1e-3
    )  # At GWT and layer 1 boundary
    assert soil_profile.calc_normal_stress(5.0) == pytest.approx(
        9.9, rel=1e-3
    )  # At layer 2 boundary


def test_calc_effective_stress():
    """
    Test effective stress calculation for a soil profile with multiple layers.
    """
    # Define multiple soil layers
    layer1 = SoilLayer(
        depth=2.0, dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0
    )
    layer2 = SoilLayer(
        depth=5.0, dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0
    )
    layer3 = SoilLayer(
        depth=6.5, dry_unit_weight=2.0, saturated_unit_weight=2.2, thickness=1.5
    )

    # Create a soil profile with GWT at 3.0 meters
    soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=3.0)

    # Test effective stress at different depths
    assert soil_profile.calc_effective_stress(1.0) == pytest.approx(
        1.8, rel=1e-3
    )  # Above GWT
    assert soil_profile.calc_effective_stress(3.0) == pytest.approx(
        5.5, rel=1e-3
    )  # At GWT
    assert soil_profile.calc_effective_stress(4.0) == pytest.approx(
        6.62, rel=1e-3
    )  # Below GWT
    assert soil_profile.calc_effective_stress(6.0) == pytest.approx(
        8.956, rel=1e-3
    )  # Below GWT


def test_calc_effective_stress_full_saturation():
    """
    Test effective stress when the GWT is below all layers (fully saturated).
    """
    # Define multiple soil layers
    layer1 = SoilLayer(
        depth=2.0, dry_unit_weight=1.8, saturated_unit_weight=2.0, thickness=2.0
    )
    layer2 = SoilLayer(
        depth=5.0, dry_unit_weight=1.9, saturated_unit_weight=2.1, thickness=3.0
    )

    # Create a soil profile with GWT below all layers
    soil_profile = SoilProfile(layers=[layer1, layer2], ground_water_level=0.0)

    # Test effective stress at different depths
    assert soil_profile.calc_effective_stress(2.0) == pytest.approx(
        2.038, rel=1e-3
    )  # Fully saturated
    assert soil_profile.calc_effective_stress(5.0) == pytest.approx(
        5.395, rel=1e-3
    )  # Fully saturated
