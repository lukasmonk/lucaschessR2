# This code is a translation to python from pg_key.c and pg_show.c released in the public domain by Michel Van den Bergh
# http://alpha.uhasselt.be/Research/Algebra/Toga

import os
import sys

import FasterCode

from Code.Base.Constantes import FEN_INITIAL, FIRST_BEST_MOVE, ALL_BEST_MOVES, ALL_MOVES, TOP2_FIRST_MOVES, \
    TOP3_FIRST_MOVES


class Entry:
    key = 0
    move = 0
    weight = 0
    learn = 0

    def pv(self):
        move = self.move

        f = (move >> 6) & 0o77
        fr = (f >> 3) & 0x7
        ff = f & 0x7
        t = move & 0o77
        tr = (t >> 3) & 0x7
        tf = t & 0x7
        p = (move >> 12) & 0x7
        pv = chr(ff + ord("a")) + chr(fr + ord("1")) + chr(tf + ord("a")) + chr(tr + ord("1"))
        if p:
            pv += " nbrq"[p]

        return {"e1h1": "e1g1", "e1a1": "e1c1", "e8h8": "e8g8", "e8a8": "e8c8"}.get(pv, pv)


class Polyglot:
    """
    fen = "rnbqkbnr/pppppppp/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    fich = "varied.bin"

    p = Polyglot()
    li = p.lista( fich, fen )

    for entry in li:
        p rint entry.pv(), entry.weight
    """

    def __init__(self, path=None):
        self.path = path
        self.f = None

    def __enter__(self):
        self.f = open(self.path, "rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.f:
            self.f.close()

    def hash(self, fen):
        return FasterCode.hash_polyglot8(fen)

    def int_from_file(self, length, r):
        cad = self.f.read(length)

        if len(cad) != length:
            return True, 0
        for c in cad:
            r = (r << 8) + c
        return False, r

    def entry_from_file(self):
        entry = Entry()

        r = 0
        ret, r = self.int_from_file(8, r)
        if ret:
            return True, None
        entry.key = r

        ret, r = self.int_from_file(2, r)
        if ret:
            return True, None
        entry.move = r & 0xFFFF

        ret, r = self.int_from_file(2, r)
        if ret:
            return True, None
        entry.weight = r & 0xFFFF

        ret, r = self.int_from_file(4, r)
        if ret:
            return True, None
        entry.learn = r & 0xFFFFFFFF

        return False, entry

    def find_key(self, key):
        first = -1
        try:
            if not self.f.seek(-16, os.SEEK_END):
                entry = Entry()
                entry.key = key + 1
                return -1, entry
        except:
            return -1, None

        last = self.f.tell() // 16
        ret, last_entry = self.entry_from_file()
        while True:
            if last - first == 1:
                return last, last_entry

            middle = (first + last) // 2
            self.f.seek(16 * middle, os.SEEK_SET)
            ret, middle_entry = self.entry_from_file()
            if key <= middle_entry.key:
                last = middle
                last_entry = middle_entry
            else:
                first = middle

    def lista(self, path, fen):
        with open(path, "rb") as self.f:
            return self.xlista(fen)

    def xlista(self, fen):
        key = self.hash(fen)

        offset, entry = self.find_key(key)
        li = []
        if entry and entry.key == key:

            li.append(entry)

            self.f.seek(16 * (offset + 1), os.SEEK_SET)
            while True:
                ret, entry = self.entry_from_file()
                if ret or (entry.key != key):
                    break

                li.append(entry)

            li.sort(key=lambda x: x.weight, reverse=True)

        return li


class Line:
    def __init__(self, pol_w, pol_b, lines, mode_white, mode_black, start_fen, dispatch, porc_min_white,
                 porc_min_black, weight_min_white, weight_min_black):
        self.li_pv = []
        self.st_fens_m2 = set()
        self.start_fen = start_fen if start_fen else FEN_INITIAL
        self.last_fen = self.start_fen

        self.finished = False
        self.pol_w: Polyglot = pol_w
        self.pol_b: Polyglot = pol_b
        self.mode_white = mode_white
        self.mode_black = mode_black

        self.porc_min_white = porc_min_white
        self.porc_min_black = porc_min_black
        self.weight_min_white = weight_min_white
        self.weight_min_black = weight_min_black

        self.dispatch = dispatch

        self.lines = lines
        self.lines.append(self)

    def add_entry(self, xentry: Entry):
        FasterCode.set_fen(self.last_fen)
        pv = xentry.pv()
        FasterCode.make_move(pv)
        new_fen = FasterCode.get_fen()
        new_fenm2 = FasterCode.fen_fenm2(new_fen)
        if new_fenm2 in self.st_fens_m2:
            self.finished = True
            return False
        self.li_pv.append(pv)
        self.st_fens_m2.add(new_fenm2)
        self.last_fen = new_fen
        return True

    def next_level(self, xmax_lines) -> bool:
        if len(self.lines) > xmax_lines:
            return False
        if self.finished:
            return False
        is_white = "w" in self.last_fen
        polyglot = self.pol_w if is_white else self.pol_b
        li_entries = polyglot.xlista(self.last_fen)
        if not li_entries:
            self.finished = True
            return False
        xentry: Entry

        if is_white:
            mode = self.mode_white
            porc = self.porc_min_white
            min_weight = self.weight_min_white
        else:
            mode = self.mode_black
            porc = self.porc_min_black
            min_weight = self.weight_min_black

        if porc:
            tt = sum(xentry.weight for xentry in li_entries)
            if tt == 0:
                self.finished = True
                return False
            li_entries = [xentry for xentry in li_entries if xentry.weight / tt >= porc]
            if not li_entries:
                self.finished = True
                return False

        if min_weight:
            li_entries = [xentry for xentry in li_entries if xentry.weight >= min_weight]

        if mode != ALL_MOVES:
            li_entries.sort(key=lambda x: x.weight, reverse=True)
            if mode == FIRST_BEST_MOVE:
                li_entries = li_entries[:1]
            elif mode == ALL_BEST_MOVES:
                weight1 = li_entries[0].weight
                li_entries = [entry for entry in li_entries if entry.weight == weight1]
            elif mode == TOP2_FIRST_MOVES:
                li_entries = li_entries[:2]
            elif mode == TOP3_FIRST_MOVES:
                li_entries = li_entries[:3]

        for xentry in li_entries[1:]:
            if len(self.lines) >= xmax_lines:
                break
            new_line = Line(self.pol_w, self.pol_b, self.lines, self.mode_white, self.mode_black,
                            self.start_fen, self.dispatch, 0.0, 0.0, 0, 0)
            new_line.li_pv = self.li_pv[:]
            new_line.st_fens_m2 = set(self.st_fens_m2)
            new_line.last_fen = self.last_fen
            if not new_line.add_entry(xentry):
                del self.lines[-1]

            if not self.dispatch(len(self.li_pv) + 1, len(self.lines)):
                return False

        self.add_entry(li_entries[0])
        return True

    def __str__(self):
        return " ".join(self.li_pv)

    def __len__(self):
        return len(self.li_pv)


def dic_modes():
    return {
        FIRST_BEST_MOVE: _("First best move"),
        ALL_BEST_MOVES: _("All best moves"),
        TOP2_FIRST_MOVES: _("Two first moves"),
        TOP3_FIRST_MOVES: _("Three first moves"),
        ALL_MOVES: _("All moves"),
    }


def gen_lines(path_pol_w, path_pol_b, mode_w, mode_b, max_lines, max_depth, start_fen, dispatch, porc_min_white=None,
              porc_min_black=None, weight_min_white=None, weight_min_black=None):
    with Polyglot(path_pol_w) as pol_w, Polyglot(path_pol_b) as pol_b:
        lines = []
        Line(pol_w, pol_b, lines, mode_w, mode_b, start_fen, dispatch, porc_min_white, porc_min_black, weight_min_white,
             weight_min_black)

        if max_depth == 0:
            max_depth = sys.maxsize
        if max_lines == 0:
            max_lines = sys.maxsize

        depth = 0
        while depth < max_depth:
            ok = False
            num_lines = len(lines)
            for pos in range(num_lines):
                line = lines[pos]
                if line.next_level(max_lines):
                    ok = True
                else:
                    if not dispatch(None, None):
                        break
            if not ok:
                break
            depth += 1

    return lines
