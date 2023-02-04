"""
This module holds the controller whcih connects interface and model.

Classes:
    Controller

Functions:
    start
"""

from .export import Exporter

controller = None


class Controller(object):
    """Connect the user interface with model."""

    def __init__(self, view_) -> None:

        self._view = view_
        self.set_up_signals()

    def set_up_signals(self) -> None:
        """
        Connect interface signal with model functions.
        """
        self.view.export_for_nuke.connect(self.export_for_nuke)
        self.view.export_for_csv.connect(self.export_for_csv)
        self.view.export_for_clipboard.connect(self.export_for_clipboard)

    def export_for_nuke(self, color_sets: list) -> None:
        """
        Export given color sets into Nuke.

        Args:
            color_sets (list): Color sets to export.
        """
        export = Exporter(color_sets=color_sets)
        export.export_to_nuke()

    def export_for_csv(self, color_sets: list, path: str) -> None:
        """
        Export given color sets as .csv file on given path.

        Args:
            color_sets (list): Color sets to export.
            path (str): Location to save .csv file.
        """
        export = Exporter(color_sets=color_sets)
        export.export_as_csv(path=path)

    def export_for_clipboard(self, color_sets: list) -> None:
        """
        Copy given color sets in clipboard.

        Args:
            color_sets (list): Color sets to copy.
        """
        export = Exporter(color_sets)
        export.copy_to_clipboard()

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
