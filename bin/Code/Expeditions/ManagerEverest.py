import copy
import time

from PySide2 import QtCore

from Code import Manager
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_CANCEL,
    TB_UTILITIES,
)
from Code.Expeditions import Everest
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio


class ManagerEverest(Manager.Manager):
    def start(self, recno):

        self.expedition = Everest.Expedition(self.configuration, recno)
        self.expedition.run()

        self.dic_analysis = {}

        self.is_competitive = True
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.siAnalizando = False
        self.human_side = self.expedition.is_white
        self.is_engine_side_white = not self.expedition.is_white
        self.gameObj = self.expedition.game
        self.game.set_tags(self.gameObj.li_tags)
        self.numJugadasObj = self.gameObj.num_moves()
        self.posJugadaObj = 0
        self.nombreObj = self.expedition.name

        self.xanalyzer.maximize_multipv()

        self.puntos = 0
        self.vtime = 0.0

        self.book = Opening.OpeningPol(999)

        self.main_window.pon_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG))

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.remove_hints(True, True)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.human_side)
        self.show_side_indicator(True)
        self.set_label1(self.expedition.label())
        self.set_label2("")

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.check_boards_setposition()

        self.state = ST_PLAYING
        self.play_next_move()

    def ponPuntos(self):
        self.set_label2("%s : <b>%d</b>" % (_("Score"), self.puntos))

    def run_action(self, key):
        if key == TB_CANCEL:
            self.cancelar()

        elif key == TB_REINIT:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
            change_game = self.restart(False)
            if change_game:
                self.terminar()
            else:
                self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key == TB_CLOSE:
            self.terminar()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.cancelar()

    def cancelar(self):
        if self.posJugadaObj > 1 and self.state == ST_PLAYING:
            self.restart(False)
        self.terminar()
        return False

    def terminar(self):
        self.analizaTerminar()
        self.terminaNoContinuo()
        self.procesador.start()
        self.procesador.showEverest(self.expedition.recno)

    def reiniciar(self):
        self.game.set_position()
        self.posJugadaObj = 0
        self.puntos = 0
        self.ponPuntos()
        self.vtime = 0.0
        self.book = Opening.OpeningPol(999)
        self.state = ST_PLAYING
        self.board.set_position(self.game.first_position)
        self.pgnRefresh(True)
        self.check_boards_setposition()
        self.analyze_end()
        self.terminaNoContinuo()

        self.set_label1(self.expedition.label())
        self.ponPuntos()
        self.play_next_move()

    def restart(self, lost_points):
        self.terminaNoContinuo()
        change_game, is_last, is_last_last = self.expedition.add_try(False, self.vtime, self.puntos)
        self.vtime = 0.0
        licoment = []
        if lost_points:
            licoment.append(_("You have exceeded the limit of lost centipawns."))

        if change_game:
            licoment.append(_("You have exceeded the limit of tries, you will fall back to the previous."))
        elif lost_points:
            licoment.append(_("You must repeat the game from beginning."))
        if licoment:
            comment = "\n".join(licoment)
            w = WindowJuicio.MensajeF(self.main_window, comment)
            w.mostrar()
        return change_game

    def analyze_begin(self):
        self.xanalyzer.ac_inicio(self.game)
        self.siAnalizando = True

    def analyze_minimum(self, minTime):
        self.mrm = copy.deepcopy(self.xanalyzer.ac_minimo(minTime, False))
        return self.mrm

    def analyze_state(self):
        self.xanalyzer.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xanalyzer.ac_estado())
        return self.mrm

    def analyze_end(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.ac_final(-1)

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.terminar()

    def analizaNoContinuo(self):
        self.tiempoNoContinuo += 500
        if self.tiempoNoContinuo >= 5000:
            self.analyze_minimum(5)
            self.analyze_end()
            self.pendienteNoContinuo = False
        else:
            QtCore.QTimer.singleShot(500, self.analizaNoContinuo)

    def analizaNoContinuoFinal(self):
        if self.tiempoNoContinuo < 5000:
            um = QTUtil2.analizando(self.main_window)
            self.analyze_minimum(5000)
            um.final()

    def terminaNoContinuo(self):
        if not self.continueTt:
            self.tiempoNoContinuo = 99999
            self.pendienteNoContinuo = False

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        if self.puntos < -self.expedition.tolerance:
            self.restart(True)
            self.state = ST_ENDGAME
            self.main_window.pon_toolbar((TB_CLOSE, TB_REINIT, TB_CONFIG, TB_UTILITIES))
            return
            # if change_game:
            #     self.terminar()
            #     return
            # self.reiniciar()

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

        # self.refresh()

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
            if not self.continueTt:
                QtCore.QTimer.singleShot(1000, self.analizaNoContinuo)
                self.tiempoNoContinuo = 0
                self.pendienteNoContinuo = True

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jgUsu = self.check_human_move(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jgObj = self.gameObj.move(self.posJugadaObj)
        fen = jgObj.position_before.fen()

        siAnalizaJuez = True
        if self.book:
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
            position = self.game.last_position
            saved = fen in self.dic_analysis
            if saved:
                rmObj, posObj, analysis, mrm = self.dic_analysis[fen]
            else:
                if self.continueTt:
                    um = QTUtil2.analizando(self.main_window)
                    mrm = self.analyze_minimum(3000) if self.continueTt else self.mrm
                    um.final()
                else:
                    self.analizaNoContinuoFinal()
                    mrm = self.mrm
                rmObj, posObj = mrm.buscaRM(jgObj.movimiento())
                analysis = mrm, posObj
                self.dic_analysis[fen] = [rmObj, posObj, analysis, mrm]

            rmUsu, posUsu = mrm.buscaRM(jgUsu.movimiento())
            if rmUsu is None:
                um = QTUtil2.analizando(self.main_window)
                self.analyze_end()
                rmUsu = self.xanalyzer.valora(position, from_sq, to_sq, promotion)
                mrm.agregaRM(rmUsu)
                self.analyze_begin()
                um.final()

            w = WindowJuicio.WJuicio(self, self.xanalyzer, self.nombreObj, position, mrm, rmObj, rmUsu, analysis, is_competitive=False)
            w.exec_()

            if not saved:
                analysis = w.analysis
                self.dic_analysis[fen][2] = analysis

            dpts = w.difPuntos()
            self.puntos += dpts
            self.ponPuntos()

            if posUsu != posObj:
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
        if not self.continueTt:
            self.terminaNoContinuo()

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

    def put_result(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        change_game, is_last, is_last_last = self.expedition.add_try(True, self.vtime, self.puntos)

        if is_last:
            mensaje = _("Congratulations, goal achieved")
            if is_last_last:
                mensaje += "\n\n" + _("You have climbed Everest!")
            self.mensaje(mensaje)
        else:
            mensaje = _("Congratulations you have passed this game.")
            self.mensajeEnPGN(mensaje)

        self.terminar()
