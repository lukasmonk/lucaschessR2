import collections

import FasterCode

import Code
from Code import Util
from Code.Base import Position
from Code.Translations import TrListas


class Opening:
    def __init__(self, key):
        self.name = key
        self.parent_fm2 = ""
        self.children_fm2 = []
        self.a1h8 = ""
        self.pgn = ""
        self.eco = ""
        self.is_basic = False
        self.fm2 = None

    @property
    def tr_name(self):
        return _FO(self.name)

    def tr_pgn(self):
        p = ""
        pzs = "KQRBNPkqrbnp"
        pgn = self.pgn
        for n, c in enumerate(pgn):
            if c in pzs and not pgn[n + 1].isdigit():
                c = TrListas.letter_piece(c)
            p += c
        return p

    def __str__(self):
        return self.name + " " + self.pgn


class ListaOpeningsStd:
    def __init__(self):
        self.st_fenm2_test = set()
        self.dic_fenm2_op, self.dic_fenm2_op_all = {}, {}

    @staticmethod
    def read_fenm2_test():
        path = Code.path_resource("Openings", "openings.lkfen")
        with open(path, "rt") as q:
            st_fenm2 = set(q.read().split("|"))

        return st_fenm2

    @staticmethod
    def read_fenm2_op():
        path = Code.path_resource("Openings", "openings.lkop")
        dic_fenm2_op = {}
        dic_fenm2_op_all = collections.defaultdict(set)
        st_fenm2_test = set()
        with open(path, "rt", encoding="utf-8") as q:
            for linea in q:
                name, a1h8, pgn, eco, basic, fenm2, hijos, parent, lfenm2 = linea.strip().split("|")

                dic_fenm2_op[fenm2] = op = Opening(name)
                op.a1h8 = a1h8
                op.eco = eco
                op.pgn = pgn
                op.parent_fm2 = parent
                op.is_basic = basic == "Y"
                op.fm2 = fenm2

                if parent:
                    st_fenm2_test.add(parent)
                st_fenm2_test.add(fenm2)
                dic_fenm2_op_all[fenm2].add(op)

                li_pv = a1h8.split(" ")
                li_fenm2 = lfenm2.split(",")
                for x in range(len(li_pv)):
                    fenm2 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -" if x == 0 else li_fenm2[x - 1]
                    dic_fenm2_op_all[fenm2].add(op)
                    st_fenm2_test.add(fenm2)

        return dic_fenm2_op, dic_fenm2_op_all, st_fenm2_test

    @staticmethod
    def dic_fen64():
        path = Code.path_resource("Openings", "openings.lkop")
        dd = collections.defaultdict(list)
        with open(path, "rt", encoding="utf-8") as q:
            for linea in q:
                name, a1h8, pgn, eco, basic, fenm2, hijos, parent, lfenm2 = linea.strip().split("|")

                li_fen = [p for p in lfenm2.split(",")]
                li_fen.append(fenm2)
                li = a1h8.split(" ")

                for pos in range(len(li)):
                    pv = " ".join(li[:pos + 1])
                    # xpv = FasterCode.pv_xpv(pv)
                    fen = li_fen[pos]
                    fen64 = Util.fen_fen64(fen)
                    if pv not in dd[fen64]:
                        dd[fen64].append(pv)
        return dd

    def reset(self):
        self.dic_fenm2_op, self.dic_fenm2_op_all, self.st_fenm2_test = self.read_fenm2_op()
        self.read_personal()

    def read_personal(self):
        fichero_pers = Code.configuration.file_pers_openings()
        lista = Util.restore_pickle(fichero_pers, [])
        for reg in lista:
            estandar = reg["ESTANDAR"]
            op = Opening(reg["NOMBRE"])
            op.eco = reg["ECO"]
            op.a1h8 = reg["A1H8"]
            op.pgn = reg["PGN"]
            op.is_basic = estandar
            li_uci = op.a1h8.split(" ")
            num = len(li_uci)
            for x in range(num):
                pv = " ".join(li_uci[: x + 1])
                fen = FasterCode.make_pv(pv)
                fm2 = Position.legal_fenm2(fen)
                self.st_fenm2_test.add(fm2)
                if x == num - 1:
                    self.dic_fenm2_op[fm2] = op
                    op.fm2 = fm2

    def assign_opening(self, game):
        game.opening = None
        game.pending_opening = True

        without = 0
        for nj, move in enumerate(game.li_moves):
            fm2 = move.position.fenm2()
            if fm2 in self.st_fenm2_test:
                if fm2 in self.dic_fenm2_op:
                    game.opening = self.dic_fenm2_op[fm2]
                    for np in range(nj + 1):
                        game.move(np).in_the_opening = True

            else:
                without += 1
                if without == 10:
                    game.pending_opening = False
                    return

    def list_possible_openings(self, game):
        li_openings = []
        fm2 = game.last_position.fenm2()
        if fm2 in self.dic_fenm2_op_all:
            op_select = self.dic_fenm2_op.get(fm2)
            for op in self.dic_fenm2_op_all[fm2]:
                if op != op_select:
                    li_openings.append(op)
        li_openings.sort(key=lambda xop: xop.a1h8)
        li = []
        ultima = "zzzz"
        for op in li_openings:
            if not op.a1h8.startswith(ultima):
                ultima = op.a1h8
                li.append(op)
        li.sort(key=lambda xop: ("A" if xop.is_basic else "B") + xop.tr_name.upper())
        return li

    def base_xpv(self, xpv):
        lipv = FasterCode.xpv_pv(xpv).split(" ")
        last_ap = None

        FasterCode.set_init_fen()
        for n, pv in enumerate(lipv):
            FasterCode.make_move(pv)
            fen = FasterCode.get_fen()
            fenm2 = Position.legal_fenm2(fen)
            if fenm2 in self.dic_fenm2_op:
                last_ap = self.dic_fenm2_op[fenm2]
        return last_ap

    def xpv(self, xpv):
        last_ap = self.base_xpv(xpv)
        return last_ap.tr_name if last_ap else ""

    def assign_pv(self, pv):
        lipv = pv.split(" ")
        last_ap = None

        FasterCode.set_init_fen()
        for n, pv in enumerate(lipv):
            FasterCode.make_move(pv)
            fen = FasterCode.get_fen()
            fenm2 = Position.legal_fenm2(fen)
            if fenm2 in self.dic_fenm2_op:
                last_ap = self.dic_fenm2_op[fenm2]
        return last_ap

    def is_book_fenm2(self, fenm2):
        return fenm2 in self.st_fenm2_test


ap = ListaOpeningsStd()
