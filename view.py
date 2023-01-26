from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QLineF, QPointF, QRect, Qt
from PySide2.QtGui import (QColor, QConicalGradient, QMouseEvent, QPainter,
                           QPaintEvent, QRadialGradient, QResizeEvent)
from PySide2.QtWidgets import QSizePolicy, QWidget

from harmonies import HARMONY_SETS


class ColorWheel(QWidget):
    color_changed = QtCore.Signal(QColor)

    def __init__(self, parent=None, startupcolor: list = [255, 255, 255], margin=10) -> None:
        super().__init__(parent=parent)
        self.radius = 0
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

        self._harmony_set = None

    def _update_harmony(self, harmony_set):
        self._harmony_set = harmony_set

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
        if self._harmony_set:
            self.draw_harmony(p, angle, center)

    def draw_harmony(self, p, angle, center):

        for harmony in self._harmony_set.harmonies:
            self.calc_harmonies(p, angle, center, harmony)

    def calc_harmonies(self, p, angle, center, harmony):

        line = QLineF.fromPolar(
            self.radius * (self.s * harmony.saturation_scale), (angle + harmony.hue_offset)-360)
        line.translate(center)
        p.drawLine(line)

        target_harmony = (
            ((self.h * 360 + harmony.hue_offset) - 360) % 360) / 360
        p.setBrush(QColor.fromHsvF(target_harmony, self.s, self.v))
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)

    def recalc(self) -> None:
        self.selected_color.setHsvF(self.h, self.s, self.v)
        self.color_changed.emit(self.selected_color)
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
        self.recalc()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev)

    def set_hue(self, hue: float) -> None:
        if 0 <= hue <= 1:
            self.h = float(hue)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def set_saturation(self, saturation: float) -> None:
        if 0 <= saturation <= 1:
            self.s = float(saturation)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def set_value(self, value: float) -> None:
        if 0 <= value <= 1:
            self.v = float(value)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def set_color(self, color: QColor) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.recalc()

    def get_hue(self) -> float:
        return self.h

    def get_saturation(self) -> float:
        return self.s

    def get_value(self) -> float:
        return self.v

    def get_color(self) -> QColor:
        return self.selected_color


class HarmonyButton(QtWidgets.QPushButton):

    def __init__(self, harmony_set, parent=None) -> None:
        super().__init__(parent=parent)
        self.harmony_set = harmony_set
        self.setText(self.harmony_set.name)
        self.setCheckable(True)
        self.setMaximumWidth(200)


class HarmonieSelection(QtWidgets.QWidget):
    harmony_changed = QtCore.Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
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
            self.harmony_changed.emit(self.sender().harmony_set)
            if self._current:
                self._current.setChecked(False)
            self._current = button


class Variation(QtWidgets.QWidget):
    def __init__(self, color, parent=None) -> None:
        super().__init__(parent=parent)
        self.set_up_window_properties()

        self._color = color

    def set_up_window_properties(self):
        self.setFixedSize(300, 100)

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(self._color)
        qp.drawRect(0, 0, self.width(), self.height())
        qp.end()

    def set_color(self, color):
        self._color = color
        self.repaint()


class ColorPaletteUi(QtWidgets.QWidget):
    def __init__(self):
        super(ColorPaletteUi, self).__init__()

        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

        self._harmony = None

    def build_widgets(self):
        self.colorwheel = ColorWheel()
        self.harmonies = HarmonieSelection()
        self.variation_1 = Variation(QtGui.QColor(0, 0, 0, 0))
        self.variation_2 = Variation(QtGui.QColor(0, 50, 0, 0))
        self.variation_3 = Variation(QtGui.QColor(0, 50, 50, 0))
        self.variation_4 = Variation(QtGui.QColor(50, 0, 0, 0))
        self.variation_5 = Variation(QtGui.QColor(50, 0, 50, 0))

    def build_layouts(self):

        colorwheel_layout = QtWidgets.QVBoxLayout()
        colorwheel_layout.addWidget(self.colorwheel)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addLayout(colorwheel_layout)
        top_layout.addWidget(self.harmonies)
        top_layout.addWidget(self.colorwheel)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.variation_1)
        bottom_layout.addWidget(self.variation_2)
        bottom_layout.addWidget(self.variation_3)
        bottom_layout.addWidget(self.variation_4)
        bottom_layout.addWidget(self.variation_5)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        width = 1500
        height = 500
        self.resize(width, height)
        self.setWindowTitle("color palette")
        self.setMinimumSize(width, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def set_up_signals(self):
        self.colorwheel.color_changed.connect(self.output_values)
        self.harmonies.harmony_changed.connect(self.harmony_change)

    def abort(self):
        """Emit close signal and close view."""
        self.cancel.emit()
        self.close()

    def keyPressEvent(self, event):
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def output_values(self, color):
        self.variation_1.set_color(color)
        self.variation_3.set_color(color)

    @property
    def harmony(self):
        return self._harmony

    def harmony_change(self, harmony):
        self.colorwheel._update_harmony(harmony)


if __name__ == "__main__":
    import sys

    from PySide2 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)

    window = ColorPaletteUi()
    window.show()
    sys.exit(app.exec_())
