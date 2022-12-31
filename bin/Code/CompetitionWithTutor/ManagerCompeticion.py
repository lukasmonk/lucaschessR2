import gettext
_ = gettext.gettext
import Code
from Code import Adjournments
from Code import Manager
from Code.Base import Move
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    RS_WIN_OPPONENT,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADJOURN,
    TB_CANCEL,
    TB_RESIGN,
    TB_UTILITIES,
    GT_COMPETITION_WITH_TUTOR,
)
from Code.CompetitionWithTutor import CompetitionWithTutor
from Code.Engines import EngineResponse
from Code.Openings import Opening
from Code.Polyglots import Books
from Code.QT import QTUtil2
from Code.Tutor import Tutor


class ManagerCompeticion(Manager.Manager):
    def start(self, categorias, categoria, nivel, is_white, puntos):
        self.base_inicio(categorias, categoria, nivel, is_white, puntos)
        self.play_next_move()

    def base_inicio(self, categorias, categoria, nivel, is_white, puntos):
        self.game_type = GT_COMPETITION_WITH_TUTOR

        self.liReiniciar = categoria, nivel, is_white

        self.dbm = CompetitionWithTutor.DBManagerCWT()

        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_competitive = True

        self.plays_instead_of_me_option = True

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.rm_rival = None

        self.categorias = categorias
        self.categoria = categoria
        self.nivelJugado = nivel
        self.puntos = puntos

        self.is_tutor_enabled = self.configuration.x_default_tutor_active
        self.main_window.set_activate_tutor(self.is_tutor_enabled)
        self.tutor_book = Books.BookGame(Code.tbook)

        self.hints = categoria.hints
        self.ayudas_iniciales = self.hints  # Se guarda para guardar el PGN

        self.in_the_opening = True
        self.opening = Opening.OpeningPol(nivel)  # lee las aperturas

        self.rival_conf = self.dbm.get_current_rival()
        self.xrival = self.procesador.creaManagerMotor(self.rival_conf, None, nivel)

        self.set_toolbar((TB_CANCEL, TB_RESIGN, TB_TAKEBACK, TB_REINIT, TB_ADJOURN, TB_CONFIG, TB_UTILITIES))
        self.main_window.activaJuego(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.put_pieces_bottom(is_white)
        self.ponAyudas(self.hints)
        self.show_side_indicator(True)
        label = "%s: %s\n%s %s %d" % (_("Opponent"), self.xrival.name, categoria.name(), _("Level"), nivel)
        if self.puntos:
            label += " (+%d %s)" % (self.puntos, _("points"))
        self.set_label1(label)
        self.xrotulo2()

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()

        self.game.set_tag("Event", _("Competition with tutor"))

        player = self.configuration.nom_player()
        other = "%s (%s %d)" % (self.xrival.name, _("Level"), self.nivelJugado)
        w, b = (player, other) if self.is_human_side_white else (other, player)
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.is_analyzed_by_tutor = False

        self.check_boards_setposition()

        self.game.add_tag_timestart()

    def xrotulo2(self):
        self.set_label2(
            "%s: <b>%s</b><br>%s: %d %s"
            % (_("Tutor"), self.xtutor.name, _("Total score"), self.dbm.puntuacion(), _("pts"))
        )

    def run_action(self, key):

        if key == TB_CANCEL:
            self.finalizar()

        elif key == TB_RESIGN:
            self.rendirse()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_UTILITIES:
            self.utilities(siArbol=False)

        elif key == TB_ADJOURN:
            self.adjourn()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def reiniciar(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.game.set_position()
            categoria, nivel, is_white = self.liReiniciar
            self.procesador.stop_engines()
            self.main_window.activaInformacionPGN(False)
            self.start(self.categorias, categoria, nivel, is_white, self.puntos)

    def adjourn(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):

            label_menu = _("Competition with tutor") + ". " + self.xrival.name

            dic = {
                "ISWHITE": self.is_human_side_white,
                "GAME_SAVE": self.game.save(),
                "SITUTOR": self.is_tutor_enabled,
                "HINTS": self.hints,
                "CATEGORIA": self.categoria.key,
                "LEVEL": self.nivelJugado,
                "PUNTOS": self.puntos,
                "RIVAL_KEY": self.dbm.get_current_rival_key(),
            }

            with Adjournments.Adjournments() as adj:
                adj.add(self.game_type, dic, label_menu)
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        puntos = dic["PUNTOS"]
        is_white = dic["ISWHITE"]
        nivel = dic["LEVEL"]
        dbm = CompetitionWithTutor.DBManagerCWT()
        categorias = dbm.get_categorias_rival(dic["RIVAL_KEY"])
        categoria = categorias.segun_clave(dic["CATEGORIA"])
        self.base_inicio(categorias, categoria, nivel, is_white, puntos)
        self.hints = dic["HINTS"]
        self.game.restore(dic["GAME_SAVE"])
        self.goto_end()

        self.play_next_move()

    def final_x(self):
        return self.finalizar()

    def finalizar(self):
        if self.state == ST_ENDGAME:
            self.ponFinJuego()
            return True
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("End game?")):
                return False  # no termina
            self.ponFinJuego()
            self.autosave()
        else:
            self.procesador.start()

        return False

    def rendirse(self):
        if self.state == ST_ENDGAME:
            return True
        siJugadas = len(self.game) > 0
        if siJugadas:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?")):
                return False  # no abandona
            self.resultado = RS_WIN_OPPONENT
            self.game.resign(self.is_human_side_white)
            self.ponFinJuego()
            self.autosave()
        else:
            self.procesador.start()

        return False

    def takeback(self):
        if self.hints and len(self.game):
            if QTUtil2.pregunta(self.main_window, _("Do you want to go back in the last movement?")):
                self.hints -= 1
                self.ponAyudas(self.hints)
                self.game.anulaUltimoMovimiento(self.is_human_side_white)
                self.in_the_opening = False
                self.game.assign_opening()
                self.goto_end()
                self.is_analyzed_by_tutor = False
                self.refresh()
                self.play_next_move()

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

        if self.hints == 0:
            if self.categoria.sinAyudasFinal:
                self.remove_hints()
                self.is_tutor_enabled = False

        siRival = is_white == self.is_engine_side_white
        self.set_side_indicator(is_white)

        self.refresh()

        if siRival:
            self.thinking(True)
            self.disable_all()

            siPensar = True

            if self.in_the_opening:

                ok, from_sq, to_sq, promotion = self.opening.run_engine(self.last_fen())

                if ok:
                    self.rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
                    self.rm_rival.from_sq = from_sq
                    self.rm_rival.to_sq = to_sq
                    self.rm_rival.promotion = promotion
                    siPensar = False
                else:
                    self.in_the_opening = False

            if siPensar:
                self.rm_rival = self.xrival.play_game(self.game)

            self.thinking(False)

            if self.rival_has_moved(self.rm_rival):
                self.play_next_move()
        else:
            self.human_is_playing = True
            self.activate_side(is_white)
            self.analyze_begin()

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()
        self.human_is_playing = False

        mensaje, beep, player_win = self.game.label_resultado_player(self.is_human_side_white)

        self.beepResultado(beep)
        if player_win:
            hecho = "B" if self.is_human_side_white else "N"
            if self.categorias.put_result(self.categoria, self.nivelJugado, hecho):
                mensaje += "\n\n%s: %d (%s)" % (
                    _("Move to the next level"),
                    self.categoria.level_done + 1,
                    self.categoria.name(),
                )
            self.dbm.set_categorias_rival(self.rival_conf.key, self.categorias)
            if self.puntos:
                puntuacion = self.dbm.puntuacion()
                mensaje += "\n\n%s: %d+%d = %d %s" % (
                    _("Total score"),
                    puntuacion - self.puntos,
                    self.puntos,
                    puntuacion,
                    _("pts"),
                )
                self.xrotulo2()

        self.mensaje(mensaje)
        self.ponFinJuego()
        self.autosave()

    def analyze_begin(self):
        self.if_analyzing = False
        self.is_analyzed_by_tutor = False
        if self.is_tutor_enabled:
            self.is_analyzed_by_tutor = False
            if not self.is_finished():
                self.if_analyzing = True
                if self.continueTt:
                    self.xtutor.ac_inicio(self.game)
                else:
                    self.xtutor.ac_inicio_limit(self.game)

    def analyze_end(self):
        if self.if_analyzing:
            self.mrmTutor = self.xtutor.ac_final(-1)
            self.is_analyzed_by_tutor = True
            self.if_analyzing = False

    def change_tutor_active(self):
        previous = self.is_tutor_enabled
        self.is_tutor_enabled = not previous
        self.set_activate_tutor(self.is_tutor_enabled)
        if previous:
            self.analyze_end()
        elif self.human_is_playing:
            self.analyze_begin()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False
        movimiento = move.movimiento()
        self.analyze_end()

        siMirarTutor = self.is_tutor_enabled
        if self.in_the_opening:
            if self.opening.check_human(self.last_fen(), from_sq, to_sq):
                siMirarTutor = False

        if siMirarTutor:
            if not self.is_analyzed_by_tutor:
                self.mrmTutor = self.analizaTutor()

            if self.mrmTutor is None:
                self.sigueHumano()
                return False
            if not self.tutor_book.si_esta(self.last_fen(), movimiento):
                if Tutor.launch_tutor_movimiento(self.mrmTutor, movimiento):
                    self.refresh()
                    if not move.is_mate:
                        tutor = Tutor.Tutor(self, move, from_sq, to_sq, False)

                        if self.in_the_opening:
                            liApPosibles = self.listaOpeningsStd.list_possible_openings(self.game)
                        else:
                            liApPosibles = None

                        if tutor.elegir(self.hints > 0, liApPosibles=liApPosibles):
                            if self.hints > 0:  # doble entrada a tutor.
                                self.set_piece_again(from_sq)
                                self.hints -= 1
                                from_sq = tutor.from_sq
                                to_sq = tutor.to_sq
                                promotion = tutor.promotion
                                ok, mens, jgTutor = Move.get_game_move(
                                    self.game, self.game.last_position, from_sq, to_sq, promotion
                                )
                                if ok:
                                    move = jgTutor
                        elif self.configuration.x_save_tutor_variations:
                            tutor.ponVariations(move, 1 + len(self.game) / 2)

                        del tutor

        self.move_the_pieces(move.liMovs)
        self.add_move(move, True)
        self.play_next_move()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.ponAyudas(self.hints)

        self.pgnRefresh(self.game.last_position.is_white)
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
