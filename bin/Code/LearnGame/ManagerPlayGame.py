import copy
import time

from Code import Manager
from Code import Util
from Code.Base import Game
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    RS_WIN_PLAYER,
    RS_WIN_OPPONENT,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_CANCEL,
    TB_UTILITIES,
)
from Code.LearnGame import WindowPlayGame
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio


class ManagerPlayGame(Manager.Manager):
    def start(self, recno, is_white):

        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        reg = db.leeRegistro(recno)
        gameObj = Game.Game()
        gameObj.restore(reg["GAME"])
        nombreObj = gameObj.get_tag("WHITE" if is_white else "BLACK")
        label = db.label(recno)
        db.close()

        self.recno = recno
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.if_analyzing = False
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white
        self.numJugadasObj = gameObj.num_moves()
        self.gameObj = gameObj
        self.posJugadaObj = 0
        self.nombreObj = nombreObj

        self.siSave = False
        self.minTiempo = 5000

        self.xanalyzer.maximize_multipv()

        self.puntosMax = 0
        self.puntos = 0
        self.vtime = 0.0

        self.book = Opening.OpeningPol(999)

        self.set_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG, TB_UTILITIES))

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.remove_hints(True, True)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.is_human_side_white)
        self.show_side_indicator(True)
        self.set_label1(label)
        self.set_label2("")

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.check_boards_setposition()

        self.state = ST_PLAYING

        var_config = "LEARN_GAME_PLAY_AGAINST"

        dic = self.configuration.read_variables(var_config)

        self.show_all = dic.get("SHOW_ALL", False)
        self.show_rating_always, self.show_rating_different, self.show_rating_never = None, True, False
        self.show_rating = dic.get("SHOW_RATING", self.show_rating_always)

        self.play_next_move()

    def ponPuntos(self):
        self.set_label2(
            '%s:<table border="1" cellpadding="5" cellspacing="0" style="margin-left:60px"><tr><td>%s</td><td><b>%d</b></td></tr><tr><td>%s</td><td><b>%d</b></td></tr></table>'
            % (_("Score in relation to"), self.nombreObj, self.puntos, self.xanalyzer.name, -self.puntosMax)
        )

    def run_action(self, key):
        if key == TB_CLOSE:
            self.procesador.start()
            self.procesador.play_game_show(self.recno)

        elif key == TB_CANCEL:
            self.cancelar()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.cancelar()

    def cancelar(self):
        self.puntos = -999
        self.analizaTerminar()
        self.procesador.start()
        return False

    def reiniciar(self, siPregunta):
        if siPregunta:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
        self.main_window.activaInformacionPGN(False)
        self.game.set_position()
        self.posJugadaObj = 0
        self.puntos = 0
        self.puntosMax = 0
        self.ponPuntos()
        self.vtime = 0.0
        self.book = Opening.OpeningPol(999)
        self.state = ST_PLAYING
        self.board.set_position(self.game.first_position)
        self.pgnRefresh(True)
        self.check_boards_setposition()
        self.analyze_end()

        self.play_next_move()

    def validoMRM(self, pvUsu, pvObj, mrmActual):
        move = self.gameObj.move(self.posJugadaObj)
        if move.analysis:
            mrm, pos = move.analysis
            msAnalisis = mrm.getTime()
            if msAnalisis > self.minTiempo:
                if mrmActual.getTime() > msAnalisis and mrmActual.contain(pvUsu) and mrmActual.contain(pvObj):
                    return None
                if mrm.contain(pvObj) and mrm.contain(pvUsu):
                    return mrm
        return None

    def analyze_begin(self):
        if not self.is_finished():
            self.xanalyzer.ac_inicio(self.game)
            self.if_analyzing = True

    def analyze_minimum(self, pvUsu, pvObj):
        mrmActual = self.xanalyzer.ac_estado()
        mrm = self.validoMRM(pvUsu, pvObj, mrmActual)
        if mrm:
            return mrm
        self.mrm = copy.deepcopy(self.xanalyzer.ac_minimo(self.minTiempo, False))
        return self.mrm

    def analyze_state(self):
        self.xanalyzer.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xanalyzer.ac_estado())
        return self.mrm

    def analyze_end(self):
        if self.if_analyzing:
            self.if_analyzing = False
            self.xanalyzer.ac_final(-1)
            self.siSave = True

    def analizaTerminar(self):
        if self.if_analyzing:
            self.if_analyzing = False
            self.xanalyzer.terminar()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        num_moves = len(self.game)
        if num_moves >= self.numJugadasObj:
            self.put_result()
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
            self.iniTiempo = time.time()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jg_usu = self.check_human_move(from_sq, to_sq, promotion)
        if not jg_usu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jg_obj = self.gameObj.move(self.posJugadaObj)

        si_analiza_juez = True
        if self.book:
            fen = self.last_fen()
            si_book_usu = self.book.check_human(fen, from_sq, to_sq)
            si_book_obj = self.book.check_human(fen, jg_obj.from_sq, jg_obj.to_sq)
            if si_book_usu and si_book_obj:
                if jg_obj.movimiento() != jg_usu.movimiento():
                    bmove = _("book move")
                    comment = "%s: %s %s<br>%s: %s %s" % (
                        self.nombreObj,
                        jg_obj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jg_usu.pgn_translated(),
                        bmove,
                    )
                    if self.show_rating in (self.show_rating_always, self.show_rating_different):
                        QTUtil2.message_result(self.main_window, comment)
                si_analiza_juez = False
            else:
                si_analiza_juez = True
                if not si_book_obj:
                    self.book = None

        analysis = None
        comment = None

        if si_analiza_juez:
            um = QTUtil2.analizando(self.main_window)
            pv_usu = jg_usu.movimiento()
            pv_obj = jg_obj.movimiento()
            mrm = self.analyze_minimum(pv_usu, pv_obj)
            position = self.game.last_position

            rm_usu, nada = mrm.buscaRM(pv_usu)
            rm_obj, pos_obj = mrm.buscaRM(pv_obj)

            analysis = mrm, pos_obj
            um.final()

            if self.show_rating == self.show_rating_different:
                si_analiza_juez = pv_usu != pv_obj
            elif self.show_rating == self.show_rating_never:
                si_analiza_juez = False

            if si_analiza_juez:
                w = WindowJuicio.WJuicio(self, self.xanalyzer, self.nombreObj, position, mrm, rm_obj, rm_usu, analysis,
                                         is_competitive=not self.show_all)
                w.exec_()

                analysis = w.analysis
                if w.siAnalisisCambiado:
                    self.siSave = True
                dpts = w.difPuntos()
                dpts_max = w.difPuntosMax()
                rm_usu = w.rmUsu
                rm_obj = w.rmObj
            else:
                dpts = rm_usu.puntosABS_5() - rm_obj.puntosABS_5()
                dpts_max = mrm.mejorMov().puntosABS_5() - rm_usu.puntosABS_5()

            self.puntos += dpts
            self.puntosMax += dpts_max

            comentario_usu = " %s" % (rm_usu.abrTexto())
            comentario_obj = " %s" % (rm_obj.abrTexto())
            comentario_puntos = "%s = %d %+d %+d = %d" % (
                _("Score"),
                self.puntos - dpts,
                rm_usu.centipawns_abs(),
                -rm_obj.centipawns_abs(),
                self.puntos,
            )
            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.nombreObj,
                jg_obj.pgn_translated(),
                comentario_obj,
                self.configuration.x_player,
                jg_usu.pgn_translated(),
                comentario_usu,
                comentario_puntos,
            )
            self.ponPuntos()

        self.analyze_end()

        self.add_move(True, analysis, comment)
        self.play_next_move()
        return True

    def add_move(self, siNuestra, analysis=None, comment=None):
        move = self.gameObj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analysis:
            move.analysis = analysis
        if comment:
            move.add_comment(comment)

        self.game.add_move(move)
        self.check_boards_setposition()

        self.move_the_pieces(move.liMovs, True)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

    def put_result(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        if self.puntos < 0:
            mensaje = _("Unfortunately you have lost.")
            quien = RS_WIN_OPPONENT
        else:
            mensaje = _("Congratulations you have won.")
            quien = RS_WIN_PLAYER

        self.beepResultadoCAMBIAR(quien)

        self.message_on_pgn(mensaje)
        self.ponFinJuego()
        self.guardar()

    def guardar(self):
        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        reg = db.leeRegistro(self.recno)

        dicIntento = {
            "DATE": Util.today(),
            "COLOR": "w" if self.is_human_side_white else "b",
            "POINTS": self.puntos,
            "POINTSMAX": self.puntosMax,
            "TIME": self.vtime,
        }

        if not ("LIINTENTOS" in reg):
            reg["LIINTENTOS"] = []
        reg["LIINTENTOS"].insert(0, dicIntento)

        if self.siSave:
            reg["GAME"] = self.gameObj.save()
            self.siSave = False

        db.cambiaRegistro(self.recno, reg)

        db.close()
