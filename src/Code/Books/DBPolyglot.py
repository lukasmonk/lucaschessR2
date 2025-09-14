import os
import shutil
import sqlite3

import FasterCode

import Code
from Code import Util
from Code.QT import QTUtil2
from Code.SQL import UtilSQL


class DBPolyglot:
    def __init__(self, path):
        self.path = path
        created = os.path.isfile(path)
        self.conexion = sqlite3.connect(path)
        if not created:
            self.conexion.execute(
                "CREATE TABLE IF NOT EXISTS BOOK( CKEY TEXT, MOVE INT, WEIGHT INT, SCORE INT, DEPTH INT, LEARN INT);"
            )
            self.conexion.execute("CREATE INDEX IF NOT EXISTS CKEY_INDEX ON BOOK( CKEY );")
            self.import_previous()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.conexion:
            self.conexion.commit()
            self.conexion.close()
            self.conexion = None

    def insert_entry(self, entry):
        sql = "INSERT INTO BOOK( CKEY, MOVE, WEIGHT, SCORE, DEPTH, LEARN ) VALUES( ?, ?, ?, ?, ?, ? );"
        cursor = self.conexion.execute(
            sql, (FasterCode.int_str(entry.key), entry.move, entry.weight, entry.score, entry.depth, entry.learn)
        )
        return cursor.lastrowid

    def update_entry(self, rowid, entry):
        sql = "UPDATE BOOK SET WEIGHT=?, SCORE=?, DEPTH=?, LEARN=? WHERE ROWID=?"
        self.conexion.execute(sql, (entry.weight, entry.score, entry.depth, entry.learn, rowid))

    def replace_entry(self, entry, collisions):
        sql = "SELECT ROWID, WEIGHT, SCORE, DEPTH, LEARN FROM BOOK WHERE CKEY=? AND MOVE=?"
        ckey = FasterCode.int_str(entry.key)
        cursor = self.conexion.execute(sql, (ckey, entry.move))
        row = cursor.fetchone()
        if row:
            rowid, weight, score, depth, learn = row
            if collisions == "add":
                entry.weight += weight
                entry.score += score
                entry.depth += depth
                entry.learn += learn
            elif collisions == "discard":
                return
            else:
                if entry.weight == 0:
                    self.delete(rowid)
                    return
            self.update_entry(rowid, entry)
        else:
            self.insert_entry(entry)

    def delete(self, rowid):
        sql = "DELETE FROM BOOK WHERE rowid = ?"
        self.conexion.execute(sql, (rowid,))

    def save_entry(self, rowid, entry):
        if rowid == 0:
            rowid = self.insert_entry(entry)
        else:
            if entry.weight == 0:
                self.delete(rowid)
                rowid = 0
            else:
                self.update_entry(rowid, entry)
        self.conexion.commit()

        return rowid

    def import_previous(self):
        old_folder = Util.opj(Code.configuration.folder_polyglots_factory(), "old")
        mkbin_path = self.path[:-5] + "mkbin"
        if os.path.isfile(mkbin_path):
            pol_mkbin = FasterCode.Polyglot(mkbin_path)
            for entry in pol_mkbin:
                self.insert_entry(entry)
            self.conexion.commit()
            pol_mkbin.close()
            Util.create_folder(old_folder)
            shutil.move(mkbin_path, old_folder)

        dbbin_path = self.path[:-5] + "dbbin"
        if os.path.isfile(dbbin_path):
            db_ant = UtilSQL.DictSQL(dbbin_path)
            dic = db_ant.as_dictionary()
            db_ant.close()
            for key_str, dic_moves in dic.items():
                for move, entry in dic_moves.items():
                    sql = "SELECT ROWID FROM BOOK WHERE CKEY=? AND MOVE=?"
                    cursor = self.conexion.execute(sql, (key_str, move))
                    row = cursor.fetchone()
                    if row:
                        rowid = row[0]
                        self.update_entry(rowid, entry)
                    else:
                        self.insert_entry(entry)
            self.conexion.commit()
            Util.create_folder(old_folder)
            shutil.move(dbbin_path, old_folder)

    def __len__(self):
        sql = "SELECT COUNT(*) FROM BOOK"
        cursor = self.conexion.execute(sql)
        row = cursor.fetchone()
        return row[0] if row else 0

    def get_entries(self, fen):
        key = FasterCode.hash_polyglot8(fen)
        ckey = FasterCode.int_str(key)
        sql = "SELECT ROWID, MOVE, WEIGHT, SCORE, DEPTH, LEARN FROM BOOK WHERE CKEY=?"
        cursor = self.conexion.execute(sql, (ckey,))
        rows = cursor.fetchall()
        li_resp = []
        if rows:
            for row in rows:
                entry = FasterCode.Entry()
                entry.key = key
                entry.rowid, entry.move, entry.weight, entry.score, entry.depth, entry.learn = row
                li_resp.append(entry)
        return li_resp

    def get_all(self):
        sql = "SELECT DISTINCT length(CKEY) FROM BOOK"
        cursor = self.conexion.execute(sql)
        li_length = [int(x[0]) for x in cursor.fetchall()]
        li_length.sort()

        sql = "SELECT CKEY, MOVE, WEIGHT, SCORE, DEPTH, LEARN FROM BOOK WHERE LENGTH(CKEY) = ? ORDER BY CKEY"

        for length in li_length:
            cursor = self.conexion.execute(sql, (length,))
            while True:
                row = cursor.fetchone()
                if not row:
                    break
                entry = FasterCode.Entry()
                ckey, entry.move, entry.weight, entry.score, entry.depth, entry.learn = row
                entry.key = FasterCode.str_int(ckey)
                yield entry

        yield None

    def commit(self):
        self.conexion.commit()


class IndexPolyglot:
    def __init__(self):
        self.index = Code.configuration.file_index_polyglots()
        self.folder = Code.configuration.folder_polyglots_factory()

        if not os.path.isfile(self.index):
            self.import_olds()

        self._list = Util.restore_pickle(self.index, [])

        self.update_soft()

    def list(self):
        return self._list

    def import_olds(self):
        owner = Code.procesador.main_window
        um = QTUtil2.working(owner)
        st_antiguos = set()  # para que haga de cada mkbin y dbbin uno solo
        for entry_file in os.scandir(self.folder):
            if entry_file.name.lower().endswith(".dbbin") or entry_file.name.lower().endswith(".mkbin"):  # antiguo
                st_antiguos.add(entry_file.path[:-5])
        for st_antiguo in st_antiguos:
            with DBPolyglot(st_antiguo + "lcbin"):
                pass
        um.final()

    def update_soft(self):
        # changed = False
        li_resp = []
        for entry_file in os.scandir(self.folder):
            if not (entry_file.is_file()) or not entry_file.name.endswith("lcbin"):
                continue
            ok = False
            for dic in self._list:
                if dic["FILENAME"] == entry_file.name:
                    if dic["MTIME"] != entry_file.stat().st_mtime:
                        with DBPolyglot(entry_file.path) as db:
                            dic["MTIME"] = entry_file.stat().st_mtime
                            dic["SIZE"] = len(db)
                    li_resp.append(dic)
                    ok = True
            if not ok:
                with DBPolyglot(entry_file.path) as db:
                    d = {"FILENAME": entry_file.name, "MTIME": os.stat(entry_file.path).st_mtime, "SIZE": len(db)}
                    li_resp.append(d)

        li_resp.sort(key=lambda x: x["MTIME"], reverse=True)
        Util.save_pickle(self.index, li_resp)
        self._list = li_resp

        return self._list

    def update_hard(self, owner):
        um = QTUtil2.working(owner)
        li = []
        for entry_file in os.scandir(self.folder):
            if not entry_file.is_file():
                continue
            if entry_file.name.endswith(".lcbin"):
                with DBPolyglot(entry_file.path) as db:
                    d = {"FILENAME": entry_file.name, "MTIME": entry_file.stat().st_mtime, "SIZE": len(db)}
                    li.append(d)
        li.sort(key=lambda x: x["MTIME"], reverse=True)
        Util.save_pickle(self.index, li)
        um.final()
        self._list = li
        return self._list
