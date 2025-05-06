from PySide2 import QtCore

from Code import Manager
from Code import Util
from Code.Base import Move, Game
from Code.Base.Constantes import (
    GT_VARIATIONS,
    ST_ENDGAME,
    ST_PLAYING,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ACCEPT,
    TB_CANCEL,
    TB_UTILITIES,
    GO_START,
    ADJUST_BETTER,
)
from Code.QT import Iconos, QTUtil, QTUtil2
import Code.PlayAgainstEngine.WPlayAgainstEngine as WindowEntMaq


class ManagerVariations(Manager.Manager):
    accepted: bool
    is_white_bottom: bool
    with_engine_active: bool
    dicRival: dict
    play_against_engine: bool
    is_human_side_white: bool

    def start(self, game, is_white_bottom, with_engine_active, is_competitive, go_to_move=None):

        self.thinking(True)

        self.kibitzers_manager = self.procesador.kibitzers_manager

        self.accepted = False

        self.game = game
        self.is_white_bottom = is_white_bottom
        self.with_engine_active = with_engine_active
        self.is_competitive = is_competitive

        self.game_type = GT_VARIATIONS

        self.human_is_playing = True
        self.dicRival = {}

        self.play_against_engine = False

        self.state = ST_PLAYING

        self.set_toolbar((TB_ACCEPT, TB_CANCEL, TB_TAKEBACK, TB_REINIT, TB_CONFIG, TB_UTILITIES))

        self.is_human_side_white = is_white_bottom
        self.main_window.active_game(True, False)
        self.remove_hints(True, False)
        self.main_window.set_label1(None)
        self.main_window.set_label2(None)
        self.show_side_indicator(True)
        self.put_pieces_bottom(self.is_human_side_white)
        self.set_dispatcher(self.player_has_moved)
        self.pgn_refresh(True)

        self.show_info_extra()

        self.refresh()

        if len(self.game):
            if go_to_move is None:
                self.move_according_key(GO_START)
                move = self.game.move(0)
            else:
                self.place_in_movement(go_to_move)
                move = self.game.move(go_to_move)
            self.put_arrow_sc(move.from_sq, move.to_sq)
            self.disable_all()
        else:
            self.set_position(self.game.last_position)

        self.thinking(False)

        is_white = self.game.last_position.is_white
        self.is_human_side_white = is_white
        self.human_is_playing = True

        if with_engine_active and not is_competitive:
            self.change_rival()
            self.active_engine()

        if not len(self.game):
            self.play_next_move()
        else:
            self.goto_current()

    def run_action(self, key):
        if key == TB_ACCEPT:
            self.accepted = True
            # self.resultado =
            self.procesador.close_engines()
            self.main_window.accept()

        elif key == TB_CANCEL:
            self.procesador.close_engines()
            self.main_window.reject()

        elif key == TB_TAKEBACK:
            self.takeback()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar()

        elif key == TB_UTILITIES:
            sep = (None, None, None, None)
            li_extra_options = [
                ("books", _("Consult a book"), Iconos.Libros()),
                sep,
                ("pastepgn", _("Paste PGN"), Iconos.Pegar16(), "Ctrl+V"),
            ]

            resp = self.utilities(li_extra_options)
            if resp == "books":
                li_movs = self.librosConsulta(True)
                if li_movs:
                    for x in range(len(li_movs) - 1, -1, -1):
                        from_sq, to_sq, promotion = li_movs[x]
                        self.player_has_moved(from_sq, to_sq, promotion)
                elif resp == "pastepgn":
                    self.paste_pgn()


        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def control_teclado(self, nkey, modifiers):
        if modifiers and (modifiers & QtCore.Qt.ControlModifier) > 0:
            if nkey == QtCore.Qt.Key_V:
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
            if self.game.first_position != game.first_position:
                return
            self.game = game
            self.reiniciar()

    def valor(self):
        if self.accepted:
            return self.game
        else:
            return None

    def final_x(self):
        self.procesador.close_engines()
        self.main_window.reject()
        return False

    def final_x0(self):
        self.procesador.close_engines()
        self.main_window.reject()
        return False

    def place_in_movement(self, movenum):
        row = (movenum + 1) / 2 if self.game.starts_with_black else movenum / 2
        move: Move.Move = self.game.move(movenum)
        is_white = move.position_before.is_white
        self.main_window.pgnColocate(row, is_white)
        self.set_position(move.position)
        self.put_view()

    def takeback(self):
        if len(self.game) and self.in_end_of_line():
            self.game.remove_only_last_movement()
            if not self.fen:
                self.game.assign_opening()
            self.goto_end()
            self.refresh()
            self.play_next_move()

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.put_view()
        self.board.set_position(self.game.last_position)

        is_white = self.game.last_position.is_white
        self.is_human_side_white = is_white
        self.human_is_playing = True

        if self.game.is_finished():
            return

        self.set_side_indicator(is_white)

        self.activate_side(is_white)
        self.refresh()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move = self.check_human_move(from_sq, to_sq, promotion)
        if not move:
            return False
        self.move_the_pieces(move.liMovs)

        self.add_move(move)
        if self.play_against_engine:
            self.play_against_engine = False
            self.disable_all()
            self.play_rival()
            self.play_against_engine = True  # Como juega por mi pasa por aqui, para que no se meta en un bucle infinito

        self.play_next_move()
        return True

    def add_move(self, move):
        self.game.add_move(move)

        self.beep_extended(True)

        self.changed = True

        self.put_arrow_sc(move.from_sq, move.to_sq)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def reiniciar(self):
        self.main_window.activaInformacionPGN(False)
        self.start(self.game, self.is_white_bottom, self.with_engine_active, self.is_competitive)

    def configurar(self):
        if not self.is_competitive:
            if self.play_against_engine:
                mt = _X(_("Disable %1"), self.xrival.name)
                li_extra_options = [("engine_disable", mt, Iconos.Engines()), (None, None, None),
                                    ("engine_change", _("Change opponent"), Iconos.Engine2())]
            else:
                mt = _X(_("Enable %1"), _("Engine").lower())
                li_extra_options = [("engine_enable", mt, Iconos.Engines()), ]


        else:
            li_extra_options = []

        resp = Manager.Manager.configurar(self, li_extra_options, with_change_tutor=not self.is_competitive)
        if resp:
            self.set_label1("")
            if resp == "engine_disable":
                self.xrival.terminar()
                self.xrival = None
                self.play_against_engine = False
            elif resp in ("engine_enable", "engine_change"):
                if self.play_against_engine:
                    self.xrival.terminar()
                    self.xrival = None
                    self.play_against_engine = False
                self.change_rival()

    def play_rival(self):
        if not self.is_finished():
            self.thinking(True)
            rm = self.xrival.play_game(self.game, adjusted=self.xrival.nAjustarFuerza)
            if rm.from_sq:
                ok, self.error, move = Move.get_game_move(
                    self.game, self.game.last_position, rm.from_sq, rm.to_sq, rm.promotion
                )
                self.add_move(move)
                self.move_the_pieces(move.liMovs)
            self.thinking(False)

    def active_engine(self):
        dic_base = self.configuration.read_variables("ENG_VARIANTES")
        if dic_base:
            self.set_rival(dic_base)
        else:
            self.change_rival()

    def change_rival(self):

        if self.dicRival:
            dic_base = self.dicRival
        else:
            dic_base = self.configuration.read_variables("ENG_VARIANTES")
        dic_base["ISWHITE"] = self.is_human_side_white

        dic = self.dicRival = WindowEntMaq.change_rival(
            self.main_window, self.configuration, dic_base, is_create_own_game=True
        )

        if dic:
            self.set_rival(dic)

    def set_rival(self, dic):
        dr = dic["RIVAL"]
        rival = dr["CM"]
        if not Util.exist_file(rival.path_exe):
            return self.change_rival()
        r_timems = dr.get("ENGINE_TIME", 0) * 100  # Se guarda en decimas -> milesimas
        r_depth = dr.get("ENGINE_DEPTH", 0)
        r_nodes = dr.get("ENGINE_NODES", 0)
        if r_timems <= 0:
            r_timems = None
        if r_depth <= 0:
            r_depth = None
        if r_nodes <= 0:
            r_nodes = None
        if r_timems is None and r_depth is None and r_nodes is None and not dic.get("SITIEMPO", False):
            r_timems = 1000

        n_ajustar_fuerza = dic["ADJUST"]
        self.xrival = self.procesador.creaManagerMotor(rival, r_timems, r_depth, n_ajustar_fuerza != ADJUST_BETTER)
        if r_nodes:
            self.xrival.set_nodes(r_nodes)
        self.xrival.nAjustarFuerza = n_ajustar_fuerza

        self.is_human_side_white = dic["ISWHITE"]
        self.is_engine_side_white = not self.is_human_side_white

        dic["ROTULO1"] = _("Opponent") + ": <b>" + self.xrival.name
        self.set_label1(dic["ROTULO1"])
        self.play_against_engine = True
        self.configuration.write_variables("ENG_VARIANTES", dic)
        if self.game.is_white() == self.is_engine_side_white:
            self.play_rival()
            self.play_next_move()
