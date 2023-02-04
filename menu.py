"""Integrate commands in Nuke menu."""

import nuke
import nukescripts

from nuke_color_harmony import controller as harmony_controller
from nuke_color_harmony import view as harmony_view


def show_harmony_ui():
    harmony_controller.start()


nuke.menu("Nuke").addCommand("Color Harmony",
                             show_harmony_ui, 
                             shortcut="shift+r")
pane = nuke.getPaneFor("Properties.1")
nukescripts.panels.registerWidgetAsPanel("harmony_view.ColorHarmonyUi", "Color Harmony",
                                         "de.kombinat-13b.ColorHarmonyUi", True).addToPane(pane)
