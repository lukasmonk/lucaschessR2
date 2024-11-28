import datetime
import random

import Code
from Code import Adjournments
from Code import Manager
from Code import Util
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    RS_WIN_PLAYER,
    RS_WIN_OPPONENT,
    RS_DRAW,
    GT_WICKER,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_DRAW,
    TB_RESIGN,
    TB_UTILITIES,
    BOOK_RANDOM_UNIFORM,
    BOOK_RANDOM_PROPORTIONAL,
    TERMINATION_RESIGN,
)
from Code.Books import Books
from Code.Engines import Engines, EngineResponse
from Code.Engines import EnginesWicker
from Code.QT import QTUtil2, QTUtil
from Code.SQL import UtilSQL


class DicWickerElos:
    def __init__(self):
        self.variable = "DicWickerElos"
        self.configuration = Code.configuration
        self._dic = self.configuration.read_variables(self.variable)

    def dic(self):
        return self._dic

    def cambia_elo(self, clave_motor, nuevo_elo):
        self._dic = self.configuration.read_variables(self.variable)
        self._dic[clave_motor] = nuevo_elo
        self.configuration.write_variables(self.variable, self._dic)


def lista():
    li = EnginesWicker.read_wicker_engines()
    dic_elos = DicWickerElos().dic()
    for mt in li:
        k = mt.alias
        if k in dic_elos:
            mt.elo = dic_elos[k]

    li.sort(key=lambda x: x.elo)
    return li


class ManagerWicker(Manager.Manager):
    li_t = None
    with_time = True

    @staticmethod
    def calc_dif_elo(elo_jugador, elo_rival, resultado):
        if resultado == RS_WIN_PLAYER:
            result = 1
        elif resultado == RS_DRAW:
            result = 0
        else:
            result = -1
        return Util.fideELO(elo_jugador, elo_rival, result)

    def list_engines(self, elo):
        self.li_t = (
            (0, 50, 3),
            (20, 53, 5),
            (40, 58, 4),
            (60, 62, 4),
            (80, 66, 5),
            (100, 69, 4),
            (120, 73, 3),
            (140, 76, 3),
            (160, 79, 3),
            (180, 82, 2),
            (200, 84, 9),
            (300, 93, 4),
            (400, 97, 3),
        )
        # self.liK = ((0, 60), (800, 50), (1200, 40), (1600, 30), (2000, 30), (2400, 10))

        li = []
        self.list_engines = lista()
        numX = len(self.list_engines)
        for num, mt in enumerate(self.list_engines):
            mtElo = mt.elo
            mt.siJugable = abs(mtElo - elo) < 400
            mt.siOut = not mt.siJugable
            mt.baseElo = elo  # servira para rehacer la lista y elegir en aplazamiento
            if mt.siJugable or (mtElo > elo):
                def rot(res):
                    return self.calc_dif_elo(elo, mtElo, res)

                def rrot(res):
                    return self.calc_dif_elo(mtElo, elo, res)

                mt.pgana = rot(RS_WIN_PLAYER)
                mt.ptablas = rot(RS_DRAW)
                mt.ppierde = rot(RS_WIN_OPPONENT)

                mt.rgana = rrot(RS_WIN_PLAYER)
                mt.rtablas = rrot(RS_DRAW)
                mt.rpierde = rrot(RS_WIN_OPPONENT)

                mt.number = numX - num

                li.append(mt)

        return li

    def start(self, engine_rival, minutos, seconds):
        self.base_inicio(engine_rival, minutos, seconds)
        self.start_message()
        self.play_next_move()

    def base_inicio(self, engine_rival, minutos, seconds, human_side=None):
        self.game_type = GT_WICKER

        self.engine_rival = engine_rival
        self.minutos = minutos
        self.seconds = seconds

        self.is_competitive = True

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING
        self.showed_result = False  # Problema doble asignacion de ptos Thomas

        if human_side is None:
            is_white = self.get_the_side(engine_rival)
        else:
            is_white = human_side

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -1000

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(False)
        self.ayudas_iniciales = self.hints = 0

        self.max_seconds = minutos * 60
        self.with_time = self.max_seconds > 0
        self.seconds_per_move = seconds if self.with_time else 0

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black

        if self.engine_rival.book:
            cbook = self.engine_rival.book
        else:
            path_rodent = Code.configuration.path_book("rodent.bin")
            cbook = random.choice([Code.tbook, path_rodent])

        self.book = Books.Book("P", cbook, cbook, True)
        self.book.polyglot()

        elo = self.engine_rival.elo
        self.maxMoveBook = (elo // 100) if 0 <= elo <= 1700 else 9999

        eloengine = self.engine_rival.elo
        eloplayer = self.configuration.wicker_elo()
        self.whiteElo = eloplayer if is_white else eloengine
        self.blackElo = eloplayer if not is_white else eloengine

        self.xrival = EnginesWicker.EngineManagerWicker(self.engine_rival)
        self.xrival.options(None, None, has_multipv=self.engine_rival.multiPV > 0)
        self.xrival.check_engine()

        self.pte_tool_resigndraw = False
        if self.is_human_side_white:
            self.pte_tool_resigndraw = True
            self.maxPlyRendirse = 1
        else:
            self.maxPlyRendirse = 0

        self.pon_toolbar()

        self.main_window.active_game(True, self.with_time)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        self.remove_hints(True, siQuitarAtras=True)
        self.show_side_indicator(True)

        nbsp = "&nbsp;" * 3

        txt = "%s:%+d%s%s:%+d%s%s:%+d" % (
            _("Win"),
            self.engine_rival.pgana,
            nbsp,
            _("Draw"),
            self.engine_rival.ptablas,
            nbsp,
            _("Loss"),
            self.engine_rival.ppierde,
        )
        self.set_label1("<center>%s</center>" % txt)
        self.set_label2("")
        self.pgn_refresh(True)
        self.show_info_extra()

        rival_name = self.engine_rival.name
        self.rival = "%s (%d)" % (rival_name, self.engine_rival.elo)
        white_name, black_name = self.configuration.nom_player(), rival_name
        white_elo, black_elo = self.configuration.wicker_elo(), self.engine_rival.elo
        if self.is_engine_side_white:
            white_name, black_name = black_name, white_name
            white_elo, black_elo = black_elo, white_elo

        self.game.set_tag("Event", _("Tourney-Elo"))

        self.game.set_tag("White", white_name)
        self.game.set_tag("Black", black_name)
        self.game.set_tag("WhiteElo", str(white_elo))
        self.game.set_tag("BlackElo", str(black_elo))

        white_player = white_name + " (%d)" % white_elo
        black_player = black_name + " (%d)" % black_elo

        if self.with_time:
            time_control = "%d" % int(self.max_seconds)
            if self.seconds_per_move:
                time_control += "+%d" % self.seconds_per_move
            self.game.set_tag("TimeControl", time_control)

            self.tc_player.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)
            self.tc_rival.config_clock(self.max_seconds, self.seconds_per_move, 0, 0)

            tp_bl, tp_ng = self.tc_white.label(), self.tc_black.label()
            self.main_window.set_data_clock(white_player, tp_bl, black_player, tp_ng)
            self.main_window.start_clock(self.set_clock, 1000)

        else:
            self.set_label1("%s: <b>%s</b><br>%s: <b>%s</b>" % (_("White"), white_player, _("Black"), black_player))

        self.refresh()

        self.check_boards_setposition()

        self.game.add_tag_timestart()

    def pon_toolbar(self):
        if self.pte_tool_resigndraw:
            liTool = (TB_CANCEL, TB_ADJOURN, TB_TAKEBACK, TB_CONFIG, TB_UTILITIES)
        else:
            liTool = (TB_RESIGN, TB_DRAW, TB_ADJOURN, TB_CONFIG, TB_UTILITIES)

        self.set_toolbar(liTool)

    def run_action(self, key):
        if key in (TB_RESIGN, TB_CANCEL):
            self.rendirse()

        elif key == TB_DRAW:
            self.tablasPlayer()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def save_state(self):
        self.main_window.stop_clock()
        self.tc_white.stop()
        self.tc_black.stop()

        dic = {
            "engine_rival": self.engine_rival.save(),
            "minutos": self.minutos,
            "seconds": self.seconds,
            "game_save": self.game.save(),
            "time_white": self.tc_white.save(),
            "time_black": self.tc_black.save(),
            "pgana": self.engine_rival.pgana,
            "ptablas": self.engine_rival.ptablas,
            "ppierde": self.engine_rival.ppierde,
            "alias": self.engine_rival.alias,
            "human_side": self.is_human_side_white,
        }

        return dic

    def restore_state(self, dic):
        engine_rival = Engines.Engine()
        engine_rival.restore(dic["engine_rival"])
        engine_rival.pgana = dic["pgana"]
        engine_rival.ptablas = dic["ptablas"]
        engine_rival.ppierde = dic["ppierde"]
        engine_rival.alias = dic["alias"]

        minutos = dic["minutos"]
        seconds = dic["seconds"]

        self.base_inicio(
            engine_rival, minutos, seconds, human_side=dic.get("human_side")
        )

        self.game.restore(dic["game_save"])

        self.tc_white.restore(dic["time_white"])
        self.tc_black.restore(dic["time_black"])

        self.goto_end()

    def adjourn(self):
        if QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = self.save_state()

            # se guarda en una bd Adjournments dic key = fecha y hora y tipo
            label_menu = _("The Wicker Park Tourney") + ". " + self.engine_rival.name

            self.state = ST_ENDGAME

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        self.restore_state(dic)
        self.check_boards_setposition()
        self.start_message()
        self.show_clocks()
        self.play_next_move()

    def final_x(self):
        return self.rendirse()

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        if (len(self.game) > 0) and not self.pte_tool_resigndraw:
            if not QTUtil2.pregunta(
                    self.main_window,
                    _("Do you want to resign?") + " (%d)" % self.engine_rival.ppierde,
            ):
                return False  # no abandona
            self.game.resign(self.is_human_side_white)
            self.show_result()
        else:
            self.procesador.start()

        return False

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        if self.game.is_finished():
            self.show_result()
            return

        is_rival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if is_rival:
            self.tc_rival.start()
            self.thinking(True)
            self.disable_all()

            si_encontrada = False

            if self.book:
                if self.game.last_position.num_moves >= self.maxMoveBook:
                    self.book = None
                else:
                    fen = self.last_fen()
                    pv = self.book.eligeJugadaTipo(fen, BOOK_RANDOM_UNIFORM if len(
                        self.game) > 2 else BOOK_RANDOM_PROPORTIONAL)
                    if pv:
                        rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
                        rm_rival.from_sq = pv[:2]
                        rm_rival.to_sq = pv[2:4]
                        rm_rival.promotion = pv[4:]
                        si_encontrada = True
                    else:
                        self.book = None
            if not si_encontrada:
                if self.with_time:
                    time_white = self.tc_white.pending_time
                    time_black = self.tc_black.pending_time
                else:
                    time_white = int(5 * 60 * self.whiteElo / 1500)
                    time_black = int(5 * 60 * self.blackElo / 1500)
                rm_rival = self.xrival.play_time(self.game, time_white, time_black, self.seconds_per_move)
                if rm_rival is None:
                    self.thinking(False)
                    return False

            self.thinking(False)
            if self.rival_has_moved(rm_rival):
                self.lirm_engine.append(rm_rival)
                if self.valoraRMrival():
                    self.play_next_move()
                else:
                    if self.game.is_finished():
                        self.show_result()
                        return
            else:
                self.game.set_termination(TERMINATION_RESIGN, RS_WIN_PLAYER)
                self.show_result()
                return
        else:
            self.tc_player.start()

            self.human_is_playing = True
            self.activate_side(is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        time_s = self.stop_clock(True)
        if time_s > 0.005:
            move.set_time_ms(time_s * 1000)
            move.set_clock_ms(self.tc_player.pending_time * 1000)

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.play_next_move()
        return True

    def rival_has_moved(self, engine_response):
        from_sq = engine_response.from_sq
        to_sq = engine_response.to_sq

        promotion = engine_response.promotion

        ok, mens, move = Move.get_game_move(
            self.game, self.game.last_position, from_sq, to_sq, promotion
        )
        if ok:
            time_s = self.stop_clock(False)
            move.set_time_ms(time_s * 1000)
            move.set_clock_ms(self.tc_rival.pending_time * 1000)
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

        if self.pte_tool_resigndraw:
            if len(self.game) > self.maxPlyRendirse:
                self.pte_tool_resigndraw = False
                self.pon_toolbar()

    def show_result(self):
        if self.showed_result:  # Problema doble asignacion de ptos Thomas
            return
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False
        self.main_window.stop_clock()

        mensaje, beep, player_win = self.game.label_resultado_player(
            self.is_human_side_white
        )

        self.beep_result(beep)
        self.autosave()
        QTUtil.refresh_gui()

        elo = self.configuration.wicker_elo()
        relo = self.engine_rival.elo
        if player_win:
            difelo = self.engine_rival.pgana

        elif self.game.is_draw():
            difelo = self.engine_rival.ptablas

        else:
            difelo = self.engine_rival.ppierde

        nelo = elo + difelo
        if nelo < 0:
            nelo = 0
        self.configuration.set_wicker(nelo)

        rnelo = relo - difelo
        if rnelo < 100:
            rnelo = 100
        dme = DicWickerElos()
        dme.cambia_elo(self.engine_rival.alias, rnelo)
        # TODO en el mensaje poner el elo con el que queda el rival, self.rival incluye el elo antiguo, hay que indicar el elo nuevo

        self.historial(elo, nelo)
        self.configuration.graba()

        mensaje += "\n\n%s : %d\n" % (_("Elo"), nelo)

        self.showed_result = True
        self.message_on_pgn(mensaje)
        self.set_end_game()

    def historial(self, elo, nelo):
        dic = {}
        dic["FECHA"] = datetime.datetime.now()
        dic["RIVAL"] = self.engine_rival.name
        dic["RESULTADO"] = self.resultado
        dic["AELO"] = elo
        dic["NELO"] = nelo

        lik = UtilSQL.ListSQL(self.configuration.fichEstadWicker)
        lik.append(dic)
        lik.close()

        dd = UtilSQL.DictSQL(self.configuration.fichEstadWicker, tabla="color")
        key = self.engine_rival.name
        dd[key] = self.is_human_side_white
        dd.close()

    def get_the_side(self, engine_rival):
        key = engine_rival.name

        dd = UtilSQL.DictSQL(self.configuration.fichEstadWicker, tabla="color")
        previo = dd.get(key, random.randint(0, 1) == 0)
        dd.close()
        return not previo

    def set_clock(self):
        if self.state != ST_PLAYING:
            return

        def mira(is_white):
            tc = self.tc_white if is_white else self.tc_black
            tc.set_labels()

            if tc.time_is_consumed():
                self.game.set_termination_time()
                self.show_result()
                return False

            return True

        if Code.eboard:
            Code.eboard.writeClocks(
                self.tc_white.label_dgt(), self.tc_black.label_dgt()
            )

        if self.human_is_playing:
            is_white = self.is_human_side_white
        else:
            is_white = not self.is_human_side_white
        return mira(is_white)

    def stop_clock(self, is_player):
        tc = self.tc_player if is_player else self.tc_rival
        secs = tc.stop()
        self.show_clocks()
        return secs

    def show_clocks(self):
        if Code.eboard:
            Code.eboard.writeClocks(
                self.tc_white.label_dgt(), self.tc_black.label_dgt()
            )

        self.tc_white.set_labels()
        self.tc_black.set_labels()
