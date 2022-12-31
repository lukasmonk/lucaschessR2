import gettext
_ = gettext.gettext
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
    TB_HELP,
    TB_NEXT,
    TB_UTILITIES,
    GT_ROUTES,
)
from Code.Endings import LibChess
from Code.Polyglots import Books
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.Routes import Routes


class GR_Engine:
    def __init__(self, procesador, nlevel):
        self._label = "%s - %s %d" % (_("Engine"), _("Level"), nlevel)
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
            return mrm.rmBest().movimiento()
        else:
            return FasterCode.run_fen(fen, 1, 0, 2)

    def elos(self):
        x = """stockfish 1284 1377 1377 1496
alaric 1154 1381 1813 2117
amyan 1096 1334 1502 1678
bikjump 1123 1218 1489 1572
cheng 1137 1360 1662 1714
chispa 1109 1180 1407 1711
clarabit 1119 1143 1172 1414
critter 1194 1614 1814 1897
discocheck 1138 1380 1608 1812
fruit 1373 1391 1869 1932
gaia 1096 1115 1350 1611
cyrano 1154 1391 1879 2123
garbochess 1146 1382 1655 1892
gaviota 1152 1396 1564 1879
greko 1158 1218 1390 1742
hamsters 1143 1382 1649 1899
komodo 1204 1406 1674 1891
lime 1143 1206 1493 1721
pawny 1096 1121 1333 1508
rhetoric 1131 1360 1604 1820
roce 1122 1150 1206 1497
umko 1120 1384 1816 1930
rybka 1881 2060 2141 2284
simplex 1118 1166 1411 1814
ufim 1189 1383 1928 2134
texel 1154 1387 1653 1874
toga 1236 1495 1928 2132"""
        d = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        def mas(engine, depth, celo):
            elo = int(celo)
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
            if engine in self.configuration.dic_engines:
                d[tp].append((engine, depth, elo))

        for line in x.split("\n"):
            engine, d1, d2, d3, d4 = line.split(" ")
            mas(engine, 1, d1)
            mas(engine, 2, d2)
            mas(engine, 3, d3)
            mas(engine, 4, d4)
        return d


class ManagerRoutes(Manager.Manager):
    def start(self, route):
        self.route = route
        if not hasattr(self, "time_start"):
            self.time_start = time.time()
        self.state = route.state

        self.game_type = GT_ROUTES

    def end_game(self):
        self.procesador.start()
        self.route.add_time(time.time() - self.time_start, self.state)

    def final_x(self):
        self.end_game()
        return False

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()


class ManagerRoutesPlay(ManagerRoutes):
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

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.remove_hints(True)

        self.set_label1(self.engine.label)
        if self.must_win:
            self.set_label2(_("You must win to pass this step."))

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.pgnRefresh(True)
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

        self.play_next_move()

    def end_game(self):
        self.engine.close()
        ManagerRoutes.end_game(self)

    def run_action(self, key):
        if key in (TB_CLOSE, TB_NEXT):
            self.end_game()
            self.procesador.showRoute()

        elif key == TB_REINIT:
            self.game.set_position()
            self.start(self.route)

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

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
                pv = self.book.eligeJugadaTipo(fen, "au")
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
                    QTUtil2.mensajeTemporal(self.main_window, _("Wrong move"), 2)
                    self.run_action(TB_REINIT)
                else:
                    QTUtil2.message_error(
                        self.main_window, "%s\n%s" % (_("Wrong move"), _("Right move: %s") % Game.pv_san(fen, op_pv))
                    )
                    self.sigueHumano()
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
        self.disable_all()
        self.human_is_playing = False
        self.state = ST_ENDGAME
        self.refresh()
        li_options = [TB_CLOSE, TB_UTILITIES, TB_NEXT]
        self.set_toolbar(li_options)
        jgUlt = self.game.last_jg()

        siwin = (jgUlt.is_white() == self.is_human_side_white) and not jgUlt.is_draw
        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beepResultado(beep)

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

        li_options = [TB_CLOSE, TB_HELP]
        self.set_toolbar(li_options)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.remove_hints(True)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.ponWarnings()

        self.pgnRefresh(True)
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
            self.end_game()
            self.procesador.showRoute()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_HELP:
            self.get_help()

        elif key == TB_NEXT:
            if self.route.km_pending():
                self.start(self.route)
            else:
                self.end_game()
                self.procesador.showRoute()

        elif key == TB_UTILITIES:
            self.utilities()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def end_game(self):
        if self.t4:
            self.t4.close()
        ManagerRoutes.end_game(self)

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
            self.human_is_playing = True
            self.activate_side(is_white)

    def show_error(self, mens):
        QTUtil2.mensajeTemporal(self.main_window, "   %s    " % mens, 1, background="#FF9B00", physical_pos="ad")

    def show_mens(self, mens):
        QTUtil2.mensajeTemporal(self.main_window, mens, 4, physical_pos="tb", background="#C3D6E8")

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
                self.sigueHumano()
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
                self.sigueHumano()
                return False

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
            QTUtil2.message_bold(self.main_window, mensaje)
            self.message_on_pgn(mensaje)
            self.start(self.route)

    def current_pgn(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgnBase()

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

        li_options = [TB_CLOSE, TB_HELP]
        self.set_toolbar(li_options)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.remove_hints(True)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)
        # self.set_label1("<b>%s</b>" % tactica.label)
        self.set_label2(route.mens_tactic(False))
        self.pgnRefresh(True)
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()
            self.procesador.showRoute()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_HELP:
            self.get_help()

        elif key == TB_NEXT:
            if self.route.km_pending():
                self.start(self.route)
            else:
                self.end_game()
                self.procesador.showRoute()

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

                    QTUtil2.mensajeTemporal(
                        self.main_window,
                        _("You have selected one correct move, but the line use %s") % jgObj.pgn_translated(),
                        3,
                        physical_pos="ad",
                    )
                    self.get_help(False)
                    self.sigueHumano()
                    return False
            QTUtil2.mensajeTemporal(self.main_window, _("Wrong move"), 0.8, physical_pos="ad")
            self.route.error_tactic(self.game_objetivo.num_moves())
            self.set_label2(self.route.mens_tactic(False))
            self.sigueHumano()
            return False

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

        resp += "\n" + self.game.pgnBase()

        return resp
