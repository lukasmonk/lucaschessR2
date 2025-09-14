import sqlite3

from Code import Util
from Code.Databases import DBgames
from Code.Openings import OpeningsStd
from Code.SQL import UtilSQL


class DBgamesMov:
    def __init__(self, dbgames: DBgames.DBgames):
        self.dbgames = dbgames
        self.path = self.dbgames.path_file[:-5] + ".lcmv"

        self.dic_fen64_sequences = OpeningsStd.ap.dic_fen64()

    def need_generate(self):
        return not (Util.exist_file(self.path) and self.read_lastrowid_saved() > 0)

    def pending(self):
        lastrowid = self.read_lastrowid_saved()
        return self.dbgames.count_greater_rowid(lastrowid)

    def conexion(self):
        conexion = sqlite3.connect(self.path)
        conexion.row_factory = sqlite3.Row
        return conexion

    def generate(self, ws) -> bool:
        with UtilSQL.DictBig() as db:
            rowid_prev = 0
            pos_reg = 0

            last_rowid = 0

            for rowid, fen, pos, pv in self.dbgames.yield_allfens():
                if rowid != rowid_prev:
                    if rowid > last_rowid:
                        last_rowid = rowid
                    pos_reg += 1
                    if pos_reg % 100 == 0:
                        ws.pon(pos_reg)
                    rowid_prev = rowid
                if ws.is_canceled():
                    return False

                fen64 = Util.fen_fen64(fen)
                if fen64 in self.dic_fen64_sequences and pv in self.dic_fen64_sequences[fen64]:
                    continue
                li = db.get(fen64, {"G": [], "S": []})
                li["G"].append(f"{rowid}:{pos}")
                if pv not in li["S"]:
                    li["S"].append(pv)
                db[fen64] = li

            Util.remove_file(self.path)
            self.create()
            conexion = self.conexion()
            ws.put_label(_("Saving..."))
            total = len(db)
            if total > 1000:
                limit = 100
            else:
                limit = 2

            ws.set_total(len(db))
            for pos, (fen64, value) in enumerate(db.items()):
                if pos % limit == 0:
                    ws.pon(pos)
                g = value["G"]
                s = value["S"]
                t_g = sum(len(x.split(":")[0]) + 2 for x in g)
                t_s = sum(len(x) + 2 for x in s)
                if t_s * 3 < t_g:
                    data = "S" + "|".join(s)
                else:
                    data = "G" + "|".join(g)
                sql = "INSERT INTO POSITIONS( FEN64, DATA ) VALUES( ?, ? );"
                conexion.execute(sql, (fen64, data))
            conexion.commit()
            conexion.close()
            self.write_lastrowid_saved(last_rowid)
        return True

    def update(self, ws) -> bool:
        conexion = self.conexion()
        last_rowid = self.read_lastrowid_saved()
        rowid_prev = 0
        pos_reg = 0
        for rowid, fen, pos, pv in self.dbgames.yield_allfens(last_rowid):
            if rowid != rowid_prev:
                if rowid > last_rowid:
                    last_rowid = rowid
                rowid_prev = rowid
                pos_reg += 1
                ws.pon(pos_reg)
                if ws.is_canceled():
                    break

            fen64 = Util.fen_fen64(fen)
            if fen64 in self.dic_fen64_sequences and pv in self.dic_fen64_sequences[fen64]:
                continue

            sql = "SELECT DATA FROM POSITIONS WHERE FEN64=?;"
            cursor = conexion.execute(sql, (fen64,))
            row = cursor.fetchone()
            if row:
                data = row[0]
                if data.startswith("G"):
                    row = f"|{rowid}:{pos}"
                    if row not in data:
                        data += row
                    else:
                        continue
                else:
                    if pv not in data:
                        data += f"|{pv}"
                    else:
                        continue
                sql = "UPDATE POSITIONS SET DATA=? WHERE FEN64=?;"
                li_datos = [data, fen64]
            else:
                data = f"G{rowid}:{pos}"
                sql = "INSERT INTO POSITIONS( FEN64, DATA ) VALUES( ?, ? );"
                li_datos = [fen64, data]
            conexion.execute(sql, li_datos)

        conexion.commit()
        conexion.close()
        self.write_lastrowid_saved(last_rowid)
        return not ws.is_canceled()

    def filter(self, fen):
        fen64 = Util.fen_fen64(fen)
        conexion = self.conexion()
        sql = "SELECT DATA FROM POSITIONS WHERE FEN64=?;"
        cursor = conexion.execute(sql, (fen64,))
        row = cursor.fetchone()
        conexion.close()
        if row is None:
            if fen64 in self.dic_fen64_sequences:
                return self.dic_fen64_sequences[fen64], []
            return None
        data = row[0]
        if data.startswith("G"):
            li_dt = [dt.split(":") for dt in data[1:].split("|")]
            li = [(int(x[0]), int(x[1])) for x in li_dt]
            return self.dic_fen64_sequences.get(fen64), li

        li = data[1:].split("|")
        if self.dic_fen64_sequences.get(fen64):
            li.extend(self.dic_fen64_sequences.get(fen64))
        return li, []

    def create(self):
        conexion = self.conexion()
        for sql in (
                "CREATE TABLE POSITIONS(FEN64 VARCHAR PRIMARY KEY,DATA VARCHAR);",
                "PRAGMA page_size = 4096;",
                "PRAGMA synchronous = OFF;",
                "PRAGMA cache_size = 10000;",
                "PRAGMA journal_mode = MEMORY;",
        ):
            conexion.execute(sql)
        conexion.commit()
        conexion.close()

    def seek_fen(self, fen):
        fen64 = Util.fen_fen64(fen)

        li_rowids = []
        if fen64 in self.dic_fen64_sequences:
            li_sequences = self.dic_fen64_sequences[fen64]
        else:
            li_sequences = []

        sql = "SELECT GAMES, SEQUENCES FROM POSITIONS WHERE FEN64 = ?"

        conexion = sqlite3.connect(self.path)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.execute(sql, (fen64,))
        li = cursor.fetchall()
        if li:
            for games, sequences in li:
                if games:
                    li_rowids.extend([int(rowid) for rowid in games.split(",")])
                if sequences:
                    li_sequences.extend([xpv for xpv in sequences.split(",")])

        conexion.close()
        return li_rowids, li_sequences

    def save_config(self, key, valor):
        with UtilSQL.DictRawSQL(self.path, "Config") as dbconf:
            dbconf[key] = valor

    def read_config(self, key, default=None):
        with UtilSQL.DictRawSQL(self.path, "Config") as dbconf:
            return dbconf.get(key, default)

    def write_lastrowid_saved(self, last):
        self.save_config("LAST_ROWID_SAVED", last)

    def read_lastrowid_saved(self):
        return self.read_config("LAST_ROWID_SAVED", 0)
