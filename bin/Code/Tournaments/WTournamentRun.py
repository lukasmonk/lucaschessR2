import gettext
_ = gettext.gettext
import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import CPU
from Code import ControlPGN
from Code import Util
from Code.Sound import Sound
from Code.Base import Game, Move
from Code.Base.Constantes import (
    ST_PLAYING,
    RESULT_DRAW,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    ST_WAITING,
    TERMINATION_ADJUDICATION,
    BLACK,
    WHITE,
    ST_PAUSE,
    TERMINATION_UNKNOWN,
    TERMINATION_WIN_ON_TIME,
)
from Code.Board import Board
from Code.Engines import EngineManager
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.SQL import UtilSQL
from Code.Tournaments import Tournament
from Code import TimeControl


class TournamentRun:
    def __init__(self, file_tournament):
        self.file_tournament = file_tournament
        with self.tournament() as torneo:
            self.run_name = torneo.name()
            self.run_drawRange = torneo.draw_range()
            self.run_drawMinPly = torneo.draw_min_ply()
            self.run_resign = torneo.resign()
            self.run_bookDepth = torneo.bookDepth()

    def name(self):
        return self.run_name

    def draw_range(self):
        return self.run_drawRange

    def draw_min_ply(self):
        return self.run_drawMinPly

    def resign(self):
        return self.run_resign

    def bookDepth(self):
        return self.run_bookDepth

    def tournament(self):
        return Tournament.Tournament(self.file_tournament)

    def get_game_queued(self, file_work, times=0):
        with self.tournament() as torneo:
            self.run_name = torneo.name()
            self.run_drawRange = torneo.draw_range()
            self.run_drawMinPly = torneo.draw_min_ply()
            self.run_resign = torneo.resign()
            self.run_bookDepth = torneo.bookDepth()
            game_tournament = torneo.get_game_queued(file_work)
            return game_tournament

    def fenNorman(self):
        with self.tournament() as torneo:
            return torneo.fenNorman()

    def slow_pieces(self):
        with self.tournament() as torneo:
            return torneo.slow_pieces()

    def adjudicator_active(self):
        with self.tournament() as torneo:
            return torneo.adjudicator_active()

    def adjudicator(self):
        with self.tournament() as torneo:
            return torneo.adjudicator()

    def adjudicator_time(self):
        with self.tournament() as torneo:
            return torneo.adjudicator_time()

    def buscaHEngine(self, h):
        with self.tournament() as torneo:
            return torneo.buscaHEngine(h)

    def book(self):
        with self.tournament() as torneo:
            return torneo.book()

    def game_done(self, game):
        with self.tournament() as torneo:
            return torneo.game_done(game)

    def close(self):
        pass


class WTournamentRun(QtWidgets.QWidget):
    tc_white: TimeControl
    tc_black: TimeControl

    def __init__(self, file_tournament, file_work):
        QtWidgets.QWidget.__init__(self)

        Code.list_engine_managers = EngineManager.ListEngineManagers()
        self.torneo = TournamentRun(file_tournament)  # Tournament.Tournament(file_tournament)
        self.file_work = file_work
        self.db_work = UtilSQL.ListSQL(file_work)

        self.slow_pieces = self.torneo.slow_pieces()

        self.setWindowTitle("%s - %s %d" % (self.torneo.name(), _("Worker"), int(file_work[-5:])))
        self.setWindowIcon(Iconos.Torneos())

        # Toolbar
        self.tb = QTVarios.LCTB(self, icon_size=24)

        # Board
        conf_board = Code.configuration.config_board("TOURNEYPLAY", 36)
        self.board = Board.Board(self, conf_board)
        self.board.crea()
        Delegados.generaPM(self.board.piezas)

        ct = self.board.config_board
        self.antiguoAnchoPieza = ct.anchoPieza()

        # PGN
        self.configuration = Code.configuration
        self.game = Game.Game()
        self.pgn = ControlPGN.ControlPGN(self)
        ly_pgn = self.crea_bloque_informacion()

        self.is_closed = False
        self.state = None
        self.current_side = WHITE

        ly_tt = Colocacion.V().control(self.tb).control(self.board)

        layout = Colocacion.H().otro(ly_tt).otro(ly_pgn).relleno().margen(3)
        self.setLayout(layout)

        self.cpu = CPU.CPU(self)

        self.pon_estado(ST_WAITING)

    def pon_estado(self, state):
        self.state = state
        self.pon_toolbar(state)

    def pon_toolbar(self, state):
        li_acciones = [(_("Close"), Iconos.Close(), self.close), None]
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
        self.grid_pgn.tipoLetra(puntos=configuration.x_pgn_fontpoints)
        self.grid_pgn.ponAltoFila(configuration.x_pgn_rowheight)

        # # Blancas y negras
        f = Controles.TipoLetra(puntos=configuration.x_sizefont_infolabels + 2, peso=75)
        alto_lb = 48
        self.lb_player = {}
        for side in (WHITE, BLACK):
            self.lb_player[side] = Controles.LB(self).anchoFijo(n_ancho_labels).altoFijo(alto_lb)
            self.lb_player[side].align_center().ponFuente(f).set_wrap()
            self.lb_player[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)

        self.lb_player[WHITE].setProperty("type", "white")
        self.lb_player[BLACK].setProperty("type", "black")

        # Relojes
        f = Controles.TipoLetra("Arial Black", puntos=26, peso=75)

        self.lb_clock = {}
        for side in (WHITE, BLACK):
            self.lb_clock[side] = (
                Controles.LB(self, "00:00")
                .ponFuente(f)
                .align_center()
                .anchoMinimo(n_ancho_labels)
            )
            self.lb_clock[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
            self.lb_clock[side].setProperty("type", "clock")

        # Rotulos de informacion
        f = Controles.TipoLetra(puntos=configuration.x_sizefont_infolabels)
        self.lbRotulo3 = Controles.LB(self).set_wrap().ponFuente(f)

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
        if self.torneo:
            self.tournament_game = self.torneo.get_game_queued(self.file_work)
            if self.tournament_game is None:
                return
            self.procesa_game()
            if not self.is_closed:
                self.looking_for_work()

    def procesa_game(self):
        self.pon_estado(ST_PLAYING)

        # Configuración
        self.fen_inicial = self.torneo.fenNorman()

        # Cerramos los motores anteriores si los hay
        Code.list_engine_managers.close_all()

        if self.torneo.adjudicator_active():
            conf_engine = Code.configuration.buscaRival(self.torneo.adjudicator())
            self.xadjudicator = EngineManager.EngineManager(self, conf_engine)
            self.xadjudicator.options(self.torneo.adjudicator_time() * 1000, 0, False)
            self.xadjudicator.remove_multipv()
        else:
            self.xadjudicator = None
        self.next_control = 0

        self.max_seconds = self.tournament_game.minutos * 60.0
        self.seconds_per_move = self.tournament_game.seconds_per_move

        # abrimos motores
        rival = {
            WHITE: self.torneo.buscaHEngine(self.tournament_game.hwhite),
            BLACK: self.torneo.buscaHEngine(self.tournament_game.hblack),
        }
        for side in (WHITE, BLACK):
            self.lb_player[side].set_text(rival[side].key)

        self.book = {}
        self.bookRR = {}

        self.xengine = {}

        for side in (WHITE, BLACK):
            rv = rival[side]
            self.xengine[side] = EngineManager.EngineManager(self, rv)
            self.xengine[side].options(rv.time * 1000, rv.depth, False)
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
            self.bookRR[side] = rv.bookRR

        self.game = Game.Game(fen=self.fen_inicial)
        self.pgn.game = self.game

        self.lbRotulo3.altoFijo(32)

        self.board.disable_all()
        self.board.set_position(self.game.last_position)
        self.grid_pgn.refresh()

        self.tc_white = TimeControl.TimeControl(self, self.game, WHITE)
        self.tc_white.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
        self.tc_white.set_labels()
        self.tc_black = TimeControl.TimeControl(self, self.game, BLACK)
        self.tc_black.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
        self.tc_black.set_labels()

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
        self.game.set_tag("Event", self.torneo.name())

        hoy = Util.today()
        self.game.set_tag("Date", "%d.%02d.%02d" % (hoy.year, hoy.month, hoy.day))

        motor_white = self.xengine[WHITE].confMotor
        motor_black = self.xengine[BLACK].confMotor
        self.game.set_tag("White", motor_white.name)
        self.game.set_tag("Black", motor_black.name)
        if motor_white.elo:
            self.game.set_tag("WhiteElo", motor_white.elo)
        if motor_black.elo:
            self.game.set_tag("BlackElo", motor_black.elo)

        time_control = "%d" % int(self.max_seconds)
        if self.seconds_per_move:
            time_control += "+%d" % self.seconds_per_move
        self.game.set_tag("TimeControl", time_control)

        self.game.set_extend_tags()
        self.game.sort_tags()

        self.tournament_game.result = self.game.result
        self.tournament_game.game_save = self.game.save(True)
        self.torneo.game_done(self.tournament_game)

    def terminar(self):
        self.is_closed = True
        if self.torneo:
            Code.list_engine_managers.close_all()
            self.torneo.close()
            self.db_work.close()
            self.torneo = None
            self.db_work = None
            Util.remove_file(self.file_work)

    def closeEvent(self, event):
        self.terminar()

    def pausa(self):
        self.pon_estado(ST_PAUSE)

    def seguir(self):
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
        tc.stop()
        tc.set_labels()

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

    def select_book_move(self, book, tipo):
        bdepth = self.torneo.bookDepth()
        if bdepth == 0 or len(self.game) < bdepth:
            fen = self.game.last_fen()
            pv = book.eligeJugadaTipo(fen, tipo)
            if pv:
                return True, pv[:2], pv[2:4], pv[4:]
        return False, None, None, None

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

    def showPV(self, pv, nArrows):
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
            self.board.creaFlechaMov(pv[:2], pv[2:4], tipo + str(opacity))
            if n % 2 == 1:
                opacity -= cambio
                cambio = salto
            tipo = "ms" if tipo == "mt" else "mt"
        return True

    def play_next_move(self):
        if self.test_is_finished():
            return False

        self.current_side = is_white = self.game.is_white()

        self.board.set_side_indicator(is_white)

        move_found = False
        analysis = None
        bk = self.book[is_white]
        if bk:
            move_found, from_sq, to_sq, promotion = self.select_book_move(bk, self.bookRR[is_white])
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
                self.pause_clock(is_white)
                self.board.borraMovibles()
                return True
            self.stop_clock(is_white)
            if mrm is None:
                return False
            rm = mrm.mejorMov()
            from_sq = rm.from_sq
            to_sq = rm.to_sq
            promotion = rm.promotion
            analysis = mrm, 0

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if not move:
            return False
        if analysis:
            move.analysis = analysis
            move.del_nags()
        self.add_move(move)
        self.sound(move)

        self.move_the_pieces(move.liMovs)

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

        pgn = move.pgnFigurinesSP() if self.configuration.x_pgn_withfigurines else move.pgn_translated()

        return pgn, color, info, indicador_inicial, stNAGS

    def gui_dispatch(self, rm):
        if self.is_closed or self.state != ST_PLAYING:
            return False
        if not rm.sinInicializar:
            p = Game.Game(self.game.last_position)
            p.read_pv(rm.pv)
            rm.is_white = self.game.last_position.is_white
            txt = "<b>[%s]</b> (%s) %s" % (rm.name, rm.abrTexto(), p.pgn_translated())
            self.lbRotulo3.set_text(txt)
            self.showPV(rm.pv, 1)
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
        if num_moves == 0:
            return False

        if self.state != ST_PLAYING or self.is_closed or self.game_finished() or self.game.is_finished():
            return True

        if num_moves < 2:
            return False

        self.next_control -= 1
        if self.next_control > 0 and self.xadjudicator:
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
        dr = self.torneo.draw_range()
        if dr > 0 and num_moves >= self.torneo.draw_min_ply():
            if abs(pUlt) <= dr and abs(pAnt) <= dr:
                if self.xadjudicator:
                    mrmTut = self.xadjudicator.analiza(self.game.last_position.fen())
                    rmTut = mrmTut.mejorMov()
                    pTut = rmTut.centipawns_abs()
                    if abs(pTut) <= dr:
                        self.game.set_termination(TERMINATION_ADJUDICATION, RESULT_DRAW)
                        return True
                    return False
                else:
                    self.game.set_termination(TERMINATION_ADJUDICATION, RESULT_DRAW)
                    return True

        # Resign
        rs = self.torneo.resign()
        if 0 < rs <= abs(pUlt):
            if self.xadjudicator:
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
            else:
                if rs <= abs(pAnt):
                    if (pAnt > 0 and pUlt > 0) or (pAnt < 0 and pUlt < 0):
                        result = RESULT_WIN_WHITE if pUlt > 0 else RESULT_WIN_BLACK
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
                        dist = (dc**2 + df**2) ** 0.5
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
            self.antiguoAnchoPieza = 1000 if ant.maximizado else ct.anchoPieza()
            self.board.maximizaTam(True)
        else:
            if ant.fullscreen:
                self.base.tb.show()
                self.board.normalTam(self.antiguoAnchoPieza)
                self.ajustaTam()
                if self.antiguoAnchoPieza == 1000:
                    self.setWindowState(QtCore.Qt.WindowMaximized)
            elif nue.maximizado:
                self.antiguoAnchoPieza = ct.anchoPieza()
                self.board.maximizaTam(False)
            elif ant.maximizado:
                if not self.antiguoAnchoPieza or self.antiguoAnchoPieza == 1000:
                    self.antiguoAnchoPieza = self.board.calculaAnchoMXpieza()
                self.board.normalTam(self.antiguoAnchoPieza)
                self.ajustaTam()

    def ajustaTam(self):
        QTUtil.shrink(self)
