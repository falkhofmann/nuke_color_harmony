"""
This module holds all user interface related classes.

Classes:
    ColorWheel
    ValueSlider
    HarmonyButton
    HarmonieSelection
    Variation
    ColorBars
    StoreItem
    ColorHarmonyUi

Functions:
    set_style_sheet
    pen_color

"""

import os
from functools import partial
from random import choice, uniform

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QLineF, QPointF, QRect, Qt
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QLinearGradient,
                           QMouseEvent, QPainter, QPaintEvent, QRadialGradient,
                           QResizeEvent)

from nuke_color_harmony.controller import Controller as HarmonyController
from nuke_color_harmony.harmonies import HARMONY_SETS, Color, Harmony


def set_style_sheet(widget: QtWidgets.QWidget) -> None:
    """
    Apply stylesheet to given widget.

    Args:
        widget (QtWidgets.QWidget): Widget to apply stylesheet on.
    """

    styles_file = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                "stylesheet.qss"))

    with open(styles_file, "r") as file_:
        style = file_.read()
        widget.setStyleSheet(style)


def pen_color(value: float) -> QColor:
    """
    Return a color based on the given threshold.

    Args:
        value (float): threshold to switch.

    Returns:
        QColor: Dark or light grey as QColor.
    """
    return QtGui.QColor(10, 10, 10) if value > 0.3 else QtGui.QColor(150, 150, 150)


class ColorWheel(QtWidgets.QWidget):
    """
    Colorwheel widget to display color in Hue and saturation.
    """

    color_changed = QtCore.Signal(object)

    def __init__(self, parent=None, startcolor: list = [0.0, 0.0, 1.0, 1.0], margin=10) -> None:
        super().__init__(parent=parent)
        self.radius = 0

        self.selected_color = QColor.fromHsvF(*startcolor)
        self.x = 0.5
        self.y = 0.5

        self.set_color(self.selected_color)
        self.margin = margin

        qsp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

        self._circle_size = 12

        self._harmony = None
        self._calc_colors = []

    def _update_harmony(self, harmony: Harmony, trigger: bool) -> None:
        """
        Update the color harmony (math) on hte colorwheel.

        Args:
            harmony (Harmony): Color harmony
            trigger (bool): Boolean to decide if repaint is requeired.
        """
        self._harmony = harmony
        self.set_color(self.selected_color, repaint=trigger)

    def randomize_value(self, random_color: QColor) -> None:
        """
        Apply a given color to the colorwheel

        Args:
            random_color (QColor): Created random color.
        """
        self.selected_color = random_color
        self.set_color(random_color)
        angle = 360 * self.h + 90
        self.calculate_colors(angle=angle)

    def resizeEvent(self, ev: QResizeEvent) -> None:
        """
        Override resize event

        Args:
            ev (QResizeEvent): ResizeEvent.
        """
        size = min(self.width(), self.height()) - self.margin * 2
        self.radius = size / 2
        self.square = QRect(0, 0, size, size)
        self.square.moveCenter(self.rect().center())

    def paintEvent(self, ev: QPaintEvent) -> None:
        """
        Override paintEvent.

        Args:
            ev (QPaintEvent): QPaintEvent.
        """
        p_color = pen_color(self.v)
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

        p.setPen(p_color)
        p.setBrush(self.selected_color)

        angle = 360 * self.h + 90
        center = self.rect().center()
        line = QLineF.fromPolar(self.radius * self.s, 360 * self.h + 90)
        line.translate(center)
        p.drawLine(line)
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)

        self.calculate_colors(angle=angle, p=p)
        self.color_changed.emit(self._calc_colors)

    def get_target_color(self, color: QColor) -> QColor:
        """
        Calculate anohter color based on the given Harmony.

        Args:
            color (QColor): Colr as part from a harmony set.

        Returns:
            QColor: Calculated new color based on the given harmony color rules.
        """
        target = (
            ((self.h * 360 + color.hue_offset) - 360) % 360) / 360

        target_color = QColor().fromHsvF(
            target, self.s*color.saturation_scale, self.v*color.value_scale)
        return target_color

    def calculate_colors(self, angle: float, p=None) -> None:
        """
        Calculate all to be included on the current Harmony set and potentially draaw them.

        Args:
            angle (float): Angle in wheel of current selected color.
            p (QPainter, optional): QPainter to draw. Defaults to None.
        """
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

    def draw_color_on_wheel(self, p: QPainter, angle: float, center: float, color: Color, target_color: QColor):
        """
        Draw elipse and line of given target color onto the colorwheel.

        Args:
            p (QPainter): Painter object.
            angle (float): Angle of selected color.
            center (float): Center of wheel.
            color (Color): Color with the offset and scale attributes.
            target_color (QColor): Taregt color.
        """
        line = QLineF.fromPolar(
            self.radius * (self.s * color.saturation_scale), (angle + color.hue_offset)-360)
        line.translate(center)
        p.drawLine(line)

        p.setBrush(target_color)
        p.drawEllipse(line.p2(), self._circle_size, self._circle_size)

    def recalc(self) -> None:
        """
        Recalculate the selected color components and repaint widget.
        """
        self.selected_color.setHsvF(self.h, self.s, self.v)
        self.repaint()

    def map_color(self, x: int, y: int) -> tuple:
        """
        Map colors from coordinates into HSV.

        Args:
            x (int): X position.
            y (int): Y position.

        Returns:
            tuple: HSV values.
        """
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
        """
        Set internal color values from given color and potentially repaint.

        Args:
            color (QColor): color to update colorwheel to.
            repaint (bool, optional): If True a repaint will be triggered. Defaults to True.
        """
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.selected_color = color
        if repaint:
            self.repaint()

    def set_value(self, value: float) -> None:
        """
        Set the value component of the HSV color.

        Args:
            value (float): Value component.
        """
        self.v = value
        self.recalc()

    def restore(self, harmony: Harmony, color=QColor) -> None:
        """
        Restore colorwheel from given StoreItem.

        Args:
            item (StoreItem): Storeitem which holds harmmony and color set.
        """
        self._harmony = harmony
        self.set_color(color=color)

    @property
    def current_color(self) -> list:
        return self._calc_colors


class ValueSlider(QtWidgets.QWidget):
    value_changed = QtCore.Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self._value = 1.0
        self._scale_factor = 100

        self.build_widgets()
        self.build_layouts()
        self.set_up_signals()

    def build_widgets(self) -> None:
        """
        Build widgets to add to this very widget.
        """
        self.slider = QtWidgets.QSlider()
        self.slider.setOrientation(QtCore.Qt.Vertical)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)

    def build_layouts(self):
        """
        Build widget layout and add other widgets accordingly.
        """
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.slider)
        self.setLayout(main_layout)

    def set_up_signals(self) -> None:
        """
        Connect signals from withhin this widget.
        """
        self.slider.valueChanged.connect(self.emit_value_changed)

    def emit_value_changed(self, value: float) -> None:
        """
        Emit the signal for value change on the slider.

        Args:
            value (float): New value of slider.
        """
        self.value_changed.emit(value/self._scale_factor)

    @property
    def value(self) -> None:
        """
        Property to access protected attribute.

        Returns:
            float: Protected attribute for value.
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """
        Property setter for the protected attribute value. Temporary blocking signals.

        Args:
            value (float): New value to set property.
        """
        self.slider.blockSignals(True)
        self._value = value
        self.slider.setValue(value * self._scale_factor)
        self.slider.blockSignals(False)


class HarmonyButton(QtWidgets.QPushButton):
    """
    Custom button with minor adjusted attrinbutes.
    """

    def __init__(self, harmony_set, parent=None) -> None:
        super().__init__(parent=parent)
        self.harmony_set = harmony_set
        self.setText(self.harmony_set.name)
        self.setCheckable(True)
        self.setMaximumWidth(250)
        self.setToolTip(self.harmony_set.tooltip)
        set_style_sheet(self)


class HarmonieSelection(QtWidgets.QGroupBox):
    """GroupBox to hold Harmony selection as buttons."""

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

    def build_widgets(self) -> None:
        """
        Build widgets to add to this very widget.
        """
        for harmony_set in HARMONY_SETS:
            btn = HarmonyButton(harmony_set)
            self._harmony_btns.append(btn)

        self.btn_randomize = QtWidgets.QPushButton("randomize")
        self.btn_add_to_store = QtWidgets.QPushButton("add to store >>")

        self.btn_randomize.setMaximumWidth(250)
        self.btn_add_to_store.setMaximumWidth(250)

        self.btn_randomize.setObjectName("Button")
        self.btn_add_to_store.setObjectName("Button")
        set_style_sheet(self.btn_randomize)
        set_style_sheet(self.btn_add_to_store)

    def build_layouts(self) -> None:
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

    def set_up_signals(self) -> None:
        """
        Connect signals from withhin this widget.
        """
        for btn in self._harmony_btns:
            btn.clicked.connect(self.emit_harmony_change)

        self.btn_randomize.clicked.connect(self.emit_randomize_values)
        self.btn_add_to_store.clicked.connect(self.emit_add_to_store)

    def restore(self, harmony: Harmony) -> None:
        """
        Restore checked state based on given harmony.   

        Args:
            harmony (Harmony): Harmony to set checked.
        """
        self._current.setChecked(False)
        for btn in self._harmony_btns:
            if btn.harmony_set == harmony:
                btn.setChecked(True)
                self._current = btn
                return

    def emit_harmony_change(self, _=None, btn: HarmonyButton = None, trigger: bool = True) -> None:
        """
        Emit harmony changed signal and set current harmony on widget.

        Args:
            _ (_type_, optional): Passed along argument. Can be ignored. Defaults to None.
            btn (HarmonyButton, optional): Button which has been set checked.. Defaults to None.
            trigger (bool, optional): Option to trigger signals further down. Defaults to True.
        """
        button = btn or self.sender()
        if button.isChecked():
            self.selection_changed.emit(button.harmony_set, trigger)
            if self._current:
                self._current.setChecked(False)
            self._current = button
            self._current.setChecked(True)

    def emit_randomize_values(self) -> None:
        """
        Emit signal that randomize has been clicked.
        """
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

    def emit_add_to_store(self) -> None:
        """
        Emit signal to store the current selected colors into the store.
        """
        self.add_current_to_store.emit()


class Variation(QtWidgets.QWidget):
    """
    Widget to show the a specific color with overlay of its RGB colors.
    """

    def __init__(self, color=None, parent=None) -> None:
        super().__init__(parent=parent)
        self._clear_color = QColor(0.0, 0.0, 0.0, 0.0)
        self._color = color or self._clear_color
        self._color_label = ""
        self._active = False

    def set_color(self, color: QColor) -> None:
        """
        Apply given color to the background.

        Args:
            color (QColor): Color to apply onto widget.
        """
        self._color = color
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.build_overlay()
        self._active = True

    def sizeHint(self) -> QtCore.QSize:
        """
        Override size hint.

        Returns:
            QtCore.QSize: Size used as siz hint.
        """
        return QtCore.QSize(200, 400)

    def clear_color(self) -> None:
        """
        Clear out color on the variation widget.
        """
        self._color = self._clear_color
        self.set_color(self._clear_color)
        self._active = False

    @property
    def color(self) -> QColor:
        """
        Access protected attribute as property.

        Returns:
            QColor: Protected attribte _color.
        """
        return self._color

    def build_overlay(self) -> None:
        """
        Assemble overlay text for variation.
        """
        rgb = self._color.getRgbF()[:3]
        rgb_colors = f"red:     {rgb[0]:.2f}\ngreen: {rgb[1]:.2f}\nblue:   {rgb[2]:.2f}\n"
        self._color_label = rgb_colors

    def paintEvent(self, event) -> None:
        """
        Override PaintEvent.

        Args:
            event (QPaintEvent): PaintEvent.
        """
        if self._active:
            painter = QtGui.QPainter()
            painter.begin(self)
            self.draw_text(event, painter)
            painter.end()

    def draw_text(self, event, painter: QPainter) -> None:
        """
        Draw text onto the Variation widget.

        Args:
            event (QPaintEvent): PaintEvent.
            painter (QPainter): QPainter.
        """
        p_color = pen_color(self._color.valueF())
        painter.setPen(p_color)
        painter.setFont(QtGui.QFont("Decorative", 10))
        painter.drawText(event.rect(),
                         QtCore.Qt.AlignBottom,
                         self._color_label)


class ColorBars(QtWidgets.QGroupBox):
    """
    Widget to hold the different color variations.
    """

    def __init__(self, parent=None):
        super(ColorBars, self).__init__(parent=parent)
        self.setTitle("Preview")
        self._variations = []

        self.build_widgets()
        self.build_layouts()

    def build_widgets(self) -> None:
        """
        Build widgets to add to this very widget.
        """
        for _ in range(5):
            new_var = Variation(parent=self)
            self._variations.append(new_var)

    def build_layouts(self) -> None:
        """
        Build widget layout and add other widgets accordingly.
        """
        bars_layout = QtWidgets.QHBoxLayout()
        for var in self._variations:
            bars_layout.addWidget(var)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(bars_layout)
        self.setLayout(main_layout)

    def update(self, colors: list) -> None:
        """
        Set given coolor onto the variations.

        Args:
            colors (list): Colors to be displayed on the colorbars widget.
        """
        self.clear_colors()
        for index, color in enumerate(colors):
            self._variations[index].set_color(color)

    def clear_colors(self) -> None:
        """
        Clear out every color on the variations.
        """
        for var in self._variations:
            var.clear_color()

    @property
    def variations(self) -> list:
        """
        Access protected atribte _variations.

        Returns:
            list: protected atribte _variations.
        """
        return self._variations


class HarmonyStore(QtWidgets.QGroupBox):
    """
    Store object to collect multiple colorsets.
    """

    restore_store_item = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(HarmonyStore, self).__init__(parent=parent)
        self.setTitle("Harmony Store")
        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self) -> None:
        """
        Build widgets to add to this very widget.
        """
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)

    def build_layouts(self) -> None:
        """
        Build widget layout and add other widgets accordingly.
        """
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

    def set_up_window_properties(self) -> None:
        """
        Apply window properties to this widget.
        """
        self.setFixedWidth(250)

    def set_up_signals(self) -> None:
        """
        Connect signals from widgets to adapt UI.
        """
        self.list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_widget.connect(self.list_widget,
                                 QtCore.SIGNAL(
                                     "customContextMenuRequested(QPoint)"),
                                 self.context_menu)

        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)

    @property
    def items(self) -> list:
        """
        Get all StoreItems in the Store.

        Returns:
            list: All StoreItems as list generator,
        """
        return [self.list_widget.item(index) for index in range(self.list_widget.count())]

    def add_colors_to_store(self, harmony: Harmony, color_set: list) -> None:
        """
        Add given color and harmony to store as StoreItem.

        Args:
            harmony (Harmony): Harmony Set.
            color_set (list): Colors as list.
        """
        store_item = StoreItem(
            harmony=harmony, color_set=color_set, parent=self)
        self.list_widget.addItem(store_item)

    def context_menu(self, QPos: QPointF) -> None:
        """
        Build context menu on Store.

        Args:
            QPos (QPointF): Point to place menu.
        """
        self.listMenu = QtWidgets.QMenu()
        menu_item = self.listMenu.addAction("Remove Item")
        self.connect(menu_item, QtCore.SIGNAL(
            "triggered()"), self.remove_selected_items)
        parentPosition = self.list_widget.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def remove_selected_items(self) -> None:
        """
        Remove the selected items from the store.
        """
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def item_double_clicked(self, item) -> None:
        """
        Emit signal that an icon has been double clicked.
        """
        self.restore_store_item.emit(item)

    def keyPressEvent(self, event) -> None:
        """
        Catch user key interactions. Close on escape.

        Args:
            event (QEvent): Event to check against.
        """
        if event.key() == QtCore.Qt.Key_Delete:
            self.remove_selected_items()


class StoreItem(QtWidgets.QListWidgetItem):
    """
    Widget to hold data as item in the Store.
    """

    def __init__(self, harmony, color_set, parent=None):
        super(StoreItem, self).__init__(parent=parent)
        self._harmony = harmony
        self._color_set = color_set.copy()
        self.setText(self._harmony.name)
        self.draw_background()

    def draw_background(self):
        gradient = QLinearGradient(0, 0, 250, 0)
        sub_stop = 1.0/(len(self.color_set)-1)
        gradient.setColorAt(0, self.color_set[0])
        gradient.setColorAt(1, self.color_set[-1])

        for index, color in enumerate(self.color_set, start=0):
            gradient.setColorAt(sub_stop * index, color)
            gradient.setColorAt((sub_stop * index) + sub_stop - 0.0001, color)
        gradient.setColorAt(1, self.color_set[-1])
        brush = QBrush(gradient)
        self.setBackground(brush)

    @property
    def color_set(self) -> list:
        """
        Access protected attribute _color_set.

        Returns:
            list: Protected attribute _color_set.
        """
        return self._color_set

    @property
    def harmony(self) -> Harmony:
        """
        Access protected attribute _harmony.

        Returns:
            Harmony: Protected attribute _harmony.
        """
        return self._harmony


class ColorHarmonyUi(QtWidgets.QDialog):
    """
    Main widget to hold other widget.
    """

    export_for_clipboard = QtCore.Signal(object, object, str)
    export_for_csv = QtCore.Signal(object, object)
    import_to_nuke = QtCore.Signal(object, object, str)
    toggle_link = QtCore.Signal(bool)
    current_colors = QtCore.Signal(object)

    def __init__(self):
        super(ColorHarmonyUi, self).__init__()

        self._controller = HarmonyController(self)

        self._harmony = None
        self._color_set = []
        self._variations = []
        self._live_link_activated = False

        self.build_widgets()
        self.build_menu()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self) -> None:
        """
        Build widgets to add to main widget.
        """
        self.colorwheel = ColorWheel()
        self.value_slider = ValueSlider()
        self.harmonies = HarmonieSelection(self)
        self.colorbars = ColorBars(self)
        self.harmony_store = HarmonyStore(self)
        self.status_bar = QtWidgets.QStatusBar()

    def build_layouts(self) -> None:
        """
        Build widget layout and add other widgets accordingly.
        """
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
        main_layout.addWidget(self.status_bar)
        self.setLayout(main_layout)

    def build_menu(self) -> None:
        """
        Build Menubar.
        """
        self.tool_bar = QtWidgets.QToolBar()

        self.menu_bar = QtWidgets.QMenuBar()

        import_into_nuke = QtWidgets.QAction("Import Store into Nuke", self)
        import_into_nuke.setToolTip(
            "Import current items from store into nuke.")
        self.menu_bar.addAction(import_into_nuke)
        self.export_menu = self.menu_bar.addMenu("Export ..")
        export_nuke = QtWidgets.QAction("Export as .nk", self)
        export_clipboard = QtWidgets.QAction("Copy to Clipboard", self)
        export_csv = QtWidgets.QAction("Export CSV", self)

        self.export_menu.addAction(export_nuke)
        self.export_menu.addAction(export_clipboard)
        self.export_menu.addAction(export_csv)

        activate_link = QtWidgets.QAction("LiveLink", self)
        activate_link.setCheckable(True)
        self.menu_bar.addAction(activate_link)

        import_into_nuke.triggered.connect(self.import_into_nuke)
        export_nuke.triggered.connect(self.export_nuke)
        export_clipboard.triggered.connect(self.export_clipboard)
        export_csv.triggered.connect(self.export_csv)
        activate_link.triggered.connect(self.toggle_live_link)
        activate_link.setToolTip(
            "Active Live link between Panel and selected harmony nodes.")

    def set_up_window_properties(self) -> None:
        """
        Set window properties on main widget.
        """
        width = 1000
        height = 1000
        self.resize(width, height)
        self.setWindowTitle("Nuke Color Harmony")
        self.setMinimumSize(width, height)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def set_up_signals(self) -> None:
        """
        Connect signals from widgets to adapt UI.
        """
        self.colorwheel.color_changed.connect(self.update_current_color_set)
        self.value_slider.value_changed.connect(self.slider_value_changed)
        self.harmonies.selection_changed.connect(self.harmony_selection_change)
        self.harmonies.randomize_values.connect(self.randomize_values)
        self.harmonies.add_current_to_store.connect(self.add_current_to_store)
        self.harmony_store.restore_store_item.connect(self.restore_store_item)
        self.colorwheel.color_changed.connect(self.emit_current_colors)

    def abort(self) -> None:
        """
        Emit close signal and close view.
        """
        self.cancel.emit()
        self.close()

    def keyPressEvent(self, event) -> None:
        """
        Catch user key interactions. Close on escape.

        Args:
            event (QEvent): Event to check against.
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def restore_store_item(self, item: StoreItem) -> None:
        """
        Restore colorwheel, slider and button selection based on given item.

        Args:
            item (StoreItem): StoreItem to drive restore.
        """
        color_set = item.color_set
        value = color_set[0].valueF()
        self.colorwheel.restore(harmony=item.harmony, color=item.color_set[0])
        self.value_slider.value = value
        self.harmonies.restore(item.harmony)

    def update_current_color_set(self, color_set) -> None:
        """
        Emit signal to update current color selection.

        Args:
            color_set (list): List of current calculated colors.
        """
        self._color_set = color_set
        self.colorbars.update(self._color_set)

    def import_into_nuke(self) -> None:
        """
        Emit signal for nuke import.
        """
        self.import_to_nuke.emit(
            self.get_items(), self.callback, "Imported into Nuke")

    def export_nuke(self) -> None:
        pass

    def export_csv(self) -> None:
        """
        Emit signal for csv export.
        """
        file_dialog = QtWidgets.QFileDialog()
        file_path, __ = file_dialog.getSaveFileName(filter="csv(*.csv)")
        if file_path:
            self.export_for_csv.emit(self.get_items(),
                                     file_path,
                                     self.callback, f"exported as {file_path}")

    def export_clipboard(self) -> None:
        """
        Emit signal to copy the store to the clipboard.
        """
        self.export_for_clipboard.emit(self.get_items(),
                                       self.callback, "copied to clipboard")

    def get_items(self) -> list:
        """
        Get all color_sets from the store.

        Returns:
            list: Color sets from the HarmonyStore.
        """
        return [item for item in self.harmony_store.items]

    def toggle_live_link(self, flag: bool) -> None:
        self.toggle_link.emit(flag)
        self._live_link_activated = flag

    def emit_current_colors(self) -> None:
        if self._live_link_activated:
            self.current_colors.emit(self.colorwheel.current_color)

    def callback(self, status):
        self.status_bar.showMessage(status)

    @property
    def harmony(self):
        """
        Access protected attribute _harmony.

        Returns:
            Harmony: Current selected color harmony scheme.
        """
        return self._harmony

    def add_current_to_store(self) -> None:
        """
        Add current color sets to the store,
        """
        if self._color_set and self._harmony:
            self.harmony_store.add_colors_to_store(
                harmony=self._harmony,
                color_set=self._color_set)

    def slider_value_changed(self, value: float) -> None:
        """
        Apply given value on the colorwheel.

        Args:
            value (float): Value to implement into the colorwheel representation.
        """
        self.colorwheel.set_value(value=value)

    def harmony_selection_change(self, harmony: Harmony, trigger: bool) -> None:
        """
        Clear variations based on given harmony.

        Args:
            harmony (Harmony): Harmony to apply to the colorwheel.
            trigger (bool): Defines if a repaint of the colorwheel is required.
        """
        self._harmony = harmony
        self.colorbars.clear_colors()
        self._color_set.clear()
        self.colorwheel._update_harmony(self._harmony, trigger)

    def randomize_values(self) -> None:
        """
        Generate random HSV values and apply to slider and colorwheel.
        """
        value = uniform(0.4, 1)
        random_color = QColor.fromHsvF(
            uniform(0.2, 1), uniform(0.2, 1), value, 1.0)
        self.value_slider.value = value
        self.colorwheel.randomize_value(random_color=random_color)
