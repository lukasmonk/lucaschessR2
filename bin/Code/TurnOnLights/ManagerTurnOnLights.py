import time

from Code import Manager
from Code.Base import Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_ADVICE,
    TB_NEXT,
    TB_UTILITIES,
    GT_TURN_ON_LIGHTS,
)
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.TurnOnLights import TurnOnLights


class ManagerTurnOnLights(Manager.Manager):
    def start(self, num_theme, num_block, tol):

        if hasattr(self, "reiniciando"):
            if self.reiniciando:
                return
        self.reiniciando = True

        self.num_theme = num_theme
        self.num_block = num_block
        self.tol = tol
        self.block = self.tol.get_block(self.num_theme, self.num_block)
        self.block.shuffle()

        self.calculation_mode = self.tol.is_calculation_mode()
        self.penaltyError = self.block.penaltyError(self.calculation_mode)
        self.penaltyHelp = self.block.penaltyHelp(self.calculation_mode)
        # self.factorDistancia = self.block.factorDistancia() # No se usa es menor que 1.0

        self.av_seconds = self.block.av_seconds()
        if self.av_seconds:
            cat, ico = self.block.cqualification(self.calculation_mode)
            self.lb_previous = '%s - %0.2f"' % (cat, self.av_seconds)
        else:
            self.lb_previous = None
        self.num_line = 0
        self.num_lines = len(self.block)
        self.num_moves = 0

        self.total_time_used = 0.0
        self.hints = 0
        self.errores = 0
        self.dicFENayudas = {}  # se muestra la arrow a partir de dos del mismo

        self.game_type = GT_TURN_ON_LIGHTS

        self.human_is_playing = False

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(False)
        self.ayudas_iniciales = 0

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True, True)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)

        self.reiniciando = False

        self.next_line_run()

    def pon_rotulos(self, next):
        r1 = _("Calculation mode") if self.calculation_mode else _("Memory mode")
        r1 += "<br>%s" % self.line.label

        if self.lb_previous:
            r1 += "<br><b>%s</b>" % self.lb_previous
        if self.num_line:
            av_secs, txt = self.block.calc_current(
                self.num_line - 1, self.total_time_used, self.errores, self.hints, self.calculation_mode
            )
            r1 += '<br><b>%s: %s - %0.2f"' % (_("Current"), txt, av_secs)
        self.set_label1(r1)
        if next is not None:
            r2 = "<b>%d/%d</b>" % (self.num_line + next, self.num_lines)
        else:
            r2 = None
        self.set_label2(r2)

    def next_line(self):
        if self.num_line < self.num_lines:
            self.line = self.block.line(self.num_line)
            self.num_move = -1
            self.ini_time = None

            cp = Position.Position()
            cp.read_fen(self.line.fen)
            self.game.set_position(cp)

            is_white = cp.is_white
            self.is_human_side_white = is_white
            self.is_engine_side_white = not is_white
            self.set_position(self.game.last_position)
            self.put_pieces_bottom(is_white)
            self.pgn_refresh(True)

            self.game.pending_opening = False
            self.pon_rotulos(1)

    def next_line_run(self):
        li_options = [TB_CLOSE, TB_ADVICE, TB_REINIT]
        self.set_toolbar(li_options)

        self.next_line()

        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.state = ST_PLAYING

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_ADVICE:
            self.get_help()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=False)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_NEXT:
            self.next_line_run()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def reiniciar(self):
        if self.state == ST_PLAYING:
            if self.ini_time:
                self.total_time_used += time.time() - self.ini_time
        if self.total_time_used:
            self.block.new_reinit(self.total_time_used, self.errores, self.hints)
            self.total_time_used = 0.0
            TurnOnLights.write_tol(self.tol)
        self.main_window.activaInformacionPGN(False)
        self.start(self.num_theme, self.num_block, self.tol)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        self.num_move += 1
        if self.num_move >= self.line.total_moves():
            self.end_line()
            return

        if siRival:
            pv = self.line.get_move(self.num_move)
            from_sq, to_sq, promotion = pv[:2], pv[2:4], pv[4:]
            self.rival_has_moved(from_sq, to_sq, promotion)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.base_time = time.time()
            if not (
                    self.calculation_mode and self.ini_time is None
            ):  # Se inicia salvo que sea el principio de la linea
                self.ini_time = self.base_time
            self.activate_side(is_white)
            if self.calculation_mode:
                self.board.setDispatchMove(self.dispatchMove)

    def dispatchMove(self):
        if self.ini_time is None:
            self.ini_time = time.time()

    def end_line(self):
        self.num_line += 1
        islast_line = self.num_line == self.num_lines
        if islast_line:

            # Previous
            ant_tm = self.block.av_seconds()
            ant_done = self.tol.done_level()
            ant_cat_level, nada = self.tol.cat_num_level()
            ant_cat_global = self.tol.cat_global()

            num_moves = self.block.num_moves()
            ta = self.total_time_used + self.errores * self.penaltyError + self.hints * self.penaltyHelp
            tm = ta / num_moves
            self.block.new_result(tm, self.total_time_used, self.errores, self.hints)
            TurnOnLights.write_tol(self.tol)
            cat_block, ico = TurnOnLights.qualification(tm, self.calculation_mode)
            cat_level, ico = self.tol.cat_num_level()
            cat_global = self.tol.cat_global()

            txt_more_time = ""
            txt_more_cat = ""
            txt_more_line = ""
            txt_more_global = ""
            if ant_tm is None or tm < ant_tm:
                txt_more_time = '<span style="color:red">%s</span>' % _("New record")
                done = self.tol.done_level()
                if done and (not ant_done):
                    if not self.tol.islast_level():
                        txt_more_line = "%s<hr>" % _("Open the next level")
                if cat_level != ant_cat_level:
                    txt_more_cat = '<span style="color:red">%s</span>' % _("New")
                if cat_global != ant_cat_global:
                    txt_more_global = '<span style="color:red">%s</span>' % _("New")

            cErrores = (
                '<tr><td align=right> %s </td><td> %d (x%d"=%d")</td></tr>'
                % (_("Errors"), self.errores, self.penaltyError, self.errores * self.penaltyError)
                if self.errores
                else ""
            )
            cAyudas = (
                '<tr><td align=right> %s </td><td> %d (x%d"=%d")</td></tr>'
                % (_("Hints"), self.hints, self.penaltyHelp, self.hints * self.penaltyHelp)
                if self.hints
                else ""
            )
            mens = (
                    "<hr><center><big>"
                    + _("You have finished this block of positions")
                    + "<hr><table>"
                    + '<tr><td align=right> %s </td><td> %0.2f"</td></tr>' % (_("Time used"), self.total_time_used)
                    + cErrores
                    + cAyudas
                    + '<tr><td align=right> %s: </td><td> %0.2f" %s</td></tr>' % (_("Time assigned"), ta, txt_more_time)
                    + "<tr><td align=right> %s: </td><td> %d</td></tr>" % (_("Total moves"), num_moves)
                    + '<tr><td align=right> %s: </td><td> %0.2f"</td></tr>' % (_("Average time"), tm)
                    + "<tr><td align=right> %s: </td><td> %s</td></tr>" % (_("Block qualification"), cat_block)
                    + "<tr><td align=right> %s: </td><td> %s %s</td></tr>"
                    % (_("Level qualification"), cat_level, txt_more_cat)
                    + "<tr><td align=right> %s: </td><td> %s %s</td></tr>"
                    % (_("Global qualification"), cat_global, txt_more_global)
                    + "</table></center></big><hr>"
                    + txt_more_line
            )
            self.pon_rotulos(None)
            QTUtil2.message_bold(self.main_window, mens, _("Result"))
            self.total_time_used = 0

        else:
            if (self.tol.go_fast is True) or ((self.tol.go_fast is None) and self.tol.work_level > 0):
                self.next_line_run()
                return
            QTUtil2.temporary_message(self.main_window, _("Line completed"), 1.3)
            self.pon_rotulos(0)

        self.state = ST_ENDGAME
        self.disable_all()

        li_options = [TB_CLOSE, TB_REINIT, TB_CONFIG, TB_UTILITIES]

        if not islast_line:
            li_options.append(TB_NEXT)

        self.set_toolbar(li_options)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        if self.ini_time is None:
            self.ini_time = self.base_time
        end_time = time.time()
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        movimiento = move.movimiento().lower()
        if movimiento == self.line.get_move(self.num_move).lower():
            self.move_the_pieces(move.liMovs)
            self.add_move(move, True)
            self.error = ""
            self.total_time_used += end_time - self.ini_time
            self.play_next_move()
            return True

        self.errores += 1
        self.continue_human()
        return False

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def rival_has_moved(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.error = ""

    def get_help(self):
        self.hints += 1
        mov = self.line.get_move(self.num_move).lower()
        self.board.mark_position(mov[:2])
        fen = self.game.last_position.fen()
        if not (fen in self.dicFENayudas):
            self.dicFENayudas[fen] = 1
        else:
            self.dicFENayudas[fen] += 1
            if self.dicFENayudas[fen] > 2:
                self.put_arrow_sc(mov[:2], mov[2:4])

    def end_game(self):
        self.procesador.start()
        self.procesador.showTurnOnLigths(self.tol.name)

    def final_x(self):
        self.procesador.start()
        return False

    def current_pgn(self):
        resp = '[Event "%s"]\n' % _("Turn on the lights")
        resp += '[Site "%s"]\n' % self.line.label.replace("<br>", " ").strip()
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgn_base()

        return resp
