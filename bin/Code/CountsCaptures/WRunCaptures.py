import time

import FasterCode

import Code
from Code.Board import Board2
from Code.CountsCaptures import WRunCommon
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, QTUtil2
from Code.QT import LCDialog


class WRunCaptures(LCDialog.LCDialog):
    def __init__(self, owner, db_captures, capture):

        LCDialog.LCDialog.__init__(self, owner, _("Captures and threats in a game"), Iconos.Captures(), "runcaptures")

        self.configuration = Code.configuration
        self.capture = capture
        self.db_captures = db_captures

        conf_board = self.configuration.config_board("RUNCAPTURES", 64)

        self.board = Board2.BoardEstaticoMensaje(self, conf_board, None)
        self.board.crea()

        # Rotulo informacion
        self.lb_info_game = Controles.LB(self, self.capture.game.titulo("DATE", "EVENT", "WHITE", "BLACK", "RESULT"))

        # Movimientos
        self.liwm_captures = []
        ly = Colocacion.G().margen(4)
        self.visible_captures = 8
        for i in range(16):
            f = i // 2
            c = i % 2
            wm = WRunCommon.WEdMove(self)
            self.liwm_captures.append(wm)
            ly.control(wm, f, c)
            if i >= self.visible_captures:
                wm.hide()

        self.gb_captures = Controles.GB(self, _("Captures"), ly).set_font(Controles.FontType(puntos=10, peso=750))

        self.liwm_threats = []
        ly = Colocacion.G().margen(4)
        self.visible_threats = 8
        for i in range(16):
            f = i // 2
            c = i % 2
            wm = WRunCommon.WEdMove(self)
            self.liwm_threats.append(wm)
            ly.control(wm, f, c)
            if i >= self.visible_threats:
                wm.hide()

        self.gb_threats = Controles.GB(self, _("Threats"), ly).set_font(Controles.FontType(puntos=10, peso=750))

        self.lb_result = Controles.LB(self).set_font_type(puntos=10, peso=500).anchoFijo(254).set_wrap()
        self.lb_info = (
            Controles.LB(self)
            .anchoFijo(254)
            .set_foreground_backgound("white", "#496075")
            .align_center()
            .set_font_type(puntos=self.configuration.x_font_points)
        )

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Verify"), Iconos.Check(), self.verify),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones, icon_size=32)
        self.show_tb(self.terminar, self.begin)

        ly_right = (
            Colocacion.V()
            .control(self.tb)
            .controlc(self.lb_info)
            .relleno()
            .control(self.gb_captures)
            .relleno()
            .control(self.gb_threats)
            .control(self.lb_result)
            .relleno()
        )

        ly_center = Colocacion.H().control(self.board).otro(ly_right)

        ly = Colocacion.V().otro(ly_center).control(self.lb_info_game).margen(3)

        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        # Tiempo
        self.time_base = time.time()

        self.gb_captures.setDisabled(True)
        self.gb_threats.setDisabled(True)

        self.liwm_captures[0].activa()

        self.ultimaCelda = None

        self.pon_info_posic()
        self.set_position()

    def set_position(self):
        self.move_base = self.capture.game.move(self.capture.current_posmove)
        num_move = self.capture.current_posmove + self.capture.current_depth
        if num_move >= len(self.capture.game):
            self.position_obj = self.capture.game.move(-1).position
        else:
            self.position_obj = self.capture.game.move(
                self.capture.current_posmove + self.capture.current_depth
            ).position_before
        self.board.set_position(self.move_base.position_before)

    def pon_info_posic(self):
        self.lb_info.set_text(
            "%s: %d + %s: %d<br>%s: %d"
            % (
                _("Position"),
                self.capture.current_posmove,
                _("Depth"),
                self.capture.current_depth,
                _("Total moves"),
                len(self.capture.game),
            )
        )

    def pulsada_celda(self, celda):
        if self.ultimaCelda:
            self.ultimaCelda.set_text(celda)

            self.test_celdas()
            ucld = self.ultimaCelda
            for liwm in (self.liwm_captures, self.liwm_threats):
                for num, wm in enumerate(liwm):
                    if wm.origen == ucld:
                        wm.activaDestino()
                        self.ultimaCelda = wm.destino
                        return
                    elif wm.destino == ucld:
                        if num < (len(liwm) - 1):
                            x = num + 1
                        else:
                            x = 0
                        wm = liwm[x]
                        wm.activa()
                        self.ultimaCelda = wm.origen
                        return

    def test_celdas(self):
        if len(self.liwm_captures[self.visible_captures - 1].movimiento()) == 4:
            complete = True
            for num, wm in enumerate(self.liwm_captures):
                if num >= self.visible_captures:
                    break
                if len(wm.movimiento()) != 4:
                    complete = False
                    break
            if complete:
                self.visible_captures += 2
                for num, wm in enumerate(self.liwm_captures):
                    if num < self.visible_captures:
                        if not wm.isVisible():
                            wm.setVisible(True)
        if len(self.liwm_threats[self.visible_threats - 1].movimiento()) == 4:
            complete = True
            for num, wm in enumerate(self.liwm_threats):
                if num >= self.visible_threats:
                    break
                if len(wm.movimiento()) != 4:
                    complete = False
                    break
            if complete:
                self.visible_threats += 2
                for num, wm in enumerate(self.liwm_threats):
                    if num < self.visible_threats:
                        wm.show()

    def ponUltimaCelda(self, wmcelda):
        self.ultimaCelda = wmcelda

    def closeEvent(self, event):
        self.save_video()
        event.accept()

    def terminar(self):
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        self.tb.setEnabled(True)
        QTUtil.refresh_gui()

    def begin(self):
        self.seguir()

    def seguir(self):
        self.pon_info_posic()
        self.set_position()
        self.lb_result.set_text("")
        for wm in self.liwm_captures:
            wm.limpia()
        for wm in self.liwm_threats:
            wm.limpia()

        self.tb.setEnabled(False)

        # Mostramos los movimientos según depth
        depth = self.capture.current_depth
        if depth:
            txt_ant = ""
            for x in range(depth):
                if not self.configuration.x_captures_showall:
                    if x != depth - 1:
                        continue
                move = self.capture.game.move(self.capture.current_posmove + x)
                txt = move.pgn_translated()
                if txt == txt_ant:
                    self.board.pon_texto("", 1)
                    QTUtil.refresh_gui()
                    time.sleep(0.3)
                txt_ant = txt
                self.board.pon_texto(txt, 0.9)
                QTUtil.refresh_gui()
                dif = depth - x
                factor = 1.0 - dif * 0.1
                if factor < 0.7:
                    factor = 0.7
                time.sleep(2.6 * factor * factor)
                self.board.pon_texto("", 1)
                QTUtil.refresh_gui()

        # Ponemos el toolbar
        self.show_tb(self.verify, self.terminar)

        # Activamos capturas
        self.gb_captures.setEnabled(True)
        self.gb_threats.setEnabled(True)

        # Marcamos el tiempo
        self.time_base = time.time()

        self.liwm_captures[0].activa()

    def verify(self):
        tiempo = time.time() - self.time_base

        def test(liwm, si_mb):
            st_busca = {mv.xfrom() + mv.xto() for mv in FasterCode.get_captures(self.position_obj.fen(), si_mb)}
            st_sel = set()
            ok = True
            for wm in liwm:
                wm.deshabilita()
                mv = wm.movimiento()
                if mv:
                    if mv in st_sel:
                        wm.repetida()
                    elif mv in st_busca:
                        wm.correcta()
                        st_sel.add(mv)
                    else:
                        wm.error()
                        ok = False
            if ok:
                ok = (len(st_busca) == len(st_sel)) or st_sel == 16
            return ok

        ok_captures = test(self.liwm_captures, True)
        ok_threats = test(self.liwm_threats, False)

        ok = ok_captures and ok_threats
        xtry = self.capture.current_posmove, self.capture.current_depth, ok, tiempo
        self.capture.tries.append(xtry)

        if ok:
            self.capture.current_depth += 1
            if (self.capture.current_posmove + self.capture.current_depth) >= (len(self.capture.game) + 1):
                QTUtil2.message_result_win(self, _("Training finished") + "<br><br>" +
                                           _('Congratulations, goal achieved'))
                self.db_captures.change_count_capture(self.capture)
                self.terminar()
                return
            self.lb_result.set_text("%s (%d)" % (_("Right, go to the next level of depth"), self.capture.current_depth))
            self.lb_result.set_foreground("green")

        else:
            if self.capture.current_depth >= 1:
                self.capture.current_posmove += self.capture.current_depth - 1
                if self.capture.current_posmove < 0:
                    self.capture.current_posmove = 0
                self.capture.current_depth = 0
                self.lb_result.set_text(
                    "%s (%d)" % (_("Wrong, return to the last position solved"), self.capture.current_posmove)
                )
                self.lb_result.set_foreground("red")
            else:
                self.lb_result.set_text(_("Wrong, you must repeat this position"))
                self.lb_result.set_foreground("red")
            self.board.set_position(self.position_obj)

        self.db_captures.change_count_capture(self.capture)
        self.show_tb(self.terminar, self.seguir)
