"""
This module holds a simple start up function for stand alone usage.

Functions:
    start_from_main

"""

import sys

from PySide2 import QtWidgets

from nuke_color_harmony.controller import Controller
from nuke_color_harmony.view import ColorHarmonyUi


def start_from_main():
    """
    Start up function from outside nuke.
    """
    app = QtWidgets.QApplication(sys.argv)
    view_ = ColorHarmonyUi()
    controller = Controller(view_)
    controller.view.raise_()
    controller.view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    start_from_main()
