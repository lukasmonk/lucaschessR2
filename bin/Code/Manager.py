import os
import random
import time

import FasterCode

import Code
from Code import ControlPGN
from Code import Util
from Code import XRun
from Code.Analysis import Analysis, AnalysisGame, AnalysisIndexes, Histogram, WindowAnalysisGraph
from Code.Base import Game, Move, Position
from Code.Base.Constantes import (
    GT_ALONE,
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
    RS_UNKNOWN,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_UTILITIES,
    TB_EBOARD,
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
    GT_OPENINGS,
    GT_POSITIONS,
    GT_TACTICS,
    TERMINATION_DRAW_AGREEMENT,
)
from Code.Board import BoardTypes
from Code.Databases import DBgames
from Code.Engines import WConfEngines
from Code.Kibitzers import Kibitzers
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
        self.hints = None
        self.ayudas_iniciales = 0

        self.is_competitive = False

        self.resultado = RS_UNKNOWN

        self.categoria = None

        self.main_window.set_manager_active(self)

        self.game: Game.Game
        self.new_game()

        self.listaOpeningsStd = OpeningsStd.ap

        self.human_is_playing = False

        self.pgn = ControlPGN.ControlPGN(self)

        self.timekeeper = Util.Timekeeper()

        self.xtutor = procesador.XTutor()
        self.xanalyzer = procesador.XAnalyzer()
        self.xrival = None

        self.if_analyzing = False
        self.is_analyzed_by_tutor = False

        self.resign_limit = -99999

        self.rm_rival = None  # Usado por el tutor para mostrar las intenciones del rival

        self.plays_instead_of_me_option = False

        self.unMomento = self.procesador.unMomento
        self.um = None

        self.xRutinaAccionDef = None

        self.xpelicula = None

        self.main_window.ajustaTam()

        self.board.exePulsadoNum = self.exePulsadoNum
        self.board.exePulsadaLetra = self.exePulsadaLetra

        # Capturas
        self.capturasActivable = False

        # Informacion
        self.informacionActivable = False

        self.nonDistract = None

        # x Control del tutor
        #  asi sabemos si ha habido intento de analysis previo (por ejemplo el usuario mientras piensa decide activar el tutor)
        self.siIniAnalizaTutor = False

        self.continueTt = not self.configuration.x_engine_notbackground

        # Atajos raton:
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

        self.messenger = None

        self.kibitzers_manager = self.procesador.kibitzers_manager

        self.with_eboard = len(self.configuration.x_digital_board) > 0

    def disable_use_eboard(self):
        if self.configuration.x_digital_board:
            self.with_eboard = False

    def new_game(self):
        self.game = Game.Game()
        self.game.set_tag("Site", Code.lucas_chess)
        hoy = Util.today()
        self.game.set_tag("Date", "%d.%02d.%02d" % (hoy.year, hoy.month, hoy.day))

    def ponFinJuego(self, with_takeback=False):
        self.main_window.thinking(False)
        self.runSound.close()
        if len(self.game):
            self.state = ST_ENDGAME
            self.disable_all()
            li_options = [TB_CLOSE]
            if hasattr(self, "reiniciar"):
                li_options.append(TB_REINIT)
            if with_takeback:
                li_options.append(TB_TAKEBACK)
            li_options.append(TB_CONFIG)
            li_options.append(TB_UTILITIES)

            self.main_window.pon_toolbar(li_options, with_eboard=self.with_eboard)
            self.remove_hints(siQuitarAtras=not with_takeback)
            # self.main_window.deactivate_eboard()
        else:
            self.procesador.reset()
            # self.main_window.deactivate_eboard()

    def set_toolbar(self, li_options):
        self.main_window.pon_toolbar(li_options, with_eboard=self.with_eboard)

    def finManager(self):
        # se llama from_sq procesador.start, antes de borrar el manager
        self.board.atajosRaton = None
        if self.nonDistract:
            self.main_window.base.tb.setVisible(True)

    def atajosRatonReset(self):
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

    @staticmethod
    def otherCandidates(liMoves, position, liC):
        liPlayer = []
        for mov in liMoves:
            if mov.mate():
                liPlayer.append((mov.xto(), "P#"))
            elif mov.check():
                liPlayer.append((mov.xto(), "P+"))
            elif mov.capture():
                liPlayer.append((mov.xto(), "Px"))
        oposic = position.copia()
        oposic.is_white = not position.is_white
        oposic.en_passant = ""
        siJaque = FasterCode.ischeck()
        FasterCode.set_fen(oposic.fen())
        liO = FasterCode.get_exmoves()
        liRival = []
        for n, mov in enumerate(liO):
            if not siJaque:
                if mov.mate():
                    liRival.append((mov.xto(), "R#"))
                elif mov.check():
                    liRival.append((mov.xto(), "R+"))
                elif mov.capture():
                    liPlayer.append((mov.xto(), "Rx"))
            elif mov.capture():
                liPlayer.append((mov.xto(), "Rx"))

        liC.extend(liRival)
        liC.extend(liPlayer)

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
        siOrigen = siDestino = False
        for mov in li:
            from_sq = mov.xfrom()
            to_sq = mov.xto()
            if a1h8 == from_sq:
                siOrigen = True
                break
            if a1h8 == to_sq:
                siDestino = True
                break
        origen = destino = None
        if siOrigen or siDestino:
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

        liC = []
        for mov in li:
            a1 = mov.xfrom()
            h8 = mov.xto()
            siO = (origen == a1) if origen else None
            siD = (destino == h8) if destino else None

            if (siO and siD) or ((siO is None) and siD) or ((siD is None) and siO):
                t = (a1, h8)
                if not (t in liC):
                    liC.append(t)

        if origen:
            liC = [(dh[1], "C") for dh in liC]
        else:
            liC = [(dh[0], "C") for dh in liC]
        self.otherCandidates(li, position, liC)
        return liC

    def atajosRaton(self, position, a1h8):
        if a1h8 is None or not self.board.pieces_are_active:
            self.atajosRatonReset()
            return

        # is_white = position.is_white
        # num_moves, nj, row, is_white = self.jugadaActual()
        # if nj < num_moves - 1:
        #     self.atajosRatonReset()
        #     liC = self.colect_candidates(a1h8)
        #     self.board.show_candidates(liC)
        #     return

        # position = self.game.last_position
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
            self.atajosRatonReset()
            return

        def mueve():
            self.board.muevePiezaTemporal(self.atajosRatonOrigen, self.atajosRatonDestino)
            if (not self.board.mensajero(self.atajosRatonOrigen, self.atajosRatonDestino)) and self.atajosRatonOrigen:
                self.board.set_piece_again(self.atajosRatonOrigen)
            self.atajosRatonReset()

        def show_candidates():
            if self.configuration.x_show_candidates:
                li_c = []
                for mov in li_moves:
                    a1 = mov.xfrom()
                    h8 = mov.xto()
                    if a1 == self.atajosRatonOrigen:
                        li_c.append((h8, "C"))
                if self.state != ST_PLAYING:
                    self.otherCandidates(li_moves, position, li_c)
                self.board.show_candidates(li_c)

        if not self.configuration.x_mouse_shortcuts:
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

    def repiteUltimaJugada(self):
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
            # self.goto_end()

    def move_the_pieces(self, liMovs, is_rival=False):
        if is_rival and self.configuration.x_show_effects:

            rapidez = self.configuration.pieces_speed_porc()
            cpu = self.procesador.cpu
            cpu.reset()
            seconds = None

            # primero los movimientos
            for movim in liMovs:
                if movim[0] == "m":
                    if seconds is None:
                        from_sq, to_sq = movim[1], movim[2]
                        dc = ord(from_sq[0]) - ord(to_sq[0])
                        df = int(from_sq[1]) - int(to_sq[1])
                        # Maxima distancia = 9.9 ( 9,89... sqrt(7**2+7**2)) = 4 seconds
                        dist = (dc**2 + df**2) ** 0.5
                        seconds = 4.0 * dist / (9.9 * rapidez)
                    if self.procesador.manager:
                        cpu.muevePieza(movim[1], movim[2], seconds)
                    else:
                        return

            if seconds is None:
                seconds = 1.0

            # segundo los borrados
            for movim in liMovs:
                if movim[0] == "b":
                    if self.procesador.manager:
                        cpu.borraPiezaSecs(movim[1], seconds)
                    else:
                        return

            # tercero los cambios
            for movim in liMovs:
                if movim[0] == "c":
                    if self.procesador.manager:
                        cpu.cambiaPieza(movim[1], movim[2], siExclusiva=True)
                    else:
                        return

            if self.procesador.manager:
                cpu.runLineal()

        else:
            for movim in liMovs:
                if movim[0] == "b":
                    self.board.borraPieza(movim[1])
                elif movim[0] == "m":
                    self.board.muevePieza(movim[1], movim[2])
                elif movim[0] == "c":
                    self.board.cambiaPieza(movim[1], movim[2])
        # Aprovechamos que esta operacion se hace en cada move
        self.atajosRatonReset()

    def num_rows(self):
        return self.pgn.num_rows()

    def put_view(self):
        if not hasattr(self.pgn, "move"):  # manager60 por ejemplo
            return
        row, column = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(row, column.key)

        if (
            self.main_window.siCapturas
            or self.main_window.siInformacionPGN
            or self.kibitzers_manager.some_working()
            or self.configuration.x_show_bestmove
        ):
            if move:
                dic = move.position.capturas_diferencia()
                if move.analysis and self.configuration.x_show_bestmove:
                    mrm, pos = move.analysis
                    if pos:  # no se muestra la mejor move si es la realizada
                        rm0 = mrm.mejorMov()
                        self.board.put_arrow_scvar([(rm0.from_sq, rm0.to_sq)])

            else:
                dic = self.game.last_position.capturas_diferencia()

            nomOpening = ""
            opening = self.game.opening
            if opening:
                nomOpening = opening.tr_name
                if opening.eco:
                    nomOpening += " (%s)" % opening.eco
            if self.main_window.siCapturas:
                self.main_window.ponCapturas(dic)
            if self.main_window.siInformacionPGN:
                if (row == 0 and column.key == "NUMBER") or row < 0:
                    self.main_window.put_informationPGN(self.game, None, nomOpening)
                else:
                    move.pos_in_game = pos_move
                    self.main_window.put_informationPGN(None, move, nomOpening)

            if self.kibitzers_manager.some_working():
                if self.si_mira_kibitzers():
                    self.mira_kibitzers(True)
                else:
                    self.kibitzers_manager.stop()

    def si_mira_kibitzers(self):
        return (self.state == ST_ENDGAME) or (not self.is_competitive)
        # self.game_type in (GT_POSITIONS, GT_AGAINST_PGN, GT_AGAINST_ENGINE, GT_TACTICS, GT_AGAINST_GM, GT_ALONE, GT_BOOK, GT_OPENINGS) or
        # (self.game_type in (GT_ELO, GT_MICELO) and ))

    def mira_kibitzers(self, all_kibitzers):
        row, column = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(row, column.key)
        if pos_move is not None:
            if column.key == "NUMBER" and pos_move != -1:
                pos_move -= 1
        game_run = self.game.copy_raw(pos_move)
        self.kibitzers_manager.put_game(game_run, self.board.is_white_bottom, not all_kibitzers)

    def put_pieces_bottom(self, is_white):
        self.board.set_side_bottom(is_white)

    def remove_hints(self, siTambienTutorAtras=True, siQuitarAtras=True):
        self.main_window.remove_hints(siTambienTutorAtras, siQuitarAtras)
        self.set_activate_tutor(False)

    def ponAyudas(self, hints, siQuitarAtras=True):
        self.main_window.ponAyudas(hints, siQuitarAtras)

    def thinking(self, siPensando):
        if self.configuration.x_cursor_thinking:
            self.main_window.thinking(siPensando)

    def set_activate_tutor(self, siActivar):
        self.main_window.set_activate_tutor(siActivar)
        self.is_tutor_enabled = siActivar

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
        self.board.set_dispatcher(self.player_has_moved_base, self.atajosRaton)

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

    def beepExtendido(self, siNuestro=False):
        if siNuestro:
            if not self.configuration.x_sound_our:
                return
        if self.configuration.x_sound_move:
            if len(self.game):
                move = self.game.move(-1)
                self.runSound.play_list(move.listaSonidos())
        if self.configuration.x_sound_beep:
            self.runSound.playBeep()

    def beepZeitnot(self):
        self.runSound.playZeitnot()

    def beepError(self):
        if self.configuration.x_sound_error:
            self.runSound.playError()

    def beepResultadoCAMBIAR(self, resfinal):  # TOO Cambiar por beepresultado1
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

    def beepResultado(self, beep_result):
        if beep_result:
            if not self.configuration.x_sound_results:
                return
            self.runSound.play_key(beep_result)

    def pgnRefresh(self, is_white):
        self.main_window.pgnRefresh(is_white)

    def refresh(self):
        self.board.escena.update()
        self.main_window.update()
        QTUtil.refresh_gui()

    def mueveJugada(self, tipo):
        game = self.game
        if not len(game):
            return
        row, column = self.main_window.pgnPosActual()

        key = column.key
        if key == "NUMBER":
            is_white = tipo == "-"
            row -= 1
        else:
            is_white = key != "BLACK"

        starts_with_black = game.starts_with_black

        lj = len(game)
        if starts_with_black:
            lj += 1
        ultFila = (lj - 1) / 2
        siUltBlancas = lj % 2 == 1

        if tipo == GO_BACK:
            if is_white:
                row -= 1
            is_white = not is_white
            pos = row * 2
            if not is_white:
                pos += 1
            if row < 0 or (row == 0 and pos == 0 and starts_with_black):
                self.ponteAlPrincipio()
                return
        elif tipo == GO_FORWARD:
            if not is_white:
                row += 1
            is_white = not is_white
        elif tipo == GO_START:
            self.ponteAlPrincipio()
            return
        elif tipo == GO_END:
            row = ultFila
            is_white = not game.last_position.is_white

        if row == ultFila:
            if siUltBlancas and not is_white:
                return

        if row < 0 or row > ultFila:
            self.refresh()
            return
        if row == 0 and is_white and starts_with_black:
            is_white = False

        self.main_window.pgnColocate(row, is_white)
        self.pgnMueve(row, is_white)

    def ponteEnJugada(self, numJugada):
        row = (numJugada + 1) / 2 if self.game.starts_with_black else numJugada / 2
        move = self.game.move(numJugada)
        is_white = move.position_before.is_white
        self.main_window.pgnColocate(row, is_white)
        self.pgnMueve(row, is_white)

    def ponteAlPrincipio(self):
        self.set_position(self.game.first_position)
        self.main_window.base.pgn.goto(0, 0)
        self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

    def ponteAlPrincipioColor(self):
        if self.game.li_moves:
            move = self.game.move(0)
            self.set_position(move.position)
            self.main_window.base.pgn.goto(0, 2 if move.position.is_white else 1)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
            self.put_view()
        else:
            self.ponteAlPrincipio()

    def pgnMueve(self, row, is_white):
        self.pgn.mueve(row, is_white)
        self.put_view()

    def pgnMueveBase(self, row, column):
        if column == "NUMBER":
            if row <= 0:
                if self.pgn.variations_mode:
                    self.set_position(self.game.first_position, "-1")
                    self.main_window.base.pgn.goto(0, 0)
                    self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
                    self.put_view()
                else:
                    self.ponteAlPrincipio()
                return
            else:
                row -= 1
        self.pgn.mueve(row, column == "WHITE")
        self.put_view()

    def goto_end(self):
        if len(self.game):
            self.mueveJugada(GO_END)
        else:
            self.set_position(self.game.first_position)
            self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

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

    def in_end_of_line(self):
        num_moves, nj, row, is_white = self.jugadaActual()
        return nj == num_moves-1


    def pgnInformacion(self):
        if self.informacionActivable:
            self.main_window.activaInformacionPGN()
            self.put_view()
            self.refresh()

    def remove_info(self, is_activatable=False):
        self.main_window.activaInformacionPGN(False)
        self.informacionActivable = is_activatable

    def autosave(self):
        if len(self.game) > 1:
            if self.ayudas_iniciales > 0:
                if not (self.hints is None):
                    usado = self.ayudas_iniciales - self.hints
                    if usado:
                        self.game.set_tag("HintsUsed", str(usado))

            self.game.tag_timeend()
            self.game.set_extend_tags()
            DBgames.autosave(self.game)

    def ponCapPorDefecto(self):
        self.capturasActivable = True
        if self.configuration.x_captures_activate:
            self.main_window.activaCapturas(True)
            self.put_view()

    def ponInfoPorDefecto(self):
        self.informacionActivable = True
        if self.configuration.x_info_activate:
            self.main_window.activaInformacionPGN(True)
            self.put_view()

    def ponCapInfoPorDefecto(self):
        self.ponCapPorDefecto()
        self.ponInfoPorDefecto()

    def capturas(self):
        if self.capturasActivable:
            self.main_window.activaCapturas()
            self.put_view()

    def quitaCapturas(self):
        self.main_window.activaCapturas(False)
        self.put_view()

    def nonDistractMode(self):
        self.nonDistract = self.main_window.base.nonDistractMode(self.nonDistract)
        self.main_window.ajustaTam()

    def boardRightMouse(self, is_shift, is_control, is_alt):
        self.board.lanzaDirector()

    def gridRightMouse(self, is_shift, is_control, is_alt):
        if is_control:
            self.capturas()
        elif is_shift or is_alt:
            self.arbol()
        else:
            self.pgnInformacion()

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
        siUltimo = (pos + 1) >= tam_lj
        if siUltimo:
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
        # self.thinking(True)
        fen = self.game.last_position.fen()
        if not self.is_finished():
            self.mrmTutor = self.xtutor.analiza(fen)
        else:
            self.mrmTutor = None
        # self.thinking(False)
        if with_cursor:
            self.main_window.pensando_tutor(False)
        return self.mrmTutor

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
            self.analyze_begin()

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
        siUltimo = (pos + 1) >= tam_lj

        move = self.game.move(pos)
        return move, is_white, siUltimo, tam_lj, pos

    def help_to_move(self):
        if not self.is_finished():
            move = Move.Move(self.game, position_before=self.game.last_position.copia())
            Analysis.show_analysis(self.procesador, self.xtutor, move, self.board.is_white_bottom, 0, must_save=False)

    def analize_position(self, row, key):
        if row < 0:
            return

        move, is_white, siUltimo, tam_lj, pos_jg = self.dameJugadaEn(row, key)
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
                    GT_BOOK,
                    GT_OPENINGS,
                    GT_TACTICS,
                ]
                or (self.game_type in [GT_ELO, GT_MICELO] and not self.is_competitive)
            ):
                if siUltimo or self.hints == 0:
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
                            '%s\n%s: %d %s: %.01f"' % (mens, _("Depth"), rm.depth, _("Time"), tm)
                        )
                        if self.xanalyzer.mstime_engine and tm*1000 > self.xanalyzer.mstime_engine:
                            self.xanalyzer.stop()
                            ya_cancelado[0] = True
                    return True

                self.xanalyzer.set_gui_dispatch(test_me)
            mrm, pos = self.xanalyzer.analizaJugadaPartida(
                self.game, pos_jg, self.xanalyzer.mstime_engine, self.xanalyzer.depth_engine
            )
            move.analysis = mrm, pos
            self.main_window.base.tb.setDisabled(False)
            self.main_window.base.hide_message()

        Analysis.show_analysis(self.procesador, self.xanalyzer, move, self.board.is_white_bottom, pos_jg)
        self.put_view()

    def analizar(self):
        self.main_window.base.tb.setDisabled(True)
        AnalysisGame.analysis_game(self)
        self.main_window.base.tb.setDisabled(False)
        self.refresh()

    def borrar(self):
        separador = FormLayout.separador
        li_del = []
        li_del.append((_("All") + ":", False))
        li_del.append(separador)
        li_del.append(separador)
        li_del.append((_("Variations") + ":", False))
        li_del.append(separador)
        li_del.append((_("Ratings") + ":", False))
        li_del.append(separador)
        li_del.append((_("Comments") + ":", False))
        li_del.append(separador)
        li_del.append((_("Analysis") + ":", False))
        li_del.append(separador)
        li_del.append((_("Themes") + ":", False))
        resultado = FormLayout.fedit(li_del, title=_("Remove"), parent=self.main_window, icon=Iconos.Delete())
        if resultado:
            is_all, variations, ratings, comments, analysis, themes = resultado[1]
            if is_all:
                variations = ratings = comments = analysis = themes = True
            for move in self.game.li_moves:
                if variations:
                    move.del_variations()
                if ratings:
                    move.del_nags()
                if comments:
                    move.del_comment()
                if analysis:
                    move.del_analysis()
                if themes:
                    move.del_themes()
            self.main_window.base.pgnRefresh()
            self.refresh()

    def replay(self):
        resp = WReplay.param_replay(self.configuration, self.main_window)
        if resp is None:
            return

        seconds, if_start, if_pgn, if_beep, seconds_before = resp

        self.xpelicula = WReplay.Replay(self, seconds, if_start, if_pgn, if_beep, seconds_before)

    def ponRutinaAccionDef(self, rutina):
        self.xRutinaAccionDef = rutina

    def rutinaAccionDef(self, key):
        if self.xRutinaAccionDef:
            self.xRutinaAccionDef(key)
        elif key == TB_CLOSE:
            self.procesador.reset()
        elif key == TB_EBOARD:
            if Code.eboard and self.with_eboard:
                if Code.eboard.driver:
                    self.main_window.deactivate_eboard(100)
                else:
                    Code.eboard.activate(self.board.dispatch_eboard)
                    Code.eboard.set_position(self.board.last_position)
                self.main_window.set_title_toolbar_eboard()

        else:
            self.procesador.run_action(key)

    def finalX0(self):
        # Se llama from_sq la main_window al pulsar X
        # Se verifica si estamos en la replay
        if self.xpelicula:
            self.xpelicula.terminar()
            return False
        return self.final_x()

    def exePulsadoNum(self, siActivar, number):
        if number in [1, 8]:
            if siActivar:
                # Que move esta en el board
                fen = self.fenActivoConInicio()
                is_white = " w " in fen
                if number == 1:
                    siMB = is_white
                else:
                    siMB = not is_white
                self.board.remove_arrows()
                if self.board.flechaSC:
                    self.board.flechaSC.hide()
                li = FasterCode.get_captures(fen, siMB)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.board.creaFlechaMov(d, h, "c")
            else:
                self.board.remove_arrows()
                if self.board.flechaSC:
                    self.board.flechaSC.show()

        elif number in [2, 7]:
            if siActivar:
                # Que move esta en el board
                fen = self.fenActivoConInicio()
                is_white = " w " in fen
                if number == 2:
                    siMB = is_white
                else:
                    siMB = not is_white
                if siMB != is_white:
                    fen = FasterCode.fen_other(fen)
                cp = Position.Position()
                cp.read_fen(fen)
                liMovs = cp.aura()

                self.liMarcosTmp = []
                regMarco = BoardTypes.Marco()
                color = self.board.config_board.flechaActivoDefecto().colorinterior
                if color == -1:
                    color = self.board.config_board.flechaActivoDefecto().color

                st = set()
                for h8 in liMovs:
                    if not (h8 in st):
                        regMarco.a1h8 = h8 + h8
                        regMarco.siMovible = True
                        regMarco.color = color
                        regMarco.colorinterior = color
                        regMarco.opacity = 0.5
                        box = self.board.creaMarco(regMarco)
                        self.liMarcosTmp.append(box)
                        st.add(h8)

            else:
                for box in self.liMarcosTmp:
                    self.board.xremoveItem(box)
                self.liMarcosTmp = []

    def exePulsadaLetra(self, siActivar, letra):
        if siActivar:
            dic = {
                "a": GO_START,
                "b": GO_BACK,
                "c": GO_BACK,
                "d": GO_BACK,
                "e": GO_FORWARD,
                "f": GO_FORWARD,
                "g": GO_FORWARD,
                "h": GO_END,
            }
            self.mueveJugada(dic[letra])

    def kibitzers(self, orden):
        if orden == "edit":
            self.kibitzers_manager.edit()
        else:
            huella = orden
            self.kibitzers_manager.run_new(huella)
            self.mira_kibitzers(False)

    def paraHumano(self):
        self.human_is_playing = False
        self.disable_all()

    def sigueHumano(self):
        self.human_is_playing = True
        self.check_boards_setposition()
        self.activate_side(self.game.last_position.is_white)
        QTUtil.refresh_gui()

    def check_human_move(self, from_sq, to_sq, promotion, with_premove=False):
        if self.human_is_playing:
            if not with_premove:
                self.paraHumano()
        else:
            self.sigueHumano()
            return None

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.game.last_position.siPeonCoronando(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.game.last_position.is_white)
            if promotion is None:
                self.sigueHumano()
                return None
        if promotion:
            movimiento += promotion

        ok, self.error, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            return move
        else:
            self.sigueHumano()
            return None

    def librosConsulta(self, siEnVivo):
        w = WindowArbolBook.WindowArbolBook(self, siEnVivo)
        if w.exec_():
            return w.resultado
        else:
            return None

    def set_position(self, position, variation_history=None):
        self.board.set_position(position, variation_history=variation_history)

    def check_boards_setposition(self):
        self.board.set_raw_last_position(self.game.last_position)

    def play_instead_of_me(self):
        if (
            self.plays_instead_of_me_option
            and self.state == ST_PLAYING
            and (self.hints or self.game_type in (GT_AGAINST_ENGINE, GT_ALONE, GT_POSITIONS, GT_TACTICS))
        ):
            if not self.is_finished():
                if self.if_analyzing and hasattr(self, "analyze_end"):
                    self.analyze_end()
                if self.is_analyzed_by_tutor:
                    mrm = self.mrmTutor
                else:
                    mrm = self.analizaTutor(with_cursor=True)
                rm = mrm.mejorMov()
                if rm.from_sq:
                    self.is_analyzed_by_tutor = True
                    self.player_has_moved_base(rm.from_sq, rm.to_sq, rm.promotion)
                    if self.hints:
                        self.hints -= 1
                        if self.hints:
                            self.ponAyudas(self.hints)
                        else:
                            self.remove_hints()

    def control1(self):
        self.play_instead_of_me()

    def configurar(self, liMasOpciones=None, siCambioTutor=False, siSonidos=False, siBlinfold=True):
        menu = QTVarios.LCMenu(self.main_window)

        # Vista
        menuVista = menu.submenu(_("Show/hide"), Iconos.Vista())
        menuVista.opcion("vista_pgn", _("PGN information"), siChecked=self.configuration.x_info_activate)
        menuVista.separador()
        menuVista.opcion("vista_capturas", _("Captured material"), siChecked=self.configuration.x_captures_activate)
        menuVista.separador()
        menuVista.opcion(
            "vista_bestmove",
            _("Arrow with the best move when there is an analysis"),
            siChecked=self.configuration.x_show_bestmove,
        )
        menu.separador()

        # Ciega - Mostrar todas - Ocultar blancas - Ocultar negras
        if siBlinfold:
            menuCG = menu.submenu(_("Blindfold chess"), Iconos.Ojo())

            si = self.board.blindfold
            if si:
                ico = Iconos.Naranja()
                tit = _("Deactivate")
            else:
                ico = Iconos.Verde()
                tit = _("Activate")
            menuCG.opcion("cg_change", tit, ico)
            menuCG.separador()
            menuCG.opcion("cg_conf", _("Configuration"), Iconos.Opciones())
            menuCG.separador()
            menuCG.opcion("cg_pgn", "%s: %s" % (_("PGN"), _("Hide") if self.pgn.must_show else _("Show")), Iconos.PGN())

        # Sonidos
        if siSonidos:
            menu.separador()
            menu.opcion("sonido", _("Sounds"), Iconos.S_Play())

        menu.separador()
        menu.opcion("engines", _("Engines configuration"), Iconos.ConfEngines())

        # On top
        menu.separador()
        label = _("Disable") if self.main_window.onTop else _("Enable")
        menu.opcion(
            "ontop", "%s: %s" % (label, _("window on top")), Iconos.Bottom() if self.main_window.onTop else Iconos.Top()
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

        # Mas Opciones
        if liMasOpciones:
            menu.separador()
            for key, label, icono in liMasOpciones:
                if label is None:
                    menu.separador()
                else:
                    menu.opcion(key, label, icono)

        resp = menu.lanza()
        if resp:

            if liMasOpciones:
                for key, label, icono in liMasOpciones:
                    if resp == key:
                        return resp

            if resp == "log_open":
                Code.list_engine_managers.active_logs(True)

            elif resp == "log_close":
                Code.list_engine_managers.active_logs(False)

            elif resp.startswith("vista_"):
                resp = resp[6:]
                if resp == "pgn":
                    self.main_window.activaInformacionPGN()
                    self.put_view()
                elif resp == "capturas":
                    self.main_window.activaCapturas()
                    self.put_view()
                elif resp == "bestmove":
                    self.configuration.x_show_bestmove = not self.configuration.x_show_bestmove
                    self.configuration.graba()
                    self.put_view()

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
                    self.main_window.base.pgnRefresh()
                elif orden == "change":
                    x = str(self)
                    modoPosicionBlind = False
                    for tipo in ("ManagerEntPos",):
                        if tipo in x:
                            modoPosicionBlind = True
                    self.board.blindfoldChange(modoPosicionBlind)

                elif orden == "conf":
                    self.board.blindfoldConfig()

        return None

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

    def utilities(self, liMasOpciones=None, siArbol=True):

        menu = QTVarios.LCMenu(self.main_window)

        siJugadas = len(self.game) > 0

        # Grabar
        icoGrabar = Iconos.Grabar()
        icoFichero = Iconos.GrabarFichero()
        icoCamara = Iconos.Camara()
        icoClip = Iconos.Clipboard()

        trFichero = _("Save to a file")
        trPortapapeles = _("Copy to clipboard")

        menu_save = menu.submenu(_("Save"), icoGrabar)

        key_ctrl = _("CTRL") if self.configuration.x_copy_ctrl else _("ALT")
        menu_pgn = menu_save.submenu(_("PGN Format"), Iconos.PGN())
        menu_pgn.opcion("pgnfile", trFichero, Iconos.PGN())
        menu_pgn.separador()
        menu_pgn.opcion(
            "pgnclipboard", "%s [%s %s C]" % (trPortapapeles, key_ctrl, _("SHIFT || From keyboard")), icoClip
        )
        menu_save.separador()

        menu_fen = menu_save.submenu(_("FEN Format"), Iconos.Naranja())
        menu_fen.opcion("fenfile", trFichero, icoFichero)
        menu_fen.separador()
        menu_fen.opcion("fenclipboard", "%s [%s C]" % (trPortapapeles, key_ctrl), icoClip)

        menu_save.separador()

        menu_save.opcion("lcsbfichero", "%s -> %s" % (_("lcsb Format"), _("Create your own game")), Iconos.JuegaSolo())

        menu_save.separador()

        menuDB = menu_save.submenu(_("A database"), Iconos.DatabaseMas())
        QTVarios.menuDB(menuDB, self.configuration, True, indicador_previo="dbf_")  # , remove_autosave=True)
        menu_save.separador()

        menuV = menu_save.submenu(_("Board -> Image"), icoCamara)
        menuV.opcion("volfichero", trFichero, icoFichero)
        menuV.opcion("volportapapeles", trPortapapeles, icoClip)

        menu.separador()

        # Kibitzers
        if self.si_mira_kibitzers():
            menu.separador()
            menuKibitzers = menu.submenu(_("Kibitzers"), Iconos.Kibitzer())

            kibitzers = Kibitzers.Kibitzers()
            for huella, name, ico in kibitzers.lista_menu():
                menuKibitzers.opcion("kibitzer_%s" % huella, name, ico)
            menuKibitzers.separador()
            menuKibitzers.opcion("kibitzer_edit", _("Edition"), Iconos.ModificarP())

            menu.separador()
            menu.opcion("play", _("Play current position"), Iconos.MoverJugar())

        # Analizar
        if siJugadas:
            if not (self.game_type in (GT_ELO, GT_MICELO) and self.is_competitive and self.state == ST_PLAYING):
                menu.separador()
                nAnalisis = 0
                for move in self.game.li_moves:
                    if move.analysis:
                        nAnalisis += 1
                if nAnalisis > 4:
                    submenu = menu.submenu(_("Analysis"), Iconos.Analizar())
                else:
                    submenu = menu
                submenu.opcion("analizar", _("Analyze"), Iconos.Analizar())
                if nAnalisis > 4:
                    submenu.separador()
                    submenu.opcion("analizar_grafico", _("Show graphics"), Iconos.Estadisticas())
                menu.separador()

                menu.opcion("borrar", _("Remove"), Iconos.Delete())
                menu.separador()

        # Pelicula
        if siJugadas:
            menu.opcion("replay", _("Replay game"), Iconos.Pelicula())
            menu.separador()

        # Juega por mi
        if (
            self.plays_instead_of_me_option
            and self.state == ST_PLAYING
            and (self.hints or self.game_type in (GT_AGAINST_ENGINE, GT_ALONE, GT_POSITIONS, GT_TACTICS))
        ):
            menu.separador()
            menu.opcion("play_instead_of_me", _("Play instead of me") + "  [%s 1]" % _("CTRL"), Iconos.JuegaPorMi()),

        # Arbol de movimientos
        if siArbol:
            menu.separador()
            menu.opcion("arbol", _("Moves tree"), Iconos.Arbol())

        # Mas Opciones
        if liMasOpciones:
            menu.separador()
            submenu = menu
            for key, label, icono in liMasOpciones:
                if label is None:
                    if icono is None:
                        # liMasOpciones.append((None, None, None))
                        submenu.separador()
                    else:
                        # liMasOpciones.append((None, None, True))  # Para salir del submenu
                        submenu = menu
                elif key is None:
                    # liMasOpciones.append((None, titulo, icono))
                    submenu = menu.submenu(label, icono)

                else:
                    # liMasOpciones.append((key, titulo, icono))
                    submenu.opcion(key, label, icono)
            menu.separador()

        resp = menu.lanza()

        if not resp:
            return

        if liMasOpciones:
            for key, label, icono in liMasOpciones:
                if resp == key:
                    return resp

        if resp == "play_instead_of_me":
            self.play_instead_of_me()

        elif resp == "analizar":
            self.analizar()

        elif resp == "analizar_grafico":
            self.show_analysis()

        elif resp == "borrar":
            self.borrar()

        elif resp == "replay":
            self.replay()

        elif resp == "play":
            self.play_current_position()

        elif resp.startswith("kibitzer_"):
            self.kibitzers(resp[9:])

        elif resp == "arbol":
            self.arbol()

        elif resp.startswith("vol"):
            accion = resp[3:]
            if accion == "fichero":
                resp = SelectFiles.salvaFichero(
                    self.main_window, _("File to save"), self.configuration.x_save_folder, "png", False
                )
                if resp:
                    self.board.save_as_img(resp, "png")

            else:
                self.board.save_as_img()

        elif resp == "lcsbfichero":
            self.game.set_extend_tags()
            self.save_lcsb()

        elif resp == "pgnfile":
            self.game.set_extend_tags()
            self.save_pgn()

        elif resp == "pgnclipboard":
            self.game.set_extend_tags()
            self.save_pgn_clipboard()

        elif resp.startswith("dbf_"):
            self.game.set_extend_tags()
            self.save_db(resp[4:])

        elif resp.startswith("fen"):
            # extension = resp[:3]
            si_fichero = resp.endswith("fichero")
            self.save_fen(si_fichero)

        return None

    def message_on_pgn(self, mens, titulo=None, delayed=False):
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        QTUtil2.message(self.main_window, mens, titulo=titulo, px=p.x(), py=p.y(), delayed=delayed)

    def mensaje(self, mens, titulo=None, delayed=False):
        QTUtil2.message_bold(self.main_window, mens, titulo, delayed=delayed)

    def show_analysis(self):
        um = self.procesador.unMomento()
        elos = self.game.calc_elos(self.configuration)
        elosFORM = self.game.calc_elosFORM(self.configuration)
        alm = Histogram.genHistograms(self.game)
        (
            alm.indexesHTML,
            alm.indexesHTMLelo,
            alm.indexesHTMLmoves,
            alm.indexesRAW,
            alm.eloW,
            alm.eloB,
            alm.eloT,
        ) = AnalysisIndexes.gen_indexes(self.game, elos, elosFORM, alm)
        alm.is_white_bottom = self.board.is_white_bottom
        um.final()
        if len(alm.lijg) == 0:
            QTUtil2.message(self.main_window, _("There are no analyzed moves."))
        else:
            WindowAnalysisGraph.showGraph(self.main_window, self, alm, Analysis.show_analysis)

    def save_db(self, database):
        try:
            pgn = self.listado("pgn")
            liTags = []
            for linea in pgn.split("\n"):
                if linea.startswith("["):
                    ti = linea.split('"')
                    if len(ti) == 3:
                        key = ti[0][1:].strip()
                        valor = ti[1].strip()
                        liTags.append([key, valor])
                else:
                    break
        except AttributeError:
            liTags = []

        pc = Game.Game(li_tags=liTags)
        pc.assign_other_game(self.game)

        db = DBgames.DBgames(database)
        resp = db.insert(pc)
        db.close()
        if resp:
            QTUtil2.message_bold(self.main_window, _("Saved") + ": " + db.nom_fichero)
        else:
            QTUtil2.message_error(self.main_window, _("This game already exists."))

    def save_lcsb(self):
        if self.game_type == GT_ALONE and hasattr(self, "grabarComo"):
            return getattr(self, "grabarComo")()

        dic = dict(GAME=self.game.save(True))
        extension = "lcsb"
        file = self.configuration.x_save_lcsb
        while True:
            file = SelectFiles.salvaFichero(self.main_window, _("File to save"), file, extension, False)
            if file:
                file = str(file)
                if os.path.isfile(file):
                    yn = QTUtil2.preguntaCancelar(
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
                    QTUtil2.mensajeTemporal(self.main_window, _X(_("Saved to %1"), name), 0.8)
                    return
                else:
                    QTUtil2.message_error(self.main_window, "%s: %s" % (_("Unable to save"), name))

            break

    def save_pgn(self):
        w = WindowSavePGN.WSave(self.main_window, self.game, self.configuration)
        w.exec_()

    def save_pgn_clipboard(self):
        QTUtil.ponPortapapeles(self.game.pgn())
        QTUtil2.message_bold(self.main_window, _("PGN is in clipboard"))

    def save_fen(self, siFichero):
        dato = self.listado("fen")
        if siFichero:
            extension = "fns"
            resp = SelectFiles.salvaFichero(
                self.main_window, _("File to save"), self.configuration.x_save_folder, extension, False
            )
            if resp:
                try:

                    modo = "w"
                    if Util.exist_file(resp):
                        yn = QTUtil2.preguntaCancelar(
                            self.main_window,
                            _X(_("The file %1 already exists, what do you want to do?"), resp),
                            si=_("Append"),
                            no=_("Overwrite"),
                        )
                        if yn is None:
                            return
                        if yn:
                            modo = "a"
                            dato = "\n" * 2 + dato
                    with open(resp, modo, encoding="utf-8", errors="ignore") as q:
                        q.write(dato.replace("\n", "\r\n"))
                    QTUtil2.message_bold(self.main_window, _X(_("Saved to %1"), resp))
                    direc = os.path.dirname(resp)
                    if direc != self.configuration.x_save_folder:
                        self.configuration.x_save_folder = direc
                        self.configuration.graba()
                except:
                    QTUtil.ponPortapapeles(dato)
                    QTUtil2.message_error(
                        self.main_window,
                        "%s : %s\n\n%s"
                        % (_("Unable to save"), resp, _("It is saved in the clipboard to paste it wherever you want.")),
                    )

        else:
            QTUtil.ponPortapapeles(dato)

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
            pgn += p.pgnBaseRAW()
            pgn = pgn.replace("|", "-")

            siguientes = ""
            if nj < len(self.game) - 1:
                p = self.game.copiaDesde(nj + 1)
                siguientes = p.pgnBaseRAW(p.first_position.num_moves).replace("|", "-")

            txt = "%s||%s|%s\n" % (fen, siguientes, pgn)
            QTUtil.ponPortapapeles(txt)
            QTUtil2.mensajeTemporal(
                self.main_window, _("It is saved in the clipboard to paste it wherever you want."), 2
            )

    def tablasPlayer(self):
        # Para elo games + entmaq
        siAcepta = False
        nplies = len(self.game)
        if len(self.lirm_engine) >= 4 and nplies > 40:
            if nplies > 100:
                limite = -50
            elif nplies > 60:
                limite = -100
            else:
                limite = -150
            siAcepta = True
            for rm in self.lirm_engine[-3:]:
                if rm.centipawns_abs() > limite:
                    siAcepta = False
            if not siAcepta:
                si_ceros = True
                for rm in self.lirm_engine[-3:]:
                    if abs(rm.centipawns_abs()) > 15:
                        si_ceros = False
                        break
                if si_ceros:
                    mrm = self.xtutor.analiza(self.game.last_position.fen(), None, 7)
                    rm = mrm.mejorMov()
                    if abs(rm.centipawns_abs()) < 15:
                        siAcepta = True
        if siAcepta:
            self.game.last_jg().is_draw_agreement = True
            self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
        else:
            QTUtil2.message_bold(self.main_window, _("Sorry, but the engine doesn't accept a draw right now."))
        self.next_test_resign = 5
        return siAcepta

    def valoraRMrival(self):
        if len(self.game) < 50 or len(self.lirm_engine) <= 5:
            return True
        if self.next_test_resign:
            self.next_test_resign -= 1
            return True
        b = random.random() ** 0.33

        # Resign
        siResign = True
        for n, rm in enumerate(self.lirm_engine[-5:]):
            if int(rm.centipawns_abs() * b) > self.resign_limit:
                siResign = False
                break
        if siResign:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 wants to resign, do you accept it?"), self.xrival.name))
            if resp:
                self.game.resign(self.is_engine_side_white)
                return False
            else:
                self.next_test_resign = 9
                return True

        # # Draw
        siDraw = True
        for rm in self.lirm_engine[-5:]:
            pts = rm.centipawns_abs()
            if (not (-250 < int(pts * b) < -100)) or pts < -250:
                siDraw = False
                break
        if siDraw:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 proposes draw, do you accept it?"), self.xrival.name))
            if resp:
                self.game.last_jg().is_draw_agreement = True
                self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
                return False
            else:
                self.next_test_resign = 9
                return True

        return True

    def utilidadesElo(self):
        if self.is_competitive:
            self.utilities(siArbol=False)
        else:
            liMasOpciones = (("books", _("Consult a book"), Iconos.Libros()),)

            resp = self.utilities(liMasOpciones, siArbol=True)
            if resp == "books":
                liMovs = self.librosConsulta(True)
                if liMovs:
                    for x in range(len(liMovs) - 1, -1, -1):
                        from_sq, to_sq, promotion = liMovs[x]
                        self.player_has_moved_base(from_sq, to_sq, promotion)

    def pgnInformacionMenu(self):
        menu = QTVarios.LCMenu(self.main_window)

        for key, valor in self.game.dicTags().items():
            siFecha = key.upper().endswith("DATE")
            if key.upper() == "FEN":
                continue
            if siFecha:
                valor = valor.replace(".??", "").replace(".?", "")
            valor = valor.strip("?")
            if valor:
                menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())

        menu.lanza()

    def saveSelectedPosition(self, lineaTraining):
        # Llamado from_sq ManagerEnPos and ManagerEntTac, para salvar la position tras pulsar una P
        with open(self.configuration.ficheroSelectedPositions, "at", encoding="utf-8", errors="ignore") as q:
            q.write(lineaTraining + "\n")
        QTUtil2.mensajeTemporal(
            self.main_window, _('Position saved in "%s" file.') % self.configuration.ficheroSelectedPositions, 2
        )
        self.procesador.entrenamientos.menu = None

    def play_current_position(self):
        row, column = self.main_window.pgnPosActual()
        num_moves, nj, row, is_white = self.jugadaActual()
        self.game.is_finished()
        if row == 0 and column.key == "NUMBER" or nj == -1:
            gm = self.game.copia(0)
            gm.li_moves = []
            gm.is_finished()
        else:
            gm = self.game.copia(nj)
        gm.set_unknown()
        dic = {"GAME": gm.save(), "ISWHITE": gm.last_position.is_white}
        fich = Util.relative_path(self.configuration.ficheroTemporal("pkd"))
        Util.save_pickle(fich, dic)

        XRun.run_lucas("-play", fich)

    def showPV(self, pv, nArrows):
        if not pv:
            return True
        self.board.remove_arrows()
        tipo = "ms"
        opacity = 100
        pv = pv.strip()
        while "  " in pv:
            pv = pv.replace("  ", " ")
        lipv = pv.split(" ")
        npv = len(lipv)
        nbloques = min(npv, nArrows)
        salto = (80 - 15) * 2 / (nbloques - 1) if nbloques > 1 else 0
        cambio = max(30, salto)

        for n in range(nbloques):
            pv = lipv[n]
            self.board.creaFlechaMov(pv[:2], pv[2:4], tipo + str(opacity))
            if n % 2 == 1:
                opacity -= cambio
                cambio = salto
            tipo = "ms" if tipo == "mt" else "mt"
        return True

    def start_message(self, nomodal=False):
        mensaje = _("Press the continue button to start.")
        self.mensaje(mensaje, delayed=nomodal)

    def player_has_moved_base(self, from_sq, to_sq, promotion=""):
        if self.board.variation_history is not None:
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

        if not promotion and var_move.position_before.siPeonCoronando(from_sq, to_sq):
            promotion = self.board.peonCoronando(var_move.position_before.is_white)
            if promotion is None:
                return None
        else:
            promotion = ""

        movimiento = from_sq + to_sq + promotion

        if is_in_main_move:
            if var_move.movimiento() == movimiento:
                self.mueveJugada(GO_FORWARD)
                return
            else:
                position_before = var_move.position_before.copia()
                game_var = Game.Game(first_position=position_before)
                ok, mens, new_move = Move.get_game_move(game_var, position_before, from_sq, to_sq, promotion)
                if not ok:
                    return

                game_var.add_move(new_move)
                var_move.add_variation(game_var)

                self.main_window.activaInformacionPGN(True)
                row, column = self.main_window.pgnPosActual()
                is_white = var_move.position_before.is_white
                if is_white:
                    row += 1
                self.main_window.pgnColocate(row, is_white)
                self.put_view()
                link_variation_pressed("%d|%d|0" % (num_var_move, len(var_move.variations) - 1))
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
