"""Connect user interface with model."""

from .export import Exporter

controller = None


class Controller(object):
    """Connect the user interface with model."""

    def __init__(self, view_):

        self._view = view_
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

    def export_for_nuke(self, color_sets):
        export = Exporter(color_sets=color_sets)
        export.export_to_nuke()

    def export_for_csv(self, color_sets, path):
        export = Exporter(color_sets=color_sets)
        export.export_as_csv(path=path)

    def export_for_clipboard(self, color_sets):
        export = Exporter(color_sets)
        export.copy_to_clipboard()

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view_):
        self._view = view_


def start():
    """Start up function."""
    from .view import ColorHarmonyUi
    view_ = ColorHarmonyUi()
    controller = Controller(view_)

    controller.view.raise_()
    controller.view.show()
