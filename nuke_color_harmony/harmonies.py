
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
    tooltip: str


HARMONY_SETS = [Harmony(name="analogous",
                        colors=[Color(hue_offset=15),
                                Color(hue_offset=-15),
                                Color(hue_offset=-30),
                                Color(hue_offset=30)],
                        tooltip="Analogous Harmony - consists of two or more color that are side-by-side\n"
                        "on the color wheel. To select an analogous color scheme, find any color on the\n"
                        "color wheel. Then, choose two to four more colors directly to the left or right\n"
                        "of your color without skipping over any colors; also called adjoining colors."
                        ),

                Harmony(name="complementary",
                        colors=[Color(saturation_scale=0.7, value_scale=0.75),
                                Color(saturation_scale=0.5, value_scale=0.6),
                                Color(hue_offset=180),
                                Color(hue_offset=180, saturation_scale=0.5),
                                ],
                        tooltip="Complementary Harmony - created by pairing the two colors positioned\n"
                        "directly across the color wheel from one another. Each color on the wheel has\n"
                        "only one complement, which is also called its direct complement."
                        ),

                Harmony(name="diad",
                        colors=[Color(saturation_scale=0.8, value_scale=0.8),
                                Color(saturation_scale=0.5, value_scale=0.5),
                                Color(hue_offset=25, saturation_scale=0.5,
                                      value_scale=0.9),
                                Color(hue_offset=25,
                                      saturation_scale=0.5, value_scale=0.5)
                                ],
                        tooltip="Diad Harmony - a combination of two colors that are separated\n"
                        "by one color on the color wheel, ex. yellow and green or yellow-orange\n"
                        "and red-orange. While the hues in this harmony can be used on their own,\n"
                        "you will often see the diad combination used as accents colors with neutrals."
                        ),

                Harmony(name="split-complementary",
                        colors=[Color(hue_offset=150),
                                Color(hue_offset=210)],
                        tooltip="Split Complementary Harmony - One color paired with the two \n"
                        "colors on either side of that color’s direct complement,\n"
                        "also known as a divided complement. "
                        ),

                Harmony(name="double-split-complementary",
                        colors=[Color(hue_offset=-25),
                                Color(hue_offset=25),
                                Color(hue_offset=155),
                                Color(hue_offset=205)],
                        tooltip="Double Complement - a color combinations made up of\n"
                        "two sets of complementary colors."),

                Harmony(name="monochromatic",
                        colors=[Color(saturation_scale=0.8),
                                Color(saturation_scale=0.3, value_scale=0.65),
                                Color(saturation_scale=0.5),
                                Color(saturation_scale=0.8, value_scale=0.8)
                                ],
                        tooltip="Monochromatic Harmony - is made from a single color family.\n"
                        "In most designs, a monochromatic scheme includes a combination of\n"
                        "tints, tones, and shades from the same color family together with black,\n"
                        "white and / or gray. to add depth and contrast."
                        ),

                Harmony(name="triad",
                        colors=[Color(hue_offset=120),
                                Color(hue_offset=240)],
                        tooltip="Triad - a combination of three hues that are equally spaced\n"
                        "from one another around the color wheel.\n"
                        "Ex. Red, Yellow, Blue or Green, Purple, Orange."
                        ),
                Harmony(name="squares",
                        colors=[Color(hue_offset=90),
                                Color(hue_offset=180),
                                Color(270)],
                        tooltip="Tetrad Colors - combinations of two complementary pairs of\n"
                        "colors with none of the colors being adjacent on the color wheeln\n"
                        "Ex. Yellow, Purple, Green, and Blue. There are two formations of \n"
                        "the tetrad harmony, rectangular and square."
                        )
                ]
