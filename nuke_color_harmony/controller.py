"""
This module holds the controller whcih connects interface and model.

Classes:
    Controller

Functions:
    start
"""

from .export import Exporter
from .linker import Linker

controller = None


class Controller(object):
    """Connect the user interface with model."""

    def __init__(self, view_) -> None:

        self._view = view_
        self._linker = None
        self.set_up_signals()

    def set_up_signals(self) -> None:
        """
        Connect interface signal with model functions.
        """
        self.view.import_to_nuke.connect(self.import_to_nuke)
        self.view.export_as_nukefile.connect(self.export_as_nukefile)
        self.view.export_for_csv.connect(self.export_for_csv)
        self.view.export_for_clipboard.connect(self.export_for_clipboard)
        self.view.toggle_link.connect(self.toggle_live_link)
        self.view.current_colors.connect(self.set_live_color)

    def import_to_nuke(self, items: list, callback, params: str) -> None:
        """
        Export given color sets into Nuke.

        Args:
            items (list): Color sets to export.
        """
        exporter = Exporter(items=items)
        exporter.import_into_nuke(callback, params)

    def export_as_nukefile(self, items: list, callback, params: str) -> None:
        """
        Export given color sets into Nuke.

        Args:
            items (list): Color sets to export.
        """
        exporter = Exporter(items=items)
        exporter.export_as_nukefile(callback, params)

    def export_for_csv(self, items: list, path: str, callback, param:str) -> None:
        """
        Export given color sets as .csv file on given path.

        Args:
            items (list): Color sets to export.
            path (str): Location to save .csv file.
        """
        exporter = Exporter(items=items)
        exporter.export_as_csv(path=path)

    def export_for_clipboard(self, items: list, callback, param:str) -> None:
        """
        Copy given color sets in clipboard.

        Args:
            items (list): Color sets to copy.
        """
        exporter = Exporter(items=items)
        exporter.copy_to_clipboard(callback, param)

    def toggle_live_link(self, flag: bool) -> None:
        if flag:
            self._linker = Linker()

    def set_live_color(self, colors) -> None:
        if colors:
            self._linker.values = colors

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view_):
        self._view = view_


def start():
    """
    Start up function.
    """
    from .view import ColorHarmonyUi
    view_ = ColorHarmonyUi()
    controller = Controller(view_)

    controller.view.raise_()
    controller.view.show()
