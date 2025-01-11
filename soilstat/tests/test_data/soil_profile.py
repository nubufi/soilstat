from soilstat.models.soil_profile import SoilProfile, SoilLayer

layer1 = SoilLayer(
    thickness=2,
    dry_unit_weight=16,
    saturated_unit_weight=18,
)

layer2 = SoilLayer(
    thickness=5,
    dry_unit_weight=16,
    saturated_unit_weight=18,
)
layer3 = SoilLayer(
    thickness=15,
    dry_unit_weight=16,
    saturated_unit_weight=18,
)

soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=1)
