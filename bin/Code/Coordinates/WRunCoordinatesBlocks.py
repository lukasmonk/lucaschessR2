import time

from PySide2 import QtCore, QtWidgets

import Code
from Code.Base import Position
from Code.Board import Board2
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, QTUtil2
from Code.QT import LCDialog


class WRunCoordinatesBlocks(LCDialog.LCDialog):
    def __init__(self, owner, db_coordinates, coordinates, config):

        LCDialog.LCDialog.__init__(self, owner, _("Coordinates by blocks"), Iconos.Blocks(), "runcoordinatesblocks")

        self.configuration = Code.configuration
        self.coordinates = coordinates
        self.db_coordinates = db_coordinates
        self.current_score = 0
        self.working = False
        self.time_ini = None
        self.square_object = None
        self.square_next = None

        conf_board = self.configuration.config_board("RUNCOORDINATESBLOCKS", self.configuration.size_base())

        self.board = Board2.BoardEstaticoMensaje(self, conf_board, None, 0.6)
        self.board.crea()
        self.board.bloqueaRotacion(True)
        if config.with_pieces:
            self.cp_initial = Position.Position()
            self.cp_initial.set_pos_initial()
            self.board.set_position(self.cp_initial)
        else:
            self.cp_initial = None
        if not config.with_coordinates:
            self.board.show_coordinates(False)

        font = Controles.FontType(puntos=14, peso=500)

        lb_block_k = Controles.LB(self, _("Block") + ":").set_font(font)
        self.lb_block = Controles.LB(self).set_font(font)

        lb_try_k = Controles.LB(self, _("Tries in this block") + ":").set_font(font)
        self.lb_try = Controles.LB(self).set_font(font)

        lb_minimum_score_k = Controles.LB(self, _("Minimum score") + ":").set_font(font)
        self.lb_minimum_score = Controles.LB(self).set_font(font)

        lb_current_score_block_k = Controles.LB(self, _("Max score in block") + ":").set_font(font)
        self.lb_current_score_block = Controles.LB(self).set_font(font)
        self.lb_current_score_enough = Controles.LB(self).ponImagen(Iconos.pmCorrecto())
        self.lb_current_score_enough.hide()

        self.lb_active_score_k = Controles.LB(self, _("Active score") + ":").set_font(font)
        self.lb_active_score = Controles.LB(self).set_font(font)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)
        self.show_tb(self.terminar, self.begin)

        separacion = 20
        ly_info = Colocacion.G()
        ly_info.controld(lb_block_k, 0, 0).controld(self.lb_block, 0, 1)
        ly_info.filaVacia(1, separacion)
        ly_info.controld(lb_try_k, 2, 0).controld(self.lb_try, 2, 1)
        ly_info.filaVacia(3, separacion)
        ly_info.controld(lb_minimum_score_k, 4, 0).controld(self.lb_minimum_score, 4, 1)
        ly_info.filaVacia(5, separacion)
        ly_info.controld(lb_current_score_block_k, 6, 0).controld(self.lb_current_score_block, 6, 1)
        ly_info.filaVacia(7, separacion)
        ly_info.controld(self.lb_active_score_k, 8, 0).controld(self.lb_active_score, 8, 1)

        ly_right = Colocacion.V().control(self.tb).relleno().otro(ly_info).relleno()

        w = QtWidgets.QWidget(self)
        w.setLayout(ly_right)
        w.setMinimumWidth(240)

        ly_center = Colocacion.H().control(self.board).control(w).margen(3)

        self.setLayout(ly_center)

        self.restore_video()
        self.show_data()
        self.adjustSize()

    def new_try(self):
        is_white = self.coordinates.new_try()
        self.board.set_side_bottom(is_white)
        if self.cp_initial:
            self.board.set_position(self.cp_initial)
        self.board.set_side_indicator(is_white)
        self.lb_active_score_k.set_text(_("Active score") + ":")
        self.current_score = 0
        self.working = True
        self.time_ini = time.time()
        QtCore.QTimer.singleShot(1000, self.comprueba_time)

    def show_data(self):
        is_white = self.coordinates.current_side()
        self.board.set_side_bottom(is_white)
        if self.cp_initial:
            self.board.set_position(self.cp_initial)
        self.board.set_side_indicator(is_white)
        self.lb_block.set_text("%d/%d" % (self.coordinates.current_block + 1, self.coordinates.num_blocks()))
        self.lb_try.set_text("%d" % self.coordinates.current_try_in_block)
        self.lb_minimum_score.set_text("%d" % self.coordinates.min_score_side())
        self.lb_current_score_block.set_text("%d" % self.coordinates.current_max_in_block)

    def end_block(self):
        self.working = False
        self.board.pon_textos("", "", 1)
        self.lb_active_score_k.set_text(_("Last score") + ":")
        si_pasa_block, si_final = self.coordinates.new_done(self.current_score)
        self.db_coordinates.save(self.coordinates)
        if si_final:
            mens = '<b><big><span style="color:green">%s</span><br><br>%s:<br><center>%s=%d&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s=%d</center' % (
                _('Congratulations, goal achieved'),
                _("Result"), _("White"), self.coordinates.min_score_white, _("Black"), self.coordinates.min_score_black
            )

            QTUtil2.message_result_win(self, mens)
            self.terminar()
            return
        else:
            if si_pasa_block:
                QTUtil2.message(self, _("Block ended"))
                self.lb_active_score.set_text("")
            self.show_tb(self.terminar, self.seguir)
        self.show_data()

    def comprueba_time(self):
        if self.working:
            dif_time = time.time() - self.time_ini
            if dif_time >= 30.0:
                self.end_block()
            else:
                tm = 1000 if dif_time > 1.0 else dif_time * 1000
                QtCore.QTimer.singleShot(tm, self.comprueba_time)

    def begin(self):
        self.seguir()

    def seguir(self):
        self.new_try()
        self.show_tb(self.terminar)
        self.lb_active_score.set_text("0")
        self.show_data()
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
                self.lb_active_score.set_text("%d" % self.current_score)
                self.go_next()
            else:
                QTUtil2.message_error(self, "%s: %s ≠ %s" % (_("Error"), celda, self.square_object))
                self.end_block()

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
