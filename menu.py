"""Integrate commands in Nuke menu."""

import nuke
import nukescripts

from nuke_color_harmony import controller as harmony_controller
from nuke_color_harmony import view as harmony_view


def add_to_menus():

    menu = nuke.menu("Nuke").addMenu("fhofmann")
    menu.addCommand("nuke_color_harmony", harmony_controller.start)
    pane = nuke.getPaneFor("Properties.1")
    nukescripts.panels.registerWidgetAsPanel("harmony_view.ColorHarmonyUi", "Color Harmony",
                                             "de.kombinat-13b.ColorHarmonyUi", True).addToPane(pane)


add_to_menus()
