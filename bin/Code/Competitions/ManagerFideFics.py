import copy
import datetime
import random

import FasterCode

import Code
from Code import Adjournments
from Code import Manager
from Code import Util
from Code.Base import Game
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    RS_WIN_PLAYER,
    RS_WIN_OPPONENT,
    RS_DRAW,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_RESIGN,
    TB_UTILITIES,
    GT_FICS,
    GT_FIDE,
    GT_LICHESS,
    GO_END,
)
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio
from Code.SQL import Base
from Code.SQL import UtilSQL


class ManagerFideFics(Manager.Manager):
    def selecciona(self, type_play):
        self.game_type = type_play
        if type_play == GT_FICS:
            self._db = Code.path_resource("IntFiles", "FicsElo.db")
            self._activo = self.configuration.ficsActivo
            self._ponActivo = self.configuration.ponFicsActivo
            self.name_obj = _("Fics-player")  # self.cabs[ "White" if self.is_human_side_white else "Black" ]
            self._fichEstad = self.configuration.fichEstadFicsElo
            self._titulo = _("Fics-Elo")
            self._newTitulo = _("New Fics-Elo")
            self._TIPO = "FICS"

        elif type_play == GT_FIDE:
            self._db = Code.path_resource("IntFiles", "FideElo.db")
            self._activo = self.configuration.fideActivo
            self._ponActivo = self.configuration.ponFideActivo
            self.name_obj = _("Fide-player")  # self.cabs[ "White" if self.is_human_side_white else "Black" ]
            self._fichEstad = self.configuration.fichEstadFideElo
            self._titulo = _("Fide-Elo")
            self._newTitulo = _("New Fide-Elo")
            self._TIPO = "FIDE"

        elif type_play == GT_LICHESS:
            self._db = Code.path_resource("IntFiles", "LichessElo.db")
            self._activo = self.configuration.lichessActivo
            self._ponActivo = self.configuration.ponLichessActivo
            self.name_obj = _("Lichess-player")
            self._fichEstad = self.configuration.fichEstadLichessElo
            self._titulo = _("Lichess-Elo")
            self._newTitulo = _("New Lichess-Elo")
            self._TIPO = "LICHESS"

    def elige_juego(self, nivel):
        color = self.determinaColor(nivel)
        db = Base.DBBase(self._db)
        dbf = db.dbfT("data", "ROWID", condicion="LEVEL=%d AND WHITE=%d" % (nivel, 1 if color else 0))
        dbf.leer()
        reccount = dbf.reccount()
        recno = random.randint(1, reccount)
        dbf.goto(recno)
        xid = dbf.ROWID
        dbf.cerrar()
        db.cerrar()

        return xid

    def read_id(self, xid):
        db = Base.DBBase(self._db)
        dbf = db.dbfT("data", "LEVEL,WHITE,CABS,MOVS", condicion="ROWID=%d" % xid)
        dbf.leer()
        dbf.gotop()

        self.nivel = dbf.LEVEL

        is_white = dbf.WHITE
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        pv = FasterCode.xpv_pv(dbf.MOVS)
        self.game_obj = Game.Game()
        self.game_obj.read_pv(pv)
        self.posJugadaObj = 0
        self.numJugadasObj = self.game_obj.num_moves()

        li = dbf.CABS.split("\n")
        for x in li:
            if x:
                key, valor = x.split("=")
                self.game.set_tag(key, valor)

        dbf.cerrar()
        db.cerrar()

    def start(self, id_game):
        self.base_inicio(id_game)
        self.play_next_move()

    def base_inicio(self, id_game):
        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING
        self.analysis = None
        self.comment = None
        self.if_analyzing = False

        self.is_competitive = True

        self.read_id(id_game)
        self.id_game = id_game

        self.eloObj = int(self.game.get_tag("WhiteElo" if self.is_human_side_white else "BlackElo"))
        self.eloUsu = self._activo()

        self.pwin = Util.fideELO(self.eloUsu, self.eloObj, +1)
        self.pdraw = Util.fideELO(self.eloUsu, self.eloObj, 0)
        self.plost = Util.fideELO(self.eloUsu, self.eloObj, -1)

        self.puntos = 0

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(self.is_tutor_enabled)

        self.hints = 0
        self.ayudas_iniciales = 0

        self.xtutor.maximize_multipv()

        self.book = Opening.OpeningPol(999)

        self.pon_toolbar()

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.is_human_side_white)
        self.remove_hints(True, siQuitarAtras=True)
        self.show_side_indicator(True)
        label = "%s: <b>%d</b> | %s: <b>%d</b>" % (self._titulo, self.eloUsu, _("Elo rival"), self.eloObj)
        label += " | %+d %+d %+d" % (self.pwin, self.pdraw, self.plost)
        self.set_label1(label)

        self.set_label2("")
        self.pgnRefresh(True)
        self.show_info_extra()

        self.check_boards_setposition()

    def ponPuntos(self):
        self.set_label2("%s : <b>%d</b>" % (_("Score"), self.puntos))

    def pon_toolbar(self):
        liTool = [TB_RESIGN, TB_ADJOURN, TB_CONFIG, TB_UTILITIES]
        self.set_toolbar(liTool)

    def run_action(self, key):
        if key in (TB_RESIGN, TB_CANCEL):
            self.rendirse()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_TAKEBACK:
            return  # disable

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def adjourn(self):
        if len(self.game) > 0 and QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = {
                "IDGAME": self.id_game,
                "POSJUGADAOBJ": self.posJugadaObj,
                "GAME_SAVE": self.game.save(),
                "PUNTOS": self.puntos,
            }

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, self._titulo)
                self.analizaTerminar()
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        id_game = dic["IDGAME"]
        self.base_inicio(id_game)
        self.posJugadaObj = dic["POSJUGADAOBJ"]
        self.game.restore(dic["GAME_SAVE"])
        self.puntos = dic["PUNTOS"]
        self.mueveJugada(GO_END)
        self.ponPuntos()

        self.play_next_move()

    def final_x(self):
        return self.rendirse()

    def rendirse(self):
        if self.state == ST_ENDGAME:
            self.analizaTerminar()
            return True
        if len(self.game) > 0:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?") + " (%d)" % self.plost):
                return False  # no abandona
            self.puntos = -999
            self.analizaTerminar()
            self.show_result()
        else:
            self.analizaTerminar()
            self.procesador.start()

        return False

    def analyze_begin(self):
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.if_analyzing = True

    def analyze_state(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analyze_minimum(self, minTime):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(minTime, False))
        return self.mrm

    def analyze_end(self):
        if self.if_analyzing:
            self.if_analyzing = False
            self.xtutor.ac_final(-1)

    def analizaTerminar(self):
        if self.if_analyzing:
            self.if_analyzing = False
            self.xtutor.terminar()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        num_moves = len(self.game)
        if num_moves >= self.numJugadasObj:
            self.show_result()
            return

        siRival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if siRival:
            self.add_move(False)
            self.play_next_move()
        else:

            self.human_is_playing = True
            self.thinking(True)
            self.analyze_begin()
            self.activate_side(is_white)
            self.thinking(False)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jg_usu = self.check_human_move(from_sq, to_sq, promotion)
        if not jg_usu:
            return False

        jgObj = self.game_obj.move(self.posJugadaObj)

        analysis = None
        comment = None

        comentario_usu = ""
        comentario_obj = ""

        si_analiza_juez = jg_usu.movimiento() != jgObj.movimiento()
        if self.book:
            fen = self.last_fen()
            siBookUsu = self.book.check_human(fen, from_sq, to_sq)
            siBookObj = self.book.check_human(fen, jgObj.from_sq, jgObj.to_sq)
            if siBookUsu:
                comentario_usu = _("book move")
            if siBookObj:
                comentario_obj = _("book move")
            if siBookUsu and siBookObj:
                if jgObj.movimiento() != jg_usu.movimiento():
                    # comment = "%s: %s" % (_("Same book move"), jgObj.pgn_translated())
                    # else:
                    bmove = _("book move")
                    comment = "%s: %s %s<br>%s: %s %s" % (
                        self.name_obj,
                        jgObj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jg_usu.pgn_translated(),
                        bmove,
                    )
                    QTUtil2.message_information(self.main_window, comment)
                si_analiza_juez = False
            else:
                if not siBookObj:
                    self.book = None

        if si_analiza_juez:
            um = QTUtil2.analizando(self.main_window)
            if not self.continueTt:
                self.analyze_begin()
            mrm = self.analyze_minimum(5000)
            position = self.game.last_position

            rmUsu, nada = mrm.buscaRM(jg_usu.movimiento())
            if rmUsu is None:
                self.analyze_end()
                rmUsu = self.xtutor.valora(position, jg_usu.from_sq, jg_usu.to_sq, jg_usu.promotion)
                mrm.add_rm(rmUsu)
                self.analyze_begin()

            rmObj, posObj = mrm.buscaRM(jgObj.movimiento())
            if rmObj is None:
                self.analyze_end()
                rmObj = self.xtutor.valora(position, jgObj.from_sq, jgObj.to_sq, jgObj.promotion)
                posObj = mrm.add_rm(rmObj)
                self.analyze_begin()

            analysis = mrm, posObj
            um.final()

            w = WindowJuicio.WJuicio(self, self.xtutor, self.name_obj, position, mrm, rmObj, rmUsu, analysis)
            w.exec_()

            analysis = w.analysis
            dpts = w.difPuntos()

            self.puntos += dpts
            self.ponPuntos()

            comentario_usu += " %s" % (w.rmUsu.abrTexto())
            comentario_obj += " %s" % (w.rmObj.abrTexto())

            comentarioPuntos = "%s = %d %+d %+d = %d" % (
                _("Score"),
                self.puntos - dpts,
                w.rmUsu.centipawns_abs(),
                -w.rmObj.centipawns_abs(),
                self.puntos,
            )

            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.name_obj,
                jgObj.pgn_translated(),
                comentario_obj,
                self.configuration.x_player,
                jg_usu.pgn_translated(),
                comentario_usu,
                comentarioPuntos,
            )

        self.analyze_end()

        self.add_move(True, comment, analysis)
        self.play_next_move()
        return True

    def add_move(self, siNuestra, comment=None, analysis=None):

        move = self.game_obj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analysis:
            move.analysis = analysis
        if comment:
            move.set_comment(comment)

        if comment:
            self.comment = comment.replace("\n", "<br><br>") + "<br>"

        if not siNuestra:
            if self.posJugadaObj:
                self.comment = None

        self.game.add_move(move)
        self.check_boards_setposition()
        self.move_the_pieces(move.liMovs, True)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

    def show_result(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        if self.puntos < -50:
            mensaje = _X(_("Unfortunately you have lost against %1."), self.name_obj)
            quien = RS_WIN_OPPONENT
            difelo = self.plost
        elif self.puntos > 50:
            mensaje = _X(_("Congratulations you have won against %1."), self.name_obj)
            quien = RS_WIN_PLAYER
            difelo = self.pwin
        else:
            mensaje = _X(_("Draw against %1."), self.name_obj)
            quien = RS_DRAW
            difelo = self.pdraw

        self.beepResultadoCAMBIAR(quien)

        nelo = self.eloUsu + difelo
        if nelo < 0:
            nelo = 0
        self._ponActivo(nelo)

        self.historial(self.eloUsu, nelo)
        self.configuration.graba()

        mensaje += "<br><br>%s : %d<br>" % (self._newTitulo, self._activo())

        self.message_on_pgn(mensaje)
        self.set_end_game()

    def historial(self, elo, nelo):
        dic = {}
        dic["FECHA"] = datetime.datetime.now()
        dic["LEVEL"] = self.nivel
        dic["RESULTADO"] = self.resultado
        dic["AELO"] = elo
        dic["NELO"] = nelo

        lik = UtilSQL.ListSQL(self._fichEstad)
        lik.append(dic)
        lik.close()

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        key = "%s-%d" % (self._TIPO, self.nivel)
        dd[key] = self.is_human_side_white
        dd.close()

    def determinaColor(self, nivel):
        key = "%s-%d" % (self._TIPO, nivel)

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        previo = dd.get(key, random.randint(0, 1) == 0)
        dd.close()
        return not previo
