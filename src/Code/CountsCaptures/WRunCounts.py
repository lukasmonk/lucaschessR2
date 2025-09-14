import time

import FasterCode
from PySide2 import QtCore, QtGui

import Code
from Code.Board import Board2
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, QTUtil2
from Code.QT import LCDialog


class WRunCounts(LCDialog.LCDialog):
    def __init__(self, owner, db_counts, count):

        LCDialog.LCDialog.__init__(self, owner, _("Count moves"), Iconos.Count(), "runcounts")

        self.configuration = Code.configuration
        self.count = count
        self.db_counts = db_counts

        self.move_base = None
        self.position_obj = None

        conf_board = self.configuration.config_board("RUNCOUNTS", 64)

        self.board = Board2.BoardEstaticoMensaje(self, conf_board, None)
        self.board.crea()

        # Rotulo informacion
        self.lb_info_game = Controles.LB(
            self, self.count.game.titulo("DATE", "EVENT", "WHITE", "BLACK", "RESULT")
        )  # .set_font_type(puntos=self.configuration.x_pgn_fontpoints)

        # Movimientos
        self.ed_moves = Controles.ED(self, "").set_font_type(puntos=32)
        self.ed_moves.setValidator(QtGui.QIntValidator(self.ed_moves))
        self.ed_moves.setAlignment(QtCore.Qt.AlignRight)
        self.ed_moves.anchoFijo(72)

        ly = Colocacion.H().relleno().control(self.ed_moves).relleno()

        self.gb_counts = Controles.GB(self, _("Number of moves"), ly).set_font(Controles.FontType(puntos=10, peso=75))

        self.lb_result = Controles.LB(self).set_font_type(puntos=10, peso=500).anchoFijo(254).altoFijo(32).set_wrap()
        self.lb_info = (
            Controles.LB(self)
            .set_font_type(puntos=14, peso=500)
            .set_foreground_backgound("white", "#496075")
            .align_center()
        )

        # Botones
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Verify"), Iconos.Check(), self.verify),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)
        self.show_tb(self.terminar, self.begin)

        ly_right = (
            Colocacion.V()
            .control(self.tb)
            .controlc(self.lb_info)
            .relleno()
            .control(self.gb_counts)
            .relleno()
            .control(self.lb_result)
            .relleno()
        )

        ly_center = Colocacion.H().control(self.board).otro(ly_right)

        ly = Colocacion.V().otro(ly_center).control(self.lb_info_game).margen(3)

        self.setLayout(ly)

        self.restore_video()
        # self.adjustSize()

        # Tiempo
        self.time_base = time.time()

        self.gb_counts.setDisabled(True)

        self.pon_info_posic()
        self.set_position()

    def pulsada_celda(self, celda):  # Incluida por compatibilidad del Board
        pass

    def set_position(self):
        self.move_base = self.count.game.move(self.count.current_posmove)
        num_move = self.count.current_posmove + self.count.current_depth
        if num_move >= len(self.count.game):
            self.position_obj = self.count.game.move(-1).position
        else:
            self.position_obj = self.count.game.move(
                self.count.current_posmove + self.count.current_depth
            ).position_before
        self.board.set_position(self.move_base.position_before)
        self.ed_moves.setFocus()

    def pon_info_posic(self):
        self.lb_info.set_text(
            "%s: %d + %s: %d<br>%s: %d"
            % (
                _("Position"),
                self.count.current_posmove,
                _("Depth"),
                self.count.current_depth,
                _("Total moves"),
                len(self.count.game),
            )
        )

    def closeEvent(self, event):
        self.save_video()
        event.accept()

    def terminar(self):
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        QTUtil.refresh_gui()

    def begin(self):
        self.seguir()

    def seguir(self):
        self.pon_info_posic()
        self.set_position()
        self.lb_result.set_text("")
        self.ed_moves.set_text("")

        self.show_tb()

        # Mostramos los movimientos según depth
        depth = self.count.current_depth
        if depth:
            for x in range(depth):
                if not self.configuration.x_counts_showall:
                    if x != depth - 1:
                        continue
                move = self.count.game.move(self.count.current_posmove + x)
                txt = move.pgn_translated()
                self.board.pon_texto(txt, 0.9)
                QTUtil.refresh_gui()
                dif = depth - x
                factor = 1.0 - dif * 0.1
                if factor < 0.5:
                    factor = 0.5

                time.sleep(2.6 * factor * factor)
                self.board.pon_texto("", 0)
                QTUtil.refresh_gui()

        # Ponemos el toolbar
        self.show_tb(self.verify, self.terminar)

        # Activamos capturas
        self.gb_counts.setEnabled(True)

        # Marcamos el tiempo
        self.time_base = time.time()

        self.ed_moves.setFocus()

    def verify(self):
        tiempo = time.time() - self.time_base

        moves = FasterCode.get_exmoves_fen(self.position_obj.fen())

        cmoves = self.ed_moves.texto().strip()
        num_moves_calculated = int(cmoves) if cmoves.isdigit() else 0
        ok = num_moves_calculated == len(moves)

        xtry = self.count.current_posmove, self.count.current_depth, ok, tiempo
        self.count.tries.append(xtry)

        if ok:
            self.count.current_depth += 1
            if (self.count.current_posmove + self.count.current_depth) >= (len(self.count.game) + 1):
                QTUtil2.message_result_win(self, _("Training finished") + "<br><br>" +
                                           _('Congratulations, goal achieved'))
                self.db_counts.change_count_capture(self.count)
                self.terminar()
                return
            self.lb_result.set_text("%s (%d)" % (_("Right, go to the next level of depth"), self.count.current_depth))
            self.lb_result.set_foreground("green")

        else:
            if self.count.current_depth >= 1:
                self.count.current_posmove += self.count.current_depth - 1
                if self.count.current_posmove < 0:
                    self.count.current_posmove = 0
                self.count.current_depth = 0
                self.lb_result.set_text(
                    "%s (%d)" % (_("Wrong, return to the last position solved"), self.count.current_posmove)
                )
                self.lb_result.set_foreground("red")
            else:
                self.lb_result.set_text(_("Wrong, you must repeat this position"))
                self.lb_result.set_foreground("red")
            self.board.set_position(self.position_obj)
            for x in moves:
                self.board.creaFlechaTmp(x.xfrom(), x.xto(), False)

        self.db_counts.change_count_capture(self.count)
        self.show_tb(self.terminar, self.seguir)
