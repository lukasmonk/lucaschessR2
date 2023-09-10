import math

import Code
from Code.Base.Constantes import NO_RATING, MISTAKE, BLUNDER, INACCURACY
from Code.Config import Configuration


class AnalysisEval:
    def __init__(self):
        self.conf: Configuration.Configuration = Code.configuration

    def _lv(self, cp: int, factor: float) -> float:
        # Based in https://lichess.org/blog/WFvLpiQAACMA8e9D/learn-from-your-mistakes
        is_neg = cp < 0.0
        if is_neg:
            cp = -cp

        def base(xcp):
            return (200.0 / (1.0 + math.exp(-factor * xcp / 10000.0))) - 100.0

        xr = min(max(base(cp) * 50.0 / base(self.conf.x_eval_limit_score), 0.0), 50.0)

        return 50.0 + (-xr if is_neg else xr)

    def lv(self, cp: int) -> float:
        return self._lv(cp, self.conf.x_eval_curve_degree)

    def lv_dif(self, cp, cp_best):
        return self.lv(cp_best) - self.lv(cp)

    def evaluate(self, rm_j, rm_c):
        dif = self.evaluate_dif(rm_j, rm_c)

        if dif >= self.conf.x_eval_blunder:
            return BLUNDER
        if dif >= self.conf.x_eval_mistake:
            return MISTAKE
        if dif >= self.conf.x_eval_inaccuracy:
            return INACCURACY
        return NO_RATING

    def evaluate_dif(self, rm_j, rm_c):
        if rm_j.mate == 0 and rm_c.mate == 0:
            return self.lv_dif(rm_c.puntos, rm_j.puntos)

        elif rm_c.mate == 0:
            if rm_j.mate > self.conf.x_eval_mate_human:
                xadd = self.conf.x_eval_inaccuracy
            else:
                dif_mate = self.conf.x_eval_mate_human - rm_j.mate
                if dif_mate >= self.conf.x_eval_difmate_blunder:
                    xadd = self.conf.x_eval_blunder
                elif dif_mate >= self.conf.x_eval_difmate_mistake:
                    xadd = self.conf.x_eval_mistake
                elif dif_mate >= self.conf.x_eval_difmate_inaccuracy:
                    xadd = self.conf.x_eval_inaccuracy
                else:
                    xadd = 0

            return self.lv_dif(rm_c.puntos, self.conf.x_eval_limit_score) + xadd

        elif rm_j.mate == 0 and rm_c.mate < 0:
            return max(self.lv_dif(rm_c.centipawns_abs(), rm_j.centipawns_abs()), self.conf.x_eval_mistake)

        else:
            dif_mate = rm_j.mate - rm_c.mate
            if dif_mate >= self.conf.x_eval_difmate_blunder:
                return self.conf.x_eval_blunder
            if dif_mate >= self.conf.x_eval_difmate_mistake:
                return self.conf.x_eval_mistake
            if dif_mate >= self.conf.x_eval_difmate_inaccuracy:
                return self.conf.x_eval_mistake
            return 0

    def elo(self, rm_j, rm_c):
        dif = self.evaluate_dif(rm_j, rm_c)
        mx = self.conf.x_eval_max_elo
        mn = self.conf.x_eval_min_elo
        bl2 = self.conf.x_eval_blunder * 1.5
        if dif > bl2:
            return mn
        elif dif == 0:
            return mx
        elif dif >= self.conf.x_eval_blunder:
            mx *= 0.1
        elif dif >= self.conf.x_eval_mistake:
            mx *= 0.3
        elif dif >= self.conf.x_eval_inaccuracy:
            mx *= 0.6
        rg = max(mx - mn, 0)
        return int((bl2 - dif / 10) * rg / bl2 + mn)

    def elo_bad_vbad(self, rm_j, rm_c):
        elo = self.elo(rm_j, rm_c)
        ev = self.evaluate(rm_j, rm_c)
        bad = ev == MISTAKE
        vbad = ev == BLUNDER
        quest = ev == INACCURACY
        return elo, quest, bad, vbad
