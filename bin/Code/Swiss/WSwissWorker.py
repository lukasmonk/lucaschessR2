import sqlite3
import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import CPU
from Code import ControlPGN
from Code import TimeControl
from Code import Util
from Code.Base import Game, Move
from Code.Base.Constantes import (
    BLACK,
    WHITE,
    ST_PLAYING,
    ST_WAITING,
    ST_PAUSE,
    RESULT_DRAW,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    TERMINATION_UNKNOWN,
    TERMINATION_WIN_ON_TIME,
    TERMINATION_ADJUDICATION,
    TERMINATION_ENGINE_MALFUNCTION,
    ENG_WICKER,
)
from Code.Board import Board
from Code.Books import Books
from Code.Engines import EngineManager, EnginesWicker, EngineResponse
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.Sound import Sound
from Code.Swiss import SwissWork, Swiss


class WSwissWorker(QtWidgets.QWidget):
    tc_white: TimeControl.TimeControl
    tc_black: TimeControl.TimeControl

    def __init__(self, name_swiss):
        QtWidgets.QWidget.__init__(self)

        Code.list_engine_managers = EngineManager.ListEngineManagers()
        self.swiss = Swiss.Swiss(name_swiss)
        self.swiss_work = SwissWork.SwissWork(self.swiss)

        self.slow_pieces = self.swiss.slow_pieces

        self.setWindowTitle("%s - %s" % (self.swiss.name(), _("Worker")))
        self.setWindowIcon(Iconos.Swiss())

        self.tb = QTVarios.LCTB(self, icon_size=24)

        conf_board = Code.configuration.config_board("SWISSPLAY", 36)
        self.board = Board.Board(self, conf_board)
        self.board.crea()
        Delegados.genera_pm(self.board.piezas)

        ct = self.board.config_board
        self.antiguoAnchoPieza = ct.width_piece()

        self.configuration = Code.configuration
        self.game = Game.Game()
        self.pgn = ControlPGN.ControlPGN(self)
        ly_pgn = self.crea_bloque_informacion()

        self.is_closed = False
        self.state = None
        self.current_side = WHITE
        self.next_control = 0

        ly_tt = Colocacion.V().control(self.tb).control(self.board)

        layout = Colocacion.H().otro(ly_tt).otro(ly_pgn).relleno().margen(3)
        self.setLayout(layout)

        self.cpu = CPU.CPU(self)

        self.pon_estado(ST_WAITING)

    def pon_estado(self, state):
        self.state = state
        self.pon_toolbar(state)

    def pon_toolbar(self, state):
        li_acciones = [(_("Cancel"), Iconos.Cancelar(), self.cancel_match), None]
        if state == ST_PLAYING:
            li_acciones.extend(
                [
                    (_("Pause"), Iconos.Pause(), self.pausa),
                    None,
                    (_("Adjudication"), Iconos.EndGame(), self.adjudication),
                    None,
                ]
            )
        elif state == ST_PAUSE:
            li_acciones.extend(
                [
                    (_("Continue"), Iconos.Continue(), self.seguir),
                    None,
                    (_("Adjudication"), Iconos.EndGame(), self.adjudication),
                    None,
                ]
            )
        self.tb.reset(li_acciones)

    def crea_bloque_informacion(self):
        configuration = Code.configuration
        n_ancho_pgn = configuration.x_pgn_width
        n_ancho_color = (n_ancho_pgn - 52 - 24) // 2
        n_ancho_labels = max(int((n_ancho_pgn - 3) // 2), 140)
        # # Pgn
        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("NUMBER", _("N."), 52, align_center=True)
        with_figurines = configuration.x_pgn_withfigurines
        o_columnas.nueva(
            "WHITE", _("White"), n_ancho_color, edicion=Delegados.EtiquetaPGN(True if with_figurines else None)
        )
        o_columnas.nueva(
            "BLACK", _("Black"), n_ancho_color, edicion=Delegados.EtiquetaPGN(False if with_figurines else None)
        )
        self.grid_pgn = Grid.Grid(self, o_columnas, siCabeceraMovible=False)
        self.grid_pgn.setMinimumWidth(n_ancho_pgn)
        self.grid_pgn.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.grid_pgn.font_type(puntos=configuration.x_pgn_fontpoints)
        self.grid_pgn.ponAltoFila(configuration.x_pgn_rowheight)

        # # Blancas y negras
        f = Controles.FontType(puntos=configuration.x_sizefont_players, peso=500)
        self.lb_player = {}
        for side in (WHITE, BLACK):
            self.lb_player[side] = Controles.LB(self).anchoFijo(n_ancho_labels)
            self.lb_player[side].align_center().set_font(f).set_wrap()
            self.lb_player[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)

        self.configuration.set_property(self.lb_player[WHITE], "white")
        self.configuration.set_property(self.lb_player[BLACK], "black")

        # Relojes
        f = Controles.FontType("Arial Black", puntos=26, peso=75)

        self.lb_clock = {}
        for side in (WHITE, BLACK):
            self.lb_clock[side] = (
                Controles.LB(self, "00:00")
                .set_font(f)
                .align_center()
                .anchoMinimo(n_ancho_labels)
            )
            self.lb_clock[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
            self.configuration.set_property(self.lb_clock[side], "clock")

        # Rotulos de informacion
        f = Controles.FontType(puntos=configuration.x_pgn_fontpoints)
        self.lbRotulo3 = Controles.LB(self).set_wrap().set_font(f)

        # Layout
        lyColor = Colocacion.G()
        lyColor.controlc(self.lb_player[WHITE], 0, 0).controlc(self.lb_player[BLACK], 0, 1)
        lyColor.controlc(self.lb_clock[WHITE], 1, 0).controlc(self.lb_clock[BLACK], 1, 1)

        # Abajo
        lyAbajo = Colocacion.V()
        lyAbajo.setSizeConstraint(lyAbajo.SetFixedSize)
        lyAbajo.control(self.lbRotulo3)

        lyV = Colocacion.V().otro(lyColor).control(self.grid_pgn)
        lyV.otro(lyAbajo).margen(7)

        return lyV

    def grid_num_datos(self, grid):
        return self.pgn.num_rows()

    def looking_for_work(self):
        try:
            self.xmatch = self.swiss_work.get_other_match()
        except sqlite3.IntegrityError:
            self.xmatch = None
        if self.xmatch is None:
            return
        self.procesa_match()
        if not self.is_closed:
            self.looking_for_work()

    def procesa_match(self):
        self.pon_estado(ST_PLAYING)

        # Cerramos los motores anteriores si los hay
        Code.list_engine_managers.close_all()

        if self.swiss.adjudicator_active:
            conf_engine = Code.configuration.buscaRival(self.swiss.adjudicator)
            self.xadjudicator = EngineManager.EngineManager(conf_engine)
            self.xadjudicator.options(self.swiss.adjudicator_time * 1000, 0, False)
            self.xadjudicator.remove_multipv()
        else:
            self.xadjudicator = None
        self.next_control = 0

        max_minute, self.seconds_per_move = self.swiss.time_engine_engine
        self.max_seconds = max_minute * 60

        # abrimos motores
        rival = {
            WHITE: self.swiss.opponent_by_xid(self.xmatch.xid_white),
            BLACK: self.swiss.opponent_by_xid(self.xmatch.xid_black),
        }
        for side in (WHITE, BLACK):
            self.lb_player[side].set_text(rival[side].name())

        self.book = {}
        self.book_rr = {}
        self.book_max_plies = {}

        self.xengine = {}

        for side in (WHITE, BLACK):
            opponent = rival[side]
            rv = opponent.element
            if rv.type == ENG_WICKER:
                xmanager = EnginesWicker.EngineManagerWicker(rv)
            else:
                xmanager = EngineManager.EngineManager(rv)
            self.xengine[side] = xmanager
            self.xengine[side].set_gui_dispatch(self.gui_dispatch)

            bk = rv.book
            if bk == "*":
                bk = self.torneo.book()
            if bk == "-":  # Puede que el torneo tenga "-"
                bk = None
            if bk:
                self.book[side] = Books.Book("P", bk, bk, True)
                self.book[side].polyglot()
            else:
                self.book[side] = None
            self.book_rr[side] = rv.book_rr
            self.book_max_plies[side] = rv.book_max_plies

        self.game = Game.Game()
        self.pgn.game = self.game

        self.tc_white = TimeControl.TimeControl(self, self.game, WHITE)
        self.tc_white.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
        self.tc_white.set_labels()
        self.tc_black = TimeControl.TimeControl(self, self.game, BLACK)
        self.tc_black.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
        self.tc_black.set_labels()

        h_max = 0
        for side in (WHITE, BLACK):
            h = self.lb_player[side].height()
            if h > h_max:
                h_max = h
        for side in (WHITE, BLACK):
            self.lb_player[side].altoFijo(h_max)

        time_control = "%d" % int(self.max_seconds)
        if self.seconds_per_move:
            time_control += "+%d" % self.seconds_per_move
        self.game.set_tag("TimeControl", time_control)

        self.board.disable_all()
        self.board.set_position(self.game.last_position)
        self.grid_pgn.refresh()

        while self.state == ST_PAUSE or self.play_next_move():
            if self.state == ST_PAUSE:
                QTUtil.refresh_gui()
                time.sleep(0.1)
            if self.is_closed:
                break
        for side in (WHITE, BLACK):
            self.xengine[side].terminar()

        if not self.is_closed:
            if self.game_finished():
                self.save_game_done()

    def save_game_done(self):
        self.game.set_tag("Site", Code.lucas_chess)
        self.game.set_tag("Event", self.swiss_work.nom_swiss)
        self.game.set_tag("Season", str(self.swiss.current_num_season + 1))
        journey = self.swiss_work.get_journey_match(self.xmatch)
        self.game.set_tag("Round", str(journey + 1))

        hoy = Util.today()
        self.game.set_tag("Date", "%d.%02d.%02d" % (hoy.year, hoy.month, hoy.day))

        engine_white = self.xengine[WHITE].confMotor
        engine_black = self.xengine[BLACK].confMotor
        self.game.set_tag("White", engine_white.name)
        self.game.set_tag("Black", engine_black.name)
        if engine_white.elo:
            self.game.set_tag("WhiteElo", engine_white.elo)
        if engine_black.elo:
            self.game.set_tag("BlackElo", engine_black.elo)

        self.game.set_extend_tags()
        self.game.sort_tags()

        self.swiss_work.put_match_done(self.xmatch, self.game)

    def terminar(self):
        self.is_closed = True
        Code.list_engine_managers.close_all()

    def cancel_match(self):
        self.is_closed = True
        Code.list_engine_managers.close_all()
        self.swiss_work.cancel_match(self.xmatch.xid)

    def closeEvent(self, event):
        self.terminar()

    def pausa(self):
        self.pause_clock(self.current_side)
        self.pon_estado(ST_PAUSE)

    def seguir(self):
        self.start_clock(self.current_side)
        self.pon_estado(ST_PLAYING)

    def adjudication(self):
        self.pon_estado(ST_PAUSE)
        QTUtil.refresh_gui()
        menu = QTVarios.LCMenu(self)
        menu.opcion(RESULT_DRAW, RESULT_DRAW, Iconos.Tablas())
        menu.separador()
        menu.opcion(RESULT_WIN_WHITE, RESULT_WIN_WHITE, Iconos.Blancas())
        menu.separador()
        menu.opcion(RESULT_WIN_BLACK, RESULT_WIN_BLACK, Iconos.Negras())
        resp = menu.lanza()
        if resp is not None:
            self.game.set_termination(TERMINATION_ADJUDICATION, resp)
            self.save_game_done()

    def set_clock(self):
        if self.is_closed or self.game_finished():
            return False

        tc = self.tc_white if self.current_side == WHITE else self.tc_black
        tc.set_labels()
        if tc.time_is_consumed():
            self.game.set_termination_time()
            return False

        QTUtil.refresh_gui()
        return True

    def start_clock(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        tc.start()

    def stop_clock(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        secs = tc.stop()
        tc.set_labels()
        return secs

    def pause_clock(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        tc.pause()
        tc.set_labels()

    def restart_clock(self, is_white):
        tc = self.tc_white if is_white else self.tc_black
        tc.restart()
        tc.set_labels()

    def set_clock_label(self, side, tm, tm2):
        if tm2 is not None:
            tm += '<br><FONT SIZE="-4">' + tm2
        self.lb_clock[side].set_text(tm)

    def set_clock_white(self, tm, tm2):
        self.set_clock_label(WHITE, tm, tm2)

    def set_clock_black(self, tm, tm2):
        self.set_clock_label(BLACK, tm, tm2)

    def add_move(self, move):
        self.game.add_move(move)

        self.board.borraMovibles()
        self.board.put_arrow_sc(move.from_sq, move.to_sq)
        self.grid_pgn.refresh()
        self.grid_pgn.gobottom(2 if self.game.last_position.is_white else 1)

        self.refresh()

    def refresh(self):
        self.board.escena.update()
        self.update()
        QTUtil.refresh_gui()

    def game_finished(self):
        return self.game.termination != TERMINATION_UNKNOWN

    def show_pv(self, pv, nArrows):
        if not pv:
            return True
        self.board.remove_arrows()
        tipo = "mt"
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
            self.board.show_arrow_mov(pv[:2], pv[2:4], tipo, opacity=opacity / 100)
            if n % 2 == 1:
                opacity -= cambio
                cambio = salto
            tipo = "ms" if tipo == "mt" else "mt"
        return True

    def select_book_move(self, book, tipo, bdepth):
        if bdepth == 0 or len(self.game) < bdepth:
            fen = self.game.last_fen()
            pv = book.eligeJugadaTipo(fen, tipo)
            if pv:
                rm_rival = EngineResponse.EngineResponse("Opening", self.game.last_position.is_white)
                rm_rival.from_sq = pv[:2]
                rm_rival.to_sq = pv[2:4]
                rm_rival.promotion = pv[4:]
                return True, rm_rival
        return False, None

    def play_next_move(self):
        if self.test_is_finished():
            return False

        self.current_side = is_white = self.game.is_white()

        self.board.set_side_indicator(is_white)

        move_found = False
        analysis = None
        rm = None
        time_seconds = None
        clock_seconds = None

        bk = self.book[is_white]
        if bk:
            move_found, rm = self.select_book_move(bk, self.book_rr[is_white], self.book_max_plies[is_white])
            if not move_found:
                self.book[is_white] = None

        if not move_found:
            xrival = self.xengine[is_white]
            time_pending_white = self.tc_white.pending_time
            time_pending_black = self.tc_black.pending_time
            self.start_clock(is_white)
            if xrival.depth_engine and xrival.depth_engine > 0:
                mrm = xrival.play_fixed_depth_time_tourney(self.game)
            else:
                mrm = xrival.play_time_tourney(self.game, time_pending_white, time_pending_black, self.seconds_per_move)
            if self.state == ST_PAUSE:
                self.board.borraMovibles()
                return True
            time_seconds = self.stop_clock(is_white)
            clock_seconds = self.tc_white.pending_time if is_white else self.tc_black.pending_time
            if mrm is None:
                self.sudden_end(is_white)
                return True
            rm = mrm.best_rm_ordered()
            analysis = mrm, 0

        from_sq = rm.from_sq
        to_sq = rm.to_sq
        promotion = rm.promotion

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if not move:
            self.sudden_end(is_white)
            return True

        if analysis:
            move.analysis = analysis
            move.del_nags()

        if time_seconds:
            move.set_time_ms(time_seconds * 1000.0)
        if clock_seconds:
            move.set_clock_ms(clock_seconds * 1000.0)
        self.add_move(move)
        self.move_the_pieces(move.liMovs)
        self.sound(move)

        return True

    def sound(self, move):
        if self.configuration.x_sound_tournements:
            if not Code.runSound:
                runSound = Sound.RunSound()
            else:
                runSound = Code.runSound
            if self.configuration.x_sound_move:
                runSound.play_list(move.listaSonidos())
            if self.configuration.x_sound_beep:
                runSound.playBeep()

    def sudden_end(self, is_white):
        result = RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE
        self.game.set_termination(TERMINATION_ENGINE_MALFUNCTION, result)

    def grid_dato(self, grid, row, o_column):
        controlPGN = self.pgn

        col = o_column.key
        if col == "NUMBER":
            return controlPGN.dato(row, col)

        move = controlPGN.only_move(row, col)
        if move is None:
            return ""

        color = None
        info = ""
        indicador_inicial = None

        stNAGS = set()

        if move.analysis:
            mrm, pos = move.analysis
            rm = mrm.li_rm[pos]
            mate = rm.mate
            si_w = move.position_before.is_white
            if mate:
                if mate == 1:
                    info = ""
                else:
                    if not si_w:
                        mate = -mate
                    info = "M%+d" % mate
            else:
                pts = rm.puntos
                if not si_w:
                    pts = -pts
                info = "%+0.2f" % float(pts / 100.0)

            nag, color_nag = mrm.set_nag_color(rm)
            stNAGS.add(nag)

        if move.in_the_opening:
            indicador_inicial = "R"

        pgn = move.pgn_figurines() if self.configuration.x_pgn_withfigurines else move.pgn_translated()

        return pgn, color, info, indicador_inicial, stNAGS

    def gui_dispatch(self, rm):
        if self.is_closed or self.state != ST_PLAYING:
            return False
        if not rm.sinInicializar:
            p = Game.Game(self.game.last_position)
            p.read_pv(rm.pv)
            rm.is_white = self.game.last_position.is_white
            txt = "<b>[%s]</b> (%s) %s" % (rm.name, rm.abbrev_text(), p.pgn_translated())
            self.lbRotulo3.set_text(txt)
            self.show_pv(rm.pv, 1)
        return self.set_clock()

    def clocks_finished(self):
        if self.tc_white.time_is_consumed():
            self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK)
            return True
        if self.tc_black.time_is_consumed():
            self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_WHITE)
            return True
        return False

    def test_is_finished(self):
        if self.clocks_finished():
            return True

        num_moves = len(self.game)
        if num_moves < 2:
            return False

        if self.state != ST_PLAYING or self.is_closed or self.game_finished() or self.game.is_finished():
            return True

        self.next_control -= 1
        if self.next_control > 0:
            return False
        self.next_control = 20

        last_jg = self.game.last_jg()
        if not last_jg.analysis:
            return False
        mrm, pos = last_jg.analysis
        rmUlt = mrm.li_rm[pos]
        jgAnt = self.game.move(-2)
        if not jgAnt.analysis:
            return False
        mrm, pos = jgAnt.analysis
        rmAnt = mrm.li_rm[pos]

        # Draw
        pUlt = rmUlt.centipawns_abs()
        pAnt = rmAnt.centipawns_abs()
        dr = self.swiss.draw_range
        if dr > 0 and num_moves >= self.swiss.draw_min_ply:
            if abs(pUlt) <= dr and abs(pAnt) <= dr:
                mrmTut = self.xadjudicator.analiza(self.game.last_position.fen())
                rmTut = mrmTut.best_rm_ordered()
                pTut = rmTut.centipawns_abs()
                if abs(pTut) <= dr:
                    self.game.set_termination(TERMINATION_ADJUDICATION, RESULT_DRAW)
                    return True
                return False

        # Resign
        rs = self.swiss.resign
        if 0 < rs <= abs(pUlt):
            rmTut = self.xadjudicator.play_game(self.game)
            pTut = rmTut.centipawns_abs()
            if abs(pTut) >= rs:
                is_white = self.game.last_position.is_white
                if pTut > 0:
                    result = RESULT_WIN_WHITE if is_white else RESULT_WIN_BLACK
                else:
                    result = RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE
                self.game.set_termination(TERMINATION_ADJUDICATION, result)
                return True

        return False

    def move_the_pieces(self, liMovs):
        if self.slow_pieces:

            rapidez = self.configuration.pieces_speed_porc()
            cpu = self.cpu
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
                        dist = (dc ** 2 + df ** 2) ** 0.5
                        seconds = 4.0 * dist / (9.9 * rapidez)
                    cpu.muevePieza(movim[1], movim[2], siExclusiva=False, seconds=seconds)

            if seconds is None:
                seconds = 1.0

            # segundo los borrados
            for movim in liMovs:
                if movim[0] == "b":
                    n = cpu.duerme(seconds * 0.80 / rapidez)
                    cpu.borraPieza(movim[1], padre=n)

            # tercero los cambios
            for movim in liMovs:
                if movim[0] == "c":
                    cpu.cambiaPieza(movim[1], movim[2], siExclusiva=True)

            cpu.runLineal()

        else:
            for movim in liMovs:
                if movim[0] == "b":
                    self.board.borraPieza(movim[1])
                elif movim[0] == "m":
                    self.board.muevePieza(movim[1], movim[2])
                elif movim[0] == "c":
                    self.board.cambiaPieza(movim[1], movim[2])

    def changeEvent(self, event):
        QtWidgets.QWidget.changeEvent(self, event)
        if event.type() != QtCore.QEvent.WindowStateChange:
            return

        nue = QTUtil.EstadoWindow(self.windowState())
        ant = QTUtil.EstadoWindow(event.oldState())

        ct = self.board.config_board

        if nue.fullscreen:
            self.board.siF11 = True
            self.antiguoAnchoPieza = 1000 if ant.maximizado else ct.width_piece()
            self.board.maximize_size(True)
        else:
            if ant.fullscreen:
                self.base.tb.show()
                self.board.normal_size(self.antiguoAnchoPieza)
                self.adjust_size()
                if self.antiguoAnchoPieza == 1000:
                    self.setWindowState(QtCore.Qt.WindowMaximized)
            elif nue.maximizado:
                self.antiguoAnchoPieza = ct.width_piece()
                self.board.maximize_size(False)
            elif ant.maximizado:
                if not self.antiguoAnchoPieza or self.antiguoAnchoPieza == 1000:
                    self.antiguoAnchoPieza = self.board.calc_width_mx_piece()
                self.board.normal_size(self.antiguoAnchoPieza)
                self.adjust_size()

    def adjust_size(self):
        QTUtil.shrink(self)
