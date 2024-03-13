import random

import Code
from Code.Base import Game
from Code.Books import Polyglot


class EtiOpening:
    def __init__(self, name, eco, a1h8, pgn):
        self.name = name
        self.eco = eco
        self.a1h8 = a1h8.split(" ")
        self.pgn = pgn
        self.li_hijos = []

    def hijo(self, ea):
        self.li_hijos.append(ea)


class OpeningPol:
    def __init__(self, max_nivel, elo=None):
        if elo:
            si_ptz = elo < 1700
        else:
            si_ptz = 1 <= max_nivel <= 2
        self.file = Code.tbookPTZ if si_ptz else Code.tbook
        self.book = Polyglot.Polyglot()
        self.activa = True
        self.max_level = max_nivel * 2
        self.nivel_actual = 0
        self.si_obligatoria = False

    def lee_random(self, fen):
        li = self.book.lista(self.file, fen)
        if not li:
            return None
        li_num = []
        for nentry, entry in enumerate(li):
            li_num.extend([nentry] * (entry.weight + 1))  # Always entry.weight+1> 0
        return li[random.choice(li_num)]

    def is_active(self, fen):
        x = self.lee_random(fen)
        return x is not None

    def run_engine(self, fen):
        self.nivel_actual += 1
        if self.nivel_actual > self.max_level:
            self.activa = False
            return False, None, None, None

        if not self.activa:
            return False, None, None, None

        entry = self.lee_random(fen)
        if entry is None:
            self.activa = False
            return False, None, None, None

        pv = entry.pv()

        return True, pv[:2], pv[2:4], pv[4:]

    def check_human(self, fen, from_sq, to_sq):
        if not self.activa:
            return False

        li = self.book.lista(self.file, fen)
        if not li:
            return False

        for entry in li:
            pv = entry.pv()
            if pv[:2] == from_sq and pv[2:4] == to_sq:
                return True
        return False


class JuegaOpening:
    def __init__(self, a1h8):
        p = Game.Game()
        p.read_pv(a1h8)
        self.dicFEN = {}
        for move in p.li_moves:
            self.dicFEN[move.position_before.fen()] = move
        self.activa = True

    def run_engine(self, fen):
        try:
            move = self.dicFEN[fen]
            return True, move.from_sq, move.to_sq, move.promotion
        except:
            self.activa = False
            return False, None, None, None

    def check_human(self, fen, from_sq, to_sq):
        if fen in self.dicFEN:
            move = self.dicFEN[fen]
            return from_sq == move.from_sq and to_sq == move.to_sq
        else:
            self.activa = False
            return False

    def from_to_active(self, fen):
        if fen in self.dicFEN:
            move = self.dicFEN[fen]
            return move.from_sq, move.to_sq, move.promotion
        self.activa = False
        return None, None, None
