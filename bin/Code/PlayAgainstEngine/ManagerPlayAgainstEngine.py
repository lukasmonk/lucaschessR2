import os
import time

import FasterCode
from PySide2 import QtCore

import Code
from Code import Adjournments
from Code import Manager
from Code import Util
from Code.Analysis import Analysis
from Code.Base import Game, Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_CONTINUE,
    TB_DRAW,
    TB_PAUSE,
    TB_QUIT,
    TB_RESIGN,
    TB_STOP,
    TB_UTILITIES,
    GT_AGAINST_ENGINE,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    TERMINATION_RESIGN,
    TERMINATION_WIN_ON_TIME,
    WHITE,
    BLACK,
    ADJUST_BETTER,
    ADJUST_SELECTED_BY_PLAYER,
    ST_PAUSE,
    ENG_ELO,
    MISTAKE,
    BOOK_BEST_MOVE,
    SELECTED_BY_PLAYER
)
from Code.Books import Books, WBooks
from Code.Engines import EngineResponse
from Code.Openings import Opening, OpeningLines
from Code.PlayAgainstEngine import WPlayAgainstEngine, Personalities
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Tutor import Tutor
from Code.Voyager import Voyager


class ManagerPlayAgainstEngine(Manager.Manager):
    reinicio = None
    cache = None
    is_analyzing = False

    tc_player = None
    tc_rival = None

    summary = None
    with_summary = False
    is_engine_side_white = False
    conf_engine = None
    lirm_engine = None
    next_test_resign = 0
    opening_mandatory = None
    primeroBook = False
    book_player = None
    book_player_active = False
    book_player_depth = 0
    book_rival = None
    book_rival_active = False
    book_rival_select = None
    book_rival_depth = 0
    is_tutor_enabled = False
    nArrows = 0
    thoughtOp = -1
    thoughtTt = -1
    continueTt = False
    nArrowsTt = 0
    chance = True
    tutor_con_flechas = False
    tutor_book = None
    nAjustarFuerza = 0
    resign_limit = -99999
    siBookAjustarFuerza = True
    timed = False
    max_seconds = 0
    segundosJugada = 0
    secs_extra = 0
    nodes = 0
    zeitnot = 0
    is_analyzed_by_tutor = False
    toolbar_state = None
    premove = None
    last_time_show_arrows = None
    rival_is_thinking = False
    humanize = False
    unlimited_minutes = 5
    is_human_side_white: bool
    opening_line = None
    play_while_win = None
    limit_pww = 90
    dic_reject = {"opening_line": 0, "book_rival": 0, "book_player": 0}
    cache_analysis = {}
    with_takeback = True
    seconds_per_move = 0
    mrm_tutor = None

    def start(self, dic_var):
        self.base_inicio(dic_var)
        if self.timed:
            if self.hints:
                self.xtutor.check_engine()
            self.xrival.check_engine()
            self.start_message(nomodal=Code.eboard and Code.is_linux)  # nomodal: problema con eboard

        self.play_next_move()

    def base_inicio(self, dic_var):
        self.reinicio = dic_var

        self.cache = dic_var.get("cache", {})
        self.cache_analysis = dic_var.get("cache_analysis", {})

        self.game_type = GT_AGAINST_ENGINE

        self.human_is_playing = False
        self.rival_is_thinking = False
        self.state = ST_PLAYING
        self.is_analyzing = False

        self.summary = {}  # movenum : "a"ccepted, "s"ame, "r"ejected, dif points, time used
        self.with_summary = dic_var.get("SUMMARY", False)

        is_white = dic_var["ISWHITE"]
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.conf_engine = dic_var["RIVAL"].get("CM", None)

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -99999  # never

        self.opening_mandatory = None

        self.fen = dic_var["FEN"]
        if self.fen:
            cp = Position.Position()
            cp.read_fen(self.fen)
            self.game.set_position(cp)
            self.game.pending_opening = False

        if dic_var["OPENING"]:
            self.opening_mandatory = Opening.JuegaOpening(dic_var["OPENING"].a1h8)
            self.primeroBook = False  # la opening es obligatoria

        self.opening_line = None
        if dic_var["OPENING_LINE"]:
            dic_op = dic_var["OPENING_LINE"]
            path = self.configuration.folder_base_openings
            if "folder" in dic_op:
                path = Util.opj(path, dic_op["folder"])
            path = Util.opj(path, dic_op["file"])
            if os.path.isfile(path):
                self.opening_line = OpeningLines.Opening(path).dic_fenm2_moves()

        self.book_rival_active = False
        self.book_rival = dic_var.get("BOOKR", None)
        if self.book_rival:
            self.book_rival_active = True
            self.book_rival_depth = dic_var.get("BOOKRDEPTH", 0)
            self.book_rival.polyglot()
            self.book_rival_select = dic_var.get("BOOKRR", BOOK_BEST_MOVE)
        elif self.conf_engine.book:
            self.book_rival_active = True
            self.book_rival = Books.Book("P", self.conf_engine.book, self.conf_engine.book, True)
            self.book_rival.polyglot()
            self.book_rival_select = BOOK_BEST_MOVE
            self.book_rival_depth = getattr(self.conf_engine, "book_max_plies", 0)

        self.book_player_active = False
        self.book_player = dic_var.get("BOOKP", None)
        if self.book_player:
            self.book_player_active = True
            self.book_player_depth = dic_var.get("BOOKPDEPTH", 0)
            self.book_player.polyglot()

        self.is_tutor_enabled = self.configuration.x_default_tutor_active
        self.main_window.set_activate_tutor(self.is_tutor_enabled)

        self.hints = dic_var["HINTS"]
        self.ayudas_iniciales = self.hints  # Se guarda para guardar el PGN
        self.nArrows = dic_var.get("ARROWS", 0)
        n_box_height = dic_var.get("BOXHEIGHT", 24)
        self.thoughtOp = dic_var.get("THOUGHTOP", -1)
        self.thoughtTt = dic_var.get("THOUGHTTT", -1)
        self.continueTt = not Code.configuration.x_engine_notbackground
        self.nArrowsTt = dic_var.get("ARROWSTT", 0)
        self.chance = dic_var.get("2CHANCE", True)

        self.play_while_win = dic_var.get("WITH_LIMIT_PWW", False)
        self.limit_pww = dic_var.get("LIMIT_PWW", 90)

        self.humanize = dic_var.get("HUMANIZE", False)
        # if dic_var.get("ANALYSIS_BAR", False):
        #     self.main_window.activate_analysis_bar(True)

        if dic_var.get("ACTIVATE_EBOARD"):
            Code.eboard.activate(self.board.dispatch_eboard)

        if self.nArrowsTt != 0 and self.hints == 0:
            self.nArrowsTt = 0

        self.last_time_show_arrows = time.time() - 2.0

        self.with_takeback = dic_var.get("TAKEBACK", True)

        self.tutor_con_flechas = self.nArrowsTt > 0 and self.hints > 0
        self.tutor_book = Books.BookGame(Code.tbook)

        mx = max(self.thoughtOp, self.thoughtTt)
        if mx > -1:
            self.set_hight_label3(n_box_height)

        dr = dic_var["RIVAL"]
        rival = dr["CM"]
        self.unlimited_minutes = dr.get("ENGINE_UNLIMITED", 5)

        if dr["TYPE"] == ENG_ELO:
            r_t = 0
            r_p = rival.max_depth
            self.nAjustarFuerza = ADJUST_BETTER

        else:
            r_t = dr["ENGINE_TIME"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["ENGINE_DEPTH"]
            self.nAjustarFuerza = dic_var.get("ADJUST", ADJUST_BETTER)

        self.nodes = dr.get("ENGINE_NODES", 0)

        if not self.xrival:  # reiniciando is not None
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic_var["WITHTIME"]:
                r_t = None
            rival.liUCI = dr["LIUCI"]
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, self.nAjustarFuerza != ADJUST_BETTER)
            if self.nodes:
                self.xrival.set_nodes(self.nodes)
            if self.nAjustarFuerza != ADJUST_BETTER:
                self.xrival.maximize_multipv()
        self.resign_limit = dic_var["RESIGN"]

        self.game.set_tag("Event", _("Play against an engine"))

        player = self.configuration.nom_player()
        other = self.xrival.name
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.siBookAjustarFuerza = self.nAjustarFuerza != ADJUST_BETTER

        self.xrival.is_white = self.is_engine_side_white

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black

        self.timed = dic_var["WITHTIME"]
        self.tc_white.set_displayed(self.timed)
        self.tc_black.set_displayed(self.timed)
        if self.timed:
            self.max_seconds = dic_var["MINUTES"] * 60.0
            self.seconds_per_move = dic_var["SECONDS"]
            secs_extra = dic_var.get("MINEXTRA", 0) * 60.0
            zeitnot = dic_var.get("ZEITNOT", 0)

            self.tc_player.config_clock(self.max_seconds, self.seconds_per_move, zeitnot, secs_extra)
            self.tc_rival.config_clock(self.max_seconds, self.seconds_per_move, zeitnot, 0)

            time_control = "%d" % int(self.max_seconds)
            if self.seconds_per_move:
                time_control += "+%d" % self.seconds_per_move
            self.game.set_tag("TimeControl", time_control)
            if secs_extra:
                self.game.set_tag("TimeExtra" + ("White" if self.is_human_side_white else "Black"), "%d" % secs_extra)

        self.pon_toolbar()

        self.main_window.active_game(True, self.timed)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        if self.ayudas_iniciales:
            self.show_hints()
        else:
            self.remove_hints(siQuitarAtras=False)
        self.put_pieces_bottom(is_white)

        self.show_basic_label()
        self.set_label2("")

        if self.nAjustarFuerza != ADJUST_BETTER:
            pers = Personalities.Personalities(None, self.configuration)
            label = pers.label(self.nAjustarFuerza)
            if label:
                self.game.set_tag("Strength", label)

        self.show_info_extra()

        self.pgn_refresh(True)

        rival = self.xrival.name
        player = self.configuration.x_player
        bl, ng = player, rival
        if self.is_engine_side_white:
            bl, ng = ng, bl

        if self.timed:
            tp_bl, tp_ng = self.tc_white.label(), self.tc_black.label()

            self.main_window.set_data_clock(bl, tp_bl, ng, tp_ng)
            self.refresh()
        else:
            self.main_window.base.change_player_labels(bl, ng)

        self.main_window.start_clock(self.set_clock, 1000)

        self.main_window.set_notify(self.mueve_rival_base)

        self.is_analyzed_by_tutor = False
        if self.play_while_win:
            self.is_tutor_enabled = True

        self.game.add_tag_timestart()

        self.check_boards_setposition()

    def pon_toolbar(self):
        if self.state == ST_PLAYING:
            if self.toolbar_state != self.state:
                li = [
                    TB_CANCEL,
                    TB_RESIGN,
                    TB_DRAW,
                    TB_REINIT,
                    TB_PAUSE,
                    TB_ADJOURN,
                    TB_CONFIG,
                    TB_UTILITIES,
                    TB_STOP,
                ]
                if self.with_takeback:
                    li.insert(3, TB_TAKEBACK)

                self.set_toolbar(li)
            hip = self.human_is_playing
            self.main_window.enable_option_toolbar(TB_RESIGN, hip)
            self.main_window.enable_option_toolbar(TB_DRAW, hip)
            self.main_window.enable_option_toolbar(TB_TAKEBACK, hip)
            self.main_window.enable_option_toolbar(TB_PAUSE, hip)
            self.main_window.enable_option_toolbar(TB_CONFIG, hip)
            self.main_window.enable_option_toolbar(TB_UTILITIES, hip)
            self.main_window.enable_option_toolbar(TB_STOP, not hip)
            self.main_window.enable_option_toolbar(TB_ADJOURN, hip)

        elif self.state == ST_PAUSE:
            li = [TB_CONTINUE]
            self.set_toolbar(li)
        else:
            li = [TB_CLOSE]
            self.set_toolbar(li)

        self.toolbar_state = self.state

    def show_basic_label(self):
        rotulo1 = ""
        if self.book_rival_active:
            rotulo1 += "<br>%s-%s: <b>%s</b>" % (_("Book"), _("Opponent"), os.path.basename(self.book_rival.name))
        if self.book_player_active:
            rotulo1 += "<br>%s-%s: <b>%s</b>" % (_("Book"), _("Player"), os.path.basename(self.book_player.name))
        self.set_label1(rotulo1)

    def show_time(self, is_player):
        tc = self.tc_player if is_player else self.tc_rival
        tc.set_labels()

    def set_clock(self):
        if self.state == ST_ENDGAME:
            self.main_window.stop_clock()
            return
        if self.state != ST_PLAYING:
            return

        if self.human_is_playing:
            if self.is_analyzing:
                mrm = self.xtutor.ac_estado()
                if mrm:
                    rm = mrm.best_rm_ordered()
                    if self.nArrowsTt > 0:
                        if time.time() - self.last_time_show_arrows > 3.4:
                            self.last_time_show_arrows = time.time()
                            self.show_pv(rm.pv, self.nArrowsTt)
                    if self.thoughtTt > -1:
                        self.show_dispatch(self.thoughtTt, rm)
        elif self.thoughtOp > -1 or self.nArrows > 0:
            rm = self.xrival.current_rm()
            if rm:
                if self.nArrows:
                    if time.time() - self.last_time_show_arrows > 3.4:
                        self.last_time_show_arrows = time.time()
                        self.show_pv(rm.pv, self.nArrows)
                if self.thoughtOp > -1:
                    self.show_dispatch(self.thoughtOp, rm)

        if self.timed:
            if Code.eboard:
                Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

            is_white = self.game.last_position.is_white
            is_player = self.is_human_side_white == is_white

            tc = self.tc_player if is_player else self.tc_rival
            tc.set_labels()

            if tc.time_is_consumed():
                t = time.time()
                if is_player and QTUtil2.pregunta(
                        self.main_window,
                        _X(_("%1 has won on time."), self.xrival.name) + "\n\n" + _("Add time and keep playing?"),
                ):
                    min_x = WPlayAgainstEngine.dameMinutosExtra(self.main_window)
                    if min_x:
                        more = time.time() - t
                        tc.add_extra_seconds(min_x * 60 + more)
                        tc.set_labels()
                        return
                self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE)
                self.state = ST_ENDGAME  # necesario que esté antes de stop_clock para no entrar en bucle
                self.stop_clock(is_player)
                self.show_result()
                return

            elif is_player and tc.is_zeitnot():
                self.beep_zeitnot()

    def stop_clock(self, is_player):
        tc = self.tc_player if is_player else self.tc_rival
        time_s = tc.stop()
        self.show_time(is_player)
        return time_s

    def run_action(self, key):
        if key == TB_CANCEL:
            self.finalizar()

        elif key == TB_RESIGN:
            self.rendirse()

        elif key == TB_DRAW:
            if self.tablasPlayer():
                self.show_result()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_PAUSE:
            self.xpause()

        elif key == TB_CONTINUE:
            self.xcontinue()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            li_mas_opciones = []
            if self.state == ST_PLAYING and self.game_type == GT_AGAINST_ENGINE:
                li_mas_opciones.append((None, None, None))
                li_mas_opciones.append(("rival", _("Change opponent"), Iconos.Engine()))
                if len(self.game) > 0:
                    li_mas_opciones.append((None, None, None))
                    li_mas_opciones.append(("moverival", _("Change opponent move"), Iconos.TOLchange()))
            resp = self.configurar(li_mas_opciones, with_sounds=True, with_change_tutor=self.ayudas_iniciales > 0)
            if resp == "rival":
                self.change_rival()
            elif resp == "moverival":
                self.change_last_move_engine()

        elif key == TB_UTILITIES:
            li_mas_opciones = []
            if self.human_is_playing or self.is_finished():
                li_mas_opciones.append(("books", _("Consult a book"), Iconos.Libros()))
            li_mas_opciones.append(("start_position", _("Change the starting position"), Iconos.PGN()))

            resp = self.utilities(li_mas_opciones)
            if resp == "books":
                si_en_vivo = self.human_is_playing and not self.is_finished()
                li_movs = self.librosConsulta(si_en_vivo)
                if li_movs and si_en_vivo:
                    from_sq, to_sq, promotion = li_movs[-1]
                    self.player_has_moved(from_sq, to_sq, promotion)
            elif resp == "play":
                self.play_current_position()
            elif resp == "start_position":
                self.start_position()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key == TB_STOP:
            self.stop_engine()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def save_state(self):
        self.analyze_terminate()
        dic = self.reinicio

        # cache
        dic["cache"] = self.cache
        dic["cache_analysis"] = self.cache_analysis

        # game
        dic["game_save"] = self.game.save()

        # tiempos
        if self.timed:
            self.main_window.stop_clock()
            dic["time_white"] = self.tc_white.save()
            dic["time_black"] = self.tc_black.save()

        dic["is_tutor_enabled"] = self.is_tutor_enabled

        dic["hints"] = self.hints
        dic["summary"] = self.summary

        return dic

    def restore_state(self, dic):
        self.base_inicio(dic)
        self.game.restore(dic["game_save"])

        if self.timed:
            self.tc_white.restore(dic["time_white"])
            self.tc_black.restore(dic["time_black"])

        self.is_tutor_enabled = dic["is_tutor_enabled"]
        self.hints = dic["hints"]
        self.summary = dic["summary"]
        self.goto_end()

    def close_position(self, key):
        self.main_window.deactivate_eboard(100)
        if key == TB_CLOSE:
            self.autosave_now()
            self.procesador.run_action(TB_QUIT)
        else:
            self.run_action(key)

    def play_position(self, dic, restore_game):
        self.ponRutinaAccionDef(self.close_position)
        game = Game.Game()
        game.restore(restore_game)
        player = self.configuration.nom_player()
        # dic["FEN"] = game.last_position.fen()
        self.base_inicio(dic)
        self.reinicio["play_position"] = dic, restore_game
        other = self.xrival.name
        w, b = (player, other) if self.is_human_side_white else (other, player)
        for tag, value in self.game.li_tags:
            if not game.get_tag(tag):
                game.set_tag(tag, value)
        game.add_tag_date()
        game.set_tag("White", w)
        game.set_tag("Black", b)
        game.add_tag_timestart()
        game.order_tags()
        self.game = game
        self.goto_end()
        self.play_next_move()

    def reiniciar(self, si_pregunta):
        if self.state == ST_ENDGAME and self.play_while_win:
            si_pregunta = False
        if si_pregunta:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
        if self.timed:
            self.main_window.stop_clock()
        self.analyze_terminate()
        if self.book_rival_select == SELECTED_BY_PLAYER or self.nAjustarFuerza == ADJUST_SELECTED_BY_PLAYER:
            self.cache = {}
        self.reinicio["cache"] = self.cache
        self.reinicio["cache_analysis"] = self.cache_analysis
        self.autosave_now()

        if "play_position" in self.reinicio:
            self.procesador.stop_engines()
            dic, restore_game = self.reinicio["play_position"]
            return self.play_position(dic, restore_game)

        self.game.reset()
        self.toolbar_state = ST_ENDGAME
        self.main_window.activaInformacionPGN(False)

        reinicio = self.reinicio.get("REINIT", 0) + 1
        self.game.set_tag("Reinit", str(reinicio))
        self.reinicio["REINIT"] = reinicio

        self.start(self.reinicio)

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            # se guarda en una bd Adjournments dic key = fecha y hora y tipo
            label_menu = _("Play against an engine") + ". " + self.xrival.name

            self.state = ST_ENDGAME

            self.finalizar()
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.ac_final(-1)

            bp = dic.get("BOOKP")
            if bp:
                bp.book = None
            br = dic.get("BOOKR")
            if br:
                br.book = None

            with Adjournments.Adjournments() as adj:
                if self.game_type == GT_AGAINST_ENGINE:
                    engine = dic["RIVAL"]["CM"]
                    if hasattr(engine, "ICON"):
                        delattr(engine, "ICON")
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        self.restore_state(dic)
        self.check_boards_setposition()
        if self.timed:
            self.show_clocks()
        if self.timed:
            if self.hints:
                self.xtutor.check_engine()
            self.xrival.check_engine()
            self.start_message()

        self.pgn_refresh(not self.is_engine_side_white)
        self.play_next_move()

    def xpause(self):
        is_white = self.game.last_position.is_white
        tc = self.tc_white if is_white else self.tc_black
        if is_white == self.is_human_side_white:
            tc.pause()
        else:
            tc.reset()
            self.stop_engine()
        tc.set_labels()
        self.state = ST_PAUSE
        self.thinking(False)
        if self.is_analyzing:
            self.is_analyzing = False
            self.xtutor.ac_final(-1)
        self.board.set_position(self.game.first_position)
        self.board.disable_all()
        self.main_window.hide_pgn()
        self.pon_toolbar()

    def xcontinue(self):
        self.state = ST_PLAYING
        self.board.set_position(self.game.last_position)
        self.pon_toolbar()
        self.main_window.show_pgn()
        self.play_next_move()

    def final_x(self):
        return self.finalizar()

    def stop_engine(self):
        if not self.human_is_playing:
            self.xrival.stop()

    def finalizar(self):
        if self.state == ST_ENDGAME:
            return True
        si_jugadas = len(self.game) > 0
        if si_jugadas:
            if not QTUtil2.pregunta(self.main_window, _("End game?")):
                return False  # no abandona
            if self.timed:
                self.main_window.stop_clock()
                self.show_clocks()
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.ac_final(-1)
            self.state = ST_ENDGAME
            self.stop_engine()
            self.game.set_unknown()
            self.set_end_game(self.with_takeback)
            self.autosave()
        else:
            if self.timed:
                self.main_window.stop_clock()
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.ac_final(-1)
            self.state = ST_ENDGAME
            self.stop_engine()
            self.main_window.active_game(False, False)
            self.quitaCapturas()
            if self.xRutinaAccionDef:
                self.xRutinaAccionDef(TB_CLOSE)
            else:
                self.procesador.start()

        return False

    def rendirse(self, with_question=True):
        if self.state == ST_ENDGAME:
            return True
        if self.timed:
            self.main_window.stop_clock()
            self.show_clocks()
        if len(self.game) > 0 or self.play_while_win:
            if with_question:
                if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
                    return False  # no abandona
            self.analyze_terminate()
            self.game.set_termination(
                TERMINATION_RESIGN, RESULT_WIN_WHITE if self.is_engine_side_white else RESULT_WIN_BLACK
            )
            self.saveSummary()
            if not self.play_while_win:
                self.set_end_game(self.with_takeback)
            if not self.play_while_win:
                self.autosave()
        else:
            self.analyze_terminate()
            self.main_window.active_game(False, False)
            self.quitaCapturas()
            self.procesador.start()

        return False

    def analyze_terminate(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.xtutor.ac_final(-1)

    def takeback(self):
        if len(self.game):
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.stop()
            if self.hints:
                self.hints -= 1
                self.tutor_con_flechas = self.nArrowsTt > 0 and self.hints > 0
            self.show_hints()
            self.game.anulaUltimoMovimiento(self.is_human_side_white)
            if not self.fen:
                self.game.assign_opening()
            self.goto_end()
            self.reOpenBook()
            self.refresh()
            if self.state == ST_ENDGAME:
                self.state = ST_PLAYING
                self.toolbar_state = None
                self.pon_toolbar()
            self.play_next_move()

    def testBook(self):
        if self.book_rival_active:
            resp = self.book_rival.get_list_moves(self.last_fen())
            if not resp:
                self.book_rival_active = False
                self.show_basic_label()

    def reOpenBook(self):
        if self.book_rival:
            self.book_rival_active = True
            self.show_basic_label()
        if self.book_player:
            self.book_player_active = True
        self.siBookAjustarFuerza = self.nAjustarFuerza != ADJUST_BETTER

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.rival_is_thinking = False
        self.put_view()

        is_white = self.game.is_white()

        if self.game.is_finished():
            self.show_result()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        si_rival = is_white == self.is_engine_side_white

        if si_rival:
            self.play_rival(is_white)

        else:
            self.play_human(is_white)

    def set_summary(self, key, value):
        njug = len(self.game)
        if not (njug in self.summary):
            self.summary[njug] = {}
        self.summary[njug][key] = value

    def is_mandatory_move(self):
        if self.opening_mandatory:
            return True

        # OPENING LINE--------------------------------------------------------------------------------------------------
        if self.opening_line:
            fen_basem2 = self.game.last_position.fenm2()
            if fen_basem2 in self.opening_line:
                return True

        # BOOK----------------------------------------------------------------------------------------------------------
        if self.book_player_active:
            fen_base = self.game.last_position.fen()
            lista_jugadas = self.book_player.get_list_moves(fen_base)
            if lista_jugadas:
                return True

        return False

    def analyze_begin(self):
        if self.is_mandatory_move():
            return

        if self.game.last_position.fenm2() in self.cache_analysis:
            self.mrm_tutor = self.cache_analysis[self.game.last_position.fenm2()]
            self.is_analyzed_by_tutor = True
            self.is_analyzing = False
            return

        if not self.is_tutor_enabled:
            return
        self.is_analyzing = False
        self.is_analyzed_by_tutor = False
        if not self.play_while_win and not self.tutor_con_flechas:
            if self.opening_mandatory or self.ayudas_iniciales <= 0:
                return
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_end(self, is_mate=False):
        if self.is_mandatory_move():
            return

        if self.game.last_position.fenm2() in self.cache_analysis:
            self.mrm_tutor = self.cache_analysis[self.game.last_position.fenm2()]
            self.is_analyzed_by_tutor = True
            self.is_analyzing = False
            return

        if not self.is_tutor_enabled:
            if self.is_analyzing:
                self.xtutor.stop()
                self.is_analyzing = False
            return

        if is_mate:
            if self.is_analyzing:
                self.xtutor.stop()
            return

        if self.is_analyzed_by_tutor:
            return

        # estado = self.is_analyzing
        self.is_analyzing = False
        if not self.play_while_win:
            if not self.tutor_con_flechas:
                if self.is_analyzed_by_tutor or not self.is_tutor_enabled or self.ayudas_iniciales <= 0:
                    return

        if self.is_analyzed_by_tutor:
            return

        self.main_window.pensando_tutor(True)
        if self.continueTt:
            self.mrm_tutor = self.xtutor.ac_final(self.xtutor.mstime_engine)
        else:
            self.mrm_tutor = self.xtutor.ac_final_limit()
        self.main_window.pensando_tutor(False)
        self.is_analyzed_by_tutor = True

    def ajustaPlayer(self, mrm):
        position = self.game.last_position

        FasterCode.set_fen(position.fen())
        li = FasterCode.get_exmoves()

        li_options = []
        for rm in mrm.li_rm:
            li_options.append(
                (rm, "%s (%s)" % (position.pgn_translated(rm.from_sq, rm.to_sq, rm.promotion), rm.abbrev_text()))
            )
            mv = rm.movimiento()
            for x in range(len(li)):
                if li[x].move() == mv:
                    del li[x]
                    break

        for mj in li:
            rm = EngineResponse.EngineResponse("", position.is_white)
            rm.from_sq = mj.xfrom()
            rm.to_sq = mj.xto()
            rm.promotion = mj.promotion()
            rm.puntos = None
            li_options.append((rm, position.pgn_translated(rm.from_sq, rm.to_sq, rm.promotion)))

        if len(li_options) == 1:
            return li_options[0][0]

        menu = QTVarios.LCMenu(self.main_window)
        titulo = _("White") if position.is_white else _("Black")
        icono = Iconos.Carpeta()

        self.main_window.cursorFueraBoard()
        menu.opcion(None, titulo, icono)
        menu.separador()
        icono = Iconos.PuntoNaranja() if position.is_white else Iconos.PuntoNegro()
        for rm, txt in li_options:
            menu.opcion(rm, txt, icono)
        while True:
            resp = menu.lanza()
            if resp:
                return resp

    def select_book_move_base(self, book, book_select):
        fen = self.last_fen()

        if book_select == SELECTED_BY_PLAYER:
            lista_jugadas = book.get_list_moves(fen)
            if lista_jugadas:
                resp = WBooks.eligeJugadaBooks(self.main_window, lista_jugadas, self.game.last_position.is_white)
                return True, resp[0], resp[1], resp[2]
        else:
            pv = book.eligeJugadaTipo(fen, book_select)
            if pv:
                return True, pv[:2], pv[2:4], pv[4:]

        return False, None, None, None

    def select_book_move(self):
        return self.select_book_move_base(self.book_rival, self.book_rival_select)

    def select_book_move_adjusted(self):
        if self.nAjustarFuerza < 1000:
            return False, None, None, None
        dic_personalidad = self.configuration.li_personalities[self.nAjustarFuerza - 1000]
        nombook = dic_personalidad.get("BOOK", None)
        if (nombook is None) or (not Util.exist_file(nombook)):
            return False, None, None, None

        book = Books.Book("P", nombook, nombook, True)
        book.polyglot()
        mode = dic_personalidad.get("BOOKRR", BOOK_BEST_MOVE)
        return self.select_book_move_base(book, mode)

    def play_human(self, is_white):
        self.tc_player.start()
        self.human_is_playing = True
        last_position = self.game.last_position
        si_changed, from_sq, to_sq = self.board.piece_out_position(last_position)
        if si_changed:
            self.board.set_position(last_position)
            if from_sq:
                self.premove = from_sq, to_sq
        if self.premove:
            from_sq, to_sq = self.premove
            promotion = "q" if self.game.last_position.pawn_can_promote(from_sq, to_sq) else None
            ok, error, move = Move.get_game_move(
                self.game, self.game.last_position, self.premove[0], self.premove[1], promotion
            )
            if ok:
                self.player_has_moved(from_sq, to_sq, promotion)
                return
            self.premove = None

        self.pon_toolbar()
        self.analyze_begin()

        self.activate_side(is_white)

    def play_rival(self, is_white):
        self.board.remove_arrows()
        self.tc_rival.start()
        self.human_is_playing = False
        self.rival_is_thinking = True
        self.rm_rival = None
        self.pon_toolbar()
        if not self.is_tutor_enabled:
            self.activate_side(self.is_human_side_white)

        from_sq = to_sq = promotion = ""
        is_choosed = False

        # CACHE---------------------------------------------------------------------------------------------------------
        fen_ultimo = self.last_fen()
        if fen_ultimo in self.cache:
            move = self.cache[fen_ultimo]
            self.move_the_pieces(move.liMovs, True)
            self.add_move(move)
            if self.timed:
                self.tc_rival.restore(move.cacheTime)
                self.show_clocks()
            return self.play_next_move()

        # OPENING MANDATORY---------------------------------------------------------------------------------------------
        if self.opening_mandatory:
            is_choosed, from_sq, to_sq, promotion = self.opening_mandatory.run_engine(fen_ultimo)
            if not is_choosed:
                self.opening_mandatory = None

        # BOOK----------------------------------------------------------------------------------------------------------
        if not is_choosed and self.book_rival_active:
            if self.book_rival_depth == 0 or self.book_rival_depth > len(self.game):
                is_choosed, from_sq, to_sq, promotion = self.select_book_move()
                if not is_choosed:
                    self.dic_reject["book_rival"] += 1
            else:
                self.dic_reject["book_rival"] += 1
            self.book_rival_active = self.dic_reject["book_rival"] <= 5
            self.show_basic_label()

        if not is_choosed and self.siBookAjustarFuerza:
            is_choosed, from_sq, to_sq, promotion = self.select_book_move_adjusted()  # book de la personalidad
            if not is_choosed:
                self.siBookAjustarFuerza = False

        # --------------------------------------------------------------------------------------------------------------
        if is_choosed:
            rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
            rm_rival.from_sq = from_sq
            rm_rival.to_sq = to_sq
            rm_rival.promotion = promotion
            self.rival_has_moved(rm_rival)
        else:
            self.thinking(True)
            if self.timed:
                seconds_white = self.tc_white.pending_time
                seconds_black = self.tc_black.pending_time
                seconds_move = self.tc_white.seconds_per_move
            else:
                seconds_white = seconds_black = self.unlimited_minutes * 60
                seconds_move = 0

            self.xrival.play_time_routine(
                self.game,
                self.main_window.notify,
                seconds_white,
                seconds_black,
                seconds_move,
                adjusted=self.nAjustarFuerza,
                humanize=self.humanize,
            )

    def continue_analysis_human_move(self):
        self.analyze_begin()
        Manager.Manager.sigueHumano(self)

    def mueve_rival_base(self):
        self.rival_has_moved(self.main_window.dato_notify)

    def rival_has_moved(self, rm_rival):
        if self.state == ST_PAUSE:
            return True
        self.rival_is_thinking = False
        time_s = self.stop_clock(False)
        self.thinking(False)
        self.set_summary("TIMERIVAL", time_s)

        if self.state in (ST_ENDGAME, ST_PAUSE):
            return self.state == ST_ENDGAME
        with_cache = True
        if self.nAjustarFuerza == ADJUST_SELECTED_BY_PLAYER and hasattr(rm_rival, "li_rm"):
            rm_rival = self.ajustaPlayer(rm_rival)
            with_cache = False

        self.lirm_engine.append(rm_rival)
        if not self.valoraRMrival():
            self.show_result()
            return True

        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, rm_rival.from_sq, rm_rival.to_sq, rm_rival.promotion
        )
        self.rm_rival = rm_rival
        if ok:
            fen_ultimo = self.last_fen()
            move.set_time_ms(int(time_s * 1000))
            move.set_clock_ms(int(self.tc_rival.pending_time * 1000))
            self.add_move(move)
            self.move_the_pieces(move.liMovs, True)
            self.beepExtendido(False)
            if with_cache:
                if self.timed:
                    move.cacheTime = self.tc_rival.save()
                self.cache[fen_ultimo] = move
            self.play_next_move()
            return True

        else:
            return False

    def check_premove(self, from_sq, to_sq):
        self.board.remove_arrows()
        if self.premove:
            if from_sq == self.premove[0] and to_sq == self.premove[1]:
                self.premove = None
                return
        self.board.creaFlechaPremove(from_sq, to_sq)
        self.premove = from_sq, to_sq

        return True

    def remove_premove(self):
        if self.premove:
            self.board.remove_arrows()
            self.premove = None

    def help_to_move(self):
        move = Move.Move(self.game, position_before=self.game.last_position.copia())
        if self.is_tutor_enabled:
            self.analyze_end()
            if self.mrm_tutor:
                move.analysis = self.mrm_tutor, 0
        Analysis.show_analysis(self.procesador, self.xtutor, move, self.board.is_white_bottom, 0, must_save=False)
        if self.hints:
            self.hints -= 1
            self.show_hints()

    def play_instead_of_me(self):
        if self.state != ST_PLAYING or self.is_finished() or self.game_type != GT_AGAINST_ENGINE:
            return

        fen_base = self.last_fen()

        if self.hints:
            self.hints -= 1
            if self.hints:
                self.ponAyudas(self.hints)
            else:
                self.remove_hints()

        if self.book_rival:
            listaJugadas = self.book_rival.get_list_moves(fen_base)
            if listaJugadas:
                apdesde, aphasta, appromotion, nada, nada1 = listaJugadas[0]
                return self.player_has_moved_base(apdesde, aphasta, appromotion)

        if self.opening_mandatory:
            apdesde, aphasta, promotion = self.opening_mandatory.from_to_active(fen_base)
            if apdesde:
                return self.player_has_moved_base(apdesde, aphasta, promotion)

        if self.opening_line:
            fenm2 = FasterCode.fen_fenm2(fen_base)
            if fenm2 in self.opening_line:
                st = self.opening_line[fenm2]
                sel = list(st)[0]
                return self.player_has_moved_base(sel[:2], sel[2:4], sel[4:])

        if self.is_tutor_enabled:
            self.analyze_end()
            rm = self.mrm_tutor.best_rm_ordered()
            return self.player_has_moved_base(rm.from_sq, rm.to_sq, rm.promotion)

        if self.is_analyzing:
            self.analyze_end()

        mrm = self.analizaTutor(with_cursor=True)
        rm = mrm.best_rm_ordered()
        if rm and rm.from_sq:
            self.player_has_moved_base(rm.from_sq, rm.to_sq, rm.promotion)

    def pww_centipawns_lost(self, rm_user: EngineResponse.EngineResponse):
        for move in self.game.li_moves:
            if move.is_white() == self.is_human_side_white:
                if move.analysis:
                    mrm: EngineResponse.MultiEngineResponse
                    mrm, pos = move.analysis
                    rm_best1: EngineResponse.EngineResponse = mrm.rm_best()
                    return rm_best1.score_abs5() - rm_user.score_abs5()

        return 0

    def enable_toolbar(self):
        self.main_window.toolbar_enable(True)

    def disable_toolbar(self):
        self.main_window.toolbar_enable(False)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        if self.rival_is_thinking:
            return self.check_premove(from_sq, to_sq)
        move = self.check_human_move(from_sq, to_sq, promotion, not self.is_tutor_enabled)
        if not move:
            return False
        self.tc_player.pause()
        self.tc_player.set_labels()

        self.disable_toolbar()

        a1h8 = move.movimiento()
        si_analisis = False
        is_choosed = False
        fen_base = self.last_fen()
        fen_basem2 = FasterCode.fen_fenm2(fen_base)
        game_over_message_pww = None

        # OPENING MANDATORY---------------------------------------------------------------------------------------------
        if self.opening_mandatory:
            if self.opening_mandatory.check_human(fen_base, from_sq, to_sq):
                is_choosed = True
            else:
                apdesde, aphasta, promotion = self.opening_mandatory.from_to_active(fen_base)
                if apdesde is None:
                    self.opening_mandatory = None
                else:
                    if self.play_while_win:
                        self.board.ponFlechas(((apdesde, aphasta, False),))
                        is_choosed = True  # para que continue sin buscar
                        game_over_message_pww = _("This movement is not in the mandatory opening")
                    else:
                        self.board.ponFlechasTmp(((apdesde, aphasta, False),))
                        self.beep_error()
                        self.tc_player.restart()
                        self.enable_toolbar()
                        self.sigueHumano()
                        return False

        # OPENING LINE--------------------------------------------------------------------------------------------------
        if self.opening_line:
            if fen_basem2 in self.opening_line:
                st_validos = self.opening_line[fen_basem2]
                if a1h8 in st_validos:
                    is_choosed = True
                else:
                    li_flechas = [(a1h8[:2], a1h8[2:4], False) for a1h8 in st_validos]
                    if self.play_while_win:
                        self.board.ponFlechas(li_flechas)
                        is_choosed = True  # para que continue sin buscar
                        game_over_message_pww = _("This movement is not in the opening line selected")
                    else:
                        self.board.ponFlechasTmp(li_flechas)
                        self.beep_error()
                        self.tc_player.restart()
                        self.enable_toolbar()
                        self.sigueHumano()
                        return False
            else:
                self.dic_reject["opening_line"] += 1
                if self.dic_reject["opening_line"] > 5:
                    self.opening_line = None

        # BOOK----------------------------------------------------------------------------------------------------------
        if not is_choosed and self.book_player_active:
            test_book = False
            if self.book_player_depth == 0 or self.book_player_depth > len(self.game):
                lista_jugadas = self.book_player.get_list_moves(fen_base)
                if lista_jugadas:
                    li = []
                    for apdesde, aphasta, appromotion, nada, nada1 in lista_jugadas:
                        mx = apdesde + aphasta + appromotion
                        if mx.strip().lower() == a1h8:
                            is_choosed = True
                            break
                        li.append((apdesde, aphasta, False))
                    if not is_choosed:
                        if self.play_while_win:
                            self.board.ponFlechas(li)
                            is_choosed = True  # para que continue sin buscar
                            game_over_message_pww = _("This movement is not in the mandatory book")
                        else:
                            self.board.ponFlechasTmp(li)
                            self.tc_player.restart()
                            self.enable_toolbar()
                            self.sigueHumano()
                            return False
                else:
                    test_book = True
            else:
                test_book = True
            if test_book:
                self.dic_reject["book_player"] += 1
                self.book_player_active = self.dic_reject["book_player"] > 5
            self.show_basic_label()

        # TUTOR---------------------------------------------------------------------------------------------------------
        is_mate = move.is_mate
        self.analyze_end(is_mate)  # tiene que acabar siempre
        if not is_mate and not is_choosed and self.is_tutor_enabled:
            if not self.tutor_book.si_esta(fen_base, a1h8):
                rm_user, n = self.mrm_tutor.search_rm(a1h8)
                if not rm_user:
                    self.main_window.pensando_tutor(True)
                    rm_user = self.xtutor.valora(self.game.last_position, from_sq, to_sq, move.promotion)
                    self.main_window.pensando_tutor(False)
                    if not rm_user:
                        self.continue_analysis_human_move()
                        self.tc_player.restart()
                        self.enable_toolbar()
                        return False
                    self.mrm_tutor.add_rm(rm_user)
                self.cache_analysis[fen_basem2] = self.mrm_tutor

                si_analisis = True
                points_best, points_user = self.mrm_tutor.dif_points_best(a1h8)
                self.set_summary("POINTSBEST", points_best)
                self.set_summary("POINTSUSER", points_user)

                if self.play_while_win:
                    if Tutor.launch_tutor(self.mrm_tutor, rm_user, tp=MISTAKE):
                        game_over_message_pww = _("You have made a bad move.")
                    else:
                        cpws_lost = self.pww_centipawns_lost(rm_user)
                        if cpws_lost > self.limit_pww:
                            game_over_message_pww = "%s<br>%s" % (
                                _("You have exceeded the limit of lost centipawns."),
                                _("Lost centipawns %d") % cpws_lost,
                            )
                    if game_over_message_pww:
                        rm0 = self.mrm_tutor.best_rm_ordered()
                        self.board.put_arrow_scvar([(rm0.from_sq, rm0.to_sq)])

                elif Tutor.launch_tutor(self.mrm_tutor, rm_user):
                    if not move.is_mate:
                        si_tutor = True
                        self.beep_error()
                        if self.chance:
                            num = self.mrm_tutor.num_better_move_than(a1h8)
                            if num:
                                rm_tutor = self.mrm_tutor.rm_best()
                                menu = QTVarios.LCMenu(self.main_window)
                                menu.opcion("None", _("There are %d best movements") % num, Iconos.Engine())
                                menu.separador()
                                resp = rm_tutor.abbrev_text_base()
                                if not resp:
                                    resp = _("Mate")
                                menu.opcion("tutor", "&1. %s (%s)" % (_("Show tutor"), resp), Iconos.Tutor())
                                menu.separador()
                                menu.opcion("try", "&2. %s" % _("Try again"), Iconos.Atras())
                                menu.separador()
                                menu.opcion(
                                    "user",
                                    "&3. %s (%s)" % (_("Select my move"), rm_user.abbrev_text_base()),
                                    Iconos.Player(),
                                )
                                self.main_window.cursorFueraBoard()
                                resp = menu.lanza()
                                if resp == "try":
                                    self.continue_analysis_human_move()
                                    self.enable_toolbar()
                                    self.tc_player.restart()
                                    return False
                                elif resp == "user":
                                    si_tutor = False
                                elif resp != "tutor":
                                    self.continue_analysis_human_move()
                                    self.enable_toolbar()
                                    self.tc_player.restart()
                                    return False
                        if si_tutor:
                            tutor = Tutor.Tutor(self, move, from_sq, to_sq, False)

                            li_ap_posibles = self.listaOpeningsStd.list_possible_openings(self.game)

                            if tutor.elegir(self.hints > 0, li_ap_posibles=li_ap_posibles):
                                if self.hints > 0:  # doble entrada a tutor.
                                    self.set_piece_again(from_sq)
                                    self.hints -= 1
                                    self.tutor_con_flechas = self.nArrowsTt > 0 and self.hints > 0
                                    from_sq = tutor.from_sq
                                    to_sq = tutor.to_sq
                                    promotion = tutor.promotion
                                    ok, mens, jg_tutor = Move.get_game_move(
                                        self.game, self.game.last_position, from_sq, to_sq, promotion
                                    )
                                    if ok:
                                        move = jg_tutor
                                        self.set_summary("SELECTTUTOR", True)
                            if self.configuration.x_save_tutor_variations:
                                tutor.ponVariations(move, 1 + len(self.game) / 2)

                            del tutor

        # --------------------------------------------------------------------------------------------------------------
        time_s = self.tc_player.stop()
        if self.timed:
            self.show_clocks()

        move.set_time_ms(time_s * 1000)
        move.set_clock_ms(self.tc_player.pending_time * 1000)
        self.set_summary("TIMEUSER", time_s)

        if si_analisis:
            rm, nPos = self.mrm_tutor.search_rm(move.movimiento())
            if rm:
                move.analysis = self.mrm_tutor, nPos

        if game_over_message_pww:
            game_over_message_pww = '<span style="font-size:14pts">%s<br>%s<br><br><b>%s</b>' % (
                _("GAME OVER"),
                game_over_message_pww,
                _("You can try again, by pressing Reinit, the engine will repeat the moves."),
            )
            self.message_on_pgn(game_over_message_pww)
            self.rendirse(with_question=False)

        self.add_move(move)
        self.move_the_pieces(move.liMovs, False)
        self.beepExtendido(True)

        # if game_over_message_pww:
        #     return True

        self.error = ""

        self.enable_toolbar()
        self.play_next_move()
        return True

    def add_move(self, move):
        self.game.add_move(move)
        self.show_clocks()
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)

        self.show_hints()

        self.pgn_refresh(self.game.last_position.is_white)

        self.refresh()

    def saveSummary(self):
        if not self.with_summary or not self.summary:
            return

        j_num = 0
        j_same = 0
        st_accept = 0
        st_reject = 0
        nt_accept = 0
        nt_reject = 0
        j_sum = 0

        time_user = 0.0
        ntime_user = 0
        time_rival = 0.0
        ntime_rival = 0

        for njg, d in self.summary.items():
            if "POINTSBEST" in d:
                j_num += 1
                p = d["POINTSBEST"] - d["POINTSUSER"]
                if p:
                    if d.get("SELECTTUTOR", False):
                        st_accept += p
                        nt_accept += 1
                    else:
                        st_reject += p
                        nt_reject += 1
                    j_sum += p
                else:
                    j_same += 1
            if "TIMERIVAL" in d:
                ntime_rival += 1
                time_rival += d["TIMERIVAL"]
            if "TIMEUSER" in d:
                ntime_user += 1
                time_user += d["TIMEUSER"]

        comment = self.game.first_comment
        if comment:
            comment += "\n"

        if j_num:
            comment += _("Tutor") + ": %s\n" % self.xtutor.name
            comment += _("Number of moves") + ":%d\n" % j_num
            comment += _("Same move") + ":%d (%0.2f%%)\n" % (j_same, j_same * 1.0 / j_num)
            comment += _("Accepted") + ":%d (%0.2f%%) %s: %0.2f\n" % (
                nt_accept,
                nt_accept * 1.0 / j_num,
                _("Average centipawns lost"),
                st_accept * 1.0 / nt_accept if nt_accept else 0.0,
            )
            comment += _("Rejected") + ":%d (%0.2f%%) %s: %0.2f\n" % (
                nt_reject,
                nt_reject * 1.0 / j_num,
                _("Average centipawns lost"),
                st_reject * 1.0 / nt_reject if nt_reject else 0.0,
            )
            comment += _("Total") + ":%d (100%%) %s: %0.2f\n" % (
                j_num,
                _("Average centipawns lost"),
                j_sum * 1.0 / j_num,
            )

        if ntime_user or ntime_rival:
            comment += _("Average time (seconds)") + ":\n"
            if ntime_user:
                comment += "%s: %0.2f\n" % (self.configuration.x_player, time_user / ntime_user)
            if ntime_rival:
                comment += "%s: %0.2f\n" % (self.xrival.name, time_rival / ntime_rival)

        self.game.first_comment = comment

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False
        if self.timed:
            self.main_window.stop_clock()

        if Code.eboard and Code.eboard.driver:
            self.main_window.delay_routine(
                300, self.muestra_resultado_delayed
            )  # Para que eboard siga su proceso y no se pare por la pregunta
        else:
            self.muestra_resultado_delayed()

    def muestra_resultado_delayed(self):
        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beep_result(beep)
        self.saveSummary()
        self.autosave()
        QTUtil.refresh_gui()
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        if not (self.play_while_win and self.game.termination == TERMINATION_RESIGN):
            QTUtil2.message(self.main_window, mensaje, px=p.x(), py=p.y(), si_bold=True)
        self.set_end_game(self.with_takeback)

    def show_hints(self):
        self.ponAyudas(self.hints, siQuitarAtras=False)

    def change_rival(self):
        dic = WPlayAgainstEngine.change_rival(self.main_window, self.configuration, self.reinicio)

        if dic:
            dr = dic["RIVAL"]
            rival = dr["CM"]
            if hasattr(rival, "icono"):
                delattr(rival, "icono")
            for k, v in dic.items():
                self.reinicio[k] = v

            is_white = dic["ISWHITE"]

            self.pon_toolbar()

            self.nAjustarFuerza = dic["ADJUST"]

            r_t = dr["ENGINE_TIME"] * 100  # Se guarda en decimas y se pasa a milesimas
            r_p = dr["ENGINE_DEPTH"]
            r_n = dr["ENGINE_NODES"]
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None

            dr["RESIGN"] = self.resign_limit
            self.xrival.terminar()
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, self.nAjustarFuerza != ADJUST_BETTER)
            if r_n:
                self.xrival.set_nodes(r_n)
                self.nodes = r_n

            self.xrival.is_white = not is_white

            rival = self.xrival.name
            player = self.configuration.x_player
            bl, ng = player, rival
            if not is_white:
                bl, ng = ng, bl
            self.main_window.change_player_labels(bl, ng)

            self.show_basic_label()

            self.put_pieces_bottom(is_white)
            if is_white != self.is_human_side_white:
                self.is_human_side_white = is_white
                self.is_engine_side_white = not is_white

                self.play_next_move()

    def show_dispatch(self, tp, rm):
        if rm.time or rm.depth:
            color_engine = "DarkBlue" if self.human_is_playing else "brown"
            if rm.nodes:
                nps = "/%d" % rm.nps if rm.nps else ""
                nodes = " | %d%s" % (rm.nodes, nps)
            else:
                nodes = ""
            seldepth = "/%d" % rm.seldepth if rm.seldepth else ""
            li = [
                '<span style="color:%s">%s' % (color_engine, rm.name),
                '<b>%s</b> | <b>%d</b>%s | <b>%d"</b>%s'
                % (rm.abbrev_text_base(), rm.depth, seldepth, rm.time // 1000, nodes),
            ]
            pv = rm.pv
            if tp < 999:
                li1 = pv.split(" ")
                if len(li1) > tp:
                    pv = " ".join(li1[:tp])
            p = Game.Game(self.game.last_position)
            p.read_pv(pv)
            li.append(p.pgnBaseRAW())
            self.set_label3("<br>".join(li) + "</span>")
            QTUtil.refresh_gui()

    def show_clocks(self):
        if not self.timed:
            return

        if Code.eboard:
            Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

        for is_white in (WHITE, BLACK):
            tc = self.tc_white if is_white else self.tc_black
            tc.set_labels()

    def change_tutor_active(self):
        previous = self.is_tutor_enabled
        self.is_tutor_enabled = not previous
        self.set_activate_tutor(self.is_tutor_enabled)
        if previous:
            self.analyze_end()
        elif self.human_is_playing:
            self.analyze_begin()

    def change_last_move_engine(self):
        if self.state != ST_PLAYING or not self.human_is_playing or len(self.game) == 0:
            return
        self.main_window.cursorFueraBoard()
        menu = QTVarios.LCMenu(self.main_window)
        last_move = self.game.move(-1)
        position = last_move.position_before
        li_exmoves = position.get_exmoves()
        icono = Iconos.PuntoNaranja() if position.is_white else Iconos.PuntoNegro()

        for mj in li_exmoves:
            rm = EngineResponse.EngineResponse("", position.is_white)
            rm.from_sq = mj.xfrom()
            rm.to_sq = mj.xto()
            rm.promotion = mj.promotion()
            rm.puntos = None
            txt = position.pgn_translated(rm.from_sq, rm.to_sq, rm.promotion)
            menu.opcion(rm, txt, icono)
        rm = menu.lanza()
        if rm is None:
            return

        self.analyze_terminate()

        self.board.disable_eboard_here()

        last_move = self.game.move(-1)
        self.game.anulaSoloUltimoMovimiento()

        self.set_position(position)
        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, rm.from_sq, rm.to_sq, rm.promotion
        )
        self.rm_rival = rm
        move.set_time_ms(last_move.time_ms)
        move.set_clock_ms(last_move.clock_ms)
        fen_ultimo = self.last_fen()
        self.add_move(move)
        self.move_the_pieces(move.liMovs, True)
        if hasattr(last_move, "cacheTime"):
            move.cacheTime = last_move.cacheTime
        self.cache[fen_ultimo] = move

        self.check_boards_setposition()

        self.board.enable_eboard_here()

        self.play_next_move()

    def show_pv(self, pv, n_arrows):
        if not pv:
            return True
        self.board.remove_arrows()
        pv = pv.strip()
        while "  " in pv:
            pv = pv.replace("  ", " ")
        lipv = pv.split(" ")
        npv = len(lipv)
        nbloques = min(npv, n_arrows)

        for side in range(2):
            base = "p" if side == 0 else "r"
            alt = base + "t"
            opacity = 1.00

            previo = None
            for n in range(side, nbloques, 2):
                pv = lipv[n]
                if previo:
                    self.board.show_arrow_mov(previo[2:4], pv[:2], "tr", opacity=max(opacity / 2, 0.3))

                self.board.show_arrow_mov(pv[:2], pv[2:4], base if n == side else alt, opacity=opacity)
                previo = pv
                opacity = max(opacity - 0.20, 0.40)
        return True

    def setup_board_live(self, is_white, position):
        previo = self.current_position().fen()
        previo = " ".join(previo.split(" ")[:2])
        new = position.fen()
        new = " ".join(new.split(" ")[:2])
        if previo != new:
            self.board.set_side_bottom(is_white)
            self.reinicio["FEN"] = position.fen()
            self.reiniciar(False)

    def start_position(self):
        if Code.eboard and Code.eboard.deactivate():
            self.main_window.set_title_toolbar_eboard()

        position, is_white_bottom = Voyager.voyager_position(
            self.main_window, self.game.last_position
        )
        if position is not None:
            self.setup_board_live(is_white_bottom, position)

    def control_teclado(self, nkey, modifiers):
        if modifiers and (modifiers & QtCore.Qt.ControlModifier) > 0:
            if nkey == QtCore.Qt.Key_S:
                self.start_position()
