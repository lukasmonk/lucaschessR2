import pickle
import random
import sqlite3
import threading

import psutil
import sortedcontainers

import Code
from Code import Util


class DictSQL(object):
    def __init__(self, path_db, tabla="Data", max_cache=2048):
        self.tabla = tabla
        self.max_cache = max_cache
        self.cache = {}

        self.conexion = sqlite3.connect(path_db)

        self.conexion.execute("CREATE TABLE IF NOT EXISTS %s( KEY TEXT PRIMARY KEY, VALUE BLOB );" % tabla)

        cursor = self.conexion.execute("SELECT KEY FROM %s" % self.tabla)
        self.li_keys = [reg[0] for reg in cursor.fetchall()]

        self.normal_save_mode = True
        self.pending_commit = False

        self.li_breplaces_pickle = []

    def reset(self):
        cursor = self.conexion.execute("SELECT KEY FROM %s" % self.tabla)
        self.li_keys = [reg[0] for reg in cursor.fetchall()]

    def set_faster_mode(self):
        self.normal_save_mode = False

    def set_normal_mode(self):
        if self.pending_commit:
            self.conexion.commit()
        self.normal_save_mode = True

    def add_cache(self, key, obj):
        if self.max_cache:
            if len(self.cache) > self.max_cache:
                lik = list(self.cache.keys())
                for x in lik[: self.max_cache // 2]:
                    del self.cache[x]
            self.cache[key] = obj

    def __contains__(self, key):
        return key in self.li_keys

    def __setitem__(self, key, obj):
        if not self.conexion:
            return
        dato = pickle.dumps(obj)
        si_ya_esta = key in self.li_keys
        if si_ya_esta:
            sql = "UPDATE %s SET VALUE=? WHERE KEY = ?" % self.tabla
        else:
            sql = "INSERT INTO %s (VALUE,KEY) values(?,?)" % self.tabla
            self.li_keys.append(key)
        self.conexion.execute(sql, (memoryview(dato), key))

        self.add_cache(key, obj)
        if self.normal_save_mode:
            self.conexion.commit()
        elif not self.pending_commit:
            self.pending_commit = True

    def wrong_pickle(self, bwrong, bcorrect):
        self.li_breplaces_pickle.append((bwrong, bcorrect))

    def __getitem__(self, key):
        if key in self.li_keys:
            if key in self.cache:
                return self.cache[key]

            sql = "SELECT VALUE FROM %s WHERE KEY= ?" % self.tabla
            row = self.conexion.execute(sql, (key,)).fetchone()
            try:
                obj = pickle.loads(row[0])
            except AttributeError:
                if self.li_breplaces_pickle:
                    btxt = row[0]
                    for btxt_wrong, btxt_correct in self.li_breplaces_pickle:
                        btxt = btxt.replace(btxt_wrong, btxt_correct)
                    obj = pickle.loads(btxt)
                    self.__setitem__(key, obj)
                else:
                    obj = None

            self.add_cache(key, obj)
            return obj
        return None

    def __delitem__(self, key):
        if key in self.li_keys:
            self.li_keys.remove(key)
            if key in self.cache:
                del self.cache[key]
            sql = "DELETE FROM %s WHERE KEY= ?" % self.tabla
            self.conexion.execute(sql, (key,))
            if self.normal_save_mode:
                self.conexion.commit()
            else:
                self.pending_commit = True

    def __len__(self):
        return len(self.li_keys)

    def is_closed(self):
        return self.conexion is None

    def close(self):
        if self.conexion:
            if self.pending_commit:
                self.conexion.commit()
            self.conexion.close()
            self.conexion = None

    def keys(self, si_ordenados=False, si_reverse=False):
        return sorted(self.li_keys, reverse=si_reverse) if si_ordenados else self.li_keys

    def get(self, key, default=None):
        key = str(key)
        if key in self.li_keys:
            return self.__getitem__(key)
        else:
            return default

    def as_dictionary(self):
        sql = "SELECT KEY,VALUE FROM %s" % self.tabla
        cursor = self.conexion.execute(sql)
        dic = {}
        for key, dato in cursor.fetchall():
            dic[key] = pickle.loads(dato)
        return dic

    def pack(self):
        self.conexion.execute("VACUUM")
        self.conexion.commit()

    def zap(self):
        self.conexion.execute("DELETE FROM %s" % self.tabla)
        self.conexion.commit()
        self.conexion.execute("VACUUM")
        self.conexion.commit()
        self.cache = {}
        self.li_keys = []

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()

    def copy_from(self, dbdict):
        mode = self.normal_save_mode
        self.set_faster_mode()
        for key in dbdict.keys():
            self[key] = dbdict[key]
        self.conexion.commit()
        self.pending_commit = False
        self.normal_save_mode = mode


class DictSQLRawExclusive(object):
    GET_ALL = 1
    GET_ONE = 2
    GET_NONE = 0

    def __init__(self, path_db, tabla="Data"):
        self.tabla = tabla
        self.conexion = sqlite3.connect(path_db, isolation_level="EXCLUSIVE")

        self.conexion.execute("CREATE TABLE IF NOT EXISTS %s( KEY TEXT PRIMARY KEY, VALUE BLOB );" % tabla)

        cursor = self.conexion.execute("SELECT KEY FROM %s" % self.tabla)
        self.li_keys = [reg[0] for reg in cursor.fetchall()]

    def execute(self, sql, args=None, is_all=None, commit=False):
        tries = 10
        while tries:
            try:
                if args:
                    cursor = self.conexion.execute(sql, args)
                else:
                    cursor = self.conexion.execute(sql)
                if is_all == self.GET_ALL:
                    return cursor.fetchall()
                elif is_all == self.GET_ONE:
                    return cursor.fetchone()
                if commit:
                    self.conexion.commit()
                return

            except sqlite3.OperationalError:
                tries -= 1

    def exist(self, key):
        sql = "SELECT VALUE FROM %s WHERE KEY= ?" % self.tabla
        row = self.execute(sql, (key,), self.GET_ONE)
        return row is not None

    def __contains__(self, key):
        return self.exist(key)

    def __setitem__(self, key, obj):
        if not self.conexion:
            return
        if self.exist(key):
            sql = "UPDATE %s SET VALUE=? WHERE KEY = ?" % self.tabla
        else:
            sql = "INSERT INTO %s (VALUE,KEY) values(?,?)" % self.tabla
        dato = pickle.dumps(obj)
        self.execute(sql, (memoryview(dato), key), commit=True)

    def __getitem__(self, key):
        if self.exist(key):
            sql = "SELECT VALUE FROM %s WHERE KEY= ?" % self.tabla

            row = self.execute(sql, (key,), self.GET_ONE)
            if row[0] is not None:
                return pickle.loads(row[0])
        return None

    def __delitem__(self, key):
        sql = "DELETE FROM %s WHERE KEY= ?" % self.tabla
        self.execute(sql, (key,), commit=True)

    def __len__(self):
        sql = "SELECT COUNT(*) FROM %s" % self.tabla
        row = self.execute(sql, is_all=self.GET_ONE)
        return row[0]

    def close(self):
        try:
            if self.conexion:
                self.conexion.close()
        except:
            pass
        self.conexion = None

    def get(self, key, default=None):
        key = str(key)
        value = self.__getitem__(key)
        if value is None:
            value = default
        return value

    def as_dictionary(self):
        sql = "SELECT KEY,VALUE FROM %s" % self.tabla
        li_all = self.execute(sql, is_all=self.GET_ALL)
        dic = {}
        if li_all:
            for key, dato in li_all:
                dic[key] = pickle.loads(dato)
        return dic

    def keys(self):
        sql = "SELECT KEY FROM %s" % self.tabla
        li_all = self.execute(sql, is_all=self.GET_ALL)
        return [row[0] for row in li_all]

    def zap(self):
        self.execute("DELETE FROM %s" % self.tabla, commit=True)
        self.execute("VACUUM", commit=True)

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()


class DictObjSQL(DictSQL):
    def __init__(self, path_db, class_storage, tabla="Data", max_cache=2048):
        self.class_storage = class_storage
        DictSQL.__init__(self, path_db, tabla, max_cache)

    def __setitem__(self, key, obj):
        dato = Util.save_obj_pickle(obj)
        si_ya_esta = key in self.li_keys
        if si_ya_esta:
            sql = "UPDATE %s SET VALUE=? WHERE KEY = ?" % self.tabla
        else:
            sql = "INSERT INTO %s (VALUE,KEY) values(?,?)" % self.tabla
            self.li_keys.append(key)
        self.conexion.execute(sql, (memoryview(dato), key))
        self.conexion.commit()

        if key in self.cache:
            self.add_cache(key, obj)

    def __getitem__(self, key):
        if key in self.li_keys:
            if key in self.cache:
                return self.cache[key]

            sql = "SELECT VALUE FROM %s WHERE KEY= ?" % self.tabla
            row = self.conexion.execute(sql, (key,)).fetchone()
            obj = self.class_storage()
            Util.restore_obj_pickle(obj, row[0])
            self.add_cache(key, obj)
            return obj
        else:
            return None

    def __iter__(self):
        for key in self.li_keys:
            yield self.__getitem__(key)

    def as_dictionary(self):
        sql = "SELECT KEY,VALUE FROM %s" % self.tabla
        cursor = self.conexion.execute(sql)
        dic = {}
        for key, dato in cursor.fetchall():
            obj = self.class_storage()
            Util.restore_obj_pickle(obj, dato)
            dic[key] = obj
        return dic


class DictRawSQL(DictSQL):
    def __init__(self, path_db, tabla="Data"):
        DictSQL.__init__(self, path_db, tabla, max_cache=0)


class ListSQL:
    def __init__(self, path_file, tabla="LISTA", max_cache=2048, reverted=False):
        self.path_file = path_file
        self._conexion = sqlite3.connect(path_file)
        self.tabla = tabla
        self.max_cache = max_cache
        self.cache = {}
        self.reverted = reverted

        self._conexion.execute("CREATE TABLE IF NOT EXISTS %s( DATO BLOB );" % tabla)

        self.li_row_ids = self.read_rowids()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def read_rowids(self):
        sql = "SELECT ROWID FROM %s" % self.tabla
        if self.reverted:
            sql += " ORDER BY ROWID DESC"
        cursor = self._conexion.execute(sql)
        return [rowid for rowid, in cursor.fetchall()]

    def refresh(self):
        self.li_row_ids = self.read_rowids()

    def add_cache(self, key, obj):
        if self.max_cache:
            if len(self.cache) > self.max_cache:
                lik = list(self.cache.keys())
                for x in lik[: self.max_cache // 2]:
                    del self.cache[x]
            self.cache[key] = obj

    def append(self, valor, with_cache=False):
        sql = "INSERT INTO %s( DATO ) VALUES( ? )" % self.tabla
        obj = pickle.dumps(valor)
        cursor = self._conexion.execute(sql, (memoryview(obj),))
        self._conexion.commit()
        lastrowid = cursor.lastrowid
        if self.reverted:
            self.li_row_ids.insert(0, lastrowid)
        else:
            self.li_row_ids.append(lastrowid)
        if with_cache:
            self.add_cache(lastrowid, obj)

    def __getitem__(self, pos):
        if pos < len(self.li_row_ids):
            rowid = self.li_row_ids[pos]
            if rowid in self.cache:
                return self.cache[rowid]

            sql = "select DATO from %s where ROWID=?" % self.tabla
            cursor = self._conexion.execute(sql, (rowid,))
            row = cursor.fetchone()
            if row is None:
                self.li_row_ids = self.read_rowids()
                return None
            obj = pickle.loads(row[0])
            self.add_cache(rowid, obj)
            return obj
        else:
            return None

    def __setitem__(self, pos, obj):
        if pos < len(self.li_row_ids):
            dato = pickle.dumps(obj)
            rowid = self.li_row_ids[pos]
            sql = "UPDATE %s SET dato=? WHERE ROWID = ?" % self.tabla
            self._conexion.execute(sql, (memoryview(dato), rowid))
            self._conexion.commit()
            if rowid in self.cache:
                self.add_cache(rowid, obj)

    def __delitem__(self, pos):
        if pos < len(self.li_row_ids):
            rowid = self.li_row_ids[pos]
            sql = "DELETE FROM %s WHERE ROWID= ?" % self.tabla
            self._conexion.execute(sql, (rowid,))
            self._conexion.commit()
            del self.li_row_ids[pos]

            if rowid in self.cache:
                del self.cache[rowid]

    def __len__(self):
        return len(self.li_row_ids)

    def close(self):
        if self._conexion:
            self._conexion.close()
            self._conexion = None

    def __iter__(self):
        for pos in range(len(self.li_row_ids)):
            yield self.__getitem__(pos)

    def pack(self):
        self._conexion.execute("VACUUM")
        self._conexion.commit()

    def zap(self):
        self._conexion.execute("DELETE FROM %s" % self.tabla)
        self._conexion.commit()
        self.pack()
        self.li_row_ids = []
        self.cache = {}

    def rowid(self, pos):
        return self.li_row_ids[pos]

    def pos_rowid(self, rowid):
        try:
            return self.li_row_ids.index(rowid)
        except:
            return -1


class ListSQLBig:
    def __init__(self, path_file, tabla="LIST"):
        self.path_file = path_file
        self._conexion = sqlite3.connect(path_file)
        self.tabla = tabla
        self.insert = "INSERT INTO %s( DATA ) VALUES( ? )" % self.tabla

        self._conexion.execute("CREATE TABLE IF NOT EXISTS %s( DATA TEXT );" % tabla)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def append(self, valor):
        self._conexion.execute(self.insert, (valor,))

    def close(self):
        if self._conexion:
            self._conexion.commit()
            self._conexion.close()
            self._conexion = None

    def lista(self, rev):
        self._conexion.commit()
        cursor = self._conexion.execute(f"SELECT DATA FROM {self.tabla} ORDER BY DATA" + " DESC;" if rev else ";")
        while True:
            row = cursor.fetchone()
            if row:
                yield row[0]
            else:
                break


class ListObjSQL(ListSQL):
    def __init__(self, path_file, class_storage, tabla="datos", max_cache=2048, reverted=False):
        self.class_storage = class_storage
        ListSQL.__init__(self, path_file, tabla, max_cache, reverted)

    def append(self, obj, with_cache=False, with_commit=True):
        sql = "INSERT INTO %s( DATO ) VALUES( ? )" % self.tabla
        dato = Util.save_obj_pickle(obj)
        cursor = self._conexion.execute(sql, (memoryview(dato),))
        if with_commit:
            self._conexion.commit()
        lastrowid = cursor.lastrowid
        if self.reverted:
            self.li_row_ids.insert(0, lastrowid)
        else:
            self.li_row_ids.append(lastrowid)
        if with_cache:
            self.add_cache(lastrowid, obj)

    def commit(self):
        self._conexion.commit()

    def __getitem__(self, pos):
        if pos < len(self.li_row_ids):
            rowid = self.li_row_ids[pos]
            if rowid in self.cache:
                return self.cache[rowid]

            sql = "select DATO from %s where ROWID=?" % self.tabla
            cursor = self._conexion.execute(sql, (rowid,))
            obj = self.class_storage()
            x = cursor.fetchone()
            if x:
                Util.restore_obj_pickle(obj, x[0])
            self.add_cache(rowid, obj)
            return obj

    def __setitem__(self, pos, obj):
        if pos < len(self.li_row_ids):
            rowid = self.li_row_ids[pos]
            sql = "UPDATE %s SET dato=? WHERE ROWID = ?" % self.tabla
            dato = Util.save_obj_pickle(obj)
            self._conexion.execute(sql, (memoryview(dato), rowid))
            self._conexion.commit()

            if rowid in self.cache:
                self.add_cache(rowid, obj)


class IPC(object):
    def __init__(self, path_file, si_crear):
        if si_crear:
            Util.remove_file(path_file)

        self._conexion = sqlite3.connect(path_file)
        self.path_file = path_file

        if si_crear:
            sql = "CREATE TABLE DATOS( DATO BLOB );"
            self._conexion.execute(sql)
            self._conexion.commit()

        self.key = 0

    def pop(self):
        nk = self.key + 1
        sql = "SELECT dato FROM DATOS WHERE ROWID = %d" % nk
        cursor = self._conexion.execute(sql)
        reg = cursor.fetchone()
        if reg:
            valor = pickle.loads(reg[0])
            self.key = nk
        else:
            valor = None
        return valor

    def read_again(self):
        self.key -= 1

    def has_more_data(self):
        nk = self.key + 1
        sql = "SELECT dato FROM DATOS WHERE ROWID = %d" % nk
        cursor = self._conexion.execute(sql)
        reg = cursor.fetchone()
        return reg is not None

    def push(self, valor):
        dato = sqlite3.Binary(pickle.dumps(valor))
        sql = "INSERT INTO DATOS (dato) values(?)"
        self._conexion.execute(sql, [dato])
        self._conexion.commit()

    def close(self):
        if self._conexion:
            self._conexion.close()
            self._conexion = None


class RowidReader:
    def __init__(self, path_file, tabla):
        self.path_file = path_file
        self.tabla = tabla
        self.where = None
        self.order = None
        self.running = False
        self.li_row_ids = []
        self.chunk = 2024
        self.stop = False
        self.lock = None
        self.thread = None

    def run(self, li_row_ids, where, order):
        self.stopnow()
        self.where = where
        self.order = order
        self.running = True
        self.stop = False
        self.li_row_ids = li_row_ids
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run_thread)
        self.thread.daemon = True
        self.thread.start()

    def _run_thread(self):
        conexion = sqlite3.connect(self.path_file)
        sql = "SELECT ROWID FROM %s" % self.tabla
        if self.where:
            sql += " WHERE %s" % self.where
        if self.order:
            sql += " ORDER BY %s" % self.order
        else:
            sql += " ORDER BY ROWID"
        cursor = conexion.cursor()
        try:
            cursor.execute(sql)
            ch = random.randint(1000, 3000)
            while not self.stop:
                li = cursor.fetchmany(ch)
                if li:
                    self.lock.acquire()
                    self.li_row_ids.extend([x[0] for x in li])
                    self.lock.release()
                if len(li) < ch:
                    break
                ch = self.chunk
        except sqlite3.OperationalError:
            pass

        cursor.close()
        conexion.close()
        self.running = False

    def terminado(self):
        return not self.running

    def stopnow(self):
        if self.running:
            self.stop = True
            self.thread.join()

    def reccount(self):
        return len(self.li_row_ids)


class DictBig(object):
    def __init__(self):
        self.dict = sortedcontainers.SortedDict()
        self.db = None
        self.test_mem = 100_000

    def __contains__(self, key):
        if key in self.dict:
            return True
        elif self.db is not None:
            return key in self.db
        return False

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        elif self.db is not None:
            return self.db[key]
        return None

    def test_memory(self):
        ps = psutil.virtual_memory()
        if ps.available < (512 * 1024 * 1024) or Util.memory_python() > (512 * 1024 * 1024):
            self.db = DictBigDB()
        else:
            self.test_mem = 50_000

    def __setitem__(self, key, value):
        if key in self.dict:
            self.dict[key] = value
        elif self.db is not None:
            self.db[key] = value
        else:
            self.dict[key] = value
            self.test_mem -= 1
            if self.test_mem == 0:
                self.test_memory()

    def __delitem__(self, key):
        if key in self.dict:
            del self.dict[key]
        elif self.db is not None:
            del self.db[key]

    def __len__(self):
        tam = len(self.dict)
        if self.db is not None:
            tam += len(self.db)
        return tam

    def close(self):
        if self.dict:
            del self.dict
            if self.db is not None:
                self.db.close()
                self.db = None
            self.dict = None

    def get(self, key, default):
        valor = self.__getitem__(key)
        if valor is None:
            return default
        return valor

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()

    def items(self):
        if self.db is None:
            for k, v in self.dict.items():
                yield k, v
            return

        g_db = iter(self.db)

        kg = vg = None

        for k, v in self.dict.items():
            while g_db is not None:
                if kg is None:
                    try:
                        kg, vg = next(g_db)
                        if kg < k:
                            yield kg, vg
                            kg = None
                        else:
                            break
                    except StopIteration:
                        g_db = None
                        break
                else:
                    if kg < k:
                        yield kg, vg
                        kg = None
                    else:
                        break
            yield k, v

        while g_db is not None:
            try:
                kg, vg = next(g_db)
                yield kg, vg
            except StopIteration:
                g_db = None


class DictBigDB(object):
    def __init__(self):
        self.conexion = sqlite3.connect(Code.configuration.ficheroTemporal("dbdb"))
        self.conexion.execute("CREATE TABLE IF NOT EXISTS DATA( KEY TEXT PRIMARY KEY, VALUE BLOB );")
        self.conexion.execute("PRAGMA journal_mode=REPLACE")
        self.conexion.execute("PRAGMA synchronous=OFF")
        self.conexion.execute("PRAGMA locking_mode=EXCLUSIVE")
        self.conexion.commit()

    def __contains__(self, key):
        cursor = self.conexion.execute("SELECT KEY FROM DATA WHERE key=?;", (key,))
        return cursor.fetchone() is not None

    def __getitem__(self, key):
        cursor = self.conexion.execute("SELECT VALUE FROM DATA WHERE key=?;", (key,))
        row = cursor.fetchone()
        if row is not None:
            return pickle.loads(row[0])
        else:
            return None

    def __setitem__(self, key, value):
        xvalue = pickle.dumps(value)
        self.conexion.execute("REPLACE INTO DATA (KEY, VALUE) VALUES (?,?)", (key, xvalue))

    def __delitem__(self, key):
        sql = "DELETE FROM DATA WHERE KEY= ?"
        self.conexion.execute(sql, (key,))

    def __len__(self):
        cursor = self.conexion.execute("SELECT COUNT(*) FROM DATA")
        row = cursor.fetchone()
        return row[0] if row else 0

    def close(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None

    def get(self, key, default):
        valor = self.__getitem__(key)
        if valor is None:
            return default
        return valor

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()

    def __iter__(self):
        self.cursor_iter = self.conexion.execute("SELECT KEY,VALUE FROM DATA ORDER BY KEY")
        self.pos_iter = 0
        self.max_iter = 0
        return self

    def __next__(self):
        if self.pos_iter >= self.max_iter:
            self.rows_iter = self.cursor_iter.fetchmany(10000)
            self.max_iter = len(self.rows_iter) if self.rows_iter else 0
            if self.max_iter == 0:
                raise StopIteration
            self.pos_iter = 0
        k, v = self.rows_iter[self.pos_iter]
        self.pos_iter += 1
        return k, pickle.loads(v)



def check_table_in_db(path_db: str, table: str):
    conexion = sqlite3.connect(path_db)
    cursor = conexion.cursor()
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table,))
    resp = cursor.fetchone()[0] == 1
    conexion.close()
    return resp


def list_tables(path_db: str):
    conexion = sqlite3.connect(path_db)
    cursor = conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    li_resp = cursor.fetchall()
    if li_resp:
        return [row[0] for row in li_resp]
    return []


def remove_table(path_db: str, table: str):
    conexion = sqlite3.connect(path_db)
    cursor = conexion.cursor()
    cursor.execute("DROP TABLE IF EXISTS %s" % table)
    conexion.execute("VACUUM")
    conexion.commit()
    conexion.close()


class DictTextSQL(object):
    def __init__(self, path_db, tabla="DataText", max_cache=2048):
        self.tabla = tabla
        self.max_cache = max_cache
        self.cache = {}

        self.conexion = sqlite3.connect(path_db)

        self.conexion.execute("CREATE TABLE IF NOT EXISTS %s( KEY TEXT PRIMARY KEY, VALUE TEXT );" % tabla)

        cursor = self.conexion.execute("SELECT KEY FROM %s" % self.tabla)
        self.li_keys = [reg[0] for reg in cursor.fetchall()]

        self.normal_save_mode = True
        self.pending_commit = False

    def set_faster_mode(self):
        self.normal_save_mode = False

    def set_normal_mode(self):
        if self.pending_commit:
            self.conexion.commit()
        self.normal_save_mode = True

    def add_cache(self, key: str, txt: str):
        if self.max_cache:
            if len(self.cache) > self.max_cache:
                lik = list(self.cache.keys())
                for x in lik[: self.max_cache // 2]:
                    del self.cache[x]
            self.cache[key] = txt

    def __contains__(self, key: str):
        return key in self.li_keys

    def __setitem__(self, key: str, txt: str):
        if not self.conexion:
            return
        si_ya_esta = key in self.li_keys
        if si_ya_esta:
            sql = "UPDATE %s SET VALUE=? WHERE KEY = ?" % self.tabla
        else:
            sql = "INSERT INTO %s (VALUE,KEY) values(?,?)" % self.tabla
            self.li_keys.append(key)
        self.conexion.execute(sql, (txt, key))

        self.add_cache(key, txt)
        if self.normal_save_mode:
            self.conexion.commit()
        elif not self.pending_commit:
            self.pending_commit = True

    def __getitem__(self, key: str):
        if key in self.li_keys:
            if key in self.cache:
                return self.cache[key]

            sql = "SELECT VALUE FROM %s WHERE KEY= ?" % self.tabla
            row = self.conexion.execute(sql, (key,)).fetchone()
            txt = row[0]

            self.add_cache(key, txt)
            return txt
        return None

    def __delitem__(self, key: str):
        if key in self.li_keys:
            self.li_keys.remove(key)
            if key in self.cache:
                del self.cache[key]
            sql = "DELETE FROM %s WHERE KEY= ?" % self.tabla
            self.conexion.execute(sql, (key,))
            if self.normal_save_mode:
                self.conexion.commit()
            else:
                self.pending_commit = True

    def __len__(self):
        return len(self.li_keys)

    def is_closed(self):
        return self.conexion is None

    def close(self):
        if self.conexion:
            if self.pending_commit:
                self.conexion.commit()
            self.conexion.close()
            self.conexion = None

    def keys(self, si_ordenados=False, si_reverse=False):
        return sorted(self.li_keys, reverse=si_reverse) if si_ordenados else self.li_keys

    def get(self, key, default=None):
        key = str(key)
        if key in self.li_keys:
            return self.__getitem__(key)
        else:
            return default

    def as_dictionary(self):
        sql = "SELECT KEY,VALUE FROM %s" % self.tabla
        cursor = self.conexion.execute(sql)
        dic = {}
        for key, dato in cursor.fetchall():
            dic[key] = dato
        return dic

    def pack(self):
        self.conexion.execute("VACUUM")
        self.conexion.commit()

    def zap(self):
        self.conexion.execute("DELETE FROM %s" % self.tabla)
        self.conexion.commit()
        self.conexion.execute("VACUUM")
        self.conexion.commit()
        self.cache = {}
        self.li_keys = []

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        self.close()

    def copy_from(self, dbdict):
        mode = self.normal_save_mode
        self.set_faster_mode()
        for key in dbdict.keys():
            self[key] = dbdict[key]
        self.conexion.commit()
        self.pending_commit = False
        self.normal_save_mode = mode
