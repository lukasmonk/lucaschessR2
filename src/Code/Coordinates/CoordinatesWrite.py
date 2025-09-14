import datetime
import random

import Code
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


class CoordinatesWrite:
    date: datetime.datetime
    st_done: set
    errors: int
    ms_time: int
    is_record: bool

    def __init__(self):
        self.date = datetime.datetime.now()
        self.st_done = set()
        self.ms_time = 0
        self.errors = 0
        self.is_record = False

    def next(self, pieces):
        chess_squares = {f"{file}{rank}" for file in 'abcdefgh' for rank in '12345678'}
        resto = chess_squares - self.st_done
        return set(random.sample(resto, pieces))

    def save(self):
        dic = {"date": self.date, "st_done": self.st_done, "ms_time": self.ms_time,
               "errors": self.errors}
        return dic

    def restore(self, dic):
        self.date = dic["date"]
        self.st_done = dic["st_done"]
        self.ms_time = dic["ms_time"]
        self.errors = dic["errors"]

    def pending(self):
        return len(self.st_done) < 64

    def starting(self):
        return len(self.st_done) == 0

    def finished(self):
        return len(self.st_done) == 64

    def str_done(self, pieces):
        if self.pending():
            return f'{len(self.st_done) // pieces}/{64 // pieces}'
        else:
            return _("Ended")

    def str_done_info(self, pieces):
        return f'{len(self.st_done) // pieces}/{64 // pieces}'

    def str_time(self, add_seconds=0):
        seconds = self.ms_time // 1000 + add_seconds
        return f"{seconds:d}\""

    def add_time(self, ms):
        self.ms_time += ms

    def add_error(self):
        self.errors += 1

    def add_done(self, st):
        self.st_done.update(st)


class DBCoordinatesWrite:
    side: bool
    pieces: int
    table: str
    li_data: list
    li_dates: list

    def __init__(self, pieces, side):
        self.side = side
        self.pieces = pieces
        self.path = Code.configuration.file_coordinates_write()
        self.table = f"{'W' if side == WHITE else 'B'}{pieces}"
        self.refresh()

    def refresh(self):
        with self.db() as db:
            li_dates = db.keys(True, True)
            dic_data = db.as_dictionary()
            self.li_data = []
            coord_record = None
            for date in li_dates:
                coord = CoordinatesWrite()
                coord.restore(dic_data[date])
                if coord.finished():
                    if coord_record is None:
                        coord_record = coord
                    elif coord.errors < coord_record.errors:
                        coord_record = coord
                    elif coord.errors == coord_record.errors:
                        if coord.ms_time < coord_record.ms_time:
                            coord_record = coord
                self.li_data.append(coord)
            if coord_record:
                coord_record.is_record = True

    def db(self):
        return UtilSQL.DictSQL(self.path, tabla=self.table)

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

    def save(self, coord: CoordinatesWrite):
        with self.db() as db:
            db[str(coord.date)] = coord.save()

    def coordinate(self, recno) -> CoordinatesWrite:
        return self.li_data[recno] if recno < len(self.li_data) else None

    def pending(self):
        if len(self.li_data) == 0:
            return False
        return self.li_data[0].pending()
