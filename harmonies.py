
from dataclasses import dataclass


@dataclass
class Color:

    hue_offset: float = 0.0
    saturation_scale: float = 1.0
    value_scale: float = 1.0


@dataclass
class Harmony:

    name: str
    colors: list


HARMONY_SETS = [Harmony(name="analogous",
                        colors=[Color(hue_offset=15),
                                Color(hue_offset=-15),
                                Color(hue_offset=-30),
                                Color(hue_offset=30)]),
                Harmony(name="complementary",
                        colors=[Color(saturation_scale=0.7, value_scale=0.75),
                                Color(saturation_scale=0.5, value_scale=0.6),
                                Color(hue_offset=180),
                                Color(hue_offset=180, saturation_scale=0.5),
                                ]),
                Harmony(name="diad",
                        colors=[Color(saturation_scale=0.8, value_scale=0.8),
                                Color(saturation_scale=0.5, value_scale=0.5),
                                Color(hue_offset=25, saturation_scale=0.5,
                                      value_scale=0.9),
                                Color(hue_offset=25, saturation_scale=0.5,
                                      value_scale=0.5),
                                Color(hue_offset=25),

                                ]),
                Harmony(name="split-complementary",
                        colors=[Color(hue_offset=150),
                                Color(hue_offset=210)]),
                Harmony(name="double-split-complementary",
                        colors=[Color(hue_offset=-25),
                                Color(hue_offset=25),
                                Color(hue_offset=155),
                                Color(hue_offset=205)]),
                Harmony(name="monochromatic",
                        colors=[Color(saturation_scale=0.8),
                                Color(saturation_scale=0.3, value_scale=0.65),
                                Color(saturation_scale=0.5),
                                Color(saturation_scale=0.8, value_scale=0.8)
                                ]),
                Harmony(name="triad",
                        colors=[Color(hue_offset=120),
                                Color(hue_offset=240)]),
                Harmony(name="shades",
                        colors=[Color(saturation_scale=0.8),
                                Color(value_scale=0.25),
                                Color(value_scale=0.5),
                                Color(saturation_scale=0.5, value_scale=0.7)]),
                Harmony(name="squares",
                        colors=[Color(hue_offset=90),
                                Color(hue_offset=180),
                                Color(270)])
                ]
