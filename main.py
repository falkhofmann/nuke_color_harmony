
import sys

from PySide2 import QtWidgets

from nuke_color_harmony import view
from nuke_color_harmony.controller import Controller


def start_from_main():
    """Start up function from outside nuke."""

    app = QtWidgets.QApplication(sys.argv)
    view_ = view.ColorHarmonyUi()
    controller = Controller(view_)
    controller.view.raise_()
    controller.view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    start_from_main()
