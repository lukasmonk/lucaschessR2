import random
import time
from itertools import permutations

import Code


class Chess2880:
    def __init__(self):
        self.lista = self.generate()
        self.key = "CHESS2880"

    @staticmethod
    def generate():
        letras = "RNBQKBNR"
        st = set()
        for permutation in permutations(letras):
            x = permutation.index("B")
            y = permutation.index("B", x + 1)
            if x % 2 == y % 2:
                continue
            permutation = "".join(permutation)
            if permutation in st:
                continue
            st.add(permutation)
        st.remove(letras)
        li = list(st)
        li.sort()
        random.seed(2880)
        random.shuffle(li)
        random.seed(time.time_ns())
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
