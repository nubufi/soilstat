import pytest
from soilstat.models.soil_profile import SoilLayer, SoilProfile


def test_calc_layer_depths():
    """
    Test the calc_layer_depths() method to ensure it correctly calculates layer depths and centers.
    """
    # Create sample layers
    layer1 = SoilLayer(thickness=2.0)
    layer2 = SoilLayer(thickness=3.0)
    layer3 = SoilLayer(thickness=1.5)

    # Create a soil profile
    soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=1.0)

    # Assert calculated values for each layer
    assert soil_profile.layers[0].center == 1.0
    assert soil_profile.layers[0].depth == 2.0

    assert soil_profile.layers[1].center == 3.5
    assert soil_profile.layers[1].depth == 5.0

    assert soil_profile.layers[2].center == 6.25
    assert soil_profile.layers[2].depth == 6.5


def test_get_layer_index():
    """
    Test the get_layer_index() method to ensure it returns the correct layer index for a given depth.
    """
    # Create sample layers
    layer1 = SoilLayer(thickness=2.0)
    layer2 = SoilLayer(thickness=3.0)
    layer3 = SoilLayer(thickness=1.5)

    # Create a soil profile
    soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=1.0)

    # Test depths within each layer
    assert soil_profile.get_layer_index(1.0) == 0  # Depth in first layer
    assert soil_profile.get_layer_index(2.5) == 1  # Depth in second layer
    assert soil_profile.get_layer_index(6.0) == 2  # Depth in third layer

    # Test depth exactly at layer boundaries
    assert soil_profile.get_layer_index(2.0) == 0  # Exact bottom of first layer
    assert soil_profile.get_layer_index(5.0) == 1  # Exact bottom of second layer
    assert soil_profile.get_layer_index(6.5) == 2  # Exact bottom of third layer

    # Test depth beyond all layers
    assert (
        soil_profile.get_layer_index(10.0) == 2
    )  # Beyond all layers, should return last layer
