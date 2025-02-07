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
    def dic_results(self):
        return self._dicResults

    def points(self, a1h8):
        return self._maxpts, self._dicResults.get(a1h8, 0)

    @property
    def maxpts(self):
        return self._maxpts

    def best_a1_h8(self):
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
        key = None
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
            # num, key = k.split(".")
            # key = key.strip()
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
        self._dic_elem = {}

    def elem(self, num, valor=None):
        if valor is not None:
            self._dic_elem[num] = valor
        return self._dic_elem.get(num, None)

    def save(self):
        dic = {"DICELEM": self._dic_elem}
        return dic

    def restore(self, dic):
        self._dic_elem = dic["DICELEM"]

    def __len__(self):
        return len(self._dic_elem)

    def points(self, group):
        tt = 0
        tp = 0
        for num, a1h8 in self._dic_elem.items():
            t, p = group.points(num, a1h8)
            tt += t
            tp += p
        return tt, tp


class Results:
    def __init__(self, ngroups):
        self._li_result_groups = []
        for ngroup in range(ngroups):
            self._li_result_groups.append(ResultGroup())

    def save(self):
        li = []
        for result_group in self._li_result_groups:
            li.append(result_group.save())
        return li

    def restore(self, li):
        self._li_result_groups = []
        for savegroup in li:
            result_group = ResultGroup()
            result_group.restore(savegroup)
            self._li_result_groups.append(result_group)

    def done_positions_group(self, ngroup):
        result_group = self._li_result_groups[ngroup]
        return len(result_group)

    def num_points_group(self, group, ngroup):
        result_group = self._li_result_groups[ngroup]
        return result_group.points(group)

    def resoult_group(self, ngroup):
        return self._li_result_groups[ngroup]


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
        self.work_time = 0.0

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
        self.work_time = dic.get("WORKTIME", 0.0)

    def save(self):
        return {
            "REF": self.ref,
            "INFO": self.info,
            "SECONDS": self.seconds,
            "DEPTH": self.depth,
            "ENGINE": self.me.save(),
            "INI": self.ini,
            "END": self.end,
            "RESULTS": self.results.save(),
            "GROUPACTIVE": self.liGroupActive,
            "WORKTIME": self.work_time
        }

    def clone(self):
        w = Work(self.ngroups)
        ant_results = self.results
        self.results = Results(15)
        w.restore(self.save())
        self.results = ant_results
        return w

    def num_positions(self):
        return self.end - self.ini + 1

    def done_positions_group(self, ngroup):
        return self.results.done_positions_group(ngroup)

    def num_points_group(self, group, ngroup):
        return self.results.num_points_group(group, ngroup)

    def is_group_active(self, ngroup):
        return self.liGroupActive[ngroup]

    def siguiente_posicion(self, ngroup):
        if not self.liGroupActive[ngroup]:
            return None
        resoult_group = self.results.resoult_group(ngroup)
        for x in range(self.ini, self.end + 1):
            elem = resoult_group.elem(x)
            if elem is None:
                return x
        return None

    def config_engine(self):
        return self.me

    def path_to_exe(self):
        return self.me.path_exe

    def set_result(self, ngroup, nfen, a1h8, ts):
        resoult_group = self.results.resoult_group(ngroup)
        resoult_group.elem(nfen, a1h8)
        self.work_time += ts


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

    def get_work(self, num):
        return self.lista[num]

    def remove(self, num):
        if  0 <= num < len(self.lista):
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


class Formula:
    def __init__(self):
        self.is_default = True
        self.x_default_base = 0.2065
        self.k_default_base = 154.51
        self.x = self.x_default = self.x_default_base
        self.k = self.k_default = self.k_default_base
        self.read_default()

    def read_default(self):
        dic = Code.configuration.read_variables("STSFORMULA")
        if dic:
            self.x_default = dic["X"]
            self.k_default = dic["K"]

    def write_default(self):
        dic = {"X": self.x_default, "K": self.k_default}
        Code.configuration.write_variables("STSFORMULA", dic)

    def change_default(self, x, k):
        self.x = self.x_default = x
        self.k = self.k_default = k
        self.write_default()

    def check_isdefault(self):
        if self.is_default:
            self.x = self.x_default
            self.k = self.k_default
        else:
            self.is_default = self.k == self.k_default and self.x == self.x_default

    def restore_dic(self, dic):
        if dic:
            self.is_default = dic["IS_DEFAULT"]
            if self.is_default:
                self.x = self.x_default
                self.k = self.k_default
            else:
                self.x = dic["X"]
                self.k = dic["K"]
                self.check_isdefault()
        else:
            self.is_default = True
            self.x = self.x_default
            self.k = self.k_default

    def save_dic(self) -> dict:
        self.check_isdefault()
        return {
            "IS_DEFAULT": self.is_default,
            "X": self.x,
            "K": self.k
        }

    def change(self, x, k):
        self.x = x
        self.k = k
        self.is_default = False
        self.check_isdefault()

    def elo(self, pts: int):
        return "%d" % int(pts * self.x + self.k) if pts else ""


class STS:
    def __init__(self, name):
        self.name = name
        self.formula = Formula()

        if os.path.isfile(self.path()):
            self.restore()
        else:
            self.groups = Groups()
            self.works = Works()
        self.orden = "", False

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
        self.formula.restore_dic(dic.get("FORMULA"))

    def save_copy_new(self, new_name):
        ant_name = self.name
        ant_works = self.works
        self.name = new_name
        self.works = Works()
        self.save()
        self.name = ant_name
        self.works = ant_works

    def save(self):
        dic = {
            "WORKS": self.works.save(),
            "GROUPS": self.groups.save(),
            "FORMULA": self.formula.save_dic()
        }
        Util.save_pickle(self.path(), dic)

    def add_work(self, work):
        self.works.new(work)

    def create_work(self, me):
        w = Work(len(self.groups))
        w.ref = me.key
        w.me = me
        return w

    def get_work(self, num):
        return self.works.get_work(num)

    def remove_work(self, num):
        self.works.remove(num)

    @staticmethod
    def done_positions(work, ngroup):
        if work.is_group_active(ngroup):
            num_positions = work.num_positions()
            done_positions_group = work.done_positions_group(ngroup)
            return "%d/%d" % (done_positions_group, num_positions)
        else:
            return "-"

            # def is_done_group(self, ngroup):
            # if work.isGroupActive(ngroup):
            # numPositions = work.numPositions()
            # donePositionsGroup = work.donePositionsGroup(ngroup)
            # return donePositionsGroup >= numPositions
            # else:
            # return False

    def done_points(self, work, ngroup):
        if work.is_group_active(ngroup):
            group = self.groups.group(ngroup)
            tt, tp = work.num_points_group(group, ngroup)
            p = tp * 100.0 / tt if tt else 0.0
            return "%d/%d-%0.2f%%" % (tp, tt, p)
        else:
            return "-"

    def xdone_points(self, work, ngroup):
        if work.is_group_active(ngroup):
            group = self.groups.group(ngroup)
            tt, tp = work.num_points_group(group, ngroup)
            return tp
        else:
            return 0

    def all_points(self, work):
        gt = 0
        gp = 0
        for ngroup in range(len(self.groups)):
            if work.is_group_active(ngroup):
                group = self.groups.group(ngroup)
                tt, tp = work.num_points_group(group, ngroup)
                gt += tt
                gp += tp
        p = gp * 100.0 / gt if gt else 0.0
        return "%d/%d-%0.2f%%" % (gp, gt, p)

    def xelo(self, work):
        gp = 0
        for ngroup in range(len(self.groups)):
            if work.is_group_active(ngroup):
                group = self.groups.group(ngroup)
                tt, tp = work.num_points_group(group, ngroup)
                if tt != 1000:
                    return 0
                gp += tp
            else:
                return 0
        return gp

    def elo(self, work):
        gp = self.xelo(work)
        return self.formula.elo(gp)

    def orden_works(self, que):
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
                work.gp = self.xdone_points(work, test)
            self.works.lista = sorted(self.works.lista, key=lambda uno: uno.gp, reverse=direc)

        self.orden = que, direc

    def siguiente_posicion(self, work):
        for ngroup in range(len(self.groups)):
            nfen = work.siguiente_posicion(ngroup)
            if nfen is not None:
                fen = self.groups.fen(ngroup, nfen)
                return ngroup, nfen, fen
        return None

    @staticmethod
    def set_result(work, ngroup, nfen, a1h8, ts):
        work.set_result(ngroup, nfen, a1h8, ts)

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

    def write_csv(self, fich):
        f = open(fich, "wt")

        licabs = [_("Reference"), _("Time"), _("Depth"), _("Sample"), _("Result"), _("Elo")]
        for x in range(len(self.groups)):
            group = self.groups.group(x)
            licabs.append(group.name)
        f.write("%s\n" % ";".join(licabs))

        def xt(c):
            return c[: c.find("/")] if "/" in c else ""

        for nwork in range(len(self.works)):
            work = self.works.get_work(nwork)
            li = [
                work.ref,
                str(work.seconds) if work.seconds else "",
                str(work.depth) if work.depth else "",
                "[%d-%d]" % (work.ini + 1, work.end + 1),
                xt(self.all_points(work)), self.elo(work)
            ]
            for x in range(len(self.groups)):
                li.append(xt(self.done_points(work, x)))
            f.write("%s\n" % ";".join(li))
        f.close()

        Code.startfile(fich)
