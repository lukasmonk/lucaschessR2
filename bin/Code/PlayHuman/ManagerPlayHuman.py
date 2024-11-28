import Code
from Code import Adjournments
from Code import Manager
from Code.Base.Constantes import (
    TB_TAKEBACK,
    TB_ADJOURN,
    TB_CANCEL,
    TB_CONTINUE,
    TB_DRAW,
    TB_PAUSE,
    TB_RESIGN,
    GT_HUMAN,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    TERMINATION_RESIGN,
    TERMINATION_WIN_ON_TIME,
    ST_PAUSE,
    WHITE,
    BLACK,
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_UTILITIES,
    RESULT_DRAW,
    TERMINATION_DRAW_AGREEMENT,
)

from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2


class ManagerPlayHuman(Manager.Manager):
    with_analysis_bar = False
    with_takeback = True
    timed = False
    reinicio = None
    max_seconds = None
    seconds_per_move = None
    toolbar_state = None
    white = None
    black = None
    is_human_side_white = True  # necesario en adjourn
    auto_rotate = False

    def start(self, dic_var):
        self.base_inicio(dic_var)
        self.start_message(nomodal=Code.eboard and Code.is_linux)  # nomodal: problema con eboard
        self.play_next_move()

    def base_inicio(self, dic_var):
        self.reinicio = dic_var

        self.game_type = GT_HUMAN

        self.state = ST_PLAYING

        if dic_var.get("ACTIVATE_EBOARD"):
            Code.eboard.activate(self.board.dispatch_eboard)

        self.with_takeback = True

        w, b = dic_var["WHITE"], dic_var["BLACK"]
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.timed = dic_var["WITHTIME"]
        self.tc_white.set_displayed(self.timed)
        self.tc_black.set_displayed(self.timed)
        if self.timed:
            self.max_seconds = dic_var["MINUTES"] * 60.0
            self.seconds_per_move = dic_var["SECONDS"]

            self.tc_white.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
            self.tc_black.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)

            time_control = "%d" % int(self.max_seconds)
            if self.seconds_per_move:
                time_control += "+%d" % self.seconds_per_move
            self.game.set_tag("TimeControl", time_control)

        self.pon_toolbar()

        self.main_window.active_game(True, self.timed)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints(siQuitarAtras=False)
        self.put_pieces_bottom(True)

        self.show_info_extra()

        self.pgn_refresh(True)

        self.white, self.black = w, b

        if self.timed:
            tp_bl, tp_ng = self.tc_white.label(), self.tc_black.label()

            self.main_window.set_data_clock(w, tp_bl, b, tp_ng)
            self.refresh()
        else:
            self.main_window.base.change_player_labels(w, b)

        self.game.add_tag_timestart()

        self.main_window.start_clock(self.set_clock, 1000)

        self.auto_rotate = self.get_auto_rotate()

        self.check_boards_setposition()

        self.human_is_playing = True

    def pon_toolbar(self):
        if self.state == ST_PLAYING:
            if self.toolbar_state != self.state:
                li = [
                    TB_CANCEL,
                    TB_RESIGN,
                    TB_DRAW,
                    TB_TAKEBACK,
                    TB_REINIT,
                    TB_PAUSE,
                    TB_ADJOURN,
                    TB_CONFIG,
                    TB_UTILITIES,
                ]
                self.set_toolbar(li)

        elif self.state == ST_PAUSE:
            li = [TB_CONTINUE]
            self.set_toolbar(li)
        else:
            li = [TB_CLOSE]
            self.set_toolbar(li)

        self.toolbar_state = self.state

    def show_time(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        tc.set_labels()

    def set_clock(self):
        if self.state == ST_ENDGAME:
            self.main_window.stop_clock()
            return
        if self.state != ST_PLAYING:
            return

        if self.timed:
            if Code.eboard:
                Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

            is_white = self.game.last_position.is_white

            tc = self.tc_white if is_white else self.tc_black
            tc.set_labels()

            if tc.time_is_consumed():
                self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE)
                self.state = ST_ENDGAME  # necesario que esté antes de stop_clock para no entrar en bucle
                self.stop_clock(is_white)
                self.show_result()
                return

    def stop_clock(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        time_s = tc.stop()
        self.show_time(is_white)
        return time_s

    def run_action(self, key):
        if key == TB_CANCEL:
            self.finalizar()

        elif key == TB_RESIGN:
            self.rendirse()

        elif key == TB_DRAW:
            if self.tablasPlayer():
                self.show_result()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_PAUSE:
            self.xpause()

        elif key == TB_CONTINUE:
            self.xcontinue()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            if self.state == ST_PLAYING:
                self.configurar([], with_sounds=True, with_change_tutor=self.ayudas_iniciales > 0)

        elif key == TB_UTILITIES:
            li_mas_opciones = [("books", _("Consult a book"), Iconos.Libros())]
            resp = self.utilities(li_mas_opciones)
            if resp == "books":
                si_en_vivo = not self.is_finished()
                li_movs = self.librosConsulta(si_en_vivo)
                if li_movs and si_en_vivo:
                    from_sq, to_sq, promotion = li_movs[-1]
                    self.player_has_moved(from_sq, to_sq, promotion)
            elif resp == "play":
                self.play_current_position()

        elif key == TB_ADJOURN:
            self.adjourn()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def save_state(self):
        dic = self.reinicio

        # game
        dic["game_save"] = self.game.save()

        # tiempos
        if self.timed:
            self.main_window.stop_clock()
            dic["time_white"] = self.tc_white.save()
            dic["time_black"] = self.tc_black.save()

        return dic

    def restore_state(self, dic):
        self.base_inicio(dic)
        self.game.restore(dic["game_save"])

        if self.timed:
            self.tc_white.restore(dic["time_white"])
            self.tc_black.restore(dic["time_black"])

        self.goto_end()

    def reiniciar(self, siPregunta):
        if siPregunta:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
        if self.timed:
            self.main_window.stop_clock()
        self.game.reset()
        self.toolbar_state = ST_ENDGAME
        self.autosave()
        self.main_window.activaInformacionPGN(False)

        reinicio = self.reinicio.get("REINIT", 0) + 1
        self.game.set_tag("Reinit", str(reinicio))
        self.reinicio["REINIT"] = reinicio

        self.start(self.reinicio)

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            # se guarda en una bd Adjournments dic key = fecha y hora y tipo
            label_menu = _("Play human vs human") + ". " + self.white + " - " + self.black

            self.state = ST_ENDGAME

            self.finalizar()

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        self.restore_state(dic)
        self.check_boards_setposition()
        if self.timed:
            self.show_clocks()
            self.start_message()

        self.pgn_refresh(True)
        self.play_next_move()

    def xpause(self):
        is_white = self.game.last_position.is_white
        tc = self.tc_white if is_white else self.tc_black
        if is_white == self.is_human_side_white:
            tc.pause()
        else:
            tc.reset()
        tc.set_labels()
        self.state = ST_PAUSE
        self.board.set_position(self.game.first_position)
        self.board.disable_all()
        self.main_window.hide_pgn()
        self.pon_toolbar()

    def xcontinue(self):
        self.state = ST_PLAYING
        self.board.set_position(self.game.last_position)
        self.pon_toolbar()
        self.main_window.show_pgn()
        self.play_next_move()

    def final_x(self):
        return self.finalizar()

    def finalizar(self):
        if self.state == ST_ENDGAME:
            return True
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("End game?")):
                return False  # no abandona
            if self.timed:
                self.main_window.stop_clock()
                self.show_clocks()
            self.state = ST_ENDGAME
            self.game.set_unknown()
            self.set_end_game(self.with_takeback)
            self.autosave()
        else:
            if self.timed:
                self.main_window.stop_clock()
            self.state = ST_ENDGAME
            self.main_window.active_game(False, False)
            self.quitaCapturas()
            if self.xRutinaAccionDef:
                self.xRutinaAccionDef(TB_CLOSE)
            else:
                self.procesador.start()

        return False

    def rendirse(self, with_question=True):
        if self.state == ST_ENDGAME:
            return True
        if self.timed:
            self.main_window.stop_clock()
            self.show_clocks()
        if len(self.game) > 0:
            if with_question:
                player = self.white if self.game.last_position.is_white else self.black
                if not QTUtil2.pregunta(self.main_window, f"<big>{player}</big><br>" + _("Do you want to resign?")):
                    return False  # no abandona
            self.game.set_termination(
                TERMINATION_RESIGN, RESULT_WIN_WHITE if not self.game.last_position.is_white else RESULT_WIN_BLACK
            )
            self.autosave()
            self.set_end_game(False)
        else:
            self.main_window.active_game(False, False)
            self.quitaCapturas()
            self.procesador.start()

        return False

    def takeback(self):
        if len(self.game):
            self.game.remove_last_move(self.is_human_side_white)
            if not self.fen:
                self.game.assign_opening()
            self.goto_end()
            self.refresh()
            if self.state == ST_ENDGAME:
                self.state = ST_PLAYING
                self.toolbar_state = None
                self.pon_toolbar()
            self.play_next_move()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.put_view()

        is_white = self.game.is_white()

        if self.game.is_finished():
            self.show_result()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        if self.with_analysis_bar:
            self.main_window.base.analysis_bar.set_game(self.game)

        if self.auto_rotate:
            if is_white != self.board.is_white_bottom:
                self.board.rotate_board()
        self.play_human(is_white)

    def play_human(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        tc.start()
        self.pon_toolbar()
        self.activate_side(is_white)
        self.human_is_playing = True
        self.is_human_side_white = is_white

    def enable_toolbar(self):
        self.main_window.toolbar_enable(True)

    def disable_toolbar(self):
        self.main_window.toolbar_enable(False)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False
        tc = self.tc_white if self.game.last_position.is_white else self.tc_black
        time_s = tc.stop()
        tc.set_labels()

        self.disable_toolbar()

        if self.timed:
            self.show_clocks()

        move.set_time_ms(time_s * 1000)
        move.set_clock_ms(tc.pending_time * 1000)
        self.add_move(move)
        self.move_the_pieces(move.liMovs, False)
        self.beep_extended(True)

        self.error = ""

        self.enable_toolbar()
        self.play_next_move()
        return True

    def add_move(self, move):
        self.game.add_move(move)
        self.show_clocks()
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)

        self.pgn_refresh(self.game.last_position.is_white)

        self.refresh()

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False
        if self.timed:
            self.main_window.stop_clock()

        if Code.eboard and Code.eboard.driver:
            self.main_window.delay_routine(
                300, self.muestra_resultado_delayed
            )  # Para que eboard siga su proceso y no se pare por la pregunta
        else:
            self.muestra_resultado_delayed()

    def muestra_resultado_delayed(self):
        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)
        player = self.white if self.is_human_side_white else self.black

        mensaje = f"{player}. {mensaje}"

        self.beep_result(beep)
        self.autosave()
        QTUtil.refresh_gui()
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        QTUtil2.message(self.main_window, mensaje, px=p.x(), py=p.y(), si_bold=True)
        self.set_end_game(self.with_takeback)

    def show_clocks(self):
        if not self.timed:
            return

        if Code.eboard:
            Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

        for is_white in (WHITE, BLACK):
            tc = self.tc_white if is_white else self.tc_black
            tc.set_labels()

    def tablasPlayer(self):
        if QTUtil2.pregunta(self.main_window, _("Do both players agree to end the game with a draw?")):
            self.game.last_jg().is_draw_agreement = True
            self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
            return True
        return False
