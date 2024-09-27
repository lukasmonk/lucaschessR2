from PySide2 import QtCore, QtWidgets

import Code
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WAnalisisVariations(QtWidgets.QDialog):
    def __init__(self, o_base, ventana, segundos_pensando, is_white, c_puntos):
        super(WAnalisisVariations, self).__init__(ventana)

        self.oBase = o_base
        
        self.timer = None

        # Creamos los controles
        self.setWindowTitle(_("Variations"))

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(Iconos.Tutor())

        f = Controles.FontType(puntos=12, peso=75)
        flb = Controles.FontType(puntos=10)

        lb_puntuacion_anterior = Controles.LB(self, c_puntos).align_center().set_font(flb)
        self.lbPuntuacionNueva = Controles.LB(self).align_center().set_font(flb)

        config_board = Code.configuration.config_board("ANALISISVARIANTES", 32)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(is_white)

        self.boardT = Board.Board(self, config_board)
        self.boardT.crea()
        self.boardT.set_side_bottom(is_white)

        bt_terminar = Controles.PB(self, _("Close"), self.close).ponPlano(False)
        bt_reset = Controles.PB(self, _("Another change"), o_base.reset).ponIcono(Iconos.MoverLibre()).ponPlano(False)
        li_mas_acciones = (("FEN:%s" % _("Copy to clipboard"), "MoverFEN", Iconos.Clipboard()),)
        lytb_tutor, self.tb = QTVarios.ly_mini_buttons(self, "", siLibre=True, liMasAcciones=li_mas_acciones)

        self.seconds, lb_segundos = QTUtil2.spinbox_lb(self, segundos_pensando, 1, 999, max_width=40,
                                                       etiqueta=_("Second(s)"))

        # Creamos los layouts

        ly_variacion = Colocacion.V().control(lb_puntuacion_anterior).control(self.board)
        gb_variacion = Controles.GB(self, _("Proposed change"), ly_variacion).set_font(f).align_center()

        ly_tutor = Colocacion.V().control(self.lbPuntuacionNueva).control(self.boardT)
        gb_tutor = Controles.GB(self, _("Analyzer's prediction"), ly_tutor).set_font(f).align_center()

        ly_bt = Colocacion.H().control(bt_terminar).control(bt_reset).relleno().control(lb_segundos).control(self.seconds)

        layout = Colocacion.G().control(gb_variacion, 0, 0).control(gb_tutor, 0, 1)
        layout.otro(ly_bt, 1, 0).otro(lytb_tutor, 1, 1)

        self.setLayout(layout)

        self.move(ventana.x() + 20, ventana.y() + 20)

    def get_seconds(self):
        return int(self.seconds.value())

    def set_score(self, pts):
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
