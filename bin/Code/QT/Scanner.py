import os

from PySide2 import QtCore, QtGui, QtWidgets

from Code.QT import QTUtil
from Code import Util


class Scanner_vars:
    def __init__(self, folder_scanners):
        self.fich_vars = os.path.join(folder_scanners, "last.data64")
        self.read()

    def read(self):
        dic = Util.restore_pickle(self.fich_vars)
        if not dic:
            dic = {}

        self.opacity = dic.get("OPACITY", 0.3)
        self.last_width = dic.get("LAST_WIDTH", 0)
        self.last_height = dic.get("LAST_HEIGHT", self.last_width)
        self.tolerance = dic.get("TOLERANCE", 6)
        self.tolerance_learns = dic.get("TOLERANCE_LEARNS", max(self.tolerance - 3, 1))
        self.scanner = dic.get("SCANNER", "")
        self.ask = dic.get("ASK", True)
        self.rem_ghost = dic.get("REM_GHOST", False)

    def write(self):
        dic = {
            "OPACITY": self.opacity,
            "LAST_WIDTH": self.last_width,
            "LAST_HEIGHT": self.last_height,
            "TOLERANCE": self.tolerance,
            "TOLERANCE_LEARNS": self.tolerance_learns,
            "SCANNER": self.scanner,
            "ASK": self.ask,
            "REM_GHOST": self.rem_ghost,
        }
        Util.save_pickle(self.fich_vars, dic)


class Scanner(QtWidgets.QDialog):
    def __init__(self, folder_scanners, fich_png):
        QtWidgets.QDialog.__init__(self)

        self.vars = Scanner_vars(folder_scanners)

        self.fich_png = fich_png

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(self.vars.opacity)
        self.setGeometry(QtWidgets.QDesktopWidget().availableGeometry())

        self.path = None
        self.selecting = False
        self.selected = False
        self.x = self.y = self.width = self.height = 0

    def quit(self, ok):
        self.hide()
        if ok:
            self.vars.write()
            rect = QtCore.QRect(self.x, self.y, self.width, self.height)
            screen = QtWidgets.QApplication.primaryScreen()
            desktop = screen.grabWindow(0, 0, 0, QTUtil.anchoEscritorio(), QTUtil.altoEscritorio())
            selected_pixmap = desktop.copy(rect)
            selected_pixmap = selected_pixmap.scaled(256, 256, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
            selected_pixmap.save(self.fich_png)
        else:
            with open(self.fich_png, "w"):
                pass
        self.close()

    def paintEvent(self, event):
        if self.path:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.red))
            painter.drawPath(self.path)

    def setPath(self, point):
        width = point.x() - self.x
        height = point.y() - self.y
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.AltModifier:
            width = max(width, height)
            if width > 0:
                self.height = self.width = width
                self.setPathW()
        else:
            if width > 0 and height > 0:
                self.width = width
                self.height = height
                self.setPathW()

    def setPathW(self):
        celdaw = self.width // 8
        self.width = celdaw * 8
        celdah = self.height // 8
        self.height = celdah * 8
        rect = QtGui.QPainterPath()
        x = self.x
        y = self.y
        for c in range(8):
            dx = x + c * celdaw
            rect.moveTo(dx, y)
            rect.lineTo(dx + celdaw, y)
            rect.lineTo(dx + celdaw, y + self.height)
            rect.lineTo(dx, y + self.height)
            rect.lineTo(dx, y)
        for f in range(1, 8):
            dy = y + f * celdah
            rect.moveTo(x, dy)
            rect.lineTo(x + self.width, dy)
        rect.closeSubpath()

        self.path = rect
        self.update()

    def mouseMoveEvent(self, eventMouse):
        if self.selecting:
            self.setPath(eventMouse.pos())

    def mousePressEvent(self, eventMouse):
        if eventMouse.button() == QtCore.Qt.LeftButton:
            self.selecting = True
            self.selected = False
            origin = eventMouse.pos()
            self.x = origin.x()
            self.y = origin.y()
            self.width = 0
            self.height = 0
        elif eventMouse.button() == QtCore.Qt.RightButton:
            self.quit(True)
            self.close()
        eventMouse.ignore()

    def mouseReleaseEvent(self, eventMouse):
        self.selecting = False
        self.selected = True
        if self.width < 10:
            if self.vars.last_width > 10:
                self.width = self.vars.last_width
                self.height = self.vars.last_height
                self.setPathW()
        else:
            self.vars.last_width = self.width
            self.vars.last_height = self.height

    def keyPressEvent(self, event):
        k = event.key()
        m = int(event.modifiers())
        is_ctrl = (m & QtCore.Qt.ControlModifier) > 0
        is_alt = (m & QtCore.Qt.AltModifier) > 0
        x = self.x
        y = self.y
        width = self.width
        height = self.height

        if k in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_S):
            self.quit(True)

        elif k == QtCore.Qt.Key_Escape:
            self.quit(False)

        elif k == QtCore.Qt.Key_Plus:
            self.vars.opacity += 0.05
            if self.vars.opacity > 0.5:
                self.vars.opacity = 0.5
            self.setWindowOpacity(self.vars.opacity)

        elif k == QtCore.Qt.Key_Minus:
            self.vars.opacity -= 0.05
            if self.vars.opacity < 0.1:
                self.vars.opacity = 0.1
            self.setWindowOpacity(self.vars.opacity)

        else:
            if k == QtCore.Qt.Key_Right:
                if is_ctrl:
                    width += 8
                    height += 8
                elif is_alt:
                    width += 8
                else:
                    x += 1
            elif k == QtCore.Qt.Key_Left:
                if is_ctrl:
                    width -= 8
                    height -= 8
                elif is_alt:
                    width -= 8
                else:
                    x -= 1
            elif k == QtCore.Qt.Key_Up:
                if is_ctrl:
                    height -= 8
                    width -= 8
                elif is_alt:
                    height -= 8
                else:
                    y -= 1
            elif k == QtCore.Qt.Key_Down:
                if is_ctrl:
                    height += 8
                    width += 8
                elif is_alt:
                    height += 8
                else:
                    y += 1

            if self.selected:
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                self.setPathW()

        event.ignore()
