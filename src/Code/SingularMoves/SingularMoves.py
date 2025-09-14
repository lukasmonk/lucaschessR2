import datetime
import random

import Code
from Code import Util
from Code.SQL import UtilSQL


class SingularMoves:
    def __init__(self, fichero_db):
        fichero_tactic = Code.path_resource("IntFiles", "tactic0.bm")
        self.dic = self.lee(fichero_tactic)
        self.li_bloque = None
        self.li_bloque_sol = []
        self.registro = None
        self.current_key = None

        self.db = UtilSQL.DictSQL(fichero_db)
        self.db_keys = self.db.keys(si_ordenados=True, si_reverse=True)

    def lee(self, fichero_tactic):
        with open(fichero_tactic, "rt", encoding="utf-8", errors="ignore") as f:
            dic = {}
            for xdif in "12345":
                dic[xdif] = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    dic[linea[-1]].append(linea)
        return dic

    def nuevo_bloque(self):
        li = random.sample(self.dic["1"], 3)
        li.extend(random.sample(self.dic["2"], 3))
        li.extend(random.sample(self.dic["3"], 2))
        li.extend(random.sample(self.dic["4"], 1))
        li.extend(random.sample(self.dic["5"], 1))
        # no shuffle, que la experiencia sea de menos a mas
        self.li_bloque = li
        self.registro = None
        self.current_key = None

    def repite(self, row):
        self.current_key = self.db_keys[row]
        self.registro = self.db[self.current_key]
        self.li_bloque = [lin["LINE"] for lin in self.registro["BLOCK"]]

    def linea_bloque(self, pos):
        alm = Util.Record()
        alm.fen, alm.bm, alm.sol, alm.pgn, alm.dif = self.li_bloque[pos].split("|")
        alm.max_time = (int(alm.dif) ** 2) * 5 + 120
        return alm

    def add_bloque_sol(self, alm):
        self.li_bloque_sol.append(alm)

    def media(self):
        if self.li_bloque_sol:
            tt = 0.0
            for alm in self.li_bloque_sol:
                tt += alm.score
            return tt / len(self.li_bloque_sol)
        else:
            return None

    def rotulo_media(self):
        m = self.media()
        return "" if m is None else "%0.2f" % m

    def graba(self):
        if self.current_key is None:
            self.graba_nuevo()
        else:
            self.graba_repeticion()

    def graba_repeticion(self):
        repeticiones = self.registro.get("REPETITIONS", [])
        rep = {}
        rep["DATETIME"] = datetime.datetime.now()
        strength = rep["STRENGTH"] = self.media()
        li = rep["BLOCK"] = []
        for pos, alm in enumerate(self.li_bloque_sol):
            bl = {}
            bl["SCORE"] = alm.score
            bl["TIME"] = alm.time
            li.append(bl)
        repeticiones.append(rep)
        self.registro["REPETITIONS"] = repeticiones
        best = self.registro.get("BEST", 0.00)
        if best < strength:
            self.registro["BEST"] = strength
        self.db[self.current_key] = self.registro

    def graba_nuevo(self):
        hoy = datetime.datetime.now()
        key = hoy.strftime("%Y%m%d%H%M")

        registro = {}
        registro["DATETIME"] = hoy
        registro["STRENGTH"] = self.media()
        li = registro["BLOCK"] = []
        for pos, alm in enumerate(self.li_bloque_sol):
            bl = {}
            bl["LINE"] = self.li_bloque[pos]
            bl["SCORE"] = alm.score
            bl["TIME"] = alm.time
            li.append(bl)

        self.db[key] = registro
        self.db_keys.insert(0, key)

    def len_db(self):
        return len(self.db_keys)

    def reg_db(self, row):
        return self.db[self.db_keys[row]]

    def borra_db(self, lista):
        li = [self.db_keys[row] for row in lista]

        for key in li:
            del self.db[key]

        self.db.pack()
        self.db_keys = self.db.keys(si_ordenados=True, si_reverse=True)
