import time

from PySide2 import QtCore, QtWidgets

import Code
from Code.Base import Position
from Code.Board import Board2
from Code.Coordinates import CoordinatesBasic
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, QTUtil2
from Code.QT import LCDialog


class WRunCoordinatesBasic(LCDialog.LCDialog):
    def __init__(self, owner, db_coordinates, is_white, config):

        LCDialog.LCDialog.__init__(self, owner, _("Coordinates"), Iconos.Blocks(), "runcoordinatesbasic")

        self.configuration = Code.configuration
        self.is_white = is_white
        self.db_coordinates = db_coordinates
        self.coordinates = None
        self.current_score = 0
        self.working = False
        self.time_ini = None

        conf_board = self.configuration.config_board("RUNCOORDINATESBASIC", self.configuration.size_base())

        self.board = Board2.BoardEstaticoMensaje(self, conf_board, None, 0.6)
        self.board.crea()
        self.board.bloqueaRotacion(True)
        self.board.set_side_bottom(self.is_white)
        if config.with_pieces:
            self.cp_initial = Position.Position()
            self.cp_initial.set_pos_initial()
            self.board.set_position(self.cp_initial)
        if not config.with_coordinates:
            self.board.show_coordinates(False)
        self.board.set_side_indicator(self.is_white)

        font = Controles.FontType(puntos=26, peso=500)

        lb_score_k = Controles.LB(self, _("Score")).set_font(font)
        self.lb_score = Controles.LB(self).set_font(font)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)
        self.show_tb(self.terminar, self.begin)

        ly_info = Colocacion.G()
        ly_info.controlc(lb_score_k, 0, 0).controlc(self.lb_score, 1, 0)

        ly_right = Colocacion.V().control(self.tb).relleno().otro(ly_info).relleno()

        w = QtWidgets.QWidget(self)
        w.setLayout(ly_right)
        w.setMinimumWidth(240)

        ly_center = Colocacion.H().control(self.board).control(w).margen(3)

        self.setLayout(ly_center)

        self.restore_video()
        self.adjustSize()

    def new_try(self):
        self.coordinates = CoordinatesBasic.CoordinatesBasic(self.is_white)
        self.coordinates.new_try()
        self.current_score = 0
        self.lb_score.set_text("0")
        self.working = True
        self.time_ini = time.time()
        QtCore.QTimer.singleShot(1000, self.comprueba_time)

    def end_work(self):
        self.working = False
        self.coordinates.new_done(self.current_score)
        self.db_coordinates.save(self.coordinates)
        QTUtil2.message(self, "%s\n\n%s: %d\n" % (_("Ended"), _("Result"), self.coordinates.score))
        self.board.pon_textos("", "", 1)
        self.show_tb(self.terminar, self.seguir)

    def comprueba_time(self):
        if self.working:
            dif_time = time.time() - self.time_ini
            if dif_time >= 30.0:
                self.end_work()
            else:
                tm = 1000 if dif_time > 1.0 else dif_time * 1000
                QtCore.QTimer.singleShot(tm, self.comprueba_time)

    def begin(self):
        self.seguir()

    def seguir(self):
        self.new_try()
        self.show_tb(self.terminar)
        self.go_next()

    def go_next(self):
        if self.working:
            self.square_object, self.square_next = self.coordinates.next()
            self.board.pon_textos(self.square_object, self.square_next, 0.8)
            QTUtil.refresh_gui()

    def pulsada_celda(self, celda):
        if self.working:
            if celda == self.square_object:
                self.current_score += 1
                self.lb_score.set_text("%d" % self.current_score)
                self.go_next()
            else:
                QTUtil2.message_error(self, "%s: %s ≠ %s" % (_("Error"), celda, self.square_object))
                self.end_work()

    def closeEvent(self, event):
        self.working = False
        self.save_video()
        event.accept()

    def terminar(self):
        self.working = False
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        QTUtil.refresh_gui()
