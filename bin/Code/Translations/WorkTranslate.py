import builtins
import datetime
import os
import sqlite3
import traceback

import polib

import Code
from Code import XRun


class WorkTranslate(object):
    def __init__(self, nom_db, is_lucas, tr_actual):
        self.is_lucas = is_lucas
        self.tr_actual = tr_actual
        self.popen = None

        self.last_50 = []

        self.conexion = sqlite3.connect(nom_db)
        self.conexion.execute("CREATE TABLE IF NOT EXISTS LC_TR( KEY TEXT, VALUE TEXT );")
        self.conexion.execute("CREATE TABLE IF NOT EXISTS TR_LC( KEY TEXT, VALUE TEXT );")

        self.is_closed = False
        self.last_rowid = 0
        if is_lucas:
            self.dic_lucas = {}
            self.pending_commit = False
        else:
            self.dic_wtranslate = {}
        self.read_dic()

    def check_commits(self):
        if self.is_closed:
            return False
        if self.pending_commit:
            self.conexion.commit()
            self.pending_commit = False
        self.read_from_wtranslate()
        return True

    def translate(self, english_text):
        if not self.is_closed:
            if english_text not in self.last_50:
                x = traceback.format_stack()[-3]
                x0 = x.split('"')[1]
                li = x0.split(os.sep)
                li = li[li.index("bin") + 1:]
                where = "\\".join(li)[:-3]
                if where.startswith("Code"):
                    where = "." + where[4:] + ".py"
                self.send_to_wtranslate(english_text, where)
                self.last_50.append(english_text)
                if len(self.last_50) > 70:
                    self.last_50 = self.last_50[-40:]
                self.last_50.append(english_text)

        valor = self.dic_lucas.get(english_text, english_text)
        return valor[: valor.index("||")].strip() if "||" in valor else valor

    def send_to_wtranslate(self, key, value):
        sql = "INSERT INTO LC_TR (KEY,VALUE) values(?,?)"
        self.conexion.execute(sql, (key, value))
        self.pending_commit = True
        self.conexion.commit()

    def read_from_wtranslate(self):
        sql = "SELECT ROWID, KEY, VALUE FROM TR_LC WHERE ROWID >= %d" % self.last_rowid
        cursor = self.conexion.execute(sql)
        li_all = cursor.fetchall()
        if not li_all:
            return False
        for rowid, key, value in li_all:
            self.last_rowid = rowid + 1
            if key == "":
                if value == "CLOSE":
                    self.is_closed = True
                    return False
            elif key in self.dic_lucas and not value:
                del self.dic_lucas[key]
            else:
                self.dic_lucas[key] = value
        return True

    def read_from_lucas(self):
        sql = "SELECT ROWID, KEY, VALUE FROM LC_TR WHERE ROWID >= %d" % self.last_rowid
        cursor = self.conexion.execute(sql)
        li_all = cursor.fetchall()
        if not li_all:
            return None

        li_received = []
        for rowid, key, value in li_all:
            self.last_rowid = rowid + 1
            if key == "":
                if value == "CLOSE":
                    self.is_closed = True
                    return None
            li_received.append((key, value))
        return li_received

    def close(self):
        if self.conexion:
            if self.is_lucas:
                self.send_to_wtranslate("", "CLOSE")
                if self.popen:
                    try:
                        self.popen.terminate()
                        self.popen = None
                    except:
                        pass
            else:
                self.send_to_lucas("", "CLOSE")
            self.is_closed = True
            self.conexion.close()
            self.conexion = None

    def send_to_lucas(self, key, value):
        if not self.is_closed:
            sql = "INSERT INTO TR_LC (KEY,VALUE) values(?,?)"
            self.conexion.execute(sql, (key, value))
            self.conexion.commit()

    def read_dic(self):
        path_po = Code.path_resource("Locale", "messages.pot")
        pofile = polib.pofile(path_po)

        path_mo = Code.path_resource("Locale", self.tr_actual, "LC_MESSAGES", "lucaschess.mo")
        mofile = polib.mofile(path_mo)
        dmo = {entry.msgid: entry.msgstr for entry in mofile}

        path_po_saved = Code.configuration.po_saved()
        if os.path.isfile(path_po_saved):
            pofile_saved = polib.pofile(path_po_saved)
            dpo_saved = {entry.msgid: entry.msgstr for entry in pofile_saved}
        else:
            dpo_saved = {}

        now = datetime.datetime.now()
        for entry in pofile:
            trans = dmo.get(entry.msgid, "")
            new = dpo_saved.get(entry.msgid, "")
            if entry.occurrences:
                li_occurrences = []
                li = []
                for rut, linea in entry.occurrences:
                    if rut in li:
                        li_occurrences[li.index(rut)][1].append(int(linea))
                    else:
                        li.append(rut)
                        li_occurrences.append([rut, [int(linea)]])
            else:
                li_occurrences = [("Web", [])]

            where = "|".join(rut for rut, lineas in li_occurrences)

            if trans == new:
                new = ""

            if self.is_lucas:
                if trans:
                    self.dic_lucas[entry.msgid] = new if new else trans

            else:
                self.dic_wtranslate[entry.msgid] = {
                    "TRANS": trans,
                    "NEW": new,
                    "WHERE": "|%s|" % where,
                    "LI_OCCURRENCES": li_occurrences,
                    "WHEN": now,
                }

    def save_popen(self, popen):
        self.popen = popen

    def working_wtranslate(self):
        if self.popen is None:
            return False
        return self.popen.poll() is None

    def F(self, txt):
        return self.translate(txt) if txt else ""

    def SP(self, key):
        if not key:
            return ""
        key = key.strip()
        t = self.F(key)
        if t == key:
            li = []
            for x in key.split(" "):
                if x:
                    li.append(_F(x))
            return " ".join(li)
        else:
            return t


def launch_wtranslation():
    path_workfile = Code.configuration.ficheroTemporal("db")
    work_translate = WorkTranslate(path_workfile, True, Code.configuration.x_translator)

    popen = XRun.run_lucas("-translate", path_workfile)
    work_translate.save_popen(popen)

    builtins.__dict__["_"] = work_translate.translate
    builtins.__dict__["_F"] = work_translate.F
    builtins.__dict__["_SP"] = work_translate.SP

    return work_translate
