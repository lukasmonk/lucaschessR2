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
    min_mstime = 5000
    _db: str
    _activo = None
    _ponActivo = None
    name_obj: str
    _fichEstad: str
    _titulo: str
    _newTitulo: str
    _TIPO: str
    analysis = None
    comment = None
    is_analyzing = False
    is_competitive = True
    eloObj = 0
    eloUsu = 0
    pwin = 0
    pdraw = 0
    plost = 0
    puntos = 0
    is_tutor_enabled = False
    nivel = 0
    is_human_side_white = True
    is_engine_side_white = True
    game_obj = None
    posJugadaObj = 0
    numJugadasObj = 0
    tag_result = None
    id_game = 0
    book = None
    mrm = None
    name = None

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
        color = self.get_the_side(nivel)
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

        self.tag_result = self.game.get_tag("RESULT")

        self.game.set_unknown()
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
        self.is_analyzing = False

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

        if self.eloUsu < 1800:
            self.xtutor = self.procesador.super_tutor()
        self.xtutor.options(self.min_mstime, 0, True)

        self.book = Opening.OpeningPol(999)

        self.pon_toolbar()

        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.is_human_side_white)
        self.remove_hints(True, siQuitarAtras=True)
        self.show_side_indicator(True)
        label = "%s: <b>%d</b> | %s: <b>%d</b>" % (self._titulo, self.eloUsu, _("Elo rival"), self.eloObj)
        label += " | %+d %+d %+d" % (self.pwin, self.pdraw, self.plost)
        self.set_label1(label)

        self.set_label2("")
        self.pgn_refresh(True)
        self.show_info_extra()

        self.check_boards_setposition()

    def set_score(self):
        self.set_label2("%s : <b>%d</b>" % (_("Score"), self.puntos))

    def pon_toolbar(self):
        li_tool = [TB_RESIGN, TB_ADJOURN, TB_CONFIG, TB_UTILITIES]
        self.set_toolbar(li_tool)

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
                self.analyzer_close()
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        id_game = dic["IDGAME"]
        self.base_inicio(id_game)
        self.posJugadaObj = dic["POSJUGADAOBJ"]
        self.game.restore(dic["GAME_SAVE"])
        self.puntos = dic["PUNTOS"]
        self.move_according_key(GO_END)
        self.set_score()

        self.play_next_move()

    def final_x(self):
        return self.rendirse()

    def rendirse(self):
        if self.state == ST_ENDGAME:
            self.analyzer_close()
            return True
        if len(self.game) > 0:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?") + " (%d)" % self.plost):
                return False  # no abandona
            self.puntos = -999
            self.analyzer_close()
            self.show_result()
        else:
            self.analyzer_close()
            self.procesador.start()

        return False

    def analyze_begin(self):
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_state(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analyze_minimum(self):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(self.min_mstime, False))
        return self.mrm

    def analyze_end(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.xtutor.ac_final(-1)

    def analyzer_close(self):
        if self.is_analyzing:
            self.is_analyzing = False
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

        si_rival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if si_rival:
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

        jg_obj = self.game_obj.move(self.posJugadaObj)

        analysis = None
        comment = None

        comentario_usu = ""
        comentario_obj = ""

        si_analiza_juez = jg_usu.movimiento() != jg_obj.movimiento()
        if self.book:
            fen = self.last_fen()
            si_book_usu = self.book.check_human(fen, from_sq, to_sq)
            si_book_obj = self.book.check_human(fen, jg_obj.from_sq, jg_obj.to_sq)
            if si_book_usu:
                comentario_usu = _("book move")
            if si_book_obj:
                comentario_obj = _("book move")
            if si_book_usu and si_book_obj:
                if jg_obj.movimiento() != jg_usu.movimiento():
                    # comment = "%s: %s" % (_("Same book move"), jg_obj.pgn_translated())
                    # else:
                    bmove = _("book move")
                    comment = "%s: %s %s\n%s: %s %s" % (
                        self.name_obj,
                        jg_obj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jg_usu.pgn_translated(),
                        bmove,
                    )
                    QTUtil2.message_information(self.main_window, comment.replace("\n", "<br>"))
                si_analiza_juez = False
            else:
                if not si_book_obj:
                    self.book = None

        if si_analiza_juez:
            um = QTUtil2.analizando(self.main_window)
            mrm = self.analyze_minimum()
            position = self.game.last_position

            continue_tt = self.continueTt

            rm_usu, nada = mrm.search_rm(jg_usu.movimiento())
            if rm_usu is None:
                self.analyze_end()
                continue_tt = False
                rm_usu = self.xtutor.valora(position, jg_usu.from_sq, jg_usu.to_sq, jg_usu.promotion)
                mrm.add_rm(rm_usu)

            rm_obj, pos_obj = mrm.search_rm(jg_obj.movimiento())
            if rm_obj is None:
                self.analyze_end()
                continue_tt = False
                rm_obj = self.xtutor.valora(position, jg_obj.from_sq, jg_obj.to_sq, jg_obj.promotion)
                pos_obj = mrm.add_rm(rm_obj)

            analysis = mrm, pos_obj
            um.final()

            w = WindowJuicio.WJuicio(self, self.xtutor, self.name_obj, position, mrm, rm_obj, rm_usu, analysis,
                                     is_competitive=True, continue_tt=continue_tt)
            w.exec_()

            analysis = w.analysis
            dpts = w.difPuntos()

            self.puntos += dpts
            self.set_score()

            comentario_usu += " %s" % (w.rmUsu.abbrev_text())
            comentario_obj += " %s" % (w.rmObj.abbrev_text())

            comentario_puntos = "%s = %d %+d %+d = %d" % (
                _("Score"),
                self.puntos - dpts,
                w.rmUsu.centipawns_abs(),
                -w.rmObj.centipawns_abs(),
                self.puntos,
            )

            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.name_obj,
                jg_obj.pgn_translated(),
                comentario_obj,
                self.configuration.x_player,
                jg_usu.pgn_translated(),
                comentario_usu,
                comentario_puntos,
            )

        self.analyze_end()

        self.add_move(True, comment, analysis)
        self.play_next_move()
        return True

    def add_move(self, si_nuestra, comment=None, analysis=None):
        move = self.game_obj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analysis:
            move.analysis = analysis
        if comment:
            move.set_comment(comment)

        if comment:
            self.comment = comment.replace("\n", "<br><br>") + "<br>"

        if not si_nuestra:
            if self.posJugadaObj:
                self.comment = None

        self.game.add_move(move)
        self.check_boards_setposition()
        self.move_the_pieces(move.liMovs, True)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(si_nuestra)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def show_result(self):
        self.analyzer_close()
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

        self.beep_result_change(quien)

        nelo = self.eloUsu + difelo
        if nelo < 0:
            nelo = 0
        self._ponActivo(nelo)

        self.historial(self.eloUsu, nelo)
        self.configuration.graba()

        mensaje += "<br><br>%s : %d<br>" % (self._newTitulo, self._activo())

        self.message_on_pgn(mensaje)

        if self.tag_result:
            self.game.set_tag("Result", self.tag_result)

        self.set_end_game()

    def historial(self, elo, nelo):
        dic = {
            "FECHA": datetime.datetime.now(),
            "LEVEL": self.nivel,
            "RESULTADO": self.resultado,
            "AELO": elo,
            "NELO": nelo
        }

        lik = UtilSQL.ListSQL(self._fichEstad)
        lik.append(dic)
        lik.close()

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        key = "%s-%d" % (self._TIPO, self.nivel)
        dd[key] = self.is_human_side_white
        dd.close()

    def get_the_side(self, nivel):
        key = "%s-%d" % (self._TIPO, nivel)

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        previo = dd.get(key, random.randint(0, 1) == 0)
        dd.close()
        return not previo
