"""Connect user interface with model."""

from nuke_color_harmony import view

# try:
#     from nuke_color_harmony import view
# except ImportError:
#     pass


controller = None


class Controller(object):
    """Connect the user interface with model."""

    def __init__(self, view_):
        self.view = view_
        self.set_up_signals()

    def set_up_signals(self):
        """Connect interface signal with model functions."""
        self.view.open_sesion.connect(self.open_sesion)
        self.view.save_sesion.connect(self.save_sesion)
        self.view.export_for_nuke.connect(self.export_for_nuke)
        self.view.export_for_csv.connect(self.export_for_csv)
        self.view.export_for_clipboard.connect(self.export_for_clipboard)

    def open_sesion(self, session_data):
        print("open session")

    def save_sesion(self, sesion_data):
        print("save_sesion")

    def export_for_nuke(self, sesion_data):
        print("export_for_nuke")

    def export_for_csv(self, sesion_data):
        print("export_for_csv")

    def export_for_clipboard(self, sesion_data):
        print("export_for_clipboard")


def start():
    """Start up function."""
    view_ = view.ColorPaletteUi()

    controller = Controller(view_)
    controller.view.raise_()
    controller.view.show()


def start_from_main():
    """Start up function from outside nuke."""

    import sys

    from PySide2 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    view_ = view.ColorPaletteUi()
    controller = Controller(view_)
    controller.view.raise_()
    controller.view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    start_from_main()
