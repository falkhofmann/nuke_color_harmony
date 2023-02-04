import os
from random import choice, uniform

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QLineF, QPointF, QRect, Qt
from PySide2.QtGui import (QColor, QConicalGradient, QMouseEvent, QPainter,
                           QPaintEvent, QRadialGradient, QResizeEvent)

from nuke_color_harmony.controller import Controller as HarmonyController
from nuke_color_harmony.harmonies import HARMONY_SETS


def set_style_sheet(widget):

    styles_file = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                "stylesheet.qss"))

    with open(styles_file, "r") as file_:
        style = file_.read()
        widget.setStyleSheet(style)


class ColorWheel(QtWidgets.QWidget):
    color_changed = QtCore.Signal(object)

    def __init__(self, parent=None, startcolor: list = [0.0, 0.0, 1.0, 1.0], margin=10) -> None:
        super().__init__(parent=parent)
        self.radius = 0

        self.setMinimumSize(500, 500)
        self.selected_color = QColor.fromHsvF(*startcolor)
        self.x = 0.5
        self.y = 0.5

        self.set_color(self.selected_color)
        self.margin = margin

        qsp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                    QtWidgets.QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

        self._circle_size = 12

        self._harmony = None
        self._calc_colors = []

    def _update_harmony(self, harmony, trigger):
        self._harmony = harmony
        self.set_color(self.selected_color, repaint=trigger)

    def randomize_value(self, random_color):
        # self.blockSignals(True)
        self.selected_color = random_color
        self.set_color(random_color)
        # self.blockSignals(False)
        angle = 360 * self.h + 90
        self.calculate_colors(angle=angle)

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

        self.calculate_colors(angle=angle, p=p)
        self.color_changed.emit(self._calc_colors)

    def get_target_color(self, harmony):
        target = (
            ((self.h * 360 + harmony.hue_offset) - 360) % 360) / 360

        target_color = QColor().fromHsvF(
            target, self.s*harmony.saturation_scale, self.v*harmony.value_scale)
        return target_color

    def calculate_colors(self, angle, p=None):
        self._calc_colors.clear()
        self._calc_colors.append(self.selected_color)
        if not self._harmony:
            return

        center = self.rect().center()

        for color in self._harmony.colors:
            target_color = self.get_target_color(color)
            self._calc_colors.append(target_color)
            if p is not None:
                self.draw_color_on_wheel(p, angle, center, color, target_color)

    def draw_color_on_wheel(self, p, angle, center, harmony, target_color):

        line = QLineF.fromPolar(
            self.radius * (self.s * harmony.saturation_scale), (angle + harmony.hue_offset)-360)
        line.translate(center)
        p.drawLine(line)

        p.setBrush(target_color)
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)

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

    def set_color(self, color: QColor, repaint=True) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.selected_color = color
        if repaint:
            self.repaint()

    def set_value(self, value):
        self.v = value
        self.recalc()


class ValueSlider(QtWidgets.QWidget):
    value_changed = QtCore.Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self._value = 1.0
        self._scale_factor = 100

        self.build_widgets()
        self.build_layouts()
        self.set_up_signals()

    def build_widgets(self):
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Vertical)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)

    def build_layouts(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.slider)
        self.setLayout(main_layout)

    def set_up_signals(self):
        self.slider.valueChanged.connect(self.emit_value_changed)

    def emit_value_changed(self, value):
        self.value_changed.emit(value/self._scale_factor)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.slider.blockSignals(True)
        self._value = value
        self.slider.setValue(value*self._scale_factor)
        self.slider.blockSignals(False)


class HarmonyButton(QtWidgets.QPushButton):

    def __init__(self, harmony_set, parent=None) -> None:
        super().__init__(parent=parent)
        self.harmony_set = harmony_set
        self.setText(self.harmony_set.name)
        self.setCheckable(True)
        self.setMaximumWidth(200)
        self.setToolTip(self.harmony_set.tooltip)
        set_style_sheet(self)


class HarmonieSelection(QtWidgets.QGroupBox):
    selection_changed = QtCore.Signal(object, bool)
    randomize_values = QtCore.Signal()
    add_current_to_store = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setTitle("Hamony Types")
        self._harmony_btns = []

        self.build_widgets()
        self.build_layouts()
        self.set_up_signals()

        self._current = None
        self._last = None

    def build_widgets(self):
        """
        Build widgets to add to this very widget.
        """
        for harmony_set in HARMONY_SETS:
            btn = HarmonyButton(harmony_set)
            self._harmony_btns.append(btn)

        self.btn_randomize = QtWidgets.QPushButton("randomize")
        self.btn_add_to_store = QtWidgets.QPushButton("add to store >>")

    def build_layouts(self):
        """
        Build widget layout and add other widgets accordingly.
        """
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addStretch()
        for btn in self._harmony_btns:
            button_layout.addWidget(btn)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_randomize)
        button_layout.addWidget(self.btn_add_to_store)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def set_up_signals(self):
        for btn in self._harmony_btns:
            btn.clicked.connect(self.emit_harmony_change)

        self.btn_randomize.clicked.connect(self.emit_randomize_values)
        self.btn_add_to_store.clicked.connect(self.emit_add_to_store)

    def emit_harmony_change(self, _=None, btn=None, trigger=True):
        button = btn or self.sender()
        if button.isChecked():
            self.selection_changed.emit(button.harmony_set, trigger)
            if self._current:
                self._current.setChecked(False)
            self._current = button
            self._current.setChecked(True)

    def emit_randomize_values(self):
        btns = self._harmony_btns.copy()
        if self._current:
            self._current.setChecked(False)
            btns.remove(self._current)
            btn = choice(btns)
        else:
            btn = choice(btns)
        self._current = btn
        btn.setChecked(True)

        self.emit_harmony_change(btn=btn, trigger=False)
        self.randomize_values.emit()

    def emit_add_to_store(self):
        self.add_current_to_store.emit()


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
        """
        Build widgets to add to this very widget.
        """
        for _ in range(5):
            new_var = Variation()
            self._variations.append(new_var)

    def build_layouts(self):
        """
        Build widget layout and add other widgets accordingly.
        """
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

    restore_store_item = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(HarmonyStore, self).__init__(parent=parent)
        self.setTitle("Harmony Store")
        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self):
        """
        Build widgets to add to this very widget.
        """
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)

    def build_layouts(self):
        """
        Build widget layout and add other widgets accordingly.
        """
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

    def set_up_window_properties(self):
        self.setMinimumWidth(250)

    def set_up_signals(self):
        self.list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_widget.connect(self.list_widget,
                                 QtCore.SIGNAL(
                                     "customContextMenuRequested(QPoint)"),
                                 self.context_menu)

        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)

    @property
    def items(self):
        return [self.list_widget.item(index) for index in range(self.list_widget.count())]

    def add_colors_to_store(self, harmony, color_set):
        store_item = StoreItem(harmony=harmony, color_set=color_set)
        self.list_widget.addItem(store_item)

    def context_menu(self, QPos):
        self.listMenu = QtWidgets.QMenu()
        menu_item = self.listMenu.addAction("Remove Item")
        self.connect(menu_item, QtCore.SIGNAL(
            "triggered()"), self.remove_selected_items)
        parentPosition = self.list_widget.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def remove_selected_items(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def item_double_clicked(self, item):
        pass

    def keyPressEvent(self, event):
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_selected_items()


class StoreItem(QtWidgets.QListWidgetItem):
    def __init__(self, harmony, color_set, parent=None):
        super(StoreItem, self).__init__(parent=parent)
        self._harmony = harmony
        self.color_set = color_set.copy()
        self.setText(self._harmony.name)


class ColorHarmonyUi(QtWidgets.QDialog):

    export_for_clipboard = QtCore.Signal(object)
    export_for_csv = QtCore.Signal(object, object)
    export_for_nuke = QtCore.Signal(object)
    open_sesion = QtCore.Signal(object)
    save_sesion = QtCore.Signal(object)

    def __init__(self):
        super(ColorHarmonyUi, self).__init__()

        self._controller = HarmonyController(self)

        self._harmony = None
        self._color_set = []
        self._variations = []

        self.build_widgets()
        self.build_menu()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self):
        """
        Build widgets to add to main widget.
        """
        self.colorwheel = ColorWheel()
        self.value_slider = ValueSlider()
        self.harmonies = HarmonieSelection(self)
        self.colorbars = ColorBars(self)
        self.harmony_store = HarmonyStore(self)

    def build_layouts(self):
        """
        Build widget layout and add other widgets accordingly.
        """
        colorwheel_layout = QtWidgets.QVBoxLayout()
        colorwheel_layout.addWidget(self.colorwheel)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.colorwheel)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.value_slider)
        top_layout.addWidget(self.harmonies)
        top_layout.addWidget(self.harmony_store)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.menu_bar)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.colorbars)
        self.setLayout(main_layout)

    def build_menu(self):
        self.menu_bar = QtWidgets.QMenuBar()
        self.session_menu = self.menu_bar.addMenu('Session')
        self.export_menu = self.menu_bar.addMenu('Export')

        open_session = QtWidgets.QAction('Open Session ...', self)
        open_session.triggered.connect(self.open_session)
        self.session_menu.addAction(open_session)

        save_session = QtWidgets.QAction('Save Session ...', self)
        save_session.triggered.connect(self.export_session)
        self.session_menu.addAction(save_session)

        export_nuke = QtWidgets.QAction('Export into nuke', self)
        export_nuke.triggered.connect(self.export_nuke)
        self.export_menu.addAction(export_nuke)

        self.export_menu.addSeparator()

        export_clipboard = QtWidgets.QAction('Copy to Clipboard', self)
        export_clipboard.triggered.connect(self.export_clipboard)
        self.export_menu.addAction(export_clipboard)

        export_csv = QtWidgets.QAction('Export CSV', self)
        export_csv.triggered.connect(self.export_csv)
        self.export_menu.addAction(export_csv)

    def set_up_window_properties(self):
        """
        Set window properties on main widget.
        """
        width = 1100
        height = 1000
        self.resize(width, height)
        self.setWindowTitle("Nuke color harmony")
        self.setMinimumSize(width, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def set_up_signals(self):
        """
        Connect signals from widgets to adapt UI.
        """
        self.colorwheel.color_changed.connect(self.update_current_color_set)
        self.value_slider.value_changed.connect(self.slider_value_changed)
        self.harmonies.selection_changed.connect(self.harmony_selection_change)
        self.harmonies.randomize_values.connect(self.randomize_values)
        self.harmonies.add_current_to_store.connect(self.add_current_to_store)
        self.harmony_store.restore_store_item.connect(self.restore_store_item)

    def abort(self):
        """
        Emit close signal and close view.
        """
        self.cancel.emit()
        self.close()

    def keyPressEvent(self, event):
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def restore_store_item(self, item):
        pass

    def update_current_color_set(self, color_set):
        """
        Emit signl to update current color selection.

        Args:
            colors (list): List of current calculated colors.
        """
        self._color_set = color_set
        self.colorbars.update(self._color_set)

    def _get_export_data(self):
        pass

    def export_nuke(self):
        self.export_for_nuke.emit(self.get_color_sets())

    def export_csv(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, __ = file_dialog.getSaveFileName(filter="csv(*.csv)")
        if file_path:
            self.export_for_csv.emit(self.get_color_sets(), file_path)

    def export_clipboard(self):
        self.export_for_clipboard.emit(self.get_color_sets())

    def export_session(self):
        self.save_sesion.emit(None)

    def open_session(self):
        self.open_sesion.emit(None)

    def get_color_sets(self):
        return [item.color_set for item in self.harmony_store.items]

    @property
    def harmony(self):
        """
        Get current Harmony

        Returns:
            Harmony: Current selected color harmony scheme.
        """
        return self._harmony

    def add_current_to_store(self):
        self.harmony_store.add_colors_to_store(
            harmony=self._harmony, color_set=self._color_set)

    def slider_value_changed(self, value):
        self.colorwheel.set_value(value=value)

    def harmony_selection_change(self, harmony, trigger):
        self._harmony = harmony
        self.colorbars.clear_colors()
        self._color_set.clear()
        self.colorwheel._update_harmony(self._harmony, trigger)

    def randomize_values(self):
        value = uniform(0.4, 1)
        random_color = QColor.fromHsvF(
            uniform(0.2, 1), uniform(0.2, 1), value, 1.0)
        self.colorwheel.randomize_value(random_color=random_color)
