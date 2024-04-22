import FasterCode
from PySide2 import QtCore

from Code import Manager
from Code.Base import Game, Position
from Code.Base.Constantes import (
    GT_GAME,
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_CANCEL,
    TB_NEXT,
    TB_PGN_LABELS,
    TB_PREVIOUS,
    TB_REPLAY,
    TB_SAVE,
    TB_UTILITIES,
    ADJUST_BETTER,
)
from Code.PlayAgainstEngine import WPlayAgainstEngine
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import WReplay
from Code.QT import WindowPgnTags
from Code.Voyager import Voyager


class ManagerGame(Manager.Manager):
    dic_rival = None
    def start(self, game, is_complete, only_consult, with_previous_next, save_routine):
        self.game_type = GT_GAME

        self.game = game
        self.game.is_finished()  # Necesario para que no haya cambios a posteriori y close pregunte si grabar
        self.is_complete = is_complete
        self.only_consult = only_consult
        self.with_previous_next = with_previous_next
        self.save_routine = save_routine
        self.changed = False
        self.auto_rotate = self.get_auto_rotate()

        self.human_is_playing = True
        self.is_human_side_white = True

        self.state = ST_PLAYING

        self.main_window.active_game(True, False)
        self.remove_hints(True, False)
        self.main_window.set_label1(None)
        self.main_window.set_label2(None)
        self.set_dispatcher(self.player_has_moved)
        self.show_side_indicator(True)
        self.put_pieces_bottom(game.is_white())
        self.ponteAlPrincipio()
        self.show_info_extra()

        self.check_boards_setposition()

        self.put_information()
        self.put_toolbar()

        self.reinicio = self.game.save()

        if len(self.game) == 0:
            self.play_next_move()

    def is_changed(self):
        return self.changed or self.game.save() != self.reinicio

    def ask_for_save_game(self):
        if self.is_changed():
            return QTUtil2.question_withcancel(self.main_window, _("Do you want to save changes?"), _("Yes"), _("No"))
        return False

    def put_toolbar(self):
        li = [TB_CLOSE, TB_PGN_LABELS, TB_TAKEBACK, TB_REINIT, TB_REPLAY, TB_CONFIG, TB_UTILITIES]
        if self.changed and self.save_routine:
            pos = li.index(TB_PGN_LABELS)
            li.insert(pos, TB_SAVE)
        # if_previous, if_next = False, False
        if self.with_previous_next:
            pos = li.index(TB_PGN_LABELS)
            li.insert(pos, TB_NEXT)
            li.insert(pos, TB_PREVIOUS)
        self.set_toolbar(li)
        if self.with_previous_next:
            if_previous, if_next = self.with_previous_next("with_previous_next", self.game)
            self.main_window.enable_option_toolbar(TB_PREVIOUS, if_previous)
            self.main_window.enable_option_toolbar(TB_NEXT, if_next)
            QTUtil.refresh_gui()

    def put_information(self):
        white = black = result = None
        for key, valor in self.game.li_tags:
            key = key.upper()
            if key == "WHITE":
                white = valor
            elif key == "BLACK":
                black = valor
            elif key == "RESULT":
                result = valor
        self.set_label1(
            "%s : <b>%s</b><br>%s : <b>%s</b>" % (_("White"), white, _("Black"), black) if white and black else ""
        )
        self.set_label2("%s : <b>%s</b>" % (_("Result"), result) if result else "")

    def reiniciar(self):
        if self.is_changed() and not QTUtil2.pregunta(self.main_window, _("You will loose all changes, are you sure?")):
            return
        p = Game.Game()
        p.restore(self.reinicio)
        p.recno = getattr(self.game, "recno", None)
        self.main_window.activaInformacionPGN(False)
        self.start(p, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine)

    def run_action(self, key):
        if key == TB_REINIT:
            self.reiniciar()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_SAVE:
            if self.save_routine:
                self.save_routine(self.game.recno, self.game)
                self.changed = False
                self.reinicio = self.game.save()
                self.put_toolbar()
            else:
                self.main_window.accept()

        elif key == TB_CONFIG:
            self.configurar()

        elif key == TB_UTILITIES:
            self.utilities_gs()

        elif key == TB_PGN_LABELS:
            self.informacion()

        elif key in (TB_CANCEL, TB_CLOSE):
            self.end_game()

        elif key in (TB_PREVIOUS, TB_NEXT):
            if self.ask_for_save_game():
                self.with_previous_next("save", self.game)
            game1 = self.with_previous_next("previous" if key == TB_PREVIOUS else "next", self.game)
            self.main_window.setWindowTitle(game1.window_title())
            self.start(game1, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def end_game(self):
        ok = False
        if not self.only_consult:
            ok = self.ask_for_save_game()

        if ok is None:
            return ok

        if ok:
            self.main_window.accept()
        else:
            self.main_window.reject()
        return ok

    def final_x(self):
        return self.end_game()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.put_view()

        is_white = self.game.last_position.is_white
        self.is_human_side_white = is_white  # Compatibilidad, sino no funciona el cambio en pgn

        if self.game.is_finished():
            self.show_result()
            return

        self.set_side_indicator(is_white)
        self.refresh()

        self.human_is_playing = True
        self.activate_side(is_white)

    def show_result(self):
        self.state = ST_ENDGAME
        self.disable_all()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.human_is_playing = True
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)

        self.play_next_move()
        if not self.changed:
            self.changed = True
            self.put_toolbar()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def informacion(self):
        if WindowPgnTags.menu_pgn_labels(self.main_window, self.game):
            fen_antes = self.game.get_tag("FEN")
            resp = WindowPgnTags.edit_tags_pgn(self.procesador.main_window, self.game.li_tags, not self.is_complete)
            if resp:
                self.game.li_tags = resp
                self.game.set_result()
                fen_despues = self.game.get_tag("FEN")
                if fen_antes != fen_despues:
                    fen_antes_fenm2 = FasterCode.fen_fenm2(fen_antes)
                    fen_despues_fenm2 = FasterCode.fen_fenm2(fen_despues)
                    if fen_antes_fenm2 != fen_despues_fenm2:
                        cp = Position.Position()
                        cp.read_fen(fen_despues)
                        self.game.set_position(cp)
                        self.start(
                            self.game, self.is_complete, self.only_consult, self.with_previous_next,
                            self.save_routine
                        )

                self.put_information()
                if not self.changed:
                    if self.is_changed():
                        self.changed = True
                        self.put_toolbar()

    def utilities_gs(self):
        sep = (None, None, None)
        li_mas_opciones = [(None, _("Change the starting position"), Iconos.PGN())]
        if not self.is_complete:
            li_mas_opciones.extend(
                [
                    ("position", _("Board editor"), Iconos.Datos()),
                    sep,
                    ("pasteposicion", _("Paste FEN position"), Iconos.Pegar16()),
                    sep,
                    ("voyager", _("Voyager 2"), Iconos.Voyager()),
                ]
            )

        li_mas_opciones.extend(
            [
                sep,
                ("leerpgn", _("Read PGN file"), Iconos.PGN_Importar()),
                sep,
                ("pastepgn", _("Paste PGN"), Iconos.Pegar16()),
                sep,
            ]
        )
        li_mas_opciones.extend([(None, None, True), sep, ("books", _("Consult a book"), Iconos.Libros())])

        resp = self.utilities(li_mas_opciones)

        if resp == "books":
            liMovs = self.librosConsulta(True)
            if liMovs:
                for x in range(len(liMovs) - 1, -1, -1):
                    from_sq, to_sq, promotion = liMovs[x]
                    self.player_has_moved(from_sq, to_sq, promotion)

        elif resp == "position":
            ini_position = self.game.first_position
            new_position, is_white_bottom = Voyager.voyager_position(self.main_window, ini_position)
            if new_position and new_position != ini_position:
                self.game.set_position(new_position)
                self.start(self.game, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine)
                self.changed = True
                self.put_toolbar()
                self.board.set_side_bottom(is_white_bottom)

        elif resp == "pasteposicion":
            texto = QTUtil.get_txt_clipboard()
            if texto:
                new_position = Position.Position()
                try:
                    new_position.read_fen(str(texto))
                    ini_position = self.game.first_position
                    if new_position and new_position != ini_position:
                        self.game.set_position(new_position)
                        self.start(
                            self.game, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine
                        )
                        self.changed = True
                        self.put_toolbar()

                except:
                    pass

        elif resp == "leerpgn":
            game = self.procesador.select_1_pgn(self.main_window)
            self.replace_game(game)

        elif resp == "pastepgn":
            self.paste_pgn()

        elif resp == "voyager":
            ptxt = Voyager.voyager_game(self.main_window, self.game)
            game = Game.Game()
            game.restore(ptxt)
            self.replace_game(game)

        elif resp == "replay_continuous":
            self.replay_continuous()

        else:
            if self.is_changed():
                self.changed = True
                self.put_toolbar()

    def replay_continuous(self):
        if self.ask_for_save_game():
            self.with_previous_next("save", self.game)

        def next_game():
            game1 = self.with_previous_next("next", self.game)
            if not game1:
                return False
            seconds_before1 = min(2.0, self.xpelicula.seconds_before)
            if not self.xpelicula.sleep_refresh(seconds_before1):
                return

            self.main_window.setWindowTitle(game1.window_title())
            self.start(game1, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine)
            return True

        self.xpelicula = WReplay.Replay(self, next_game=next_game)

    def replace_game(self, game):
        if not game:
            return
        if self.is_complete and not game.is_fen_initial():
            return
        p = Game.Game()
        p.assign_other_game(game)
        p.recno = getattr(self.game, "recno", None)
        self.start(p, self.is_complete, self.only_consult, self.with_previous_next, self.save_routine)

        self.changed = True
        self.put_toolbar()

    def control_teclado(self, nkey, modifiers):
        if nkey == QtCore.Qt.Key_V:  # V
            self.paste_pgn()

    def paste_pgn(self):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            ok, game = Game.pgn_game(texto)
            if not ok:
                QTUtil2.message_error(
                    self.main_window, _("The text from the clipboard does not contain a chess game in PGN format")
                )
                return
            self.replace_game(game)

    def play_rival(self):
        if not self.is_finished():
            self.thinking(True)
            rm = self.xrival.play_game(self.game, adjusted=self.xrival.nAjustarFuerza)
            self.thinking(False)
            if rm.from_sq:
                self.player_has_moved(rm.from_sq, rm.to_sq, rm.promotion)

    def change_rival(self):
        if self.dic_rival:
            dic_base = self.dic_rival
        else:
            dic_base = self.configuration.read_variables("ENG_MANAGERSOLO")

        dic = self.dic_rival = WPlayAgainstEngine.change_rival(
            self.main_window, self.configuration, dic_base, is_create_own_game=True
        )

        if dic:
            for k, v in dic.items():
                self.reinicio[k] = v

            dr = dic["RIVAL"]
            rival = dr["CM"]
            r_t = dr["TIME"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["DEPTH"]
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic.get("SITIEMPO", False):
                r_t = 1000

            nAjustarFuerza = dic["ADJUST"]
            self.xrival = self.procesador.creaManagerMotor(rival, r_t, r_p, nAjustarFuerza != ADJUST_BETTER)
            self.xrival.nAjustarFuerza = nAjustarFuerza

            dic["ROTULO1"] = _("Opponent") + ": <b>" + self.xrival.name
            self.set_label1(dic["ROTULO1"])
            self.play_against_engine = True
            self.configuration.write_variables("ENG_MANAGERSOLO", dic)

    def takeback(self):
        if len(self.game) and self.in_end_of_line():
            self.game.anulaSoloUltimoMovimiento()
            self.game.assign_opening()
            self.goto_end()
            self.state = ST_PLAYING
            self.refresh()
            self.changed = True
            self.put_toolbar()
            self.play_next_move()
