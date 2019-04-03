"""Library of susceptibility and coverage calculation functions"""

import numpy as np


def calculate_zhu2016_susceptibility(
    vs30, precipitation, distance_to_coast, distance_to_rivers, water_table_depth
):
    return (
        8.801
        + np.log(vs30) * -1.918
        + precipitation * 0.0005408
        + np.minimum(distance_to_coast, distance_to_rivers) * -0.2054
        + water_table_depth * -0.0333
    )


def calculate_zhu2016_coverage(
    pgv, vs30, precipitation, distance_to_coast, distance_to_rivers, water_table_depth
):
    p = probability_transform(
        pgv * 0.334
        + calculate_zhu2016_susceptibility(
            vs30,
            precipitation,
            distance_to_coast,
            distance_to_rivers,
            water_table_depth,
        )
    )
    return 0.4915 / (1 + 42.40 * np.exp(-9.165 * p)) ** 2


def calculate_zhu2017_coverage(
    scaled_pgv,
    vs30,
    precipitation,
    distance_to_coast,
    distance_to_rivers,
    water_table_depth,
):
    return calculate_zhu2016_coverage(
        scaled_pgv,
        vs30,
        precipitation,
        distance_to_coast,
        distance_to_rivers,
        water_table_depth,
    )


def calculate_zhu2015_coastal_coverage(scaled_pga, cti, vs30):
    p = probability_transform(
        24.10 + scaled_pga * 2.067 + cti * 0.355 + np.log(vs30) * -4.784
    )
    return 0.81 * p


def calculate_zhu2016_coastal_coverage(pgv, vs30, precip, dc, dr):
    p = probability_transform(
        12.435
        + np.log(pgv) * 0.301
        + np.log(vs30) * -2.615
        + precip * 0.0005556
        + np.pow(dc, 0.5) * -0.0287
        + dr * 0.0666
        + np.pow(dc, 0.5) * dr * -0.0369
    )
    return 0.4208 / (1 + 62.59 * np.exp(-11.43 * p)) ** 2


def calculate_zhu2017_coastal_coverage(pgv, vs30, precip, dc, dr):
    return calculate_zhu2016_coastal_coverage(pgv, vs30, precip, dc, dr)


def calculate_jessee2017_susceptibility(slope, rock, cti, landcover):
    return (
        -6.3
        + np.arctan(slope) * 0.06 * 180 / np.pi
        + rock * 1
        + cti * 0.03
        + landcover * 1.0
    )


def calculate_jessee2017_probability(pgv, slope, rock, cti, landcover):
    p = probability_transform(
        np.log(pgv) * 1.65
        + calculate_jessee2017_susceptibility(slope, rock, cti, landcover)
        + np.log(pgv) * np.arctan(slope) * 180 / np.pi * 0.01
    )
    return np.exp(-7.592 + 5.237 * p - 3.042 * p ** 2 + 4.035 * p ** 3)


def probability_transform(p):
    """
    The inverse of the equation -np.log(1/P-1).
    Verification of this is left as an exercise to the reader."""
    return 1 / (np.exp(-p) + 1)
