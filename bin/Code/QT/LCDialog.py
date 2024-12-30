from PySide2 import QtCore, QtWidgets

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
            QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
            | QtCore.Qt.WindowCloseButtonHint
        )

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

    def restore_video(self, siTam=True, siAncho=True, anchoDefecto=None, altoDefecto=None, dicDef=None, shrink=False):
        dic = self.restore_dicvideo()
        if not dic:
            dic = dicDef

        if QtWidgets.QDesktopWidget().screenCount() > 1:
            wE = hE = 1024 * 1024
        else:
            wE, hE = QTUtil.desktop_size()
        if dic:
            if siTam:
                if not ("_SIZE_" in dic):
                    w, h = self.width(), self.height()
                    for k in dic:
                        if k.startswith("_TAMA"):
                            w, h = dic[k].split(",")
                else:
                    w, h = dic["_SIZE_"].split(",")
                w = int(w)
                h = int(h)
                if w > wE:
                    w = wE
                elif w < 20:
                    w = 20
                if h > (hE - 40):
                    h = hE - 40
                elif h < 20:
                    h = 20
                if siAncho:
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
                    if li_sp and type(li_sp) == list and len(li_sp) == 2 and type(li_sp[0]) == int:
                        sp.setSizes(li_sp)
            except TypeError:
                pass
            if shrink:
                QTUtil.shrink(self)
            if "_POSICION_" in dic:
                x, y = dic["_POSICION_"].split(",")
                x = int(x)
                y = int(y)
                if not (0 <= x <= (wE - 50)):
                    x = 0
                if not (0 <= y <= (hE - 50)):
                    y = 0
                self.move(x, y)
            return True
        else:
            if anchoDefecto or altoDefecto:
                if anchoDefecto is None:
                    anchoDefecto = self.width()
                if altoDefecto is None:
                    altoDefecto = self.height()
                if anchoDefecto > wE:
                    anchoDefecto = wE
                if altoDefecto > (hE - 40):
                    altoDefecto = hE - 40
                self.resize(anchoDefecto, altoDefecto)

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
