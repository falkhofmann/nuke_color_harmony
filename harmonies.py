
from dataclasses import dataclass


@dataclass
class Harmony:

    hue_offset: float = 0.0
    saturation_scale: float = 1.0
    value_scale: float = 1.0


@dataclass
class HarmonySet:

    name: str
    harmonies: list


HARMONY_SETS = [HarmonySet(name="analogous",
                           harmonies=[Harmony(hue_offset=15),
                                      Harmony(hue_offset=-15),
                                      Harmony(hue_offset=-30),
                                      Harmony(hue_offset=30)]),
                HarmonySet(name="complementary",
                           harmonies=[Harmony(hue_offset=180)]),
                HarmonySet(name="diad",
                           harmonies=[Harmony(hue_offset=25)]),
                HarmonySet(name="split-complementary",
                           harmonies=[Harmony(hue_offset=150),
                                      Harmony(hue_offset=210)]),
                HarmonySet(name="double-split-complementary",
                           harmonies=[Harmony(hue_offset=-25),
                                      Harmony(hue_offset=25),
                                      Harmony(hue_offset=155),
                                      Harmony(hue_offset=205)]),
                HarmonySet(name="monochromatic",
                           harmonies=[Harmony(saturation_scale=0.5),
                                      Harmony(saturation_scale=0.8,),
                                      Harmony(value_scale=0.8)]),
                HarmonySet(name="triad",
                           harmonies=[Harmony(hue_offset=120),
                                      Harmony(hue_offset=240)]),
                HarmonySet(name="shades",
                           harmonies=[Harmony(saturation_scale=0.8),
                                      Harmony(value_scale=0.4),
                                      Harmony(value_scale=0.8)]),
                HarmonySet(name="squares",
                           harmonies=[Harmony(hue_offset=90),
                                      Harmony(hue_offset=180),
                                      Harmony(270)])
                ]
