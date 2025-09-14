import time

from Code import Manager
from Code.Base import Game
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    TB_CLOSE,
    TB_CONFIG,
    TB_NEXT,
    TB_RESIGN,
    TB_UTILITIES,
    GT_SINGULAR_MOVES,
)


class ManagerSingularM(Manager.Manager):
    def start(self, singularMoves):
        self.singularMoves = singularMoves

        self.pos_bloque = 0
        self.game_type = GT_SINGULAR_MOVES

        self.is_rival_thinking = False

        self.is_competitive = True

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.main_window.set_activate_tutor(False)
        self.remove_hints(True)

        self.ayudas_iniciales = 0

        self.main_window.active_game(True, True)
        self.main_window.remove_hints(True)
        self.set_dispatcher(self.player_has_moved)

        self.pgn_refresh(True)

        self.play_next_move()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.end_game()

        elif key == TB_RESIGN:
            self.resign()

        elif key == TB_NEXT:
            self.play_next_move()

        elif key == TB_UTILITIES:
            self.utilities()

        elif key == TB_CONFIG:
            self.configurar()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Manager.Manager.rutinaAccionDef(self, key)

    def end_game(self):
        self.procesador.start()
        self.procesador.strenght101()

    def final_x(self):
        return self.end_game()

    def play_next_move(self):
        self.set_toolbar([TB_CLOSE, TB_RESIGN])

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.is_competitive = True

        self.linea_bloque = self.singularMoves.linea_bloque(self.pos_bloque)

        is_white = " w " in self.linea_bloque.fen
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.set_activate_tutor(False)
        self.remove_hints(True)
        self.game = Game.Game(fen=self.linea_bloque.fen)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.put_pieces_bottom(is_white)
        self.set_side_indicator(is_white)
        self.main_window.change_player_labels("%d/10" % (self.pos_bloque + 1,), _("Complete"))

        self.main_window.set_clock_white("", None)
        self.main_window.set_clock_black(self.singularMoves.rotulo_media(), None)

        self.refresh()

        self.human_is_playing = True
        self.activate_side(is_white)

        self.main_window.start_clock(self.set_clock, transicion=1000)
        self.time_inicio = time.time()
        self.set_clock()

    def calc_puntuacion(self, vtime):
        if vtime <= 3.0:
            return 100.00
        else:
            max_time = self.linea_bloque.max_time
            if vtime > max_time:
                return 0.0
            return (max_time - vtime) * 100.0 / max_time

    def set_clock(self):
        p = self.calc_puntuacion(time.time() - self.time_inicio)
        self.main_window.set_clock_white("%0.2f" % p, None)

    def resign(self):
        self.add_move(None)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        jgSel = self.check_human_move(from_sq, to_sq, promotion)
        if not jgSel:
            return False
        self.add_move(jgSel)

    def add_move(self, jgSel):
        self.main_window.stop_clock()
        tm = time.time() - self.time_inicio
        self.linea_bloque.time = tm
        score = self.calc_puntuacion(tm)

        resp = jgSel.movimiento() if jgSel else "a1a1"
        bm = self.linea_bloque.bm
        ok = bm == resp
        self.linea_bloque.score = score if ok else 0
        self.main_window.set_clock_white("%0.2f" % self.linea_bloque.score, None)

        self.singularMoves.add_bloque_sol(self.linea_bloque)
        self.main_window.set_clock_black(self.singularMoves.rotulo_media(), None)

        if jgSel:
            self.move_the_pieces(jgSel.liMovs)

            self.game.add_move(jgSel)
            self.check_boards_setposition()

            self.put_arrow_sc(jgSel.from_sq, jgSel.to_sq)
            if not ok:
                self.board.creaFlechaTmp(bm[:2], bm[2:], False)
            self.beep_extended(True)

        else:
            self.put_arrow_sc(bm[:2], bm[2:])
            self.check_boards_setposition()

        self.pgn_refresh(self.game.last_position.is_white)

        self.pos_bloque += 1
        li = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]
        if self.pos_bloque < 10:
            li.append(TB_NEXT)
        else:
            self.singularMoves.graba()
        self.set_toolbar(li)

        self.state = ST_ENDGAME

        self.refresh()

    def current_pgn(self):
        resp = '[Event "%s"]\n' % _("Challenge 101")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgn_base()

        return resp
