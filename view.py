from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QLineF, QPointF, QRect, Qt
from PySide2.QtGui import (QColor, QConicalGradient, QMouseEvent, QPainter,
                           QPaintEvent, QRadialGradient, QResizeEvent)
from PySide2.QtWidgets import QSizePolicy

from harmonies import HARMONY_SETS


class ColorWheel(QtWidgets.QWidget):
    color_changed = QtCore.Signal(object)

    def __init__(self, parent=None, startupcolor: list = [255, 255, 255], margin=10) -> None:
        super().__init__(parent=parent)
        self.radius = 0

        self.setMinimumSize(500, 500)
        self.selected_color = QColor(
            startupcolor[0], startupcolor[1], startupcolor[2], 1)
        self.x = 0.5
        self.y = 0.5
        self.h = self.selected_color.hueF()
        self.s = self.selected_color.saturationF()
        self.v = self.selected_color.valueF()
        self.margin = margin

        qsp = QSizePolicy(QSizePolicy.Preferred,
                          QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

        self._circle_size = 12

        self._harmony = None
        self._calc_colors = []

    def _update_harmony(self, harmony):
        self._harmony = harmony

    def resizeEvent(self, ev: QResizeEvent) -> None:
        size = min(self.width(), self.height()) - self.margin * 2
        self.radius = size / 2
        self.square = QRect(0, 0, size, size)
        self.square.moveCenter(self.rect().center())

    def paintEvent(self, ev: QPaintEvent) -> None:

        center = QPointF(self.width()/2, self.height()/2)
        p = QPainter(self)
        p.setViewport(self.margin, self.margin, self.width() -
                      2*self.margin, self.height()-2*self.margin)
        hsv_grad = QConicalGradient(center, 90)
        for deg in range(360):
            col = QColor.fromHsvF(deg / 360, 1.0, self.v)
            hsv_grad.setColorAt(deg / 360, col)

        val_grad = QRadialGradient(center, self.radius)
        val_grad.setColorAt(0.0, QColor.fromHsvF(0.0, 0.0, self.v, 1.0))
        val_grad.setColorAt(1.0, Qt.transparent)

        p.setPen(Qt.transparent)
        p.setBrush(hsv_grad)
        p.drawEllipse(self.square)
        p.setBrush(val_grad)
        p.drawEllipse(self.square)

        p.setPen(Qt.black)
        p.setBrush(self.selected_color)

        angle = 360 * self.h + 90
        center = self.rect().center()
        line = QLineF.fromPolar(self.radius * self.s, 360 * self.h + 90)
        line.translate(center)
        p.drawLine(line)
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)
        self._calc_colors.clear()
        self._calc_colors.append(self.selected_color)
        if not self._harmony:
            return

        for color in self._harmony.colors:
            color = self.calc_colors(p, angle, center, color)
            self._calc_colors.append(color)

        self.color_changed.emit(self._calc_colors)

    def calc_colors(self, p, angle, center, harmony):

        line = QLineF.fromPolar(
            self.radius * (self.s * harmony.saturation_scale), (angle + harmony.hue_offset)-360)
        line.translate(center)
        p.drawLine(line)

        target = (
            ((self.h * 360 + harmony.hue_offset) - 360) % 360) / 360

        target_color = QColor().fromHsvF(
            target, self.s*harmony.saturation_scale, self.v*harmony.value_scale)
        p.setBrush(target_color)
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)
        return target_color

    def recalc(self) -> None:
        self.selected_color.setHsvF(self.h, self.s, self.v)
        self.repaint()

    def map_color(self, x: int, y: int) -> QColor:
        line = QLineF(QPointF(self.rect().center()), QPointF(x, y))
        s = min(1.0, line.length() / self.radius)
        h = (line.angle() - 90) / 360 % 1.
        return h, s, self.v

    def processMouseEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.MouseButton.RightButton:
            self.h, self.s, self.v = 0, 0, 1
        else:
            self.h, self.s, self.v = self.map_color(ev.x(), ev.y())
        self.x = ev.x() / self.width()
        self.y = ev.y() / self.height()

        self.color_changed.emit(self._calc_colors)

        self.recalc()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def set_color(self, color: QColor) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.recalc()


class HarmonyButton(QtWidgets.QPushButton):

    def __init__(self, harmony_set, parent=None) -> None:
        super().__init__(parent=parent)
        self.harmony_set = harmony_set
        self.setText(self.harmony_set.name)
        self.setCheckable(True)
        self.setMaximumWidth(200)


class HarmonieSelection(QtWidgets.QGroupBox):
    harmony_selection_changed = QtCore.Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setTitle("Hamony Types")
        self._harmony_btns = []

        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

        self._harmony_btns = None
        self._current = None
        self._last = None

    def build_widgets(self):

        for harmony_set in HARMONY_SETS:
            btn = HarmonyButton(harmony_set)
            self._harmony_btns.append(btn)

    def build_layouts(self):
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addStretch()
        for btn in self._harmony_btns:
            button_layout.addWidget(btn)
        button_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        pass

    def set_up_signals(self):
        for btn in self._harmony_btns:
            btn.clicked.connect(self.emit_harmony_change)

    def emit_harmony_change(self, btn):
        button = self.sender()
        if button.isChecked():
            self.harmony_selection_changed.emit(self.sender().harmony_set)
            if self._current:
                self._current.setChecked(False)
            self._current = button


class Variation(QtWidgets.QWidget):
    def __init__(self, color=None, parent=None) -> None:
        super().__init__(parent=parent)
        self.set_up_window_properties()
        self._clear_color = QColor(0.0, 0.0, 0.0, 0.0)
        self._color = color or self._clear_color

    def set_up_window_properties(self):
        self.setFixedSize(150, 400)

    def set_color(self, color):
        self._color = color
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def clear_color(self):
        self._color = self._clear_color
        self.set_color(self._clear_color)

    @property
    def color(self):
        return self._color


class ColorBars(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(ColorBars, self).__init__(parent=parent)
        self.setTitle("Preview")
        self._variations = []

        self.build_widgets()
        self.build_layouts()

    def build_widgets(self):
        self.variation_1 = Variation()
        self.variation_2 = Variation()
        self.variation_3 = Variation()
        self.variation_4 = Variation()
        self.variation_5 = Variation()
        self._variations.append(self.variation_1)
        self._variations.append(self.variation_2)
        self._variations.append(self.variation_3)
        self._variations.append(self.variation_4)
        self._variations.append(self.variation_5)

    def build_layouts(self):
        bars_layout = QtWidgets.QHBoxLayout()
        for var in self._variations:
            bars_layout.addWidget(var)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(bars_layout)
        self.setLayout(main_layout)

    def update(self, colors):
        self.clear_colors()
        for index, color in enumerate(colors):
            self._variations[index].set_color(color)

    def clear_colors(self):

        for var in self._variations:
            var.clear_color()

    @property
    def variations(self):
        return self._variations


class HarmonyStore(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(HarmonyStore, self).__init__(parent=parent)
        self.setTitle("Harmony Store")
        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()

    def build_widgets(self):

        self.list_widget = QtWidgets.QListWidget()

    def build_layouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        self.setMinimumWidth(250)


class StoreItem(QtWidgets.QListWidgetItem):
    def __init__(self, color_set, parent=None):
        super(StoreItem, self).__init__(parent=parent)

        self._color_set = color_set

    @property
    def color_set(self):
        return self._color_set


class ColorPaletteUi(QtWidgets.QWidget):
    def __init__(self):
        super(ColorPaletteUi, self).__init__()

        self._harmony = None
        self._colors = []
        self._variations = []

        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self):
        self.colorwheel = ColorWheel()
        self.harmonies = HarmonieSelection(self)
        self.colorbars = ColorBars(self)
        self.harmony_store = HarmonyStore(self)

    def build_layouts(self):

        colorwheel_layout = QtWidgets.QVBoxLayout()
        colorwheel_layout.addWidget(self.colorwheel)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.colorwheel)
        top_layout.addWidget(self.harmonies)
        top_layout.addWidget(self.harmony_store)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.colorbars)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        width = 1000
        height = 1000
        self.resize(width, height)
        self.setWindowTitle("Nuke color harmony")
        self.setMinimumSize(width, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def set_up_signals(self):
        self.colorwheel.color_changed.connect(self.output_values)
        self.harmonies.harmony_selection_changed.connect(
            self.harmony_selection_change)

    def abort(self):
        """Emit close signal and close view."""
        self.cancel.emit()
        self.close()

    def keyPressEvent(self, event):
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def output_values(self, colors):
        self.colorbars.update(colors)

    @property
    def harmony(self):
        return self._harmony

    def harmony_selection_change(self, harmony):
        self.colorwheel._update_harmony(harmony)
        self.colorbars.clear_colors()
        self._colors.clear()


if __name__ == "__main__":
    import sys

    from PySide2 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)

    window = ColorPaletteUi()
    window.show()
    sys.exit(app.exec_())
