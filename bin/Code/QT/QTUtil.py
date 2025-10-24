import time

from PySide2 import QtCore
from PySide2 import QtGui, QtWidgets

import Code


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


def qt_alignment(cAlin):
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


def get_screen_geometry(widget: QtWidgets.QWidget):
    screen = get_screen(widget)
    return screen.geometry()


def get_screen(widget: QtWidgets.QWidget):
    try:
        screen = widget.screen()
    except AttributeError:  # Qt512
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
        self.was_minimized = False

    def __enter__(self):
        if Code.is_windows:
            # Guardar geometría exacta antes de mover
            self.normal_geometry = self.window.normalGeometry()
            self.pos = self.window.pos()
            self.size = self.window.size()

            d = dic_monitores()
            ancho = sum(geometry.width() for geometry in d.values())
            # Mover la ventana manteniendo el tamaño exacto
            self.window.setGeometry(ancho + self.window.width() + 10, 0,
                                    self.size.width(), self.size.height())
        else:
            self.was_minimized = True
            self.window.showMinimized()
        return self

    def __exit__(self, type, value, traceback):
        if Code.is_windows:
            # Restaurar posición y tamaño exactos
            if hasattr(self, 'normal_geometry') and self.normal_geometry.isValid():
                self.window.setGeometry(self.normal_geometry)
            else:
                self.window.resize(self.size)
                self.window.move(self.pos)

            # Pequeño retraso para asegurar que Windows procese el movimiento
            QtCore.QTimer.singleShot(50, lambda: self.finalize_restore())
        else:
            self.finalize_restore()

    def finalize_restore(self):
        if self.is_maximized:
            self.window.showMaximized()
        elif self.was_minimized:
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


def keyboard_modifiers():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    is_shift = modifiers == QtCore.Qt.ShiftModifier
    is_control = modifiers == QtCore.Qt.ControlModifier
    is_alt = modifiers == QtCore.Qt.AltModifier
    return is_shift, is_control, is_alt


def shrink(widget: QtWidgets.QWidget):
    pos = widget.pos()
    r = widget.geometry()
    r.setWidth(0)
    r.setHeight(0)
    widget.setGeometry(r)
    widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
    widget.adjustSize()
    if widget.layout():
        widget.layout().activate()
    widget.move(pos)


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

