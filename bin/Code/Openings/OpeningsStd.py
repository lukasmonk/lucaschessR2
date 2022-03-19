import FasterCode

import Code
from Code.Base import Position
from Code.Translations import TrListas
from Code import Util


class Opening:
    def __init__(self, key):
        self.name = key
        self.tr_name = key
        self.parent_fm2 = ""
        self.children_fm2 = []
        self.a1h8 = ""
        self.pgn = ""
        self.eco = ""
        self.is_basic = False
        self.fm2 = None

    def tr_pgn(self):
        p = ""
        pzs = "KQRBNPkqrbnp"
        pgn = self.pgn
        for n, c in enumerate(pgn):
            if c in pzs and not pgn[n + 1].isdigit():
                c = TrListas.letterPiece(c)
            p += c
        return p

    def __str__(self):
        return self.name + " " + self.pgn


class ListaOpeningsStd:
    def __init__(self):
        self.st_fenm2_test = self.read_fenm2_test()
        self.dic_fenm2_op = self.read_fenm2_op()

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
        with open(path, "rt", encoding="utf-8") as q:
            for linea in q:
                name, a1h8, pgn, eco, basic, fenm2, hijos, parent = linea.strip().split("|")
                dic_fenm2_op[fenm2] = op = Opening(name)
                op.a1h8 = a1h8
                op.eco = eco
                op.pgn = pgn
                op.children_fm2 = hijos.split(",")
                op.parent_fm2 = parent
                op.is_basic = basic == "Y"
                op.fm2 = fenm2

        return dic_fenm2_op

    def reset(self):
        self.st_fenm2_test = self.read_fenm2_test()
        self.dic_fenm2_op = self.read_fenm2_op()
        self.read_personal()
        self.translate()

    def translate(self):
        for op in self.dic_fenm2_op.values():
            op.tr_name = Code.translations.translate_opening(op.name)

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
                if x == num-1:
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
        li_ap = []
        if len(game) == 0:
            for op in self.dic_fenm2_op.values():
                if not op.parent_fm2:
                    li_ap.append(op)
        else:
            fm2 = game.last_position.fenm2()
            for op in self.dic_fenm2_op.values():
                if fm2 == op.parent_fm2:
                    li_ap.append(op)

        li_ap.sort(key=lambda op: ("A" if op.is_basic else "B") + op.tr_name)
        return li_ap

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

    def is_book_fenm2(self, fenm2):
        return fenm2 in self.st_fenm2_test


ap = ListaOpeningsStd()


# Borrar en la versión 3.0---------------------------------

class OpeningStd(Opening):
    def __init__(self, key):
        Opening.__init__(self, key)

    @property
    def tr_name(self):
        return self.trNombre

# ^^^^Borrar en la versión 3.0---------------------------------
