import os
import random

import Code
from Code import Util
from Code.Base import Game, Position
from Code.Base.Constantes import RESULT_DRAW, RESULT_WIN_BLACK, RESULT_WIN_WHITE, WHITE, BLACK, BOOK_RANDOM_PROPORTIONAL
from Code.Engines import Engines
from Code.SQL import UtilSQL


class EngineTournament(Engines.Engine):
    def __init__(self):
        Engines.Engine.__init__(self, "", "", "", "", "")

        self.huella = None

        self.depth = 0
        self.time = 0

        self.elo_current = None

        self.book = "-"  # "*":por defecto "-":el propio del engine otro:path to book polyglot
        self.bookRR = BOOK_RANDOM_PROPORTIONAL

        # listas de huellas
        self.win_white = []
        self.win_black = []
        self.lost_white = []
        self.lost_black = []
        self.draw_white = []
        self.draw_black = []

    def pon_huella(self, torneo):
        st_huellas = set()
        for eng in torneo.db_engines:
            st_huellas.add(eng.huella)
        while True:
            self.huella = Util.huella()
            if not (self.huella in st_huellas):
                return

    def copiar(self, torneo):
        otro = EngineTournament()
        otro.restore(self.save())
        otro.pon_huella(torneo)
        otro.key += "-1"
        otro.alias = otro.key
        otro.win_white = []
        otro.win_black = []
        otro.lost_white = []
        otro.lost_black = []
        otro.draw_white = []
        otro.draw_black = []

        return otro

    def book(self, valor=None):
        if valor is not None:
            self.book = valor
        return self.book

    def bookRR(self, valor=None):
        if valor is not None:
            self.bookRR = valor
        return self.bookRR

    def set_depth(self, valor=None):
        if valor is not None:
            self.depth = valor
        return self.depth

    def set_time(self, valor=None):
        if valor is not None:
            self.time = valor
        return self.time

    def read_exist_engine(self, resp):
        cm = Code.configuration.buscaRival(resp)
        self.restore(cm.save())

    def add_result(self, game):
        result = game.result
        if self.huella == game.hwhite:
            side = WHITE
            other_huella = game.hblack
        else:
            side = BLACK
            other_huella = game.hwhite

        if result == RESULT_WIN_WHITE:
            if side == WHITE:
                self.win_white.append(other_huella)
            else:
                self.lost_black.append(other_huella)
        elif result == RESULT_WIN_BLACK:
            if side == WHITE:
                self.lost_white.append(other_huella)
            else:
                self.win_black.append(other_huella)
        elif result == RESULT_DRAW:
            if side == WHITE:
                self.draw_white.append(other_huella)
            else:
                self.draw_black.append(other_huella)

    def remove_result(self, game):
        result = game.result
        if self.huella == game.hwhite:
            side = WHITE
            other_huella = game.hblack
        else:
            side = BLACK
            other_huella = game.hwhite

        def quita(lis, huella):
            if huella in lis:
                del lis[lis.index(huella)]

        if result == RESULT_WIN_WHITE:
            if side == WHITE:
                quita(self.win_white, other_huella)
            else:
                quita(self.lost_black, other_huella)
        elif result == RESULT_WIN_BLACK:
            if side == WHITE:
                quita(self.lost_white, other_huella)
            else:
                quita(self.win_black, other_huella)
        elif result == RESULT_DRAW:
            if side == WHITE:
                quita(self.draw_white, other_huella)
            else:
                quita(self.draw_black, other_huella)


class GameTournament(object):
    def __init__(self):
        self.id_game = Util.huella()
        self.hwhite = None  # la huella de un engine
        self.hblack = None  # la huella de un engine
        self.game_save = None  # game salvada en formato pk con save
        self.minutos = None
        self.seconds_per_move = None
        self.result = None
        self.date = None
        self.termination = None
        self.elo_white = 0
        self.elo_black = 0
        self.worker = None

    def etiTiempo(self):
        if self.minutos:
            wdec = lambda x: ("%f" % x).rstrip("0").rstrip(".")
            if self.seconds_per_move:
                return "%s+%s" % (wdec(self.minutos * 60), wdec(self.seconds_per_move))
            else:
                return wdec(self.minutos * 60)
        else:
            return ""

    def game(self):
        if self.game_save:
            game = Game.Game()
            game.restore(self.game_save)
            return game

    def save_game(self, game):
        self.game_save = game.save(True)
        if game.resultado():
            self.result = game.resultado()


class Tournament:
    def __init__(self, file):
        self.file = file
        self.reopen_games()

    def reopen_games(self):
        self.db_engines = UtilSQL.DictObjSQL(self.file, EngineTournament, tabla="engines")
        self.db_games_queued = UtilSQL.ListObjSQL(self.file, GameTournament, tabla="games_queued")
        self.db_games_finished = UtilSQL.ListObjSQL(self.file, GameTournament, tabla="games_finished")

    def name(self):
        return os.path.basename(self.file)[:-4]

    def close(self):
        self.db_engines.close()
        self.db_games_finished.close()
        self.db_games_queued.close()

    def config(self, key, value, default):
        db_config = UtilSQL.DictSQL(self.file, tabla="config", max_cache=0)
        if value is None:
            value = db_config.get(key, default)
        else:
            db_config[key] = value
        db_config.close()
        return value

    def set_last_change(self):
        self.config("last_change", Util.today(), None)

    def get_last_change(self):
        return self.config("last_change", None, None)

    def fen(self, valor=None):
        v = self.config("fen", valor, "")
        if isinstance(v, Position.Position):
            v = v.fen()
        return v

    def norman(self, valor=None):
        return self.config("norman", valor, False)

    def fen_norman(self):
        fen = self.fen()
        if fen:
            return fen
        norman = self.norman()
        if norman:
            with open(Code.path_resource("IntFiles", "40H-Openings.epd")) as f:
                lista = [linea for linea in f.read().split("\n") if linea.strip()]
                fen = random.choice(lista)
            return fen + " 0 1"
        return ""

    def resign(self, valor=None):
        return self.config("resign", valor, 350)

    def slow_pieces(self, valor=None):
        return self.config("slow_pieces", valor, False)

    def draw_min_ply(self, valor=None):
        return self.config("drawminply", valor, 50)

    def draw_range(self, valor=None):
        return self.config("drawrange", valor, 10)

    def adjudicator_active(self, valor=None):
        return self.config("adjudicator_active", valor, False)

    def adjudicator(self, valor=None):
        return self.config("adjudicator", valor, Code.configuration.tutor_default)

    def adjudicator_time(self, valor=None):
        return self.config("adjudicator_time", valor, 5.0)

    def last_folder_engines(self, valor=None):
        return self.config("last_folder_engines", valor, None)

    def book(self, valor=None):
        return self.config("book", valor, "")

    def book_depth(self, valor=None):
        return self.config("bookdepth", valor, 0)

    def num_engines(self):
        return len(self.db_engines)

    def save_engine(self, me):
        self.db_engines[me.huella] = me

    def engine(self, pos):
        huella = list(self.db_engines.keys())[pos]
        return self.db_engines[huella]

    def list_engines(self):
        return [engine for engine in self.db_engines]

    def copy_engine(self, me):
        otro = me.copiar(self)
        self.save_engine(otro)

    def remove_engines(self, lista=None):
        li_rem_gm = []
        if lista is None:
            lista = range(self.num_engines())
        lista.sort(reverse=True)
        for pos in lista:
            en = self.engine(pos)
            huella = en.huella
            for n, gm in enumerate(self.db_games_queued):
                if gm.hwhite == huella or gm.hblack == huella:
                    li_rem_gm.append(n)
            for n, gm in enumerate(self.db_games_finished):
                if gm.hwhite == huella or gm.hblack == huella:
                    li_rem_gm.append(n)

        if li_rem_gm:
            self.remove_games_queued(li_rem_gm)
            self.remove_games_finished(li_rem_gm)

        for pos in lista:
            en = self.engine(pos)
            del self.db_engines[en.huella]

    def search_hengine(self, huella):
        return self.db_engines.get(huella)

    def dbs_reread(self):
        self.db_games_finished.close()
        self.db_games_queued.close()
        self.db_engines.close()
        self.reopen_games()

    def num_games_queued(self):
        return len(self.db_games_queued)

    def num_games_finished(self):
        return len(self.db_games_finished)

    def game_queued(self, pos):
        return self.db_games_queued[pos]

    def get_game_queued(self, file_worker):
        self.db_games_queued.refresh()
        num_queued = self.num_games_queued()
        if num_queued > 0:
            li = list(range(num_queued))
            random.shuffle(li)
            for pos in li:
                game = self.game_queued(pos)
                if game.worker is None:
                    if game.minutos is None:
                        continue
                    game.worker = file_worker
                    self.db_games_queued[pos] = game
                    return game
                elif Util.same_path(file_worker, game.worker):
                    return game
                else:
                    if Util.remove_file(game.worker):
                        game.worker = file_worker
                        self.db_games_queued[pos] = game
                        return game
        return None

    def game_finished(self, pos):
        return self.db_games_finished[pos]

    def save_game_finished(self, pos, game):
        self.db_games_finished[pos].save_game(game)

    def remove_games_queued(self, lista=None):
        if lista is None:
            lista = range(self.num_games_queued())
        lista = list(set(lista))
        lista.sort(reverse=True)
        for pos in lista:
            del self.db_games_queued[pos]

    def game_done(self, game):
        for pos in range(self.num_games_queued()):
            if game.id_game == self.game_queued(pos).id_game:
                # Se crea engame_finished
                self.db_games_finished.append(game)
                # Se borra de game_queued
                del self.db_games_queued[pos]
                # Se añade a los motores afectados el resultado
                eng_white = self.db_engines.get(game.hwhite)
                eng_black = self.db_engines.get(game.hblack)
                eng_white.add_result(game)
                eng_black.add_result(game)
                self.save_engine(eng_white)  # reemplaza
                self.save_engine(eng_black)  # reemplaza

                # Escribir games cambiados en el control para la gui
                self.set_last_change()
                return

    def remove_games_finished(self, lista=None):
        if lista is None:
            lista = range(self.num_games_queued())
        lista = list(set(lista))
        lista.sort(reverse=True)
        for pos in lista:
            game = self.game_finished(pos)
            if game is not None:
                eng_white = self.db_engines.get(game.hwhite)
                eng_black = self.db_engines.get(game.hblack)
                eng_white.remove_result(game)
                eng_black.remove_result(game)
                self.save_engine(eng_white)  # reemplaza
                self.save_engine(eng_black)  # reemplaza

            del self.db_games_finished[pos]

    def new_game(self, hwhite, hblack, minutos, seconds_move):
        gm = GameTournament()
        gm.hwhite = hwhite
        gm.hblack = hblack
        gm.minutos = minutos
        gm.seconds_per_move = seconds_move
        self.db_games_queued.append(gm, with_commit=False)

    def new_game_commit(self):
        self.db_games_queued.commit()

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()
