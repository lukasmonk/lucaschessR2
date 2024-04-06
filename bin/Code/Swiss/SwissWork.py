import os.path
import random
import time

import psutil

from Code.SQL import UtilSQL
from Code.Swiss import Swiss


class SwissesWorkDB:
    def __init__(self, path: str, table: str):
        self.path = path
        self.table = table
        self.db = None

    def __enter__(self):
        tries = 5
        while tries:
            tries -= 1
            try:
                self.db = UtilSQL.DictSQLRawExclusive(self.path, tabla=self.table)
                break
            except:
                time.sleep(random.randint(30, 100) / 100)
        return self.db

    def __exit__(self, xtype, value, traceback):
        tries = 3
        while tries:
            tries -= 1
            try:
                self.db.close()
                break
            except:
                time.sleep(random.randint(30, 100) / 100)
        self.db = None


class SwissWork:
    def __init__(self, swiss: Swiss.Swiss):
        self.path = swiss.path() + ".work"
        self.nom_swiss = swiss.name()
        self.swiss = swiss
        self.season = swiss.read_season()

    def get_journey_season(self):
        with self.db_work("CONFIG") as dbc:
            return dbc["JOURNEY"], dbc["NUM_SEASON"]

    def db_work(self, table):
        return SwissesWorkDB(self.path, table)

    def put_swiss(
            self,
    ):
        season = self.swiss.read_season()

        with self.db_work("CONFIG") as dbc:
            dbc["NUM_SEASON"] = self.swiss.current_num_season
            dbc["JOURNEY"] = season.get_last_journey()

        with self.db_work("MATCHS") as dbm:
            dbm.zap()
            for xmatch in season.get_all_matches():
                if xmatch.is_engine_vs_engine(self.swiss):
                    dbm[xmatch.xid] = xmatch

        with self.db_work("MATCHS_WORKING") as dbw:
            dbw.zap()

    def num_pending_matches(self):
        with self.db_work("MATCHS") as db:
            return len(db) + self.num_working_matches()

    def num_working_matches(self):
        with self.db_work("MATCHS_WORKING") as dbw:
            return len(dbw)

    def get_opponent(self, xid):
        return self.swiss.opponent_by_xid(xid)

    def control_zombies(self):
        with self.db_work("MATCHS_WORKING") as dbw:
            dic = dbw.as_dictionary()
        zombies = 0
        for xid, xmatch in dic.items():
            pid = xmatch.pid_tmp
            if not psutil.pid_exists(pid):
                self.cancel_match(xid)
                zombies += 1
        return zombies

    def get_other_match(self):
        self.control_zombies()
        with self.db_work("MATCHS") as db:
            li = db.keys()
            if len(li) == 0:
                return None

            random.shuffle(li)

            xid = li[0]
            xmatch = db[xid]
            if not xmatch:
                return None
            del db[xid]

            with self.db_work("MATCHS_WORKING") as dbw:
                xmatch.pid_tmp = os.getpid()
                dbw[xmatch.xid] = xmatch
            return xmatch

    def put_match_done(self, xmatch, game):
        with self.db_work("MATCHS_WORKING") as dbw:
            del dbw[xmatch.xid]
        self.season.put_match_done(xmatch, game)

    def cancel_match(self, xid):
        with self.db_work("MATCHS_WORKING") as dbw:
            xmatch = dbw[xid]
            if not xmatch:
                return
            del dbw[xid]
        with self.db_work("MATCHS") as db:
            db[xmatch.xid] = xmatch

    def add_match_zombie(self, xmatch):
        with self.db_work("MATCHS") as db:
            db[xmatch.xid] = xmatch

    def get_journey_match(self, xmatch):
        return self.season.get_last_journey()
