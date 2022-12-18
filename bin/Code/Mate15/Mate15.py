import datetime

import Code
from Code.SQL import UtilSQL


class Mate15:
    fen: str
    date: datetime.datetime
    info: str
    move: str
    resp: dict
    tries: list

    def __init__(self):
        self.date = datetime.datetime.now()
        self.pos = 0
        self.fen = ""
        self.info = ""
        self.move = ""
        self.resp = {}
        self.tries = []  # time

    def result(self):
        if len(self.tries) == 0:
            return None
        min_time = 99999999
        for tm in self.tries:
            if tm < min_time:
                min_time = tm
        return min_time

    def num_tries(self):
        return len(self.tries)

    def append_try(self, tm):
        self.tries.append(tm)

    def save(self):
        dic = {
            "date": self.date,
            "pos": self.pos,
            "fen": self.fen,
            "info": self.info,
            "move": self.move,
            "resp": self.resp,
            "tries": self.tries,
        }
        return dic

    def restore(self, dic):
        self.date = dic["date"]
        self.pos = dic["pos"]
        self.fen = dic["fen"]
        self.info = dic["info"]
        self.move = dic["move"]
        self.resp = dic["resp"]
        self.tries = dic["tries"]

    def copy(self):
        mate15 = Mate15()
        mate15.restore(self.save())
        mate15.date = datetime.datetime.now()
        return mate15


class DBMate15:
    def __init__(self, path):
        self.path = path

        with self.db() as db:
            li_dates = db.keys(True, True)
            dic_data = db.as_dictionary()
            self.li_data = []
            for date in li_dates:
                mate15 = Mate15()
                mate15.restore(dic_data[date])
                self.li_data.append(mate15)

    def db(self):
        return UtilSQL.DictSQL(self.path)

    def db_config(self):
        return UtilSQL.DictSQL(self.path, tabla="config")

    def __len__(self):
        return len(self.li_data)

    def last(self):
        if len(self.li_data) > 0:
            return self.li_data[0]
        return None

    def create_new(self):
        with open(Code.path_resource("IntFiles", "mate.15"), "rt", encoding="utf-8") as f:
            li = [linea.strip() for linea in f if linea.strip()]

        with self.db_config() as dbc:
            siguiente = dbc["NEXT"]
            if siguiente is None:
                siguiente = 0
            if siguiente >= len(li):
                siguiente = 0
            linea = li[siguiente]
            dbc["NEXT"] = siguiente + 1

        # 8/4K1P1/4B3/4k3/4r3/4R3/8/6Q1 w - - 0 1|Shahmat besteciliyi,2006,ABDULLAYEV Elmar|g1e1|{'e5f4': 'e1g3', 'e4e3': 'e1e3', 'e5d4': 'e1c3'}
        fen, info, move1, cdic = linea.split("|")

        m15 = Mate15()
        m15.fen = fen
        m15.pos = siguiente
        m15.info = info
        m15.move = move1
        m15.resp = eval(cdic)

        with self.db() as db:
            db[str(m15.date)] = m15.save()
            self.li_data.insert(0, m15)

        return m15

    def repeat(self, base_15):
        m15 = base_15.copy()
        m15.tries = []

        with self.db() as db:
            db[str(m15.date)] = m15.save()
            self.li_data.insert(0, m15)

    def remove_mate15(self, li_recno):
        with self.db() as db:
            li_recno.sort(reverse=True)
            for recno in li_recno:
                mate15 = self.li_data[recno]
                del db[str(mate15.date)]
                del self.li_data[recno]
            db.pack()

    def save(self, mate15):
        with self.db() as db:
            db[str(mate15.date)] = mate15.save()

    def mate15(self, recno):
        return self.li_data[recno]
