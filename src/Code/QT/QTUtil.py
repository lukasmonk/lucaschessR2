import gc
import sys
import time

from PySide2 import QtCore
from PySide2 import QtGui, QtWidgets

import Code


class GarbageCollector(QtCore.QObject):
    INTERVAL = 10000

    def __init__(self):
        super().__init__()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check)

        self.threshold = gc.get_threshold()
        gc.disable()
        self.timer.start(self.INTERVAL)

    def check(self):
        l0, l1, l2 = gc.get_count()
        if l0 > self.threshold[0]:
            self.collect_garbage(0)
        if l1 > self.threshold[1]:
            self.collect_garbage(1)
        if l2 > self.threshold[2]:
            self.collect_garbage(2)

    def collect_garbage(self, generation):
        try:
            QtCore.QTimer.singleShot(0, lambda: self.collect(generation))
        except Exception as e:
            sys.stderr.write(f"Error during garbage collection: {e}\n")

    @QtCore.Slot(int)
    def collect(self, generation):
        gc.collect(generation)


def beep():
    """
    Pitido del sistema
    """
    QtWidgets.QApplication.beep()


def backgroundGUI():
    """
    Background por defecto del GUI
    """
    return QtWidgets.QApplication.palette().brush(QtGui.QPalette.Active, QtGui.QPalette.Window).color().name()


def backgroundGUIlight(factor):
    """
    Background por defecto del GUI
    """
    return (
        QtWidgets.QApplication.palette()
        .brush(QtGui.QPalette.Active, QtGui.QPalette.Window)
        .color()
        .light(factor)
        .name()
    )


def refresh_gui():
    """
    Procesa eventos pendientes para que se muestren correctamente las windows
    """
    QtCore.QCoreApplication.processEvents()
    QtWidgets.QApplication.processEvents()


time_ini = time.time()


def refresh_gui_time():
    """
    Procesa eventos pendientes para que se muestren correctamente las windows
    """
    global time_ini
    if time.time() - time_ini > 0.5:
        QtCore.QCoreApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        time_ini = time.time()


def xrefresh_gui():
    """
    Procesa eventos pendientes para que se muestren correctamente las windows
    """
    QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)


def send_key_widget(widget, key, ckey):
    event_press = QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, key, QtCore.Qt.NoModifier, ckey)
    event_release = QtGui.QKeyEvent(QtGui.QKeyEvent.KeyRelease, key, QtCore.Qt.NoModifier, ckey)
    QtCore.QCoreApplication.postEvent(widget, event_press)
    QtCore.QCoreApplication.postEvent(widget, event_release)
    refresh_gui()


dAlineacion = {"i": QtCore.Qt.AlignLeft, "d": QtCore.Qt.AlignRight, "c": QtCore.Qt.AlignCenter}


def qtAlineacion(cAlin):
    """
    Convierte alineacion en letras (i-c-d) en constantes qt
    """
    return dAlineacion.get(cAlin, QtCore.Qt.AlignLeft)


def qtColor(nColor):
    """
    Genera un color a partir de un dato numerico
    """
    return QtGui.QColor(nColor)


def qtColorRGB(r, g, b):
    """
    Genera un color a partir del rgb
    """
    return QtGui.QColor(r, g, b)


def qtBrush(nColor):
    """
    Genera un brush a partir de un dato numerico
    """
    return QtGui.QBrush(qtColor(nColor))

def get_screen_geometry(widget:QtWidgets.QWidget):
    screen = get_screen(widget)
    return screen.geometry()

def get_screen(widget:QtWidgets.QWidget):
    try:
        screen = widget.screen()
    except AttributeError: #Qt512
        punto = widget.mapToGlobal(QtCore.QPoint(2, 2))
        screen = QtGui.QGuiApplication.screenAt(punto)
    if screen is None:
        screen = QtWidgets.QDesktopWidget()
    return screen

def center_on_desktop(window):
    """
    Centra la ventana en el escritorio
    """
    screen_geometry = get_screen_geometry(window)
    size = window.geometry()
    window.move((screen_geometry.width() - size.width()) / 2, (screen_geometry.height() - size.height()) / 2)


def center_on_widget(window):
    parent_geometry = window.parent().geometry()
    child_geometry = window.geometry()

    x = (parent_geometry.width() - child_geometry.width()) / 2
    y = (parent_geometry.height() - child_geometry.height()) / 2

    window.move(window.parent().mapToGlobal(QtCore.QPoint(x, y)))


def dic_monitores():
    return {pos: screen.geometry() for pos, screen in enumerate(QtGui.QGuiApplication.screens())}


class EscondeWindow:
    def __init__(self, window):
        self.window = window
        self.is_maximized = self.window.isMaximized()

    def __enter__(self):
        if Code.is_windows:
            self.pos = self.window.pos()
            d = dic_monitores()
            ancho = sum(geometry.width() for geometry in d.values())
            self.window.move(ancho + self.window.width() + 10, 0)
        else:
            self.window.showMinimized()
        return self

    def __exit__(self, type, value, traceback):
        if Code.is_windows:
            self.window.move(self.pos)
        if self.is_maximized:
            self.window.showMaximized()
        else:
            self.window.showNormal()
        refresh_gui()


def colorIcon(xcolor, ancho, alto):
    color = QtGui.QColor(xcolor)
    pm = QtGui.QPixmap(ancho, alto)
    pm.fill(color)
    return QtGui.QIcon(pm)


def desktop_size():
    if Code.main_window:
        screen_geometry = get_screen_geometry(Code.main_window)
    else:
        desktop = QtWidgets.QDesktopWidget()
        screen_geometry = desktop.geometry()
    return screen_geometry.width(), screen_geometry.height()


def desktop_size_available():
    if Code.main_window:
        screen = get_screen(Code.main_window)
        screen_geometry = screen.availableGeometry()
    else:
        desktop = QtWidgets.QDesktopWidget()
        screen_geometry = desktop.availableGeometry()
    return screen_geometry.width(), screen_geometry.height()


def desktop_width():
    return desktop_size()[0]


def desktop_height():
    return desktop_size()[1]


def exit_application(xid):
    QtWidgets.QApplication.exit(xid)


def set_clipboard(dato, tipo="t"):
    cb = QtWidgets.QApplication.clipboard()
    if tipo == "t":
        cb.setText(dato)
    elif tipo == "i":
        cb.setImage(dato)
    elif tipo == "p":
        cb.setPixmap(dato)


def get_txt_clipboard():
    cb = QtWidgets.QApplication.clipboard()
    return cb.text()


class MaintainGeometry:
    def __init__(self, window):
        self.window = window
        self.geometry = window.geometry()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.window.setGeometry(self.geometry)


def get_clipboard():
    clipboard = QtWidgets.QApplication.clipboard()
    mimedata = clipboard.mimeData()

    if mimedata.hasImage():
        return "p", mimedata.imageData()
    elif mimedata.hasHtml():
        return "h", mimedata.html()
    elif mimedata.hasHtml():
        return "h", mimedata.html()
    elif mimedata.hasText():
        return "t", mimedata.text()
    return None, None


def shrink(widget):
    widget.adjustSize()
    r = widget.geometry()
    r.setWidth(0)
    r.setHeight(0)
    widget.setGeometry(r)


def keyboard_modifiers():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    is_shift = modifiers == QtCore.Qt.ShiftModifier
    is_control = modifiers == QtCore.Qt.ControlModifier
    is_alt = modifiers == QtCore.Qt.AltModifier
    return is_shift, is_control, is_alt


class EstadoWindow:
    def __init__(self, x):
        self.noEstado = x == QtCore.Qt.WindowNoState
        self.minimizado = x == QtCore.Qt.WindowMinimized
        self.maximizado = x == QtCore.Qt.WindowMaximized
        self.fullscreen = x == QtCore.Qt.WindowFullScreen
        self.active = x == QtCore.Qt.WindowActive


def get_width_text(widget, text):
    metrics = QtGui.QFontMetrics(widget.font())
    return metrics.horizontalAdvance(text)


def get_height_text(widget, text):
    metrics = QtGui.QFontMetrics(widget.font())
    return metrics.boundingRect(text).height()
