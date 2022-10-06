import os.path
import random
import time

import psutil

from Code.Leagues import Leagues
from Code.SQL import UtilSQL


class Lock:
    def __init__(self, path):
        self.path = path
        self.key = "LAST_LOCK"

    def get(self):
        with UtilSQL.DictRawSQL(self.path, "CONFIG") as db:
            try:
                return db.get(self.key)
            except TypeError:
                return None

    def put(self):
        with UtilSQL.DictRawSQL(self.path, "CONFIG") as db:
            db[self.key] = time.time()

    def __enter__(self):
        last_lock = self.get()
        while last_lock and ((time.time() - last_lock) < 10):
            n = 0
            while n < 4:
                try:
                    last_lock = self.get()
                    break
                except:
                    time.sleep(random.randint(50, 100) / 100)
                    n += 1
        n = 0
        while n < 4:
            try:
                self.put()
                break
            except:
                time.sleep(random.randint(50, 100) / 100)
                n += 1
        return self

    def __exit__(self, xtype, value, traceback):
        with UtilSQL.DictRawSQL(self.path, "CONFIG") as db:
            db.__delitem__(self.key)


class LeaguesWork:
    def __init__(self, league: Leagues.League):
        self.path = league.path() + ".work"
        self.nom_league = league.name()
        self.league = league
        self.season = league.read_season()

    def get_journey_season(self):
        with UtilSQL.DictRawSQL(self.path, "CONFIG") as dbc:
            return dbc["JOURNEY"], dbc["NUM_SEASON"]

    def put_league(self, ):
        season = self.league.read_season()

        with UtilSQL.DictRawSQL(self.path, "CONFIG") as dbc:
            dbc["NUM_SEASON"] = self.league.current_num_season
            dbc["JOURNEY"] = season.get_current_journey()

        with UtilSQL.DictRawSQL(self.path, "MATCHS") as dbm:
            dbm.zap()
            for xmatch in season.get_all_matches():
                if xmatch.is_engine_vs_engine(self.league):
                    dbm[xmatch.xid] = xmatch

        with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
            dbw.zap()

    def num_pending_matches(self):
        with UtilSQL.DictRawSQL(self.path, "MATCHS") as db:
            return len(db) + self.num_working_matches()

    def num_working_matches(self):
        with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
            return len(dbw)

    def get_opponent(self, xid):
        return self.league.opponent_by_xid(xid)

    def control_zombies(self):
        with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
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
        with Lock(self.path), UtilSQL.DictRawSQL(self.path, "MATCHS") as db:
            li = db.keys()
            if len(li) == 0:
                return None

            random.shuffle(li)

            xid = li[0]
            xmatch = db[xid]
            del db[xid]

            with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
                xmatch.pid_tmp = os.getpid()
                dbw[xmatch.xid] = xmatch
            return xmatch

    def put_match_done(self, xmatch, game):
        with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
            del dbw[xmatch.xid]
        self.season.put_match_done(xmatch, game)

    def cancel_match(self, xid):
        with UtilSQL.DictRawSQL(self.path, "MATCHS_WORKING") as dbw:
            xmatch = dbw[xid]
            if not xmatch:
                return
            del dbw[xid]
        with UtilSQL.DictRawSQL(self.path, "MATCHS") as db:
            db[xmatch.xid] = xmatch
