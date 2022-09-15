from PySide2 import QtCore, QtWidgets

import Code
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WAnalisisVariations(QtWidgets.QDialog):
    def __init__(self, oBase, ventana, segundosPensando, is_white, cPuntos):
        super(WAnalisisVariations, self).__init__(ventana)

        self.oBase = oBase

        # Creamos los controles
        self.setWindowTitle(_("Variations"))

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(Iconos.Tutor())

        f = Controles.TipoLetra(puntos=12, peso=75)
        flb = Controles.TipoLetra(puntos=10)

        lbPuntuacionAnterior = Controles.LB(self, cPuntos).align_center().ponFuente(flb)
        self.lbPuntuacionNueva = Controles.LB(self).align_center().ponFuente(flb)

        config_board = Code.configuration.config_board("ANALISISVARIANTES", 32)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(is_white)

        self.boardT = Board.Board(self, config_board)
        self.boardT.crea()
        self.boardT.set_side_bottom(is_white)

        btTerminar = Controles.PB(self, _("Close"), self.close).ponPlano(False)
        btReset = Controles.PB(self, _("Another change"), oBase.reset).ponIcono(Iconos.MoverLibre()).ponPlano(False)
        liMasAcciones = (("FEN:%s" % _("Copy to clipboard"), "MoverFEN", Iconos.Clipboard()),)
        lytbTutor, self.tb = QTVarios.lyBotonesMovimiento(self, "", siLibre=True, liMasAcciones=liMasAcciones)

        self.seconds, lbSegundos = QTUtil2.spinBoxLB(self, segundosPensando, 1, 999, maxTam=40, etiqueta=_("Second(s)"))

        # Creamos los layouts

        lyVariacion = Colocacion.V().control(lbPuntuacionAnterior).control(self.board)
        gbVariacion = Controles.GB(self, _("Proposed change"), lyVariacion).ponFuente(f).align_center()

        lyTutor = Colocacion.V().control(self.lbPuntuacionNueva).control(self.boardT)
        gbTutor = Controles.GB(self, _("Tutor's prediction"), lyTutor).ponFuente(f).align_center()

        lyBT = Colocacion.H().control(btTerminar).control(btReset).relleno().control(lbSegundos).control(self.seconds)

        layout = Colocacion.G().control(gbVariacion, 0, 0).control(gbTutor, 0, 1)
        layout.otro(lyBT, 1, 0).otro(lytbTutor, 1, 1)

        self.setLayout(layout)

        self.move(ventana.x() + 20, ventana.y() + 20)

    def get_seconds(self):
        return int(self.seconds.value())

    def ponPuntuacion(self, pts):
        self.lbPuntuacionNueva.set_text(pts)

    def process_toolbar(self):
        self.oBase.process_toolbar(self.sender().key)

    def start_clock(self, funcion):
        if not hasattr(self, "timer"):
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(funcion)
        self.timer.start(1000)

    def stop_clock(self):
        if hasattr(self, "timer"):
            self.timer.stop()
            delattr(self, "timer")

    def closeEvent(self, event):  # Cierre con X
        self.stop_clock()

    def keyPressEvent(self, event):
        k = event.key()
        if k == QtCore.Qt.Key.Key_Down:  # abajo
            key = "MoverAtras"
        elif k == QtCore.Qt.Key.Key_Up:  # arriba
            key = "MoverAdelante"
        elif k == QtCore.Qt.Key.Key_Left:  # izda
            key = "MoverAtras"
        elif k == QtCore.Qt.Key.Key_Right:  # dcha
            key = "MoverAdelante"
        elif k == QtCore.Qt.Key.Key_Home:  # start
            key = "MoverInicio"
        elif k == QtCore.Qt.Key.Key_End:  # final
            key = "MoverFinal"
        elif k == QtCore.Qt.Key.Key_Escape:  # esc
            self.stop_clock()
            self.accept()
            return
        else:
            return
        self.oBase.process_toolbar(key)
