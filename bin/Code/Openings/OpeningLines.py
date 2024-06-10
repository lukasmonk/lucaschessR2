import collections
import datetime
import os
import random
import shutil
import sqlite3

import FasterCode

import Code
from Code import Util
from Code.Base import Game, Position, Move
from Code.Base.Constantes import WHITE, ALL_VARIATIONS
from Code.Databases import DBgamesST, DBgames
from Code.Engines import EnginesBunch
from Code.Openings import OpeningsStd
from Code.QT import QTUtil2
from Code.SQL import UtilSQL


class ItemTree:
    def __init__(self, parent, move, pgn, opening, side_resp):
        self.move = move
        self.pgn = pgn
        self.parent = parent
        self.opening = opening
        self.dicHijos = {}
        self.item = None
        self.side_resp = side_resp
        self.elements = 0
        self.with_figurines = Code.configuration.x_pgn_withfigurines
        self.translated = Code.configuration.x_translator != "en" and not Code.configuration.x_pgn_english
        if self.with_figurines:
            self.translated = False

    def add(self, move, pgn, opening):
        if not (move in self.dicHijos):
            self.dicHijos[move] = ItemTree(self, move, pgn, opening, not self.side_resp)
        self.elements += 1
        return self.dicHijos[move]

    def add_list(self, limoves, lipgn, liop):
        n = len(limoves)
        if n > 0:
            item = self.add(limoves[0], lipgn[0], liop[0])
            if n > 1:
                item.add_list(limoves[1:], lipgn[1:], liop[1:])

    def game(self):
        li = []
        if self.pgn:
            li.append(self.pgn)

        item = self.parent
        while item is not None:
            if item.pgn:
                li.append(item.pgn)
            item = item.parent
        return " ".join(reversed(li))

    def game_translated(self):
        pgn = self.game()
        if Code.configuration.x_translator != "en":
            if not Code.configuration.x_pgn_english:
                if Code.configuration.x_pgn_withfigurines:
                    li = []
                    for c in pgn:
                        if c.isupper():
                            c = _F(c)
                        li.append(c)
                    pgn = "".join(li)
        return pgn

    def game_figurines(self):
        pgn = self.game()
        if Code.configuration.x_pgn_withfigurines:
            dconv_fig = Move.dicHTMLFigs
            li = []
            is_white = False
            for c in pgn:
                if c.isupper():
                    c = dconv_fig.get(c if is_white else c.lower(), c)
                elif c.isdigit():
                    is_white = True
                elif c == " ":
                    is_white = False

                li.append(c)
            pgn = "".join(li)
        return pgn

    def list_pv(self):
        li = []
        if self.move:
            li.append(self.move)

        item = self.parent
        while item is not None:
            if item.move:
                li.append(item.move)
            item = item.parent
        return li[::-1]

    def next_in_parent(self):
        li_pv = self.list_pv()
        pos = len(li_pv) - 1
        xdata = self
        while pos >= 0:
            xparent = xdata.parent
            move = li_pv[pos]
            the_next = False
            for data_parent_parent in xparent.dicHijos.values():
                if the_next:
                    return data_parent_parent
                if data_parent_parent.move == move:
                    the_next = True
            pos -= 1
            xdata = xparent

        return None


class ListaOpenings:
    def __init__(self):
        self.folder = Code.configuration.folder_openings()
        if not self.folder or not os.path.isdir(self.folder):
            self.folder = Code.configuration.folder_base_openings

        self.file = Util.opj(self.folder, "openinglines.pk")

        self.lista = Util.restore_pickle(self.file)
        if self.lista is None:
            self.lista = self.read()  # file, lines, title, pv
            self.save()
        else:
            self.testdates()

    def testdates(self):
        index_date = Util.datefile(self.file)

        for pos, dic in enumerate(self.lista):
            pathfile = Util.opj(self.folder, dic["file"])
            file_date = Util.datefile(pathfile)
            if file_date is None:
                self.reiniciar()
                break
            if file_date > index_date:
                op = Opening(pathfile)
                self.lista[pos]["lines"] = len(op)
                op.close()
                self.save()

    def reiniciar(self):
        self.lista = self.read()
        self.save()

    def __len__(self):
        return len(self.lista)

    def __getitem__(self, item):
        return self.lista[item] if self.lista and item < len(self.lista) else None

    def __delitem__(self, item):
        dicline = self.lista[item]
        del self.lista[item]
        os.remove(Util.opj(self.folder, dicline["file"]))
        self.save()

    def arriba(self, item):
        if item > 0:
            self.lista[item], self.lista[item - 1] = self.lista[item - 1], self.lista[item]
            self.save()
            return True
        else:
            return False

    def abajo(self, item):
        if item < (len(self.lista) - 1):
            self.lista[item], self.lista[item + 1] = self.lista[item + 1], self.lista[item]
            self.save()
            return True
        else:
            return False

    def read(self):
        li = []
        for entry in Util.listdir(self.folder):
            file = entry.name
            if file.endswith(".opk"):
                op = Opening(entry.path)
                dicline = {
                    "file": file,
                    "pv": op.basePV,
                    "title": op.title,
                    "lines": len(op),
                    "withtrainings": op.withTrainings(),
                    "withtrainings_engines": op.withTrainingsEngines(),
                }
                li.append(dicline)
                op.close()
        return li

    def save(self):
        Util.save_pickle(self.file, self.lista)

    def select_filename(self, name):
        name = name.strip().replace(" ", "_")
        name = Util.asciiNomFichero(name)

        plant = name + "%d.opk"
        file = name + ".opk"
        num = 0
        while os.path.isfile(Util.opj(self.folder, file)):
            num += 1
            file = plant % num
        return file

    def filepath(self, num):
        return Util.opj(self.folder, self.lista[num]["file"])

    def new(self, file, basepv, title, lines=0):
        dicline = {"file": file, "pv": basepv, "title": title, "lines": lines, "withtrainings": False}
        self.lista.append(dicline)
        op = Opening(self.filepath(len(self.lista) - 1))
        op.setbasepv(basepv)
        op.settitle(title)
        op.close()
        self.save()

    def copy(self, pos):
        dicline = dict(self.lista[pos])
        base = dicline["file"][:-4]
        if base.split("-")[-1].isdigit():
            li = base.split("-")
            base = "-".join(li[:-1])
        filenew = "%s-1.opk" % base
        n = 1
        while os.path.isfile(Util.opj(self.folder, filenew)):
            filenew = "%s-%d.opk" % (base, n)
            n += 1
        try:
            shutil.copy(self.filepath(pos), Util.opj(self.folder, filenew))
        except:
            return

        dicline["file"] = filenew
        dicline["title"] = dicline["title"] + " -%d" % (n - 1 if n > 1 else 1)
        self.lista.append(dicline)
        op = Opening(self.filepath(len(self.lista) - 1))
        op.settitle(dicline["title"])
        op.close()
        self.save()

    def change_title(self, num, title):
        op = Opening(self.filepath(num))
        op.settitle(title)
        op.close()
        self.lista[num]["title"] = title
        self.save()

    def change_file(self, num, file):
        self.lista[num]["file"] = os.path.basename(file)
        self.save()

    def change_first_moves(self, num, new_pv, num_lines):
        self.lista[num]['pv'] = new_pv
        self.lista[num]['lines'] = num_lines
        self.save()

    def add_training_file(self, file):
        for dicline in self.lista:
            if file == dicline["file"]:
                dicline["withtrainings"] = True
                self.save()
                return

    def add_training_engines_file(self, file):
        for dicline in self.lista:
            if file == dicline["file"]:
                dicline["withtrainings_engines"] = True
                self.save()
                return


class Opening:
    def __init__(self, path_file):
        self.path_file = path_file

        self._conexion = sqlite3.connect(path_file)

        self.cache = {}
        self.max_cache = 1000
        self.del_cache = 100

        self.grupo = 0

        self.history = collections.OrderedDict()

        self.li_xpv = self.init_database()

        self.db_config_base = None
        self.db_fenvalues_base = None
        self.db_history_base = None
        self.db_cache_engines = None
        self.basePV = self.getconfig("BASEPV", "")
        self.title = self.getconfig("TITLE", os.path.basename(path_file)[:-4])

        # Check visual
        if not UtilSQL.check_table_in_db(path_file, "Flechas"):
            file_resources = Code.configuration.ficheroRecursos
            if self.db_config_base:
                self.db_config_base.close()
                self.db_config_base = None
            for tabla in ("Config", "Flechas", "Marcos", "SVGs", "Markers"):
                dbr = UtilSQL.DictSQL(path_file, tabla=tabla)
                dbv = UtilSQL.DictSQL(file_resources, tabla=tabla)
                dbr.copy_from(dbv)
                dbr.close()
                dbv.close()

        self.board = None

    @property
    def db_config(self):
        if self.db_config_base is None:
            self.db_config_base = UtilSQL.DictSQL(self.path_file, tabla="CONFIG")
        return self.db_config_base

    @property
    def db_fenvalues(self):
        if self.db_fenvalues_base is None:
            self.db_fenvalues_base = UtilSQL.DictSQL(self.path_file, tabla="FENVALUES")
        return self.db_fenvalues_base

    @property
    def db_history(self):
        if self.db_history_base is None:
            self.db_history_base = UtilSQL.DictSQL(self.path_file, tabla="HISTORY")
        return self.db_history_base

    def open_cache_engines(self):
        if self.db_cache_engines is None:
            self.db_cache_engines = UtilSQL.DictSQL(self.path_file, tabla="CACHE_ENGINES")

    def get_cache_engines(self, engine, ms, fenm2, depth=None):
        if depth:
            key = "%s-%d-%s-%d" % (engine, ms, fenm2, depth)
        else:
            key = "%s-%d-%s" % (engine, ms, fenm2)
        return self.db_cache_engines[key]

    def set_cache_engines(self, engine, ms, fenm2, move, depth=None):
        if depth:
            key = "%s-%d-%s-%d" % (engine, ms, fenm2, depth)
        else:
            key = "%s-%d-%s" % (engine, ms, fenm2)
        self.db_cache_engines[key] = move

    def reinit_cache_engines(self):
        self.open_cache_engines()
        self.db_cache_engines.zap()
        self.db_cache_engines.close()
        self.db_cache_engines = None

    def init_database(self):
        cursor = self._conexion.cursor()
        cursor.execute("pragma table_info(LINES)")
        if not cursor.fetchall():
            sql = "CREATE TABLE LINES( XPV TEXT PRIMARY KEY );"
            cursor.execute(sql)
            self._conexion.commit()
            li_xpv = []
        else:
            sql = "select XPV from LINES ORDER BY XPV"
            cursor.execute(sql)
            li_xpv = [raw[0] for raw in cursor.fetchall()]
        cursor.close()
        return li_xpv

    def pack_database(self):
        cursor = self._conexion.cursor()
        sql = "select ROWID, XPV from LINES ORDER BY XPV"
        cursor.execute(sql)
        li_xpv_r = list(cursor.fetchall())
        st_remove = set()
        for pos in range(len(li_xpv_r) - 1):
            rowid0, xpv0 = li_xpv_r[pos]
            rowid1, xpv1 = li_xpv_r[pos + 1]
            if not xpv0 or xpv1.startswith(xpv0):
                st_remove.add(rowid0)
        if st_remove:
            sql = "DELETE FROM LINES WHERE ROWID=?"
            li = [(elem,) for elem in st_remove]
            cursor.executemany(sql, li)
            self._conexion.commit()
        cursor.execute("VACUUM")
        cursor.close()

    def setdbvisual_board(self, board):
        self.board = board

    def get_others(self, game):
        liOp = ListaOpenings()
        fich = os.path.basename(self.path_file)
        pvbase = game.pv()
        liOp = [
            (dic["file"], dic["title"])
            for dic in liOp.lista
            if dic["file"] != fich and (pvbase.startswith(dic["pv"]) or dic["pv"].startswith(pvbase))
        ]
        return liOp

    def getfenvalue(self, fenm2):
        resp = self.db_fenvalues[fenm2]
        if resp and resp.get("VENTAJA") == 11:  # error antiguo
            resp["VENTAJA"] = 10
            self.setfenvalue(fenm2, resp)
        return resp if resp else {}

    def setfenvalue(self, fenm2, dic):
        if dic:
            self.db_fenvalues[fenm2] = dic
        else:
            del self.db_fenvalues[fenm2]

    def dicfenvalues(self):
        return self.db_fenvalues.as_dictionary()

    def dic_fen_comments(self):
        return {
            fenm2: reg
            for fenm2, reg in self.db_fenvalues.as_dictionary().items()
            if reg and ("COMENTARIO" in reg or "VENTAJA" in reg or "VALORACION" in reg)
        }

    def remove_analysis(self, tmpBP, mensaje):
        for n, fenm2 in enumerate(self.db_fenvalues.keys()):
            tmpBP.inc()
            tmpBP.mensaje(mensaje % n)
            if tmpBP.is_canceled():
                break
            dic = self.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                del dic["ANALISIS"]
                self.setfenvalue(fenm2, dic)
        self.pack_at_end()

    def getconfig(self, key, default=None):
        return self.db_config.get(key, default)

    def setconfig(self, key, value):
        self.db_config[key] = value

    def set_basepv(self, new_pv):
        self.setconfig("BASEPV", new_pv)
        self.basePV = new_pv

    def training(self):
        return self.getconfig("TRAINING")

    def setTraining(self, reg):
        self.setconfig("TRAINING", reg)

    def trainingEngines(self):
        return self.getconfig("TRAINING_ENGINES")

    def setTrainingEngines(self, reg):
        self.setconfig("TRAINING_ENGINES", reg)

    def preparaTraining(self, reg, procesador):
        maxmoves = reg["MAXMOVES"]
        is_white = reg["COLOR"] == "WHITE"
        is_random = reg["RANDOM"]

        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]

        if maxmoves:
            for pos, lipv in enumerate(lilipv):
                if len(lipv) > maxmoves:
                    lilipv[pos] = lipv[:maxmoves]

        # Ultimo el usuario
        for pos, lipv in enumerate(lilipv):
            if len(lipv) % 2 == (0 if is_white else 1):
                lilipv[pos] = lipv[:-1]

        # Quitamos las repetidas
        dicpv = {}
        for lipv in lilipv:
            pvmirar = "".join(lipv)
            dicpv[pvmirar] = lipv

        lilipv = []
        set_correct = set()
        for pvmirar in dicpv:
            siesta = False
            for pvotro in dicpv:
                if pvotro != pvmirar and pvotro.startswith(pvmirar):
                    siesta = True
                    break
            if not siesta:
                set_correct.add(pvmirar)

        lilipv = [value for key, value in dicpv.items() if key in set_correct]

        ligamesST = []
        ligamesSQ = []
        dicFENm2 = {}
        dicFENm2_lipv = {}
        cp = Position.Position()

        busca = " w " if is_white else " b "

        for lipv in lilipv:
            game = {}
            game["LIPV"] = lipv
            game["NOERROR"] = 0
            game["TRIES"] = []

            ligamesST.append(game)
            game = dict(game)
            ligamesSQ.append(game)

            FasterCode.set_init_fen()
            for pos, pv in enumerate(lipv, 1):
                fen = FasterCode.get_fen()
                cp.read_fen(fen)
                if busca in fen:
                    fenm2 = cp.fenm2()
                    if not (fenm2 in dicFENm2):
                        dicFENm2[fenm2] = set()
                    dicFENm2[fenm2].add(pv)
                    dicFENm2_lipv[fenm2] = lipv[:pos]
                FasterCode.make_move(pv)

        if is_random:
            random.shuffle(ligamesSQ)
            random.shuffle(ligamesST)

        reg["LIGAMES_STATIC"] = ligamesST
        reg["LIGAMES_SEQUENTIAL"] = ligamesSQ
        reg["DICFENM2"] = dicFENm2

        # bcolor = " w " if is_white else " b "
        li_train_positions = []
        for fenm2 in dicFENm2:
            data = {}
            data["FENM2"] = fenm2
            data["MOVES"] = dicFENm2[fenm2]
            data["NOERROR"] = 0
            data["TRIES"] = []
            data["LIPV"] = dicFENm2_lipv[fenm2]
            li_train_positions.append(data)
        random.shuffle(li_train_positions)
        reg["LITRAINPOSITIONS"] = li_train_positions
        reg["POS_TRAINPOSITIONS"] = 0

    def recalcFenM2(self):
        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]
        cp = Position.Position()
        dicFENm2 = {}
        if not lilipv and self.basePV:
            lilipv.append(self.basePV.split(" "))
        for lipv in lilipv:
            FasterCode.set_init_fen()
            for pv in lipv:
                fen = FasterCode.get_fen()
                cp.read_fen(fen)
                fenm2 = cp.fenm2()
                if not (fenm2 in dicFENm2):
                    dicFENm2[fenm2] = set()
                dicFENm2[fenm2].add(pv)
                FasterCode.make_move(pv)
        return dicFENm2

    def dicRepeFen(self, si_white):
        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]

        dic = {}
        busca = " w " if si_white else " b "
        for nlinea, lipv in enumerate(lilipv):
            FasterCode.set_init_fen()
            for pv in lipv:
                fen = FasterCode.get_fen()
                if busca in fen:
                    if fen not in dic:
                        dic[fen] = {}
                    dic_pv = dic[fen]
                    if pv not in dic_pv:
                        dic_pv[pv] = []
                    dic_pv[pv].append(nlinea)
                FasterCode.make_move(pv)
        d = {fen: dic_pv for fen, dic_pv in dic.items() if len(dic_pv) > 1}
        return d

    def preparaTrainingEngines(self, configuration, reg):
        reg["DICFENM2"] = self.recalcFenM2()
        reg["TIMES"] = [500, 1000, 2000, 4000, 8000]

        if reg["NUM_ENGINES"] == 0:
            reg["ENGINES"] = []
        else:
            reg["ENGINES"] = EnginesBunch.bunch(reg["KEY_ENGINE"], reg["NUM_ENGINES"], configuration.dic_engines)

    def updateTrainingEngines(self):
        reg = self.trainingEngines()
        if reg:
            reg["DICFENM2"] = self.recalcFenM2()
            self.setTrainingEngines(reg)

    def createTrainingSSP(self, reg, procesador):
        self.preparaTraining(reg, procesador)

        reg["DATECREATION"] = Util.today()
        self.setconfig("TRAINING", reg)
        self.setconfig("ULT_PACK", 100)  # Se le obliga al VACUUM

        lo = ListaOpenings()
        lo.add_training_file(os.path.basename(self.path_file))

    def createTrainingEngines(self, reg, procesador):
        self.preparaTrainingEngines(procesador.configuration, reg)
        reg["DATECREATION"] = Util.today()
        self.setTrainingEngines(reg)

        self.setconfig("ENG_LEVEL", 0)
        self.setconfig("ENG_ENGINE", 0)

        lo = ListaOpenings()
        lo.add_training_engines_file(os.path.basename(self.path_file))
        self.reinit_cache_engines()

    def withTrainings(self):
        return "TRAINING" in self.db_config

    def withTrainingsEngines(self):
        return "TRAINING_ENGINES" in self.db_config

    def updateTraining(self, procesador):
        reg = self.training()
        if reg is None:
            return
        reg1 = {}
        for key in ("MAXMOVES", "COLOR", "RANDOM"):
            reg1[key] = reg[key]
        self.preparaTraining(reg1, procesador)

        for tipo in ("LIGAMES_SEQUENTIAL", "LIGAMES_STATIC"):
            # Los que estan pero no son, los borramos
            liBorrados = []
            for pos, game in enumerate(reg[tipo]):
                pv = " ".join(game["LIPV"])
                ok = False
                for game1 in reg1[tipo]:
                    pv1 = " ".join(game1["LIPV"])
                    if pv == pv1:
                        ok = True
                        break
                if not ok:
                    liBorrados.append(pos)
            if liBorrados:
                li = reg[tipo]
                liBorrados.sort(reverse=True)
                for x in liBorrados:
                    del li[x]
                reg[tipo] = li

            # Los que son pero no estan
            liMas = []
            for game1 in reg1[tipo]:
                pv1 = " ".join(game1["LIPV"])
                ok = False
                for game in reg[tipo]:
                    pv = " ".join(game["LIPV"])
                    if pv == pv1:
                        ok = True
                        break
                if not ok:
                    liMas.append(game1)
            if liMas:
                li = reg[tipo]
                liMas.sort(reverse=True)
                for game in liMas:
                    li.insert(0, game)
                reg[tipo] = li

        reg["DICFENM2"] = reg1["DICFENM2"]

        # Posiciones

        # Estan pero no son
        liBorrados = []
        tipo = "LITRAINPOSITIONS"
        for pos, data in enumerate(reg[tipo]):
            fen = data["FENM2"]
            ok = False
            for data1 in reg1[tipo]:
                fen1 = data1["FENM2"]
                if fen == fen1:
                    ok = True
                    break
            if not ok:
                liBorrados.append(pos)
        if liBorrados:
            li = reg[tipo]
            liBorrados.sort(reverse=True)
            for x in liBorrados:
                del li[x]
            reg[tipo] = li

        # Los que son pero no estan
        liMas = []
        for data1 in reg1[tipo]:
            fen1 = data1["FENM2"]
            ok = False
            for data in reg[tipo]:
                fen = data["FENM2"]
                if fen == fen1:
                    ok = True
                    break
            if not ok:
                liMas.append(data1)
        if liMas:
            li = reg[tipo]
            li.insert(0, liMas)
            reg[tipo] = li

        self.setconfig("TRAINING", reg)
        self.pack_at_end()

    def pack_at_end(self):
        self.setconfig("ULT_PACK", 100)  # Se le obliga al VACUUM

    def settitle(self, title):
        self.setconfig("TITLE", title)

    def gettitle(self):
        return self.getconfig("TITLE")

    def setbasepv(self, basepv):
        self.setconfig("BASEPV", basepv)

    def getgamebase(self):
        base = self.getconfig("BASEPV")
        p = Game.Game()
        if base:
            p.read_pv(base)
        return p

    def add_cache(self, xpv, game):
        if len(self.cache) >= self.max_cache:
            li = list(self.cache.keys())
            for n, xpv in enumerate(li):
                del self.cache[xpv]
                if n > self.del_cache:
                    break
        self.cache[xpv] = game

    def append(self, game):
        xpv = FasterCode.pv_xpv(game.pv())
        sql = "INSERT INTO LINES( XPV ) VALUES( ? )"
        cursor = self._conexion.cursor()
        cursor.execute(sql, (xpv,))
        cursor.close()
        self._conexion.commit()
        self.li_xpv.append(xpv)
        self.li_xpv.sort()
        self.add_cache(xpv, game)

    def append_pv(self, pv):
        xpv = FasterCode.pv_xpv(pv)
        # add_pv = True
        for pos, xpv1 in enumerate(self.li_xpv):
            if xpv == xpv1 or xpv1.startswith(xpv):
                return False
            if xpv.startswith(xpv1):
                game = Game.Game()
                game.read_pv(pv)
                self.__setitem__(pos, game)
                return True
        game = Game.Game()
        game.read_pv(pv)
        self.append(game)
        return True

    def posPartida(self, game):
        # return siNueva, numlinea, siAppend
        xpv_busca = FasterCode.pv_xpv(game.pv())
        last_move = game.move(-1)
        pos = -3 if last_move.promotion else -2
        for n, xpv in enumerate(self.li_xpv):
            if xpv.startswith(xpv_busca):
                return False, n, False
            if xpv == xpv_busca[:pos]:
                return False, n, True
        return True, None, None

    def __contains__(self, xpv):
        return xpv in self.li_xpv

    def __setitem__(self, num, game_nue):
        xpv_ant = self.li_xpv[num]
        xpv_nue = FasterCode.pv_xpv(game_nue.pv())
        if xpv_nue != xpv_ant:
            if xpv_ant in self.cache:
                del self.cache[xpv_ant]
            self.li_xpv[num] = xpv_nue
            si_sort = False
            if num > 0:
                si_sort = xpv_nue < self.li_xpv[num - 1]
            if not si_sort and num < len(self.li_xpv) - 1:
                si_sort = xpv_nue > self.li_xpv[num + 1]
            if si_sort:
                self.li_xpv.sort()
                num = self.li_xpv.index(xpv_nue)
        cursor = self._conexion.cursor()
        sql = "UPDATE LINES SET XPV=? WHERE XPV=?"
        cursor.execute(sql, (xpv_nue, xpv_ant))
        self._conexion.commit()
        self.add_cache(xpv_nue, game_nue)
        cursor.close()
        return num

    def __getitem__(self, num):
        if num >= len(self.li_xpv):
            return None
        xpv = self.li_xpv[num]
        if xpv in self.cache:
            return self.cache[xpv]

        game = Game.Game()
        pv = FasterCode.xpv_pv(xpv)
        game.read_pv(pv)
        self.add_cache(xpv, game)
        return game

    def __delitem__(self, num):
        xpv = self.li_xpv[num]
        sql = "DELETE FROM LINES where XPV=?"
        cursor = self._conexion.cursor()
        cursor.execute(sql, (xpv,))
        if xpv in self.cache:
            del self.cache[xpv]
        del self.li_xpv[num]
        self._conexion.commit()
        cursor.close()

    def __len__(self):
        return len(self.li_xpv)

    def get_all_games(self):
        li_games = []
        for xpv in self.li_xpv:
            if xpv in self.cache:
                game = self.cache[xpv]
            else:
                game = Game.Game()
                pv = FasterCode.xpv_pv(xpv)
                game.read_pv(pv)
            li_games.append(game)
        return li_games

    def remove_list_lines(self, li, label):
        self.save_history(_("Removing"), label)
        li.sort(reverse=True)
        cursor = self._conexion.cursor()
        for num in li:
            xpv = self.li_xpv[num]
            sql = "DELETE FROM LINES where XPV=?"
            cursor.execute(sql, (xpv,))
            if xpv in self.cache:
                del self.cache[xpv]
            del self.li_xpv[num]
        self._conexion.commit()
        cursor.close()

    def remove_pv(self, pgn, a1h8):
        xpv = FasterCode.pv_xpv(a1h8)
        li = [pos for pos, xpv1 in enumerate(self.li_xpv) if xpv1.startswith(xpv)]
        self.remove_list_lines(li, pgn)

    def remove_lastmove(self, is_white, label):
        self.save_history(_("Removing"), label)
        n = len(self.li_xpv)
        for x in range(n - 1, -1, -1):
            xpv = self.li_xpv[x]
            pv = FasterCode.xpv_pv(xpv)
            nm = pv.count(" ")
            if nm % 2 == 0 and is_white or nm % 2 == 1 and not is_white:
                pv_nue = " ".join(pv.split(" ")[:-1])
                xpv_nue = FasterCode.pv_xpv(pv_nue)
                if xpv_nue in self.li_xpv or not xpv_nue:
                    del self.li_xpv[x]
                else:
                    self.li_xpv[x] = xpv_nue
                if xpv in self.cache:
                    del self.cache[xpv]
        self.clean()

    def list_history(self):
        return self.db_history.keys(si_ordenados=True, si_reverse=True)

    def save_history(self, *label):
        d = datetime.datetime.now()
        s = "%s-%s" % (d.strftime("%Y-%m-%d %H:%M:%S"), ",".join(label))
        self.db_history[s] = self.li_xpv[:]

    def remove_all_history(self):
        self.db_history.zap()

    def recovering_history(self, key):
        self.save_history(_("Recovering"), key)

        st_activo = set(self.li_xpv)
        li_xpv_rec = self.db_history[key]

        # se recuperan las que cumplan con base move
        if self.basePV:
            xpv_base = FasterCode.pv_xpv(self.basePV)
            li_xpv_rec = [xpv for xpv in li_xpv_rec if xpv.startswith(xpv_base)]

        st_recuperar = set(li_xpv_rec)

        cursor = self._conexion.cursor()

        # Borramos los que no estan en Recuperar
        sql = "DELETE FROM LINES where XPV=?"
        for xpv in st_activo:
            if not (xpv in st_recuperar):
                cursor.execute(sql, (xpv,))
        self._conexion.commit()

        # Mas los que no estan en Activo
        sql = "INSERT INTO LINES( XPV ) VALUES( ? )"
        for xpv in st_recuperar:
            if not (xpv in st_activo):
                cursor.execute(sql, (xpv,))
        self._conexion.commit()

        cursor.close()
        self.li_xpv = li_xpv_rec

    def close(self):
        if self._conexion:
            ult_pack = self.getconfig("ULT_PACK", 0)
            si_pack = ult_pack > 50
            self.setconfig("ULT_PACK", 0 if si_pack else ult_pack + 1)

            if self.db_config_base:
                self.db_config_base.close()
                self.db_config_base = None

            if self.db_fenvalues_base:
                self.db_fenvalues_base.close()
                self.db_fenvalues_base = None

            if self.db_cache_engines:
                self.db_cache_engines.close()
                self.db_cache_engines = None

            if self.board:
                self.board.dbvisual_close()
                self.board = None

            if si_pack:
                if len(self.db_history) > 70:
                    lik = self.db_history.keys(si_ordenados=True, si_reverse=False)
                    liremove = lik[: len(self.db_history) - 50]
                    for k in liremove:
                        del self.db_history[k]
                self.db_history_base.close()
                self.db_history_base = None

                cursor = self._conexion.cursor()
                cursor.execute("VACUUM")
                cursor.close()
                self._conexion.commit()

            else:
                if self.db_history_base:
                    self.db_history_base.close()
                    self.db_history_base = None

            self._conexion.close()
            self._conexion = None

    def import_db(self, owner, gamebase, path_db, max_depth, with_variations, with_comments):
        name = os.path.basename(path_db)

        db = DBgames.DBgames(path_db)
        self.save_history(_("Import"), _("Databases"), name)

        base = gamebase.pv() if gamebase else self.getconfig("BASEPV")

        dl_tmp = QTUtil2.BarraProgreso(owner, _("Import") + " - " + name, _("Working..."), db.all_reccount(),
                                       width=600).mostrar()

        dic_comments = {}
        for recno, game in enumerate(db.yield_games(), 1):
            dl_tmp.pon(recno)

            if dl_tmp.is_canceled():
                break

            li_pv = game.all_pv("", with_variations)
            if not game.is_fen_initial():
                continue
            for pv in li_pv:
                li = pv.split(" ")[:max_depth]
                pv = " ".join(li)

                if base and not pv.startswith(base) or base == pv:
                    continue
                xpv = FasterCode.pv_xpv(pv)
                updated = False
                for npos, xpv_ant in enumerate(self.li_xpv):
                    if xpv_ant.startswith(xpv):
                        updated = True
                        break
                    if xpv.startswith(xpv_ant) and xpv > xpv_ant:
                        self.li_xpv[npos] = xpv
                        updated = True
                        break
                if not updated:
                    if len(xpv) > 0:
                        self.li_xpv.append(xpv)

            if with_comments:
                dic_comments_game = game.all_comments(with_variations)
                for fenm2, dic in dic_comments_game.items():
                    d = self.getfenvalue(fenm2)
                    if "C" in dic:
                        d["COMENTARIO"] = dic["C"]
                        del dic["C"]
                    if "N" in dic:
                        for nag in dic["N"]:
                            if nag in (10, 14, 15, 16, 17, 18, 19):
                                d["VENTAJA"] = nag
                            elif 0 < nag < 7:
                                d["VALORACION"] = nag
                        del dic["N"]
                    if d:
                        dic_comments[fenm2] = d

        self.clean()

        dl_tmp.cerrar()
        if with_comments and dic_comments:
            self.db_fenvalues.set_faster_mode()
            um = QTUtil2.one_moment_please(owner)
            for fenm2, dic_comments_game in dic_comments.items():
                self.setfenvalue(fenm2, dic_comments_game)
            self.db_fenvalues.set_normal_mode()
            um.final()

    def import_pgn(self, owner, gamebase, path_pgn, max_depth, with_variations, with_comments):

        name = os.path.basename(path_pgn)

        dl_tmp = QTUtil2.BarraProgreso(owner, _("Import") + " - " + name, _("Working..."), Util.filesize(path_pgn),
                                       width=600).mostrar()

        self.save_history(_("Import"), _("PGN with variations"), name)

        dic_comments = {}

        base = gamebase.pv() if gamebase else self.getconfig("BASEPV")

        for n, (nbytes, game) in enumerate(Game.read_games(path_pgn)):
            dl_tmp.pon(nbytes)

            if dl_tmp.is_canceled():
                break

            li_pv = game.all_pv("", with_variations)
            if not game.is_fen_initial():
                continue
            for pv in li_pv:
                li = pv.split(" ")[:max_depth]
                pv = " ".join(li)

                if base and not pv.startswith(base) or base == pv:
                    continue
                xpv = FasterCode.pv_xpv(pv)
                updated = False
                for npos, xpv_ant in enumerate(self.li_xpv):
                    if xpv_ant.startswith(xpv):
                        updated = True
                        break
                    if xpv.startswith(xpv_ant) and xpv > xpv_ant:
                        self.li_xpv[npos] = xpv
                        updated = True
                        break
                if not updated:
                    if len(xpv) > 0:
                        self.li_xpv.append(xpv)

            if with_comments:
                dic_comments_game = game.all_comments(with_variations)
                for fenm2, dic in dic_comments_game.items():
                    d = self.getfenvalue(fenm2)
                    if "C" in dic:
                        d["COMENTARIO"] = dic["C"]
                        del dic["C"]
                    if "N" in dic:
                        for nag in dic["N"]:
                            if nag in (10, 14, 15, 16, 17, 18, 19):
                                d["VENTAJA"] = nag
                            elif 0 < nag < 7:
                                d["VALORACION"] = nag
                        del dic["N"]
                    if d:
                        dic_comments[fenm2] = d

        self.clean()

        dl_tmp.cerrar()
        if with_comments and dic_comments:
            self.db_fenvalues.set_faster_mode()
            um = QTUtil2.one_moment_please(owner)
            for fenm2, dic_comments_game in dic_comments.items():
                self.setfenvalue(fenm2, dic_comments_game)
            self.db_fenvalues.set_normal_mode()
            um.final()

    def import_pgn_comments(self, owner, path_pgn):

        dl_tmp = QTUtil2.BarraProgreso(owner, _("Import"), _("Working..."), Util.filesize(path_pgn)).mostrar()

        dic_comments = {}

        for n, (nbytes, game) in enumerate(Game.read_games(path_pgn)):
            dl_tmp.pon(nbytes)

            if dl_tmp.is_canceled():
                break

            dic_comments_game = game.all_comments(True)
            for fenm2, dic_nuevo in dic_comments_game.items():
                d_final = self.getfenvalue(fenm2)
                if "C" in dic_nuevo:
                    comment_nuevo = dic_nuevo["C"].strip()
                    comment_anterior = d_final.get("COMENTARIO", "").strip()
                    if comment_anterior and comment_nuevo not in comment_anterior:
                        comment_nuevo = f"{comment_anterior}\n-----------\n{comment_nuevo}"
                    d_final["COMENTARIO"] = comment_nuevo
                if "N" in dic_nuevo:
                    for nag in dic_nuevo["N"]:
                        if nag in (10, 14, 15, 16, 17, 18, 19):
                            d_final["VENTAJA"] = nag
                        elif 0 < nag < 7:
                            d_final["VALORACION"] = nag
                if d_final:
                    dic_comments[fenm2] = d_final

        dl_tmp.close()

        if dic_comments:
            self.db_fenvalues.set_faster_mode()
            um = QTUtil2.one_moment_please(owner)
            for fenm2, dic_comments_game in dic_comments.items():
                self.setfenvalue(fenm2, dic_comments_game)
            self.db_fenvalues.set_normal_mode()
            um.final()

    def import_other_comments(self, path_opk):
        otra = Opening(path_opk)
        self.db_fenvalues.copy_from(otra.db_fenvalues)
        self.pack_database()
        otra.close()

    def guardaPartidas(self, label, liPartidas, minMoves=0, with_history=True):
        if with_history:
            self.save_history(_("Import"), label)
        gamebase = self.getgamebase()
        sql_insert = "INSERT INTO LINES( XPV) VALUES( ? )"
        sql_update = "UPDATE LINES SET XPV=? WHERE XPV=?"
        cursor = self._conexion.cursor()
        for game in liPartidas:
            if minMoves <= len(game) > gamebase.num_moves():
                xpv = FasterCode.pv_xpv(game.pv())
                if not (xpv in self.li_xpv):
                    updated = False
                    for npos, xpv_ant in enumerate(self.li_xpv):
                        if xpv.startswith(xpv_ant):
                            cursor.execute(sql_update, (xpv, xpv_ant))
                            self.li_xpv[npos] = xpv
                            updated = True
                            break
                    if not updated:
                        cursor.execute(sql_insert, (xpv,))
                        self.li_xpv.append(xpv)

        cursor.close()
        self._conexion.commit()
        self.li_xpv.sort()

    def guardaLiXPV(self, label, liXPV):
        self.save_history(_("Import"), label)
        sql_insert = "INSERT INTO LINES( XPV) VALUES( ? )"
        sql_update = "UPDATE LINES SET XPV=? WHERE XPV=?"
        cursor = self._conexion.cursor()
        for xpv in liXPV:
            if not (xpv in self.li_xpv):
                updated = False
                for npos, xpv_ant in enumerate(self.li_xpv):
                    if xpv.startswith(xpv_ant):
                        cursor.execute(sql_update, (xpv, xpv_ant))
                        self.li_xpv[npos] = xpv
                        updated = True
                        break
                if not updated:
                    cursor.execute(sql_insert, (xpv,))
                    self.li_xpv.append(xpv)
        cursor.close()
        self._conexion.commit()
        self.li_xpv.sort()

    def import_polyglot(self, li_pv):
        self.save_history(_("Import"), _("Polyglot book"))
        li_xpv_new = [FasterCode.pv_xpv(pv) for pv in li_pv]
        self.li_xpv.extend(li_xpv_new)
        self.clean()
        return True

    def import_dbopening_explorer(self, ventana, gamebase, fichero_summary, depth, si_white, onlyone, min_moves):
        titulo = _("Importing the opening explorer of a database")
        bp = QTUtil2.BarraProgreso1(ventana, titulo)
        bp.set_total(0)
        bp.put_label(_X(_("Reading %1"), os.path.basename(fichero_summary)))
        bp.mostrar()

        db_stat = DBgamesST.TreeSTAT(fichero_summary)

        if depth == 0:
            depth = 99999

        pv_base = gamebase.pv()
        len_gamebase = len(gamebase)

        li_partidas = []

        def hazPV(lipv_ant):
            if bp.is_canceled():
                return
            n_ant = len(lipv_ant)
            si_white1 = n_ant % 2 == 0

            pv_ant = " ".join(lipv_ant) if n_ant else ""
            li_children = db_stat.children(pv_ant, False)

            if len(li_children) == 0 or len(lipv_ant) >= depth:
                game = Game.Game()
                game.read_lipv(lipv_ant)
                if len(game) > len_gamebase and len(game) >= min_moves:
                    li_partidas.append(game)
                    bp.set_total(len(li_partidas))
                    bp.pon(len(li_partidas))
                return

            if si_white1 == si_white:
                tt_max = 0
                limax = []
                for alm in li_children:
                    tt = alm.W + alm.B + alm.O + alm.D
                    if tt > tt_max:
                        tt_max = tt
                        limax = [alm]
                    elif tt == tt_max and not onlyone:
                        limax.append(alm)
                li_children = limax

            for alm in li_children:
                li = lipv_ant[:]
                li.append(alm.move)
                hazPV(li)

        hazPV(pv_base.split(" ") if pv_base else [])

        bp.put_label(_("Writing..."))
        self.guardaPartidas("%s,%s" % (_("Database opening explorer"), os.path.basename(fichero_summary)), li_partidas)
        self.pack_database()
        bp.cerrar()

        return True

    def import_other(self, path_fichero, game):
        xpvbase = FasterCode.pv_xpv(game.pv())
        tambase = len(xpvbase)
        otra = Opening(path_fichero)
        lista = []
        for n, xpv in enumerate(otra.li_xpv):
            if xpv.startswith(xpvbase) and len(xpv) > tambase:
                if not (xpv in self.li_xpv):
                    lista.append(xpv)
        self.guardaLiXPV("%s,%s" % (_("Other opening lines"), otra.title), lista)
        self.db_fenvalues.copy_from(otra.db_fenvalues)
        for tabla in ("FEN", "Flechas", "Marcos", "SVGs", "Markers"):
            dbr = UtilSQL.DictSQL(self.path_file, tabla=tabla)
            dbv = UtilSQL.DictSQL(otra.path_file, tabla=tabla)
            dbr.copy_from(dbv)
            dbr.close()
            dbv.close()
        self.pack_database()
        otra.close()

    def export_to_pgn(self, ws, result):
        li_tags = [["Event", self.title.replace('"', "")], ["Site", ""], ["Date", Util.today().strftime("%Y-%m-%d")]]
        if result:
            li_tags.append(["Result", result])

        total = len(self)

        ws.pb(total)

        alm = Util.Record()
        alm.analyze_variations = False
        alm.include_variations = True
        alm.what_variations = ALL_VARIATIONS
        alm.include_played = True
        alm.limit_include_variations = 0
        alm.info_variation = True
        alm.si_pdt = True
        alm.one_move_variation = False

        for recno in range(total):
            ws.pb_pos(recno + 1)
            if ws.pb_cancel():
                break
            game = self[recno].copia()

            li_tags[1] = ["Site", "%s %d" % (_("Line"), recno + 1)]
            for tag, value in li_tags:
                game.set_tag(tag, value)

            for move in game.li_moves:
                fenm2 = move.position.fenm2()
                dic = self.getfenvalue(fenm2)
                if dic:
                    comment = dic.get("COMENTARIO")
                    if comment:
                        move.set_comment(comment)
                    nag = dic.get("VALORACION")
                    if nag:
                        move.add_nag(nag)
                    nag = dic.get("VENTAJA")
                    if nag:
                        move.add_nag(nag)
                    analisis = dic.get("ANALISIS")
                    if analisis is not None:
                        move.analysis = analisis, -1
                        move.analisis2variantes(alm, False)

            if recno > 0 or not ws.is_new:
                ws.write("\n\n")
            tags = "".join(['[%s "%s"]\n' % (k, v) for k, v in li_tags])
            ws.write(tags)
            ws.write("\n%s" % game.pgn_base())

        ws.pb_close()

    def exportar_pgn_one(self, ws, nline, pos_move, result):

        # Removing the lines with not begining
        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]
        base_lipv = lilipv[nline]
        new_lilipv = []
        for pos_line, lipv in enumerate(lilipv):
            if pos_line == nline:
                continue
            if len(lipv) < pos_move + 1:
                continue
            ok = True
            for pos in range(pos_move):
                if lipv[pos] != base_lipv[pos]:
                    ok = False
                    break
            if ok:
                new_lilipv.append(lipv)
        lilipv = new_lilipv
        total = len(lilipv)
        ws.pb(total)

        def game_add_lipv(xgame: Game.Game, xli_pv):
            xmove: Move.Move
            for pos, xmove in enumerate(xgame.li_moves):
                if xmove.movimiento() != xli_pv[pos]:
                    if pos == 0 or pos < pos_move:
                        return
                    xli_pv_parcial = xli_pv[pos:]
                    variations = xmove.variations
                    variation: Game.Game
                    for variation in variations.li_variations:
                        if variation and variation.li_moves[0].movimiento() == xli_pv_parcial[0]:
                            game_add_lipv(variation, xli_pv_parcial)
                            return
                    variation_new = Game.Game(first_position=xmove.position_before)
                    variation_new.read_lipv(xli_pv_parcial)
                    xmove.add_variation(variation_new)
                    return

        def add_coments(xgame):
            for xmove in xgame.li_moves:
                fenm2 = xmove.position.fenm2()
                dic = self.getfenvalue(fenm2)
                if dic:
                    comment = dic.get("COMENTARIO")
                    if comment:
                        xmove.set_comment(comment)
                    nag = dic.get("VALORACION")
                    if nag:
                        xmove.add_nag(nag)
                    nag = dic.get("VENTAJA")
                    if nag:
                        xmove.add_nag(nag)

                for variation in xmove.variations.li_variations:
                    add_coments(variation)

        game_main = Game.Game()
        game_main.read_pv(" ".join(base_lipv))

        for recno in range(total):
            ws.pb_pos(recno + 1)
            if ws.pb_cancel():
                return False

            li_pv = lilipv[recno]

            game_add_lipv(game_main, li_pv)

        add_coments(game_main)

        game_main.set_tag("Site", Code.lucas_chess)
        game_main.set_tag("Event", self.title)
        if result:
            game_main.set_tag("Result", result)

        if not ws.is_new:
            ws.write("\n\n")
        tags = "".join(['[%s "%s"]\n' % (k, v) for k, v in game_main.li_tags])
        ws.write(tags)
        ws.write("\n%s" % game_main.pgn_base())

        ws.pb_close()

    def remove_info(self, is_comments, is_ratings, is_analysis, is_unused):
        st_fen = self.get_all_fen() if is_unused else None

        self.db_fenvalues.set_faster_mode()
        dic_total = self.db_fenvalues.as_dictionary()
        for fenm2, dic in dic_total.items():
            if is_unused and fenm2 not in st_fen:
                dic = None
            if dic:
                def remove(keyr):
                    if keyr in dic:
                        del dic[keyr]

                if is_comments:
                    remove("COMENTARIO")
                if is_ratings:
                    remove("VALORACION")
                    remove("VENTAJA")
                if is_analysis:
                    remove("ANALISIS")

                for key in ("COMENTARIO", "VALORACION", "VENTAJA", "ANALISIS"):
                    if key in dic and not dic[key]:
                        del dic[key]

                if dic:
                    self.db_fenvalues[fenm2] = dic

            if not dic:
                del self.db_fenvalues[fenm2]

        self.db_fenvalues.set_normal_mode()
        self.db_fenvalues.pack()

    def transpositions(self):
        self.save_history(_("Complete with transpositions"))
        for una in range(2):  # dos pasadas
            lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]
            p = Position.Position()
            dir_post = collections.defaultdict(set)
            dir_prev = collections.defaultdict(set)
            for lipv in lilipv:
                FasterCode.set_init_fen()
                s0 = set()
                for pos, a1h8 in enumerate(lipv):
                    FasterCode.make_move(a1h8)
                    fen = FasterCode.get_fen()
                    fenm2 = FasterCode.fen_fenm2(fen)
                    if not fenm2.endswith("-"):  # enpassant imposibles
                        p.read_fen(fen)
                        fenm2 = p.fenm2()
                    if fenm2 in s0:
                        break
                    s0.add(fenm2)
                    dir_prev[fenm2].add(" ".join(lipv[:pos + 1]))
                    if pos < len(lipv) - 1:
                        dir_post[fenm2].add(" ".join(lipv[pos + 1:]))
            st_pv = set()
            for fenm2, li_pv_prev in dir_prev.items():
                for pv_prev in li_pv_prev:
                    for pv_post in dir_post[fenm2]:
                        a1h8 = pv_prev + " " + pv_post
                        st_pv.add(a1h8)
            self.li_xpv = [FasterCode.pv_xpv(pv) for pv in st_pv]
            self.clean()

    def clean(self):
        li_new = []
        if self.li_xpv:
            self.li_xpv.sort()
            for pos, xpv in enumerate(self.li_xpv[:-1]):
                if not self.li_xpv[pos + 1].startswith(xpv):
                    li_new.append(xpv)
            li_new.append(self.li_xpv[-1])
        self.li_xpv = li_new
        self.remove_all_lines()
        sql_insert = "INSERT INTO LINES(XPV) VALUES( ? )"
        for xpv in self.li_xpv:
            self._conexion.execute(sql_insert, (xpv,))
        self._conexion.commit()
        self.pack_at_end()

    def remove_all_lines(self):
        self._conexion.execute("DELETE FROM LINES")
        self.cache = {}
        self._conexion.commit()

    def lines_to_remove(self, a1h8):
        xpv = FasterCode.pv_xpv(a1h8)
        li = [pos for pos, xpv1 in enumerate(self.li_xpv) if not xpv1.startswith(xpv)]
        return li

    def get_all_fen(self):
        st_fen_m2 = set()
        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]
        p = Position.Position()
        for lipv in lilipv:
            FasterCode.set_init_fen()
            for pv in lipv:
                FasterCode.make_move(pv)
                fen = FasterCode.get_fen()
                fenm2 = FasterCode.fen_fenm2(fen)
                if not fenm2.endswith("-"):
                    p.read_fen(fen)
                    fenm2 = p.fenm2()
                st_fen_m2.add(fenm2)
        return st_fen_m2

    def get_numlines_pv(self, lipv, base=1):
        xpv = FasterCode.pv_xpv(" ".join(lipv))
        li = [num for num, xpv0 in enumerate(self.li_xpv, base) if xpv0.startswith(xpv)]
        return li

    def totree(self, um):
        parent = ItemTree(None, None, None, None, WHITE)
        dic = OpeningsStd.ap.dic_fenm2_op
        translated = Code.configuration.x_translator != "en" and not Code.configuration.x_pgn_english
        if Code.configuration.x_pgn_withfigurines:
            translated = False

        game = Game.Game() if translated else None

        for xpv in self.li_xpv:
            if um.is_canceled():
                break
            lipv = FasterCode.xpv_pv(xpv).split(" ")
            if translated:
                game.reset()
                game.read_lipv(lipv)
                lipgn = [(str(pos // 2 + 1) + "." if pos % 2 == 0 else "") + move.pgn_translated()
                         for pos, move in enumerate(game.li_moves)]

            else:
                lipgn = FasterCode.xpv_pgn(xpv).replace("\n", " ").strip().split(" ")
            linom = []
            FasterCode.set_init_fen()
            for pv in lipv:
                FasterCode.make_move(pv)
                fen = FasterCode.get_fen()
                fenm2 = FasterCode.fen_fenm2(fen)
                linom.append(dic[fenm2].tr_name if fenm2 in dic else "")
            parent.add_list(lipv, lipgn, linom)
        return parent

    def dic_fenm2_moves(self):
        dic = collections.defaultdict(set)
        for xpv in self.li_xpv:
            lipv = FasterCode.xpv_pv(xpv).split(" ")
            FasterCode.set_init_fen()
            fen = FasterCode.get_fen()
            fenm2 = FasterCode.fen_fenm2(fen)
            p = Position.Position()
            for pos_next, pv in enumerate(lipv):
                dic[fenm2].add(pv)
                FasterCode.make_move(pv)
                fen = FasterCode.get_fen()
                fenm2 = FasterCode.fen_fenm2(fen)
                if not fenm2.endswith("-"):
                    p.read_fen(fen)
                    fenm2 = p.fenm2()
        return dic
