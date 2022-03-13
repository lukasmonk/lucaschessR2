from PySide2 import QtCore

from Code import Manager
from Code.Base import Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_HELP,
    TB_NEXT,
    TB_UTILITIES,
    GT_WASHING_CREATE,
    GT_WASHING_REPLAY,
    GT_WASHING_TACTICS,
)
from Code.Engines import EngineResponse
from Code.Openings import Opening
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import WindowJuicio
from Code.Tutor import Tutor
from Code.Washing import Washing


def managerWashing(procesador):
    dbwashing = Washing.DBWashing(procesador.configuration)
    washing = dbwashing.washing
    engine = washing.last_engine(procesador.configuration)
    if engine.state == Washing.CREATING:
        procesador.manager = ManagerWashingCreate(procesador)
        procesador.manager.start(dbwashing, washing, engine)

    elif engine.state == Washing.TACTICS:
        procesador.manager = ManagerWashingTactics(procesador)
        procesador.manager.start(dbwashing, washing, engine)

    elif engine.state == Washing.REPLAY:
        procesador.manager = ManagerWashingReplay(procesador)
        procesador.manager.start(dbwashing, washing, engine)


class ManagerWashingReplay(Manager.Manager):
    def start(self, dbwashing, washing, engine):
        self.dbwashing = dbwashing
        self.washing = washing
        self.engine = engine

        self.dbwashing.add_game()

        self.game_type = GT_WASHING_REPLAY

        self.human_is_playing = False

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(False)
        self.ayudas_iniciales = 0

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.remove_hints(True, True)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)

        self.gameObj = self.dbwashing.restoreGame(self.engine)
        self.numJugadasObj = self.gameObj.num_moves()
        self.posJugadaObj = 0

        li_options = [TB_CLOSE]
        self.set_toolbar(li_options)

        self.errores = 0

        self.book = Opening.OpeningPol(999, elo=engine.elo)

        is_white = self.engine.color
        self.human_side = is_white
        self.is_engine_side_white = not is_white
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)

        self.set_label1("%s: %s\n%s: %s" % (_("Opponent"), self.engine.name, _("Task"), self.engine.lbState()))

        self.pgnRefresh(True)

        self.game.pending_opening = True
        self.game.set_tag("Event", _("The Washing Machine"))

        player = self.configuration.nom_player()
        other = self.engine.name
        w, b = (player, other) if self.human_side else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)
        self.game.tag_timestart()
        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.state = ST_PLAYING

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.terminar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=False)

        elif key == TB_UTILITIES:
            self.utilidades()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.set_label2("<b>%s: %d</b>" % (_("Errors"), self.errores))

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        if siRival:
            move = self.gameObj.move(self.posJugadaObj)
            self.posJugadaObj += 1
            self.play_rival(move.from_sq, move.to_sq, move.promotion)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.timekeeper.start()
            self.activate_side(is_white)

    def end_game(self):
        ok = self.errores == 0
        self.dbwashing.done_reinit(self.engine)

        self.state = ST_ENDGAME
        self.disable_all()

        li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]
        self.set_toolbar(li_options)

        if ok:
            mens = _("Congratulations, this washing is done")
        else:
            mens = "%s<br>%s: %d" % (_("Done with errors."), _("Errors"), self.errores)
        self.mensajeEnPGN(mens)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        movUsu = move.movimiento().lower()
        self.dbwashing.add_time(self.timekeeper.stop())

        jgObj = self.gameObj.move(self.posJugadaObj)
        movObj = jgObj.movimiento().lower()
        if movUsu != movObj:
            lic = []
            if jgObj.analysis:
                mrmObj, posObj = jgObj.analysis
                rmObj = mrmObj.li_rm[posObj]
                lic.append("%s: %s (%s)" % (_("Played previously"), jgObj.pgn_translated(), rmObj.abrTextoBase()))
                ptsObj = rmObj.centipawns_abs()
                rmUsu, posUsu = mrmObj.buscaRM(movUsu)
                if posUsu >= 0:
                    lic.append("%s: %s (%s)" % (_("Played now"), move.pgn_translated(), rmUsu.abrTextoBase()))
                    ptsUsu = rmUsu.centipawns_abs()
                    if ptsUsu < ptsObj - 10:
                        lic[-1] += ' <span style="color:red"><b>%s</b></span>' % _("Bad move")
                        self.errores += 1
                        self.dbwashing.add_hint()

                else:
                    lic.append("%s: %s (?) %s" % (_("Played now"), move.pgn_translated(), _("Bad move")))
                    self.errores += 1
                    self.dbwashing.add_hint()

            else:
                # Debe ser una move de book para aceptarla
                fen = self.last_fen()
                siBookUsu = self.book.check_human(fen, from_sq, to_sq)
                bmove = _("book move")
                lic.append("%s: %s (%s)" % (_("Played previously"), jgObj.pgn_translated(), bmove))
                if siBookUsu:
                    lic.append("%s: %s (%s)" % (_("Played now"), move.pgn_translated(), bmove))
                else:
                    lic.append("%s: %s (?) %s" % (_("Played now"), move.pgn_translated(), _("Bad move")))
                    self.errores += 1
                    self.dbwashing.add_hint()

            comment = "<br>".join(lic)
            w = WindowJuicio.MensajeF(self.main_window, comment)
            w.mostrar()
            self.set_position(move.position_before)

        # Creamos un move sin analysis
        ok, self.error, move = Move.get_game_move(self.game, self.game.last_position, jgObj.from_sq, jgObj.to_sq, jgObj.promotion)

        self.move_the_pieces(move.liMovs)
        self.add_move(move, True)
        self.posJugadaObj += 1
        if len(self.game) == self.gameObj.num_moves():
            self.end_game()

        else:
            self.error = ""
            self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

    def play_rival(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.error = ""

    def terminar(self):
        self.procesador.start()
        self.procesador.showWashing()

    def final_x(self):
        self.procesador.start()
        return False


class ManagerWashingTactics(Manager.Manager):
    def start(self, dbwashing, washing, engine):
        self.dbwashing = dbwashing
        self.washing = washing
        self.engine = engine

        self.game_type = GT_WASHING_TACTICS

        self.human_is_playing = False

        self.is_tutor_enabled = False
        self.main_window.set_activate_tutor(False)
        self.ayudas_iniciales = 0

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.remove_hints(True, True)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)

        self.next_line()

    def next_line(self):
        self.line = self.dbwashing.next_tactic(self.engine)
        self.num_lines = self.engine.numTactics()
        if not self.line:
            return

        li_options = [TB_CLOSE, TB_HELP]
        self.set_toolbar(li_options)

        self.num_move = -1
        self.hints = 0
        self.errores = 0
        self.time_used = 0.0

        cp = Position.Position()
        cp.read_fen(self.line.fen)
        self.game.set_position(cp)

        is_white = cp.is_white
        self.human_side = is_white
        self.is_engine_side_white = not is_white
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        # r1 = self.line.label
        self.set_label1("")
        r2 = "<b>%s: %d</b>" % (_("Pending"), self.num_lines)
        self.set_label2(r2)
        self.pgnRefresh(True)

        self.game.pending_opening = False

        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.state = ST_PLAYING

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_HELP:
            self.ayuda()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=False)

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key == TB_NEXT:
            self.next_line()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        self.num_move += 1
        if self.num_move >= self.line.total_moves():
            self.end_line()
            return

        if siRival:
            pv = self.line.get_move(self.num_move)
            from_sq, to_sq, promotion = pv[:2], pv[2:4], pv[4:]
            self.play_rival(from_sq, to_sq, promotion)
            self.play_next_move()

        else:
            self.ayudasEsteMov = 0
            self.erroresEsteMov = 0
            self.human_is_playing = True
            self.timekeeper.start()
            self.activate_side(is_white)

    def end_line(self):
        ok = (self.hints + self.errores) == 0
        self.dbwashing.done_tactic(self.engine, ok)
        self.num_lines = self.engine.numTactics()

        self.state = ST_ENDGAME
        self.disable_all()

        li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]

        if self.num_lines:
            li_options.append(TB_NEXT)

        self.set_toolbar(li_options)

        self.set_label1(self.line.label)

        if ok:
            r2 = "<b>%s: %d</b>" % (_("Pending"), self.num_lines)
            self.set_label2(r2)
            mens = _("This line training is completed.")
            if self.num_lines == 0:
                mens = "%s\n%s" % (mens, _("You have solved all puzzles"))

            self.mensajeEnPGN(mens)
        else:
            QTUtil2.message_error(self.main_window, "%s: %d, %s: %d" % (_("Errors"), self.errores, _("Hints"), self.hints))

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            self.errores += 1
            return False

        movimiento = move.movimiento().lower()
        if movimiento == self.line.get_move(self.num_move).lower():
            self.move_the_pieces(move.liMovs)
            self.add_move(move, True)
            self.error = ""
            self.time_used += self.timekeeper.stop()
            self.play_next_move()
            return True

        self.errores += 1
        self.erroresEsteMov += 1
        self.sigueHumano()
        return False

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

    def play_rival(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.error = ""

    def ayuda(self):
        self.set_label1(self.line.label)
        self.hints += 1
        mov = self.line.get_move(self.num_move).lower()
        self.board.markPosition(mov[:2])
        self.ayudasEsteMov += 1
        if self.ayudasEsteMov > 1 and self.erroresEsteMov > 0:
            self.board.ponFlechasTmp([(mov[:2], mov[2:], True)], 1200)

    def end_game(self):
        self.procesador.start()
        self.procesador.showWashing()

    def final_x(self):
        self.procesador.start()
        return False


class ManagerWashingCreate(Manager.Manager):
    def start(self, dbwashing, washing, engine):
        self.dbwashing = dbwashing
        self.washing = washing

        self.engine = engine

        self.game_type = GT_WASHING_CREATE

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        is_white = self.engine.color
        self.human_side = is_white
        self.is_engine_side_white = not is_white
        self.is_competitive = True

        self.opening = Opening.OpeningPol(30, self.engine.elo)

        self.is_tutor_enabled = True
        self.siAnalizando = False
        # self.main_window.set_activate_tutor(self.is_tutor_enabled)

        rival = self.configuration.buscaRival(self.engine.key)

        self.xrival = self.procesador.creaManagerMotor(rival, None, None)
        self.xrival.is_white = self.is_engine_side_white
        self.rm_rival = None
        self.tmRival = 15.0 * 60.0 * engine.elo / 3000.0

        self.xtutor.maximize_multipv()
        self.is_analyzed_by_tutor = False

        self.main_window.activaJuego(True, False, False)
        self.remove_hints()
        li = [TB_CLOSE, TB_REINIT, TB_TAKEBACK]
        self.set_toolbar(li)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.set_label1(
            "%s: %s\n%s: %s\n %s: %s" % (_("Opponent"), self.engine.name, _("Task"), self.engine.lbState(), _("Tutor"), self.xtutor.name)
        )
        self.put_data_label()

        self.ponCapInfoPorDefecto()

        self.pgnRefresh(True)

        game = dbwashing.restoreGame(engine)
        if not (game is None):
            if not game.is_finished():
                self.game = game
                self.goto_end()
                self.main_window.base.pgnRefresh()
        else:
            player = self.configuration.nom_player()
            other = self.xrival.name
            w, b = (player, other) if self.human_side else (other, player)
            self.game.set_tag("Event", _("The Washing Machine"))
            self.game.set_tag("White", w)
            self.game.set_tag("Black", b)
            self.game.tag_timestart()

        self.check_boards_setposition()

        self.play_next_move()

    def put_data_label(self):
        datos = "%s: %d | %s: %d/%d | %s: %s" % (
            _("Games"),
            self.engine.games,
            _("Hints"),
            self.engine.hints_current,
            self.engine.hints,
            _("Time"),
            self.engine.lbTime(),
        )
        self.set_label2(datos)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.is_white()

        if self.game.is_finished():
            self.muestra_resultado()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        if siRival:
            if self.juegaRival():
                self.play_next_move()

        else:
            self.juegaHumano(is_white)

    def juegaRival(self):
        self.thinking(True)
        self.disable_all()

        from_sq = to_sq = promotion = ""
        siEncontrada = False

        if self.opening:
            siEncontrada, from_sq, to_sq, promotion = self.opening.run_engine(self.last_fen())
            if not siEncontrada:
                self.opening = None

        if siEncontrada:
            self.rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
            self.rm_rival.from_sq = from_sq
            self.rm_rival.to_sq = to_sq
            self.rm_rival.promotion = promotion

        else:
            self.rm_rival = self.xrival.play_time(self.game, self.tmRival, self.tmRival, 0)

        self.thinking(False)

        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, self.rm_rival.from_sq, self.rm_rival.to_sq, self.rm_rival.promotion
        )
        if ok:
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)
            return True
        else:
            return False

    def juegaHumano(self, is_white):
        self.human_is_playing = True
        self.analyze_begin()
        self.timekeeper.start()
        self.activate_side(is_white)

    def run_action(self, key):
        if key == TB_REINIT:
            self.reiniciar()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_CLOSE:
            self.final_x()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidades()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def analyze_begin(self):
        self.siAnalizando = False
        self.is_analyzed_by_tutor = False
        if self.continueTt:
            if not self.is_finished():
                self.xtutor.ac_inicio(self.game)
                self.siAnalizando = True
                QtCore.QTimer.singleShot(200, self.analizaSiguiente)
        else:
            self.analizaTutor()
            self.is_analyzed_by_tutor = True

    def analizaSiguiente(self):
        if self.siAnalizando:
            if self.human_is_playing and self.state == ST_PLAYING:
                if self.xtutor.engine:
                    mrm = self.xtutor.ac_estado()
                    if mrm:
                        QtCore.QTimer.singleShot(1000, self.analizaSiguiente)

    def analyze_end(self):
        estado = self.siAnalizando
        self.siAnalizando = False
        if self.is_analyzed_by_tutor:
            return
        if self.continueTt and estado:
            self.thinking(True)
            self.mrmTutor = self.xtutor.ac_final(max(self.xtutor.mstime_engine, 5000))
            self.thinking(False)
        else:
            self.mrmTutor = self.analizaTutor()

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xtutor.ac_final(-1)

    def sigueHumanoAnalisis(self):
        self.analyze_begin()
        Manager.Manager.sigueHumano(self)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        movimiento = move.movimiento()
        self.add_time()

        siAnalisis = False

        is_selected = False

        if self.opening:
            fenBase = self.last_fen()
            if self.opening.check_human(fenBase, from_sq, to_sq):
                is_selected = True
            else:
                self.opening = None

        self.analyze_end()  # tiene que acabar siempre
        if not is_selected:
            rmUser, n = self.mrmTutor.buscaRM(movimiento)
            if not rmUser:
                rmUser = self.xtutor.valora(self.game.last_position, from_sq, to_sq, move.promotion)
                if not rmUser:
                    self.sigueHumanoAnalisis()
                    return False
                self.mrmTutor.agregaRM(rmUser)
            siAnalisis = True
            pointsBest, pointsUser = self.mrmTutor.difPointsBest(movimiento)
            if (pointsBest - pointsUser) > 0:
                if not move.is_mate:
                    tutor = Tutor.Tutor(self, move, from_sq, to_sq, False)
                    if tutor.elegir(True):
                        self.set_piece_again(from_sq)
                        from_sq = tutor.from_sq
                        to_sq = tutor.to_sq
                        promotion = tutor.promotion
                        ok, mens, jgTutor = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
                        if ok:
                            move = jgTutor
                            self.add_hint()
                    del tutor

        self.move_the_pieces(move.liMovs)

        if siAnalisis:
            rm, nPos = self.mrmTutor.buscaRM(move.movimiento())
            if rm:
                move.analysis = self.mrmTutor, nPos

        self.add_move(move, True)
        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)

        self.refresh()

    def finalizar(self):
        self.analizaTerminar()
        self.main_window.activaJuego(False, False)
        self.quitaCapturas()
        self.procesador.start()
        self.procesador.showWashing()

    def final_x(self):
        if len(self.game) > 0:
            self.add_time()
            self.saveGame(False)
        self.finalizar()

    def add_hint(self):
        self.dbwashing.add_hint()
        self.put_data_label()

    def add_time(self):
        secs = self.timekeeper.stop()
        if secs:
            self.dbwashing.add_time(secs)
            self.put_data_label()

    def add_game(self):
        self.dbwashing.add_game()
        self.put_data_label()

    def saveGame(self, siFinal):
        self.dbwashing.saveGame(self.game, siFinal)

    def cancelGame(self):
        self.dbwashing.saveGame(None, False)
        self.add_game()

    def takeback(self):
        if len(self.game):
            self.analizaTerminar()
            self.game.anulaUltimoMovimiento(self.human_side)
            self.game.assign_opening()
            self.goto_end()
            self.opening = Opening.OpeningPol(30, self.engine.elo)
            self.is_analyzed_by_tutor = False
            self.add_hint()
            self.add_time()
            self.refresh()
            self.play_next_move()

    def reiniciar(self):
        if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            return

        self.add_time()
        self.add_game()
        self.game.set_position()
        self.dbwashing.saveGame(None, False)

        self.start(self.dbwashing, self.washing, self.engine)

    def muestra_resultado(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.human_side)

        self.beepResultado(beep)
        QTUtil.refresh_gui()

        QTUtil2.message(self.main_window, mensaje)

        li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]
        if player_win:
            li_options.insert(1, TB_REINIT)
        self.set_toolbar(li_options)
        self.remove_hints()

        self.game.set_tag("HintsUsed", self.engine.hints_current)
        self.autosave()
        if player_win:
            self.saveGame(True)
        else:
            self.cancelGame()

    def analize_position(self, row, key):
        if self.state != ST_ENDGAME:
            return
        Manager.Manager.analize_position(self, row, key)
