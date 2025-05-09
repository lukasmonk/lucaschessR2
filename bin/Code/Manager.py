import os
import random
import time

import FasterCode
from PySide2 import QtCore

import Code
from Code import ControlPGN
from Code import TimeControl
from Code import Util
from Code import XRun
from Code import Adjournments
from Code.Analysis import Analysis, AnalysisGame, AnalysisIndexes, Histogram, WindowAnalysisGraph, AI
from Code.Analysis import WindowAnalysisConfig
from Code.Base import Game, Move, Position
from Code.Base.Constantes import (
    WHITE,
    BLACK,
    GT_ALONE,
    GT_GAME,
    GT_VARIATIONS,
    ST_ENDGAME,
    ST_PLAYING,
    GT_AGAINST_PGN,
    GT_AGAINST_GM,
    RS_WIN_PLAYER,
    RS_WIN_OPPONENT,
    RS_DRAW,
    GT_BOOK,
    GT_ELO,
    GT_MICELO,
    GT_WICKER,
    RS_UNKNOWN,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_UTILITIES,
    TB_TAKEBACK,
    TB_EBOARD,
    TB_REPLAY,
    RS_DRAW_50,
    RESULT_DRAW,
    RS_DRAW_MATERIAL,
    RS_DRAW_REPETITION,
    RS_WIN_OPPONENT_TIME,
    RS_WIN_PLAYER_TIME,
    GT_AGAINST_ENGINE,
    GO_BACK,
    GO_END,
    GO_FORWARD,
    GO_START,
    GO_BACK2,
    GO_FORWARD2,
    GT_OPENINGS,
    GT_POSITIONS,
    GT_TACTICS,
    TERMINATION_DRAW_AGREEMENT,
    DICT_GAME_TYPES,
    NO_RATING, GOOD_MOVE,
)
from Code.Board import BoardTypes
from Code.Databases import DBgames
from Code.Engines import EngineResponse
from Code.Engines import WConfEngines
from Code.ForcingMoves import ForcingMoves
from Code.Kibitzers import Kibitzers
from Code.Openings import Opening
from Code.Openings import OpeningsStd
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2, QTUtil, SelectFiles
from Code.QT import QTVarios
from Code.QT import WReplay
from Code.QT import WindowArbol
from Code.QT import WindowArbolBook
from Code.QT import WindowSavePGN


class Manager:
    def __init__(self, procesador):

        self.fen = None

        self.procesador = procesador
        self.main_window = procesador.main_window
        self.board = procesador.board
        self.board.setAcceptDropPGNs(None)
        self.configuration = procesador.configuration
        self.runSound = Code.runSound

        self.state = ST_ENDGAME  # Para que siempre este definido

        self.game_type = None
        self.hints = 99999999
        self.ayudas_iniciales = 0
        self.must_be_autosaved = False

        self.is_competitive = False

        self.resultado = RS_UNKNOWN

        self.categoria = None

        self.main_window.set_manager_active(self)

        self.game: Game.Game = Game.Game()
        self.new_game()

        self.listaOpeningsStd = OpeningsStd.ap

        self.human_is_playing = False
        self.is_engine_side_white = False

        self.pgn = ControlPGN.ControlPGN(self)

        self.xtutor = procesador.XTutor()
        self.xanalyzer = procesador.XAnalyzer()
        self.xrival = None

        self.is_analyzing = False
        self.is_analyzed_by_tutor = False

        self.resign_limit = -99999
        self.lirm_engine = []

        self.rm_rival = None  # Usado por el tutor para mostrar las intenciones del rival

        self.one_moment_please = self.procesador.one_moment_please
        self.um = None

        self.xRutinaAccionDef = None

        self.xpelicula = None

        self.main_window.adjust_size()

        self.board.do_pressed_number = self.do_pressed_number
        self.board.do_pressed_letter = self.do_pressed_letter

        self.capturasActivable = False
        self.activatable_info = False

        self.auto_rotate = None

        self.nonDistract = None

        # x Control del tutor
        #  asi sabemos si ha habido intento de analysis previo (por ejemplo el usuario
        #  mientras piensa decide activar el tutor)
        self.siIniAnalizaTutor = False

        self.continueTt = not self.configuration.x_engine_notbackground

        # Atajos raton:
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

        self.messenger = None

        self.closed = False

        self.kibitzers_manager = self.procesador.kibitzers_manager

        self.with_eboard = len(self.configuration.x_digital_board) > 0

        self.with_previous_next = False

        self.tc_white = TimeControl.TimeControl(self.main_window, self.game, WHITE)
        self.tc_black = TimeControl.TimeControl(self.main_window, self.game, BLACK)

        self.ap_ratings = None

        self.key_crash = None

    def close(self):
        if not self.closed:
            self.procesador.reset()
            if self.must_be_autosaved:
                self.autosave_now()
                self.must_be_autosaved = False
            self.closed = True

    def disable_use_eboard(self):
        if self.configuration.x_digital_board:
            self.with_eboard = False

    def refresh_pgn(self):
        self.main_window.base.pgn_refresh()

    def new_game(self):
        self.game = Game.Game()
        self.game.set_tag("Site", Code.lucas_chess)
        hoy = Util.today()
        self.game.set_tag("Date", "%d.%02d.%02d" % (hoy.year, hoy.month, hoy.day))

    def set_end_game(self, with_takeback=False):
        self.main_window.thinking(False)
        self.runSound.close()
        self.state = ST_ENDGAME
        self.disable_all()
        li_options = [TB_CLOSE]
        if hasattr(self, "reiniciar"):
            li_options.append(TB_REINIT)
        if len(self.game):
            li_options.append(TB_REPLAY)
            if with_takeback:
                li_options.append(TB_TAKEBACK)
        li_options.append(TB_CONFIG)
        li_options.append(TB_UTILITIES)

        self.set_toolbar(li_options)
        self.main_window.toolbar_enable(True)
        self.remove_hints(siQuitarAtras=not with_takeback)
        self.procesador.close_engines()

    def set_toolbar(self, li_options):
        self.main_window.pon_toolbar(li_options, with_eboard=self.with_eboard)

    def end_manager(self):
        # se llama from_sq procesador.start, antes de borrar el manager
        self.board.atajos_raton = None
        if self.nonDistract:
            self.main_window.base.tb.setVisible(True)
        if self.must_be_autosaved:
            self.autosave_now()
        self.crash_adjourn_end()

    def crash_adjourn_end(self):
        if self.key_crash:
            with Adjournments.Adjournments() as adj:
                adj.rem_crash(self.key_crash)
                self.key_crash = None

    def reset_shortcuts_mouse(self):
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

    @staticmethod
    def other_candidates(li_moves, position, li_c):
        li_player = []
        for mov in li_moves:
            if mov.mate():
                li_player.append((mov.xto(), "P#"))
            elif mov.check():
                li_player.append((mov.xto(), "P+"))
            elif mov.capture():
                li_player.append((mov.xto(), "Px"))
        oposic = position.copia()
        oposic.is_white = not position.is_white
        oposic.en_passant = ""
        si_jaque = FasterCode.ischeck()
        FasterCode.set_fen(oposic.fen())
        li_o = FasterCode.get_exmoves()
        li_rival = []
        for n, mov in enumerate(li_o):
            if not si_jaque:
                if mov.mate():
                    li_rival.append((mov.xto(), "R#"))
                elif mov.check():
                    li_rival.append((mov.xto(), "R+"))
                elif mov.capture():
                    li_player.append((mov.xto(), "Rx"))
            elif mov.capture():
                li_player.append((mov.xto(), "Rx"))

        li_c.extend(li_rival)
        li_c.extend(li_player)

    def colect_candidates(self, a1h8):
        if not hasattr(self.pgn, "move"):  # manager60 por ejemplo
            return None
        row, column = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(row, column.key)
        if move:
            position = move.position
        else:
            position = self.game.first_position

        FasterCode.set_fen(position.fen())
        li = FasterCode.get_exmoves()
        if not li:
            return None

        # Se verifica si algun movimiento puede empezar o terminar ahi
        si_origen = si_destino = False
        for mov in li:
            from_sq = mov.xfrom()
            to_sq = mov.xto()
            if a1h8 == from_sq:
                si_origen = True
                break
            if a1h8 == to_sq:
                si_destino = True
                break
        origen = destino = None
        if si_origen or si_destino:
            pieza = position.squares.get(a1h8, None)
            if pieza is None:
                destino = a1h8
            elif position.is_white:
                if pieza.isupper():
                    origen = a1h8
                else:
                    destino = a1h8
            else:
                if pieza.isupper():
                    destino = a1h8
                else:
                    origen = a1h8

        li_c = []
        for mov in li:
            a1 = mov.xfrom()
            h8 = mov.xto()
            si_o = (origen == a1) if origen else None
            si_d = (destino == h8) if destino else None

            if (si_o and si_d) or ((si_o is None) and si_d) or ((si_d is None) and si_o):
                t = (a1, h8)
                if t not in li_c:
                    li_c.append(t)

        if origen:
            li_c = [(dh[1], "C") for dh in li_c]
        else:
            li_c = [(dh[0], "C") for dh in li_c]
        self.other_candidates(li, position, li_c)
        return li_c

    def atajos_raton(self, position, a1h8):
        if a1h8 is None or not self.board.pieces_are_active:
            self.reset_shortcuts_mouse()
            return

        FasterCode.set_fen(position.fen())
        li_moves = FasterCode.get_exmoves()
        if not li_moves:
            return

        # Se verifica si algun movimiento puede empezar o terminar ahi
        li_destinos = []
        li_origenes = []
        for mov in li_moves:
            from_sq = mov.xfrom()
            to_sq = mov.xto()
            if a1h8 == from_sq:
                li_destinos.append(to_sq)
            if a1h8 == to_sq:
                li_origenes.append(from_sq)
        if not (li_destinos or li_origenes):
            self.reset_shortcuts_mouse()
            return

        def mueve():
            self.board.move_pieceTemporal(self.atajosRatonOrigen, self.atajosRatonDestino)
            if (not self.board.mensajero(self.atajosRatonOrigen, self.atajosRatonDestino)) and self.atajosRatonOrigen:
                self.board.set_piece_again(self.atajosRatonOrigen)
            self.reset_shortcuts_mouse()

        def show_candidates():
            if self.configuration.x_show_candidates:
                li_c = []
                for xmov in li_moves:
                    a1 = xmov.xfrom()
                    h8 = xmov.xto()
                    if a1 == self.atajosRatonOrigen:
                        li_c.append((h8, "C"))
                if self.state != ST_PLAYING:
                    self.other_candidates(li_moves, position, li_c)
                self.board.show_candidates(li_c)

        if self.configuration.x_mouse_shortcuts is None:
            return

        if self.configuration.x_mouse_shortcuts is not None:
            if li_destinos:
                self.atajosRatonOrigen = a1h8
                self.atajosRatonDestino = None
                # if self.atajosRatonDestino and self.atajosRatonDestino in li_destinos:
                #     mueve()
                # else:
                #     self.atajosRatonDestino = None
                show_candidates()
                return
            elif li_origenes:
                self.atajosRatonDestino = a1h8
                if self.atajosRatonOrigen and self.atajosRatonOrigen in li_origenes:
                    mueve()
                else:
                    self.atajosRatonOrigen = None
                    self.atajosRatonDestino = None
                    show_candidates()
            return

        if li_origenes:
            self.atajosRatonDestino = a1h8
            if self.atajosRatonOrigen and self.atajosRatonOrigen in li_origenes:
                mueve()
            elif len(li_origenes) == 1:
                self.atajosRatonOrigen = li_origenes[0]
                mueve()
            else:
                show_candidates()
            return

        if li_destinos:
            self.atajosRatonOrigen = a1h8
            if self.atajosRatonDestino and self.atajosRatonDestino in li_destinos:
                mueve()
            elif len(li_destinos) == 1:
                self.atajosRatonDestino = li_destinos[0]
                mueve()
            else:
                show_candidates()
            return

    def repeat_last_movement(self):
        # Manager ent tac + ent pos si hay game
        if len(self.game):
            move = self.game.last_jg()
            self.board.set_position(move.position_before)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            QTUtil.refresh_gui()
            time.sleep(0.6)
            ant = self.configuration.x_show_effects
            self.configuration.x_show_effects = True
            self.move_the_pieces(move.liMovs, True)
            self.configuration.x_show_effects = ant
            self.board.set_position(move.position)
            self.main_window.base.pgn.refresh()
            self.main_window.base.pgn.gobottom(1 if move.is_white() else 2)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            # self.goto_end()

    def move_the_pieces(self, li_moves, is_rival=False):
        self.main_window.end_think_analysis_bar()
        if is_rival and self.configuration.x_show_effects:

            rapidez = self.configuration.pieces_speed_porc()
            cpu = self.procesador.cpu
            cpu.reset()
            seconds = None

            # primero los movimientos
            for movim in li_moves:
                if movim[0] == "m":
                    if seconds is None:
                        from_sq, to_sq = movim[1], movim[2]
                        dc = ord(from_sq[0]) - ord(to_sq[0])
                        df = int(from_sq[1]) - int(to_sq[1])
                        # Maxima distancia = 9.9 ( 9,89... sqrt(7**2+7**2)) = 4 seconds
                        dist = (dc ** 2 + df ** 2) ** 0.5
                        seconds = 4.0 * dist / (9.9 * rapidez)
                    if self.procesador.manager:
                        cpu.move_piece(movim[1], movim[2], seconds)
                    else:
                        return

            if seconds is None:
                seconds = 1.0

            # segundo los borrados
            for movim in li_moves:
                if movim[0] == "b":
                    if self.procesador.manager:
                        cpu.remove_piece_insecs(movim[1], seconds)
                    else:
                        return

            # tercero los cambios
            for movim in li_moves:
                if movim[0] == "c":
                    if self.procesador.manager:
                        cpu.change_piece(movim[1], movim[2], is_exclusive=True)
                    else:
                        return

            if self.procesador.manager:
                cpu.run_lineal()

        else:
            for movim in li_moves:
                if movim[0] == "b":
                    self.board.remove_piece(movim[1])
                elif movim[0] == "m":
                    self.board.move_piece(movim[1], movim[2])
                elif movim[0] == "c":
                    self.board.change_piece(movim[1], movim[2])
        # Aprovechamos que esta operacion se hace en cada move
        self.reset_shortcuts_mouse()

    def num_rows(self):
        return self.pgn.num_rows()

    def put_view(self):
        if not hasattr(self.pgn, "move"):  # manager60 por ejemplo
            return
        row, column = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(row, column.key)
        if column.key == "NUMBER":
            if row > 0:
                pos_move, move = self.pgn.move(row-1, "BLACK")

        if self.main_window.with_analysis_bar:
            self.main_window.run_analysis_bar(self.current_game())

        if (
                self.main_window.siCapturas
                or self.main_window.siInformacionPGN
                or self.kibitzers_manager.some_working()
                or self.configuration.x_show_bestmove
                or self.configuration.x_show_rating
        ):
            if move and (self.configuration.x_show_bestmove or self.configuration.x_show_rating):
                move_check = move
                if column.key == "NUMBER":
                    if row == 0:
                        move_check = None
                if move_check:
                    if move_check.analysis and self.configuration.x_show_bestmove:
                        mrm, pos = move_check.analysis
                        if pos:  # no se muestra la mejor move si es la realizada
                            rm0 = mrm.best_rm_ordered()
                            self.board.put_arrow_scvar([(rm0.from_sq, rm0.to_sq)])

                    if self.configuration.x_show_rating:
                        self.show_rating(move_check)

            nom_opening = ""
            opening = self.game.opening
            if opening:
                nom_opening = opening.tr_name
                if opening.eco:
                    nom_opening += " (%s)" % opening.eco
            if self.main_window.siCapturas:
                if self.board.last_position is not None:
                    if Code.configuration.x_captures_mode_diferences:
                        dic = self.board.last_position.capturas_diferencia()
                    else:
                        dic = self.board.last_position.capturas()
                    self.main_window.put_captures(dic)
            if self.main_window.siInformacionPGN:
                if (row == 0 and column.key == "NUMBER") or row < 0:
                    self.main_window.put_informationPGN(self.game, None, nom_opening)
                else:
                    move_check = move
                    move_check.pos_in_game = pos_move
                    self.main_window.put_informationPGN(None, move_check, nom_opening)

            if self.kibitzers_manager.some_working():
                if self.si_check_kibitzers():
                    self.check_kibitzers(True)
                else:
                    self.kibitzers_manager.stop()
        self.check_changed()

    def show_rating(self, move_check):
        nag = move_check.get_nag()
        color = NO_RATING
        if not nag:
            if move_check.analysis:
                mrm, pos = move_check.analysis
                rm = mrm.li_rm[pos]
                nag, color = mrm.set_nag_color(rm)
        if nag == NO_RATING:
            if move_check.in_the_opening:
                nag = 1000
            elif color == GOOD_MOVE:
                nag = 999
            else:
                if move_check.is_book:
                    nag = 1001
                elif move_check.is_book is None:
                    if self.ap_ratings is None:
                        self.ap_ratings = Opening.OpeningGM()
                    move_check.is_book = self.ap_ratings.check_human(move_check.position_before.fen(),
                                                                     move_check.from_sq, move_check.to_sq)
                    if move_check.is_book:
                        nag = 1001
        poscelda = 0 if (move_check.to_sq[0] < move_check.from_sq[0]) and (
                move_check.to_sq[1] < move_check.from_sq[1]) else 1
        if nag != NO_RATING or (nag == NO_RATING and move_check.analysis):
            self.board.put_rating(move_check.from_sq, move_check.to_sq, nag, poscelda)
        if nag != 1000 and move_check.in_the_opening:
            poscelda = 1 if poscelda == 0 else 0
            self.board.put_rating(move_check.from_sq, move_check.to_sq, 1000, poscelda)

    def si_check_kibitzers(self):
        return (self.state == ST_ENDGAME) or (not self.is_competitive)

    def show_bar_kibitzers_variation(self, game_run):
        if self.kibitzers_manager.some_working():
            if self.si_check_kibitzers():
                self.kibitzers_manager.put_game(game_run, self.board.is_white_bottom, False)
        if self.main_window.with_analysis_bar:
            self.main_window.run_analysis_bar(game_run)

    def current_game(self):
        row, column = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(row, column.key)
        if pos_move is not None:
            if column.key == "NUMBER" and pos_move != -1:
                pos_move -= 1
        if pos_move is None or pos_move + 1 == len(self.game):
            return self.game
        game_run = self.game.copy_raw(pos_move)
        if move is None or move.position != self.board.last_position:
            game_run = Game.Game(self.board.last_position)
        return game_run

    def check_kibitzers(self, all_kibitzers):
        game_run = self.current_game()
        self.kibitzers_manager.put_game(game_run, self.board.is_white_bottom, not all_kibitzers)

    def put_pieces_bottom(self, is_white):
        self.board.set_side_bottom(is_white)

    def remove_hints(self, siTambienTutorAtras=True, siQuitarAtras=True):
        self.main_window.remove_hints(siTambienTutorAtras, siQuitarAtras)
        self.set_activate_tutor(False)

    def ponAyudas(self, hints, siQuitarAtras=True):
        self.main_window.ponAyudas(hints, siQuitarAtras)

    def show_button_tutor(self, ok):
        self.main_window.show_button_tutor(ok)

    def thinking(self, si_pensando):
        if self.configuration.x_cursor_thinking:
            self.main_window.thinking(si_pensando)

    def set_activate_tutor(self, si_activar):
        self.main_window.set_activate_tutor(si_activar)
        self.is_tutor_enabled = si_activar

    def change_tutor_active(self):
        self.is_tutor_enabled = not self.is_tutor_enabled
        self.set_activate_tutor(self.is_tutor_enabled)

    def disable_all(self):
        self.board.disable_all()

    def activate_side(self, is_white):
        self.board.activate_side(is_white)

    def show_side_indicator(self, yes_no):
        self.board.side_indicator_sc.setVisible(yes_no)

    def set_side_indicator(self, is_white):
        self.board.set_side_indicator(is_white)

    def set_dispatcher(self, messenger):
        self.messenger = messenger
        self.board.set_dispatcher(self.player_has_moved_base, self.atajos_raton)

    def put_arrow_sc(self, from_sq, to_sq, lipvvar=None):
        self.board.remove_arrows()
        self.board.put_arrow_sc(from_sq, to_sq)
        if lipvvar:
            self.board.put_arrow_scvar(lipvvar)

    def set_piece_again(self, posic):
        self.board.set_piece_again(posic)

    def set_label1(self, mensaje):
        return self.main_window.set_label1(mensaje)

    def set_label2(self, mensaje):
        return self.main_window.set_label2(mensaje)

    def set_label3(self, mensaje):
        return self.main_window.set_label3(mensaje)

    def remove_label3(self):
        return self.main_window.set_label3(None)

    def set_hight_label3(self, px):
        return self.main_window.set_hight_label3(px)

    def get_labels(self):
        return self.main_window.get_labels()

    def restore_labels(self, li_labels):
        lb1, lb2, lb3 = li_labels

        def pon(lb, rut):
            if lb:
                rut(lb)

        pon(lb1, self.set_label1)
        pon(lb2, self.set_label2)
        pon(lb3, self.set_label3)

    def beep_extended(self, is_player_move):
        self.main_window.end_think_analysis_bar()
        if is_player_move:
            if not self.configuration.x_sound_our:
                return
        played = False
        if self.configuration.x_sound_move:
            if len(self.game):
                move = self.game.move(-1)
                played = self.runSound.play_list(move.sounds_list())
        if not played and self.configuration.x_sound_beep:
            self.runSound.playBeep()

    def beep_zeitnot(self):
        self.runSound.play_zeinot()

    def beep_error(self):
        if self.configuration.x_sound_error:
            self.runSound.playError()

    def beep_result_change(self, resfinal):  # TOO Cambiar por beepresultado1
        if not self.configuration.x_sound_results:
            return
        dic = {
            RS_WIN_PLAYER: "GANAMOS",
            RS_WIN_OPPONENT: "GANARIVAL",
            RS_DRAW: "TABLAS",
            RS_DRAW_REPETITION: "TABLASREPETICION",
            RS_DRAW_50: "TABLAS50",
            RS_DRAW_MATERIAL: "TABLASFALTAMATERIAL",
            RS_WIN_PLAYER_TIME: "GANAMOSTIEMPO",
            RS_WIN_OPPONENT_TIME: "GANARIVALTIEMPO",
        }
        if resfinal in dic:
            self.runSound.play_key(dic[resfinal])

    def beep_result(self, xbeep_result):
        if xbeep_result:
            if not self.configuration.x_sound_results:
                return
            self.runSound.play_key(xbeep_result)

    def pgn_refresh(self, is_white):
        self.main_window.pgn_refresh(is_white)

    def refresh(self):
        self.board.escena.update()
        self.main_window.update()
        QTUtil.refresh_gui()

    def mueve_number(self, tipo):
        game = self.game
        row, column = self.main_window.pgnPosActual()

        col = 0

        starts_with_black = game.starts_with_black
        lj = len(game)
        if starts_with_black:
            lj += 1
        ult_fila = (lj - 1) // 2

        if tipo == GO_BACK:
            row -= 1
            if row < 0:
                self.goto_firstposition()
                return
            col = 1
        elif tipo == GO_BACK2:
            if row == 0:
                return
            row -= 1
        elif tipo == GO_FORWARD:
            if row == 0 and game.starts_with_black:
                return self.goto_firstposition()
            col = 1
        elif tipo == GO_FORWARD2:
            row += 1
        elif tipo == GO_START:
            self.goto_firstposition()
            return
        elif tipo == GO_END:
            row = ult_fila

        if row > ult_fila:
            return

        move: Move.Move = self.game.move(row * 2 + col)
        self.set_position(move.position_before)
        self.main_window.base.pgn.goto(row, col)
        self.refresh_pgn()  # No se puede usar pgn_refresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()
        if row > 0 or col > 0:
            move: Move.Move = self.game.move(row * 2 + col - 1)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            self.main_window.pgnColocate(row, col)
            self.pgnMueve(row, move.is_white())

    def move_according_key(self, tipo):
        game = self.game
        if not len(game):
            return
        row, column = self.main_window.pgnPosActual()

        starts_with_black = game.starts_with_black

        key = column.key
        if key == "NUMBER":
            return self.mueve_number(tipo)
        else:
            is_white = key != "BLACK"

        lj = len(game)
        if starts_with_black:
            lj += 1
        ult_fila = (lj - 1) / 2
        si_ult_blancas = lj % 2 == 1

        if tipo == GO_BACK:
            if is_white:
                row -= 1
            is_white = not is_white
            pos = row * 2
            if not is_white:
                pos += 1
            if row < 0 or (row == 0 and pos == 0 and starts_with_black):
                self.goto_firstposition()
                return
        elif tipo == GO_BACK2:
            row -= 1
        elif tipo == GO_FORWARD:
            if not is_white:
                row += 1
            is_white = not is_white
        elif tipo == GO_FORWARD2:
            row += 1
        elif tipo == GO_START:
            self.goto_firstposition()
            return
        elif tipo == GO_END:
            row = ult_fila
            is_white = not game.last_position.is_white

        if row == ult_fila:
            if si_ult_blancas and not is_white:
                return

        if row < 0 or row > ult_fila:
            self.refresh()
            return
        if row == 0 and is_white and starts_with_black:
            is_white = False

        self.main_window.pgnColocate(row, is_white)
        self.pgnMueve(row, is_white)

    def goto_firstposition(self):
        self.set_position(self.game.first_position)
        self.main_window.base.pgn.goto(0, 0)
        self.refresh_pgn()  # No se puede usar pgn_refresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

    # def ponteAlPrincipioColor(self):
    #     if self.game.li_moves:
    #         move = self.game.move(0)
    #         self.set_position(move.position)
    #         self.main_window.base.pgn.goto(0, 2 if move.position.is_white else 1)
    #         self.board.put_arrow_sc(move.from_sq, move.to_sq)
    #         self.refresh_pgn()  # No se puede usar pgn_refresh, ya que se usa con gobottom en otros lados
    #         # y aqui eso no funciona
    #         self.put_view()
    #     else:
    #         self.goto_firstposition()

    def pgnMueve(self, row, is_white):
        self.pgn.mueve(row, is_white)
        self.put_view()

    def pgnMueveBase(self, row, column):
        if column == "NUMBER":
            if row <= 0:
                if self.pgn.variations_mode:
                    self.set_position(self.game.first_position, "-1")
                    self.main_window.base.pgn.goto(0, 0)
                    self.refresh_pgn()  # No se puede usar pgn_refresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
                    self.put_view()
                else:
                    self.goto_firstposition()
                return
            else:
                row -= 1
                is_white = False
        else:
            is_white = column == "WHITE"
        self.pgn.mueve(row, is_white)
        self.put_view()

    def goto_end(self):
        if len(self.game):
            self.move_according_key(GO_END)
        else:
            self.set_position(self.game.first_position)
            self.refresh_pgn()  # No se puede usar pgn_refresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

    def goto_current(self):
        num_moves, nj, row, is_white = self.jugadaActual()
        self.pgnMueve(row, is_white)

    def jugadaActual(self):
        game = self.game
        row, column = self.main_window.pgnPosActual()
        is_white = column.key != "BLACK"
        starts_with_black = game.starts_with_black

        num_moves = len(game)
        if num_moves == 0:
            return 0, -1, -1, game.first_position.is_white
        nj = row * 2
        if not is_white:
            nj += 1
        if starts_with_black:
            nj -= 1
        return num_moves, nj, row, is_white

    def current_move_number(self):
        game = self.game
        row, column = self.main_window.pgnPosActual()
        if column.key == "WHITE":
            is_white = True
        elif column.key == "BLACK":
            is_white = False
        else:
            if row > 0:
                is_white = False
                row -= 1
            else:
                is_white = True
        # is_white = column.key != "BLACK"
        starts_with_black = game.starts_with_black

        num_moves = len(game)
        if num_moves == 0:
            return 0, -1, -1, game.first_position.is_white
        nj = row * 2
        if not is_white:
            nj += 1
        if starts_with_black:
            nj -= 1
        return num_moves, nj, row, is_white

    def in_end_of_line(self):
        num_moves, nj, row, is_white = self.jugadaActual()
        return nj == num_moves - 1

    def pgnInformacion(self):
        if self.activatable_info:
            self.main_window.activaInformacionPGN()
            self.put_view()
            self.refresh()

    def remove_info(self, is_activatable=False):
        self.main_window.activaInformacionPGN(False)
        self.activatable_info = is_activatable

    def autosave(self):
        self.must_be_autosaved = True
        if len(self.game) > 1:
            self.game.tag_timeend()
            self.game.set_extend_tags()
            if self.ayudas_iniciales > 0:
                if self.hints is not None:
                    usado = self.ayudas_iniciales - self.hints
                    if usado:
                        self.game.set_tag("HintsUsed", str(usado))

    def autosave_now(self):
        if len(self.game) > 1:
            if self.game.has_analisis():
                self.game.add_accuracy_tags()
            DBgames.autosave(self.game)
            self.must_be_autosaved = False

    def show_info_extra(self):
        key = "SHOW_INFO_EXTRA_" + DICT_GAME_TYPES[self.game_type]
        dic = self.configuration.read_variables(key)

        captured_material = dic.get("CAPTURED_MATERIAL")
        if captured_material is None:  # importante preguntarlo aquí, no vale pillarlo en el get
            captured_material = self.configuration.x_captures_activate
        self.main_window.activaCapturas(captured_material)

        pgn_information = dic.get("PGN_INFORMATION")
        if pgn_information is None:
            pgn_information = self.configuration.x_info_activate
        self.main_window.activaInformacionPGN(pgn_information)

        analysis_bar = dic.get("ANALYSIS_BAR")
        if analysis_bar is None:
            analysis_bar = self.configuration.x_analyzer_activate_ab
        self.main_window.activate_analysis_bar(analysis_bar)

        self.put_view()

    def change_info_extra(self, who):
        key = "SHOW_INFO_EXTRA_" + DICT_GAME_TYPES[self.game_type]
        dic = self.configuration.read_variables(key)

        if who == "pgn_information":
            pgn_information = not self.main_window.is_active_information_pgn()
            if pgn_information == self.configuration.x_info_activate:  # cuando es igual que el por defecto general,
                # se aplicará el general, por lo que si se cambia el general se cambiarán los que tengan None
                pgn_information = None
            dic["PGN_INFORMATION"] = pgn_information

        elif who == "captured_material":
            captured_material = not self.main_window.is_active_captures()
            if captured_material == self.configuration.x_captures_activate:
                captured_material = None
            dic["CAPTURED_MATERIAL"] = captured_material

        elif who == "analysis_bar":
            analysis_bar = not self.main_window.is_active_analysisbar()
            if analysis_bar == self.configuration.x_analyzer_activate_ab:
                analysis_bar = None
            dic["ANALYSIS_BAR"] = analysis_bar

        self.configuration.write_variables(key, dic)

        self.show_info_extra()
        self.put_view()

    def capturas(self):
        if self.capturasActivable:
            self.main_window.activaCapturas()
            self.put_view()

    def quitaCapturas(self):
        self.main_window.activaCapturas(False)
        self.put_view()

    def nonDistractMode(self):
        self.nonDistract = self.main_window.base.nonDistractMode(self.nonDistract)
        self.main_window.adjust_size()

    def boardRightMouse(self, is_shift, is_control, is_alt):
        self.board.lanzaDirector()

    def gridRightMouse(self, is_shift, is_control, is_alt):
        if is_alt:
            self.arbol()
        else:
            menu = QTVarios.LCMenu12(self.main_window)
            self.add_menu_vista(menu)
            resp = menu.lanza()
            if resp:
                self.exec_menu_vista(resp)

    def listado(self, tipo):
        if tipo == "pgn":
            return self.pgn.actual()
        elif tipo == "fen":
            return self.fenActivoConInicio()

    def jugadaActiva(self):
        row, column = self.main_window.pgnPosActual()
        is_white = column.key != "BLACK"
        pos = row * 2
        if not is_white:
            pos += 1
        if self.game.starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        si_ultimo = (pos + 1) >= tam_lj
        if si_ultimo:
            pos = tam_lj - 1
        return pos, self.game.move(pos) if tam_lj else None

    def fenActivo(self):
        pos, move = self.jugadaActiva()
        return move.position.fen() if move else self.last_fen()

    def fenActivoConInicio(self):
        pos, move = self.jugadaActiva()
        if pos == 0:
            row, column = self.main_window.pgnPosActual()
            if column.key == "NUMBER":
                return self.game.first_position.fen()
        return move.position.fen() if move else self.last_fen()

    def last_fen(self):
        return self.game.last_fen()

    def fenPrevio(self):
        row, column = self.main_window.pgnPosActual()
        is_white = column.key != "BLACK"
        pos = row * 2
        if not is_white:
            pos += 1
        if self.game.starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        if 0 <= pos < tam_lj:
            return self.game.move(pos).position_before.fen()
        else:
            return self.game.first_position.fen()

    def analizaTutor(self, with_cursor=False):
        if with_cursor:
            self.main_window.pensando_tutor(True)
        self.thinking(True)
        fen = self.game.last_position.fen()
        if not self.is_finished():
            self.mrm_tutor = self.xtutor.analiza(fen)
        else:
            self.mrm_tutor = None
        self.thinking(False)
        if with_cursor:
            self.main_window.pensando_tutor(False)
        return self.mrm_tutor

    def conf_engines(self):
        w = WConfEngines.WConfEngines(self.main_window)
        w.exec_()
        self.procesador.cambiaXTutor()
        self.procesador.cambiaXAnalyzer()
        self.xtutor = self.procesador.xtutor
        self.set_label2(_("Tutor") + ": <b>" + self.xtutor.name)
        self.is_analyzed_by_tutor = False

        self.procesador.cambiaXAnalyzer()
        self.xanalyzer = self.procesador.xanalyzer

        if self.game_type == GT_AGAINST_ENGINE:
            getattr(self, "analyze_begin")()

    def is_finished(self):
        return self.game.is_finished()

    def dameJugadaEn(self, row, key):
        is_white = key != "BLACK"

        pos = row * 2
        if not is_white:
            pos += 1
        if self.game.starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        if tam_lj == 0:
            return
        si_ultimo = (pos + 1) >= tam_lj

        move = self.game.move(pos)
        return move, is_white, si_ultimo, tam_lj, pos

    def analize_after_last_move(self):
        si_cancelar = self.xanalyzer.mstime_engine > 2000 or self.xanalyzer.depth_engine > 8
        mens = _("Analyzing the move....")
        self.main_window.base.show_message(mens, si_cancelar, tit_cancel=_("Stop thinking"))
        self.main_window.base.tb.setDisabled(True)
        if si_cancelar:
            ya_cancelado = [False]
            tm_ini = time.time()

            def test_me(rm):
                if self.main_window.base.is_canceled():
                    if not ya_cancelado[0]:
                        self.xanalyzer.stop()
                        ya_cancelado[0] = True
                else:
                    tm = time.time() - tm_ini
                    self.main_window.base.change_message(
                        '%s<br><small>%s: %d %s: %.01f"' % (mens, _("Depth"), rm.depth, _("Time"), rm.time / 1000)
                    )
                    if self.xanalyzer.mstime_engine and tm * 1000 > self.xanalyzer.mstime_engine:
                        self.xanalyzer.stop()
                        ya_cancelado[0] = True
                return True

            self.xanalyzer.set_gui_dispatch(test_me)

        mrm = self.xanalyzer.play_game_raw(self.game)
        self.xanalyzer.set_gui_dispatch(None)
        self.main_window.base.tb.setDisabled(False)
        self.main_window.base.hide_message()
        return mrm

    def analize_position(self, row, key):
        if row < 0:
            return

        move, is_white, si_ultimo, tam_lj, pos_jg = self.dameJugadaEn(row, key)
        if not move:
            return
        if self.state != ST_ENDGAME:
            if not (
                    self.game_type
                    in [
                        GT_POSITIONS,
                        GT_AGAINST_PGN,
                        GT_AGAINST_ENGINE,
                        GT_AGAINST_GM,
                        GT_ALONE,
                        GT_GAME,
                        GT_VARIATIONS,
                        GT_BOOK,
                        GT_OPENINGS,
                        GT_TACTICS,
                    ]
                    or (self.game_type in [GT_ELO, GT_MICELO, GT_WICKER] and not self.is_competitive)
            ):
                if si_ultimo or self.hints == 0:
                    return
        if move.analysis is None:
            si_cancelar = self.xanalyzer.mstime_engine > 1000 or self.xanalyzer.depth_engine > 8
            mens = _("Analyzing the move....")
            self.main_window.base.show_message(mens, si_cancelar, tit_cancel=_("Stop thinking"))
            self.main_window.base.tb.setDisabled(True)
            if si_cancelar:
                ya_cancelado = [False]
                tm_ini = time.time()

                def test_me(rm):
                    if self.main_window.base.is_canceled():
                        if not ya_cancelado[0]:
                            self.xanalyzer.stop()
                            ya_cancelado[0] = True
                    else:
                        tm = time.time() - tm_ini
                        self.main_window.base.change_message(
                            '%s<br><small>%s: %d %s: %.01f"' % (mens, _("Depth"), rm.depth, _("Time"), rm.time / 1000)
                        )
                        if self.xanalyzer.mstime_engine and tm * 1000 > self.xanalyzer.mstime_engine:
                            self.xanalyzer.stop()
                            ya_cancelado[0] = True
                    return True

                self.xanalyzer.set_gui_dispatch(test_me)
            mrm, pos = self.xanalyzer.analyzes_move_game(
                self.game, pos_jg, self.xanalyzer.mstime_engine, self.xanalyzer.depth_engine
            )
            self.xanalyzer.set_gui_dispatch(None)
            move.analysis = mrm, pos
            move.refresh_nags()
            self.main_window.base.tb.setDisabled(False)
            self.main_window.base.hide_message()

        Analysis.show_analysis(self.procesador, self.xanalyzer, move, self.board.is_white_bottom, pos_jg)
        self.put_view()
        self.check_changed()

    def analizar(self):
        if Code.eboard and Code.eboard.driver:
            self.rutinaAccionDef(TB_EBOARD)
        self.main_window.base.tb.setDisabled(True)
        self.is_analyzing = True
        AnalysisGame.analysis_game(self)
        self.is_analyzing = False
        self.main_window.base.tb.setDisabled(False)
        self.refresh()
        self.check_changed()

    def check_changed(self):
        pass

    def borrar(self):
        form = FormLayout.FormLayout(self.main_window, _("Remove"), Iconos.Delete(), anchoMinimo=300)
        form.apart_np(_("Information"))
        form.checkbox(_("All"), False)
        form.separador()
        form.checkbox(_("Variations"), False)
        form.checkbox(_("Ratings") + " (NAGs)", False)
        form.checkbox(_("Comments"), False)
        form.checkbox(_("Analysis"), False)
        form.checkbox(_("Themes"), False)
        form.checkbox(_("Time used") + " (%emt)", False)
        form.checkbox(_("Pending time") + " (%clk)", False)
        form.separador()

        num_moves, nj, row, is_white = self.jugadaActual()
        with_moves = num_moves > 0 and self.can_be_analysed()
        if with_moves:
            form.apart_np(_("Movements"))
            form.checkbox(_("From the beginning to the active position"), False)
            form.checkbox(_("From the active position to the end"), False)
            form.separador()
        resultado = form.run()
        if resultado:
            is_all, variations, ratings, comments, analysis, themes, time_ms, clock_ms = resultado[1][:8]
            if is_all:
                variations = ratings = comments = analysis = themes = time_ms = clock_ms = True
            self.game.remove_info_moves(variations, ratings, comments, analysis, themes, time_ms, clock_ms)
            if with_moves:
                beginning, ending = resultado[1][8:]
                if beginning:
                    self.game.remove_moves(nj, False)
                    self.goto_firstposition()
                elif ending:
                    self.game.remove_moves(nj, True)
                    self.goto_end()
            self.put_view()
            self.refresh_pgn()
            self.refresh()
            self.check_changed()

    def replay(self):
        if not WReplay.param_replay(self.configuration, self.main_window, self.with_previous_next):
            return

        if self.with_previous_next:
            dic_var = WReplay.read_params()
            if dic_var["REPLAY_CONTINUOUS"]:
                getattr(self, "replay_continuous")()
                return

        self.xpelicula = WReplay.Replay(self)

    def replay_direct(self):
        self.xpelicula = WReplay.Replay(self)

    def ponRutinaAccionDef(self, rutina):
        self.xRutinaAccionDef = rutina

    def rutinaAccionDef(self, key):
        if key == TB_EBOARD:
            if Code.eboard and self.with_eboard:
                if Code.eboard.is_working():
                    return
                Code.eboard.set_working()
                if Code.eboard.driver:
                    self.main_window.deactivate_eboard(50)

                else:
                    if Code.eboard.activate(self.board.dispatch_eboard):
                        Code.eboard.set_position(self.board.last_position)

                self.main_window.set_title_toolbar_eboard()
                QTUtil.refresh_gui()

        elif self.xRutinaAccionDef:
            self.xRutinaAccionDef(key)

        elif key == TB_CLOSE:
            self.close()

        elif key == TB_REPLAY:
            self.replay_direct()

        else:
            self.procesador.run_action(key)

    def final_x0(self):
        # Se llama from_sq la main_window al pulsar X
        # Se verifica si estamos en la replay
        if self.xpelicula:
            self.xpelicula.terminar()
            return False
        if self.is_analyzing:
            self.main_window.base.check_is_hide()
        return getattr(self, "final_x")()

    def do_pressed_number(self, si_activar, number):
        if number in [1, 8]:
            if si_activar:
                # Que move esta en el board
                fen = self.board.fen_active() #fenActivoConInicio()
                is_white = " w " in fen
                if number == 1:
                    si_mb = is_white
                else:
                    si_mb = not is_white
                self.board.remove_arrows()
                if self.board.arrow_sc:
                    self.board.arrow_sc.hide()
                li = FasterCode.get_captures(fen, si_mb)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.board.show_arrow_mov(d, h, "c")
            else:
                num_moves, nj, row, is_white = self.current_move_number()
                if nj < 0:
                    return
                move = self.game.move(nj)
                self.board.set_position(move.position)
                self.board.remove_arrows()
                self.board.put_arrow_sc(move.from_sq, move.to_sq)
                if Code.configuration.x_show_bestmove:
                    move = self.game.move(nj)
                    mrm: EngineResponse.MultiEngineResponse
                    mrm, pos = move.analysis
                    if not move.analysis:
                        return
                    rm0 = mrm.best_rm_ordered()
                    self.board.put_arrow_scvar([(rm0.from_sq, rm0.to_sq)])

        elif number in [2, 7]:
            if si_activar:
                # Que move esta en el board
                fen = self.board.fen_active() #fenActivoConInicio()
                is_white = " w " in fen
                if number == 2:
                    si_mb = is_white
                else:
                    si_mb = not is_white
                if si_mb != is_white:
                    fen = FasterCode.fen_other(fen)
                cp = Position.Position()
                cp.read_fen(fen)
                li_movs = cp.aura()

                self.liMarcosTmp = []
                reg_marco = BoardTypes.Marco()
                color = self.board.config_board.flechaActivoDefecto().colorinterior
                if color == -1:
                    color = self.board.config_board.flechaActivoDefecto().color

                st = set()
                for h8 in li_movs:
                    if h8 not in st:
                        reg_marco.a1h8 = h8 + h8
                        reg_marco.siMovible = True
                        reg_marco.color = color
                        reg_marco.colorinterior = color
                        reg_marco.opacity = 0.5
                        box = self.board.creaMarco(reg_marco)
                        self.liMarcosTmp.append(box)
                        st.add(h8)

            else:
                for box in self.liMarcosTmp:
                    self.board.xremove_item(box)
                self.liMarcosTmp = []

    def do_pressed_letter(self, si_activar, letra):
        num_moves, nj, row, is_white = self.current_move_number()
        if not (num_moves and num_moves > nj):
            return
        move = self.game.move(nj)
        if not move.analysis:
            return
        mrm: EngineResponse.MultiEngineResponse
        mrm, pos = move.analysis

        if si_activar:
            self.board.remove_arrows()
            if self.board.arrow_sc:
                self.board.arrow_sc.hide()
            self.board.set_position(move.position_before)

            def show(xpos):
                if xpos >= len(mrm.li_rm):
                    return
                rm: EngineResponse.EngineResponse = mrm.li_rm[xpos]
                li_pv = rm.pv.split(" ")
                for side in range(2):
                    base = "s" if side == 0 else "t"
                    alt = "m" + base
                    opacity = 0.8
                    li = [li_pv[x] for x in range(len(li_pv)) if x % 2 == side]
                    for pv in li:
                        self.board.show_arrow_mov(pv[:2], pv[2:4], alt, opacity=opacity)
                        opacity = max(opacity / 1.4, 0.3)

            if letra == "a":
                show(pos)
            else:
                show(ord(letra) - ord("b"))

        else:
            self.board.set_position(move.position)
            self.board.remove_arrows()
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            if Code.configuration.x_show_bestmove:
                rm0 = mrm.best_rm_ordered()
                self.board.put_arrow_scvar([(rm0.from_sq, rm0.to_sq)])

    def kibitzers(self, orden):
        if orden == "edit":
            self.kibitzers_manager.edit()
        else:
            huella = orden
            self.kibitzers_manager.run_new(huella)
            self.check_kibitzers(False)

    def stop_human(self):
        self.human_is_playing = False
        self.disable_all()

    def continue_human(self):
        self.human_is_playing = True
        self.check_boards_setposition()
        self.activate_side(self.game.last_position.is_white)
        QTUtil.refresh_gui()

    def check_human_move(self, from_sq, to_sq, promotion, with_premove=False):
        if self.human_is_playing:
            if not with_premove:
                self.stop_human()
        else:
            self.continue_human()
            return None

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.game.last_position.pawn_can_promote(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.game.last_position.is_white)
            if promotion is None:
                self.continue_human()
                return None
        if promotion:
            movimiento += promotion

        ok, self.error, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            return move
        else:
            self.continue_human()
            return None

    def librosConsulta(self, on_live):
        w = WindowArbolBook.WindowArbolBook(self, on_live)
        if w.exec_():
            return w.resultado
        else:
            return None

    def set_position(self, position, variation_history=None):
        self.board.set_position(position, variation_history=variation_history)

    def check_boards_setposition(self):
        self.board.set_raw_last_position(self.game.last_position)

    def control1(self):
        if self.active_play_instead_of_me():
            if hasattr(self, "play_instead_of_me"):
                getattr(self, "play_instead_of_me")()

    def control2(self):
        if self.active_help_to_move():
            if hasattr(self, "help_to_move"):
                getattr(self, "help_to_move")()

    def can_be_analysed(self):
        return (len(self.game) > 0
                and not (self.game_type in (GT_ELO, GT_MICELO, GT_WICKER)
                         and self.is_competitive and self.state == ST_PLAYING))

    def alt_a(self):
        if self.can_be_analysed():
            self.analizar()

    def active_play_instead_of_me(self):
        if self.is_competitive and not self.game.is_finished():
            return False
        return True

    def play_instead_of_me(self):
        rm = self.bestmove_from_analysis_bar()
        if rm is None:
            self.main_window.pensando_tutor(True)
            self.thinking(True)
            cp = self.current_position()
            mrm_tutor = self.xtutor.analiza(cp.fen())
            self.thinking(False)
            self.main_window.pensando_tutor(False)
            rm = mrm_tutor.best_rm_ordered()
        if rm.from_sq:
            self.player_has_moved_base(rm.from_sq, rm.to_sq, rm.promotion)

    @staticmethod
    def active_help_to_move():
        return True

    def add_menu_vista(self, menu_vista):
        menu_vista.opcion("vista_pgn_information", _("PGN information"),
                          is_ckecked=self.main_window.is_active_information_pgn())
        menu_vista.separador()
        menu_vista.opcion("vista_captured_material", _("Captured material"),
                          is_ckecked=self.main_window.is_active_captures())
        menu_vista.separador()
        menu_vista.opcion(
            "vista_analysis_bar",
            _("Analysis Bar"),
            is_ckecked=self.main_window.is_active_analysisbar(),
        )
        menu_vista.separador()
        menu_vista.opcion(
            "vista_bestmove",
            _("Arrow with the best move when there is an analysis"),
            is_ckecked=self.configuration.x_show_bestmove,
        )
        menu_vista.separador()
        menu_vista.opcion(
            "vista_rating",
            _("Ratings") + " (NAGs)",
            is_ckecked=self.configuration.x_show_rating,
        )

    def exec_menu_vista(self, resp):
        resp = resp[6:]
        if resp == "bestmove":
            self.configuration.x_show_bestmove = not self.configuration.x_show_bestmove
            self.configuration.graba()
            self.put_view()
        elif resp == "rating":
            self.configuration.x_show_rating = not self.configuration.x_show_rating
            self.configuration.graba()
            self.put_view()
        else:
            self.change_info_extra(resp)

    def configurar(self, li_extra_options=None, with_sounds=False, with_blinfold=True):
        menu = QTVarios.LCMenu(self.main_window)

        menu_vista = menu.submenu(_("Show/hide"), Iconos.Vista())
        self.add_menu_vista(menu_vista)
        menu.separador()

        if with_blinfold:
            menu_cg = menu.submenu(_("Blindfold chess"), Iconos.Ojo())

            si = self.board.blindfold
            if si:
                ico = Iconos.Naranja()
                tit = _("Disable")
            else:
                ico = Iconos.Verde()
                tit = _("Enable")
            menu_cg.opcion("cg_change", tit, ico, shortcut="Alt+Y")
            menu_cg.separador()
            menu_cg.opcion("cg_conf", _("Configuration"), Iconos.Opciones(), shortcut="CTRL+Y")
            menu_cg.separador()
            menu_cg.opcion("cg_pgn", "%s: %s" % (_("PGN"), _("Hide") if self.pgn.must_show else _("Show")),
                           Iconos.PGN())

        # Sonidos
        if with_sounds:
            menu.separador()
            menu.opcion("sonido", _("Sounds"), Iconos.S_Play())

        menu.separador()
        menu.opcion("engines", _("Engines configuration"), Iconos.ConfEngines())

        # On top
        menu.separador()
        label = _("Disable") if self.main_window.onTop else _("Enable")
        menu.opcion(
            "ontop", "%s: %s" % (label, _("window on top")), Iconos.Unpin() if self.main_window.onTop else Iconos.Pin()
        )

        # Right mouse
        menu.separador()
        label = _("Disable") if self.configuration.x_direct_graphics else _("Enable")
        menu.opcion(
            "mouseGraphics", "%s: %s" % (label, _("Live graphics with the right mouse button")), Iconos.RightMouse()
        )

        # Logs of engines
        menu.separador()
        is_engines_log_active = Code.list_engine_managers.is_logs_active()
        label = _("Save engines log")
        if is_engines_log_active:
            icono = Iconos.LogActive()
            label += " ...%s" % _("Working...")
            key = "log_close"
        else:
            icono = Iconos.LogInactive()
            key = "log_open"
        menu.opcion(key, label, icono)
        menu.separador()

        menu.opcion("analysis_config", _("Analysis configuration parameters"), Iconos.ConfAnalysis())

        # auto_rotate
        if self.auto_rotate is not None:
            menu.separador()
            prefix = _("Disable") if self.auto_rotate else _("Enable")
            menu.opcion("auto_rotate", "%s: %s" % (prefix, _("Auto-rotate board")), Iconos.JS_Rotacion())

        # Mas Opciones
        if li_extra_options:
            menu.separador()
            for key, label, icono in li_extra_options:
                if label is None:
                    menu.separador()
                else:
                    menu.opcion(key, label, icono)

        resp = menu.lanza()
        if resp:

            if li_extra_options:
                for key, label, icono in li_extra_options:
                    if resp == key:
                        return resp

            if resp == "log_open":
                Code.list_engine_managers.active_logs(True)

            elif resp == "log_close":
                Code.list_engine_managers.active_logs(False)

            elif resp.startswith("vista_"):
                self.exec_menu_vista(resp)

            elif resp == "sonido":
                self.config_sonido()

            elif resp == "engines":
                self.conf_engines()

            elif resp == "ontop":
                self.main_window.onTopWindow()

            elif resp == "mouseGraphics":
                self.configuration.x_direct_graphics = not self.configuration.x_direct_graphics
                self.configuration.graba()

            elif resp.startswith("cg_"):
                orden = resp[3:]
                if orden == "pgn":
                    self.pgn.must_show = not self.pgn.must_show
                    self.refresh_pgn()
                elif orden == "change":
                    self.board.blindfoldChange()

                elif orden == "conf":
                    self.board.blindfoldConfig()

            elif resp == "analysis_config":
                self.config_analysis_parameters()

            elif resp == "auto_rotate":
                self.change_auto_rotate()

        return None

    def change_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate
        self.configuration.set_auto_rotate(self.game_type, self.auto_rotate)
        is_white = self.game.last_position.is_white
        if self.auto_rotate:
            if is_white != self.board.is_white_bottom:
                self.board.rotate_board()

    def get_auto_rotate(self):
        return Code.configuration.get_auto_rotate(self.game_type)

    def config_analysis_parameters(self):
        w = WindowAnalysisConfig.WConfAnalysis(self.main_window, self)
        w.show()

    def refresh_analysis(self):
        if not self.game:
            return

        for move in self.game.li_moves:
            move.refresh_nags()

        self.main_window.base.pgn.refresh()
        self.refresh()

    def config_sonido(self):
        form = FormLayout.FormLayout(self.main_window, _("Configuration"), Iconos.S_Play(), anchoMinimo=440)
        form.separador()
        form.apart(_("After each opponent move"))
        form.checkbox(_("Sound a beep"), self.configuration.x_sound_beep)
        form.checkbox(_("Play customised sounds"), self.configuration.x_sound_move)
        form.separador()
        form.checkbox(_("The same for player moves"), self.configuration.x_sound_our)
        form.separador()
        form.separador()
        form.apart(_("When finishing the game"))
        form.checkbox(_("Play customised sounds for the result"), self.configuration.x_sound_results)
        form.separador()
        form.separador()
        form.apart(_("Others"))
        form.checkbox(_("Play a beep when there is an error in tactic trainings"), self.configuration.x_sound_error)
        form.separador()
        form.add_tab(_("Sounds"))
        resultado = form.run()
        if resultado:
            (
                self.configuration.x_sound_beep,
                self.configuration.x_sound_move,
                self.configuration.x_sound_our,
                self.configuration.x_sound_results,
                self.configuration.x_sound_error,
            ) = resultado[1][0]
            self.configuration.graba()

    def utilities(self, li_extra_options=None, with_tree=True):
        menu = QTVarios.LCMenu(self.main_window)

        si_jugadas = len(self.game) > 0

        # Grabar
        ico_grabar = Iconos.Grabar()
        ico_fichero = Iconos.GrabarFichero()
        ico_camara = Iconos.Camara()
        ico_clip = Iconos.Clipboard()

        tr_fichero = _("Save to a file")
        tr_portapapeles = _("Copy to clipboard")

        menu_save = menu.submenu(_("Save"), ico_grabar)

        key_ctrl = "Ctrl" if self.configuration.x_copy_ctrl else "Alt"
        menu_pgn = menu_save.submenu(_("PGN Format"), Iconos.PGN())
        menu_pgn.opcion("pgnfile", tr_fichero, Iconos.GrabarFichero())
        menu_pgn.separador()
        menu_pgn.opcion("pgnclipboard", tr_portapapeles, ico_clip, shortcut=f"{key_ctrl}+Shift+C")
        menu_save.separador()

        menu_fen = menu_save.submenu(_("FEN Format"), Iconos.Naranja())
        menu_fen.opcion("fenfile", tr_fichero, ico_fichero)
        menu_fen.separador()
        menu_fen.opcion("fenclipboard", tr_portapapeles, ico_clip, shortcut=f'{key_ctrl}+C')

        menu_save.separador()

        menu_save.opcion("lcsbfichero", "%s -> %s" % (_("lcsb Format"), _("Create your own game")), Iconos.JuegaSolo())

        menu_save.separador()

        menu_save_db = menu_save.submenu(_("To a database"), Iconos.DatabaseMas())
        QTVarios.menuDB(menu_save_db, self.configuration, True, indicador_previo="dbf_")  # , remove_autosave=True)
        menu_save.separador()

        menu_save_image = menu_save.submenu(_("Board -> Image"), ico_camara)
        menu_save_image.opcion("volfichero", tr_fichero, ico_fichero)
        menu_save_image.opcion("volportapapeles", tr_portapapeles, ico_clip)

        if len(self.game) > 1:
            menu_save.separador()
            menu_save.opcion("gif", _("As GIF file"), Iconos.GIF())

        menu.separador()

        # Kibitzers
        if self.si_check_kibitzers():
            menu.separador()
            menu_kibitzers = menu.submenu(_("Kibitzers"), Iconos.Kibitzer())

            kibitzers = Kibitzers.Kibitzers()
            for huella, name, ico in kibitzers.lista_menu():
                menu_kibitzers.opcion("kibitzer_%s" % huella, name, ico)
            menu_kibitzers.separador()
            menu_kibitzers.opcion("kibitzer_edit", _("Maintenance"), Iconos.ModificarP())

        # Analizar
        if self.can_be_analysed():
            menu.separador()

            submenu = menu.submenu(_("Analysis"), Iconos.Analizar())

            has_analysis = self.game.has_analisis()
            submenu.opcion("analizar", _("Analyze"), Iconos.Analizar(), shortcut="Alt+A")
            if has_analysis:
                submenu.separador()
                submenu.opcion("analizar_grafico", _("Show graphics"), Iconos.Estadisticas())
            submenu.separador()

            AI.add_submenu(submenu)

        if si_jugadas:
            menu.separador()
            menu.opcion("borrar", _("Remove"), Iconos.Delete())
            menu.separador()

        # Pelicula
        if si_jugadas:
            menu.opcion("replay", _("Replay game"), Iconos.Pelicula())
            menu.separador()

        # Juega por mi + help to move
        if self.active_play_instead_of_me():
            if hasattr(self, "play_instead_of_me"):
                menu.separador()
                menu.opcion("play_instead_of_me", _("Play instead of me"), Iconos.JuegaPorMi(), shortcut='Ctrl+1')

        if self.active_help_to_move():
            if hasattr(self, "help_to_move"):
                menu.separador()
                menu.opcion("help_to_move", _("Help to move"), Iconos.BotonAyuda(), shortcut='Ctrl+2')

        # Arbol de movimientos
        if with_tree:
            menu.separador()
            menu.opcion("arbol", _("Moves tree"), Iconos.Arbol(), shortcut='Alt+M')

        menu.separador()
        menu.opcion("play", _("Play current position"), Iconos.MoverJugar(), shortcut='Alt+X')

        # Hints
        menu.separador()
        menu.opcion("forcing_moves", _("Find forcing moves"), Iconos.Thinking())

        # Learn this game
        if len(self.game) > 0:
            menu.separador()
            menu.opcion("learn_mem", _("Learn") + " - " + _("Memorizing their moves"), Iconos.LearnGame())

        # Mas Opciones
        if li_extra_options:
            menu.separador()
            submenu = menu
            for data in li_extra_options:
                if len(data) == 3:
                    key, label, icono = data
                    shortcut = ""
                elif len(data) == 4:
                    key, label, icono, shortcut = data
                else:
                    key, label, icono, shortcut = None, None, None, None

                if label is None:
                    if icono is None:
                        submenu.separador()
                    else:
                        submenu = menu
                elif key is None:
                    submenu = menu.submenu(label, icono)

                else:
                    submenu.opcion(key, label, icono, shortcut=shortcut)
            menu.separador()

        resp = menu.lanza()

        if not resp:
            return None

        if li_extra_options:
            for data in li_extra_options:
                key = data[0]
                if resp == key:
                    return resp

        if resp == "play_instead_of_me":
            getattr(self, "play_instead_of_me")()
            return None

        elif resp == "analizar":
            self.analizar()
            return None

        elif resp == "analizar_grafico":
            self.show_analysis()
            return None

        elif resp == "borrar":
            self.borrar()
            return None

        elif resp == "replay":
            self.replay()
            return None

        elif resp == "play":
            self.play_current_position()
            return None

        elif resp.startswith("kibitzer_"):
            self.kibitzers(resp[9:])
            return None

        elif resp == "arbol":
            self.arbol()
            return None

        elif resp.startswith("vol"):
            accion = resp[3:]
            if accion == "fichero":
                resp = SelectFiles.salvaFichero(
                    self.main_window, _("File to save"), self.configuration.save_folder(), "png", False
                )
                if resp:
                    self.board.save_as_img(resp, "png")
                    return None
                return None

            else:
                self.board.save_as_img()
                return None

        elif resp == "gif":
            self.save_gif()
            return None

        elif resp == "lcsbfichero":
            self.game.set_extend_tags()
            self.save_lcsb()
            return None

        elif resp == "pgnfile":
            self.game.set_extend_tags()
            self.save_pgn()
            return None

        elif resp == "pgnclipboard":
            self.game.set_extend_tags()
            self.save_pgn_clipboard()
            return None

        elif resp.startswith("dbf_"):
            self.game.set_extend_tags()
            self.save_db(resp[4:])
            return None

        elif resp.startswith("fen"):
            si_fichero = resp.endswith("file")
            self.save_fen(si_fichero)
            return None

        elif resp == "forcing_moves":
            self.forcing_moves()
            return None

        elif resp == "learn_mem":
            self.procesador.learn_game(self.game)
            return None

        elif resp == "help_to_move":
            getattr(self, "help_to_move")()
            return None

        elif resp.startswith("ai_"):
            AI.run_menu(self.main_window, resp, self.game)
            return None
        return None

    def save_gif(self):
        from Code.QT import WGif
        w = WGif.WGif(self.main_window, self.game)
        w.exec_()

    def forcing_moves(self):
        fen = self.board.last_position.fen()
        num_moves, nj, row, is_white = self.jugadaActual()
        if num_moves and num_moves > (nj + 1):
            move = self.game.move(nj + 1)
            fen = self.board.last_position.fen()
            if move.analysis:
                mrm, pos = move.analysis
                forcing_moves = ForcingMoves.ForcingMoves(self.board, mrm, self.main_window)
                forcing_moves.fm_show_checklist()
                return

        self.main_window.pensando_tutor(True)
        mrm = self.xanalyzer.analiza(fen)
        self.main_window.pensando_tutor(False)
        forcing_moves = ForcingMoves.ForcingMoves(self.board, mrm, self.main_window)
        forcing_moves.fm_show_checklist()

    def message_on_pgn(self, mens, titulo=None, delayed=False):
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        QTUtil2.message(self.main_window, mens, titulo=titulo, px=p.x(), py=p.y(), delayed=delayed)

    def mensaje(self, mens, titulo=None, delayed=False):
        QTUtil2.message_bold(self.main_window, mens, titulo, delayed=delayed)

    def show_analysis(self):
        with QTUtil2.OneMomentPlease(self.main_window):
            elos = self.game.calc_elos(self.configuration)
            elos_form = self.game.calc_elos_form(self.configuration)
            alm = Histogram.gen_histograms(self.game)
            (
                alm.indexesHTML,
                alm.indexesHTMLelo,
                alm.indexesHTMLmoves,
                alm.indexesRAW,
                alm.eloW,
                alm.eloB,
                alm.eloT,
            ) = AnalysisIndexes.gen_indexes(self.game, elos, elos_form, alm)
            alm.is_white_bottom = self.board.is_white_bottom

        if len(alm.lijg) == 0:
            QTUtil2.message(self.main_window, _("There are no analyzed moves."))
        else:
            WindowAnalysisGraph.show_graph(self.main_window, self, alm, Analysis.show_analysis)

    def save_db(self, database):
        try:
            pgn = self.listado("pgn")
            li_tags = []
            for linea in pgn.split("\n"):
                if linea.startswith("["):
                    ti = linea.split('"')
                    if len(ti) == 3:
                        key = ti[0][1:].strip()
                        valor = ti[1].strip()
                        li_tags.append([key, valor])
                else:
                    break
        except AttributeError:
            li_tags = []

        pc = Game.Game(li_tags=li_tags)
        pc.assign_other_game(self.game)

        db = DBgames.DBgames(database)
        resp = db.insert(pc)
        db.close()
        if resp:
            QTUtil2.message_bold(self.main_window, _("Saved") + ": " + db.path_file)
        else:
            QTUtil2.message_error(self.main_window, _("This game already exists."))

    def save_lcsb(self):
        if self.game_type in (GT_ALONE, GT_GAME, GT_VARIATIONS) and hasattr(self, "grabarComo"):
            return getattr(self, "grabarComo")()

        dic = dict(GAME=self.game.save(True))
        extension = "lcsb"
        file = self.configuration.folder_save_lcsb()
        while True:
            file = SelectFiles.salvaFichero(self.main_window, _("File to save"), file, extension, False)
            if file:
                file = str(file)
                if os.path.isfile(file):
                    yn = QTUtil2.question_withcancel(
                        self.main_window,
                        _X(_("The file %1 already exists, what do you want to do?"), file),
                        si=_("Overwrite"),
                        no=_("Choose another"),
                    )
                    if yn is None:
                        break
                    if not yn:
                        continue
                direc = os.path.dirname(file)
                if direc != self.configuration.folder_save_lcsb():
                    self.configuration.folder_save_lcsb(direc)
                    self.configuration.graba()

                name = os.path.basename(file)
                if Util.save_pickle(file, dic):
                    QTUtil2.temporary_message(self.main_window, _X(_("Saved to %1"), name), 0.8)
                    return
                else:
                    QTUtil2.message_error(self.main_window, "%s: %s" % (_("Unable to save"), name))

            break

    def save_pgn(self):
        w = WindowSavePGN.WSave(self.main_window, self.game)
        w.exec_()

    def save_pgn_clipboard(self):
        QTUtil.set_clipboard(self.game.pgn())
        QTUtil2.message_bold(self.main_window, _("PGN is in clipboard"))

    def save_fen(self, siFichero):
        dato = self.listado("fen")
        if siFichero:
            extension = "fns"
            resp = SelectFiles.salvaFichero(
                self.main_window, _("File to save"), self.configuration.save_folder(), extension, False
            )
            if resp:
                if "." not in resp:
                    resp += ".fns"
                try:
                    modo = "w"
                    if Util.exist_file(resp):
                        yn = QTUtil2.question_withcancel(
                            self.main_window,
                            _X(_("The file %1 already exists, what do you want to do?"), resp),
                            si=_("Append"),
                            no=_("Overwrite"),
                        )
                        if yn is None:
                            return
                        if yn:
                            modo = "a"
                            dato = "\n" + dato
                    with open(resp, modo, encoding="utf-8", errors="ignore") as q:
                        q.write(dato)
                    QTUtil2.message_bold(self.main_window, _X(_("Saved to %1"), resp))
                    direc = os.path.dirname(resp)
                    if direc != self.configuration.save_folder():
                        self.configuration.set_save_folder(direc)
                except:
                    QTUtil.set_clipboard(dato)
                    QTUtil2.message_error(
                        self.main_window,
                        "%s : %s\n\n%s"
                        % (_("Unable to save"), resp, _("It is saved in the clipboard to paste it wherever you want.")),
                    )

        else:
            QTUtil.set_clipboard(dato)
            QTVarios.fen_is_in_clipboard(self.main_window)

    def arbol(self):
        row, column = self.main_window.pgnPosActual()
        num_moves, nj, row, is_white = self.jugadaActual()
        if column.key == "NUMBER":
            nj -= 1
        w = WindowArbol.WindowArbol(self.main_window, self.game, nj, self.procesador)
        w.exec_()

    def control0(self):
        row, column = self.main_window.pgnPosActual()
        num_moves, nj, row, is_white = self.jugadaActual()
        if num_moves:
            self.game.is_finished()
            if row == 0 and column.key == "NUMBER":
                fen = self.game.first_position.fen()
                nj = -1
            else:
                move = self.game.move(nj)
                fen = move.position.fen()

            pgn_active = self.pgn.actual()
            pgn = ""
            for linea in pgn_active.split("\n"):
                if linea.startswith("["):
                    pgn += linea.strip()
                else:
                    break

            p = self.game.copia(nj)
            pgn += p.pgn_base_raw()
            pgn = pgn.replace("|", "-")

            siguientes = ""
            if nj < len(self.game) - 1:
                p = self.game.copy_from_move(nj + 1)
                siguientes = p.pgn_base_raw(p.first_position.num_moves).replace("|", "-")

            txt = "%s||%s|%s\n" % (fen, siguientes, pgn)
            QTUtil.set_clipboard(txt)
            QTUtil2.temporary_message(
                self.main_window, _("It is saved in the clipboard to paste it wherever you want."), 2
            )

    def tablasPlayer(self):
        # Para elo games + entmaq
        si_acepta = False
        nplies = len(self.game)
        if len(self.lirm_engine) >= 4 and nplies > 40:
            if nplies > 100:
                limite = -50
            elif nplies > 60:
                limite = -100
            else:
                limite = -150
            si_acepta = True
            for rm in self.lirm_engine[-3:]:
                if rm.centipawns_abs() > limite:
                    si_acepta = False
            if not si_acepta:
                si_ceros = True
                for rm in self.lirm_engine[-3:]:
                    if abs(rm.centipawns_abs()) > 15:
                        si_ceros = False
                        break
                if si_ceros:
                    mrm = self.xtutor.analiza(self.game.last_position.fen(), None, 7)
                    rm = mrm.best_rm_ordered()
                    if abs(rm.centipawns_abs()) < 15:
                        si_acepta = True
        if si_acepta:
            self.game.last_jg().is_draw_agreement = True
            self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
        else:
            QTUtil2.message_bold(self.main_window, _("Sorry, but the engine doesn't accept a draw right now."))
        self.next_test_resign = 999
        return si_acepta

    def valoraRMrival(self):
        if len(self.game) < 50 or len(self.lirm_engine) <= 5:
            return True
        if self.next_test_resign:
            self.next_test_resign -= 1
            return True
        b = random.random() ** 0.33

        # Resign
        is_resign = True
        for n, rm in enumerate(self.lirm_engine[-5:]):
            if int(rm.centipawns_abs() * b) > self.resign_limit:
                is_resign = False
                break
        if is_resign:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 wants to resign, do you accept it?"), self.xrival.name))
            if resp:
                self.game.resign(self.is_engine_side_white)
                return False
            else:
                self.next_test_resign = 999
                return True

        # # Draw
        is_draw = True
        for rm in self.lirm_engine[-5:]:
            pts = rm.centipawns_abs()
            if (not (-250 < int(pts * b) < -100)) or pts < -250:
                is_draw = False
                break
        if is_draw:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 proposes draw, do you accept it?"), self.xrival.name))
            if resp:
                self.game.last_jg().is_draw_agreement = True
                self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
                return False
            else:
                self.next_test_resign = 999
                return True

        return True

    def utilidadesElo(self):
        if self.is_competitive:
            self.utilities(with_tree=False)
        else:
            li_extra_options = (("books", _("Consult a book"), Iconos.Libros()),)

            resp = self.utilities(li_extra_options, with_tree=True)
            if resp == "books":
                li_movs = self.librosConsulta(True)
                if li_movs:
                    for x in range(len(li_movs) - 1, -1, -1):
                        from_sq, to_sq, promotion = li_movs[x]
                        self.player_has_moved_base(from_sq, to_sq, promotion)

    def pgn_informacion_menu(self):
        menu = QTVarios.LCMenu(self.main_window)

        for key, valor in self.game.dic_tags().items():
            si_fecha = key.upper().endswith("DATE")
            if key.upper() == "FEN":
                continue
            if si_fecha:
                valor = valor.replace(".??", "").replace(".?", "")
            valor = valor.strip("?")
            if valor:
                menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())

        menu.lanza()

    def save_selected_position(self, linea_training):
        # Llamado from_sq ManagerEnPos and ManagerEntTac, para salvar la position tras pulsar una P
        with open(self.configuration.ficheroSelectedPositions, "at", encoding="utf-8", errors="ignore") as q:
            q.write(linea_training + "\n")
        QTUtil2.temporary_message(
            self.main_window, _('Position saved in "%s" file.') % self.configuration.ficheroSelectedPositions, 2
        )
        self.procesador.entrenamientos.menu = None

    def current_position(self):
        num_moves, nj, row, is_white = self.jugadaActual()
        if nj == -1:
            return self.game.first_position
        else:
            move: Move.Move = self.game.move(nj)
            return move.position

    def play_current_position(self):
        row, column = self.main_window.pgnPosActual()
        num_moves, nj, row, is_white = self.jugadaActual()
        self.game.is_finished()
        if row == 0 and column.key == "NUMBER" or nj == -1:
            gm = self.game.copia(0)
            gm.li_moves = []
        else:
            gm = self.game.copia(nj)
        gm.set_unknown()
        gm.is_finished()
        gm.li_tags = []
        gm.set_tag("Site", Code.lucas_chess)
        gm.set_tag("Event", _("Play current position"))
        for previous in ("Event", "Site", "Date", "Round", "White", "Black", "Result", "WhiteElo", "BlackElo"):
            ori = self.game.get_tag(previous)
            if ori:
                gm.set_tag(f"Original{previous}", ori)
        dic = {"GAME": gm.save(), "ISWHITE": gm.last_position.is_white}
        fich = Util.relative_path(self.configuration.temporary_file("pkd"))
        Util.save_pickle(fich, dic)

        XRun.run_lucas("-play", fich)

    def start_message(self, nomodal=False):
        mensaje = _("Press the continue button to start.")
        self.mensaje(mensaje, delayed=nomodal)

    def player_has_moved_base(self, from_sq, to_sq, promotion=""):
        if self.board.variation_history is not None:
            if not (self.in_end_of_line() and self.board.variation_history.count("|") == 0):
                return self.mueve_variation(from_sq, to_sq, promotion="")
        return self.messenger(from_sq, to_sq, promotion)

    def mueve_variation(self, from_sq, to_sq, promotion=""):
        link_variation_pressed = self.main_window.informacionPGN.variantes.link_variation_pressed
        li_variation_move = [int(cnum) for cnum in self.board.variation_history.split("|")]
        num_var_move = li_variation_move[0]

        is_in_main_move = len(li_variation_move) == 1
        variation = None

        if is_in_main_move:
            num_var_move += 1
            var_move = self.game.move(num_var_move)
            # pgn debe ir al siguiente movimiento
        else:
            is_num_variation = True
            var_move = self.game.move(num_var_move)
            variation = None
            for num in li_variation_move[1:]:
                if is_num_variation:
                    variation = var_move.variations.get(num)
                else:
                    var_move = variation.move(num)
                    num_var_move = num
                is_num_variation = not is_num_variation

        if not promotion and var_move.position_before.pawn_can_promote(from_sq, to_sq):
            promotion = self.board.peonCoronando(var_move.position_before.is_white)
            if promotion is None:
                return None
        else:
            promotion = ""

        movimiento = from_sq + to_sq + promotion

        if is_in_main_move:
            if var_move.movimiento() == movimiento:
                self.move_according_key(GO_FORWARD)
                return
            else:
                position_before = var_move.position_before.copia()
                game_var = Game.Game(first_position=position_before)
                ok, mens, new_move = Move.get_game_move(game_var, position_before, from_sq, to_sq, promotion)
                if not ok:
                    return

                game_var.add_move(new_move)
                num_var = var_move.add_variation(game_var)

                self.main_window.activaInformacionPGN(True)
                row, column = self.main_window.pgnPosActual()
                is_white = var_move.position_before.is_white
                # if is_white and column.key == "WHITE":
                if is_white and column.key == "BLACK":
                    row += 1
                self.main_window.pgnColocate(row, is_white)
                self.put_view()
                link_variation_pressed(f"{num_var_move}|{num_var}|0")
                self.kibitzers_manager.put_game(game_var, self.board.is_white_bottom)
        else:
            # si tiene mas movimientos se verifica si coincide con el siguiente
            if len(variation) > num_var_move + 1:
                cvariation_move = "|".join([cnum for cnum in self.board.variation_history.split("|")][:-1])
                var_move = variation.move(num_var_move + 1)
                if var_move.movimiento() == movimiento:
                    link = "%s|%d" % (cvariation_move, (num_var_move + 1))
                    self.main_window.informacionPGN.variantes.link_variation_pressed(link)
                    return

                position_before = var_move.position_before.copia()
                game_var = Game.Game(first_position=position_before)
                ok, mens, new_move = Move.get_game_move(game_var, position_before, from_sq, to_sq, promotion)
                if not ok:
                    return

                game_var.add_move(new_move)
                var_move.add_variation(game_var)
                link_variation_pressed(
                    "%s|%d|%d|%d" % (cvariation_move, (num_var_move + 1), len(var_move.variations) - 1, 0)
                )
                self.kibitzers_manager.put_game(game_var, self.board.is_white_bottom)

            # si no tiene mas movimientos se añade al final
            else:
                position_before = var_move.position.copia()
                ok, mens, new_move = Move.get_game_move(variation, position_before, from_sq, to_sq, promotion)
                if not ok:
                    return

                variation.add_move(new_move)
                cvariation_move = "|".join([cnum for cnum in self.board.variation_history.split("|")][:-1])
                link_variation_pressed("%s|%d" % (cvariation_move, (num_var_move + 1)))
                self.kibitzers_manager.put_game(variation, self.board.is_white_bottom)

    def keypressed_when_variations(self, nkey, modifiers):
        if len(self.game) == 0:
            return

        # Si no tiene variantes -> move_according_key
        num_moves, nj, row, is_white = self.jugadaActual()
        main_move: Move.Move = self.game.move(nj)
        if len(main_move.variations) == 0:
            return self.move_according_key(nkey)

        variation_history = self.board.variation_history
        navigating_variations = variation_history.count("|") >= 2
        if modifiers:  # and modifiers == QtCore.Qt.ShiftModifier:
            if not navigating_variations:
                variation_history = f'{variation_history.split("|")[0]}|0|0'
                self.main_window.informacionPGN.variantes.link_variation_pressed(variation_history)
                return

        if not navigating_variations:
            return self.move_according_key(nkey)

        if variation_history.count("|") == 2:
            num_move, num_variation, num_variation_move = [int(cnum) for cnum in variation_history.split("|")]
            main_move: Move.Move = self.game.move(num_move)
            num_variations = len(main_move.variations)
            num_moves_current_variation = len(main_move.variations.li_variations[num_variation])

            if nkey == GO_BACK:
                if num_variation_move > 0:
                    num_variation_move -= 1
                else:
                    self.move_according_key(nkey)
                    return
            elif nkey == GO_FORWARD:
                if num_variation_move < num_moves_current_variation - 1:
                    num_variation_move += 1
                else:
                    return
            elif nkey == GO_BACK2:
                if num_variation > 0 and modifiers != QtCore.Qt.ShiftModifier:
                    num_variation -= 1
                    num_variation_move = 0
                else:
                    if modifiers == QtCore.Qt.ShiftModifier:
                        self.main_window.informacionPGN.variantes.link_variation_pressed(str(num_move))
                    return
            elif nkey == GO_FORWARD2:
                if num_variation < num_variations - 1:
                    num_variation += 1
                    num_variation_move = 0
                else:
                    return
            else:
                return

            link = f"{num_move}|{num_variation}|{num_variation_move}"
            self.main_window.informacionPGN.variantes.link_variation_pressed(link)

        else:

            li_var = variation_history.split("|")
            last = int(li_var[-1])

            if nkey == GO_BACK:
                if last > 0:
                    li_var[-1] = str(last-1)
                else:
                    li_var = li_var[:-2]

            elif nkey == GO_FORWARD:
                li_var[-1] = str(last+1)

            elif nkey == GO_BACK2:
                li_var = li_var[:-2]

            elif nkey == GO_FORWARD2:
                li_var = li_var[:-2]

            else:
                return

            link = "|".join(li_var)
            self.main_window.informacionPGN.variantes.link_variation_pressed(link)

    def bestmove_from_analysis_bar(self):
        return self.main_window.bestmove_from_analysis_bar()

    def is_active_analysys_bar(self):
        return self.main_window.with_analysis_bar
