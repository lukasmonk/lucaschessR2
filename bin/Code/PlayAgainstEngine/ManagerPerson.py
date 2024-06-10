from Code.Base.Constantes import (
    ST_PLAYING,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_PAUSE,
    TB_RESIGN,
    TB_UTILITIES,
    GT_AGAINST_CHILD_ENGINE,
)
from Code.Openings import Opening
from Code.PlayAgainstEngine import ManagerPlayAgainstEngine
from Code.QT import QTVarios


class ManagerPerson(ManagerPlayAgainstEngine.ManagerPlayAgainstEngine):
    def base_inicio(self, dic_var):
        self.reinicio = dic_var

        self.cache = dic_var.get("cache", {})

        self.game_type = GT_AGAINST_CHILD_ENGINE

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.summary = {}  # movenum : "a"ccepted, "s"ame, "r"ejected, dif points, time used
        self.with_summary = dic_var.get("SUMMARY", False)

        is_white = dic_var["ISWHITE"]
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.with_takeback = True

        cmrival = self.configuration.buscaRival("irina", None)
        self.xrival = self.procesador.creaManagerMotor(cmrival, None, 2)
        imagen = None
        for name, trans, ico, elo in QTVarios.list_irina():
            if name == dic_var["RIVAL"]:
                self.xrival.name = trans
                imagen = ico.pixmap(ico.availableSizes()[0])
                break
        self.xrival.set_option("Personality", dic_var["RIVAL"])
        if not dic_var["FASTMOVES"]:
            self.xrival.set_option("Max Time", "5")
            self.xrival.set_option("Min Time", "1")

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -99999  # never

        self.aperturaObl = self.aperturaStd = None

        self.human_is_playing = False
        self.state = ST_PLAYING
        self.is_analyzing = False

        self.aperturaStd = Opening.OpeningPol(1)

        self.set_dispatcher(self.player_has_moved)
        self.main_window.set_notify(self.mueve_rival_base)

        self.thinking(True)

        self.main_window.set_activate_tutor(False)

        self.hints = 0
        self.ayudas_iniciales = 0

        self.xrival.is_white = self.is_engine_side_white

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black

        self.timed = dic_var["SITIEMPO"]
        self.tc_white.set_displayed(self.timed)
        self.tc_black.set_displayed(self.timed)
        if self.timed:
            max_seconds = dic_var["MINUTOS"] * 60.0
            seconds_per_move = dic_var["SEGUNDOS"]
            secs_extra = dic_var.get("MINEXTRA", 0) * 60.0

            self.tc_player.config_clock(max_seconds, seconds_per_move, 0.0, secs_extra)
            self.tc_rival.config_clock(max_seconds, seconds_per_move, 0.0, secs_extra)

            time_control = "%d" % int(self.max_seconds)
            if seconds_per_move:
                time_control += "+%d" % seconds_per_move
            self.game.set_tag("TimeControl", time_control)

        self.thinking(False)

        li = [TB_CANCEL, TB_RESIGN, TB_TAKEBACK, TB_REINIT, TB_ADJOURN, TB_PAUSE, TB_CONFIG, TB_UTILITIES]
        self.set_toolbar(li)

        self.main_window.active_game(True, self.timed)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints(True, siQuitarAtras=False)
        self.put_pieces_bottom(is_white)

        self.main_window.base.lbRotulo1.put_image(imagen)
        self.main_window.base.lbRotulo1.show()

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

        if self.timed:
            tp_bl, tp_ng = self.tc_white.label(), self.tc_black.label()

            self.main_window.set_data_clock(bl, tp_bl, ng, tp_ng)
            self.refresh()
        else:
            self.main_window.base.change_player_labels(bl, ng)

        self.main_window.start_clock(self.set_clock, 1000)
        self.main_window.set_notify(self.mueve_rival_base)

        self.check_boards_setposition()

        w, b = self.configuration.nom_player(), self.xrival.name
        if not is_white:
            w, b = b, w
        self.game.set_tag("Event", _("Opponents for young players"))
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.game.add_tag_timestart()
