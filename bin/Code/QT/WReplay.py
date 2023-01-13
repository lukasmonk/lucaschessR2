import gettext
_ = gettext.gettext
import time

import Code
from Code.Base.Constantes import (
    TB_CONTINUE_REPLAY,
    TB_END_REPLAY,
    TB_FAST_REPLAY,
    TB_PAUSE_REPLAY,
    TB_PGN_REPLAY,
    TB_REPEAT_REPLAY,
    TB_SLOW_REPLAY,
    TB_CHANGE,
)
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil


def read_params(configuration):
    nomVar = "PARAMPELICULA"
    dic = configuration.read_variables(nomVar)
    if len(dic) == 0:
        dic["SECONDS"] = 2.0
        dic["START"] = True
        dic["PGN"] = True
        dic["BEEP"] = False
        dic["SECONDS_BEFORE"] = 0.0
    return dic


def param_replay(configuration, parent):

    dicVar = read_params(configuration)

    # Datos
    form = FormLayout.FormLayout(parent, _("Replay game"), Iconos.Pelicula(), anchoMinimo=460)
    form.separador()

    form.float(_("Number of seconds between moves"), dicVar.get("SECONDS", 2.0))
    form.separador()

    form.checkbox(_("Start from first move"), dicVar.get("START", True))
    form.separador()

    form.checkbox(_("Show PGN"), dicVar.get("PGN", True))
    form.separador()

    form.checkbox(_("Beep after each move"), dicVar.get("BEEP", False))
    form.separador()

    form.float(_("Seconds before first move"), dicVar.get("SECONDS_BEFORE", 0.0))
    form.separador()

    resultado = form.run()

    if resultado:
        accion, liResp = resultado

        seconds, if_start, if_pgn, if_beep, seconds_before = liResp
        dicVar["SECONDS"] = seconds
        dicVar["SECONDS_BEFORE"] = seconds_before
        dicVar["START"] = if_start
        dicVar["PGN"] = if_pgn
        dicVar["BEEP"] = if_beep
        nomVar = "PARAMPELICULA"
        configuration.write_variables(nomVar, dicVar)
        return seconds, if_start, if_pgn, if_beep, seconds_before
    else:
        return None


class Replay:
    def __init__(self, manager, seconds, if_start, siPGN, if_beep, seconds_before):
        self.manager = manager
        self.procesador = manager.procesador
        self.main_window = manager.main_window
        self.starts_with_black = manager.game.starts_with_black
        self.board = manager.board
        self.seconds = seconds
        self.if_start = if_start
        self.if_beep = if_beep
        self.rapidez = 1.0

        self.previous_visible_capturas = self.main_window.siCapturas
        self.previous_visible_information = self.main_window.siInformacionPGN

        self.siPGN = siPGN

        li_acciones = (
            TB_END_REPLAY,
            TB_SLOW_REPLAY,
            TB_PAUSE_REPLAY,
            TB_CONTINUE_REPLAY,
            TB_FAST_REPLAY,
            TB_REPEAT_REPLAY,
            TB_PGN_REPLAY,
            TB_CHANGE,
        )

        self.antAcciones = self.main_window.get_toolbar()
        self.main_window.pon_toolbar(li_acciones, separator=False)

        self.manager.ponRutinaAccionDef(self.process_toolbar)

        self.muestraPausa(True, False)

        self.num_moves, self.jugInicial, self.filaInicial, self.is_white = self.manager.jugadaActual()

        self.li_moves = self.manager.game.li_moves
        self.current_position = 0 if if_start else self.jugInicial
        self.initial_position = self.current_position

        self.siStop = False

        self.show_information()

        if seconds_before > 0.0:
            move = self.li_moves[self.current_position]
            self.board.set_position(move.position_before)
            if not self.sleep_refresh(seconds_before):
                return

        self.show_current()

    def sleep_refresh(self, seconds):
        ini_time = time.time()
        while (time.time() - ini_time) < seconds:
            QTUtil.refresh_gui()
            if self.siStop:
                return False
            time.sleep(0.01)
        return True

    def show_information(self):
        if self.siPGN:
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
        if self.siStop or self.current_position >= len(self.li_moves):
            return

        move = self.li_moves[self.current_position]
        self.board.set_position(move.position_before)
        if self.current_position > self.initial_position:
            if not self.sleep_refresh(self.seconds / self.rapidez):
                return

        liMovs = [("b", move.to_sq), ("m", move.from_sq, move.to_sq)]
        if move.position.li_extras:
            liMovs.extend(move.position.li_extras)
        self.move_the_pieces(liMovs)

        self.skip()

    def move_the_pieces(self, liMovs):
        cpu = self.procesador.cpu
        cpu.reset()
        secs = None

        move = self.li_moves[self.current_position]
        num = self.current_position
        if self.starts_with_black:
            num += 1
        row = int(num / 2)
        self.main_window.pgnColocate(row, move.position_before.is_white)
        self.main_window.base.pgnRefresh()

        # primero los movimientos
        for movim in liMovs:
            if movim[0] == "m":
                from_sq, to_sq = movim[1], movim[2]
                if secs is None:
                    dc = ord(from_sq[0]) - ord(to_sq[0])
                    df = int(from_sq[1]) - int(to_sq[1])
                    # Maxima distancia = 9.9 ( 9,89... sqrt(7**2+7**2)) = 4 seconds
                    dist = (dc**2 + df**2) ** 0.5
                    rp = self.rapidez if self.rapidez > 1.0 else 1.0
                    secs = 4.0 * dist / (9.9 * rp)
                cpu.muevePieza(from_sq, to_sq, secs)
        # return
        if secs is None:
            secs = 1.0

        # segundo los borrados
        for movim in liMovs:
            if movim[0] == "b":
                cpu.borraPiezaSecs(movim[1], secs)

        # tercero los cambios
        for movim in liMovs:
            if movim[0] == "c":
                cpu.cambiaPieza(movim[1], movim[2], siExclusiva=True)

        cpu.runLineal()
        if self.if_beep:
            Code.runSound.playBeep()
        self.manager.put_arrow_sc(move.from_sq, move.to_sq)

        self.board.set_position(move.position)

        self.manager.put_view()

        # cpu.reset()
        # cpu.duerme(self.seconds / self.rapidez)
        # cpu.runLineal()

    def muestraPausa(self, si_pausa, si_continue):
        self.main_window.show_option_toolbar(TB_PAUSE_REPLAY, si_pausa)
        self.main_window.show_option_toolbar(TB_CONTINUE_REPLAY, si_continue)
        self.main_window.show_option_toolbar(TB_CHANGE, not si_pausa)

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
            self.siPGN = not self.siPGN
            self.show_information()

        elif key == TB_CHANGE:
            resp = param_replay(self.procesador.configuration, self.main_window)
            if resp is not None:
                self.seconds, self.if_start, self.siPGN, self.if_beep, seconds_before = resp

    def terminar(self):
        self.siStop = True
        self.main_window.pon_toolbar(self.antAcciones)
        self.manager.ponRutinaAccionDef(None)
        self.manager.xpelicula = None
        if self.previous_visible_capturas:
            self.main_window.siCapturas = True
        if not self.siPGN:
            self.siPGN = True
            self.show_information()

    def lento(self):
        self.rapidez /= 1.2

    def rapido(self):
        self.rapidez *= 1.2

    def pausa(self):
        self.siStop = True
        self.muestraPausa(False, True)

    def seguir(self):
        num_moves, self.current_position, filaInicial, is_white = self.manager.jugadaActual()
        self.current_position += 1
        self.siStop = False
        self.muestraPausa(True, False)
        self.show_current()

    def repetir(self):
        self.current_position = 0 if self.if_start else self.jugInicial
        self.muestraPausa(True, False)
        if self.siStop:
            self.siStop = False
            self.show_current()

    def skip(self):
        if self.siStop:
            return
        self.current_position += 1
        if self.current_position >= self.num_moves:
            self.siStop = True
            self.muestraPausa(False, False)
        else:
            self.show_current()
