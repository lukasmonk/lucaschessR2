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
    TB_HELP,
    TB_UTILITIES,
    SELECTED_BY_PLAYER
)
from Code.Books import WBooks
from Code.Engines import EngineResponse


class ManagerTrainBooks(Manager.Manager):
    def start(self, book_player, player_highest, book_rival, resp_rival, is_white, show_menu):
        self.type_play = GT_BOOK

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

        self.set_toolbar((TB_CLOSE, TB_REINIT, TB_TAKEBACK, TB_HELP, TB_CONFIG, TB_UTILITIES))
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

        self.siguienteJugada()

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

        elif clave == TB_HELP:
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

    def siguienteJugada(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.set_side_indicator(is_white)
        self.refresh()

        fen = self.game.last_position.fen()

        siRival = is_white == self.is_book_side_white
        book = self.book_rival if siRival else self.book_player
        self.list_moves = book.get_list_moves(fen)
        if not self.list_moves:
            self.put_result()
            return

        if siRival:
            self.disable_all()

            nli = len(self.list_moves)
            if nli > 1:
                resp = self.select_rival_move()
            else:
                resp = self.list_moves[0][0], self.list_moves[0][1], self.list_moves[0][2]
            xfrom, xto, promotion = resp

            self.book_move = EngineResponse.EngineResponse("Apertura", self.is_book_side_white)
            self.book_move.from_sq = xfrom
            self.book_move.to_sq = xto
            self.book_move.promotion = promotion

            self.rival_has_moved(self.book_move)
            self.siguienteJugada()

        else:

            self.human_is_playing = True
            self.activate_side(is_white)

    def select_rival_move(self):
        select = self.resp_rival

        if select == SELECTED_BY_PLAYER:
            resp = WBooks.eligeJugadaBooks(self.main_window, self.list_moves, self.game.last_position.is_white)
        elif select == BOOK_BEST_MOVE:
            resp = self.list_moves[0][0], self.list_moves[0][1], self.list_moves[0][2]
            nmax = self.list_moves[0][4]
            for xfrom, xto, promotion, pgn, peso in self.list_moves:
                if peso > nmax:
                    resp = xfrom, xto, promotion
                    nmax = peso
        elif select == BOOK_RANDOM_UNIFORM:
            pos = random.randint(0, len(self.list_moves) - 1)
            resp = self.list_moves[pos][0], self.list_moves[pos][1], self.list_moves[pos][2]
        else:
            li = [int(x[4] * 100000) for x in self.list_moves]
            t = sum(li)
            num = random.randint(1, t)
            pos = 0
            t = 0
            for n, x in enumerate(li):
                t += x
                if num <= t:
                    pos = n
                    break
            resp = self.list_moves[pos][0], self.list_moves[pos][1], self.list_moves[pos][2]

        return resp

    def play_human(self, xfrom, xto, promotion=None):
        jg = self.check_human_move(xfrom, xto, promotion)
        if not jg:
            return False

        found = False
        actpeso = 0
        for jdesde, jhasta, jpromotion, jpgn, peso in self.list_moves:
            if xfrom == jdesde and xto == jhasta and jg.promotion == jpromotion:
                found = True
                actpeso = peso
                break

        if found and self.player_highest:  # si el jugador busca elegir el maximo
            maxpeso = 0.0
            for jdesde, jhasta, jpromotion, jpgn, peso in self.list_moves:
                if peso > maxpeso:
                    maxpeso = peso
            if actpeso < maxpeso:
                found = False

        if not found:
            self.board.set_position(self.game.last_position)

            main = self.list_moves[0][4]
            saux = False
            paux = 0

            for n, jug in enumerate(self.list_moves):
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
                resp = WBooks.eligeJugadaBooks(
                    self.main_window, self.list_moves, self.is_human_side_white, siSelectSiempre=False
                )
                self.board.remove_arrows()
            else:
                resp = None
            if resp is None:
                self.sumar_aciertos = False
                self.sigueHumano()
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
        self.siguienteJugada()
        return True

    def get_help(self):
        if self.human_is_playing:
            self.paraHumano()
        else:
            return
        self.board.set_position(self.game.last_position)

        main = self.list_moves[0][4]
        saux = False
        paux = 0

        for n, jug in enumerate(self.list_moves):
            opacity = p = jug[4]
            simain = p == main
            if not simain:
                if not saux:
                    paux = p
                    saux = True
                opacity = 1.0 if p == paux else max(p, 0.25)
            self.board.creaFlechaMulti(jug[0] + jug[1], siMain=simain, opacity=opacity)

        resp = WBooks.eligeJugadaBooks(
            self.main_window, self.list_moves, self.is_human_side_white, siSelectSiempre=False
        )
        self.board.remove_arrows()
        if resp is None:
            self.sumar_aciertos = False
            self.sigueHumano()
            return

        xfrom, xto, promotion = resp
        ok, mens, jg = Move.get_game_move(self.game, self.game.last_position, xfrom, xto, promotion)
        self.movimientos += 1

        self.set_label3("<b>%s</b>" % self.txt_matches())

        self.move_the_pieces(jg.liMovs)

        self.add_move(jg, True)
        self.error = ""
        self.sumar_aciertos = True
        self.siguienteJugada()

    def add_move(self, jg, siNuestra):

        # Para facilitar el salto a variantes
        jg.aciertos = self.aciertos
        jg.movimientos = self.movimientos
        jg.numpos = len(self.game)

        self.ponVariantes(jg)
        # Preguntamos al motor si hay movimiento
        if self.is_finished():
            jg.siJaqueMate = jg.siJaque
            jg.siAhogado = not jg.siJaque

        self.game.add_move(jg)

        self.put_arrow_sc(jg.from_sq, jg.to_sq)
        self.beepExtendido(siNuestra)

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
            self.game.anulaUltimoMovimiento(self.is_human_side_white)
            self.goto_end()
            self.refresh()
            self.siguienteJugada()

    def ponVariantes(self, jg):
        xfrom = jg.from_sq
        xto = jg.to_sq
        promotion = jg.promotion
        if promotion is None:
            promotion = ""

        comentario = ""

        linea = "-" * 24 + "\n"
        for jdesde, jhasta, jpromotion, jpgn, peso in self.list_moves:
            siLineas = xfrom == jdesde and xto == jhasta and promotion == jpromotion
            if siLineas:
                comentario += linea
            comentario += jpgn + "\n"
            if siLineas:
                comentario += linea

        jg.set_comment(comentario)

    def rival_has_moved(self, book_response):
        xfrom = book_response.from_sq
        xto = book_response.to_sq

        promotion = book_response.promotion

        ok, mens, jg = Move.get_game_move(self.game, self.game.last_position, xfrom, xto, promotion)
        if ok:
            self.ponVariantes(jg)

            self.add_move(jg, False)
            self.move_the_pieces(jg.liMovs, True)

            self.error = ""

            return True
        else:
            self.error = mens
            return False

    def txt_matches(self):
        if self.movimientos:
            self.game.set_tag("Score", "%d/%d" % (self.aciertos, self.movimientos))
            return "%s : %d/%d (%0.2f%%)" % (
                _("Score"),
                self.aciertos,
                self.movimientos,
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
