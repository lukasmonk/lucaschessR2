import datetime

from Code import Util
from Code.Base import Game
from Code.SQL import UtilSQL


class CountCapture:
    xid: str
    date: datetime.datetime
    game: Game.Game
    current_posmove: int
    current_depth: int
    tries: list
    is_captures: bool

    def __init__(self, is_captures):
        self.date = datetime.datetime.now()
        self.xid = Util.huella()
        self.game = Game.Game()
        self.current_posmove = 0
        self.current_depth = 0
        self.tries = []  # pos,depth,success,time
        self.is_captures = is_captures

    def is_finished(self):
        total = len(self.game) + 1
        # if self.is_captures:
        #     total += 1
        return (self.current_posmove + self.current_depth) >= total

    def save(self):
        dic = {
            "date": self.date,
            "xid": self.xid,
            "game": self.game.save(),
            "current_posmove": self.current_posmove,
            "current_depth": self.current_depth,
            "tries": self.tries,
        }
        return dic

    def restore(self, dic):
        self.date = dic["date"]
        self.xid = dic["xid"]
        self.game.restore(dic["game"])
        self.current_posmove = dic["current_posmove"]
        self.current_depth = dic["current_depth"]
        self.tries = dic["tries"]

    def success(self):
        ntries = 0
        for pos, depth, success, time in self.tries:
            if pos < self.current_posmove:
                ntries += 1
        return (self.current_posmove - 1) / ntries if ntries > 0 else 0.0

    def label_success(self) -> str:
        ntries = len(self.tries)
        if ntries == 0:
            return ""
        nok = 0
        for posmove, depth, ok, tiempo in self.tries:
            if ok:
                nok += 1
        porc = min(nok * 100.0 / ntries, 100.0)
        return "%.01f%%" % porc

    def label_time(self) -> str:
        tm = 0.0
        for posmove, depth, ok, tiempo in self.tries:
            tm += tiempo
        total = self.current_posmove + self.current_depth
        media = tm / total if total else 0.0
        return '%.01f"/%.01f"' % (media, tm)

    def label_time_used(self) -> str:
        tm = 0.0
        for posmove, depth, ok, tiempo in self.tries:
            tm += tiempo
        return '%.01f"' % tm

    def label_time_avg(self) -> str:
        tm = 0.0
        for posmove, depth, ok, tiempo in self.tries:
            tm += tiempo
        total = self.current_posmove + self.current_depth
        media = tm / total if total else 0.0
        return '%.01f"' % media

    def copy(self):
        capt_copy = CountCapture(self.is_captures)
        capt_copy.game = self.game.copia()
        capt_copy.current_posmove = 0
        capt_copy.current_depth = 0
        capt_copy.tries = []
        return capt_copy


class DBCountCapture:
    def __init__(self, path, is_captures):
        self.path = path

        with self.db() as db:
            li_dates = db.keys(True, True)
            dic_data = db.as_dictionary()
            self.li_data = []
            for date in li_dates:
                count_capture = CountCapture(is_captures)
                count_capture.restore(dic_data[date])
                self.li_data.append(count_capture)

    def db(self):
        return UtilSQL.DictSQL(self.path)

    def __len__(self):
        return len(self.li_data)

    def last(self):
        if len(self.li_data) > 0:
            return self.li_data[0]
        return None

    def new_count_capture(self, count_capture: CountCapture):
        with self.db() as db:
            db[str(count_capture.date)] = count_capture.save()
            self.li_data.insert(0, count_capture)
            db.pack()

    def remove_count_captures(self, li_recno):
        with self.db() as db:
            li_recno.sort(reverse=True)
            for recno in li_recno:
                count_capture = self.li_data[recno]
                del db[str(count_capture.date)]
                del self.li_data[recno]
            db.pack()

    def change_count_capture(self, count_capture):
        with self.db() as db:
            db[str(count_capture.date)] = count_capture.save()

    def count_capture(self, recno):
        return self.li_data[recno]
