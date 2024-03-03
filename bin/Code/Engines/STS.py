import collections
import os

import Code
from Code import Util
from Code.Engines import Engines


class Elem:
    def __init__(self, linea):
        self._fen, results = linea.strip().split("|")

        results = results.replace(" ", "")
        mx = 0
        dr = {}
        for resp in results.split(","):
            pv, pts = resp.split("=")
            pts = int(pts)
            dr[pv] = pts
            if pts > mx:
                mx = pts
        self._dicResults = dr
        self._maxpts = mx

    @property
    def fen(self):
        return self._fen

    @property
    def dicResults(self):
        return self._dicResults

    def points(self, a1h8):
        return self._maxpts, self._dicResults.get(a1h8, 0)

    @property
    def maxpts(self):
        return self._maxpts

    def bestA1H8(self):
        xa1h8 = ""
        xpt = 0
        for a1h8, pt in self._dicResults.items():
            if pt > xpt:
                xa1h8 = a1h8
                xpt = pt
        return xpt, xa1h8


class Group:
    def __init__(self, name, lines):
        self._name = name
        self._liElem = []
        for line in lines:
            self._liElem.append(Elem(line))

    @property
    def name(self):
        num, nom = self._name.split(".")
        return _F(nom.strip())

    def element(self, num):
        return self._liElem[num]

    def points(self, nelem, a1h8):
        elem = self._liElem[nelem]
        return elem.points(a1h8)


class Groups:
    def __init__(self, txt=None):
        if txt is None:
            with open(Code.path_resource("IntFiles", "STS.ini")) as f:
                txt = f.read()
        dic = collections.OrderedDict()
        for linea in txt.split("\n"):
            linea = linea.strip()
            if linea:
                if linea.startswith("["):
                    key = linea[1:-1]
                    dic[key] = []
                else:
                    dic[key].append(linea)
        self.lista = []
        for k in dic:
            num, key = k.split(".")
            key = key.strip()
            # g = Group(key, dic[k])
            g = Group(k, dic[k])
            self.lista.append(g)
        self._txt = txt

    def group(self, num):
        return self.lista[num]

    def __len__(self):
        return len(self.lista)

    def save(self):
        return self._txt

    def fen(self, ngroup, nfen):
        return self.lista[ngroup].element(nfen)


class ResultGroup:
    def __init__(self):
        self._dicElem = {}

    def elem(self, num, valor=None):
        if valor is not None:
            self._dicElem[num] = valor
        return self._dicElem.get(num, None)

    def save(self):
        dic = {"DICELEM": self._dicElem}
        return dic

    def restore(self, dic):
        self._dicElem = dic["DICELEM"]

    def __len__(self):
        return len(self._dicElem)

    def points(self, group):
        tt = 0
        tp = 0
        for num, a1h8 in self._dicElem.items():
            t, p = group.points(num, a1h8)
            tt += t
            tp += p
        return tt, tp


class Results:
    def __init__(self, ngroups):
        self._liResultGroups = []
        for ngroup in range(ngroups):
            self._liResultGroups.append(ResultGroup())

    def save(self):
        li = []
        for resultGroup in self._liResultGroups:
            li.append(resultGroup.save())
        return li

    def restore(self, li):
        self._liResultGroups = []
        for savegroup in li:
            resultGroup = ResultGroup()
            resultGroup.restore(savegroup)
            self._liResultGroups.append(resultGroup)

    def donePositionsGroup(self, ngroup):
        resultGroup = self._liResultGroups[ngroup]
        return len(resultGroup)

    def numPointsGroup(self, group, ngroup):
        resultGroup = self._liResultGroups[ngroup]
        return resultGroup.points(group)

    def resoultGroup(self, ngroup):
        return self._liResultGroups[ngroup]


class Work:
    def __init__(self, ngroups):
        self.me = None
        self.ref = ""
        self.info = ""
        self.seconds = 0.0
        self.depth = 3
        self.ini = 0
        self.end = 99
        self.results = Results(ngroups)
        self.liGroupActive = [True] * ngroups
        self.ngroups = ngroups
        self.workTime = 0.0

    def restore(self, dic):
        self.ref = dic["REF"]
        self.info = dic["INFO"]
        self.seconds = dic["SECONDS"]
        self.depth = dic["DEPTH"]
        self.ini = dic["INI"]
        self.end = dic["END"]
        self.results = Results(15)  # 15 = cualquier number
        self.results.restore(dic["RESULTS"])
        self.liGroupActive = dic["GROUPACTIVE"]
        self.me = Engines.engine_from_txt(dic["ENGINE"])
        self.workTime = dic.get("WORKTIME", 0.0)

    def save(self):
        dic = {}
        dic["REF"] = self.ref
        dic["INFO"] = self.info
        dic["SECONDS"] = self.seconds
        dic["DEPTH"] = self.depth
        dic["ENGINE"] = self.me.save()
        dic["INI"] = self.ini
        dic["END"] = self.end
        dic["RESULTS"] = self.results.save()
        dic["GROUPACTIVE"] = self.liGroupActive
        dic["WORKTIME"] = self.workTime
        return dic

    def clone(self):
        w = Work(self.ngroups)
        antResults = self.results
        self.results = Results(15)
        w.restore(self.save())
        self.results = antResults
        return w

    def numPositions(self):
        return self.end - self.ini + 1

    def donePositionsGroup(self, ngroup):
        return self.results.donePositionsGroup(ngroup)

    def numPointsGroup(self, group, ngroup):
        return self.results.numPointsGroup(group, ngroup)

    def isGroupActive(self, ngroup):
        return self.liGroupActive[ngroup]

    def siguientePosicion(self, ngroup):
        if not self.liGroupActive[ngroup]:
            return None
        resoultGroup = self.results.resoultGroup(ngroup)
        for x in range(self.ini, self.end + 1):
            elem = resoultGroup.elem(x)
            if elem is None:
                return x
        return None

    def configEngine(self):
        return self.me

    def pathToExe(self):
        return self.me.path_exe

    def setResult(self, ngroup, nfen, a1h8, ts):
        resoultGroup = self.results.resoultGroup(ngroup)
        resoultGroup.elem(nfen, a1h8)
        self.workTime += ts


class Works:
    def __init__(self):
        self.lista = []

    def restore(self, li):
        self.lista = []
        for dic in li:
            work = Work(15)  # 15 puede ser cualquier number, se determina el n. de grupos con restore
            work.restore(dic)
            self.lista.append(work)

    def save(self):
        li = []
        for work in self.lista:
            li.append(work.save())
        return li

    def new(self, work):
        self.lista.append(work)

    def __len__(self):
        return len(self.lista)

    def getWork(self, num):
        return self.lista[num]

    def remove(self, num):
        del self.lista[num]

    def up(self, nwork):
        if nwork:
            work = self.lista[nwork]
            self.lista[nwork] = self.lista[nwork - 1]
            self.lista[nwork - 1] = work
            return True
        else:
            return False

    def down(self, nwork):
        if nwork < len(self.lista) - 1:
            work = self.lista[nwork]
            self.lista[nwork] = self.lista[nwork + 1]
            self.lista[nwork + 1] = work
            return True
        else:
            return False


class STS:
    def __init__(self, name):
        self.name = name
        if os.path.isfile(self.path()):
            self.restore()
        else:
            self.groups = Groups()
            self.works = Works()
        self.Xdefault = self.X = 0.2065
        self.Kdefault = self.K = 154.51
        self.formulaRead()
        self.orden = "", False

    def formulaWrite(self):
        dic = {"X": self.X, "K": self.K}
        Code.configuration.write_variables("STSFORMULA", dic)

    def formulaChange(self, x, k):
        self.X = x
        self.K = k
        self.formulaWrite()

    def formulaRead(self):
        dic = Code.configuration.read_variables("STSFORMULA")
        if dic:
            self.X = dic["X"]
            self.K = dic["K"]

    def path(self):
        folder = Code.configuration.carpetaSTS
        if not os.path.isdir(folder):
            os.mkdir(folder)
        return Util.opj(folder, "%s.sts" % self.name)

    def restore(self):
        dic = Util.restore_pickle(self.path())
        self.groups = Groups(dic["GROUPS"])
        self.works = Works()
        self.works.restore(dic["WORKS"])

    def saveCopyNew(self, newName):
        antName = self.name
        antWorks = self.works
        self.name = newName
        self.works = Works()
        self.save()
        self.name = antName
        self.works = antWorks

    def save(self):
        dic = {}
        dic["WORKS"] = self.works.save()
        dic["GROUPS"] = self.groups.save()
        Util.save_pickle(self.path(), dic)

    def addWork(self, work):
        self.works.new(work)

    def createWork(self, me):
        w = Work(len(self.groups))
        w.ref = me.key
        w.me = me
        return w

    def getWork(self, num):
        return self.works.getWork(num)

    def removeWork(self, num):
        self.works.remove(num)

    def donePositions(self, work, ngroup):
        if work.isGroupActive(ngroup):
            numPositions = work.numPositions()
            donePositionsGroup = work.donePositionsGroup(ngroup)
            return "%d/%d" % (donePositionsGroup, numPositions)
        else:
            return "-"

            # def is_done_group(self, ngroup):
            # if work.isGroupActive(ngroup):
            # numPositions = work.numPositions()
            # donePositionsGroup = work.donePositionsGroup(ngroup)
            # return donePositionsGroup >= numPositions
            # else:
            # return False

    def donePoints(self, work, ngroup):
        if work.isGroupActive(ngroup):
            group = self.groups.group(ngroup)
            tt, tp = work.numPointsGroup(group, ngroup)
            p = tp * 100.0 / tt if tt else 0.0
            return "%d/%d-%0.2f%%" % (tp, tt, p)
        else:
            return "-"

    def xdonePoints(self, work, ngroup):
        if work.isGroupActive(ngroup):
            group = self.groups.group(ngroup)
            tt, tp = work.numPointsGroup(group, ngroup)
            return tp
        else:
            return 0

    def allPoints(self, work):
        gt = 0
        gp = 0
        for ngroup in range(len(self.groups)):
            if work.isGroupActive(ngroup):
                group = self.groups.group(ngroup)
                tt, tp = work.numPointsGroup(group, ngroup)
                gt += tt
                gp += tp
        p = gp * 100.0 / gt if gt else 0.0
        return "%d/%d-%0.2f%%" % (gp, gt, p)

    def xelo(self, work):
        gp = 0
        for ngroup in range(len(self.groups)):
            if work.isGroupActive(ngroup):
                group = self.groups.group(ngroup)
                tt, tp = work.numPointsGroup(group, ngroup)
                if tt != 1000:
                    return 0
                gp += tp
            else:
                return 0
        return gp

    def elo(self, work):
        gp = self.xelo(work)
        return "%d" % int(gp * self.X + self.K) if gp else ""

    def ordenWorks(self, que):
        direc = not self.orden[1] if que == self.orden[0] else False
        if que in ("ELO", "RESULT"):
            for work in self.works.lista:
                work.gp = self.xelo(work)
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.gp, reverse=direc)
        elif que == "REF":
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.ref, reverse=direc)
        elif que == "TIME":
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.seconds, reverse=direc)
        elif que == "DEPTH":
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.depth, reverse=direc)
        elif que == "SAMPLE":
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.end - uno.ini, reverse=direc)
        else:
            test = int(que[1:])
            for work in self.works.lista:
                work.gp = self.xdonePoints(work, test)
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.gp, reverse=direc)

        self.orden = que, direc

    def siguientePosicion(self, work):
        for ngroup in range(len(self.groups)):
            nfen = work.siguientePosicion(ngroup)
            if nfen is not None:
                fen = self.groups.fen(ngroup, nfen)
                return ngroup, nfen, fen
        return None

    def setResult(self, work, ngroup, nfen, a1h8, ts):
        work.setResult(ngroup, nfen, a1h8, ts)

    def up(self, nwork):
        resp = self.works.up(nwork)
        if resp:
            self.save()
        return resp

    def down(self, nwork):
        resp = self.works.down(nwork)
        if resp:
            self.save()
        return resp

    def writeCSV(self, fich):
        f = open(fich, "wt")

        licabs = [_("Reference"), _("Time"), _("Depth"), _("Sample"), _("Result"), _("Elo")]
        for x in range(len(self.groups)):
            group = self.groups.group(x)
            licabs.append(group.name)
        f.write("%s\n" % ";".join(licabs))

        def xt(c):
            return c[: c.find("/")] if "/" in c else ""

        for nwork in range(len(self.works)):
            work = self.works.getWork(nwork)
            li = []
            li.append(work.ref)
            li.append(str(work.seconds) if work.seconds else "")
            li.append(str(work.depth) if work.depth else "")
            li.append("[%d-%d]" % (work.ini + 1, work.end + 1))
            li.append(xt(self.allPoints(work)))
            li.append(self.elo(work))
            for x in range(len(self.groups)):
                li.append(xt(self.donePoints(work, x)))
            f.write("%s\n" % ";".join(li))
        f.close()

        Code.startfile(fich)
