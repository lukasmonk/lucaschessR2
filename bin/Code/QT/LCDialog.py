from PySide2 import QtCore, QtWidgets, QtGui

import Code
from Code.QT import QTUtil


class LCDialog(QtWidgets.QDialog):
    def __init__(self, main_window, titulo, icono, extparam):
        QtWidgets.QDialog.__init__(self, main_window)
        self.key_video = extparam
        self.liGrids = []
        self.liSplitters = []
        self.setWindowTitle(titulo)
        self.setWindowIcon(icono)
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        alt_o: QtWidgets.QShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+O"), self)
        alt_o.activated.connect(self.pressed_shortcut_alt_o)

    def pressed_shortcut_alt_o(self):
        self.move(QtCore.QPoint(0, 0))

    def register_grid(self, grid):
        self.liGrids.append(grid)

    def register_splitter(self, splitter, name):
        self.liSplitters.append((splitter, name))

    def save_video(self, dic_extended=None):
        dic = {} if dic_extended is None else dic_extended

        pos = self.pos()
        dic["_POSICION_"] = "%d,%d" % (pos.x(), pos.y())

        tam = self.size()
        dic["_SIZE_"] = "%d,%d" % (tam.width(), tam.height())

        for grid in self.liGrids:
            grid.save_video(dic)

        for sp, name in self.liSplitters:
            dic["SP_%s" % name] = sp.sizes()

        Code.configuration.save_video(self.key_video, dic)
        return dic

    def restore_dicvideo(self):
        return Code.configuration.restore_video(self.key_video)

    def restore_video(self, with_tam=True, with_width=True, default_width=None, default_height=None, defaul_dic=None,
                      shrink=False):
        dic = self.restore_dicvideo()
        if not dic:
            dic = defaul_dic

        screen_geometry = QTUtil.get_screen_geometry(self)
        width_desktop = screen_geometry.width()
        height_desktop = screen_geometry.height()
        if dic:
            if with_tam:
                if "_SIZE_" not in dic:
                    w, h = self.width(), self.height()
                    for k in dic:
                        if k.startswith("_TAMA"):
                            w, h = dic[k].split(",")
                else:
                    w, h = dic["_SIZE_"].split(",")
                w = int(w)
                h = int(h)
                if w > width_desktop:
                    w = width_desktop
                elif w < 20:
                    w = 20
                if h > (height_desktop - 40):
                    h = height_desktop - 40
                elif h < 20:
                    h = 20
                if with_width:
                    self.resize(w, h)
                else:
                    self.resize(self.width(), h)
            for grid in self.liGrids:
                grid.restore_video(dic)
                grid.releerColumnas()
            try:
                for sp, name in self.liSplitters:
                    k = "SP_%s" % name
                    li_sp = dic.get(k)
                    if li_sp and isinstance(li_sp, list) and len(li_sp) == 2 and isinstance(li_sp[0], int):
                        sp.setSizes(li_sp)
            except TypeError:
                pass
            if shrink:
                QTUtil.shrink(self)
            if "_POSICION_" in dic:
                x, y = dic["_POSICION_"].split(",")
                x = int(x)
                y = int(y)
                if x > width_desktop:
                    max_x = sum(screen_geometry.width() for pos, screen_geometry in QTUtil.dic_monitores().items())
                    if x > max_x - 50:
                        x = (width_desktop - self.width()) // 2
                elif x < -10:
                    x = 1
                if y < 0:
                    y = 1
                self.move(x, y)
            return True
        else:
            if default_width or default_height:
                if default_width is None:
                    default_width = self.width()
                if default_height is None:
                    default_height = self.height()
                if default_width > width_desktop:
                    default_width = width_desktop
                if default_height > (height_desktop - 40):
                    default_height = height_desktop - 40
                self.resize(default_width, default_height)

        return False

    def accept(self):
        self.save_video()
        super().accept()
        # self.close()
        # Evita excepción al salir del programa
        # ver: https://stackoverflow.com/a/36826593/3324704
        self.deleteLater()

    def reject(self):
        self.save_video()
        super().reject()
        self.deleteLater()

    def closeEvent(self, event):  # Cierre con X
        # Evita excepción al salir del programa
        # ver: https://stackoverflow.com/a/36826593/3324704
        self.deleteLater()
