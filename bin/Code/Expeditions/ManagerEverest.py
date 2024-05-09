import copy
import time

from PySide2 import QtCore

from Code import Manager
from Code.Base.Constantes import ST_ENDGAME, ST_PLAYING, TB_CLOSE, TB_CONFIG, TB_CANCEL, TB_UTILITIES, GT_AGAINST_PGN
from Code.Expeditions import Everest
from Code.Openings import Opening
from Code.QT import QTUtil2
from Code.QT import WindowJuicio


class ManagerEverest(Manager.Manager):
    def start(self, recno):

        self.expedition = Everest.Expedition(self.configuration, recno)
        self.expedition.run()

        self.dic_analysis = {}

        self.game_type = GT_AGAINST_PGN

        self.is_competitive = True
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.is_analyzing = False
        self.is_human_side_white = self.expedition.is_white
        self.is_engine_side_white = not self.expedition.is_white
        self.game_obj = self.expedition.game
        self.game.set_tags(self.game_obj.li_tags)
        self.numJugadasObj = self.game_obj.num_moves()
        self.posJugadaObj = 0
        self.name_obj = self.expedition.name

        self.xanalyzer.maximize_multipv()

        self.puntos = 0
        self.vtime = 0.0

        self.book = Opening.OpeningPol(999)

        self.set_toolbar((TB_CANCEL, TB_CONFIG))

        self.main_window.active_game(True, False)
        self.remove_hints(True, True)

        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(self.is_human_side_white)
        self.show_side_indicator(True)
        self.set_label1(self.expedition.label())
        self.set_label2("")

        self.pgn_refresh(True)
        self.show_info_extra()
        self.check_boards_setposition()

        var_config = "EXPEDITIONS"

        dic = self.configuration.read_variables(var_config)

        self.show_all = dic.get("SHOW_ALL", False)
        self.show_rating_always, self.show_rating_different, self.show_rating_never = None, True, False
        self.show_rating = dic.get("SHOW_RATING", self.show_rating_always)

        self.state = ST_PLAYING
        self.play_next_move()

    def set_score(self):
        self.set_label2("%s : <b>%d</b>" % (_("Score"), self.puntos))

    def run_action(self, key):
        if key == TB_CANCEL:
            self.cancelar()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

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
        self.analyze_terminate()
        self.terminaNoContinuo()
        self.procesador.start()
        self.procesador.showEverest(self.expedition.recno)

    def reiniciar(self):
        self.main_window.activaInformacionPGN(False)
        self.game.set_position()
        self.posJugadaObj = 0
        self.puntos = 0
        self.set_score()
        self.vtime = 0.0
        self.book = Opening.OpeningPol(999)
        self.state = ST_PLAYING
        self.board.set_position(self.game.first_position)
        self.pgn_refresh(True)
        self.check_boards_setposition()
        self.analyze_end()
        self.terminaNoContinuo()

        self.set_label1(self.expedition.label())
        self.set_score()
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
            licoment.append(_("You must repeat the game"))
        if licoment:
            comment = "\n".join(licoment)
            QTUtil2.message_information(self.main_window, comment)
        return change_game

    def analyze_begin(self):
        self.xanalyzer.ac_inicio(self.game)
        self.is_analyzing = True

    def analyze_minimum(self, minTime):
        self.mrm = copy.deepcopy(self.xanalyzer.ac_minimo(minTime, False))
        return self.mrm

    def analyze_state(self):
        self.xanalyzer.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xanalyzer.ac_estado())
        return self.mrm

    def analyze_end(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.xanalyzer.ac_final(-1)

    def analyze_terminate(self):
        if self.is_analyzing:
            self.is_analyzing = False
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
            self.set_toolbar((TB_CLOSE, TB_CONFIG, TB_UTILITIES))
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
        jg_usu = self.check_human_move(from_sq, to_sq, promotion)
        if not jg_usu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jg_obj = self.game_obj.move(self.posJugadaObj)
        fen = jg_obj.position_before.fen()

        si_analiza_juez = True
        if self.book:
            si_book_usu = self.book.check_human(fen, from_sq, to_sq)
            si_book_obj = self.book.check_human(fen, jg_obj.from_sq, jg_obj.to_sq)
            if si_book_usu and si_book_obj:
                if jg_obj.movimiento() != jg_usu.movimiento():
                    bmove = _("book move")
                    comment = "%s: %s %s<br>%s: %s %s" % (
                        self.name_obj,
                        jg_obj.pgn_translated(),
                        bmove,
                        self.configuration.x_player,
                        jg_usu.pgn_translated(),
                        bmove,
                    )
                    QTUtil2.message_information(self.main_window, comment)
                si_analiza_juez = False
            else:
                si_analiza_juez = True
                if not si_book_obj:
                    self.book = None

        analysis = None
        comment = None

        if si_analiza_juez:
            position = self.game.last_position
            saved = fen in self.dic_analysis
            if saved:
                rm_obj, pos_obj, analysis, mrm = self.dic_analysis[fen]
            else:
                if self.continueTt:
                    um = QTUtil2.analizando(self.main_window)
                    mrm = self.analyze_minimum(3000) if self.continueTt else self.mrm
                    um.final()
                else:
                    self.analizaNoContinuoFinal()
                    mrm = self.mrm
                rm_obj, pos_obj = mrm.search_rm(jg_obj.movimiento())
                analysis = mrm, pos_obj
                self.dic_analysis[fen] = [rm_obj, pos_obj, analysis, mrm]

            rm_usu, pos_usu = mrm.search_rm(jg_usu.movimiento())
            if rm_usu is None:
                um = QTUtil2.analizando(self.main_window)
                self.analyze_end()
                rm_usu = self.xanalyzer.valora(position, from_sq, to_sq, promotion)
                mrm.add_rm(rm_usu)
                self.analyze_begin()
                um.final()

            if self.show_rating == self.show_rating_different:
                pv_usu = jg_usu.movimiento()
                pv_obj = jg_obj.movimiento()
                si_analiza_juez = pv_usu != pv_obj
            elif self.show_rating == self.show_rating_never:
                si_analiza_juez = False

            if si_analiza_juez:
                w = WindowJuicio.WJuicio(
                    self, self.xanalyzer, self.name_obj, position, mrm, rm_obj, rm_usu, analysis,
                    is_competitive=not self.show_all
                )
                w.exec_()

                if not saved:
                    analysis = w.analysis
                    self.dic_analysis[fen][2] = analysis

                dpts = w.difPuntos()
                rm_usu = w.rmUsu
                rm_obj = w.rmObj
            else:
                dpts = rm_usu.score_abs5() - rm_obj.score_abs5()

            self.puntos += dpts
            self.set_score()

            if pos_usu != pos_obj:
                comentario_usu = " %s" % rm_usu.abbrev_text()
                comentario_obj = " %s" % rm_obj.abbrev_text()

                comentario_puntos = "%s = %d %+d %+d = %d" % (
                    _("Score"),
                    self.puntos - dpts,
                    rm_usu.centipawns_abs(),
                    -rm_obj.centipawns_abs(),
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
        if not self.continueTt:
            self.terminaNoContinuo()

        self.analyze_end()

        self.add_move(True, analysis, comment)

        self.play_next_move()
        return True

    def add_move(self, siNuestra, analysis=None, comment=None):
        move = self.game_obj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analysis:
            move.analysis = analysis
        if comment:
            move.set_comment(comment)

        self.game.add_move(move)
        self.check_boards_setposition()

        self.move_the_pieces(move.liMovs, True)
        self.board.set_position(move.position)
        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgn_refresh(self.game.last_position.is_white)

    def put_result(self):
        self.analyze_terminate()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        change_game, is_last, is_last_last = self.expedition.add_try(True, self.vtime, self.puntos)

        if is_last:
            mensaje = _("Congratulations, goal achieved")
            if is_last_last:
                mensaje += "\n\n" + _("You have climbed Everest!")
        else:
            mensaje = _("Congratulations you have passed this game.")
        self.mensaje(mensaje)

        self.terminar()
