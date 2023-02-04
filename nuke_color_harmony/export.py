"""
This module holds one class for export.

Classes:
    Exporter
"""

from PySide2 import QtWidgets
from PySide2.QtGui import QColor

try:
    import nuke
except ImportError:
    pass


class Exporter(object):
    """
    Object to export to various targets. Nuke, .csv file or clipboard.
    """
    delimiter = "|"

    def __init__(self, items: list) -> None:
        self._color_sets = [(item.color_set, item.harmony) for item in items]

    def to_rgb(self, color: QColor) -> tuple:
        """
        Convert given QColor to rgb tuple without alpha.

        Args:
            color (QColor): QColor to convert.

        Returns:
            tuple: Tuple which holds rgb as floats.
        """
        return color.getRgbF()[:3]

    def colorsets_to_text(self):
        """
        Convert colorsets in a format to store in csv or clipboard.

        Returns:
            str: Formatted text.
            Example: 
                r, g, b | r, g, b | r, g, b
                r, g, b | r, g, b | r, g, b | r, g, b | r, g, b
                r, g, b | r, g, b | r, g, b | r, g, b
        """
        text = ""
        for color_set, harmony in self._color_sets:
            colors_amount = len(color_set)
            for index, color in enumerate(color_set, start=1):
                text += ", ".join(str(val) for val in self.to_rgb(color))
                if index < colors_amount:
                    text += self.delimiter

            text += "\n"

        return text

    def copy_to_clipboard(self, callback, params: str) -> None:
        """
        Copy colorsets as text into clipboard.

        Args:
            callback (function): Callback after success.
            params (str): Parameter for callback.
        """
        text = self.colorsets_to_text()

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        clipboard = app.clipboard()
        clipboard.setText(text)

        callback(params)

    def export_to_nuke(self, callback, params: str) -> None:
        """
        Export colorsets into Nuke as group nodes, displaying those color sets.

        Args:
            callback (function): Callback after success.
            params (str): Parameter for callback.
        """
        root_format = nuke.root().format()
        width, height = root_format.width(), root_format.height()
        for color_set, harmony in self._color_sets:
            reformats = []
            group_node = nuke.nodes.Group(
                postage_stamp=True, label=harmony.name)
            with group_node:
                for color in color_set:
                    constant = nuke.nodes.Constant(channels="rgb")
                    colors = len(color_set)
                    c_width = width/colors
                    for index, component in enumerate(self.to_rgb(color=color)):
                        constant.knob("color").setValue(component, index)

                    constant.knob("color").setValue(1.0, 3)
                    reformat = nuke.nodes.Reformat(type="to box", box_fixed=True, box_width=c_width,  box_height=height,
                                                   resize="distort", xpos=constant.xpos(), ypos=constant.ypos() + 100, inputs=[constant])
                    reformats.append(reformat)

                contactsheet = nuke.nodes.ContactSheet(width=width, height=height,
                                                       rows=1, columns=len(reformats), gap=20, center=True,
                                                       ypos=constant.ypos() + 300)
                for index, reformat in enumerate(reformats):
                    contactsheet.setInput(index, reformat)
                nuke.nodes.Output(inputs=[contactsheet])

        callback(params)

    def export_as_csv(self, path: str, callback, params: str) -> None:
        """
        Export color sets as .csv file on given path.

        Args:
            path (str): Path to save .csv file.
            callback (function): Callback after success.
            params (str): Parameter for callback.
        """
        with open(path, 'w') as dst:
            text = self.colorsets_to_text()
            dst.writelines(text)

        callback(params)
