import random

import Code
from Code import Manager
from Code.Base import Move
from Code.Base.Constantes import BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM
from Code.Base.Constantes import (
    ST_ENDGAME,
    ST_PLAYING,
    GT_BOOK,
    TB_CLOSE,
    TB_REINIT,
    TB_TAKEBACK,
    TB_CONFIG,
    TB_ADVICE,
    TB_UTILITIES,
    SELECTED_BY_PLAYER
)
from Code.Books import WBooks
from Code.Engines import EngineResponse


class ManagerTrainBooks(Manager.Manager):
    movimientos: int
    book_player = None
    book_rival = None
    player_highest: bool
    resp_rival = None
    show_menu: bool
    aciertos: int
    sumar_aciertos: bool
    li_reinit = None
    is_human_side_white: bool
    is_book_side_white: bool
    
    def start(self, book_player, player_highest, book_rival, resp_rival, is_white, show_menu):
        self.game_type = GT_BOOK

        self.hints = 9999  # Para que analice sin problemas

        self.book_player = book_player
        self.book_player.polyglot()
        self.player_highest = player_highest
        self.book_rival = book_rival
        self.book_rival.polyglot()
        self.resp_rival = resp_rival
        self.show_menu = show_menu

        self.aciertos = 0
        self.movimientos = 0
        self.sumar_aciertos = True

        self.li_reinit = book_player, player_highest, book_rival, resp_rival, is_white, show_menu

        self.is_human_side_white = is_white
        self.is_book_side_white = not is_white

        self.set_toolbar((TB_CLOSE, TB_REINIT, TB_TAKEBACK, TB_ADVICE, TB_CONFIG, TB_UTILITIES))
        self.main_window.active_game(True, False)
        self.set_dispatcher(self.play_human)
        self.set_position(self.game.last_position)
        self.show_side_indicator(True)
        self.remove_hints(siQuitarAtras=False)
        self.put_pieces_bottom(is_white)
        self.set_label1("%s: %s" % (_("Player"), self.book_player.name))
        self.set_label2("%s: %s" % (_("Opponent"), self.book_rival.name))
        self.pgn_refresh(True)
        self.show_info_extra()

        self.state = ST_PLAYING

        self.remove_info(is_activatable=True)

        w, b = self.book_player.name, self.book_rival.name
        if not is_white:
            w, b = b, w
        self.game.set_tag("White", w)
        self.game.set_tag("Black", b)

        self.play_next_move()

    def run_action(self, clave):
        if clave == TB_CLOSE:
            self.end_game()

        elif clave == TB_REINIT:
            self.reiniciar()

        elif clave == TB_TAKEBACK:
            self.takeback()

        elif clave == TB_CONFIG:
            self.configurar(with_sounds=True)

        elif clave == TB_UTILITIES:
            self.utilities()

        elif clave == TB_ADVICE:
            self.get_help()

        else:
            Manager.Manager.rutinaAccionDef(self, clave)

    def final_x(self):
        return self.end_game()

    def end_game(self):
        self.procesador.start()
        return False

    def reiniciar(self):
        self.game.reset()
        book_player, player_highest, book_rival, resp_rival, is_white, show_menu = self.li_reinit
        self.main_window.activaInformacionPGN(False)
        self.start(book_player, player_highest, book_rival, resp_rival, is_white, show_menu)

    def get_list_moves(self, is_rival):
        book = self.book_rival if is_rival else self.book_player
        fen = self.game.last_position.fen()
        return book.get_list_moves(fen)

    def play_next_move(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white
        play_the_rival = is_white == self.is_book_side_white

        self.set_side_indicator(is_white)
        self.refresh()

        list_moves = self.get_list_moves(play_the_rival)
        if not list_moves:
            self.put_result()
            return

        if play_the_rival:
            self.disable_all()

            nli = len(list_moves)
            if nli > 1:
                resp = self.select_rival_move(list_moves)
            else:
                resp = list_moves[0][0], list_moves[0][1], list_moves[0][2]
            xfrom, xto, promotion = resp

            book_move = EngineResponse.EngineResponse("Apertura", self.is_book_side_white)
            book_move.from_sq = xfrom
            book_move.to_sq = xto
            book_move.promotion = promotion

            self.rival_has_moved(book_move)
            self.play_next_move()

        else:
            self.human_is_playing = True
            self.activate_side(is_white)

    def select_rival_move(self, list_moves):
        select = self.resp_rival

        if select == SELECTED_BY_PLAYER:
            resp = WBooks.select_move_books(self.main_window, list_moves, self.game.last_position.is_white, True)
        elif select == BOOK_BEST_MOVE:
            resp = list_moves[0][0], list_moves[0][1], list_moves[0][2]
            nmax = list_moves[0][4]
            for xfrom, xto, promotion, pgn, peso in list_moves:
                if peso > nmax:
                    resp = xfrom, xto, promotion
                    nmax = peso
        elif select == BOOK_RANDOM_UNIFORM:
            pos = random.randint(0, len(list_moves) - 1)
            resp = list_moves[pos][0], list_moves[pos][1], list_moves[pos][2]
        else:
            li = [int(x[4] * 100000) for x in list_moves]
            t = sum(li)
            num = random.randint(1, t)
            pos = 0
            t = 0
            for n, x in enumerate(li):
                t += x
                if num <= t:
                    pos = n
                    break
            resp = list_moves[pos][0], list_moves[pos][1], list_moves[pos][2]

        return resp

    def play_human(self, xfrom, xto, promotion=None):
        jg = self.check_human_move(xfrom, xto, promotion)
        if not jg:
            return False

        found = False
        actpeso = 0
        list_moves = self.get_list_moves(False)
        for jdesde, jhasta, jpromotion, jpgn, peso in list_moves:
            if xfrom == jdesde and xto == jhasta and jg.promotion == jpromotion:
                found = True
                actpeso = peso
                break

        if found and self.player_highest:  # si el jugador busca elegir el maximo
            maxpeso = 0.0
            for jdesde, jhasta, jpromotion, jpgn, peso in list_moves:
                if peso > maxpeso:
                    maxpeso = peso
            if actpeso < maxpeso:
                found = False

        if not found:
            self.board.set_position(self.game.last_position)

            main = list_moves[0][4]
            saux = False
            paux = 0

            for n, jug in enumerate(list_moves):
                opacity = p = jug[4]
                simain = p == main
                if not simain:
                    if not saux:
                        paux = p
                        saux = True
                    opacity = 1.0 if p == paux else max(p, 0.25)
                self.board.creaFlechaMulti(jug[0] + jug[1], siMain=simain, opacity=opacity)
                if simain and Code.eboard:
                    self.board.eboard_arrow(jug[0], jug[1], jug[2])

            if self.show_menu:
                resp = WBooks.select_move_books(self.main_window, list_moves, self.is_human_side_white, False)
                self.board.remove_arrows()
            else:
                resp = None
            if resp is None:
                self.sumar_aciertos = False
                self.continue_human()
                return False

            xfrom, xto, promotion = resp
            ok, mens, jg = Move.get_game_move(self.game, self.game.last_position, xfrom, xto, promotion)
        else:
            if self.sumar_aciertos:
                self.aciertos += actpeso
        self.movimientos += 1

        self.set_label3("<b>%s</b>" % self.txt_matches())

        self.move_the_pieces(jg.liMovs)

        self.add_move(jg, True)
        self.error = ""
        self.sumar_aciertos = True
        self.play_next_move()
        return True

    def get_help(self):
        if not self.human_is_playing:
            return
        list_moves = self.get_list_moves(False)
        main = list_moves[0][4]
        saux = False
        paux = 0

        for n, jug in enumerate(list_moves):
            opacity = p = jug[4]
            simain = p == main
            if not simain:
                if not saux:
                    paux = p
                    saux = True
                opacity = 1.0 if p == paux else max(p, 0.25)
            self.board.creaFlechaMulti(jug[0] + jug[1], siMain=simain, opacity=opacity)

        self.sumar_aciertos = False

    def add_move(self, jg, is_player_move):

        # Para facilitar el salto a variantes
        jg.aciertos = self.aciertos
        jg.movimientos = self.movimientos
        jg.numpos = len(self.game)

        self.set_variations(is_player_move, jg)
        # Preguntamos al motor si hay movimiento
        if self.is_finished():
            jg.siJaqueMate = jg.siJaque
            jg.siAhogado = not jg.siJaque

        self.game.add_move(jg)

        self.put_arrow_sc(jg.from_sq, jg.to_sq)
        self.beep_extended(is_player_move)

        self.check_boards_setposition()

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

    def takeback(self):
        if len(self.game):
            self.state = ST_PLAYING
            self.movimientos -= 1
            if self.movimientos < 0:
                self.movimientos = 0
            self.aciertos -= 1
            if self.aciertos < 0:
                self.aciertos = 0
            self.game.remove_last_move(self.is_human_side_white)
            self.goto_end()
            self.refresh()
            self.play_next_move()

    def set_variations(self, is_human, jg):
        xfrom = jg.from_sq
        xto = jg.to_sq
        promotion = jg.promotion
        if promotion is None:
            promotion = ""

        comentario = ""

        linea = "-" * 24 + "\n"
        list_moves = self.get_list_moves(not is_human)
        for jdesde, jhasta, jpromotion, jpgn, peso in list_moves:
            si_lineas = xfrom == jdesde and xto == jhasta and promotion == jpromotion
            if si_lineas:
                comentario += linea
            comentario += jpgn + "\n"
            if si_lineas:
                comentario += linea

        jg.set_comment(comentario)

    def rival_has_moved(self, book_response):
        xfrom = book_response.from_sq
        xto = book_response.to_sq

        promotion = book_response.promotion

        ok, mens, jg = Move.get_game_move(self.game, self.game.last_position, xfrom, xto, promotion)
        if ok:
            self.set_variations(False, jg)

            self.add_move(jg, False)
            self.move_the_pieces(jg.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def txt_matches(self):
        if self.movimientos:
            plant = "%d/%d" if self.player_highest else "%0.1f/%d"
            score = plant % (self.aciertos, self.movimientos)
            self.game.set_tag("Score", score)
            return "%s : %s (%0.2f%%)" % (
                _("Score"),
                score,
                100.0 * self.aciertos / self.movimientos,
            )
        else:
            return ""

    def put_result(self):
        self.state = ST_ENDGAME

        self.board.disable_all()

        txt = self.txt_matches()

        mensaje = "%s\n%s\n" % (_("Line completed"), txt)
        self.message_on_pgn(mensaje, delayed=True)
