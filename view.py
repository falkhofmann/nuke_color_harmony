from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QLineF, QPointF, QRect, Qt
from PySide2.QtGui import (QColor, QConicalGradient, QMouseEvent, QPainter,
                           QPaintEvent, QRadialGradient, QResizeEvent)
from PySide2.QtWidgets import QSizePolicy, QWidget


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
            col = QColor.fromHsvF(deg / 360, 1, self.v)
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
        line = QLineF.fromPolar(self.radius * self.s, 360 * self.h + 90)
        line.translate(self.rect().center())
        p.drawEllipse(line.p2(), 10, 10)

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

    def setHue(self, hue: float) -> None:
        if 0 <= hue <= 1:
            self.h = float(hue)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setSaturation(self, saturation: float) -> None:
        if 0 <= saturation <= 1:
            self.s = float(saturation)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setValue(self, value: float) -> None:
        if 0 <= value <= 1:
            self.v = float(value)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setColor(self, color: QColor) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.recalc()

    def getHue(self) -> float:
        return self.h

    def getSaturation(self) -> float:
        return self.s

    def getValue(self) -> float:
        return self.v

    def getColor(self) -> QColor:
        return self.selected_color


class ColorPaletteUi(QtWidgets.QWidget):
    def __init__(self):
        super(ColorPaletteUi, self).__init__()

        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self):
        self.colorwheel = ColorWheel()

    def build_layouts(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.colorwheel)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        width = 500
        height = 500
        self.resize(width, height)
        self.setWindowTitle("hans")
        self.setMinimumSize(width, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def set_up_signals(self):
        self.colorwheel.color_changed.connect(self.output_values)

    def abort(self):
        """Emit close signal and close view."""
        self.cancel.emit()
        self.close()

    def keyPressEvent(self, event):
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def output_values(self, color):
        print(color)


if __name__ == "__main__":
    import sys

    from PySide2 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)

    window = ColorPaletteUi()
    window.show()
    sys.exit(app.exec_())
