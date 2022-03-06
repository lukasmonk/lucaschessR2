from PySide2 import QtGui

from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2


class WAlbum(LCDialog.LCDialog):
    def __init__(self, wowner, procesador, album):

        self.album = album
        titulo = album.name
        LCDialog.LCDialog.__init__(self, wowner, titulo, album.icono(), "albumes")

        self.configuration = procesador.configuration

        ncromos = len(album)
        dicT = {6: 3, 8: 4, 10: 5, 12: 6, 14: 7, 16: 8, 18: 6, 20: 5, 24: 6, 28: 7, 32: 8, 40: 8}
        divisor = dicT.get(ncromos, 6)

        layout = Colocacion.G()

        pte = False

        icoCaracol = Iconos.Caracol()

        for pos in range(ncromos):
            cromo = album.get_cromo(pos)
            if not cromo.hecho:
                pte = True

            pb = Controles.PB(self, "", rutina=self.pulsado, plano=False)
            pb.setFixedSize(110, 110)
            pb.key = cromo

            if cromo.hecho:
                icono = cromo.icono()
                pixmap = icono.pixmap(64, 64)
                icono.addPixmap(pixmap, QtGui.QIcon.Disabled)
                pb.setEnabled(False)
            else:
                icono = icoCaracol

            pb.ponIcono(icono, 64)

            lb = Controles.LB(self, cromo.name)
            lb.ponTipoLetra(puntos=10, peso=75)
            row = pos // divisor
            col = pos % divisor
            layout.controlc(pb, row * 2, col)
            layout.controlc(lb, row * 2 + 1, col)

        mensaje = _("Select a slot to play against and get its image if you win") if pte else ""
        lb = Controles.LB(self, mensaje)

        pbExit = Controles.PB(self, _("Close"), self.quit, plano=False).ponIcono(Iconos.MainMenu())
        lyP = Colocacion.H().relleno().control(lb).relleno().control(pbExit)
        if not pte:
            pbRebuild = Controles.PB(self, _("Rebuild this album"), self.rebuild, plano=False).ponIcono(Iconos.Delete())
            lyP.control(pbRebuild)

        lyT = Colocacion.V().otro(layout).otro(lyP)

        self.setLayout(lyT)

        self.restore_video(siTam=False)

        self.resultado = None, None

    def terminar(self):
        self.save_video()

    def closeEvent(self, event):
        self.terminar()

    def quit(self):
        self.terminar()
        self.reject()

    def rebuild(self):
        if QTUtil2.pregunta(self, _("Do you want to remove this album and create a new one?")):
            self.album.reset()
            self.terminar()
            self.resultado = None, True
            self.reject()

    def pulsado(self):
        cromo = self.sender().key
        self.resultado = cromo, False
        self.accept()


def eligeCromo(wowner, procesador, album):
    w = WAlbum(wowner, procesador, album)
    w.exec_()
    return w.resultado
