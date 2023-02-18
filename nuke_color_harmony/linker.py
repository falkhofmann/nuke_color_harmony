try:
    import nuke
except ImportError:
    pass

from nuke_color_harmony import IDENTIFIER_NAME


class Linker(object):

    def __init__(self) -> None:
        self._activated = False
        self._nodes = []
        self._values = []

    @property
    def state(self) -> None:
        return self._activated

    @state.setter
    def state(self, flag: bool) -> None:
        self._activated = flag

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, colors) -> None:
        self._values = colors
        self._nodes = self._nodes or nuke.selectedNodes()
        print(self._nodes)
        for node in self._nodes:
            if not IDENTIFIER_NAME in node.knobs():
                return
            for index, color in enumerate(colors, start=1):
                knob = node.knob(f"color{index}")
                if knob:
                    knob.setValue(color.getRgbF())
