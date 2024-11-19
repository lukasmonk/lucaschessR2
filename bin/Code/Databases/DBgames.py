import os
import random
import sqlite3
import time

import FasterCode

import Code
from Code import Util
from Code.Base import Game
from Code.Base.Constantes import STANDARD_TAGS, FEN_INITIAL
from Code.Databases import DBgamesST
from Code.SQL import UtilSQL

pos_a1 = FasterCode.pos_a1
a1_pos = FasterCode.a1_pos
pv_xpv = FasterCode.pv_xpv
xpv_pv = FasterCode.xpv_pv
xpv_lipv = FasterCode.xpv_lipv
xpv_pgn = FasterCode.xpv_pgn
lipv_pgn = FasterCode.lipv_pgn
PGNreader = FasterCode.PGNreader
set_fen = FasterCode.set_fen
make_move = FasterCode.make_move
get_fen = FasterCode.get_fen
get_exmoves = FasterCode.get_exmoves
fen_fenm2 = FasterCode.fen_fenm2
make_pv = FasterCode.make_pv
num_move = FasterCode.num_move
move_num = FasterCode.move_num

drots = {x.upper(): x for x in STANDARD_TAGS}

BODY_SAVE = b"BODY "


class DBgames:
    def __init__(self, path_db):
        self.link_file = path_db
        if path_db.endswith(".lcdblink"):
            with open(path_db, "rt", encoding="utf-8", errors="ignore") as f:
                path_db = f.read().strip()
            self.external_folder = os.path.dirname(path_db)
        else:
            self.external_folder = ""
        self.path_file = os.path.abspath(path_db)

        self.conexion = sqlite3.connect(self.path_file)
        self.conexion.row_factory = sqlite3.Row
        self.order = None
        self.filter = None

        self.cache = {}
        self.mincache = 2024
        self.maxcache = 4048

        self.li_fields = self.lista_campos()
        self.st_fields = set(field.upper() for field in self.li_fields)

        self.read_options()

        self.li_order = []

        summary_depth = self.read_config("SUMMARY_DEPTH", 0)
        self.with_db_stat = summary_depth > 0
        if self.with_db_stat:
            self.db_stat = DBgamesST.TreeSTAT(self.path_file + ".st1", summary_depth)
        else:
            self.db_stat = None

        self.li_row_ids = []

        self.rowidReader = UtilSQL.RowidReader(self.path_file, "Games")

        self.with_plycount = "PLYCOUNT" in self.read_config("dcabs", {})

    def read_options(self):
        self.allows_duplicates = self.read_config("ALLOWS_DUPLICATES", True)
        self.allows_positions = self.read_config("ALLOWS_POSITIONS", True)
        self.allows_complete_game = self.read_config("ALLOWS_COMPLETE_GAMES", True)
        self.allows_zero_moves = self.read_config("ALLOWS_ZERO_MOVES", True)

    def remove_columns(self, lista):
        self.rowidReader.stopnow()

        cursor = self.conexion.execute("PRAGMA table_info('Games')")
        licreate = []
        lifields = []
        for row in cursor:
            num, key, tipo, nose1, nose2, nose3 = row
            if key not in lista:
                if key == "_DATA_":
                    licreate.append("_DATA_ BLOB")
                elif key == "PLYCOUNT":
                    licreate.append("PLYCOUNT INT")
                else:
                    licreate.append("'%s' VARCHAR" % key)
                lifields.append("'%s'" % key)
        sql_create = ",".join(licreate)
        sql_fields = ",".join(lifields)
        sql_select = ",".join(["Games_old.%s" % f for f in lifields])

        for sql in (
                "PRAGMA foreign_keys=off;",
                "BEGIN TRANSACTION;",
                "ALTER TABLE Games RENAME TO Games_old;",
                "CREATE TABLE Games (%s);" % sql_create,
                "INSERT INTO Games (%s) SELECT %s FROM Games_old;" % (sql_fields, sql_select),
                "DROP TABLE Games_old;",
                "CREATE INDEX XPV_INDEX ON Games (XPV);",
        ):
            self.conexion.execute(sql)
        self.conexion.commit()
        self.conexion.execute("VACUUM")

    def get_name(self):
        basename = os.path.basename(self.path_file)
        p = basename.rindex(".")
        return basename[:p]

    @property
    def select(self):
        return ",".join('"%s"' % campo for campo in self.li_fields)

    def lista_campos(self):
        cursor = self.conexion.execute("pragma table_info(Games)")
        if not cursor.fetchall():
            for sql in (
                    "CREATE TABLE Games(XPV VARCHAR,_DATA_ BLOB,PLYCOUNT INT);",
                    "CREATE INDEX XPV_INDEX ON Games (XPV);",
                    "PRAGMA page_size = 4096;",
                    "PRAGMA synchronous = OFF;",
                    "PRAGMA cache_size = 10000;",
                    "PRAGMA journal_mode = MEMORY;",
            ):
                self.conexion.execute(sql)
            self.conexion.commit()
        cursor = self.conexion.execute("pragma table_info(Games);")
        return [row[1] for row in cursor.fetchall()]

    def reset_cache(self):
        self.cache = {}

    def save_config(self, key, valor):
        with UtilSQL.DictRawSQL(self.path_file, "Config") as dbconf:
            dbconf[key] = valor
            if key == "dcabs":
                self.with_plycount = "PLYCOUNT" in self.read_config("dcabs", {})

    def read_config(self, key, default=None):
        with UtilSQL.DictRawSQL(self.path_file, "Config") as dbconf:
            return dbconf.get(key, default)

    def addcache(self, rowid, reg):
        if len(self.cache) > self.maxcache:
            keys = list(self.cache.keys())
            rkeys = random.sample(keys, self.mincache)
            ncache = {}
            for k in rkeys:
                ncache[k] = self.cache[k]
            self.cache = ncache
        self.cache[rowid] = reg

    def interchange(self, nfila, si_up):
        rowid = self.li_row_ids[nfila]
        if si_up:
            # buscamos el mayor, menor que rowid
            fil_other = None
            rowid_other = -1
            for fil0, rowid0 in enumerate(self.li_row_ids):
                if rowid0 < rowid:
                    if rowid0 > rowid_other:
                        fil_other = fil0
                        rowid_other = rowid0
            if fil_other is None:
                return None
        else:
            # buscamos el menor, mayor que rowid
            fil_other = None
            rowid_other = 999999999999
            for fil0, rowid0 in enumerate(self.li_row_ids):
                if rowid0 > rowid:
                    if rowid0 < rowid_other:
                        fil_other = fil0
                        rowid_other = rowid0
            if fil_other is None:
                return None
        # Hay que intercambiar rowid, con rowid_other
        select_all = ",".join(self.li_fields)
        cursor = self.conexion.execute("SELECT %s FROM Games WHERE rowid =%d" % (select_all, rowid))
        reg = cursor.fetchone()
        cursor = self.conexion.execute("SELECT %s FROM Games WHERE rowid =%d" % (select_all, rowid_other))
        reg_other = cursor.fetchone()

        # Problema con error por XPV unico cuando se intercambia, en RowidOther ponemos un xpv ficticio
        sql = "UPDATE Games SET XPV=? WHERE ROWID = %d" % rowid_other
        self.conexion.execute(sql, ("?????",))

        update_all = ",".join(["%s=?" % campo for campo in self.li_fields])
        sql = "UPDATE Games SET %s" % update_all + " WHERE ROWID = %d"

        self.conexion.execute(sql % rowid, reg_other)
        self.conexion.execute(sql % rowid_other, reg)
        self.conexion.commit()

        self.addcache(rowid, reg_other)
        self.addcache(rowid_other, reg)

        return fil_other

    def get_rowid(self, nfila):
        return self.li_row_ids[nfila]

    def field(self, nfila, name):
        rowid = self.li_row_ids[nfila]
        if not (rowid in self.cache):
            cursor = self.conexion.execute("SELECT %s FROM Games WHERE rowid =%d" % (self.select, rowid))
            reg = cursor.fetchone()
            self.addcache(rowid, reg)
        try:
            return self.cache[rowid][name]
        except:
            return ""

    def set_field(self, nfila, name, value):
        rowid = self.li_row_ids[nfila]
        sql = f"UPDATE Games SET {name}=? WHERE ROWID=?"
        self.conexion.execute(sql, (value, rowid))
        self.conexion.commit()
        if rowid in self.cache:
            del self.cache[rowid]

    def if_there_are_records_to_read(self):
        if not self.rowidReader:
            return False
        return not self.rowidReader.terminado()

    def filter_pv(self, pv, condicionAdicional=None):
        condicion = ""
        if type(pv) == list:  # transpositions
            if pv:
                li = []
                for unpv in pv:
                    xpv = pv_xpv(unpv)
                    li.append('XPV LIKE "%s%%"' % xpv)
                condicion = "(%s)" % (" OR ".join(li),)
        elif pv:
            xpv = pv_xpv(pv)
            condicion = 'XPV LIKE "%s%%"' % xpv if xpv else ""
        if condicionAdicional:
            if condicion:
                condicion += " AND (%s)" % condicionAdicional
            else:
                condicion = condicionAdicional
        self.filter = condicion

        self.li_row_ids = []
        self.rowidReader.run(self.li_row_ids, condicion, self.order)

    def reccount(self):
        if not self.rowidReader:
            return 0
        n = self.rowidReader.reccount()
        # Si es cero y no ha terminado de leer, se le da vtime para que devuelva algo
        while n == 0 and not self.rowidReader.terminado():
            time.sleep(0.05)
            n = self.rowidReader.reccount()
        return n

    def reccount_stable(self):
        return self.reccount(), self.rowidReader.terminado()

    def all_reccount(self):
        self.li_row_ids = []
        self.rowidReader.run(self.li_row_ids, None, None)
        while not self.rowidReader.terminado():
            time.sleep(0.1)
        return self.reccount()

    def __len__(self):
        while not self.rowidReader.terminado():
            time.sleep(0.1)
        return self.reccount()

    def is_empty(self):
        return self.reccount() == 0

    def close(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None
        if self.db_stat:
            self.db_stat.close()
            self.db_stat = None
        if self.rowidReader:
            self.rowidReader.stopnow()
            self.rowidReader = None

    def label(self):
        if Util.same_path(self.path_file, self.link_file):
            return Code.relative_root(self.path_file)
        else:
            return "%s (%s)" % (Code.relative_root(self.path_file), Code.relative_root(self.link_file))

    def depth_stat(self):
        return self.db_stat.depth if self.with_db_stat else 0

    @staticmethod
    def read_xpv(xpv):
        if xpv.startswith("|"):
            nada, fen, xpv = xpv.split("|")
        else:
            fen = ""
        pv = xpv_pv(xpv) if xpv else ""
        return fen, pv

    def get_pv(self, row):
        xpv = self.field(row, "XPV")
        return self.read_xpv(xpv)

    def put_order(self, li_order):
        li = []
        for campo, tipo, is_numeric in li_order:
            if is_numeric:
                li.append("CAST(%s as INT) %s" % (campo, tipo))
            else:
                li.append("%s COLLATE NOCASE %s" % (campo, tipo))
        self.order = ",".join(li)
        self.li_row_ids = []
        self.rowidReader.run(self.li_row_ids, self.filter, self.order)
        self.li_order = li_order

    def get_order(self):
        return self.li_order

    def remove_list_recnos(self, lista_recnos):
        c_sql = "DELETE FROM Games WHERE rowid = ?"
        lista_recnos.sort(reverse=True)
        for recno in lista_recnos:
            fen, pv = self.get_pv(recno)
            result = self.field(recno, "RESULT")
            if not fen and self.with_db_stat:
                self.db_stat.append(pv, result, -1)
            self.conexion.execute(c_sql, (self.li_row_ids[recno],))
            del self.li_row_ids[recno]
        if self.with_db_stat:
            self.db_stat.commit()
        self.conexion.commit()

    def remove_duplicates(self):
        li_mirar = [field for field in self.li_fields if field.upper() not in ("_DATA_", "ECO", "XPV", "PLYCOUNT")]
        select = ",".join(li_mirar)
        sql_xpv = "SELECT ROWID, %s FROM Games WHERE XPV = ?" % select

        st_rowid_borrar = set()
        sql = "SELECT XPV FROM Games GROUP BY XPV HAVING COUNT(XPV) > 1"
        cursor = self.conexion.execute(sql)
        for xpv, in cursor.fetchall():
            st = set()
            cursor = self.conexion.execute(sql_xpv, (xpv,))
            for row in cursor.fetchall():
                txt = "".join([x.strip().upper() if x else "" for x in row[1:]])
                if txt in st:
                    st_rowid_borrar.add(row[0])
                else:
                    st.add(txt)

        li_recnos = []
        for recno, rowid in enumerate(self.li_row_ids):
            if rowid in st_rowid_borrar:
                li_recnos.append(recno)

        self.remove_list_recnos(li_recnos)

    def remove_data(self, li_recnos):
        sql = "UPDATE Games SET _DATA_=NULL"
        if li_recnos is None:
            if self.filter:
                sql += " WHERE %s" % self.filter
            self.conexion.execute(sql)
        else:
            for recno in li_recnos:
                rowid = self.li_row_ids[recno]
                sqln = f"{sql} WHERE ROWID=?"
                self.conexion.execute(sqln, [rowid, ])
        self.conexion.commit()

    def get_summary(self, pvBase, dicAnalisis, with_figurines, allmoves=True):
        return self.db_stat.get_summary(pvBase, dicAnalisis, with_figurines, allmoves) if self.with_db_stat else []

    def has_result_field(self):
        return "RESULT" in self.st_fields

    def rebuild_stat(self, dispatch, depth):
        if not ("RESULT" in self.st_fields):
            return

        if not self.with_db_stat:
            self.with_db_stat = True
            self.db_stat = DBgamesST.TreeSTAT(self.path_file + ".st1", depth)

        self.save_config("SUMMARY_DEPTH", depth)
        self.db_stat.depth = depth
        self.db_stat.reset()
        if self.filter:
            self.filter_pv("")
        while self.if_there_are_records_to_read():
            time.sleep(0.1)
            dispatch(0, self.reccount())
        reccount = self.reccount()
        if reccount:
            cursor = self.conexion.execute("SELECT XPV, RESULT FROM Games")
            recno = 0
            self.db_stat.massive_append_set(True)
            while dispatch(recno, reccount):
                chunk = random.randint(60000, 100000)
                li = cursor.fetchmany(chunk)
                if li:
                    for pos, (XPV, RESULT) in enumerate(li):
                        if XPV.startswith("|"):
                            continue
                        pv = xpv_pv(XPV)
                        self.db_stat.append(pv, RESULT)
                        if (pos % (chunk // 20)) == 0:
                            if not dispatch(recno + pos, reccount):
                                break
                    nli = len(li)
                    if nli < chunk:
                        break
                    recno += nli
                    self.db_stat.commit()
                else:
                    break
            self.db_stat.massive_append_set(False)
            self.db_stat.commit()

    def read_complete_recno(self, recno):
        rowid = self.li_row_ids[recno]
        cursor = self.conexion.execute("SELECT %s FROM Games WHERE rowid =%d" % (self.select, rowid))
        return cursor.fetchone()

    def count_data(self, filtro):
        sql = "SELECT COUNT(*) FROM Games"
        if self.filter:
            sql += " WHERE %s" % self.filter
            if filtro:
                sql += " AND %s" % filtro
        else:
            if filtro:
                sql += " WHERE %s" % filtro

        cursor = self.conexion.execute(sql)
        return cursor.fetchone()[0]

    def get_fens_pgn(self, li_registros, skip_first):
        li = []
        for recno in li_registros:
            game = self.read_game_recno(recno)
            if not game.is_fen_initial():
                if skip_first:
                    game.skip_first()
                fen = game.first_position.fen()
                pgn = game.pgn_base_raw(translated=True)
                li.append((fen,pgn))
        return li

    def yield_fens(self):
        for rowid in self.li_row_ids:
            cursor = self.conexion.execute("SELECT XPV FROM Games WHERE rowid=?", (rowid,))
            raw = cursor.fetchone()
            if raw:
                if raw[0].count("|") == 2:
                    nada, fen, xpv = raw[0].split("|")
                    pv = FasterCode.xpv_pv(xpv)
                    pgn = Game.pv_pgn_raw(fen, pv) if pv else ""
                    yield fen, pgn

    def yield_allfens(self, after_rowid=0):
        sql = "SELECT ROWID, XPV FROM Games"
        if after_rowid:
            sql += f" WHERE ROWID > {after_rowid}"
        cursor = self.conexion.execute(sql)
        while True:
            row = cursor.fetchone()
            if not row:
                break
            rowid, xpv = row
            if xpv.count("|") == 2:
                nada, fen, xpv = xpv.split("|")
                yield rowid, fen, -1, ""
            else:
                fen = FEN_INITIAL
            set_fen(fen)
            li_pv = FasterCode.xpv_pv(xpv).split(" ")
            for pos, pv in enumerate(li_pv):
                make_move(pv)
                fen = get_fen()
                yield rowid, fen, pos, " ".join(li_pv[:pos + 1])

    def yield_data(self, li_fields, filtro):
        select = ",".join(li_fields)
        sql = "SELECT %s FROM Games" % (select,)
        if self.filter:
            sql += " WHERE %s" % self.filter
            if filtro:
                sql += " AND (%s)" % filtro
        else:
            if filtro:
                sql += " WHERE (%s)" % filtro

        cursor = self.conexion.execute(sql)
        while True:
            raw = cursor.fetchone()
            if raw:
                alm = Util.Record()
                for campo in li_fields:
                    setattr(alm, campo, raw[campo])
                yield alm
            else:
                return

    def yield_polyglot(self):
        selected_fields = ["XPV"]

        def select_field(name):
            if name.upper() in self.st_fields:
                selected_fields.append(name)
                return True
            return False

        si_result = select_field("RESULT")
        si_white = select_field("WHITE")
        si_black = select_field("BLACK")
        select = ",".join(selected_fields)
        sql = "SELECT %s FROM Games" % (select,)

        if self.filter:
            sql += " WHERE %s" % self.filter

        cursor = self.conexion.execute(sql)
        result = "*"
        white = ""
        black = ""
        while True:
            li_rows = cursor.fetchmany(10_000)
            if li_rows:
                for row in li_rows:
                    xpv = row[0]
                    pos = 1
                    if si_result:
                        result = row[pos]
                        pos += 1
                    if si_white:
                        white = row[pos]
                        pos += 1
                    if si_black:
                        black = row[pos]

                    yield xpv, result, white, black
            else:
                return

    def yield_games(self):
        for recno in range(self.all_reccount()):
            raw = self.read_complete_recno(recno)
            yield self.read_game_raw(raw)

    def players(self):
        sql = 'SELECT DISTINCT WHITE FROM Games WHERE XPV NOT LIKE "|%"'
        cursor = self.conexion.execute(sql)
        listaw = [raw[0] for raw in cursor.fetchall() if raw[0]]

        sql = 'SELECT DISTINCT BLACK FROM Games WHERE XPV NOT LIKE "|%"'
        cursor = self.conexion.execute(sql)
        listab = [raw[0] for raw in cursor.fetchall() if raw[0]]

        listaw.extend(listab)

        lista = list(set(listaw))
        lista.sort(key=lambda name: name.upper())
        return lista

    def read_game_recno(self, recno):
        raw = self.read_complete_recno(recno)
        return self.read_game_raw(raw)

    def read_game_raw(self, raw):
        game = Game.Game()
        xpgn = raw["_DATA_"]
        ok = False
        fen, pv = self.read_xpv(raw["XPV"])
        if xpgn:
            if xpgn.startswith(BODY_SAVE):
                pgn_read = xpgn[len(BODY_SAVE):].strip()
                if fen:
                    pgn_read = b'[FEN "%s"]\n' % fen.encode() + pgn_read
                ok, game = Game.pgn_game(pgn_read)
            else:
                try:
                    game.restore(xpgn)
                    ok = True
                except:
                    ok = False

        if not ok:
            if fen:
                game.set_fen(fen)
            game.read_pv(pv)

        litags = []
        for field in self.li_fields:
            if not (field in ("XPV", "_DATA_", "PLYCOUNT")):
                v = raw[field]
                if v:
                    litags.append((drots.get(field, Util.primera_mayuscula(field)), v if type(v) == str else str(v)))
        litags.append(("PlyCount", str(raw["PLYCOUNT"])))

        game.set_tags(litags)
        if fen and not game.get_tag("FEN"):
            game.set_tag("FEN", fen)
        if not game.get_tag("Opening"):
            game.assign_opening()

        game.order_tags()
        game.resultado()
        return game

    @staticmethod
    def blank_game():
        hoy = Util.today()
        li_tags = [["Date", f"{hoy.year:d}.{hoy.month:02d}.{hoy.day:02d}"]]
        return Game.Game(li_tags=li_tags)

    def save_game_recno(self, recno, game):
        return self.insert(game) if recno is None else self.modify(recno, game)

    def fill(self, li_field_value):
        lset = ",".join(field + "=?" for field, value in li_field_value)
        sql = "UPDATE Games SET " + lset
        if self.filter:
            sql += " WHERE %s" % self.filter
        self.conexion.execute(sql, [value for field, value in li_field_value])
        self.conexion.commit()

    def fill_pgn(self, field):
        sql = "SELECT ROWID, XPV FROM Games"
        if self.filter:
            sql += " WHERE %s" % self.filter
        cursor = self.conexion.execute(sql)
        for rowid, xpv in cursor.fetchall():
            if xpv.startswith("|"):
                nada, fen, xpv = xpv.split("|")
                pv = FasterCode.xpv_pv(xpv)
                pgn = Game.pv_pgn_raw(fen, pv) if pv else ""
            else:
                pgn = xpv_pgn(xpv)
            pgn = pgn.replace("\n", " ")
            sql = "UPDATE Games SET %s=? WHERE ROWID=?" % field
            self.conexion.execute(sql, [pgn, rowid])
        self.conexion.commit()

    def pack(self):
        self.conexion.execute("VACUUM")
        if self.with_db_stat:
            self.db_stat._conexion.execute("VACUUM")

    def insert_lcsb(self, path_lcsb):
        dic = Util.restore_pickle(path_lcsb)
        game = Game.Game()
        game.restore(dic)
        return self.insert(game)

    def li_tags(self):
        return [tag for tag in self.li_fields if not (tag in ("XPV", "_DATA_"))]

    def add_column(self, column: str):
        column = column.upper()
        if column not in self.st_fields:
            try:
                sql = f"ALTER TABLE Games ADD COLUMN '{column}' VARCHAR;"
                self.conexion.execute(sql)
                self.conexion.commit()
                self.li_fields.append(column)
                self.st_fields.add(column)
            except sqlite3.OperationalError:
                pass

    def import_pgns(self, ficheros, dl_tmp):

        erroneos = duplicados = importados = 0

        allows_fen = self.allows_positions
        allows_complete_game = self.allows_complete_game
        allows_cero_moves = self.allows_zero_moves
        duplicate_check = not self.allows_duplicates

        t1 = time.time() - 0.7  # para que empiece enseguida

        if self.with_db_stat:
            self.db_stat.massive_append_set(True)

        def write_logs(fich, pgn):
            with open(fich, "ab") as ferr:
                ferr.write(pgn)
                ferr.write(b"\n")

        si_cols_cambiados = False
        select = ",".join('"%s"' % campo for campo in self.li_fields)
        select_values = ("?," * len(self.li_fields))[:-1]
        sql = "INSERT INTO Games (%s) VALUES (%s);" % (select, select_values)

        st_xpv_bloque = set()

        li_regs = []
        n_regs = 0

        conexion = self.conexion

        dcabs = self.read_config("dcabs", drots.copy())

        obj_decode = Util.Decode()
        decode = obj_decode.decode

        for file in ficheros:
            nomfichero = os.path.basename(file)
            fich_erroneos = Util.opj(Code.configuration.temporary_folder(), nomfichero[:-3] + "errors.pgn")
            fich_duplicados = Util.opj(Code.configuration.temporary_folder(), nomfichero[:-3] + "duplicates.pgn")
            dl_tmp.pon_titulo(nomfichero)
            next_n = random.randint(1000, 2000)

            obj_decode.read_file(file)

            with PGNreader(file, self.depth_stat()) as fpgn:
                bsize = fpgn.size
                for n, (body, is_raw, pv, fens, bdCab, bdCablwr, btell) in enumerate(fpgn, 1):
                    if n == next_n:
                        if time.time() - t1 > 0.8:
                            if not dl_tmp.actualiza(
                                    erroneos + duplicados + importados,
                                    erroneos,
                                    duplicados,
                                    importados,
                                    btell * 100.0 / bsize,
                            ):
                                break
                            t1 = time.time()
                        next_n = n + random.randint(1000, 2000)

                    # Sin movimientos
                    if not pv and not allows_cero_moves:
                        erroneos += 1
                        write_logs(fich_erroneos, fpgn.bpgn())
                        continue

                    d_cab = {decode(k).replace(" ", ""): decode(v) for k, v in bdCab.items()}
                    d_cablwr = {decode(k).replace(" ", ""): decode(v) for k, v in bdCablwr.items()}
                    dcabs.update(d_cablwr)

                    xpv = pv_xpv(pv)

                    fen = d_cab.get("FEN", None)
                    if fen:
                        if fen == FEN_INITIAL:
                            del d_cab["FEN"]
                            del d_cablwr["FEN"]
                            fen = None
                        else:
                            if not allows_fen:
                                erroneos += 1
                                write_logs(fich_erroneos, fpgn.bpgn())
                                continue
                            xpv = "|%s|%s" % (fen, xpv)

                    if not fen:
                        if not allows_complete_game:
                            erroneos += 1
                            write_logs(fich_erroneos, fpgn.bpgn())
                            continue
                        fen = None  # por si hay alguno vacio

                    if duplicate_check:
                        # Duplicados en el bloque actual
                        if xpv in st_xpv_bloque:
                            ok = False

                        # Duplicados respecto a las grabadas ya
                        else:
                            cursor = conexion.execute("SELECT COUNT(*) FROM games WHERE XPV = ?", (xpv,))
                            ok = cursor.fetchone()[0] == 0

                        if not ok:
                            duplicados += 1
                            write_logs(fich_duplicados, fpgn.bpgn())
                            continue

                    st_xpv_bloque.add(xpv)

                    for k in d_cab:
                        if not (k.upper() in self.st_fields):

                            # Grabamos lo que hay
                            if li_regs:
                                n_regs = 0
                                conexion.executemany(sql, li_regs)
                                li_regs = []
                                st_xpv_bloque = set()
                                conexion.commit()
                                if self.with_db_stat:
                                    self.db_stat.massive_append_set(False)
                                    self.db_stat.commit()
                                    self.db_stat.massive_append_set(True)

                            self.add_column(k)
                            si_cols_cambiados = True
                            select_values = ("?," * len(self.li_fields))[:-1]
                            sql = "insert into Games (%s) values (%s);" % (self.select, select_values)

                    reg = []
                    result = "*"
                    for campo in self.li_fields:
                        if campo == "XPV":
                            reg.append(xpv)
                        elif campo == "_DATA_":
                            data = None
                            if not is_raw:
                                data = memoryview(BODY_SAVE + body)
                            reg.append(data)
                        elif campo == "PLYCOUNT":
                            reg.append((pv.count(" ") + 1) if pv else 0)
                        else:
                            reg.append(d_cab.get(campo))
                            if campo == "RESULT":
                                result = d_cab.get(campo, "*")

                    if self.with_db_stat and fen is None and pv:
                        self.db_stat.append(pv, result)

                    li_regs.append(reg)
                    n_regs += 1
                    importados += 1
                    if n_regs == 20000:
                        n_regs = 0
                        conexion.executemany(sql, li_regs)
                        li_regs = []
                        st_xpv_bloque = set()
                        # conexion.commit()
                        # if self.with_db_stat:
                        #     self.db_stat.commit()
            if dl_tmp.is_canceled:
                break
        dl_tmp.actualiza(erroneos + duplicados + importados, erroneos, duplicados, importados, 100.00)
        dl_tmp.ponSaving()

        if li_regs:
            conexion.executemany(sql, li_regs)
            # conexion.commit()

        if self.with_db_stat:
            self.db_stat.massive_append_set(False)
            self.db_stat.commit()
        conexion.commit()

        dl_tmp.ponContinuar()

        self.save_config("dcabs", dcabs)

        return si_cols_cambiados

    def append_db(self, db, li_recnos, dl_tmp):
        erroneos = duplicados = importados = 0

        allows_fen = self.allows_positions
        allows_complete_game = self.allows_complete_game
        allows_cero_moves = self.allows_zero_moves
        duplicate_check = not self.allows_duplicates

        t1 = time.time() - 0.7  # para que empiece enseguida

        if self.with_db_stat:
            self.db_stat.massive_append_set(True)

        si_cols_cambiados = False
        for campo in db.li_fields:
            if campo not in self.st_fields:
                self.add_column(campo)
                si_cols_cambiados = True

        dcabs_db = db.read_config("dcabs", {})
        self.save_config("dcabs", dcabs_db)

        select = db.select
        select_values = ("?," * len(db.li_fields))[:-1]
        sql = "INSERT INTO Games (%s) VALUES (%s);" % (select, select_values)

        pos_result = db.li_fields.index("RESULT") if "RESULT" in db.li_fields else None

        st_xpv_bloque = set()

        li_regs = []
        n_regs = 0

        conexion = self.conexion

        next_n = random.randint(1000, 2000)

        bsize = len(li_recnos)
        for btell, recno in enumerate(li_recnos):
            if btell == next_n:
                if time.time() - t1 > 0.9:
                    if not dl_tmp.actualiza(
                            erroneos + duplicados + importados, erroneos, duplicados, importados, btell * 100.0 / bsize
                    ):
                        break
                    t1 = time.time()
                next_n = btell + random.randint(1000, 2000)

            row = db.read_complete_recno(recno)

            xpv = row[0]

            si_fen = "|" in xpv
            if si_fen:
                if not allows_fen:
                    erroneos += 1
                    continue
                nada, fen, xpv = xpv.split("|")
            else:
                if not allows_complete_game:
                    erroneos += 1
                    continue

            if not xpv:
                if not allows_cero_moves:
                    erroneos += 1
                    continue

            if duplicate_check:
                if row[0] in st_xpv_bloque:
                    ok = False
                else:
                    cursor = conexion.execute(
                        "SELECT COUNT(*) FROM games WHERE XPV = ?", (row[0],)
                    )  # No vale la variable xpv, que se ha cambiado
                    ok = cursor.fetchone()[0] == 0
                if not ok:
                    duplicados += 1
                    continue
                st_xpv_bloque.add(row[0])

            if self.with_db_stat and not si_fen and xpv and pos_result is not None:
                pv = xpv_pv(xpv)
                result = row[pos_result]
                self.db_stat.append(pv, result)

            li_regs.append(row)
            n_regs += 1
            importados += 1
            if n_regs == 10000:
                n_regs = 0
                conexion.executemany(sql, li_regs)
                li_regs = []
                st_xpv_bloque = set()
                conexion.commit()
                if self.with_db_stat:
                    self.db_stat.commit()

        dl_tmp.actualiza(erroneos + duplicados + importados, erroneos, duplicados, importados, 100.00)
        dl_tmp.ponSaving()
        if li_regs:
            conexion.executemany(sql, li_regs)
        if self.with_db_stat:
            self.db_stat.massive_append_set(False)
            self.db_stat.commit()
        conexion.commit()
        dl_tmp.ponContinuar()
        return si_cols_cambiados

    def check_game(self, game):
        is_complete = game.is_fen_initial()

        if not self.allows_positions:
            if not is_complete:
                return _("This database does not allow games that are not complete.")

        if not self.allows_complete_game:
            if is_complete:
                return _("This database only allows positions.")

        if not self.allows_zero_moves:
            if len(game) == 0:
                return _("This database does not allows games without moves.")

        return None

    def check_columns(self, li_tags):
        dcabs_new = {}
        for tag in li_tags:
            if not (tag.upper() in self.st_fields):
                self.add_column(tag)
                dcabs_new[tag.upper()] = tag
        if dcabs_new:
            dcabs = self.read_config("dcabs", drots)
            dcabs.update(dcabs_new)
            self.save_config("dcabs", dcabs)

    @staticmethod
    def create_sql_insert(li_tags):
        li_fields = li_tags[:]
        li_fields.insert(0, "PLYCOUNT")
        li_fields.insert(0, "XPV")
        fields = ",".join(li_fields)
        values = ",".join(["?"] * len(li_fields))
        return "INSERT INTO Games (%s) VALUES (%s)" % (fields, values)

    def add_reg_lichess(self, sql, fen, pv, row, with_commit):
        xpv = f"|{fen}|{pv_xpv(pv)}"
        plycount = (pv.count(" ") + 1) if pv else 0
        row.insert(0, plycount)
        row.insert(0, xpv)
        cursor = self.conexion.execute(sql, row)
        self.li_row_ids.append(cursor.lastrowid)
        if with_commit:
            self.conexion.commit()

    def modify(self, recno, game_modificada: Game.Game):
        resp = Util.Record()
        resp.ok = True
        resp.changed = False
        resp.summary_changed = False
        resp.mens_error = None
        resp.inserted = False

        mens_error = self.check_game(game_modificada)
        if mens_error:
            resp.ok = False
            resp.mens_error = mens_error
            return resp

        game_antiguo = self.read_game_recno(recno)
        #
        # # La game antigua y la nueva son iguales ? no se hace nada.
        # if game_antigua == game_modificada:  # game.__eq__
        #     return resp

        # Test si hay nuevos tags
        for tag, valor in game_modificada.li_tags:
            if not (tag.upper() in self.st_fields):
                self.add_column(tag)

        # Modificamos datos antiguos
        li_data = []
        for campo in self.li_fields:
            if campo == "XPV":
                dato = game_modificada.xpv()
            elif campo == "_DATA_":
                dato = None if game_modificada.only_has_moves() else game_modificada.save(False)
            elif campo == "PLYCOUNT":
                dato = len(game_modificada)
            else:
                dato = game_modificada.get_tag(campo)
            li_data.append(dato)

        resp.changed = True

        fields = ",".join([f"'{field}'=?" for field in self.li_fields])
        rowid = self.li_row_ids[recno]
        sql = "UPDATE Games SET %s WHERE ROWID = %d" % (fields, rowid)
        self.conexion.execute(sql, li_data)
        self.conexion.commit()

        # Summary
        if self.with_db_stat:
            if game_antiguo.get_tag("FEN") is None:
                pv = game_antiguo.pv()
                if pv:
                    self.db_stat.append(pv, game_antiguo.resultado(), r=-1)
            if game_modificada.get_tag("FEN") is None:
                pv = game_modificada.pv()
                if pv:
                    self.db_stat.append(pv, game_modificada.resultado(), r=+1)
            resp.summary_changed = True

        if rowid in self.cache:
            del self.cache[rowid]

        return resp

    def insert(self, game_new, with_commit=True):
        resp = Util.Record()
        resp.ok = True
        resp.changed = False
        resp.summary_changed = False
        resp.inserted = True
        resp.mens_error = self.check_game(game_new)
        if resp.mens_error:
            resp.ok = False
            return resp

        # Test si hay nuevos tags
        si_fen_nue = not game_new.is_fen_initial()
        if si_fen_nue:
            if not game_new.get_tag("FEN"):
                game_new.check_tags()

        dcabs_new = {}
        for tag, valor in game_new.li_tags:
            if not (tag.upper() in self.st_fields):
                self.add_column(tag)
                dcabs_new[tag.upper()] = tag
        if dcabs_new:
            dcabs = self.read_config("dcabs", drots)
            dcabs.update(dcabs_new)
            self.save_config("dcabs", dcabs)

        li_fields = []
        li_data = []

        data_nue = None if game_new.only_has_moves() else game_new.save()
        li_fields.append("_DATA_")
        li_data.append(data_nue)

        pv_nue = game_new.pv()
        xpv_nue = pv_xpv(pv_nue)
        if si_fen_nue:
            fen_nue = game_new.first_position.fen()
            xpv_nue = "|%s|%s" % (fen_nue, xpv_nue)
        if not self.allows_duplicates:
            sql = "SELECT COUNT(*) FROM Games WHERE XPV = ?"
            cursor = self.conexion.execute(sql, (xpv_nue,))
            row = cursor.fetchone()
            if row[0] > 0:
                resp.ok = False
                resp.mens_error = _("This game is duplicated")
                return resp
        li_fields.append("XPV")
        li_data.append(xpv_nue)
        li_fields.append("PLYCOUNT")
        li_data.append(game_new.num_moves())

        result_nue = "*"
        for tag, valor_nue in game_new.li_tags:
            tag = tag.upper()
            if tag != "PLYCOUNT":
                li_fields.append(tag)
                li_data.append(valor_nue)
            if tag == "RESULT":
                result_nue = valor_nue

        fields = ",".join(li_fields)
        values = ",".join(["?"] * len(li_fields))
        sql = "INSERT INTO Games (%s) VALUES (%s)" % (fields, values)
        cursor = self.conexion.cursor()
        cursor.execute(sql, li_data)
        if with_commit:
            self.conexion.commit()
        self.li_row_ids.append(cursor.lastrowid)
        cursor.close()
        resp.recno = len(self.li_row_ids)-1

        if self.with_db_stat and not si_fen_nue and pv_nue:
            self.db_stat.append(pv_nue, result_nue, +1)
            if with_commit:
                self.db_stat.commit()
            resp.summary_changed = True

        resp.changed = True

        return resp

    def commit(self):
        self.conexion.commit()
        if self.with_db_stat:
            self.db_stat.commit()

    def has_positions(self):
        return self.allows_positions

    def has_field(self, field):
        return field.upper() in self.st_fields

    def lastrowid(self):
        cursor = self.conexion.execute("SELECT MAX(ROWID) FROM GAMES;")
        row = cursor.fetchone()
        return row[0] if row else 0

    def count_greater_rowid(self, rowid):
        cursor = self.conexion.execute("SELECT count(ROWID) FROM GAMES WHERE ROWID > ?;", (rowid,))
        row = cursor.fetchone()
        return row[0] if row else 0

    def filter_positions(self, li_seq, li_rowids):
        li = []
        if li_seq:
            for pv in li_seq:
                xpv = pv_xpv(pv)
                li.append('XPV LIKE "%s%%"' % xpv)

        if li_rowids:
            for rowid in li_rowids:
                li.append(f'ROWID = {rowid}')

        condicion = "(%s)" % (" OR ".join(li),)
        self.filter = condicion

        self.li_row_ids = []
        self.rowidReader.run(self.li_row_ids, condicion, self.order)


def get_random_game():
    db = DBgames(Code.path_resource("IntFiles", "last_games.lcdb"))
    recno = random.randint(0, db.all_reccount() - 1)
    game = db.read_game_recno(recno)
    db.close()
    return game


def autosave(game: Game.Game):
    path_db = Code.configuration.file_autosave()
    exist = os.path.isfile(path_db)
    db = DBgames(path_db)
    if not exist:
        db.save_config("SUMMARY_DEPTH", 30)
        db.close()
        db = DBgames(path_db)

    db.insert(game)
    db.close()


def save_selected_position(position):
    path_db = Code.configuration.file_selected_positions()
    exist = os.path.isfile(path_db)
    db = DBgames(path_db)
    if not exist:
        db.save_config("SUMMARY_DEPTH", 0)
        db.save_config("ALLOWS_DUPLICATES", False)
        db.save_config("ALLOWS_POSITIONS", True)
        db.save_config("ALLOWS_ZERO_MOVES", True)
        db.close()
        db = DBgames(path_db)
    game = Game.Game(position)
    resp = db.insert(game)
    db.close()
    return resp
