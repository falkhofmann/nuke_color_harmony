from PySide2 import QtWidgets
from PySide2.QtGui import QColor

try:
    import nuke
except ImportError:
    pass

class BaseExport(object):
    delimiter = "|"

    def __init__(self, color_sets: list) -> None:
        self._color_sets = color_sets.copy()

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

    def export_to_nuke(self):

        root_format = nuke.root().format()
        width, height = root_format.width(), root_format.height()
        for color_set in self._color_sets:
            reformats = []
            group_node = nuke.nodes.Group(postage_stamp=True)
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
