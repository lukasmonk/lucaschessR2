import time

from PySide2 import QtCore

import Code
from Code.Base import Position
from Code.Board import Board2
from Code.CountsCaptures import WRunCommon
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios
from Code.QT import LCDialog


class WRunMate15(LCDialog.LCDialog):
    def __init__(self, owner, db_mate15, mate15, use_pgn):

        LCDialog.LCDialog.__init__(self, owner, _X(_("Mate in %1"), "1½"), Iconos.Mate15(), "runmate15")

        self.configuration = Code.configuration
        self.mate15 = mate15
        self.db_mate15 = db_mate15

        self.use_pgn = use_pgn

        conf_board = self.configuration.config_board("RUNMATE15", 64)

        self.board = Board2.BoardEstatico(self, conf_board)
        self.board.crea()

        # Rotulo informacion
        self.lb_info = Controles.LB(self, "[%d] %s" % (self.mate15.pos + 1, self.mate15.info))
        self.lb_info.align_center().set_wrap()
        self.lb_info.setStyleSheet("QWidget { background-color: #1f497d; color: #FFFFFF;padding: 16px; }")

        self.lb_first_move = Controles.LB(self).set_font_type(puntos=12, peso=500)

        self.bt_check = Controles.PB(self, _("Verify"), self.verify, False).ponIcono(Iconos.Check(), icon_size=20)

        self.lb_result = Controles.LB(self).set_font_type(puntos=12, peso=500)

        # Movimientos
        self.li_lb_wm = []
        ly = Colocacion.G().margen(4)
        for row in range(10):
            lb = Controles.LB(self).set_font_type(puntos=12, peso=500)
            wm = WRunCommon.WEdMovePGN(self) if use_pgn else WRunCommon.WEdMove(self)
            self.li_lb_wm.append((lb, wm))
            ly.controld(lb, row, 0)
            ly.columnaVacia(1, 20)
            ly.control(wm, row, 2)
            lb.hide()
            wm.hide()

        ly.filaVacia(10, 20)
        ly.controlc(self.bt_check, 11, 0, numColumnas=3)
        ly.controlc(self.lb_result, 12, 0, numColumnas=3)
        self.gb = Controles.GB(self, _("Next moves and their solutions"), ly).set_font(
            Controles.FontType(puntos=10, peso=75)
        )
        self.gb.hide()

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Restart"), Iconos.Reset(), self.restart),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)
        self.show_tb(self.terminar, self.begin)

        ly_left = Colocacion.V().control(self.tb).control(self.board)

        ly_right = (
            Colocacion.V()
            .controlc(self.lb_info)
            .espacio(40)
            .controlc(self.lb_first_move)
            .espacio(20)
            .control(self.gb)
            .relleno()
        )

        ly_center = Colocacion.H().otro(ly_left).otro(ly_right).margen(3)

        self.setLayout(ly_center)

        self.restore_video()
        self.adjustSize()

        self.gb.setDisabled(True)

        self.li_lb_wm[0][1].activa()

        self.ultimaCelda = None

    def set_position(self):
        self.show_tb(self.terminar, self.restart)
        self.lb_info.set_text("[%d] %s" % (self.mate15.pos + 1, self.mate15.info))

        fen = self.mate15.fen
        cp = Position.Position()
        cp.read_fen(fen)
        self.board.set_position(cp)

        self.gb.show()
        self.lb_first_move.set_text("%s: %s" % (_("First move"), cp.html(self.mate15.move)))

        self.bt_check.show()

        self.lb_result.hide()

        li_moves = list(self.mate15.resp.keys())
        n_moves = len(li_moves)

        mv = self.mate15.move
        cp.play(mv[:2], mv[2:4], mv[4:])

        for n, (lb, wm) in enumerate(self.li_lb_wm):
            if n < n_moves:
                lb.set_text(cp.html(li_moves[n]))
                lb.show()
                wm.limpia()
                wm.show()
            else:
                wm.hide()
                lb.hide()

        self.gb.setEnabled(True)
        self.li_lb_wm[0][1].activa()
        self.time_base = time.time()

    def pulsada_celda(self, celda):
        if self.use_pgn:
            return

        if self.ultimaCelda:
            self.ultimaCelda.set_text(celda)

            ucld = self.ultimaCelda
            for num, (lb, wm) in enumerate(self.li_lb_wm):
                if wm.origen == ucld:
                    wm.activaDestino()
                    self.ultimaCelda = wm.destino
                    return
                elif wm.destino == ucld:
                    if num < (len(self.mate15.resp) - 1):
                        x = num + 1
                    else:
                        x = 0
                    lb, wm = self.li_lb_wm[x]
                    wm.activa()
                    self.ultimaCelda = wm.origen
                    return

    def ponUltimaCelda(self, wmcelda):
        self.ultimaCelda = wmcelda

    def closeEvent(self, event):
        self.save_video()
        event.accept()

    def process_toolbar(self):
        accion = self.sender().key
        if accion in ["terminar", "cancelar"]:
            self.save_video()
            self.reject()
        elif accion == "comprobar":
            self.verify()
        elif accion == "seguir":
            self.seguir()

    def terminar(self):
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        QTUtil.refresh_gui()

    def begin(self):
        self.set_position()

    def restart(self):
        self.set_position()

    def seguir(self):
        self.mate15 = self.db_mate15.create_new()
        self.set_position()

    def verify(self):
        self.bt_check.hide()

        cp = Position.Position()
        cp.read_fen(self.mate15.fen)

        first_move = self.mate15.move
        cp.play(first_move[:2], first_move[2:4], first_move[4:])
        fen = cp.fen()

        si_error = False

        for pos, (move, resp) in enumerate(self.mate15.resp.items()):

            wm = self.li_lb_wm[pos][1]
            mv_done = wm.movimiento()
            if self.use_pgn:
                cp.read_fen(fen)
                cp.play(move[:2], move[2:4], move[4:])
                mv_done = mv_done.lower().replace(" ", "")
                if not mv_done.endswith("#"):
                    mv_done += "#"
                resp = cp.pgn_translated(resp[:2], resp[2:4], resp[4:]).lower()

            if mv_done == resp:
                wm.correcta()
            else:
                wm.error()
                si_error = True

        if si_error:
            self.bt_check.show()
        else:
            tiempo = time.time() - self.time_base
            self.lb_result.set_text('%s: %.1f"' % (_("Time"), tiempo))
            self.lb_result.show()
            self.mate15.append_try(tiempo)
            self.db_mate15.save(self.mate15)
            self.show_tb(self.terminar, self.seguir)
