import datetime
import random

from Code.Base.Constantes import WHITE
from Code.SQL import UtilSQL


class GenTry:
    def __init__(self, xfrom, xto):
        letra_ini, letra_end = ord(xfrom[0]), ord(xto[0])
        num_ini, num_end = ord(xfrom[1]), ord(xto[1])

        li = []
        for letra in range(letra_ini, letra_end + 1):
            for num in range(num_ini, num_end + 1):
                li.append(chr(letra) + chr(num))
        self.li_base = li
        self.pos = -1
        self.li_current = None
        self.gen_new()

    def gen_new(self):
        self.pos = -1
        self.li_current = self.li_base[:]
        random.shuffle(self.li_current)

    def next(self):
        self.pos += 1
        if self.pos >= len(self.li_current) - 1:
            self.gen_new()
            self.pos += 1
        return self.li_current[self.pos], self.li_current[self.pos + 1]


class CoordinatesBasic:
    date: datetime.datetime
    score: int
    side: int
    gen_try: GenTry

    def __init__(self, is_white):
        self.date = datetime.datetime.now()
        self.score = 0
        self.side = is_white

    def str_side(self):
        return _("White") if self.side == WHITE else _("Black")

    def next(self):
        return self.gen_try.next()

    def new_try(self):
        self.gen_try = GenTry("a1", "h8")
        return self.side == WHITE

    def new_done(self, score):
        self.score = score

    def save(self):
        dic = {"date": self.date, "side": self.side, "score": self.score}
        return dic

    def restore(self, dic):
        self.date = dic["date"]
        self.score = dic["score"]
        self.side = dic["side"]


class DBCoordinatesBasic:
    def __init__(self, path):
        self.path = path
        self.refresh()

    def refresh(self):
        with self.db() as db:
            li_dates = db.keys(True, True)
            dic_data = db.as_dictionary()
            self.li_data = []
            for date in li_dates:
                coord = CoordinatesBasic(True)
                coord.restore(dic_data[date])
                self.li_data.append(coord)

    def db(self):
        return UtilSQL.DictSQL(self.path, tabla="basic")

    def db_config(self):
        return UtilSQL.DictSQL(self.path, tabla="config")

    def __len__(self):
        return len(self.li_data)

    def remove(self, li_recno):
        with self.db() as db:
            li_recno.sort(reverse=True)
            for recno in li_recno:
                coord = self.li_data[recno]
                del db[str(coord.date)]
                del self.li_data[recno]
            db.pack()

    def save(self, coord):
        with self.db() as db:
            db[str(coord.date)] = coord.save()

    def coordinate(self, recno):
        return self.li_data[recno]
