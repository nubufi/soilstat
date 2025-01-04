from soilstat.models.soil_profile import SoilProfile, SoilLayer

layer1 = SoilLayer(
    thickness=2,
    water_content=0.2,
    poissons_ratio=0.3,
    elastic_modulus=10,
    void_ratio=0.5,
    recompression_index=0.1,
    compression_index=0.2,
    preconsolidation_pressure=5,
    volume_compressibility_coefficient=0.3,
    shear_wave_velocity=100,
    spt_n=10,
    cone_resistance=20,
    rqd=0.5,
    is50=0.6,
    kp=0.7,
)

layer2 = SoilLayer(
    thickness=3,
    water_content=0.3,
    poissons_ratio=0.4,
    elastic_modulus=20,
    void_ratio=0.6,
    recompression_index=0.2,
    compression_index=0.3,
    preconsolidation_pressure=10,
    volume_compressibility_coefficient=0.4,
    shear_wave_velocity=200,
    spt_n=20,
    cone_resistance=30,
    rqd=0.6,
    is50=0.7,
    kp=0.8,
)

layer3 = SoilLayer(
    thickness=10,
    water_content=0.4,
    poissons_ratio=0.5,
    elastic_modulus=30,
    void_ratio=0.7,
    recompression_index=0.3,
    compression_index=0.4,
    preconsolidation_pressure=15,
    volume_compressibility_coefficient=0.5,
    shear_wave_velocity=300,
    spt_n=30,
    cone_resistance=40,
    rqd=0.7,
    is50=0.8,
    kp=0.9,
)

soil_profile = SoilProfile(layers=[layer1, layer2, layer3], ground_water_level=1)
