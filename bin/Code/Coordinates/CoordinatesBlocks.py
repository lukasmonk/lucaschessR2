import datetime
import random

from Code.Base.Constantes import WHITE, BLACK
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


class CoordinatesBlocks:
    date_ini: datetime.datetime
    date_end: [datetime.datetime, None]
    min_score: int
    tries: int
    current_block: int
    current_try_in_block: int
    current_max_in_block: int
    base_tries: int = 1
    gen_try: GenTry

    def __init__(self):
        self.date_ini = datetime.datetime.now()
        self.date_end = None
        self.min_score = 0
        self.min_score_white = 0
        self.min_score_black = 0
        self.tries = 0
        self.current_block = 0
        self.current_try_in_block = 0
        self.current_max_in_block = 0
        self.li_blocks = self.lista_blocks

    def num_blocks(self):
        return len(self.li_blocks)

    @property
    def lista_blocks(self):
        li = (
            ("a1", "d4"),
            ("e1", "h4"),
            ("a5", "d8"),
            ("e5", "h8"),
            ("a1", "d8"),
            ("e1", "h8"),
            ("a1", "h4"),
            ("a5", "h8"),
            ("a1", "h8"),
        )
        li_resp = []
        for xfrom, xto in li:
            for side in (WHITE, BLACK):
                li_resp.append((side, xfrom, xto))
        return li_resp

    def next(self):
        return self.gen_try.next()

    def new_try(self):
        side, xfrom, xto = self.li_blocks[self.current_block]
        self.gen_try = GenTry(xfrom, xto)
        self.min_score = self.min_score_white if side == WHITE else self.min_score_black
        return side == WHITE

    def new_done(self, num_success):
        side = self.li_blocks[self.current_block][0]
        if num_success > self.current_max_in_block:
            self.current_max_in_block = num_success
            if num_success > self.min_score:
                self.min_score = num_success
                if side == WHITE:
                    self.min_score_white = num_success
                else:
                    self.min_score_black = num_success
        self.tries += 1
        self.current_try_in_block += 1
        if self.current_try_in_block >= self.base_tries:
            minimo = self.min_score if self.min_score else 1
            if self.current_max_in_block >= minimo:
                self.current_block += 1
                self.current_try_in_block = 0
                self.current_max_in_block = 0
                if self.current_block >= self.num_blocks():
                    self.date_end = datetime.datetime.now()
                    return True, True
                return True, False
        return False, False

    def is_ended(self):
        return self.current_block >= self.num_blocks()

    def min_score_side(self):
        side = self.li_blocks[self.current_block][0]
        resp = self.min_score_white if side == WHITE else self.min_score_black
        return max(resp, 1)

    def current_side(self):
        return self.li_blocks[self.current_block][0]

    def save(self):
        dic = {
            "date_ini": self.date_ini,
            "date_end": self.date_end,
            "tries": self.tries,
            "min_score": self.min_score,
            "min_score_white": self.min_score_white,
            "min_score_black": self.min_score_black,
            "current_block": self.current_block,
            "current_try_in_block": self.current_try_in_block,
            "current_max_in_block": self.current_max_in_block,
        }
        return dic

    def restore(self, dic):
        self.date_ini = dic["date_ini"]
        self.date_end = dic["date_end"]
        self.min_score = dic["min_score"]
        self.min_score_white = dic.get("min_score_white", self.min_score)
        self.min_score_black = dic.get("min_score_black", self.min_score)
        self.current_block = dic["current_block"]
        self.current_try_in_block = dic["current_try_in_block"]
        self.current_max_in_block = dic["current_max_in_block"]
        self.tries = dic["tries"]
        if 0 <= self.current_block < len(self.li_blocks):
            side = self.li_blocks[self.current_block][0]
            self.min_score = self.min_score_white if side == WHITE else self.min_score_black


class DBCoordinatesBlocks:
    def __init__(self, path):
        self.path = path
        self.refresh()

    def refresh(self):
        with self.db() as db:
            li_dates = db.keys(True, True)
            dic_data = db.as_dictionary()
            self.li_data = []
            for date in li_dates:
                coord = CoordinatesBlocks()
                coord.restore(dic_data[date])
                self.li_data.append(coord)

    def db(self):
        return UtilSQL.DictSQL(self.path, tabla="blocks")

    def db_config(self):
        return UtilSQL.DictSQL(self.path, tabla="config")

    def __len__(self):
        return len(self.li_data)

    def remove(self, li_recno):
        with self.db() as db:
            li_recno.sort(reverse=True)
            for recno in li_recno:
                coord = self.li_data[recno]
                del db[str(coord.date_ini)]
                del self.li_data[recno]
            db.pack()

    def save(self, coord):
        with self.db() as db:
            db[str(coord.date_ini)] = coord.save()

    def coordinate(self, recno):
        return self.li_data[recno]

    def last_coordinate(self):
        if self.li_data:
            last = self.li_data[0]
            if not last.is_ended():
                return last
        coord = CoordinatesBlocks()
        return coord
