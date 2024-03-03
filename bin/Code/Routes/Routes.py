import datetime
import random

import Code
from Code import Util
from Code.Base import Game
from Code.Translations import TrListas


class Reg:
    pass


PLAYING, BETWEEN, ENDING, ENDED = range(4)
KM_TACTIC = 5
C_MILES = 1.609344


def km_mi(km, is_miles):
    return "%0.0f %s" % (float(km) / C_MILES, _("mi")) if is_miles else "%d %s" % (km, _("km"))


class Station:
    def __init__(self, km, name, xpos):
        self._km = km
        self._name = name
        self._xpos = xpos

    def is_main(self):
        return self._xpos is not None

    @property
    def km(self):
        return self._km

    @property
    def xpos(self):
        return self._xpos

    @property
    def name(self):
        return _F(self._name)


class Line:
    def __init__(self, st_from, stage):
        self._st_from = st_from
        self.li_st = [st_from]
        self._stage = stage

    @property
    def st_from(self):
        return self._st_from

    @property
    def st_to(self):
        return self.li_st[-1]

    @property
    def stage(self):
        return self._stage

    @property
    def num_stations(self):
        return len(self.li_st) - 1

    @property
    def km(self):
        return self.li_st[-1].km - self._st_from.km

    def get_track(self, km, state):
        nst = len(self.li_st) - 1
        for n in range(nst):
            st_from = self.li_st[n]
            st_to = self.li_st[n + 1]
            if state == BETWEEN:
                if st_from.km <= km < st_to.km:
                    return st_from, st_to, n + 1
            else:
                if st_from.km <= km <= st_to.km:
                    return st_from, st_to, n + 1

    def add_st(self, st):
        self.li_st.append(st)

    def km_xpos(self, km):
        st_to = self.li_st[-1]
        xdif = st_to.xpos - self.st_from.xpos
        kdif = st_to.km - self.st_from.km
        xancho = xdif * (km - self.st_from.km) / kdif
        return self.st_from.xpos + xancho

    def km_done(self, km_tot):
        return km_tot - self._st_from.km


class Transsiberian:
    def __init__(self, configuration):
        self.configuration = configuration

        self.base = base = Code.path_resource("IntFiles", "Routes", "Transsiberian")

        plant = base + "/transsiberian.%s"
        self.svg = self.read_svg(plant)
        self.lines = self.read_dat(plant)

        self.key_km = "276.42023"
        self.key_train = "372.72258"

        self.initialize()
        self.read_current()

        self.read_level()

    def initialize(self, nlevel=1):
        self._level = nlevel
        self._km = 0
        self._state = BETWEEN
        self._pos_tactics = random.randint(0, 300)
        self._dpos_endings = {}
        self._time = {PLAYING: 0.0, BETWEEN: 0.0, ENDING: 0.0}
        self._date_begin = datetime.datetime.now()
        self._date_end = datetime.datetime.now()
        self._km_tactic = KM_TACTIC
        self._is_miles = False
        self._go_fast = False
        self._key = Util.huella()

    def read_level(self):
        folder = "%s/level%d" % (self.base, self._level)

        random.seed(self._key)

        with open(Util.opj(folder, "tactics.fns")) as f:
            self.li_tactics = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    reg = Reg()
                    reg.fen, reg.label, reg.pgn = linea.split("|")
                    self.li_tactics.append(reg)
            random.shuffle(self.li_tactics)
            self.liPosTactics = [0, 1, 2]
            for n in range(len(self.li_tactics) - 3):
                self.liPosTactics.append(n + 3)
                self.liPosTactics.append(n)
            self.liPosTactics.extend([n + 1, n + 2, n + 3])

        self.dicEndings = {}
        for tp in "01M":
            with open(Code.path_resource("IntFiles", "endings%s.ini" % tp)) as f:
                for linea in f:
                    linea = linea.strip()
                    if linea:
                        if linea.startswith("["):
                            lastkey = "%s,%s" % (linea.strip("[] "), tp)
                            self.dicEndings[lastkey] = []
                        else:
                            self.dicEndings[lastkey].append(linea)
        for k in self.dicEndings:
            random.shuffle(self.dicEndings[k])

        dic = Util.ini2dic(Util.opj(folder, "config.ini"))
        for cline, txt in dic["PLAYING"].items():
            line = self.lines[int(cline) - 1]
            reg = Reg()
            cengine, color, reg.label, reg.pv = txt.split("|")
            reg.is_white = color == "W" if color in "WB" else None
            line.opening = reg
            line.engine = int(cengine)

        for cline, txt in dic["ENDING"].items():
            line = self.lines[int(cline) - 1]
            line.ending = txt

    def read_svg(self, base):
        with open(base % "svg") as f:
            x = f.read()
            dic = TrListas.transsiberian()
            for k, v in dic.items():
                x = x.replace(">%s<" % k, ">%s<" % v)
            return x

    def read_dat(self, base):
        lines = []
        line = None
        stage = 1
        with open(base % "dat") as f:
            for linea in f:
                li = linea.strip().split(",")
                if len(li) == 3:
                    km, name, xpos = li
                    km = int(km)
                    xpos = float(xpos)
                    st = Station(km, name, xpos)
                    if line:
                        line.add_st(st)
                    line = Line(st, stage)
                    stage += 1
                    lines.append(line)
                elif len(li) == 2:
                    km, name = li
                    km = int(km)
                    xpos = None
                    st = Station(km, name, xpos)
                    line.add_st(st)
                else:
                    continue
        return lines[:-1]

    def read_dic(self, dic):
        if dic:
            self._level = dic["LEVEL"]
            self._km = dic["KM"]
            self._state = dic["STATE"]
            self._pos_tactics = dic["POS_TACTICS"]
            self._km_tactic = dic["KM_TACTIC"]
            self._date_begin = dic["DATE_BEGIN"]
            self._date_end = dic["DATE_END"]
            self._time = dic["TIME"]
            self._is_miles = dic["IS_MILES"]
            self._go_fast = dic.get("GO_FAST", False)
            self._key = dic.get("KEY", self._key)
            self._dpos_endings = dic.get("DPOS_ENDINGS", self._dpos_endings)

    def read_with_level(self, nlevel):
        dic = self.configuration.read_variables(f"TRANSSIBERIAN{nlevel}")
        if dic:
            self.read_dic(dic)
        else:
            self.initialize(nlevel)

    def read_current(self):
        # self._km = 59
        # self._state = PLAYING
        # self._level = 5
        # self._is_miles = True
        # self.write_current()
        dic = self.configuration.read_variables("TRANSSIBERIAN")
        self.read_dic(dic)

    def write_dic(self):
        dic = {
            "KM": self._km,
            "LEVEL": self._level,
            "STATE": self._state,
            "POS_TACTICS": self._pos_tactics,
            "DPOS_ENDINGS": self._dpos_endings,
            "KM_TACTIC": self._km_tactic,
            "DATE_BEGIN": self._date_begin,
            "DATE_END": self._date_end,
            "TIME": self._time,
            "IS_MILES": self._is_miles,
            "GO_FAST": self._go_fast,
            "KEY": self._key,
        }
        return dic

    def write_current(self):
        self.configuration.write_variables("TRANSSIBERIAN", self.write_dic())

    def write_with_level(self):
        self.configuration.write_variables("TRANSSIBERIAN%s" % self._level, self.write_dic())

    def get_line(self):
        km = self._km
        for line in self.lines:
            if self._state == BETWEEN:
                if line.st_from.km <= km < line.st_to.km:
                    return line
            else:
                if line.st_from.km <= km <= line.st_to.km:
                    return line

    def get_txt(self):
        line = self.get_line()
        xpos = line.km_xpos(self._km)
        xtrain = "%0.5f" % (xpos - 6.2,)

        xmoscow = self.lines[0].st_from.xpos
        xkm = "%0.5f" % (xpos - xmoscow,)

        txt = self.svg.replace(self.key_km, xkm).replace(self.key_train, xtrain)
        return txt

    def get_track(self):
        line = self.get_line()
        st_from, st_to, num = line.get_track(self._km, self._state)
        return st_from, st_to

    @property
    def num_track(self):
        line = self.get_line()
        st_from, st_to, num = line.get_track(self._km, self._state)
        return num

    @property
    def km(self):
        return self._km

    @property
    def is_miles(self):
        return self._is_miles

    @property
    def total_km(self):
        return self.lines[-1].st_to.km

    @property
    def state(self):
        return self._state

    @property
    def date_begin(self):
        return self._date_begin.strftime("%d/%m/%Y - %H:%M")

    @property
    def date_end(self):
        return self._date_end.strftime("%d/%m/%Y - %H:%M")

    @property
    def go_fast(self):
        return self._go_fast

    def change_go_fast(self):
        self._go_fast = not self._go_fast
        self.write_current()

    @property
    def level(self):
        return self._level

    def set_level(self, nlevel):
        if nlevel != self._level:
            self.read_with_level(nlevel)
            # self.initialize()
            # self._level = nlevel
            self.write_current()

    def time(self, state=None):
        if state is None:
            t = 0.0
            for k, v in self._time.items():
                t += v
        else:
            t = self._time[state]
        s = int(t)
        m = s / 60
        s %= 60
        h = m / 60
        m %= 60
        return "%02d:%02d:%02d" % (h, m, s)

    @property
    def num_stages(self):
        return len(self.lines)

    def tool_tip_line(self):
        currline = self.get_line()
        stage = currline.stage
        li = []
        for line in self.lines:
            if line.stage < stage:
                x1 = "<b>"
                x2 = "</b>"
            else:
                x1 = x2 = ""
            li.append(
                "%s%2d. %s - %s (%s, %d %s) %s"
                % (
                    x1,
                    line.stage,
                    line.st_from.name,
                    line.st_to.name,
                    km_mi(line.km, self._is_miles),
                    line.num_stations,
                    _("stations"),
                    x2,
                )
            )
        return "<br>".join(li)

    def tool_tip_track(self):
        line = self.get_line()
        st_from, st_to, num_tr = line.get_track(self._km, self._state)
        li = []
        st_from = line.st_from
        for n, st in enumerate(line.li_st):
            if not n:
                continue
            if n < num_tr:
                x1 = "<b>"
                x2 = "</b>"
            else:
                x1 = x2 = ""
            li.append(
                "%s%2d. %s - %s (%s) %s" % (x1, n, st_from.name, st.name, km_mi(st.km - st_from.km, self._is_miles), x2)
            )
            st_from = st
        return "<br>".join(li)

    def mens_state(self):
        st_from, st_to = self.get_track()
        if self._state == PLAYING:
            if self._km == self.total_km:
                return _("Ending the game")
            else:
                return _("Leaving the station of %s") % st_to.name
        elif self._state == ENDING:
            return _("Arriving at the station of %s") % st_to.name
        else:
            return _("Running between %s and %s") % (st_from.name, st_to.name)

    def get_task(self):
        line = self.get_line()
        if self._state == PLAYING:
            st_from, st_to = self.get_track()
            task = line.opening, st_to == line.st_to
        elif self._state == ENDING:
            task = self.dicEndings[line.ending]
        else:
            task = self.li_tactics
        return self._state, task

    def next_task(self):
        state, task = self.get_task()
        if state == PLAYING:
            opening, win = task
            pgn = Game.pv_pgn(None, opening.pv)

            litxt = [_("To play a complete game.")]
            if opening.label:
                litxt.append(pgn)
                litxt.append(_("With the opening: %s.") % _FO(opening.label))
            if win:
                litxt.append(_("You must win to pass this step."))
            else:
                litxt.append(_("You don't need to win to pass this step."))
            return "<br>".join(litxt), Code.dic_colors["ROUTES_NEXTTASK_BACKGROUND_PLAYING"]
        elif state == ENDING:
            return _("You must solve an endgame puzzle"), Code.dic_colors["ROUTES_NEXTTASK_BACKGROUND_ENDINGS"]
        else:
            return _("You must solve tactics puzzles to advance."), Code.dic_colors[
                "ROUTES_NEXTTASK_BACKGROUND_TACTICS"]

    def get_tactic(self):
        if self._pos_tactics >= len(self.liPosTactics):
            self._pos_tactics = 0
            self._km_tactic = KM_TACTIC
        return self.li_tactics[self.liPosTactics[self._pos_tactics]]

    def error_tactic(self, nMoves):
        q = int(round(KM_TACTIC * 1.0 / nMoves))
        if q < 1:
            q = 1
        self._km_tactic -= q
        if self._km_tactic < 1:
            self._km_tactic = 1
        self.write_current()

    def end_tactic(self):
        st_from, st_to = self.get_track()
        km = self._km + self._km_tactic
        if km >= st_to.km:
            km = st_to.km
            self._state = ENDING
        kmtravel = km - self._km
        self._km = km
        self._km_tactic = KM_TACTIC
        self._pos_tactics += 1
        self.write_current()
        return kmtravel

    def mens_tactic(self, is_end):
        st_from, st_to = self.get_track()
        mens = "%s - %s" % (st_from.name, st_to.name)
        kmdif = st_to.km - self._km

        mens += "<br>" + _("To arrive to %s: %s") % (st_to.name, km_mi(kmdif, self._is_miles))
        if not is_end:
            kmtac = min(self._km_tactic, kmdif)
            mens += "<br>" + _("Advance: %s") % km_mi(kmtac, self._is_miles)
        return mens

    def get_ending(self):
        line = self.get_line()
        liEndings = self.dicEndings[line.ending]
        if not (line.ending in self._dpos_endings):
            self._dpos_endings[line.ending] = 0
            self.write_current()
        pos = self._dpos_endings[line.ending]
        return liEndings[pos % len(liEndings)]

    def end_ending(self):
        self._state = PLAYING
        line = self.get_line()
        self._dpos_endings[line.ending] += 1
        self.write_current()

    def km_pending(self):
        st_from, st_to = self.get_track()
        return st_to.km - self._km

    def must_win(self):
        state, task = self.get_task()
        opening, win = task
        return win

    def end_playing(self):
        if self._km == self.total_km:
            self._state = ENDED
            self._date_end = datetime.datetime.now()
        else:
            self._state = BETWEEN
        self.write_current()
        return self._state == ENDED

    def add_time(self, tm, state):
        self._time[state] += tm
        self.write_current()

    def is_ended(self):
        return self._state == ENDED

    def reset(self):
        is_miles = self._is_miles
        self.initialize(self._level)
        self._is_miles = is_miles
        self.write_current()

    def change_measure(self):
        self._is_miles = not self._is_miles
        self.write_current()
