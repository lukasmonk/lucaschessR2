import Code
from Code.Base.Constantes import (
    NO_RATING,
    MISTAKE,
    BLUNDER,
    INACCURACY,
)


class EvalPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def value(self):
        return self.x, self.y


class EvalLine:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.factor = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)

    def value(self, x):
        return self.p1.y + (x - self.p1.x) * self.factor

    def contiene(self, x):
        return self.p1.x <= x <= self.p2.x


class EvalLines:
    li_lines: list
    p0: EvalPoint
    last_p: EvalPoint

    def __init__(self):
        self.li_lines = []
        self.p0 = EvalPoint(0, 0)
        self.last_p = self.p0

    def add_point(self, p: EvalPoint):
        line = EvalLine(self.last_p, p)
        self.li_lines.append(line)
        self.last_p = p

    def add_xy(self, x, y):
        self.add_point(EvalPoint(x, y))

    def value(self, x):
        for line in self.li_lines:
            if line.contiene(x):
                return line.value(x)
        return 0

    def max_y(self):
        return self.last_p.y

    def max_x(self):
        return self.last_p.x

    def save_list(self):
        return [(line.p2.x, line.p2.y) for line in self.li_lines]

    def restore_list(self, li):
        for x, y in li:
            self.add_xy(x, y)


class AnalysisEval:
    eval_lines: EvalLines
    eval_lines_max_y: float
    eval_lines_max_x: float
    blunder: float
    error: float
    inaccuracy: float
    very_good_depth: int
    good_depth: int
    max_mate: int
    max_elo: float
    min_elo: float
    very_bad_factor: float
    bad_factor: float

    def __init__(self):
        conf = Code.configuration

        self.eval_lines = EvalLines()
        self.eval_lines.restore_list(conf.eval_lines)
        self.eval_lines_max_y = self.eval_lines.max_y()
        self.eval_lines_max_x = self.eval_lines.max_x()

        self.blunder = conf.eval_blunder
        self.error = conf.eval_error
        self.inaccuracy = conf.eval_inaccuracy
        self.very_good_depth = conf.eval_very_good_depth
        self.good_depth = conf.eval_good_depth
        self.max_mate = conf.eval_max_mate
        self.max_elo = conf.eval_max_elo
        self.min_elo = conf.eval_min_elo
        self.very_bad_factor = conf.eval_very_bad_factor
        self.bad_factor = conf.eval_bad_factor

    def escala10(self, rm):
        if rm.mate:
            mt = min(abs(rm.mate), self.max_mate)
            v = (mt - 1) / (self.max_mate - 1)
            rep = 5.0 - self.eval_lines_max_y
            v = rep * v
            return (10.0 - v) if rm.mate > 0 else v

        pt = min(abs(rm.puntos), self.eval_lines_max_x)
        v = self.eval_lines.value(pt)
        return (5.0 + v) if rm.puntos > 0 else (5.0 - v)

    def evaluate(self, rm_j, rm_c):
        v_j = self.escala10(rm_j)
        v_c = self.escala10(rm_c)
        dif = v_j - v_c
        if dif >= self.blunder:
            return BLUNDER
        if dif >= self.error:
            return MISTAKE
        if dif >= self.inaccuracy:
            return INACCURACY
        return NO_RATING

    def elo(self, rm_j, rm_c):
        v_j = self.escala10(rm_j)
        v_c = self.escala10(rm_c)
        df = v_j - v_c
        mx = self.max_elo
        mn = self.min_elo
        bl2 = self.blunder * 1.5
        if df > bl2:
            return mn
        elif df == 0:
            return mx
        elif df > self.blunder:
            mx *= 0.2
        elif df > self.error:
            mx *= 0.5
        elif df > self.inaccuracy:
            mx *= 0.8
        rg = max(mx - mn, 0)
        return int((bl2 - df) * rg / bl2 + mn)

    def elo_bad_vbad(self, rm_j, rm_c):
        elo = self.elo(rm_j, rm_c)
        ev = self.evaluate(rm_j, rm_c)
        bad = ev == MISTAKE
        vbad = ev == BLUNDER
        quest = ev == INACCURACY
        return elo, quest, bad, vbad
