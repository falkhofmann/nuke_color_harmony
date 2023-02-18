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

from nuke_color_harmony import IDENTIFIER_NAME
from nuke_color_harmony.harmony_template import (ADD_KNOB, GROUP, MAIN_SCRIPT,
                                                 SINGLE_COLOR)


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

    def import_into_nuke(self, callback, params: str) -> None:
        """
        Export colorsets into Nuke as group nodes, displaying those color sets.

        This could also use the export to .nk logic to reduce code

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

            constants = []
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
                    constants.append(constant)

                contactsheet = nuke.nodes.ContactSheet(width=width, height=height,
                                                       rows=1, columns=len(reformats), gap=20, center=True,
                                                       ypos=constant.ypos() + 300)
                for index, reformat in enumerate(reformats):
                    contactsheet.setInput(index, reformat)
                nuke.nodes.Output(inputs=[contactsheet])

            tab_knob = nuke.Tab_Knob(IDENTIFIER_NAME, IDENTIFIER_NAME)
            txt_knob = nuke.Text_Knob("harmony", f"<b>{harmony.name}</b>")
            group_node.addKnob(tab_knob)
            group_node.addKnob(txt_knob)

            for index, constant in enumerate(constants, start=1):
                link = nuke.Link_Knob(f"color{index}", f"color{index}")
                link.setLink(f"{constant.fullName()}.color")
                group_node.addKnob(link)

        callback(params)

    def export_as_csv(self, path: str, callback, params: str) -> None:
        """
        Export color sets as .csv file on given path.

        Args:
            path (str): Path to save .csv file.
            callback (function): Callback after success.
            params (str): Parameter for callback.
        """
        self.export_to_disk(path=path, content=self.colorsets_to_text(),
                            callback=callback, params=params)

    def export_to_disk(self, path: str, content: str, callback, params: str):
        """
        Export color hamony sets directly to disk.

        Args:
            path (str): Location where to store the file.
            content (str): Content to store inside file. Either Nuke nodes or csv pattern.
            callback (function): Callback function to confirm success.
            params (str): Message parameter for callback.
        """
        with open(path, 'w') as dst:
            dst.writelines(content)

        callback(params)

    def export_as_nukefile(self, callback, params: str) -> None:
        """
        Export color harmonines durectly to dis in native nuke format.

        Args:
            callback (function): Callback function to confirm success.
            params (str): Message parameter for callback.
        """

        path = nuke.getFilename("Export Nodes As Script",
                                "*.nk", "", "script",
                                "save", extension=".nk")
        if not path:
            return

        root_format = nuke.root().format()
        width, height = root_format.width(), root_format.height()
        nuke_version = f"{nuke.env['NukeVersionMajor']}.{nuke.env['NukeVersionMinor']} v{nuke.env['NukeVersionRelease']}"
        group_index = 1

        data = {"nuke_version_string": nuke_version,
                "reformat_height": height,
                "cs_width": width,
                "cs_height": height
                }

        groups = ""
        for color_set, harmony in self._color_sets:

            extend_data = {"color_harmony": harmony.name,
                           "group_index": group_index,
                           "group_xpos": 100 * group_index,
                           "reformat_width": width / len(color_set),
                           "color_amount": len(color_set),
                           }

            data = {**data, **extend_data}

            add_user_knobs = ""
            single_colors = ""

            for constant_index, color in enumerate(reversed(color_set), start=1):
                components = self.to_rgb(color=color)
                color_data = {"red": components[0],
                              "green": components[1],
                              "blue": components[2],
                              "constant_index": constant_index,
                              "xpos": 100 + (100 * constant_index)}
                data = {**data, **color_data}

                add_user_knobs += ADD_KNOB.format(**data) + "\n"
                single_colors += SINGLE_COLOR.format(**data) + "\n"

            data["add_user_knobs_to_script"] = add_user_knobs
            data["add_colors_to_script"] = single_colors
            group_node = GROUP.format(**data)
            groups += group_node + "\n"
            group_index += 1

        data["add_groups_to_script"] = groups
        main_script = MAIN_SCRIPT.format(**data)
        self.export_to_disk(path, main_script,
                            callback=callback,
                            params=params.format(path=path))
