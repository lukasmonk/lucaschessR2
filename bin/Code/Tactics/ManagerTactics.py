import time

from PySide2.QtCore import Qt

from Code import Manager
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_CHANGE,
    TB_NEXT,
    TB_HELP,
    TB_UTILITIES,
    GT_TACTICS,
)
from Code.CompetitionWithTutor import WCompetitionWithTutor
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.Tactics import Tactics


class ManagerTactics(Manager.Manager):
    def start(self, tactic: Tactics.Tactic):
        self.reiniciando = False
        self.tactic = tactic
        self.tactic.leeDatos()
        self.tactic.work_reset_positions()
        self.is_tutor_enabled = False
        self.ayudas_iniciales = 0
        self.is_competitive = True
        self.game_obj, self.game_base = self.tactic.work_read_position()
        self.reiniciar()

    def reiniciar(self):
        if self.reiniciando:
            return
        self.reiniciando = True

        self.main_window.activaInformacionPGN(False)

        self.pointView = self.tactic.pointView()

        self.with_automatic_jump = self.tactic.with_automatic_jump()

        self.pos_obj = 0

        cp = self.game_obj.first_position
        is_white = cp.is_white
        if self.pointView:
            is_white = self.pointView == 1
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        if self.game_base:
            self.game = self.game_base
        else:
            self.game.set_position(cp)

        self.game_type = GT_TACTICS

        self.human_is_playing = False

        self.main_window.set_activate_tutor(False)
        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True, True)
        self.informacionActivable = True
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.set_toolbar("init")

        titulo = self.tactic.work_info(False)
        self.set_label1(titulo)
        self.pgn_refresh(True)
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        if self.game_base:
            self.repiteUltimaJugada()
            self.goto_end()

        self.show_label_positions()
        self.state = ST_PLAYING
        self.reiniciando = False
        self.board.dbvisual_set_show_always(False)

        self.num_bad_tries = 0
        if self.tactic.advanced:
            self.board.show_coordinates(False)

            self.ini_clock = time.time()
            self.wsolve = self.main_window.base.wsolve
            self.wsolve.set_game(self.game_obj, self.advanced_return)

        else:
            self.play_next_move()

    def advanced_return(self, solved):
        self.tactic.masSegundos(time.time() - self.ini_clock)
        self.wsolve.hide()
        self.board.show_coordinates(True)
        more_errors = self.wsolve.errors
        more_helps = self.wsolve.helps
        if more_errors > 0 or more_helps > 0:
            self.put_penalization()
        if solved:
            for move in self.game_obj.li_moves:
                self.game.add_move(move)
            self.goto_end()
            self.pgn_refresh(self.is_human_side_white)
            self.end_line()

        else:
            self.tactic.advanced = False
            self.tactic.set_advanced(False)
            self.play_next_move()

    def set_toolbar(self, modo):
        if modo == "end":
            li_opciones = [TB_CLOSE, TB_CONFIG, TB_UTILITIES, TB_NEXT]
            if not self.tactic.reinforcement.is_activated():
                li_opciones.insert(1, TB_CHANGE)
        else:
            li_opciones = [TB_CLOSE, TB_HELP, TB_REINIT, TB_CONFIG]
            if modo == "init":
                if not self.tactic.reinforcement.is_activated():
                    li_opciones.insert(2, TB_CHANGE)

        Manager.Manager.set_toolbar(self, li_opciones)

    def show_label_positions(self):
        html = self.tactic.work_info_position()
        self.set_label2(html)

    def put_penalization(self):
        self.tactic.work_add_error()
        self.show_label_positions()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_CONFIG:
            if self.tactic.advanced:
                txt = _("Disable")
                ico = Iconos.Remove1()
            else:
                txt = _("Enable")
                ico = Iconos.Add()
            li_mas_opciones = [("lmo_advanced", "%s: %s" % (txt, _("Advanced mode")), ico), (None, None, None)]
            if self.with_automatic_jump:
                li_mas_opciones.append(("lmo_stop", _("Stop after solving"), Iconos.Stop()))
            else:
                li_mas_opciones.append(("lmo_jump", _("Jump to the next after solving"), Iconos.Jump()))

            resp = self.configurar(with_sounds=True, with_change_tutor=False, li_extra_options=li_mas_opciones)
            if resp in ("lmo_stop", "lmo_jump"):
                self.with_automatic_jump = resp == "lmo_jump"
                self.tactic.set_automatic_jump(self.with_automatic_jump)
            elif resp == "lmo_advanced":
                self.tactic.advanced = not self.tactic.advanced
                self.tactic.set_advanced(self.tactic.advanced)
                self.reiniciar()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_HELP:
            self.help()

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_NEXT:
            self.ent_siguiente()

        elif key == TB_CHANGE:
            self.cambiar()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def help(self):
        move_obj = self.game_obj.move(self.pos_obj)
        self.board.ponFlechasTmp(([move_obj.from_sq, move_obj.to_sq, True],))
        self.put_penalization()

    def control_teclado(self, nkey, modifiers):
        if nkey in (Qt.Key_Plus, Qt.Key_PageDown):
            if self.state == ST_ENDGAME:
                self.ent_siguiente()

    def list_help_keyboard(self):
        return [("+/%s" % _("Page Down"), _("Next position"))]
                # ("T", _("Save position in 'Selected positions' file"))]

    def ent_siguiente(self):
        if self.tactic.work_game_finished():
            self.end_game()
        else:
            self.start(self.tactic)

    def end_game(self):
        self.board.show_coordinates(True)
        self.procesador.start()
        self.procesador.entrenamientos.tactics_train(self.tactic)

    def final_x(self):
        self.end_game()
        return False

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        if self.pos_obj == len(self.game_obj) or self.game.is_mate():
            self.end_line()
            return

        si_rival = is_white == self.is_engine_side_white

        if si_rival:
            move = self.game_obj.move(self.pos_obj)
            self.move_the_pieces(move.liMovs, True)
            self.add_move(move, False)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.activate_side(is_white)
            self.ini_clock = time.time()

    def end_line(self):
        self.state = ST_ENDGAME
        self.disable_all()

        self.tactic.work_line_finished()
        if self.tactic.finished():
            self.end_training()
            return False

        if self.with_automatic_jump and not self.tactic.w_error:
            self.ent_siguiente()
        else:
            QTUtil2.temporary_message(self.main_window, _("Line completed"), 0.7)
            self.set_label1(self.tactic.w_label)
            self.set_toolbar("end")
            if self.configuration.x_director_icon is not None:
                self.board.dbvisual_set_show_always(True)
            self.game = self.game_obj.copia()
            self.goto_end()

        return True

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.set_toolbar("first_move")
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        a1h8 = move.movimiento()
        move_obj = self.game_obj.move(self.pos_obj)
        a1h8_obj = move_obj.movimiento()
        is_main = a1h8 == a1h8_obj or move.is_mate
        is_variation = False
        if not is_main:
            if len(move_obj.variations) > 0:
                li_a1h8 = move_obj.variations.list_movimientos()
                is_variation = a1h8 in li_a1h8
                if is_variation:
                    li_flechas = [(x[:2], x[2:4], False) for x in li_a1h8]
                    li_flechas.append((a1h8_obj[:2], a1h8_obj[2:4], True))
                    self.board.ponFlechasTmp(li_flechas)
            if not is_variation:
                self.put_penalization()
                self.num_bad_tries += 1
                if self.num_bad_tries > 3:
                    self.board.mark_position(move_obj.from_sq)
                    if self.num_bad_tries > 6:
                        self.board.creaFlechaTmp(move_obj.from_sq, move_obj.to_sq, True)
            self.beep_error()
            self.sigueHumano()
            return False

        seconds = time.time() - self.ini_clock
        self.tactic.masSegundos(seconds)

        self.add_move(move, True)
        self.num_bad_tries = 0
        self.play_next_move()
        return True

    def add_move(self, move, si_nuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.pos_obj += 1

        self.beepExtendido(si_nuestra)

        self.pgn_refresh(self.game.last_position.is_white)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.refresh()

    def cambiar(self):
        if self.tactic.w_next_position >= 0:
            pos = WCompetitionWithTutor.edit_training_position(
                self.main_window,
                self.tactic.title_extended(),
                self.tactic.w_next_position,
                pos=self.tactic.w_next_position,
            )
            if pos is not None:
                self.tactic.w_next_position = pos - 1
                self.tactic.work_set_current_position(self.tactic.w_next_position)

                self.ent_siguiente()

    def end_training(self):
        self.tactic.end_training()
        mensaje = "<big>%s<br>%s</big>" % (_("Congratulations, goal achieved"), _("GAME OVER"))
        self.message_on_pgn(mensaje)
        self.end_game()
