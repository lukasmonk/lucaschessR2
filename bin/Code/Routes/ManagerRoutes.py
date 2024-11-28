import random
import time

import FasterCode

import Code
from Code import Manager
from Code.Base import Game, Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_ADVICE,
    TB_NEXT,
    TB_UTILITIES,
    GT_ROUTES,
    BOOK_RANDOM_UNIFORM,
    TOP_RIGHT,
    ON_TOOLBAR,
)
from Code.Books import Books
from Code.Competitions import ManagerElo
from Code.Endings import LibChess
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.Routes import Routes
from Code.Translations import TrListas


class GR_Engine:
    def __init__(self, procesador, nlevel):
        self._label = "%s - %s" % (_("Engine"), TrListas.level(nlevel))
        self.configuration = procesador.configuration
        self.level = nlevel
        if nlevel == 0:
            self.manager = None
            self._name = self._label
        else:
            dEngines = self.elos()
            x = +1 if nlevel < 6 else -1
            while True:
                if len(dEngines[nlevel]) > 0:
                    nom_engine, depth, elo = random.choice(dEngines[nlevel])
                    break
                else:
                    nlevel += x
                    if nlevel > 6:
                        nlevel = 1
            rival = self.configuration.buscaRival(nom_engine)
            self.manager = procesador.creaManagerMotor(rival, None, depth)
            self._name = "%s %s %d" % (rival.name, _("Depth"), depth)
            self._label += "\n%s\n%s: %d" % (self._name, _("Estimated elo"), elo)

    def close(self):
        if self.manager and self.manager != self:
            self.manager.terminar()
            self.manager = None

    @property
    def label(self):
        return self._label

    @property
    def name(self):
        return self._name

    def play(self, fen):
        if self.manager:
            mrm = self.manager.analiza(fen)
            return mrm.rm_best().movimiento()
        else:
            return FasterCode.run_fen(fen, 1, 0, 2)

    def elos(self):

        d = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        def mas(nom_engine, xdepth, xelo):
            elo = int(xelo)
            if elo < 1100:
                tp = 1
            elif elo < 1200:
                tp = 2
            elif elo < 1400:
                tp = 3
            elif elo < 1700:
                tp = 4
            elif elo < 2000:
                tp = 5
            elif elo < 2200:
                tp = 6
            else:
                return
            if nom_engine in self.configuration.dic_engines:
                d[tp].append((nom_engine, xdepth, elo))

        li_engines = ManagerElo.listaMotoresElo()  # list (elo, key, depth)
        for elo, key, depth in li_engines:
            mas(key, depth, elo)
        return d


class ManagerRoutes(Manager.Manager):
    time_start: float = 0.0
    route = None
    route_state = 0

    def start(self, route):
        self.route = route
        self.route_state = route.state

        self.game_type = GT_ROUTES

    def ini_time(self):
        self.time_start = time.time()

    def add_time(self):
        if self.time_start:
            self.route.add_time(time.time() - self.time_start, self.route_state)
            self.time_start = 0

    def terminate(self):
        self.add_time()
        self.procesador.start()
        self.procesador.show_route()

    def final_x(self):
        self.terminate()
        return False

    def add_move(self, move, is_player):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()


class ManagerRoutesPlay(ManagerRoutes):
    engine = None

    def start(self, route):
        ManagerRoutes.start(self, route)

        line = route.get_line()

        opening = line.opening
        is_white = opening.is_white if opening.is_white is not None else random.choice([True, False])
        self.liPVopening = opening.pv.split(" ")
        self.posOpening = 0
        self.is_opening = len(opening.pv) > 0
        self.book = Books.Book("P", Code.tbookI, Code.tbookI, True)
        self.book.polyglot()

        if self.engine is None:
            self.engine = GR_Engine(self.procesador, line.engine)
        self.must_win = route.must_win()
        self.is_rival_thinking = False

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.set_activate_tutor(False)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_CONFIG, TB_REINIT]
        self.set_toolbar(li_options)

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True)

        self.set_label1(self.engine.label)
        if self.must_win:
            self.set_label2(_("You must win to pass this step."))

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.pgn_refresh(True)
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.game.set_tag("Event", _("Transsiberian Railway"))
        lbe = self.engine.name
        white, black = self.configuration.x_player, lbe
        if not self.is_human_side_white:
            white, black = black, white
        self.game.set_tag("White", white)
        self.game.set_tag("Black", black)

        self.game.add_tag_timestart()

        self.ini_time()
        self.play_next_move()

    def run_action(self, key):
        if key in (TB_CLOSE, TB_NEXT):
            self.add_time()
            self.procesador.start()
            self.procesador.show_route()

        elif key == TB_REINIT:
            self.add_time()
            self.game.set_position()
            self.start(self.route)

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        if self.game.is_finished():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            self.play_rival()
        else:
            self.human_is_playing = True
            self.activate_side(is_white)

    def play_rival(self):
        if self.is_opening:
            pv = self.liPVopening[self.posOpening]
            self.posOpening += 1
            if self.posOpening == len(self.liPVopening):
                self.is_opening = False
        else:
            fen = self.game.last_position.fen()
            pv = None
            if self.book:
                pv = self.book.eligeJugadaTipo(fen, BOOK_RANDOM_UNIFORM)
                if not pv:
                    self.book = None
            if not pv:
                if len(self.game.last_position) <= 4:
                    t4 = LibChess.T4(self.configuration)
                    pv = t4.best_move(fen)
                    t4.close()
                if not pv:
                    pv = self.engine.play(fen)

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, pv[:2], pv[2:4], pv[4:])
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.play_next_move()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jgSel = self.check_human_move(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        fen = self.game.last_position.fen()
        pv = jgSel.movimiento().lower()
        if self.is_opening:
            op_pv = self.liPVopening[self.posOpening]
            if pv != op_pv:
                if self.must_win:
                    QTUtil2.temporary_message(self.main_window, _("Wrong move"), 2)
                    self.run_action(TB_REINIT)
                else:
                    QTUtil2.message_error(
                        self.main_window, "%s\n%s" % (_("Wrong move"), _("Right move: %s") % Game.pv_san(fen, op_pv))
                    )
                    self.continue_human()
                return False
            self.posOpening += 1
            if self.posOpening == len(self.liPVopening):
                self.is_opening = False

        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.play_next_move()
        return True

    def lineaTerminada(self):
        self.add_time()
        self.disable_all()
        self.human_is_playing = False
        self.state = ST_ENDGAME
        self.refresh()
        li_options = [TB_CLOSE, TB_UTILITIES, TB_NEXT]
        self.set_toolbar(li_options)
        jgUlt = self.game.last_jg()

        siwin = (jgUlt.is_white() == self.is_human_side_white) and not jgUlt.is_draw
        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beep_result(beep)

        self.autosave()

        if siwin:
            if self.route.end_playing():
                mensaje = _("Congratulations, you have completed the game.")
            else:
                mensaje = _("Well done")
            self.message_on_pgn(mensaje)
        else:
            if self.must_win:
                QTUtil2.message_error(self.main_window, _("You must win to pass this step."))
                li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES, TB_REINIT]
                self.set_toolbar(li_options)
            else:
                QTUtil2.message(self.main_window, mensaje)
                self.route.end_playing()


class ManagerRoutesEndings(ManagerRoutes):
    def start(self, route):
        ManagerRoutes.start(self, route)

        ending = self.route.get_ending()
        if "|" in ending:
            self.is_guided = True
            self.t4 = None
            self.fen, label, pv = ending.split("|")
            self.li_pv = pv.split(" ")
            self.posPV = 0
        else:
            self.is_guided = False
            self.t4 = LibChess.T4(self.configuration)
            self.fen = ending + " - - 0 1"

        self.is_rival_thinking = False

        cp = Position.Position()
        cp.read_fen(self.fen)

        is_white = cp.is_white

        self.game.set_position(cp)
        self.game.pending_opening = False

        self.warnings = 0
        self.max_warnings = 5

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.set_activate_tutor(False)
        self.remove_hints(True)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_ADVICE]
        self.set_toolbar(li_options)

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.ponWarnings()

        self.pgn_refresh(True)
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        if self.is_guided:
            self.set_label1("<b>%s</b>" % label)

        self.play_next_move()

    def ponWarnings(self):
        if self.warnings <= self.max_warnings:
            self.set_label2(_("Warnings: %d/%d") % (self.warnings, self.max_warnings))
        else:
            self.set_label2(_("You must repeat the puzzle."))

    def run_action(self, key):
        if key in (TB_CLOSE, TB_NEXT):
            self.terminate()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=True)

        elif key == TB_ADVICE:
            self.get_help()

        elif key == TB_NEXT:
            self.add_time()
            if self.route.km_pending():
                self.start(self.route)
            else:
                self.end_game()

        elif key == TB_UTILITIES:
            self.utilities()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def terminate(self):
        if self.t4:
            self.t4.close()
        ManagerRoutes.terminate(self)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        if self.game.is_finished():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            if self.is_guided:
                pv = self.li_pv[self.posPV].split("-")[0]
                self.posPV += 1
            else:
                fen = self.game.last_position.fen()
                pv = self.t4.best_move(fen)
            self.rival_has_moved(pv[:2], pv[2:4], pv[4:])
            self.play_next_move()
        else:
            self.ini_time()
            self.human_is_playing = True
            self.activate_side(is_white)

    def show_error(self, mens):
        QTUtil2.temporary_message(self.main_window, "   %s    " % mens, 1, background="#FF9B00", physical_pos=TOP_RIGHT)

    def show_mens(self, mens):
        QTUtil2.temporary_message(self.main_window, mens, 4, physical_pos=ON_TOOLBAR, background="#C3D6E8")

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jgSel = self.check_human_move(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        if self.is_guided:
            pvSel = jgSel.movimiento().lower()
            pvObj = self.li_pv[self.posPV]
            li = pvObj.split("-")
            if li[0] != pvSel:
                if pvSel in li:
                    pgn = Game.pv_pgn(jgSel.position_before.fen(), pvObj)
                    self.show_mens(_("You have selected one correct move, but the line use %s") % pgn)
                    self.put_arrow_sc(pvObj[:2], pvObj[2:4])
                    self.get_help(False)
                else:
                    self.show_error(_("Wrong move"))
                    self.warnings += 1
                    self.ponWarnings()
                self.continue_human()
                return False
            self.posPV += 1
        else:
            fen = self.game.last_position.fen()
            pv = jgSel.movimiento().lower()
            b_wdl = self.t4.wdl(fen)
            m_wdl = self.t4.wdl_move(fen, pv)

            if b_wdl != m_wdl:
                self.show_error(_("Wrong move"))
                self.warnings += 1
                self.ponWarnings()
                self.set_position(self.game.last_position)
                self.continue_human()
                return False

        self.add_time()
        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.play_next_move()
        return True

    def rival_has_moved(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        return True

    def get_help(self, siWarning=True):
        if self.is_guided:
            pvObj = self.li_pv[self.posPV]
            li = pvObj.split("-")
        else:
            li = self.t4.better_moves(self.game.last_position.fen(), None)
        liMovs = [(pv[:2], pv[2:4], n == 0) for n, pv in enumerate(li)]
        self.board.ponFlechasTmp(liMovs)
        if siWarning:
            self.warnings += self.max_warnings
            self.ponWarnings()

    def lineaTerminada(self):
        self.add_time()
        self.disable_all()
        self.human_is_playing = False
        self.state = ST_ENDGAME
        self.refresh()

        jgUlt = self.game.last_jg()
        if jgUlt.is_draw:
            mensaje = "%s<br>%s" % (_("Draw"), _("You must repeat the puzzle."))
            self.message_on_pgn(mensaje)
            self.start(self.route)
        elif self.warnings <= self.max_warnings:
            self.set_toolbar([TB_CLOSE, TB_UTILITIES, TB_NEXT])
            self.message_on_pgn(_("Done"))
            self.route.end_ending()
        else:
            mensaje = "%s<br>%s" % (_("Done with errors."), _("You must repeat the puzzle."))
            self.message_on_pgn(mensaje)
            self.start(self.route)

    def current_pgn(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgn_base()

        return resp


class ManagerRoutesTactics(ManagerRoutes):
    def start(self, route):
        ManagerRoutes.start(self, route)

        tactica = self.route.get_tactic()

        self.game_objetivo = Game.fen_game(tactica.fen, tactica.pgn)

        self.is_rival_thinking = False

        cp = Position.Position()
        cp.read_fen(tactica.fen)

        self.fen = tactica.fen

        is_white = cp.is_white

        self.game.set_position(cp)
        self.game.pending_opening = False

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.set_activate_tutor(False)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_ADVICE]
        self.set_toolbar(li_options)

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)
        self.set_label2(route.mens_tactic(False))
        self.pgn_refresh(True)
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.terminate()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=True)

        elif key == TB_ADVICE:
            self.get_help()

        elif key == TB_NEXT:
            if self.route.km_pending():
                self.start(self.route)
            else:
                self.terminate()

        elif key == TB_UTILITIES:
            self.utilities()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def jugadaObjetivo(self):
        return self.game_objetivo.move(self.game.num_moves())

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        if len(self.game) == self.game_objetivo.num_moves():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            move = self.jugadaObjetivo()
            self.rival_has_moved(move.from_sq, move.to_sq, move.promotion)
            self.play_next_move()
        else:
            self.ini_time()
            self.human_is_playing = True
            self.activate_side(is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jgSel = self.check_human_move(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        jgObj = self.jugadaObjetivo()
        if jgObj.movimiento() != jgSel.movimiento():
            for variation in jgObj.variations.li_variations:
                jgObjV = variation.move(0)
                if jgObjV.movimiento() == jgSel.movimiento():
                    QTUtil2.temporary_message(
                        self.main_window,
                        _("You have selected one correct move, but the line use %s") % jgObj.pgn_translated(),
                        3,
                        physical_pos=TOP_RIGHT,
                    )
                    self.get_help(False)
                    self.continue_human()
                    return False
            QTUtil2.temporary_message(self.main_window, _("Wrong move"), 0.8, physical_pos=TOP_RIGHT)
            self.route.error_tactic(self.game_objetivo.num_moves())
            self.set_label2(self.route.mens_tactic(False))
            self.continue_human()
            return False

        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.add_time()

        self.play_next_move()
        return True

    def rival_has_moved(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        return True

    def get_help(self, siQuitarPuntos=True):
        jgObj = self.jugadaObjetivo()
        liMovs = [(jgObj.from_sq, jgObj.to_sq, True)]
        for variation in jgObj.variations.li_variations:
            jg0 = variation.move(0)
            liMovs.append((jg0.from_sq, jg0.to_sq, False))
        self.board.ponFlechasTmp(liMovs)
        if siQuitarPuntos:
            self.route.error_tactic(self.game_objetivo.num_moves())
            self.set_label2(self.route.mens_tactic(False))

    def lineaTerminada(self):
        self.disable_all()
        self.refresh()
        km = self.route.end_tactic()
        if not self.route.go_fast:
            mensaje = "%s<br>%s" % (_("Done"), _("You have traveled %s") % Routes.km_mi(km, self.route.is_miles))
            self.message_on_pgn(mensaje)
        self.human_is_playing = False
        self.state = ST_ENDGAME
        if self.route.go_fast:
            self.run_action(TB_NEXT)
        else:
            li_options = [TB_CLOSE, TB_UTILITIES, TB_NEXT]
            self.set_toolbar(li_options)
            self.set_label2(self.route.mens_tactic(True))

    def current_pgn(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgn_base()

        return resp
