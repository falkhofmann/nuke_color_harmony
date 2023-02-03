from PySide2 import QtWidgets
from PySide2.QtGui import QColor


class BaseExport(object):
    delimiter = "|"

    def __init__(self, color_sets: list) -> None:
        self._color_sets = color_sets

    def to_rgb(self, color):
        return color.getRgbF()[:3]

    def copy_to_clipboard(self):

        text = ""
        for color_set in self._color_sets:
            colors_amount = len(color_set)
            for index, color in enumerate(color_set, start=1):
                text += ", ".join(str(val) for val in self.to_rgb(color))
                if index < colors_amount:
                    text += self.delimiter

            text += "\n"

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        clipboard = app.clipboard()
        clipboard.setText(text)


if __name__ == "__main__":
    color_sets = [
        [QColor.fromHsvF(0.2, 0.3, 0.800000, 1.000000),
         QColor.fromHsvF(0.3, 0.4, 0.800000, 1.000000),
         QColor.fromHsvF(0.4, 0.5, 0.800000, 1.000000),
         QColor.fromHsvF(0.6, 0.3, 0.800000, 1.000000),
         QColor.fromHsvF(0.7, 0.4, 0.800000, 1.000000)],
        [QColor.fromHsvF(0.8, 0.5, 0.800000, 1.000000),
         QColor.fromHsvF(0.9, 0.7, 0.800000, 1.000000),
         QColor.fromHsvF(1.0, 0.8, 0.800000, 1.000000)]
    ]
    b = BaseExport(color_sets=color_sets)
    b.copy_to_clipboard()
