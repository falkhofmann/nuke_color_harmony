"""Integrate commands in Nuke Nodes and Nuke menu."""

# import third-party modules
import nuke  # pylint: disable = import-error
import nukescripts  # pylint: disable = import-error

# import local modules
from nuke_color_harmony import controller as harmony_controller
from nuke_color_harmony import view as harmony_view


def dev():
    print("dev")
    harmony_controller.start()


# nuke.menu("Nuke").findItem("fhofmann").addCommand(
#     "harmony", harmony_controller.start)
nuke.menu("Nuke").addCommand("Color Harmony", dev, shortcut="shift+r")
pane = nuke.getPaneFor("Properties.1")
# nukescripts.panels.registerWidgetAsPanel("harmony_view.ColorHarmonyUi", "Color Harmony",
#                                          "de.kombinat-13b.ColorHarmonyUi", True).addToPane(pane)
nukescripts.panels.registerWidgetAsPanel("harmony_view.ColorHarmonyUi", "Color Harmony",
                                         "de.kombinat-13b.ColorHarmonyUi", True).addToPane(pane)
