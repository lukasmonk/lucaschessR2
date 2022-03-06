import FasterCode

from Code.Base.Constantes import FEN_INITIAL
from Code.Translations import TrListas


class Position:
    def __init__(self):
        self.li_extras = []

    def set_pos_initial(self):
        return self.read_fen(FEN_INITIAL)

    def is_initial(self):
        return self.fen() == FEN_INITIAL

    def logo(self):
        #  self.leeFen( "8/4q1k1/1R2bpn1/1N2n1b1/1B2r1r1/1Q6/1PKNBR2/8 w - - 0 1" )
        self.read_fen("8/4Q1K1/1r2BPN1/1n2N1B1/1b2R1R1/1q6/1pknbr2/8 w - - 0 1")
        return self

    def copia(self):
        p = Position()
        p.squares = self.squares.copy()
        p.castles = self.castles
        p.en_passant = self.en_passant
        p.is_white = self.is_white
        p.num_moves = self.num_moves
        p.mov_pawn_capt = self.mov_pawn_capt
        return p

    def __eq__(self, other):
        return self.fen() == other.fen() if other else False

    def legal(self):
        if self.castles != "-":
            dic = {"K": ("K", "R", "e1", "h1"), "k": ("k", "r", "e8", "h8"), "Q": ("K", "R", "e1", "a1"), "q": ("k", "r", "e8", "a8")}
            enr = ""
            for tipo in self.castles:
                king, rook, pos_king, pos_rook = dic[tipo]
                if self.squares.get(pos_king) == king and self.squares.get(pos_rook) == rook:
                    enr += tipo
            self.castles = enr if enr else "-"

        # https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation#:~:text=En%20passant%20target%20square%20in,make%20an%20en%20passant%20capture.
        # En passant target square in algebraic notation. If there's no en passant target square, this is "-".
        # If a pawn has just made a two-square move, this is the position "behind" the pawn. This is recorded
        # regardless of whether there is a pawn in position to make an en passant capture
        if len(self.en_passant) == 2:
            if not (self.en_passant[1] in "36"):
                self.en_passant = "-"
        else:
            self.en_passant = "-"

    def is_valid_fen(self, fen):
        fen = fen.strip()
        if fen.count("/") != 7:
            return False
        try:
            self.read_fen(fen)
            return True
        except:
            return False

    def read_fen(self, fen):
        fen = fen.strip()
        if fen.count("/") != 7:
            return self.set_pos_initial()

        li = fen.split(" ")
        nli = len(li)
        if nli < 6:
            lid = ["w", "-", "-", "0", "1"]
            li.extend(lid[nli - 1 :])
        position, color, self.castles, self.en_passant, mp, move = li[:6]

        self.is_white = color == "w"
        self.num_moves = int(move)
        if self.num_moves < 1:
            self.num_moves = 1
        self.mov_pawn_capt = int(mp)

        d = {}
        for x, linea in enumerate(position.split("/")):
            cFil = chr(48 + 8 - x)
            nc = 0
            for c in linea:
                if c.isdigit():
                    nc += int(c)
                elif c in "KQRBNPkqrbnp":
                    cCol = chr(nc + 97)
                    d[cCol + cFil] = c
                    nc += 1
                else:
                    return self.set_pos_initial()
        self.squares = d
        self.legal()
        return self

    def set_lce(self):
        return FasterCode.set_fen(self.fen())

    def get_exmoves(self):
        self.set_lce()
        return FasterCode.get_exmoves()

    def fenBase(self):
        n_sin = 0
        position = ""
        for i in range(8, 0, -1):
            c_fil = chr(i + 48)
            row = ""
            for j in range(8):
                c_col = chr(j + 97)
                key = c_col + c_fil
                v = self.squares.get(key)
                if v is None:
                    n_sin += 1
                else:
                    if n_sin:
                        row += "%d" % n_sin
                        n_sin = 0
                    row += v
            if n_sin:
                row += "%d" % n_sin
                n_sin = 0

            position += row
            if i > 1:
                position += "/"
        color = "w" if self.is_white else "b"
        return position + " " + color

    def fenDGT(self):
        n_sin = 0
        resp = ""
        for i in range(8, 0, -1):
            c_fil = chr(i + 48)
            for j in range(8):
                c_col = chr(j + 97)
                key = c_col + c_fil
                v = self.squares.get(key)
                if v is None:
                    n_sin += 1
                else:
                    if n_sin:
                        resp += "%d" % n_sin
                        n_sin = 0
                    resp += v
        return resp

    def fen(self):
        position = self.fenBase()
        self.legal()
        return "%s %s %s %d %d" % (position, self.castles, self.en_passant, self.mov_pawn_capt, self.num_moves)

    def fenm2(self):
        position = self.fenBase()
        self.legal()
        return "%s %s %s" % (position, self.castles, self.en_passant)

    def siExistePieza(self, pieza, a1h8=None):
        if a1h8:
            return self.squares.get(a1h8) == pieza
        else:
            n = 0
            for k, v in self.squares.items():
                if v == pieza:
                    n += 1
            return n

    def get_pz(self, a1h8):
        return self.squares.get(a1h8)

    def pzs_key(self):
        td = "KQRBNPkqrbnp"
        key = ""
        for pz in td:
            for k, c in self.squares.items():
                if c == pz:
                    key += c
        return key

    def capturas(self):
        """
        Devuelve las piezas capturadas, liNuestro, liOponente. ( pieza, number )
        """

        dic = {}
        for pieza, num in (("P", 8), ("R", 2), ("N", 2), ("B", 2), ("Q", 1), ("K", 1)):
            dic[pieza] = num
            dic[pieza.lower()] = num

        for pieza in self.squares.values():
            if pieza and dic[pieza] > 0:
                dic[pieza] -= 1

        return dic, self.is_white

    def capturas_diferencia(self):
        """
        Devuelve las piezas capturadas, liNuestro, liOponente. ( pieza, number )
        """
        piezas = "PRNBQK"
        dic = {pz: 0 for pz in (piezas + piezas.lower())}
        for pieza in self.squares.values():
            if pieza:
                dic[pieza] += 1
        dif = {}
        for pieza in "PRNBQK":
            d = dic[pieza] - dic[pieza.lower()]
            if d < 0:
                dif[pieza.lower()] = -d
            elif d > 0:
                dif[pieza] = d
        return dif

    def moverPV(self, pv):
        return self.mover(pv[:2], pv[2:4], pv[4:])

    def mover(self, from_a1h8, to_a1h8, promotion=""):
        self.set_lce()

        mv = FasterCode.move_expv(from_a1h8, to_a1h8, promotion)
        if not mv:
            return False, "Error"

        self.li_extras = []

        enrK = mv.iscastle_k()
        enrQ = mv.iscastle_q()
        enPa = mv.is_enpassant()

        if promotion:
            if self.is_white:
                promotion = promotion.upper()
            else:
                promotion = promotion.lower()
            self.li_extras.append(("c", to_a1h8, promotion))

        elif enrK:
            if self.is_white:
                self.li_extras.append(("m", "h1", "f1"))
            else:
                self.li_extras.append(("m", "h8", "f8"))

        elif enrQ:
            if self.is_white:
                self.li_extras.append(("m", "a1", "d1"))
            else:
                self.li_extras.append(("m", "a8", "d8"))

        elif enPa:
            capt = self.en_passant.replace("6", "5").replace("3", "4")
            self.li_extras.append(("b", capt))

        self.read_fen(FasterCode.get_fen())  # despues de li_extras, por si enpassant

        return True, self.li_extras

    def pr_board(self):
        resp = "   " + "+---" * 8 + "+" + "\n"
        for row in "87654321":
            resp += " " + row + " |"
            for column in "abcdefgh":
                pieza = self.squares.get(column + row)
                if pieza is None:
                    resp += "   |"
                    # resp += "-"+column+row + "|"
                else:
                    resp += " " + pieza + " |"
            resp += " " + row + "\n"
            resp += "   " + "+---" * 8 + "+" + "\n"
        resp += "    "
        for column in "abcdefgh":
            resp += " " + column + "  "

        return resp

    def pgn(self, from_sq, to_sq, promotion=""):
        self.set_lce()
        return FasterCode.get_pgn(from_sq, to_sq, promotion)

    def get_fenm2(self, from_sq, to_sq, promotion=""):
        self.set_lce()
        fen = FasterCode.get_fen()
        return FasterCode.fen_fenm2(fen)

    def html(self, mv: str):
        pgn = self.pgn(mv[:2], mv[2:4], mv[4:])
        li = []
        tp = "w" if self.is_white else "b"
        for c in pgn:
            if c in "NBRQK":
                li.append(
                    '<img src="../Resources/IntFiles/Figs/%s%s.png" width="20" height="20" style="vertical-align:bottom">' % (tp, c.lower())
                )
            else:
                li.append(c)
        return "".join(li)

    def pv2dgt(self, from_sq, to_sq, promotion=""):
        p_ori = self.squares.get(from_sq)

        # Enroque
        if p_ori in "Kk":
            n = ord(from_sq[0]) - ord(to_sq[0])
            if abs(n) == 2:
                orden = "ke8kc8ra8rd8" if n == 2 else "ke8kg8rh8rf8"
                if p_ori == "k":
                    return orden
                else:
                    return orden.replace("k", "K").replace("8", "1")
        # Promotion
        if promotion:
            promotion = promotion.upper() if self.is_white else promotion.lower()
            return p_ori + from_sq + promotion + to_sq

        # Al paso
        if p_ori in "Pp" and to_sq == self.en_passant:
            if self.is_white:
                otro = "p"
                dif = -1
            else:
                otro = "P"
                dif = +1
            square = "%s%d" % (to_sq[0], int(to_sq[1]) + dif)
            return p_ori + from_sq + p_ori + to_sq + otro + square + "." + square

        return p_ori + from_sq + p_ori + to_sq

    def pgn_translated(self, from_sq, to_sq, promotion=""):
        d_conv = TrListas.dConv()
        li = []
        cpgn = self.pgn(from_sq, to_sq, promotion)
        if not cpgn:
            return ""
        for c in cpgn:
            if c in d_conv:
                c = d_conv[c]
            li.append(c)
        return "".join(li)

    def is_check(self):
        self.set_lce()
        return FasterCode.ischeck()

    def is_finished(self):
        return self.set_lce() == 0

    def is_mate(self):
        n = self.set_lce()
        return FasterCode.ischeck() and n == 0

    def valor_material(self):
        valor = 0
        d = {"R": 5, "Q": 10, "B": 3, "N": 3, "P": 1, "K": 0}
        for v in self.squares.values():
            if v:
                valor += d[v.upper()]
        return valor

    def siFaltaMaterial(self):
        # Rey y Rey
        # Rey + Caballo y Rey
        # Rey + Caballo y Rey y Caballo
        # Rey + alfil y Rey
        # Rey + alfil y Rey + alfil
        negras = ""
        blancas = ""
        for v in self.squares.values():
            if v:
                if v in "RrQqPp":
                    return False
                if v in "kK":
                    continue
                if v.isupper():
                    blancas += v
                else:
                    negras += v
        lb = len(blancas)
        ln = len(negras)
        if lb > 1 or ln > 1:
            return False

        if lb == 0 and ln == 0:
            return True

        todas = blancas.lower() + negras
        if todas in ["b", "n", "bn", "nb", "bb"]:
            return True

        return False

    def siFaltaMaterialColor(self, is_white):
        piezas = ""
        nb = "nb"
        prq = "prq"
        if is_white:
            nb = nb.upper()
            prq = prq.upper()
        for v in self.squares.values():
            if v:
                if v in prq:
                    return False
                if v in nb:
                    if piezas:
                        return False
                    else:
                        piezas = v
        return False

    def numPiezas(self, pieza):
        if not self.is_white:
            pieza = pieza.lower()
        num = 0
        for i in range(8):
            for j in range(8):
                c_col = chr(i + 97)
                c_fil = chr(j + 49)
                if self.squares.get(c_col + c_fil) == pieza:
                    num += 1
        return num

    def __len__(self):
        num = 0
        for pos in self.squares:
            if self.squares[pos]:
                num += 1
        return num

    def numPiezasWB(self):
        n_white = n_black = 0
        for i in range(8):
            for j in range(8):
                c_col = chr(i + 97)
                c_fil = chr(j + 49)
                pz = self.squares.get(c_col + c_fil)
                if pz and not (pz in "pkPK"):
                    if pz.islower():
                        n_black += 1
                    else:
                        n_white += 1
        return n_white, n_black

    def label(self):
        d = {x: [] for x in "KQRBNPkqrbnp"}
        for pos, pz in self.squares.items():
            d[pz].append(pos)

        li = []
        for pz in "KQRBNPkqrbnp":
            for pos in d[pz]:
                li.append("%s%s" % (pz, pos))

        return " ".join(li)

    def pesoWB(self):
        dpesos = {"Q": 110, "N": 30, "B": 32, "R": 50, "P": 10}
        peso = 0

        dposk = {True: [0, 0], False: [0, 0]}
        for i in range(8):
            for j in range(8):
                pieza = self.squares.get(chr(i + 97) + chr(j + 49))
                if pieza == "K":
                    dposk[True] = i, j
                elif pieza == "k":
                    dposk[False] = i, j

        for i in range(8):
            for j in range(8):
                pieza = self.squares.get(chr(i + 97) + chr(j + 49))
                if pieza and pieza.upper() != "K":
                    is_white = pieza.isupper()
                    ck, fk = dposk[not is_white]
                    d = 14 - (abs(i - ck) + abs(j - fk))
                    valor = d * dpesos[pieza.upper()]
                    if not is_white:
                        valor = -valor
                    peso += valor
        return peso

    def distanciaPiezaKenemigo(self, a1):
        pieza = self.squares.get(a1)
        if pieza is None:
            return 15
        k = "k" if pieza.isupper() else "K"
        for i in range(8):
            for j in range(8):
                if self.squares.get(chr(i + 97) + chr(j + 49)) == k:
                    c = ord(a1[0]) - 97
                    f = int(a1[1]) - 1
                    return abs(i - c) + abs(j - f) - 1

    def siPeonCoronando(self, from_a1h8, to_a1h8):
        pieza = self.squares.get(from_a1h8)
        if (not pieza) or (pieza.upper() != "P"):  # or self.squares[to_a1h8] is not None:
            return False
        if pieza == "P":
            ori = 7
            dest = 8
        else:
            ori = 2
            dest = 1

        if not (int(from_a1h8[1]) == ori and int(to_a1h8[1]) == dest):
            return False

        return True

    def aura(self):
        lista = []

        def add(lipos):
            for pos in lipos:
                lista.append(FasterCode.pos_a1(pos))

        def liBR(n_pos, fi, ci):
            fil, col = FasterCode.pos_rc(n_pos)
            li_m = []
            ft = fil + fi
            ct = col + ci
            while True:
                if ft < 0 or ft > 7 or ct < 0 or ct > 7:
                    break
                t = FasterCode.rc_pos(ft, ct)
                li_m.append(t)

                if self.squares.get(FasterCode.pos_a1(t)):
                    break
                ft += fi
                ct += ci
            add(li_m)

        pzs = "KQRBNP" if self.is_white else "kqrbnp"

        for i in range(8):
            for j in range(8):
                a1 = chr(i + 97) + chr(j + 49)
                pz = self.squares.get(a1)
                if pz and pz in pzs:
                    pz = pz.upper()
                    npos = FasterCode.a1_pos(a1)
                    if pz == "K":
                        add(FasterCode.li_k(npos))
                    elif pz == "Q":
                        for f_i, c_i in ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)):
                            liBR(npos, f_i, c_i)
                    elif pz == "R":
                        for f_i, c_i in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            liBR(npos, f_i, c_i)
                    elif pz == "B":
                        for f_i, c_i in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                            liBR(npos, f_i, c_i)
                    elif pz == "N":
                        add(FasterCode.li_n(npos))
                    elif pz == "P":
                        lim, lix = FasterCode.li_p(npos, self.is_white)
                        add(lix)
        return lista

    def cohesion(self):
        lipos = [k for k, v in self.squares.items() if v]
        d = 0
        for n, a in enumerate(lipos[:-1]):
            for b in lipos[n + 1 :]:
                d += distancia(a, b)
        return d


def distancia(from_sq, to_sq):
    return ((ord(from_sq[0]) - ord(to_sq[0])) ** 2 + (ord(from_sq[1]) - ord(to_sq[1])) ** 2) ** 0.5
