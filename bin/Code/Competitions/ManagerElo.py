import datetime
import random
import time

import OSEngines

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
    GT_ELO,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_DRAW,
    TB_RESIGN,
    TB_UTILITIES,
)
from Code.Engines import EngineResponse
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL


# Se elimina cinnamon, se bloquea en los mates con profundidad fija
# position startpos moves e2e4 d7d5 e4d5 d8d5 b1c3 d5e5 f1e2 c8g4 d2d4 g4e2 g1e2 e5f5 d1d3 f5d3 c2d3 b8c6 c1f4 e8c8 c3b5 g8f6 f4c7 d8d5 e2c3 d5g5 c7g3 e7e6 h2h4 g5f5 g3d6 g7g6 d6f8 f5b5 f8g7 h8g8 c3b5 g8g7 a1c1 f6d5 b5a7 c8d7 a7c6 b7c6 e1d2 g7g8 h1e1 g8b8 b2b3 b8a8 a2a4 d7d6 c1c5 a8b8 e1c1 b8b3 c5c6 d6d7 c6c8 b3b2 d2e1 d7d6 e1f1 h7h5 a4a5 d6d7 a5a6 b2a2 c8f8 a2a6 f8f7 d7d6 f7g7 d5f4 c1b1 a6a2 b1b6 d6d5
# go depth 2


def listaMotoresElo():
    x = """amyan|1|1112|5461
amyan|2|1360|6597
amyan|3|1615|7010
amyan|4|1914|7347
alaric|1|1151|5442
alaric|2|1398|6552
alaric|3|1781|7145
alaric|4|2008|7864
bikjump|1|1123|4477
bikjump|2|1204|5352
bikjump|3|1405|5953
bikjump|4|1710|6341
cheng|1|1153|5728
cheng|2|1402|6634
cheng|3|1744|7170
cheng|4|1936|7773
chispa|1|1109|5158
chispa|2|1321|6193
chispa|3|1402|6433
chispa|4|1782|7450
clarabit|1|1134|5210
clarabit|2|1166|6014
clarabit|3|1345|6407
clarabit|4|1501|6863
critter|1|1203|6822
critter|2|1618|7519
critter|3|1938|8196
critter|4|2037|8557
cyrano|1|1184|5587
cyrano|2|1392|6688
cyrano|3|1929|7420
cyrano|4|2033|7945
daydreamer|2|1358|6362
daydreamer|3|1381|6984
daydreamer|4|1629|7462
discocheck|1|1131|6351
discocheck|2|1380|6591
discocheck|3|1613|7064
discocheck|4|1817|7223
fruit|1|1407|6758
fruit|2|1501|6986
fruit|3|1783|7446
fruit|4|1937|8046
gaia|2|1080|5734
gaia|3|1346|6582
gaia|4|1766|7039
garbochess|1|1149|5640
garbochess|2|1387|6501
garbochess|3|1737|7231
garbochess|4|2010|7933
gaviota|1|1166|6503
gaviota|2|1407|7127
gaviota|3|1625|7437
gaviota|4|2026|7957
glaurung|2|1403|6994
glaurung|3|1743|7578
glaurung|4|2033|7945
greko|1|1151|5552
greko|2|1227|6282
greko|3|1673|6861
greko|4|1931|7518
hamsters|1|1142|5779
hamsters|2|1386|6365
hamsters|3|1649|7011
hamsters|4|1938|7457
komodo|1|1187|6636
komodo|2|1514|7336
komodo|3|1633|7902
komodo|4|2036|8226
lime|1|1146|5251
lime|2|1209|6154
lime|3|1500|6907
lime|4|1783|7499
pawny|2|1086|6474
pawny|3|1346|6879
pawny|4|1503|7217
rhetoric|1|1147|5719
rhetoric|2|1371|6866
rhetoric|3|1514|7049
rhetoric|4|1937|7585
rybka|1|1877|8203
rybka|2|2083|8675
rybka|3|2237|9063
rybka|4|2290|9490
simplex|1|1126|4908
simplex|2|1203|5868
simplex|3|1403|6525
simplex|4|1757|7265
stockfish|1|1200|6419
stockfish|2|1285|6252
stockfish|3|1382|6516
stockfish|4|1561|6796
texel|1|1165|6036
texel|2|1401|7026
texel|3|1506|7255
texel|4|1929|7813
toga|1|1202|6066
toga|2|1497|6984
toga|3|2031|7639
toga|4|2038|8254
ufim|1|1214|6161
ufim|2|1415|7260
ufim|3|2014|8032
ufim|4|2104|8363
umko|1|1151|6004
umko|2|1385|6869
umko|3|1883|7462
umko|4|2081|7887"""
    li = []
    dic_engines = OSEngines.read_engines(Code.folder_engines)

    for linea in x.split("\n"):
        key, depth, fide, sts = linea.split("|")
        if key in dic_engines:
            depth = int(depth)
            sts = int(sts)
            fide = int(fide)
            elo = int((fide + 0.2065 * sts + 154.51) / 2)
            li.append((elo, key, depth))
    return li


# li = listaMotoresElo()
# li.sort(key=lambda x: x[0])
# for x, y, z in li:
#     pr int(x, y)
# p rint(len(li))


class MotorElo:
    def __init__(self, elo, name, key, depth):
        self.elo = elo
        self.name = name
        self.key = key
        self.depth = depth
        self.max_depth = depth
        self.siInterno = depth == 0
        self.depthOpen = (elo / 100 - 8) if elo < 2100 else 100
        if self.depthOpen < 2:
            self.depthOpen = 2
        self.alias = self.name
        if self.depth:
            self.alias += " %d" % self.depth

    def label(self):
        resp = self.name
        if self.depth:
            resp += " %d" % self.depth
        resp += " (%d)" % self.elo
        return resp


class ManagerElo(Manager.Manager):
    def valores(self):
        li = QTVarios.list_irina()

        self.list_engines = []
        for (alias, name, icono, elo) in li:
            self.list_engines.append(MotorElo(elo, name, alias, 0))

        def m(xelo, xkey, xdepth):
            self.list_engines.append(MotorElo(xelo, Util.primera_mayuscula(xkey), xkey, xdepth))

        for elo, key, depth in listaMotoresElo():
            m(elo, key, depth)

        for k, v in self.configuration.dic_engines.items():
            if v.elo > 2000:
                m(v.elo, v.key, None)  # ponemos depth a None, para diferenciar del 0 de los motores internos

        self.list_engines.sort(key=lambda x: x.elo)

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
        self.liK = ((0, 60), (800, 50), (1200, 40), (1600, 30), (2000, 30), (2400, 10))

    def calc_dif_elo(self, eloJugador, eloRival, resultado):
        if resultado == RS_WIN_PLAYER:
            result = 1
        elif resultado == RS_DRAW:
            result = 0
        else:
            result = -1
        return Util.fideELO(eloJugador, eloRival, result)

    def list_engines(self, elo):
        self.valores()
        li = []
        numX = len(self.list_engines)
        for num, mt in enumerate(self.list_engines):
            mt_elo = mt.elo
            mt.siOut = False
            if mt_elo > elo + 400:
                mt.siOut = True
                mt_elo = elo + 400
            mt.siJugable = abs(mt_elo - elo) <= 400
            if mt.siJugable:
                def rot(res):
                    return self.calc_dif_elo(elo, mt_elo, res)

                mt.pgana = rot(RS_WIN_PLAYER)
                mt.ptablas = rot(RS_DRAW)
                mt.ppierde = rot(RS_WIN_OPPONENT)

                mt.number = numX - num

                li.append(mt)

        return li

    def get_motor(self, key, depth):
        self.valores()
        for mt in self.list_engines:
            if mt.key == key and mt.depth == depth:
                return mt

    def start(self, datos_motor):
        self.base_inicio(datos_motor)
        self.play_next_move()

    def base_inicio(self, datos_motor):
        self.game_type = GT_ELO

        self.is_competitive = True

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        is_white = self.determina_side(datos_motor)

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.lirm_engine = []
        self.next_test_resign = 5
        self.resign_limit = -1000

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(self.is_tutor_enabled)

        self.hints = 0
        self.ayudas_iniciales = self.hints

        self.in_the_opening = True

        self.datosMotor = datos_motor
        self.opening = Opening.OpeningPol(100, elo=self.datosMotor.elo)

        eloengine = self.datosMotor.elo
        eloplayer = self.configuration.eloActivo()
        self.whiteElo = eloplayer if is_white else eloengine
        self.blackElo = eloplayer if not is_white else eloengine

        self.siRivalInterno = self.datosMotor.siInterno
        if self.siRivalInterno:
            rival = self.configuration.buscaRival("irina")
            depth = 2 if self.datosMotor.key in ("Rat", "Snake") else 1
            self.xrival = self.procesador.creaManagerMotor(rival, None, depth)
            self.xrival.set_option("Personality", self.datosMotor.key)

        else:
            rival = self.configuration.buscaRival(self.datosMotor.key)
            self.xrival = self.procesador.creaManagerMotor(rival, None, self.datosMotor.depth)

        self.pte_tool_resigndraw = True

        self.pon_toolbar()

        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        self.remove_hints(True, siQuitarAtras=True)
        self.show_side_indicator(True)
        label = "%s: <b>%s</b>" % (_("Opponent"), self.datosMotor.label())
        self.set_label1(label)

        nbsp = "&nbsp;" * 3

        txt = "%s:%+d%s%s:%+d%s%s:%+d" % (
            _("Win"),
            self.datosMotor.pgana,
            nbsp,
            _("Draw"),
            self.datosMotor.ptablas,
            nbsp,
            _("Loss"),
            self.datosMotor.ppierde,
        )

        self.set_label2("<center>%s</center>" % txt)
        self.pgn_refresh(True)
        self.show_info_extra()

        self.check_boards_setposition()

        self.game.set_tag("Event", _("Lucas-Elo"))

        player = self.configuration.nom_player()
        other = self.datosMotor.name
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)
        self.game.set_tag("WhiteElo", str(self.whiteElo))
        self.game.set_tag("BlackElo", str(self.blackElo))

        self.game.add_tag_timestart()

    def adjourn(self):
        if len(self.game) > 0 and QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            self.state = ST_ENDGAME
            dic = {
                "ISWHITE": self.is_human_side_white,
                "GAME_SAVE": self.game.save(),
                "CLAVE": self.datosMotor.key,
                "DEPTH": self.datosMotor.depth,
                "PGANA": self.datosMotor.pgana,
                "PPIERDE": self.datosMotor.ppierde,
                "PTABLAS": self.datosMotor.ptablas,
            }

            label_menu = "%s. %s" % (_("Lucas-Elo"), self.datosMotor.name)
            if self.datosMotor.depth:
                label_menu += " - %d" % self.datosMotor.depth
            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        engine = self.get_motor(dic["CLAVE"], dic["DEPTH"])
        if engine is None:
            return
        engine.pgana = dic["PGANA"]
        engine.ppierde = dic["PPIERDE"]
        engine.ptablas = dic["PTABLAS"]
        self.base_inicio(engine)
        self.is_human_side_white = dic["ISWHITE"]
        self.is_engine_side_white = not self.is_human_side_white
        self.put_pieces_bottom(self.is_human_side_white)

        self.game.restore(dic["GAME_SAVE"])
        self.goto_end()

        self.pon_toolbar()

        self.play_next_move()

    def pon_toolbar(self):
        liTool = (TB_CANCEL, TB_CONFIG, TB_UTILITIES)
        if self.pte_tool_resigndraw:
            if len(self.game) > 1:
                if self.siRivalInterno:
                    liTool = (TB_RESIGN, TB_ADJOURN, TB_CONFIG, TB_UTILITIES)
                else:
                    liTool = (TB_RESIGN, TB_DRAW, TB_ADJOURN, TB_CONFIG, TB_UTILITIES)
                self.pte_tool_resigndraw = False

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

    def final_x(self):
        return self.rendirse()

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        if not self.pte_tool_resigndraw:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?") + " (%d)" % self.datosMotor.ppierde):
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

        siRival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if siRival:
            self.thinking(True)
            self.disable_all()

            iniT = time.time()

            siPensar = True

            if self.in_the_opening:

                dT, hT = 5, 5

                ok, from_sq, to_sq, promotion = self.opening.run_engine(self.last_fen())

                if ok:
                    rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
                    rm_rival.from_sq = from_sq
                    rm_rival.to_sq = to_sq
                    rm_rival.promotion = promotion
                    siPensar = False

            if siPensar:
                if self.siRivalInterno:
                    rm_rival = self.xrival.play_game(self.game)
                    dT, hT = 5, 15
                else:
                    nJugadas = len(self.game)
                    if nJugadas > 30:
                        tp = 300
                    else:
                        tp = 600
                    rm_rival = self.xrival.play_time(self.game, tp, tp, 0)  # engloba juega + juega Tiempo
                    pts = rm_rival.centipawns_abs()
                    if pts > 100:
                        dT, hT = 5, 15
                    else:
                        dT, hT = 10, 35

            difT = time.time() - iniT
            t = random.randint(dT * 10, hT * 10) * 0.01
            if difT < t:
                time.sleep(t - difT)

            self.thinking(False)
            if self.rival_has_moved(rm_rival):
                self.lirm_engine.append(rm_rival)
                if self.valoraRMrival():
                    self.play_next_move()
                else:
                    self.show_result()
                    return
        else:

            self.human_is_playing = True
            self.activate_side(is_white)

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beep_result(beep)

        elo = self.configuration.eloActivo()
        if player_win:
            difelo = self.datosMotor.pgana

        elif self.game.is_draw():
            difelo = self.datosMotor.ptablas

        else:
            difelo = self.datosMotor.ppierde

        nelo = elo + difelo
        if nelo < 0:
            nelo = 0
        self.configuration.ponEloActivo(nelo)

        self.historial(elo, nelo)
        self.configuration.graba()

        mensaje += "\n\n%s : %d\n" % (_("New Lucas-Elo"), self.configuration.eloActivo())

        self.mensaje(mensaje)
        self.set_end_game()
        self.autosave()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        if self.in_the_opening:
            self.in_the_opening = self.opening.check_human(self.last_fen(), from_sq, to_sq)

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        # self.ponAyudas( self.hints )

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

        self.check_boards_setposition()

        if self.pte_tool_resigndraw:
            self.pon_toolbar()

    def rival_has_moved(self, engine_response):
        from_sq = engine_response.from_sq
        to_sq = engine_response.to_sq

        promotion = engine_response.promotion

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def historial(self, elo, nelo):
        dic = {
            "FECHA": datetime.datetime.now(),
            "RIVAL": self.datosMotor.label(),
            "RESULTADO": self.resultado,
            "AELO": elo,
            "NELO": nelo
        }

        lik = UtilSQL.ListSQL(self.configuration.fichEstadElo)
        lik.append(dic)
        lik.close()

        dd = UtilSQL.DictSQL(self.configuration.fichEstadElo, tabla="color")
        key = "%s-%d" % (self.datosMotor.name, self.datosMotor.depth if self.datosMotor.depth else 0)
        dd[key] = self.is_human_side_white
        dd.close()

    def determina_side(self, datosMotor):
        key = "%s-%d" % (datosMotor.key, datosMotor.depth if datosMotor.depth else 0)

        with UtilSQL.DictSQL(self.configuration.fichEstadElo, tabla="color") as dd:
            return not dd.get(key, random.choice((True, False)))
