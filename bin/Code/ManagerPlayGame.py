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
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio
from Code.QT import WindowPlayGame


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
        self.siAnalizando = False
        self.human_side = is_white
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

        self.main_window.pon_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG, TB_UTILITIES))

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.remove_hints(True, True)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.human_side)
        self.show_side_indicator(True)
        self.set_label1(label)
        self.set_label2("")

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.check_boards_setposition()

        self.state = ST_PLAYING
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
            self.siAnalizando = True

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
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.ac_final(-1)
            self.siSave = True

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
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
        jgUsu = self.check_human_move(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jgObj = self.gameObj.move(self.posJugadaObj)

        siAnalizaJuez = True
        if self.book:
            fen = self.last_fen()
            siBookUsu = self.book.check_human(fen, from_sq, to_sq)
            siBookObj = self.book.check_human(fen, jgObj.from_sq, jgObj.to_sq)
            if siBookUsu and siBookObj:
                if jgObj.movimiento() != jgUsu.movimiento():
                    bmove = _("book move")
                    comment = "%s: %s %s<br>%s: %s %s" % (
                        self.nombreObj,
                        jgObj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jgUsu.pgn_translated(),
                        bmove,
                    )
                    w = WindowJuicio.MensajeF(self.main_window, comment)
                    w.mostrar()
                siAnalizaJuez = False
            else:
                siAnalizaJuez = True
                if not siBookObj:
                    self.book = None

        analysis = None
        comment = None

        if siAnalizaJuez:
            um = QTUtil2.analizando(self.main_window)
            pvUsu = jgUsu.movimiento()
            pvObj = jgObj.movimiento()
            mrm = self.analyze_minimum(pvUsu, pvObj)
            position = self.game.last_position

            rmUsu, nada = mrm.buscaRM(pvUsu)
            rmObj, posObj = mrm.buscaRM(pvObj)

            analysis = mrm, posObj
            um.final()

            w = WindowJuicio.WJuicio(self, self.xanalyzer, self.nombreObj, position, mrm, rmObj, rmUsu, analysis)
            w.exec_()

            analysis = w.analysis
            if w.siAnalisisCambiado:
                self.siSave = True
            dpts = w.difPuntos()
            self.puntos += dpts

            dptsMax = w.difPuntosMax()
            self.puntosMax += dptsMax

            comentarioUsu = " %s" % (w.rmUsu.abrTexto())
            comentarioObj = " %s" % (w.rmObj.abrTexto())

            comentarioPuntos = "%s = %d %+d %+d = %d" % (
                _("Score"),
                self.puntos - dpts,
                w.rmUsu.centipawns_abs(),
                -w.rmObj.centipawns_abs(),
                self.puntos,
            )
            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.nombreObj,
                jgObj.pgn_translated(),
                comentarioObj,
                self.configuration.x_player,
                jgUsu.pgn_translated(),
                comentarioUsu,
                comentarioPuntos,
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
            move.comment = comment

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

        self.mensajeEnPGN(mensaje)
        self.ponFinJuego()
        self.guardar()

    def guardar(self):
        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        reg = db.leeRegistro(self.recno)

        dicIntento = {
            "DATE": Util.today(),
            "COLOR": "w" if self.human_side else "b",
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
