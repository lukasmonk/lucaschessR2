from Code import Manager
from Code.Base import Move, Position
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADVICE,
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
from Code.Tutor import Tutor
from Code.Washing import Washing


def manager_washing(procesador):
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

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True, True)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)

        self.game_obj = self.dbwashing.restoreGame(self.engine)
        self.numJugadasObj = self.game_obj.num_moves()
        self.posJugadaObj = 0

        li_options = [TB_CLOSE]
        self.set_toolbar(li_options)

        self.errores = 0

        self.book = Opening.OpeningPol(999, elo=engine.elo)

        is_white = self.engine.color
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)

        self.set_label1("%s: %s\n%s: %s" % (_("Opponent"), self.engine.name, _("Task"), self.engine.lbState()))

        self.pgn_refresh(True)

        self.game.pending_opening = True
        self.game.set_tag("Event", _("The Washing Machine"))

        player = self.configuration.nom_player()
        other = self.engine.name
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)
        self.game.add_tag_timestart()
        QTUtil.refresh_gui()

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black
        self.tc_player.config_as_time_keeper()
        self.tc_rival.config_as_time_keeper()

        self.check_boards_setposition()

        self.state = ST_PLAYING

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.terminar()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=False)

        elif key == TB_UTILITIES:
            self.utilities()

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
            move = self.game_obj.move(self.posJugadaObj)
            self.posJugadaObj += 1
            self.rival_has_moved(move.from_sq, move.to_sq, move.promotion)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.tc_player.start()
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
        self.message_on_pgn(mens)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        movUsu = move.movimiento().lower()
        time_s = self.tc_player.stop()
        self.dbwashing.add_time(time_s)
        move.set_time_ms(time_s * 1000)
        move.set_clock_ms(self.tc_player.pending_time * 1000)

        jgObj = self.game_obj.move(self.posJugadaObj)
        movObj = jgObj.movimiento().lower()
        if movUsu != movObj:
            lic = []
            if jgObj.analysis:
                mrmObj, posObj = jgObj.analysis
                rmObj = mrmObj.li_rm[posObj]
                lic.append("%s: %s (%s)" % (_("Played previously"), jgObj.pgn_translated(), rmObj.abbrev_text_base()))
                ptsObj = rmObj.centipawns_abs()
                rmUsu, posUsu = mrmObj.search_rm(movUsu)
                if posUsu >= 0:
                    lic.append("%s: %s (%s)" % (_("Played now"), move.pgn_translated(), rmUsu.abbrev_text_base()))
                    ptsUsu = rmUsu.centipawns_abs()
                    if ptsUsu < ptsObj - 10:
                        lic[-1] += ' <span style="color:red"><b>%s</b></span>' % _("Bad move")
                        self.errores += 1
                        self.dbwashing.add_hint()

                else:
                    lic.append("%s: %s - %s" % (_("Played now"), move.pgn_translated(), _("Bad move")))
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
                    lic.append("%s: %s - %s" % (_("Played now"), move.pgn_translated(), _("Bad move")))
                    self.errores += 1
                    self.dbwashing.add_hint()

            comment = "<br>".join(lic)
            QTUtil2.message_information(self.main_window, comment)
            self.set_position(move.position_before)

        # Creamos un move sin analysis
        ok, self.error, move = Move.get_game_move(
            self.game, self.game.last_position, jgObj.from_sq, jgObj.to_sq, jgObj.promotion
        )

        self.move_the_pieces(move.liMovs)
        self.add_move(move, True)
        self.posJugadaObj += 1
        if len(self.game) == self.game_obj.num_moves():
            self.end_game()

        else:
            self.error = ""
            self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def rival_has_moved(self, from_sq, to_sq, promotion):
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

        self.main_window.active_game(True, False)
        self.main_window.remove_hints(True, True)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)

        self.next_line()

    def next_line(self):
        self.line = self.dbwashing.next_tactic(self.engine)
        self.num_lines = self.engine.numTactics()
        if not self.line:
            return

        li_options = [TB_CLOSE, TB_ADVICE]
        self.set_toolbar(li_options)

        self.num_move = -1
        self.hints = 0
        self.errores = 0
        self.time_used = 0.0

        cp = Position.Position()
        cp.read_fen(self.line.fen)
        self.game.set_position(cp)

        is_white = cp.is_white
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        r1 = self.line.label
        self.set_label1(r1)
        r2 = "<b>%s: %d</b>" % (_("Pending"), self.num_lines)
        self.set_label2(r2)
        self.pgn_refresh(True)

        self.tc_keeper = self.tc_white
        self.tc_keeper.config_as_time_keeper()

        self.game.pending_opening = False

        QTUtil.refresh_gui()

        self.check_boards_setposition()

        self.state = ST_PLAYING

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_ADVICE:
            self.get_help()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=False)

        elif key == TB_UTILITIES:
            self.utilities()

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
            self.rival_has_moved(from_sq, to_sq, promotion)
            self.play_next_move()

        else:
            self.ayudasEsteMov = 0
            self.erroresEsteMov = 0
            self.human_is_playing = True
            self.tc_keeper.start()
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

            self.message_on_pgn(mens)
        else:
            QTUtil2.message_error(
                self.main_window, "%s: %d, %s: %d" % (_("Errors"), self.errores, _("Hints"), self.hints)
            )

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
            self.time_used += self.tc_keeper.stop()
            self.play_next_move()
            return True

        self.errores += 1
        self.erroresEsteMov += 1
        self.continue_human()
        return False

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def rival_has_moved(self, from_sq, to_sq, promotion):
        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.error = ""

    def get_help(self):
        self.set_label1(self.line.label)
        self.hints += 1
        mov = self.line.get_move(self.num_move).lower()
        self.board.mark_position(mov[:2])
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
    is_analyzing = False
    is_analyzed_by_tutor = False
    dbwashing = None
    washing = None
    engine = None
    is_human_side_white = None
    is_engine_side_white = None
    is_competitive = True
    opening = None
    is_tutor_enabled = None
    tc_player = None
    tc_rival = None
    tm_rival = None

    def start(self, dbwashing, washing, engine):
        self.dbwashing = dbwashing
        self.washing = washing

        self.engine = engine

        self.game_type = GT_WASHING_CREATE

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        is_white = self.engine.color
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white
        self.is_competitive = True

        self.opening = Opening.OpeningPol(30, self.engine.elo)

        self.is_tutor_enabled = True
        self.is_analyzing = False

        rival = self.configuration.buscaRival(self.engine.key)

        self.xrival = self.procesador.creaManagerMotor(rival, None, None)
        self.xrival.is_white = self.is_engine_side_white
        self.rm_rival = None
        self.tmRival = 15.0 * 60.0 * engine.elo / 3000.0

        self.xtutor.maximize_multipv()
        self.is_analyzed_by_tutor = False

        self.main_window.active_game(True, False)
        self.remove_hints()
        li = [TB_CLOSE, TB_REINIT, TB_TAKEBACK]
        self.set_toolbar(li)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)

        self.set_label1(
            "%s: %s\n%s: %s\n%s: %s"
            % (_("Opponent"), self.engine.name, _("Task"), self.engine.lbState(), _("Tutor"), self.xtutor.name)
        )
        self.put_data_label()

        self.show_info_extra()

        self.pgn_refresh(True)

        game = dbwashing.restoreGame(engine)
        if not (game is None):
            if not game.is_finished():
                self.game = game
                self.goto_end()
                self.main_window.base.pgn_refresh()
        else:
            player = self.configuration.nom_player()
            other = self.xrival.name
            w, b = (player, other) if self.is_human_side_white else (other, player)
            self.game.set_tag("Event", _("The Washing Machine"))
            self.game.set_tag("White", w)
            self.game.set_tag("Black", b)
            self.game.add_tag_timestart()

        self.check_boards_setposition()

        self.tc_player = self.tc_white if self.is_human_side_white else self.tc_black
        self.tc_rival = self.tc_white if self.is_engine_side_white else self.tc_black
        self.tc_player.config_as_time_keeper()
        self.tc_rival.config_as_time_keeper()

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
            self.show_result()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        si_rival = is_white == self.is_engine_side_white

        if si_rival:
            if self.play_rival():
                self.play_next_move()

        else:
            self.play_human(is_white)

    def play_rival(self):
        self.thinking(True)
        self.disable_all()

        self.tc_rival.start()

        from_sq = to_sq = promotion = ""
        si_encontrada = False

        if self.opening:
            si_encontrada, from_sq, to_sq, promotion = self.opening.run_engine(self.last_fen())
            if not si_encontrada:
                self.opening = None

        if si_encontrada:
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
            time_s = self.tc_rival.stop()
            move.set_time_ms(time_s * 1000)
            move.set_clock_ms(self.tc_rival.pending_time * 1000)

            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)
            return True
        else:
            return False

    def play_human(self, is_white):
        self.human_is_playing = True
        self.analyze_begin()
        self.tc_player.start()
        self.activate_side(is_white)

    def run_action(self, key):
        if key == TB_REINIT:
            self.reiniciar()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_CLOSE:
            self.final_x()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def analyze_begin(self):
        self.is_analyzing = False
        self.is_analyzed_by_tutor = False
        if not self.is_finished():
            if self.continueTt:
                self.xtutor.ac_inicio(self.game)
            else:
                self.xtutor.ac_inicio_limit(self.game)
            self.is_analyzing = True

    def analyze_end(self, is_mate=False):
        if is_mate:
            if self.is_analyzing:
                self.xtutor.stop()
            return
        if self.is_analyzed_by_tutor:
            return
        self.is_analyzing = False
        self.thinking(True)
        if self.continueTt:
            self.mrm_tutor = self.xtutor.ac_final(self.xtutor.mstime_engine)
        else:
            self.mrm_tutor = self.xtutor.ac_final_limit()
        self.thinking(False)
        self.is_analyzed_by_tutor = True

    def analyze_terminate(self):
        if self.is_analyzing:
            self.is_analyzing = False
            self.xtutor.ac_final(-1)

    def continue_analysis_human_move(self):
        self.analyze_begin()
        Manager.Manager.continue_human(self)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        movimiento = move.movimiento()
        time_s = self.tc_player.stop()
        self.add_time(time_s)

        si_analisis = False

        is_selected = False

        if self.opening:
            fen_base = self.last_fen()
            if self.opening.check_human(fen_base, from_sq, to_sq):
                is_selected = True
            else:
                self.opening = None

        self.analyze_end()  # tiene que acabar siempre
        if not is_selected:
            rm_user, n = self.mrm_tutor.search_rm(movimiento)
            if not rm_user:
                rm_user = self.xtutor.valora(self.game.last_position, from_sq, to_sq, move.promotion)
                if not rm_user:
                    self.continue_analysis_human_move()
                    return False
                self.mrm_tutor.add_rm(rm_user)
            si_analisis = True
            points_best, points_user = self.mrm_tutor.dif_points_best(movimiento)
            if (points_best - points_user) > 0:
                if not move.is_mate:
                    tutor = Tutor.Tutor(self, move, from_sq, to_sq, False)
                    if tutor.elegir(True):
                        self.set_piece_again(from_sq)
                        from_sq = tutor.from_sq
                        to_sq = tutor.to_sq
                        promotion = tutor.promotion
                        ok, mens, jgTutor = Move.get_game_move(
                            self.game, self.game.last_position, from_sq, to_sq, promotion
                        )
                        if ok:
                            move = jgTutor
                            self.add_hint()
                    del tutor

        self.move_the_pieces(move.liMovs)
        move.set_time_ms(time_s * 1000)  # puede haber cambiado
        move.set_clock_ms(self.tc_player.pending_time * 1000)

        if si_analisis:
            rm, nPos = self.mrm_tutor.search_rm(move.movimiento())
            if rm:
                move.analysis = self.mrm_tutor, nPos

        self.add_move(move, True)
        self.error = ""
        self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)

        self.refresh()

    def finalizar(self):
        self.analyze_terminate()
        self.main_window.active_game(False, False)
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

    def add_time(self, time_s=None):
        if time_s is None:
            time_s = self.tc_player.stop()
        if time_s:
            self.dbwashing.add_time(time_s)
            self.put_data_label()

    def add_game(self):
        self.dbwashing.add_game()
        self.put_data_label()

    def saveGame(self, is_end):
        self.dbwashing.saveGame(self.game, is_end)

    def cancelGame(self):
        self.dbwashing.saveGame(None, False)
        self.add_game()

    def takeback(self):
        if len(self.game):
            self.analyze_terminate()
            self.game.remove_last_move(self.is_human_side_white)
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

        self.analyze_terminate()

        self.add_time()
        self.add_game()
        self.game.set_position()
        self.dbwashing.saveGame(None, False)
        self.main_window.activaInformacionPGN(False)
        self.start(self.dbwashing, self.washing, self.engine)

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beep_result(beep)
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
