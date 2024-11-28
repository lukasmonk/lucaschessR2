import random

import Code
from Code import Adjournments
from Code import Manager
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CONTINUE,
    TB_DRAW,
    TB_PAUSE,
    TB_RESIGN,
    TB_UTILITIES,
    GT_AGAINST_ENGINE_LEAGUE,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    RESULT_DRAW,
    TERMINATION_RESIGN,
    TERMINATION_WIN_ON_TIME,
    TERMINATION_DRAW_AGREEMENT,
    WHITE,
    BLACK,
    ST_PAUSE,
)
from Code.Leagues import WLeagues, Leagues
from Code.QT import QTUtil
from Code.QT import QTUtil2


class ManagerLeague(Manager.Manager):
    league: Leagues.League
    xmatch: Leagues.Match
    division: int
    engine_side: bool

    tc_player = None
    tc_rival = None

    human_side = False
    is_engine_side_white = False
    conf_engine = None
    lirm_engine = None
    next_test_resign = 0
    resign_limit = -99999
    max_seconds = 0
    seconds_move = 0
    zeitnot = 0
    toolbar_state = None
    premove = None
    last_time_show_arrows = None
    rival_is_thinking = False

    def start(self, league: Leagues.League, xmatch: Leagues.Match, division: int):
        self.base_inicio(league, xmatch, division)
        self.xrival.check_engine()
        self.start_message(nomodal=Code.eboard and Code.is_linux)  # nomodal: problema con eboard

        self.play_next_move()

    def base_inicio(self, league: Leagues.League, xmatch: Leagues.Match, division: int):

        self.league = league
        self.season = league.read_season()
        self.xmatch = xmatch
        self.division = division

        opponent_w: Leagues.Opponent
        opponent_b: Leagues.Opponent
        opponent_w, opponent_b = self.xmatch.get_opponents(league)

        self.game_type = GT_AGAINST_ENGINE_LEAGUE

        self.human_is_playing = False
        self.rival_is_thinking = False
        self.state = ST_PLAYING

        self.is_human_side_white = WHITE if opponent_w.is_human() else BLACK
        self.engine_side = WHITE if self.is_human_side_white == BLACK else BLACK
        self.is_engine_side_white = self.engine_side == WHITE

        opponent_engine = xmatch.get_engine(league, self.engine_side)
        self.conf_engine = opponent_engine.opponent

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -99999  # never

        self.main_window.set_activate_tutor(False)

        self.xrival = self.procesador.creaManagerMotor(
            self.conf_engine, self.conf_engine.max_time * 1000, self.conf_engine.max_depth
        )
        self.resign_limit = league.resign

        self.game.set_tag("Event", _("Chess leagues"))
        self.game.set_tag("Site", league.name())
        self.game.set_tag("Division", str(division + 1))

        self.game.set_tag("White", opponent_w.name())
        self.game.set_tag("Black", opponent_b.name())

        self.xrival.is_white = self.is_engine_side_white

        minutes, self.seconds_per_move = league.time_engine_human
        self.max_seconds = minutes * 60.0

        self.timed = minutes > 0.0

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black

        self.tc_player.set_displayed(self.timed)
        self.tc_rival.set_displayed(self.timed)

        if self.timed:
            time_control = "%d" % int(self.max_seconds)
            if self.seconds_per_move:
                time_control += "+%d" % self.seconds_per_move
            self.game.set_tag("TimeControl", time_control)

            self.tc_player.config_clock(minutes * 60, self.seconds_per_move, 0, 0)
            self.tc_rival.config_clock(minutes * 60, self.seconds_per_move, 0, 0)

        self.pon_toolbar()

        self.main_window.active_game(True, self.timed)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints(siQuitarAtras=True)
        self.put_pieces_bottom(self.is_human_side_white)

        self.show_info_extra()

        self.pgn_refresh(True)

        bl = opponent_w.name()
        ng = opponent_b.name()

        if self.timed:
            tp_bl, tp_ng = self.tc_white.label(), self.tc_black.label()
            self.main_window.set_data_clock(bl, tp_bl, ng, tp_ng)
            self.refresh()
            self.main_window.start_clock(self.set_clock, 1000)
        else:
            self.main_window.base.change_player_labels(bl, ng)

        self.main_window.set_notify(self.mueve_rival_base)

        self.game.add_tag_timestart()

        self.check_boards_setposition()

    def pon_toolbar(self):
        if self.state == ST_PLAYING:
            if self.toolbar_state != self.state:
                li = [TB_RESIGN, TB_DRAW, TB_PAUSE, TB_ADJOURN, TB_CONFIG, TB_UTILITIES]

                self.set_toolbar(li)
            hip = self.human_is_playing
            self.main_window.enable_option_toolbar(TB_RESIGN, hip)
            self.main_window.enable_option_toolbar(TB_DRAW, hip)
            self.main_window.enable_option_toolbar(TB_CONFIG, hip)
            self.main_window.enable_option_toolbar(TB_UTILITIES, hip)
            self.main_window.enable_option_toolbar(TB_ADJOURN, hip)

        elif self.state == ST_PAUSE:
            li = [TB_CONTINUE]
            self.set_toolbar(li)
        else:
            li = [TB_CLOSE]
            self.set_toolbar(li)

        self.toolbar_state = self.state

    def show_time(self, is_player):
        ot = self.tc_player if is_player else self.tc_rival
        ot.set_labels()

    def set_clock(self):
        if not self.timed:
            return

        if self.state == ST_ENDGAME:
            self.main_window.stop_clock()
            return
        if self.state != ST_PLAYING:
            return

        def mira(xis_white):
            ot = self.tc_white if xis_white else self.tc_black
            ot.set_labels()

            is_the_player = self.is_human_side_white == xis_white
            if ot.time_is_consumed():
                self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK if xis_white else RESULT_WIN_WHITE)
                self.state = ST_ENDGAME  # necesario que esté antes de stop_clock para no entrar en bucle
                self.stop_clock(is_the_player)
                self.show_result()
                return

            elif is_the_player and ot.is_zeitnot():
                self.beep_zeitnot()

            return

        if Code.eboard:
            Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

        if self.human_is_playing:
            is_white = self.is_human_side_white
        else:
            is_white = not self.is_human_side_white
        mira(is_white)

    def start_clock(self, is_player):
        tc = self.tc_player if is_player else self.tc_rival
        tc.start()
        if self.timed:
            tc.set_labels()

    def stop_clock(self, is_player):
        tc = self.tc_player if is_player else self.tc_rival
        time_s = tc.stop()
        if self.timed:
            tc.set_labels()
        return time_s

    def run_action(self, key):
        if key == TB_RESIGN:
            self.rendirse()

        elif key == TB_DRAW:
            self.tablasPlayer()

        elif key == TB_PAUSE:
            self.xpause()

        elif key == TB_CONTINUE:
            self.xcontinue()

        elif key == TB_CONFIG:
            self.configurar([], with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key == TB_CLOSE:
            self.procesador.start()
            WLeagues.play_league(self.main_window, self.league)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def save_state(self):
        dic = {
            "league_name": self.league.name(),
            "match_saved": self.xmatch.save(),
            "division": self.division,
            "game_save": self.game.save(),
            "timed": self.timed,
        }

        if self.timed:
            self.main_window.stop_clock()
            dic["time_white"] = self.tc_white.save()
            dic["time_black"] = self.tc_black.save()

        return dic

    def restore_state(self, dic):
        league = Leagues.League(dic["league_name"])
        xmatch = Leagues.Match("", "")
        xmatch.restore(dic["match_saved"])
        division = dic["division"]
        self.base_inicio(league, xmatch, division)
        self.game.restore(dic["game_save"])

        if dic.get("timed"):
            self.tc_white.restore(dic["time_white"])
            self.tc_black.restore(dic["time_black"])

        self.goto_end()

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            # se guarda en una bd Adjournments dic key = fecha y hora y tipo
            label_menu = "%s: %s vs %s" % (self.league.name(), self.game.get_tag("WHITE"), self.game.get_tag("BLACK"))

            self.state = ST_ENDGAME

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        self.restore_state(dic)
        self.check_boards_setposition()
        self.show_clocks()
        self.xrival.check_engine()
        self.start_message()
        self.pgn_refresh(not self.is_engine_side_white)
        self.play_next_move()

    def xpause(self):
        self.state = ST_PAUSE
        self.thinking(False)
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
        if self.state != ST_ENDGAME:
            return self.rendirse()
        return True

    def stop_engine(self):
        if not self.human_is_playing:
            self.xrival.stop()

    def save_match(self):
        self.season.put_match_done(self.xmatch, self.game)

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        self.main_window.stop_clock()
        self.show_clocks()
        if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
            return False  # no abandona
        self.game.set_termination(
            TERMINATION_RESIGN, RESULT_WIN_WHITE if self.is_engine_side_white else RESULT_WIN_BLACK
        )
        self.set_end_game()
        self.autosave()
        self.save_match()

        return False

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

        siRival = is_white == self.is_engine_side_white

        if siRival:
            self.play_rival(is_white)

        else:
            self.play_human(is_white)

    def play_human(self, is_white):
        self.start_clock(True)
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

        self.activate_side(is_white)

    def play_rival(self, is_white):
        self.board.remove_arrows()
        self.start_clock(False)
        self.human_is_playing = False
        self.rival_is_thinking = True
        self.rm_rival = None
        self.pon_toolbar()
        self.activate_side(self.is_human_side_white)

        self.thinking(True)
        if self.timed:
            seconds_white = self.tc_white.pending_time
            seconds_black = self.tc_black.pending_time
            seconds_move = self.seconds_per_move
        else:
            seconds_black = seconds_white = 10 * 60
            seconds_move = 0
        self.xrival.play_time_routine(self.game, self.main_window.notify, seconds_white, seconds_black, seconds_move)

    def mueve_rival_base(self):
        self.rival_has_moved(self.main_window.dato_notify)

    def rival_has_moved(self, rm_rival):
        self.rival_is_thinking = False
        time_s = self.stop_clock(False)
        self.thinking(False)

        if self.state in (ST_ENDGAME, ST_PAUSE):
            return self.state == ST_ENDGAME

        self.lirm_engine.append(rm_rival)
        if not self.check_draw_resign():
            self.show_result()
            return True

        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, rm_rival.from_sq, rm_rival.to_sq, rm_rival.promotion
        )
        self.rm_rival = rm_rival
        if ok:
            move.set_time_ms(int(time_s * 1000))
            move.set_clock_ms(self.tc_rival.pending_time * 1000)
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)
            self.beep_extended(False)
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

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        if self.rival_is_thinking:
            return self.check_premove(from_sq, to_sq)
        move = self.check_human_move(from_sq, to_sq, promotion, True)
        if not move:
            return False

        time_s = self.stop_clock(True)
        move.set_time_ms(time_s * 1000)
        move.set_clock_ms(self.tc_player.pending_time * 1000)

        self.add_move(move, True)
        self.move_the_pieces(move.liMovs, False)
        self.beep_extended(True)

        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.show_clocks()
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)

        self.pgn_refresh(self.game.last_position.is_white)

        self.refresh()

    def show_result(self):
        self.save_match()
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False
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
        self.autosave()
        QTUtil.refresh_gui()
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        QTUtil2.message(self.main_window, mensaje, px=p.x(), py=p.y(), si_bold=True)
        self.set_end_game()

    def show_clocks(self):
        if self.timed:
            if Code.eboard:
                Code.eboard.writeClocks(self.tc_white.label_dgt(), self.tc_black.label_dgt())

            self.tc_white.set_labels()
            self.tc_black.set_labels()

    def check_draw_resign(self):
        all_zero = True
        for rm in self.lirm_engine:
            if rm.centipawns_abs() != 0:
                all_zero = False
                break
        if all_zero:
            return True

        if len(self.game) < 50 or len(self.lirm_engine) <= 5:
            return True
        if self.next_test_resign:  # includes test draw
            self.next_test_resign -= 1
            return True

        b = random.random() ** 0.33

        # Resign
        if self.league.resign > 0:
            si_resign = True
            for n, rm in enumerate(self.lirm_engine[-5:]):
                if rm.centipawns_abs() >= -100:
                    si_resign = False
                    break
                if int(-rm.centipawns_abs() * b) < self.league.resign:
                    si_resign = False
                    break
            if si_resign:
                resp = QTUtil2.pregunta(
                    self.main_window, _X(_("%1 wants to resign, do you accept it?"), self.xrival.name)
                )
                if resp:
                    self.game.resign(self.is_engine_side_white)
                    return False
                else:
                    self.next_test_resign = 9
                    return True

        # Draw
        if (self.league.draw_min_ply > 0) and (len(self.game) >= self.league.draw_min_ply):
            si_draw = True
            for rm in self.lirm_engine[-5:]:
                pts = rm.centipawns_abs()
                if pts > -100 or pts < -250:
                    si_draw = False
                    break
            if si_draw:
                resp = QTUtil2.pregunta(
                    self.main_window, _X(_("%1 proposes draw, do you accept it?"), self.xrival.name)
                )
                if resp:
                    self.game.last_jg().is_draw_agreement = True
                    self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
                    return False
                else:
                    self.next_test_resign = 9
                    return True

        return True
