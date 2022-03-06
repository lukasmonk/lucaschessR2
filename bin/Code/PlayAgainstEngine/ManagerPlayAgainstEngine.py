import os
import time

import FasterCode

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
    TB_HELP_TO_MOVE,
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
)
from Code.Engines import EngineResponse, SelectEngines
from Code.Openings import Opening
from Code.PlayAgainstEngine import WPlayAgainstEngine, Personalities
from Code.Polyglots import Books, WindowBooks
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Tutor import Tutor


class ManagerPlayAgainstEngine(Manager.Manager):
    reinicio = None
    cache = None
    is_analyzing = False
    timekeeper = None
    summary = None
    with_summary = False
    human_side = False
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
    zeitnot = 0
    vtime = None
    is_analyzed_by_tutor = False
    toolbar_state = None
    premove = None
    last_time_show_arrows = None
    rival_is_thinking = False
    humanize = False

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

        self.game_type = GT_AGAINST_ENGINE

        self.human_is_playing = False
        self.rival_is_thinking = False
        self.plays_instead_of_me_option = True
        self.state = ST_PLAYING
        self.is_analyzing = False

        self.summary = {}  # numJugada : "a"ccepted, "s"ame, "r"ejected, dif points, time used
        self.with_summary = dic_var.get("SUMMARY", False)

        is_white = dic_var["ISWHITE"]
        self.human_side = is_white
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
        else:
            if dic_var["OPENING"]:
                self.opening_mandatory = Opening.JuegaOpening(dic_var["OPENING"].a1h8)
                self.primeroBook = False  # la opening es obligatoria

        self.book_rival_active = False
        self.book_rival = dic_var.get("BOOKR", None)
        if self.book_rival:
            self.book_rival_active = True
            self.book_rival_depth = dic_var.get("BOOKRDEPTH", 0)
            self.book_rival.polyglot()
            self.book_rival_select = dic_var.get("BOOKRR", "mp")
        elif dic_var["RIVAL"].get("TYPE", None) in (SelectEngines.MICGM, SelectEngines.MICPER):
            if self.conf_engine.book:
                self.book_rival_active = True
                self.book_rival = Books.Book("P", self.conf_engine.book, self.conf_engine.book, True)
                self.book_rival.polyglot()
                self.book_rival_select = "mp"
                self.book_rival_depth = 0

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

        self.humanize = dic_var.get("HUMANIZE", False)

        if dic_var.get("ACTIVATE_EBOARD"):
            Code.eboard.activate(self.board.dispatch_eboard)

        if self.nArrowsTt != 0 and self.hints == 0:
            self.nArrowsTt = 0

        self.last_time_show_arrows = time.time()

        self.with_takeback = dic_var.get("TAKEBACK", True)

        self.tutor_con_flechas = self.nArrowsTt > 0 and self.hints > 0
        self.tutor_book = Books.BookGame(Code.tbook)

        mx = max(self.thoughtOp, self.thoughtTt)
        if mx > -1:
            self.set_hight_label3(n_box_height)

        dr = dic_var["RIVAL"]
        rival = dr["CM"]
        self.unlimited_minutes = dr.get("ENGINE_UNLIMITED", 5)

        if dr["TYPE"] == SelectEngines.ELO:
            r_t = 0
            r_p = rival.fixed_depth
            self.nAjustarFuerza = ADJUST_BETTER

        else:
            r_t = dr["ENGINE_TIME"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["ENGINE_DEPTH"]
            self.nAjustarFuerza = dic_var.get("ADJUST", ADJUST_BETTER)

        if not self.xrival:  # reiniciando is not None
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic_var["WITHTIME"]:
                r_t = None
            rival.liUCI = dr["LIUCI"]
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, self.nAjustarFuerza != ADJUST_BETTER)
            if self.nAjustarFuerza != ADJUST_BETTER:
                self.xrival.maximize_multipv()
        self.resign_limit = dic_var["RESIGN"]

        self.game.set_tag("Event", _("Play against an engine"))

        player = self.configuration.nom_player()
        other = self.xrival.name
        w, b = (player, other) if self.human_side else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.siBookAjustarFuerza = self.nAjustarFuerza != ADJUST_BETTER

        self.xrival.is_white = self.is_engine_side_white

        self.timed = dic_var["WITHTIME"]
        if self.timed:
            self.max_seconds = dic_var["MINUTES"] * 60.0
            self.seconds_per_move = dic_var["SECONDS"]
            self.secs_extra = dic_var.get("MINEXTRA", 0) * 60.0
            self.zeitnot = dic_var.get("ZEITNOT", 0)

            self.vtime = {
                WHITE: Util.Timer2(self.game, WHITE, self.max_seconds, self.seconds_per_move),
                BLACK: Util.Timer2(self.game, BLACK, self.max_seconds, self.seconds_per_move),
            }
            if self.secs_extra:
                self.vtime[self.human_side].add_extra_seconds(self.secs_extra)

            time_control = "%d" % int(self.max_seconds)
            if self.seconds_per_move:
                time_control += "+%d" % self.seconds_per_move
            self.game.set_tag("TimeControl", time_control)
            if self.secs_extra:
                self.game.set_tag("TimeExtra" + ("White" if self.human_side else "Black"), "%d" % self.secs_extra)

        self.pon_toolbar()

        self.main_window.activaJuego(True, self.timed)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        if self.ayudas_iniciales:
            self.ponAyudasEM()
        else:
            self.remove_hints(siQuitarAtras=False)
        self.put_pieces_bottom(is_white)

        self.ponRotuloBasico()
        self.set_label2("")

        if self.nAjustarFuerza != ADJUST_BETTER:
            pers = Personalities.Personalities(None, self.configuration)
            label = pers.label(self.nAjustarFuerza)
            if label:
                self.game.set_tag("Strength", label)

        self.ponCapInfoPorDefecto()

        self.pgnRefresh(True)

        rival = self.xrival.name
        player = self.configuration.x_player
        bl, ng = player, rival
        if self.is_engine_side_white:
            bl, ng = ng, bl

        active_clock = max(self.thoughtOp, self.thoughtTt) > -1

        if self.timed:
            tp_bl = self.vtime[True].etiqueta()
            tp_ng = self.vtime[False].etiqueta()
            self.main_window.ponDatosReloj(bl, tp_bl, ng, tp_ng)
            active_clock = True
            self.refresh()
        else:
            self.main_window.base.change_player_labels(bl, ng)

        if active_clock or self.nArrowsTt > 0 or self.nArrows > 0 or self.thoughtOp > 0 or self.thoughtTt > 0:
            self.main_window.start_clock(self.set_clock, 1000)

        self.main_window.set_notify(self.mueve_rival_base)

        self.is_analyzed_by_tutor = False

        self.game.tag_timestart()

        self.check_boards_setposition()

    def pon_toolbar(self):
        if self.state == ST_PLAYING:
            if self.toolbar_state != self.state:
                li = [
                    TB_CANCEL,
                    TB_RESIGN,
                    TB_DRAW,
                    TB_HELP_TO_MOVE,
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
            self.main_window.enable_option_toolbar(TB_HELP_TO_MOVE, hip)
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

    def ponRotuloBasico(self):
        rotulo1 = ""
        if self.book_rival_active:
            rotulo1 += "<br>%s-%s: <b>%s</b>" % (_("Book"), _("Opponent"), os.path.basename(self.book_rival.name))
        if self.book_player_active:
            rotulo1 += "<br>%s-%s: <b>%s</b>" % (_("Book"), _("Player"), os.path.basename(self.book_player.name))
        self.set_label1(rotulo1)

    def show_time(self, siUsuario):
        is_white = siUsuario == self.human_side
        ot = self.vtime[is_white]
        eti, eti2 = ot.etiquetaDif2()
        if eti:
            if is_white:
                self.main_window.set_clock_white(eti, eti2)
            else:
                self.main_window.set_clock_black(eti, eti2)

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
                    rm = mrm.mejorMov()
                    if self.nArrowsTt > 0:
                        if time.time() - self.last_time_show_arrows > 1.4:
                            self.last_time_show_arrows = time.time()
                            self.showPV(rm.pv, self.nArrowsTt)
                    if self.thoughtTt > -1:
                        self.show_dispatch(self.thoughtTt, rm)
        elif self.thoughtOp > -1 or self.nArrows > 0:
            rm = self.xrival.current_rm()
            if rm:
                if self.nArrows:
                    if time.time() - self.last_time_show_arrows > 1.4:
                        self.last_time_show_arrows = time.time()
                        self.showPV(rm.pv, self.nArrows)
                if self.thoughtOp > -1:
                    self.show_dispatch(self.thoughtOp, rm)

        if not self.timed:
            return

        def mira(xis_white):
            ot = self.vtime[xis_white]

            eti, eti2 = ot.etiquetaDif2()
            if eti:
                if xis_white:
                    self.main_window.set_clock_white(eti, eti2)
                else:
                    self.main_window.set_clock_black(eti, eti2)

            siJugador = self.human_side == xis_white
            if ot.time_is_consumed():
                if siJugador and QTUtil2.pregunta(
                    self.main_window,
                    _X(_("%1 has won on time."), self.xrival.name) + "\n\n" + _("Add time and keep playing?"),
                ):
                    minX = WPlayAgainstEngine.dameMinutosExtra(self.main_window)
                    if minX:
                        ot.add_extra_seconds(minX * 60)
                        return
                self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK if xis_white else RESULT_WIN_WHITE)
                self.state = ST_ENDGAME  # necesario que esté antes de stop_clock para no entrar en bucle
                self.stop_clock(siJugador)
                self.muestra_resultado()
                return

            elif siJugador and ot.is_zeitnot():
                self.beepZeitnot()

            return

        if Code.eboard:
            Code.eboard.writeClocks(self.vtime[True].label_dgt(), self.vtime[False].label_dgt())

        if self.human_is_playing:
            is_white = self.human_side
        else:
            is_white = not self.human_side
        mira(is_white)

    def start_clock(self, siUsuario):
        if self.timed:
            self.vtime[siUsuario == self.human_side].start_marker()
            self.vtime[not siUsuario].recalc()
            self.vtime[siUsuario == self.human_side].set_zeinot(self.zeitnot)

    def stop_clock(self, siUsuario):
        if self.timed:
            self.vtime[siUsuario == self.human_side].stop_marker()
            self.show_time(siUsuario)

    def run_action(self, key):
        if key == TB_CANCEL:
            self.finalizar()

        elif key == TB_RESIGN:
            self.rendirse()

        elif key == TB_DRAW:
            if self.tablasPlayer():
                self.muestra_resultado()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_PAUSE:
            self.xpause()

        elif key == TB_CONTINUE:
            self.xcontinue()

        elif key == TB_HELP_TO_MOVE:
            self.help_to_move()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            liMasOpciones = []
            if self.state == ST_PLAYING:
                liMasOpciones.append((None, None, None))
                liMasOpciones.append(("rival", _("Change opponent"), Iconos.Engine()))
            resp = self.configurar(liMasOpciones, siSonidos=True, siCambioTutor=self.ayudas_iniciales > 0)
            if resp == "rival":
                self.cambioRival()

        elif key == TB_UTILITIES:
            liMasOpciones = []
            if self.human_is_playing or self.is_finished():
                liMasOpciones.append(("books", _("Consult a book"), Iconos.Libros()))

            resp = self.utilidades(liMasOpciones)
            if resp == "books":
                siEnVivo = self.human_is_playing and not self.is_finished()
                liMovs = self.librosConsulta(siEnVivo)
                if liMovs and siEnVivo:
                    from_sq, to_sq, promotion = liMovs[-1]
                    self.player_has_moved(from_sq, to_sq, promotion)
            elif resp == "play":
                self.play_current_position()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key == TB_STOP:
            self.stop_engine()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def save_state(self):
        self.analizaTerminar()
        dic = self.reinicio

        # cache
        dic["cache"] = self.cache

        # game
        dic["game_save"] = self.game.save()

        # tiempos
        if self.timed:
            self.main_window.stop_clock()
            dic["time_white"] = self.vtime[WHITE].save()
            dic["time_black"] = self.vtime[BLACK].save()

        dic["is_tutor_enabled"] = self.is_tutor_enabled

        dic["hints"] = self.hints
        dic["summary"] = self.summary

        return dic

    def restore_state(self, dic):
        self.base_inicio(dic)
        self.game.restore(dic["game_save"])

        if self.timed:
            self.vtime[WHITE].restore(dic["time_white"])
            self.vtime[BLACK].restore(dic["time_black"])

        self.is_tutor_enabled = dic["is_tutor_enabled"]
        self.hints = dic["hints"]
        self.summary = dic["summary"]
        self.goto_end()

    def close_position(self, key):
        if key == TB_CLOSE:
            self.procesador.run_action(TB_QUIT)
        else:
            self.run_action(key)

    def play_position(self, dic, restore_game):
        self.ponRutinaAccionDef(self.close_position)
        game = Game.Game()
        game.restore(restore_game)
        player = self.configuration.nom_player()
        dic["FEN"] = game.last_position.fen()
        self.base_inicio(dic)
        other = self.xrival.name
        w, b = (player, other) if self.human_side else (other, player)
        game.set_tag("White", w)
        game.set_tag("Black", b)
        self.game = game
        self.goto_end()
        self.play_next_move()

    def reiniciar(self, siPregunta):
        if siPregunta:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
        if self.timed:
            self.main_window.stop_clock()
        self.analizaTerminar()
        if self.book_rival_select == "su" or self.nAjustarFuerza == ADJUST_SELECTED_BY_PLAYER:
            self.cache = {}
        self.reinicio["cache"] = self.cache
        self.game.reset()
        self.toolbar_state = ST_ENDGAME
        self.autosave()
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

            with Adjournments.Adjournments() as adj:
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

        self.pgnRefresh(not self.is_engine_side_white)
        self.play_next_move()

    def xpause(self):
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
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("End game?")):
                return False  # no abandona
            if self.timed:
                self.main_window.stop_clock()
                self.show_clocks(True)
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.ac_final(-1)
            self.state = ST_ENDGAME
            self.stop_engine()
            self.game.set_unknown()
            self.ponFinJuego(self.with_takeback)
            self.autosave()
        else:
            if self.timed:
                self.main_window.stop_clock()
            if self.is_analyzing:
                self.is_analyzing = False
                self.xtutor.ac_final(-1)
            self.state = ST_ENDGAME
            self.stop_engine()
            self.main_window.activaJuego(False, False)
            self.quitaCapturas()
            if self.xRutinaAccionDef:
                self.xRutinaAccionDef(TB_CLOSE)
            else:
                self.procesador.start()

        return False

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        if self.timed:
            self.main_window.stop_clock()
            self.show_clocks(True)
        if len(self.game) > 0:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
                return False  # no abandona
            self.analizaTerminar()
            self.game.set_termination(
                TERMINATION_RESIGN, RESULT_WIN_WHITE if self.is_engine_side_white else RESULT_WIN_BLACK
            )
            self.saveSummary()
            self.ponFinJuego(self.with_takeback)
            self.autosave()
        else:
            self.analizaTerminar()
            self.main_window.activaJuego(False, False)
            self.quitaCapturas()
            self.procesador.start()

        return False

    def analizaTerminar(self):
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
            self.ponAyudasEM()
            self.game.anulaUltimoMovimiento(self.human_side)
            if not self.fen:
                self.game.assign_opening()
            self.goto_end()
            self.reOpenBook()
            self.refresh()
            if self.state == ST_ENDGAME:
                self.state = ST_PLAYING
                self.toolbar_state = None
                self.pon_toolbar()
            self.check_boards_setposition()
            self.play_next_move()

    def testBook(self):
        if self.book_rival_active:
            resp = self.book_rival.get_list_moves(self.last_fen())
            if not resp:
                self.book_rival_active = False
                self.ponRotuloBasico()

    def reOpenBook(self):
        if self.book_rival:
            self.book_rival_active = True
            self.ponRotuloBasico()
        if self.book_player:
            self.book_player_active = True

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.rival_is_thinking = False
        self.put_view()

        is_white = self.game.is_white()

        if self.game.is_finished():
            self.muestra_resultado()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        if self.book_rival:
            self.testBook()

        if siRival:
            self.juegaRival(is_white)

        else:
            self.juegaHumano(is_white)

    def setSummary(self, key, value):
        njug = len(self.game)
        if not (njug in self.summary):
            self.summary[njug] = {}
        self.summary[njug][key] = value

    def analyze_begin(self):
        if not self.is_tutor_enabled:
            return
        self.is_analyzing = False
        self.is_analyzed_by_tutor = False
        if not self.tutor_con_flechas:
            if self.opening_mandatory or not self.is_tutor_enabled or self.ayudas_iniciales <= 0:
                return
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_end(self, is_mate=False):
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
        if not self.tutor_con_flechas:
            if self.is_analyzed_by_tutor or not self.is_tutor_enabled or self.ayudas_iniciales <= 0:
                return
        if self.is_analyzed_by_tutor:
            return
        self.main_window.pensando_tutor(True)
        if self.continueTt:
            self.mrmTutor = self.xtutor.ac_final(self.xtutor.mstime_engine)
        else:
            self.mrmTutor = self.xtutor.ac_final_limit()
        self.main_window.pensando_tutor(False)
        self.is_analyzed_by_tutor = True

    def ajustaPlayer(self, mrm):
        position = self.game.last_position

        FasterCode.set_fen(position.fen())
        li = FasterCode.get_exmoves()

        li_options = []
        for rm in mrm.li_rm:
            li_options.append(
                (rm, "%s (%s)" % (position.pgn_translated(rm.from_sq, rm.to_sq, rm.promotion), rm.abrTexto()))
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

    def eligeJugadaBookBase(self, book, book_select):
        fen = self.last_fen()

        if book_select == "su":
            listaJugadas = book.get_list_moves(fen)
            if listaJugadas:
                resp = WindowBooks.eligeJugadaBooks(self.main_window, listaJugadas, self.game.last_position.is_white)
                return True, resp[0], resp[1], resp[2]
        else:
            pv = book.eligeJugadaTipo(fen, book_select)
            if pv:
                return True, pv[:2], pv[2:4], pv[4:]

        return False, None, None, None

    def eligeJugadaBook(self):
        return self.eligeJugadaBookBase(self.book_rival, self.book_rival_select)

    def eligeJugadaBookAjustada(self):
        if self.nAjustarFuerza < 1000:
            return False, None, None, None
        dicPersonalidad = self.configuration.liPersonalidades[self.nAjustarFuerza - 1000]
        nombook = dicPersonalidad.get("BOOK", None)
        if (nombook is None) or (not Util.exist_file(nombook)):
            return False, None, None, None

        book = Books.Book("P", nombook, nombook, True)
        book.polyglot()
        return self.eligeJugadaBookBase(book, "pr")

    def juegaHumano(self, is_white):
        self.start_clock(True)
        self.timekeeper.start()
        self.human_is_playing = True
        last_position = self.game.last_position
        si_changed, from_sq, to_sq = self.board.piece_out_position(last_position)
        if si_changed:
            self.board.set_position(last_position)
            if from_sq:
                self.premove = from_sq, to_sq
        if self.premove:
            from_sq, to_sq = self.premove
            promotion = "q" if self.game.last_position.siPeonCoronando(from_sq, to_sq) else None
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

    def juegaRival(self, is_white):
        self.board.remove_arrows()
        self.start_clock(False)
        self.timekeeper.start()
        self.human_is_playing = False
        self.rival_is_thinking = True
        self.rm_rival = None
        self.pon_toolbar()
        if not self.is_tutor_enabled:
            self.activate_side(self.human_side)

        from_sq = to_sq = promotion = ""
        is_choosed = False

        # CACHE---------------------------------------------------------------------------------------------------------
        fen_ultimo = self.last_fen()
        if fen_ultimo in self.cache:
            move = self.cache[fen_ultimo]
            self.move_the_pieces(move.liMovs, True)
            self.add_move(move, False)
            if self.timed:
                self.vtime[self.is_engine_side_white].restore(move.cacheTime)
                self.show_clocks()
            return self.play_next_move()

        # OPENING MANDATORY---------------------------------------------------------------------------------------------
        if self.opening_mandatory:
            is_choosed, from_sq, to_sq, promotion = self.opening_mandatory.run_engine(fen_ultimo)
            if not is_choosed:
                self.opening_mandatory = None

        # BOOK----------------------------------------------------------------------------------------------------------
        if not is_choosed and self.book_rival_active:
            if self.book_rival_depth == 0 or self.book_rival_depth >= len(self.game):
                is_choosed, from_sq, to_sq, promotion = self.eligeJugadaBook()
                if not is_choosed:
                    self.book_rival_active = False
            else:
                self.book_rival_active = False
            self.ponRotuloBasico()

        if not is_choosed and self.siBookAjustarFuerza:
            is_choosed, from_sq, to_sq, promotion = self.eligeJugadaBookAjustada()  # book de la personalidad
            if not is_choosed:
                self.siBookAjustarFuerza = False

        # --------------------------------------------------------------------------------------------------------------
        if is_choosed:
            rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
            rm_rival.from_sq = from_sq
            rm_rival.to_sq = to_sq
            rm_rival.promotion = promotion
            self.play_rival(rm_rival)
        else:
            self.thinking(True)
            if self.timed:
                seconds_white = self.vtime[True].pending_time
                seconds_black = self.vtime[False].pending_time
                seconds_move = self.seconds_per_move
            else:
                seconds_white = seconds_black = self.unlimited_minutes * 60
                seconds_move = 0

            self.xrival.play_time_routine(
                self.game,
                self.main_window.notify,
                seconds_white,
                seconds_black,
                seconds_move,
                nAjustado=self.nAjustarFuerza,
                humanize=self.humanize,
            )

    def sigueHumanoAnalisis(self):
        self.analyze_begin()
        Manager.Manager.sigueHumano(self)

    def mueve_rival_base(self):
        self.play_rival(self.main_window.dato_notify)

    def play_rival(self, rm_rival):
        self.rival_is_thinking = False
        self.stop_clock(False)
        self.thinking(False)
        time_s = self.timekeeper.stop()
        self.setSummary("TIMERIVAL", time_s)

        if self.state in (ST_ENDGAME, ST_PAUSE):
            return self.state == ST_ENDGAME
        with_cache = True
        if self.nAjustarFuerza == ADJUST_SELECTED_BY_PLAYER and hasattr(rm_rival, "li_rm"):
            rm_rival = self.ajustaPlayer(rm_rival)
            with_cache = False

        self.lirm_engine.append(rm_rival)
        if not self.valoraRMrival():
            self.muestra_resultado()
            return True

        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, rm_rival.from_sq, rm_rival.to_sq, rm_rival.promotion
        )
        self.rm_rival = rm_rival
        if ok:
            fen_ultimo = self.last_fen()
            move.set_time_ms(int(time_s * 1000))
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)
            self.beepExtendido(False)
            if with_cache:
                if self.timed:
                    move.cacheTime = self.vtime[self.is_engine_side_white].save()
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

    def help_to_move(self):
        if not self.is_finished():
            move = Move.Move(self.game, position_before=self.game.last_position.copia())
            if self.is_tutor_enabled:
                self.analyze_end()
                move.analysis = self.mrmTutor, 0
            Analysis.show_analysis(
                self.procesador, self.xtutor, move, self.board.is_white_bottom, 999, 0, must_save=False
            )

    def juegaPorMi(self):
        if self.state != ST_PLAYING or self.is_finished():
            return

        if self.hints:
            self.hints -= 1

        fen_base = self.last_fen()

        if self.book_rival:
            listaJugadas = self.book_rival.get_list_moves(fen_base)
            if listaJugadas:
                apdesde, aphasta, appromotion, nada, nada1 = listaJugadas[0]
                return self.player_has_moved_base(apdesde, aphasta, appromotion)

        if self.opening_mandatory:
            apdesde, aphasta = self.opening_mandatory.from_to_active(fen_base)
            if apdesde:
                return self.player_has_moved_base(apdesde, aphasta)

        if self.is_tutor_enabled:
            self.analyze_end()
            rm = self.mrmTutor.mejorMov()
            return self.player_has_moved_base(rm.from_sq, rm.to_sq, rm.promotion)

        return Manager.Manager.juegaPorMi(self)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        if self.rival_is_thinking:
            return self.check_premove(from_sq, to_sq)
        move = self.check_human_move(from_sq, to_sq, promotion, not self.is_tutor_enabled)
        if not move:
            return False
        self.timekeeper.pause()
        a1h8 = move.movimiento()
        si_analisis = False
        is_choosed = False
        fen_base = self.last_fen()

        # OPENING MANDATORY---------------------------------------------------------------------------------------------
        if self.opening_mandatory:
            if self.opening_mandatory.check_human(fen_base, from_sq, to_sq):
                is_choosed = True
            else:
                apdesde, aphasta = self.opening_mandatory.from_to_active(fen_base)
                if apdesde is None:
                    self.opening_mandatory = None
                else:
                    self.board.ponFlechasTmp(((apdesde, aphasta, False),))
                    self.beepError()
                    self.timekeeper.restart()
                    self.sigueHumano()
                    return False

        # BOOK----------------------------------------------------------------------------------------------------------
        if not is_choosed and self.book_player_active:
            if self.book_player_depth == 0 or self.book_player_depth >= len(self.game):
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
                        self.board.ponFlechasTmp(li)
                        self.timekeeper.restart()
                        self.sigueHumano()
                        return False
                else:
                    self.book_player_active = False
            else:
                self.book_player_active = False
            self.ponRotuloBasico()

        # TUTOR---------------------------------------------------------------------------------------------------------
        is_mate = move.is_mate
        self.analyze_end(is_mate)  # tiene que acabar siempre
        if not is_mate and not is_choosed and self.is_tutor_enabled:
            if not self.tutor_book.si_esta(fen_base, a1h8):
                rm_user, n = self.mrmTutor.buscaRM(a1h8)
                if not rm_user:
                    self.main_window.pensando_tutor(True)
                    rm_user = self.xtutor.valora(self.game.last_position, from_sq, to_sq, move.promotion)
                    self.main_window.pensando_tutor(False)
                    if not rm_user:
                        self.timekeeper.restart()
                        self.sigueHumanoAnalisis()
                        return False
                    self.mrmTutor.agregaRM(rm_user)
                si_analisis = True
                pointsBest, pointsUser = self.mrmTutor.difPointsBest(a1h8)
                self.setSummary("POINTSBEST", pointsBest)
                self.setSummary("POINTSUSER", pointsUser)
                if Tutor.launch_tutor(self.mrmTutor, rm_user):
                    if not move.is_mate:
                        si_tutor = True
                        if self.chance:
                            num = self.mrmTutor.numMejorMovQue(a1h8)
                            if num:
                                rmTutor = self.mrmTutor.rmBest()
                                menu = QTVarios.LCMenu(self.main_window)
                                menu.opcion("None", _("There are %d best moves") % num, Iconos.Engine())
                                menu.separador()
                                resp = rmTutor.abrTextoBase()
                                if not resp:
                                    resp = _("Mate")
                                menu.opcion("tutor", "&1. %s (%s)" % (_("Show tutor"), resp), Iconos.Tutor())
                                menu.separador()
                                menu.opcion("try", "&2. %s" % _("Try again"), Iconos.Atras())
                                menu.separador()
                                menu.opcion(
                                    "user",
                                    "&3. %s (%s)" % (_("Select my move"), rm_user.abrTextoBase()),
                                    Iconos.Player(),
                                )
                                self.main_window.cursorFueraBoard()
                                resp = menu.lanza()
                                if resp == "try":
                                    self.timekeeper.restart()
                                    self.sigueHumanoAnalisis()
                                    return False
                                elif resp == "user":
                                    si_tutor = False
                                elif resp != "tutor":
                                    self.timekeeper.restart()
                                    self.sigueHumanoAnalisis()
                                    return False
                        if si_tutor:
                            tutor = Tutor.Tutor(self, move, from_sq, to_sq, False)

                            liApPosibles = self.listaOpeningsStd.list_possible_openings(self.game)

                            if tutor.elegir(self.hints > 0, liApPosibles=liApPosibles):
                                if self.hints > 0:  # doble entrada a tutor.
                                    self.set_piece_again(from_sq)
                                    self.hints -= 1
                                    self.tutor_con_flechas = self.nArrowsTt > 0 and self.hints > 0
                                    from_sq = tutor.from_sq
                                    to_sq = tutor.to_sq
                                    promotion = tutor.promotion
                                    ok, mens, jgTutor = Move.get_game_move(
                                        self.game, self.game.last_position, from_sq, to_sq, promotion
                                    )
                                    if ok:
                                        move = jgTutor
                                        self.setSummary("SELECTTUTOR", True)
                            if self.configuration.x_save_tutor_variations:
                                tutor.ponVariations(move, 1 + len(self.game) / 2)

                            del tutor

        # --------------------------------------------------------------------------------------------------------------
        secs_used = self.timekeeper.stop()
        move.set_time_ms(secs_used * 1000)
        self.setSummary("TIMEUSER", secs_used)
        self.stop_clock(True)

        if si_analisis:
            rm, nPos = self.mrmTutor.buscaRM(move.movimiento())
            if rm:
                move.analysis = self.mrmTutor, nPos

        self.add_move(move, True)
        self.move_the_pieces(move.liMovs, False)
        self.beepExtendido(True)

        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.show_clocks(True)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)

        self.ponAyudasEM()

        self.pgnRefresh(self.game.last_position.is_white)

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

    def muestra_resultado(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False
        if self.timed:
            self.main_window.stop_clock()

        mensaje, beep, player_win = self.game.label_resultado_player(self.human_side)

        self.beepResultado(beep)
        self.saveSummary()
        self.autosave()
        QTUtil.refresh_gui()
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        if QTUtil2.pregunta(self.main_window, mensaje + "\n\n" + _("Do you want to play again?"), px=p.x(), py=p.y()):
            self.reiniciar(False)
        else:
            self.ponFinJuego(self.with_takeback)

    def ponAyudasEM(self):
        self.ponAyudas(self.hints, siQuitarAtras=False)

    def cambioRival(self):
        dic = WPlayAgainstEngine.cambioRival(self.main_window, self.configuration, self.reinicio)

        if dic:
            dr = dic["RIVAL"]
            rival = dr["CM"]
            if hasattr(rival, "icono"):
                delattr(rival, "icono")

            Util.save_pickle(self.configuration.ficheroEntMaquina, dic)
            for k, v in dic.items():
                self.reinicio[k] = v

            is_white = dic["ISWHITE"]

            self.pon_toolbar()

            self.nAjustarFuerza = dic["ADJUST"]

            r_t = dr["TIME"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["DEPTH"]
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic["SITIEMPO"]:
                r_t = 1000

            dr["RESIGN"] = self.resign_limit
            self.xrival.terminar()
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, self.nAjustarFuerza != ADJUST_BETTER)

            self.xrival.is_white = not is_white

            rival = self.xrival.name
            player = self.configuration.x_player
            bl, ng = player, rival
            if not is_white:
                bl, ng = ng, bl
            self.main_window.change_player_labels(bl, ng)

            # self.put_pieces_bottom( is_white )
            self.ponRotuloBasico()

            self.put_pieces_bottom(is_white)
            if is_white != self.human_side:
                self.human_side = is_white
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
                % (rm.abrTextoBase(), rm.depth, seldepth, rm.time // 1000, nodes),
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

    def analize_position(self, row, key):
        if row < 0:
            return

        move, is_white, siUltimo, tam_lj, pos = self.dameJugadaEn(row, key)
        if not move:
            return

        max_recursion = 9999

        if not (hasattr(move, "analysis") and move.analysis):
            me = QTUtil2.mensEspera.start(self.main_window, _("Analyzing the move...."), physical_pos="ad")
            mrm, pos = self.xanalyzer.analysis_move(move, self.xanalyzer.mstime_engine, self.xanalyzer.depth_engine)
            move.analysis = mrm, pos
            me.final()

        Analysis.show_analysis(self.procesador, self.xanalyzer, move, self.board.is_white_bottom, max_recursion, pos)
        self.put_view()

    def show_clocks(self, with_recalc=False):
        if not self.vtime:
            return
        if with_recalc:
            for is_white in (WHITE, BLACK):
                self.vtime[is_white].recalc()

        if Code.eboard:
            Code.eboard.writeClocks(self.vtime[True].label_dgt(), self.vtime[False].label_dgt())

        for is_white in (WHITE, BLACK):
            ot = self.vtime[is_white]

            eti, eti2 = ot.etiquetaDif2()
            if eti:
                if is_white:
                    self.main_window.set_clock_white(eti, eti2)
                else:
                    self.main_window.set_clock_black(eti, eti2)

    def change_tutor_active(self):
        previous = self.is_tutor_enabled
        self.is_tutor_enabled = not previous
        self.set_activate_tutor(self.is_tutor_enabled)
        if previous:
            self.analyze_end()
        elif self.human_is_playing:
            self.analyze_begin()
