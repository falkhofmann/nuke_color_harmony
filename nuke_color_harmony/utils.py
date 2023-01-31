# Import built-in modules
import os


def set_style_sheet(widget):

    styles_file = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                "stylesheet.qss"))

    with open(styles_file, "r") as file_:
        style = file_.read()
        widget.setStyleSheet(style)
