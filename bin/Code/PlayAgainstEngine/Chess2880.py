import random
from itertools import permutations

import Code
from Code import Util


class Chess2880:
    def __init__(self):
        self.lista = self.generate()
        self.key = "CHESS2880"

    @staticmethod
    def generate():
        letras = "RNBQKBNR"
        st = set()
        for li_permutation in permutations(letras):
            x = li_permutation.index("B")
            y = li_permutation.index("B", x + 1)
            if x % 2 == y % 2:
                continue
            permutation: str = "".join(li_permutation)
            if permutation in st:
                continue
            st.add(permutation)
        st.remove(letras)
        li = list(st)
        li.sort()
        random.seed(2880)
        random.shuffle(li)
        Util.randomize()
        return li

    def get_fen(self, num):
        grp = self.lista[num]
        castle = ""
        if grp[4] == "K":
            if grp[7] == "R":
                castle += "K"
            if grp[0] == "R":
                castle += "Q"
            castle += castle.lower()
        if not castle:
            castle = "-"
        fen = f"{grp.lower()}/pppppppp/8/8/8/8/PPPPPPPP/{grp} w {castle} - 0 1"
        return fen

    def get_fen_random(self):
        return self.get_fen(random.randint(0, 2878))

    def save_last_manual(self, number):
        dic = {"LAST_MANUAL": str(number + 1)}
        Code.configuration.write_variables(self.key, dic)

    def get_last_manual(self):
        dic = Code.configuration.read_variables(self.key)
        return dic.get("LAST_MANUAL", "")


class Chess324:
    def __init__(self):
        self.lista = self.generate()
        self.key = "CHESS324"

    @staticmethod
    def generate():
        letras = "NBQBN"
        st = set()
        li_permutation: list
        for li_permutation in permutations(letras):
            li_permutation = list(li_permutation)
            li_permutation.insert(0, "R")
            li_permutation.insert(4, "K")
            li_permutation.append("R")
            x = li_permutation.index("B")
            y = li_permutation.index("B", x + 1)
            if x % 2 == y % 2:
                continue
            permutation: str = "".join(li_permutation)
            st.add(permutation)
        li = list(st)
        li.sort()

        li_total = []
        permutation_black: str
        permutation_white: str
        for permutation_black in li:
            for permutation_white in li:
                if permutation_black == permutation_white and permutation_white == "RNBQKBNR":
                    continue
                li_total.append((permutation_black.lower(), permutation_white))

        random.seed(324)
        random.shuffle(li_total)
        Util.randomize()
        return li_total

    def get_fen(self, num):
        grp_black, grp_white = self.lista[num]
        fen = f"{grp_black}/pppppppp/8/8/8/8/PPPPPPPP/{grp_white} w KQkq - 0 1"
        return fen

    def get_fen_random(self):
        pos = random.randint(0, 323)
        return self.get_fen(pos)

    def save_last_manual(self, number):
        dic = {"LAST_MANUAL": str(number + 1)}
        Code.configuration.write_variables(self.key, dic)

    def get_last_manual(self):
        dic = Code.configuration.read_variables(self.key)
        return dic.get("LAST_MANUAL", "")
