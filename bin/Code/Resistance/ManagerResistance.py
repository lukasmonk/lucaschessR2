from Code import Manager
from Code import Util
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_RESIGN,
    TB_UTILITIES,
    GT_RESISTANCE,
)
from Code.QT import QTUtil2


class ManagerResistance(Manager.Manager):
    def start(self, resistance, num_engine, key):

        self.game_type = GT_RESISTANCE

        self.resistance = resistance
        self.num_engine = num_engine
        self.key = key
        is_white = "WHITE" in key
        self.seconds, self.puntos, self.maxerror = resistance.actual()
        self.movimientos = 0
        self.rival_points = 0
        self.lostmovepoints = 0

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.siBoxing = True

        self.rm_rival = None
        self.moves_rival = 0

        # debe hacerse antes que rival
        self.procesador.close_engines()
        self.xarbitro = self.procesador.creaManagerMotor(self.configuration.engine_tutor(), self.seconds * 1000, None)
        self.xarbitro.remove_multipv()

        engine = resistance.dameClaveEngine(num_engine)
        rival = self.configuration.buscaRival(engine)
        self.xrival = self.procesador.creaManagerMotor(rival, self.seconds * 1000, None)

        self.game.set_tag("Event", _("Resistance Test"))

        player = self.configuration.nom_player()
        other = self.xrival.name
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.set_toolbar((TB_RESIGN, TB_REINIT, TB_CONFIG, TB_UTILITIES))
        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        self.remove_hints()
        self.set_activate_tutor(False)
        self.show_side_indicator(True)
        self.put_target_label()
        self.put_current_label()
        self.pgn_refresh(True)
        self.show_info_extra()
        self.check_boards_setposition()

        tp = self.resistance.tipo
        mode = _("Normal")
        if tp:
            mode = _("Blindfold chess")
            if tp == "p1":
                mode += "-" + _("Hide only our pieces")
            elif tp == "p2":
                mode += "-" + _("Hide only opponent pieces")
            self.game.set_tag("Mode", mode)
            b = n = False
            if tp == "p2":
                if is_white:
                    b = True
                else:
                    n = True
            elif tp == "p1":
                if is_white:
                    n = True
                else:
                    b = True
            self.board.mostrarPiezas(b, n)

        self.play_next_move()

    def put_target_label(self):
        label = self.resistance.rotuloActual(False)
        label += "<br><br><b>%s</b>: %s" % (_("Opponent"), self.xrival.name)
        label += "<br><b>%s</b>: %s" % (_("Record"), self.resistance.dameEtiRecord(self.key, self.num_engine))

        self.set_label1(label)

    def put_current_label(self):
        label = "<b>%s</b>: %d" % (_("Moves"), self.movimientos)

        color = "black"
        if self.rival_points != 0:
            color = "red" if self.rival_points > 0 else "green"

        label += '<br><b>%s</b>: <font color="%s"><b>%d</b></font>' % (_("Score"), color, -self.rival_points)

        self.set_label2(label)

    def run_action(self, key):
        if key == TB_RESIGN:
            self.finJuego(False)

        elif key == TB_CLOSE:
            self.procesador.close_engines()
            self.procesador.start()
            self.procesador.entrenamientos.resistance(self.resistance.tipo)

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True, with_change_tutor=False, with_blinfold=False)

        elif key == TB_UTILITIES:
            self.utilities(with_tree=self.state == ST_ENDGAME)

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def reiniciar(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.game.set_position()
            self.main_window.activaInformacionPGN(False)
            self.start(self.resistance, self.num_engine, self.key)

    def final_x(self):
        return self.finJuego(False)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.put_current_label()

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        if self.game.is_finished():
            self.autosave()
            if self.game.is_mate():
                si_ganado = self.is_human_side_white != is_white
                if si_ganado:
                    self.movimientos += 2000
                self.finJuego(True)
                return
            if self.game.is_draw():
                self.movimientos += 1000
                self.finJuego(True)
                return

        si_rival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if si_rival:
            self.thinking(True)
            self.disable_all()

            si_pensar = True

            puntosRivalPrevio = self.rival_points

            if si_pensar:
                self.rm_rival = self.xrival.play_seconds(self.game, self.seconds)
                self.rival_points = self.rm_rival.centipawns_abs()
                self.put_current_label()
            self.thinking(False)

            if self.rival_has_moved(self.rm_rival):
                self.moves_rival += 1
                lostmovepoints = self.rival_points - puntosRivalPrevio
                if self.siBoxing and self.moves_rival > 1:
                    if (self.rival_points > self.puntos) or (self.maxerror and lostmovepoints > self.maxerror):
                        if self.verify():
                            return
                self.play_next_move()

        else:

            self.human_is_playing = True
            self.activate_side(is_white)

    def verify(self):
        if len(self.game) < (3 if self.is_engine_side_white else 4):
            return False
        self.disable_all()
        if self.xrival.confMotor.key != self.xarbitro.confMotor.key:
            sc = max(3, self.seconds)

            um = QTUtil2.waiting_message.start(self.main_window, _("Checking..."))
            rm1 = self.xarbitro.play_seconds(self.game, sc)
            self.rival_points = -rm1.centipawns_abs()
            self.put_current_label()
            if self.maxerror:
                game1 = self.game.copia()
                game1.remove_only_last_movement()
                game1.remove_only_last_movement()
                rm0 = self.xarbitro.play_seconds(game1, sc)
                previoRival = -rm0.centipawns_abs()
                self.lostmovepoints = self.rival_points - previoRival
                if self.lostmovepoints > self.maxerror:
                    self.movimientos -= 1
                    um.final()
                    return self.finJuego(False)
            um.final()

        if self.rival_points > self.puntos:
            self.movimientos -= 1
            return self.finJuego(False)

        return False

    def finJuego(self, siFinPartida):
        if self.siBoxing:
            if self.movimientos:
                siRecord = self.resistance.put_result(self.num_engine, self.key, self.movimientos)
            else:
                siRecord = False

            if siFinPartida:
                txt = "<h2>%s<h2>" % (_("Game ended"))
                txt += "<h3>%s<h3>" % (self.resistance.dameEti(Util.today(), self.movimientos))
            else:
                if self.rival_points > self.puntos:
                    txt = "<h3>%s</h3>" % (_X(_("You have lost %1 centipawns."), str(self.rival_points)))
                else:
                    txt = ""
                if self.lostmovepoints > 0:
                    msg = _("You have lost in the last move %d centipawns")
                    try:
                        msg = msg % self.lostmovepoints
                    except:
                        msg += " %d" % self.lostmovepoints
                    txt += "<h3>%s</h3>" % msg

            if siRecord:
                txt += "<h2>%s<h2>" % (_("New record!"))
                txt += "<h3>%s<h3>" % (self.resistance.dameEtiRecord(self.key, self.num_engine))
                self.put_target_label()

            if siFinPartida:
                self.message_on_pgn(txt)
            else:
                br = "<br>" if txt else ""
                resp = QTUtil2.pregunta(
                    self.main_window,
                    "%s%s%s" % (txt, br, _("Do you want to resign or continue playing?")),
                    label_yes=_("Resign"),
                    label_no=_("Continue"),
                )
                if not resp:
                    self.siBoxing = False
                    return False

        self.disable_all()
        self.state = ST_ENDGAME
        self.procesador.close_engines()
        self.xarbitro.terminar()
        self.main_window.adjust_size()
        self.main_window.resize(0, 0)
        if self.movimientos >= 1:
            li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]
            self.set_toolbar(li_options)
        else:
            self.run_action(TB_CLOSE)

        return True

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.error = ""
        self.movimientos += 1
        self.play_next_move()
        return True

    def add_move(self, move, is_player_move):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def rival_has_moved(self, engine_response):
        from_sq = engine_response.from_sq
        to_sq = engine_response.to_sq

        promotion = engine_response.promotion

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if ok:
            self.error = ""
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            return True
        else:
            self.error = mens
            return False
