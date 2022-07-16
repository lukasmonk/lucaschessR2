import collections
import datetime
import os
import random
import shutil
import sqlite3

import FasterCode

import Code
from Code import Util
from Code.Base import Game, Position
from Code.Databases import DBgamesST
from Code.Engines import EnginesBunch
from Code.Openings import OpeningsStd
from Code.QT import QTUtil2
from Code.SQL import UtilSQL


class ListaOpenings:
    def __init__(self, configuration):
        self.folder = configuration.folder_openings()
        if not self.folder or not os.path.isdir(self.folder):
            self.folder = configuration.folder_base_openings

        self.file = os.path.join(self.folder, "openinglines.pk")

        self.lista = Util.restore_pickle(self.file)
        if self.lista is None:
            self.lista = self.read()  # file, lines, title, pv
            self.save()
        else:
            self.testdates()

    def testdates(self):
        index_date = Util.datefile(self.file)

        for pos, dic in enumerate(self.lista):
            pathfile = os.path.join(self.folder, dic["file"])
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
        os.remove(os.path.join(self.folder, dicline["file"]))
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
        while os.path.isfile(os.path.join(self.folder, file)):
            num += 1
            file = plant % num
        return file

    def filepath(self, num):
        return os.path.join(self.folder, self.lista[num]["file"])

    def new(self, file, basepv, title):
        dicline = {"file": file, "pv": basepv, "title": title, "lines": 0, "withtrainings": False}
        self.lista.append(dicline)
        op = Opening(self.filepath(len(self.lista) - 1))
        op.setbasepv(basepv)
        op.settitle(title)
        op.close()
        self.save()

    def copy(self, pos):
        dicline = dict(self.lista[pos])
        base = dicline["file"][:-3]
        if base.split("-")[-1].isdigit():
            li = base.split("-")
            base = "-".join(li[:-1])
        filenew = "%s-1.opk" % base
        n = 1
        while os.path.isfile(os.path.join(self.folder, filenew)):
            filenew = "%s-%d.opk" % (base, n)
            n += 1
        try:
            shutil.copy(self.filepath(pos), os.path.join(self.folder, filenew))
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
    def __init__(self, nom_fichero):
        self.nom_fichero = nom_fichero

        self._conexion = sqlite3.connect(nom_fichero)

        self.cache = {}
        self.max_cache = 1000
        self.del_cache = 100

        self.grupo = 0

        self.history = collections.OrderedDict()

        self.li_xpv = self.init_database()

        self.db_config = UtilSQL.DictSQL(nom_fichero, tabla="CONFIG")
        self.db_fenvalues = UtilSQL.DictSQL(nom_fichero, tabla="FENVALUES")
        self.db_history = UtilSQL.DictSQL(nom_fichero, tabla="HISTORY")
        self.db_cache_engines = None
        self.basePV = self.getconfig("BASEPV", "")
        self.title = self.getconfig("TITLE", os.path.basename(nom_fichero)[:-4])

        # Check visual
        if not UtilSQL.check_table_in_db(nom_fichero, "Flechas"):
            file_resources = Code.configuration.ficheroRecursos
            for tabla in ("Config", "Flechas", "Marcos", "SVGs", "Markers"):
                dbr = UtilSQL.DictSQL(nom_fichero, tabla=tabla)
                dbv = UtilSQL.DictSQL(file_resources, tabla=tabla)
                dbr.copy_from(dbv)
                dbr.close()
                dbv.close()

        self.board = None

    def open_cache_engines(self):
        if self.db_cache_engines is None:
            self.db_cache_engines = UtilSQL.DictSQL(self.nom_fichero, tabla="CACHE_ENGINES")

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

    def setdbVisual_Board(self, board):
        self.board = board

    def getOtras(self, configuration, game):
        liOp = ListaOpenings(configuration)
        fich = os.path.basename(self.nom_fichero)
        pvbase = game.pv()
        liOp = [
            (dic["file"], dic["title"])
            for dic in liOp.lista
            if dic["file"] != fich and (pvbase.startswith(dic["pv"]) or dic["pv"].startswith(pvbase))
        ]
        return liOp

    def getfenvalue(self, fenm2):
        resp = self.db_fenvalues[fenm2]
        return resp if resp else {}

    def setfenvalue(self, fenm2, dic):
        self.db_fenvalues[fenm2] = dic

    def removeAnalisis(self, tmpBP, mensaje):
        for n, fenm2 in enumerate(self.db_fenvalues.keys()):
            tmpBP.inc()
            tmpBP.mensaje(mensaje % n)
            if tmpBP.is_canceled():
                break
            dic = self.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                del dic["ANALISIS"]
                self.setfenvalue(fenm2, dic)
        self.packAlTerminar()

    def getconfig(self, key, default=None):
        return self.db_config.get(key, default)

    def setconfig(self, key, value):
        self.db_config[key] = value

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
        siRandom = reg["RANDOM"]

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
            for pv in lipv:
                fen = FasterCode.get_fen()
                cp.read_fen(fen)
                if busca in fen:
                    fenm2 = cp.fenm2()
                    if not (fenm2 in dicFENm2):
                        dicFENm2[fenm2] = set()
                    dicFENm2[fenm2].add(pv)
                FasterCode.make_move(pv)

        if siRandom:
            random.shuffle(ligamesSQ)
            random.shuffle(ligamesST)

        reg["LIGAMES_STATIC"] = ligamesST
        reg["LIGAMES_SEQUENTIAL"] = ligamesSQ
        reg["DICFENM2"] = dicFENm2

        # bcolor = " w " if is_white else " b "
        liTrainPositions = []
        for fenm2 in dicFENm2:
            data = {}
            data["FENM2"] = fenm2
            data["MOVES"] = dicFENm2[fenm2]
            data["NOERROR"] = 0
            data["TRIES"] = []
            liTrainPositions.append(data)
        random.shuffle(liTrainPositions)
        reg["LITRAINPOSITIONS"] = liTrainPositions
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
                    if not (fen in dic):
                        dic[fen] = {}
                    dicPV = dic[fen]
                    if not (pv in dicPV):
                        dicPV[pv] = []
                    dicPV[pv].append(nlinea)
                FasterCode.make_move(pv)
        d = {}
        for fen, dicPV in dic.items():
            if len(dicPV) > 1:
                d[fen] = dicPV
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

        lo = ListaOpenings(procesador.configuration)
        lo.add_training_file(os.path.basename(self.nom_fichero))

    def createTrainingEngines(self, reg, procesador):
        self.preparaTrainingEngines(procesador.configuration, reg)
        reg["DATECREATION"] = Util.today()
        self.setTrainingEngines(reg)

        self.setconfig("ENG_LEVEL", 0)
        self.setconfig("ENG_ENGINE", 0)

        lo = ListaOpenings(procesador.configuration)
        lo.add_training_engines_file(os.path.basename(self.nom_fichero))
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
                liMas.append(data)
        if liMas:
            li = reg[tipo]
            li.insert(0, liMas)
            reg[tipo] = li

        self.setconfig("TRAINING", reg)
        self.packAlTerminar()

    def packAlTerminar(self):
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

    def removeLines(self, li, label):
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

    def remove_lastmove(self, is_white, label):
        self.save_history(_("Removing"), label)
        n = len(self.li_xpv)
        cursor = self._conexion.cursor()
        for x in range(n - 1, -1, -1):
            xpv = self.li_xpv[x]
            pv = FasterCode.xpv_pv(xpv)
            nm = pv.count(" ")
            if nm % 2 == 0 and is_white or nm % 2 == 1 and not is_white:
                pv_nue = " ".join(pv.split(" ")[:-1])
                xpv_nue = FasterCode.pv_xpv(pv_nue)
                if xpv_nue in self.li_xpv or not xpv_nue:
                    sql = "DELETE FROM LINES where XPV=?"
                    cursor.execute(sql, (xpv,))
                    del self.li_xpv[x]
                else:
                    sql = "UPDATE LINES SET XPV=? WHERE XPV=?"
                    cursor.execute(sql, (xpv_nue, xpv))
                    self.li_xpv[x] = xpv_nue
                if xpv in self.cache:
                    del self.cache[xpv]
        self.li_xpv.sort()
        self._conexion.commit()
        cursor.close()

    def list_history(self):
        return self.db_history.keys(si_ordenados=True, si_reverse=True)

    def save_history(self, *label):
        d = datetime.datetime.now()
        s = "%s-%s" % (d.strftime("%Y-%m-%d %H:%M:%S"), ",".join(label))
        self.db_history[s] = self.li_xpv[:]

    def recovering_history(self, key):
        self.save_history(_("Recovering"), key)

        stActivo = set(self.li_xpv)
        li_xpv_rec = self.db_history[key]
        stRecuperar = set(li_xpv_rec)

        cursor = self._conexion.cursor()

        # Borramos los que no estan en Recuperar
        sql = "DELETE FROM LINES where XPV=?"
        for xpv in stActivo:
            if not (xpv in stRecuperar):
                cursor.execute(sql, (xpv,))
        self._conexion.commit()

        # Mas los que no estan en Activo
        sql = "INSERT INTO LINES( XPV ) VALUES( ? )"
        for xpv in stRecuperar:
            if not (xpv in stActivo):
                cursor.execute(sql, (xpv,))
        self._conexion.commit()

        cursor.close()
        self.li_xpv = li_xpv_rec

    def close(self):
        if self._conexion:
            ult_pack = self.getconfig("ULT_PACK", 0)
            si_pack = ult_pack > 50
            self.setconfig("ULT_PACK", 0 if si_pack else ult_pack + 1)
            self.db_config.close()
            self.db_config = None

            self.db_fenvalues.close()
            self.db_fenvalues = None

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
                self.db_history.close()

                cursor = self._conexion.cursor()
                cursor.execute("VACUUM")
                cursor.close()
                self._conexion.commit()

            else:
                self.db_history.close()

            self._conexion.close()
            self._conexion = None

    def importarPGN(self, owner, gamebase, path_pgn, max_depth, with_variations, with_comments):

        dlTmp = QTUtil2.BarraProgreso(owner, _("Import"), _("Working..."), Util.filesize(path_pgn)).mostrar()

        self.save_history(_("Import"), _("PGN with variations"), os.path.basename(path_pgn))

        dic_comments = {}

        cursor = self._conexion.cursor()

        base = gamebase.pv() if gamebase else self.getconfig("BASEPV")

        sql_insert = "INSERT INTO LINES( XPV ) VALUES( ? )"
        sql_update = "UPDATE LINES SET XPV=? WHERE XPV=?"

        for n, (nbytes, game) in enumerate(Game.read_games(path_pgn)):
            dlTmp.pon(nbytes)

            li_pv = game.all_pv("", with_variations)
            if not game.siFenInicial():
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
                        cursor.execute(sql_update, (xpv, xpv_ant))
                        self.li_xpv[npos] = xpv
                        updated = True
                        break
                if not updated:
                    if len(xpv) > 0:
                        cursor.execute(sql_insert, (xpv,))
                        self.li_xpv.append(xpv)

            if with_comments:
                dic_comments_game = game.all_comments(with_variations)
                for fenm2, dic in dic_comments_game.items():
                    d = self.getfenvalue(fenm2)
                    if "C" in dic:
                        d["COMENTARIO"] = dic["C"]
                    if "N" in dic:
                        for nag in dic["N"]:
                            if nag in (11, 14, 15, 16, 17, 18, 19):
                                d["VENTAJA"] = nag
                            elif 0 < nag < 7:
                                d["VALORACION"] = nag
                    if d:
                        dic_comments[fenm2] = d

            if n % 50:
                self._conexion.commit()

        cursor.close()
        self.li_xpv.sort()
        self._conexion.commit()
        dlTmp.cerrar()
        if with_comments and dic_comments:
            self.db_fenvalues.set_faster_mode()
            um = QTUtil2.unMomento(owner)
            for fenm2, dic_comments_game in dic_comments.items():
                self.setfenvalue(fenm2, dic_comments_game)
            self.db_fenvalues.set_normal_mode()
            um.final()

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

    def import_polyglot(
        self, ventana, game, bookW, bookB, titulo, depth, siWhite, onlyone, minMoves, excl_transpositions
    ):
        bp = QTUtil2.BarraProgreso1(ventana, titulo, formato1="%m")
        bp.ponTotal(0)
        bp.ponRotulo(_X(_("Reading %1"), "..."))
        bp.mostrar()

        st_fenm2 = set()
        set_fen = FasterCode.set_fen
        make_move = FasterCode.make_move
        get_fen = FasterCode.get_fen
        control = Util.Record()
        control.liPartidas = []
        control.num_games = 0
        control.with_history = True
        control.label = "%s,%s,%s" % (_("Polyglot book"), bookW.name, bookB.name)

        def hazFEN(fen, lipv_ant, control):
            if bp.is_canceled():
                return
            if len(lipv_ant) > depth:
                return
            if excl_transpositions:
                fen_m2 = FasterCode.fen_fenm2(fen)
                if fen_m2 in st_fenm2:
                    return
                st_fenm2.add(fen_m2)

            siWhite1 = " w " in fen
            book = bookW if siWhite1 else bookB
            li_posible_moves = book.miraListaPV(fen, siWhite1 == siWhite, onlyone=onlyone)
            if li_posible_moves and len(lipv_ant) < depth:
                for pv in li_posible_moves:
                    set_fen(fen)
                    make_move(pv)
                    fenN = get_fen()
                    lipv_nue = lipv_ant[:]
                    lipv_nue.append(pv)
                    hazFEN(fenN, lipv_nue, control)
            else:
                p = Game.Game()
                p.leerLIPV(lipv_ant)
                if p.si3repetidas():
                    return
                control.liPartidas.append(p)
                control.num_games += 1
                bp.ponTotal(control.num_games)
                bp.pon(control.num_games)
                if control.num_games and control.num_games % 3751 == 0:
                    self.guardaPartidas(control.label, control.liPartidas, minMoves, with_history=control.with_history)
                    control.liPartidas = []
                    control.with_history = False

        li_games = self.get_all_games() if game is None else [game]

        for game in li_games:
            cp = game.last_position
            try:
                hazFEN(cp.fen(), game.lipv(), control)
            except RecursionError:
                pass

        bp.ponRotulo(_("Writing..."))

        if control.liPartidas:
            self.guardaPartidas(control.label, control.liPartidas, minMoves, with_history=control.with_history)
        bp.cerrar()

        return True

    def importarSummary(self, ventana, gamebase, ficheroSummary, depth, siWhite, onlyone, minMoves):
        titulo = _("Importing the summary of a database")
        bp = QTUtil2.BarraProgreso1(ventana, titulo)
        bp.ponTotal(0)
        bp.ponRotulo(_X(_("Reading %1"), os.path.basename(ficheroSummary)))
        bp.mostrar()

        db_stat = DBgamesST.TreeSTAT(ficheroSummary)

        if depth == 0:
            depth = 99999

        pvBase = gamebase.pv()
        len_gamebase = len(gamebase)

        liPartidas = []

        def hazPV(lipv_ant):
            if bp.is_canceled():
                return
            n_ant = len(lipv_ant)
            siWhite1 = n_ant % 2 == 0

            pv_ant = " ".join(lipv_ant) if n_ant else ""
            liChildren = db_stat.children(pv_ant, False)

            if len(liChildren) == 0 or len(lipv_ant) > depth:
                p = Game.Game()
                p.leerLIPV(lipv_ant)
                if len(p) > len_gamebase:
                    liPartidas.append(p)
                    bp.ponTotal(len(liPartidas))
                    bp.pon(len(liPartidas))
                return

            if siWhite1 == siWhite:
                tt_max = 0
                limax = []
                for alm in liChildren:
                    tt = alm.W + alm.B + alm.O + alm.D
                    if tt > tt_max:
                        tt_max = tt
                        limax = [alm]
                    elif tt == tt_max and not onlyone:
                        limax.append(alm)
                liChildren = limax

            for alm in liChildren:
                li = lipv_ant[:]
                li.append(alm.move)
                hazPV(li)

        hazPV(pvBase.split(" ") if pvBase else [])

        bp.ponRotulo(_("Writing..."))
        self.guardaPartidas("%s,%s" % (_("Database summary"), os.path.basename(ficheroSummary)), liPartidas)
        bp.cerrar()

        return True

    def importarOtra(self, pathFichero, game):
        xpvbase = FasterCode.pv_xpv(game.pv())
        tambase = len(xpvbase)
        otra = Opening(pathFichero)
        lista = []
        for n, xpv in enumerate(otra.li_xpv):
            if xpv.startswith(xpvbase) and len(xpv) > tambase:
                if not (xpv in self.li_xpv):
                    lista.append(xpv)
        self.guardaLiXPV("%s,%s" % (_("Other opening lines"), otra.title), lista)
        self.db_fenvalues.copy_from(otra.db_fenvalues)
        otra.close()

    def exportarPGN(self, ws, result):
        liTags = [["Event", self.title.replace('"', "")], ["Site", ""], ["Date", Util.today().strftime("%Y-%m-%d")]]
        if result:
            liTags.append(["Result", result])

        total = len(self)

        ws.pb(total)

        alm = Util.Record()
        alm.info_variation = True
        alm.best_variation = False
        alm.one_move_variation = False
        alm.si_pdt = True

        for recno in range(total):
            ws.pb_pos(recno + 1)
            if ws.pb_cancel():
                break
            game = self[recno].copia()

            liTags[1] = ["Site", "%s %d" % (_("Line"), recno + 1)]
            for tag, value in liTags:
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
            tags = "".join(['[%s "%s"]\n' % (k, v) for k, v in liTags])
            ws.write(tags)
            ws.write("\n%s" % game.pgnBase())

        ws.pb_close()

    def getAllFen(self):
        stFENm2 = set()
        lilipv = [FasterCode.xpv_pv(xpv).split(" ") for xpv in self.li_xpv]
        for lipv in lilipv:
            FasterCode.set_init_fen()
            for pv in lipv:
                FasterCode.make_move(pv)
                fen = FasterCode.get_fen()
                fenm2 = FasterCode.fen_fenm2(fen)
                stFENm2.add(fenm2)
        return stFENm2

    def getNumLinesPV(self, lipv, base=1):
        xpv = FasterCode.pv_xpv(" ".join(lipv))
        li = [num for num, xpv0 in enumerate(self.li_xpv, base) if xpv0.startswith(xpv)]
        return li

    def totree(self):
        parent = ItemTree(None, None, None, None)
        dic = OpeningsStd.ap.dic_fenm2_op
        for xpv in self.li_xpv:
            lipv = FasterCode.xpv_pv(xpv).split(" ")
            lipgn = FasterCode.xpv_pgn(xpv).replace("\n", " ").strip().split(" ")
            linom = []
            FasterCode.set_init_fen()
            for pv in lipv:
                FasterCode.make_move(pv)
                fen = FasterCode.get_fen()
                fenm2 = FasterCode.fen_fenm2(fen)
                linom.append(dic[fenm2].tr_name if fenm2 in dic else "")
            parent.addLista(lipv, lipgn, linom)
        return parent


class ItemTree:
    def __init__(self, parent, move, pgn, opening):
        self.move = move
        self.pgn = pgn
        self.parent = parent
        self.opening = opening
        self.dicHijos = {}
        self.item = None

    def add(self, move, pgn, opening):
        if not (move in self.dicHijos):
            self.dicHijos[move] = ItemTree(self, move, pgn, opening)
        return self.dicHijos[move]

    def addLista(self, limoves, lipgn, liop):
        n = len(limoves)
        if n > 0:
            item = self.add(limoves[0], lipgn[0], liop[0])
            if n > 1:
                item.addLista(limoves[1:], lipgn[1:], liop[1:])

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

    def listaPV(self):
        li = []
        if self.move:
            li.append(self.move)

        item = self.parent
        while item is not None:
            if item.move:
                li.append(item.move)
            item = item.parent
        return li[::-1]
