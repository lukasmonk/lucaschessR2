import time

from Code import Manager
from Code.Base import Game, Move
from Code.Base.Constantes import (
    WHITE,
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_REINIT,
    TB_CONFIG,
    TB_ADVICE,
    TB_NEXT,
    TB_UTILITIES,
    GT_TRAINBOOKSOL,
    TOP_RIGHT
)
from Code.Books import WBooksTrainOL
from Code.Engines import EngineResponse
from Code.QT import QTUtil2
from Code.SQL import UtilSQL


class ManagerTrainBooksOL(Manager.Manager):
    train_pos: int
    dbli_books_train: UtilSQL.ListObjSQL
    reg: WBooksTrainOL.BooksTrainOL
    pos_line: int
    time_used: float
    current_errors: int
    current_hints: int
    all_errors: int
    all_hints: int
    is_human_side_white: bool
    is_engine_side_white: bool
    game: Game.Game
    game_obj: Game.Game
    ini_time: float

    def start(self, dbli_books_train, train_rowid):
        self.train_pos = dbli_books_train.pos_rowid(train_rowid)
        self.dbli_books_train = dbli_books_train
        self.game_type = GT_TRAINBOOKSOL

        self.reg = self.dbli_books_train[self.train_pos]
        dic_training = self.reg.current_training()
        self.pos_line = dic_training["POS"]
        self.time_used = dic_training["TIME_USED"]
        self.all_errors = dic_training["ERRORS"]
        self.all_hints = dic_training["HINTS"]
        self.is_human_side_white = self.reg.side == WHITE
        self.is_engine_side_white = not self.is_human_side_white
        self.hints = 9999  # Para que analice sin problemas
        self.reinicio()

    def reinicio(self):
        self.game = Game.Game(fen=self.reg.start_fen)
        self.game_obj = Game.Game(fen=self.reg.start_fen)
        self.game_obj.read_pv(self.reg.lines[self.pos_line])

        self.main_window.active_game(True, False)
        self.set_dispatcher(self.player_has_moved)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints()
        self.put_pieces_bottom(self.is_human_side_white)
        self.pgn_refresh(True)

        self.set_toolbar((TB_CLOSE, TB_REINIT, TB_ADVICE, TB_CONFIG, TB_UTILITIES))

        self.show_info_extra()

        self.state = ST_PLAYING

        self.check_boards_setposition()

        self.current_errors = 0
        self.current_hints = 0
        self.ini_time = 0.0

        self.show_labels()
        self.play_next_move()

    def get_help(self):
        self.current_hints += 1
        self.all_hints += 1
        self.show_labels()
        move_next: Move.Move = self.game_obj.move(len(self.game))
        self.board.show_arrow_mov(move_next.from_sq, move_next.to_sq, "mt", opacity=0.80)
        fenm2 = move_next.position_before.fenm2()
        st_pv = self.reg.dic_fenm2[fenm2]
        if len(st_pv) > 1:
            pv_main = move_next.movimiento()
            for pv in st_pv:
                if pv != pv_main:
                    self.board.show_arrow_mov(pv[:2], pv[2:4], "tr", opacity=0.80)

    def show_labels(self):
        li = [
            "%s: %d/%d" % (_("Line"), self.pos_line + 1, len(self.reg.lines)),
            "%s: %d" % (_("Errors"), self.current_errors),
            "%s: %d" % (_("Hints"), self.current_hints)
        ]
        self.set_label1("\n".join(li))

    def close_time(self):
        if not self.ini_time:
            return
        tm = time.time() - self.ini_time
        self.time_used += tm
        self.ini_time = 0.0

    def game_finished(self):
        self.close_time()
        self.state = ST_ENDGAME
        li = [_("Line completed")]
        completed = self.current_errors == 0 and self.current_hints == 0
        if not completed:
            if self.current_errors:
                li.append("%s: %d" % (_("Errors"), self.current_errors))
            if self.current_hints:
                li.append("%s: %d" % (_("Hints"), self.current_hints))
        mensaje = "\n".join(li)
        self.message_on_pgn(mensaje)

        if completed:
            self.pos_line += 1

        finished = self.pos_line == len(self.reg.lines)

        li_toolbar = [TB_CLOSE, TB_NEXT, TB_CONFIG, TB_UTILITIES]
        if finished:
            li_toolbar.remove(TB_NEXT)
        self.main_window.pon_toolbar(li_toolbar)

        self.pgn_refresh(self.is_human_side_white)

        self.state = ST_ENDGAME

        if finished:
            QTUtil2.message(
                self.main_window,
                "%s\n\n%s"
                % (_("Congratulations, goal achieved"), _("Next time you will start from the first position")),
            )

        if finished:
            self.end_game()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_NEXT:
            self.reinicio()

        elif key == TB_ADVICE:
            self.get_help()

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def final_x(self):
        return self.end_game()

    def end_game(self):
        self.close_time()
        self.reg.set_last_training(self.pos_line, self.all_errors, self.all_hints, self.time_used)
        self.dbli_books_train[self.train_pos] = self.reg
        self.dbli_books_train.close()
        self.procesador.start()
        return False

    def reiniciar(self):
        self.close_time()
        self.main_window.activaInformacionPGN(False)
        self.reinicio()

    def play_next_move(self):
        self.show_labels()
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        play_oponent = is_white == self.is_engine_side_white

        num_moves = len(self.game)
        if num_moves == len(self.game_obj):
            self.game_finished()
            return

        if play_oponent:
            self.disable_all()

            self.rm_rival = EngineResponse.EngineResponse("Opening", self.is_engine_side_white)
            move: Move.Move = self.game_obj.move(num_moves)
            self.rival_has_moved(move)
            self.play_next_move()

        else:
            self.activate_side(is_white)
            self.human_is_playing = True
            self.ini_time = time.time()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        move_player: Move.Move = self.check_human_move(from_sq, to_sq, promotion)
        if not move_player:
            self.beep_error()
            return False
        pv_player = move_player.movimiento().lower()
        move_obj: Move.Move = self.game_obj.move(len(self.game))
        pv_obj = move_obj.movimiento()

        if pv_player != pv_obj:
            fenm2 = move_player.position_before.fenm2()
            if pv_player in self.reg.dic_fenm2[fenm2]:
                mens = _("You have selected a correct move, but this line uses another one.")
                background = "#C3D6E8"
            else:
                self.beep_error()
                self.current_errors += 1
                self.all_errors += 1
                mens = "%s: %d" % (_("Error"), self.current_errors)
                background = "#FF9B00"

            QTUtil2.temporary_message(self.main_window, mens, 1.5, physical_pos=TOP_RIGHT, background=background)
            self.show_labels()
            self.continue_human()
            return False

        self.close_time()
        self.move_the_pieces(move_player.liMovs)

        self.add_move(move_player, True)
        self.play_next_move()
        return True

    def rival_has_moved(self, move: Move.Move):
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        return True

    def add_move(self, move: Move.Move, is_player: bool):
        self.game.add_move(move)

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player)

        self.check_boards_setposition()

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()
