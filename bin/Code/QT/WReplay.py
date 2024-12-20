import time

from PySide2 import QtCore

import Code
from Code.Base.Constantes import (
    TB_CONTINUE_REPLAY,
    TB_END_REPLAY,
    TB_FAST_REPLAY,
    TB_PAUSE_REPLAY,
    TB_PGN_REPLAY,
    TB_REPEAT_REPLAY,
    TB_SLOW_REPLAY,
    TB_SETTINGS,
)
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil


def read_params():
    dic = {"SECONDS": 2.0, "START": True, "PGN": True, "BEEP": False, "CUSTOM_SOUNDS": False, "SECONDS_BEFORE": 0.0,
           "REPLAY_CONTINUOUS": False}
    dic.update(Code.configuration.read_variables("PARAMPELICULA"))
    return dic


def param_replay(configuration, parent, with_previous_next) -> bool:
    dic_var = read_params()

    # Datos
    form = FormLayout.FormLayout(
        parent, "%s - %s" % (_("Replay game"), _("Options")), Iconos.Preferencias(), anchoMinimo=460
    )
    form.separador()

    form.seconds(_("Number of seconds between moves"), dic_var.get("SECONDS", 2.0))
    form.separador()

    form.checkbox(_("Start from first move"), dic_var.get("START", True))
    form.separador()

    form.checkbox(_("Show PGN"), dic_var.get("PGN", True))
    form.separador()

    form.checkbox(_("Beep after each move"), dic_var.get("BEEP", False))
    form.separador()

    form.checkbox(_("Custom sounds"), dic_var.get("CUSTOM_SOUNDS", False))
    form.separador()

    form.seconds(_("Seconds before first move"), dic_var.get("SECONDS_BEFORE", 0.0))
    form.separador()

    if with_previous_next:
        form.checkbox(_("Replay of the current and following games"), dic_var.get("REPLAY_CONTINUOUS", False))
        form.separador()

    resultado = form.run()

    if resultado:
        accion, li_resp = resultado

        seconds, if_start, if_pgn, if_beep, if_custom_sounds, seconds_before = li_resp[:6]
        dic_var["SECONDS"] = seconds
        dic_var["SECONDS_BEFORE"] = seconds_before
        dic_var["START"] = if_start
        dic_var["PGN"] = if_pgn
        dic_var["BEEP"] = if_beep
        dic_var["CUSTOM_SOUNDS"] = if_custom_sounds
        if with_previous_next:
            dic_var["REPLAY_CONTINUOUS"] = li_resp[6]
        nom_var = "PARAMPELICULA"
        configuration.write_variables(nom_var, dic_var)
        return True
    else:
        return False


class Replay:
    def __init__(self, manager, next_game=None):
        dic_var = read_params()
        self.manager = manager
        self.procesador = manager.procesador
        self.main_window = manager.main_window
        self.starts_with_black = manager.game.starts_with_black
        self.board = manager.board
        self.seconds = dic_var["SECONDS"]
        self.seconds_before = dic_var["SECONDS_BEFORE"]
        self.if_start = dic_var["START"]
        self.if_beep = dic_var["BEEP"]
        self.if_custom_sounds = dic_var["CUSTOM_SOUNDS"]
        self.rapidez = 1.0
        self.next_game = next_game

        self.previous_visible_capturas = self.main_window.siCapturas
        self.previous_visible_information = self.main_window.siInformacionPGN

        self.with_pgn = dic_var["PGN"]

        self.li_acciones = (
            TB_END_REPLAY,
            TB_SLOW_REPLAY,
            TB_PAUSE_REPLAY,
            TB_CONTINUE_REPLAY,
            TB_FAST_REPLAY,
            TB_REPEAT_REPLAY,
            TB_PGN_REPLAY,
            TB_SETTINGS,
        )

        self.antAcciones = self.main_window.get_toolbar()
        self.main_window.pon_toolbar(self.li_acciones, separator=True)

        self.manager.ponRutinaAccionDef(self.process_toolbar)

        self.show_pause(True, False)

        self.num_moves, self.jugInicial, self.filaInicial, self.is_white = self.manager.jugadaActual()

        self.li_moves = self.manager.game.li_moves
        self.current_position = 0 if self.if_start else self.jugInicial
        self.initial_position = self.current_position

        self.stopped = False

        self.show_information()

        if self.seconds_before > 0.0:
            move = self.li_moves[self.current_position]
            self.board.set_position(move.position_before)
            if not self.sleep_refresh(self.seconds_before):
                return

        self.show_current()

    def sleep_refresh(self, seconds):
        ini_time = time.time()
        while (time.time() - ini_time) < seconds:
            QTUtil.refresh_gui()
            if self.stopped:
                return False
            time.sleep(0.01)
        return True

    def show_information(self):
        if self.with_pgn:
            if self.previous_visible_information:
                self.main_window.activaInformacionPGN(True)
            if self.previous_visible_capturas:
                self.main_window.siCapturas = True
            self.main_window.base.show_replay()
        else:
            if self.previous_visible_information:
                self.main_window.activaInformacionPGN(False)
            if self.previous_visible_capturas:
                self.main_window.siCapturas = False
            self.main_window.base.hide_replay()
        QTUtil.refresh_gui()

    def show_current(self):
        if self.stopped or self.current_position >= len(self.li_moves):
            return

        move = self.li_moves[self.current_position]
        # self.board.set_position(move.position_before)
        if self.current_position > self.initial_position:
            if not self.sleep_refresh(self.seconds / self.rapidez):
                return

        li_movs = [("b", move.to_sq), ("m", move.from_sq, move.to_sq)]
        if move.position.li_extras:
            li_movs.extend(move.position.li_extras)
        self.move_the_pieces(li_movs)

        QtCore.QTimer.singleShot(10, self.skip)

    def move_the_pieces(self, li_movs):
        if self.stopped:
            return
        cpu = self.procesador.cpu
        cpu.reset()
        secs = None

        move = self.li_moves[self.current_position]
        num = self.current_position
        if self.starts_with_black:
            num += 1
        row = int(num / 2)
        self.main_window.end_think_analysis_bar()
        self.main_window.pgnColocate(row, move.position_before.is_white)
        self.main_window.base.pgn_refresh()

        # primero los movimientos
        for movim in li_movs:
            if movim[0] == "m":
                from_sq, to_sq = movim[1], movim[2]
                if secs is None:
                    dc = ord(from_sq[0]) - ord(to_sq[0])
                    df = int(from_sq[1]) - int(to_sq[1])
                    # Maxima distancia = 9.9 ( 9,89... sqrt(7**2+7**2)) = 4 seconds
                    dist = (dc ** 2 + df ** 2) ** 0.5
                    rp = self.rapidez if self.rapidez > 1.0 else 1.0
                    secs = 4.0 * dist / (9.9 * rp)
                cpu.muevePieza(from_sq, to_sq, secs)
        # return
        if secs is None:
            secs = 1.0

        # segundo los borrados
        for movim in li_movs:
            if movim[0] == "b":
                cpu.borraPiezaSecs(movim[1], secs)

        # tercero los cambios
        for movim in li_movs:
            if movim[0] == "c":
                cpu.cambiaPieza(movim[1], movim[2], siExclusiva=True)

        cpu.runLineal()
        wait_seconds = 0.0
        if self.if_custom_sounds:
            wait_seconds = Code.runSound.play_list_seconds(move.sounds_list())
        if wait_seconds == 0.0 and self.if_beep:
            Code.runSound.playBeep()

        self.manager.put_arrow_sc(move.from_sq, move.to_sq)

        self.board.set_position(move.position)

        self.manager.put_view()
        if wait_seconds:
            self.sleep_refresh(wait_seconds / 1000 + 0.2)

    def show_pause(self, si_pausa, si_continue):
        self.main_window.show_option_toolbar(TB_PAUSE_REPLAY, si_pausa)
        self.main_window.show_option_toolbar(TB_CONTINUE_REPLAY, si_continue)

    def process_toolbar(self, key):
        if key == TB_END_REPLAY:
            self.terminar()
        elif key == TB_SLOW_REPLAY:
            self.lento()
        elif key == TB_PAUSE_REPLAY:
            self.pausa()
        elif key == TB_CONTINUE_REPLAY:
            self.seguir()
        elif key == TB_FAST_REPLAY:
            self.rapido()
        elif key == TB_REPEAT_REPLAY:
            self.repetir()
        elif key == TB_PGN_REPLAY:
            self.with_pgn = not self.with_pgn
            self.show_information()

        elif key == TB_SETTINGS:
            self.pausa()
            if param_replay(self.procesador.configuration, self.main_window, False):
                dic_var = read_params()
                self.seconds = dic_var["SECONDS"]
                self.if_start = dic_var["START"]
                self.with_pgn = dic_var["PGN"]
                self.if_beep = dic_var["BEEP"]
                self.if_custom_sounds = dic_var["CUSTOM_SOUNDS"]
                self.seconds_before = dic_var["SECONDS_BEFORE"]
                self.show_information()

    def terminar(self):
        self.stopped = True
        self.main_window.pon_toolbar(self.antAcciones)
        self.manager.ponRutinaAccionDef(None)
        self.manager.xpelicula = None
        if self.previous_visible_capturas:
            self.main_window.siCapturas = True
        if not self.with_pgn:
            self.with_pgn = True
            self.show_information()

    def lento(self):
        self.rapidez /= 1.2

    def rapido(self):
        self.rapidez *= 1.2

    def pausa(self):
        self.stopped = True
        self.show_pause(False, True)

    def seguir(self):
        num_moves, self.current_position, filaInicial, is_white = self.manager.jugadaActual()
        self.current_position += 1
        self.stopped = False
        self.show_pause(True, False)
        self.show_current()

    def repetir(self):
        self.current_position = 0 if self.if_start else self.jugInicial
        self.show_pause(True, False)
        if self.stopped:
            self.stopped = False
            self.show_current()

    def skip(self):
        if self.stopped:
            return
        self.current_position += 1
        if self.current_position >= self.num_moves:
            if self.next_game:
                if self.next_game():
                    self.jugInicial = 0
                    self.current_position = 0
                    self.initial_position = 0
                    self.if_start = True
                    self.antAcciones = self.main_window.get_toolbar()
                    self.main_window.pon_toolbar(self.li_acciones, separator=False)
                    self.li_moves = self.manager.game.li_moves
                    self.num_moves = len(self.li_moves)
                    if self.seconds_before > 0.0:
                        move = self.li_moves[self.current_position]
                        self.board.set_position(move.position_before)
                        if not self.sleep_refresh(self.seconds_before):
                            return
                    self.show_current()
                    return
            self.stopped = True
            self.show_pause(False, False)
        else:
            self.show_current()
