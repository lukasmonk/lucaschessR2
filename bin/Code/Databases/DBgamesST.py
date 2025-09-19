import sqlite3

import FasterCode

from Code import Util
from Code.Base import Game

pv_xpv = FasterCode.pv_xpv
set_fen = FasterCode.set_fen
make_move = FasterCode.make_move
get_fen = FasterCode.get_fen
get_exmoves = FasterCode.get_exmoves
fen_fenm2 = FasterCode.fen_fenm2
make_pv = FasterCode.make_pv
num_move = FasterCode.num_move
move_num = FasterCode.move_num


class RecordSTAT:
    def __init__(self):
        self.W = 0
        self.B = 0
        self.D = 0
        self.O = 0

        self.cached = False
        self.move = None
        self.ROWID = None

    def total(self):
        return self.W + self.B + self.D + self.O


class TreeSTAT:
    def __init__(self, path_file, depth=None):
        self.path_file = path_file
        self.defaultDepth = 30

        self.hinikey = Util.md5_lc("")
        self._conexion = sqlite3.connect(self.path_file)

        self.depth = self.defaultDepth if depth is None else depth
        self._check_table()

        self.cache = None
        self.cache_active = False

    def conexion(self):
        return self._conexion

    def _check_table(self):
        cursor = self._conexion.execute("pragma table_info(STATS)")
        if not cursor.fetchall():
            self._conexion.execute("PRAGMA page_size = 4096")
            self._conexion.execute("PRAGMA synchronous = NORMAL")
            sql = "CREATE TABLE STATS(HASHKEY INT8 PRIMARY KEY, W INT, B INT, D INT, O INT);"
            self._conexion.execute(sql)
            sql = "INSERT INTO STATS( HASHKEY, W, B, D, O ) VALUES( ?, ?, ?, ?, ? );"
            self._conexion.execute(sql, (self.hinikey, 0, 0, 0, 0))

            sql = "CREATE TABLE CONFIG( KEY TEXT PRIMARY KEY, VALUE TEXT );"
            self._conexion.execute(sql)

            self._conexion.commit()
        else:
            sql = "SELECT ROWID FROM STATS WHERE HASHKEY = ?"
            cursor = self._conexion.execute(sql, (self.hinikey,))
            raw = cursor.fetchone()
            if raw is None:
                sql = "INSERT INTO STATS( HASHKEY, W, B, D, O ) VALUES( ?, ?, ?, ?, ? );"
                self._conexion.execute(sql, (self.hinikey, 0, 0, 0, 0))
                self._conexion.commit()

    def close(self):
        if self._conexion:
            self._conexion.close()
            self._conexion = None

    def reset(self):
        self.close()
        Util.remove_file(self.path_file)
        self._conexion = sqlite3.connect(self.path_file)
        self._check_table()

    def read_rec(self, hkey):
        if self.cache_active:
            if hkey in self.cache:
                return self.cache[hkey]
        sql = "SELECT ROWID, W, B, D, O FROM STATS WHERE HASHKEY = ?"
        cursor = self._conexion.execute(sql, (hkey,))
        row = cursor.fetchone()
        rec = RecordSTAT()
        if row:
            rec.ROWID = row[0]
            rec.W = row[1]
            rec.B = row[2]
            rec.D = row[3]
            rec.O = row[4]
        return rec

    def write_rec(self, hkey, rec):
        if self.cache_active:
            if rec.total() > 10:
                self.cache[hkey] = rec
                return
        rowid = rec.ROWID
        if rowid is None:
            sql = "INSERT INTO STATS( HASHKEY, W, B, D, O ) VALUES( ?, ?, ?, ?, ? )"
            cursor = self._conexion.execute(sql, (hkey, rec.W, rec.B, rec.D, rec.O))
            rowid = cursor.lastrowid
        else:
            sql = "UPDATE STATS SET W=?, B=?, D=?, O=? WHERE ROWID=?"
            self._conexion.execute(sql, (rec.W, rec.B, rec.D, rec.O, rowid))
        return rowid

    def commit(self):
        self._conexion.commit()

    def add(self, hkey, w, b, d, o):
        rec = self.read_rec(hkey)
        if w:
            rec.W += w
        elif b:
            rec.B += b
        elif d:
            rec.D += d
        else:
            rec.O += o
        return self.write_rec(hkey, rec)

    def append(self, pv, result, r=+1):
        w = b = d = o = 0
        if result == "1-0":
            w += r
        elif result == "0-1":
            b += r
        elif result == "1/2-1/2":
            d += r
        else:
            o += r

        self.add(self.hinikey, w, b, d, o)
        li_pv = pv.split(" ")
        for depth, move in enumerate(li_pv):
            if depth >= self.depth:
                break
            hkey = Util.md5_lc("".join(li_pv[: depth + 1]))
            self.add(hkey, w, b, d, o)

    def massive_append_set(self, start):
        if start:
            self.cache = {}
            self.cache_active = True
        else:
            self.cache_active = False
            for hkey, rec in self.cache.items():
                self.write_rec(hkey, rec)
            self.cache = None

    def root(self):
        return self.read_rec(self.hinikey)

    def rootGames(self):
        return self.root().total()

    def children(self, pv_base, allmoves=True):
        make_pv(pv_base)
        li = get_exmoves()
        li_resp = []
        cpv = pv_base.replace(" ", "")
        for n, mv in enumerate(li):
            move = mv.move()
            hkey = Util.md5_lc(cpv + move)
            rec = self.read_rec(hkey)
            if not allmoves and rec.total() == 0:
                continue
            rec.move = move
            li_resp.append(rec)
        return li_resp

    def get_summary(self, pv_base, dic_analysis, with_figurines, allmoves=True):

        li_moves = []
        is_white = pv_base.count(" ") % 2 == 1 if pv_base else True

        li_children = self.children(pv_base, allmoves)

        tt = 0

        lipvmove = []
        for rec in li_children:
            win, draw, b, o = rec.W, rec.D, rec.B, rec.O
            t = rec.total()

            dic = {}
            pvmove = rec.move
            pv = pv_base + " " + pvmove
            pv = pv.strip()
            lipvmove.append(pvmove)
            dic["number"] = ""
            dic["pvmove"] = pvmove
            dic["pv"] = pv
            dic["analysis"] = dic_analysis.get(pvmove, None)
            dic["games"] = t
            tt += t
            dic["white"] = win
            dic["draw"] = draw
            dic["black"] = b
            dic["other"] = o
            dic["pwhite"] = win * 100.0 / t if t else 0.0
            dic["pdraw"] = draw * 100.0 / t if t else 0.0
            dic["pblack"] = b * 100.0 / t if t else 0.0
            dic["pother"] = o * 100.0 / t if t else 0.0

            dic["rec"] = rec

            li_moves.append(dic)

        if allmoves:
            for pvmove in dic_analysis:
                if pvmove not in lipvmove:
                    dic = {}
                    pv = pv_base + " " + pvmove
                    pv = pv.strip()
                    dic["pvmove"] = pvmove
                    dic["pv"] = pv
                    dic["analysis"] = dic_analysis[pvmove]
                    dic["games"] = 0
                    dic["white"] = 0
                    dic["draw"] = 0
                    dic["black"] = 0
                    dic["other"] = 0
                    dic["pwhite"] = 0.00
                    dic["pdraw"] = 0.00
                    dic["pblack"] = 0.00
                    dic["pother"] = 0.00
                    dic["rec"] = None

                    li_moves.append(dic)

        li_moves = sorted(li_moves, key=lambda dic: -dic["games"])

        tg = win = draw = lost = 0
        for dic in li_moves:
            dic["pgames"] = dic["games"] * 100.0 / tt if tt else 0.0
            dic["pdrawwhite"] = dic["pwhite"] + dic["pdraw"]
            dic["pdrawblack"] = dic["pblack"] + dic["pdraw"]
            if is_white:
                dic["win"] = dic["white"]
                dic["lost"] = dic["black"]
                dic["pwin"] = dic["pwhite"]
                dic["plost"] = dic["pblack"]
                dic["pdrawwin"] = dic["pdrawwhite"]
                dic["pdrawlost"] = dic["pdrawblack"]
            else:
                dic["lost"] = dic["white"]
                dic["win"] = dic["black"]
                dic["pdrawlost"] = dic["pdrawwhite"]
                dic["pdrawwin"] = dic["pdrawblack"]
                dic["plost"] = dic["pwhite"]
                dic["pwin"] = dic["pblack"]

            g = dic["games"]
            tg += g
            win += dic["win"]
            lost += dic["lost"]
            draw += dic["draw"]

            pvmove = dic["pvmove"]
            if pvmove:
                pv = dic["pv"]
                p = Game.Game()
                p.read_pv(pv)
                if p.num_moves():
                    move = p.last_jg()
                    num_moves = move.numMove()
                    pgn = move.pgn_figurines() if with_figurines else move.pgn_translated()
                    dic["move"] = pgn
                    dic["number"] = "%d." % num_moves
                    if not move.is_white():
                        # dic["move"] = pgn_translated.lower()
                        dic["number"] += ".."
                else:
                    dic["move"] = pvmove
                dic["game"] = p

        dic = {}
        dic["games"] = tg
        dic["win"] = win
        dic["draw"] = draw
        dic["lost"] = lost
        dic["pwin"] = win * 100.0 / tg if tg else 0.0
        dic["pdraw"] = draw * 100.0 / tg if tg else 0.0
        dic["plost"] = lost * 100.0 / tg if tg else 0.0
        dic["pdrawwin"] = (win + draw) * 100.0 / tg if tg else 0.0
        dic["pdrawlost"] = (lost + draw) * 100.0 / tg if tg else 0.0
        li_moves.append(dic)

        return li_moves
