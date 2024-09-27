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

    def lv_dif(self, cp_best, cp_other):
        return self.lv(cp_best) - self.lv(cp_other)

    def evaluate_dif(self, rm_best, rm_player):
        if rm_best.mate == 0 and rm_player.mate == 0:
            return self.lv_dif(rm_best.puntos, rm_player.puntos)

        elif rm_player.mate == 0:
            if rm_best.mate > self.conf.x_eval_mate_human:
                xadd = self.conf.x_eval_inaccuracy
            else:
                dif_mate = self.conf.x_eval_mate_human - rm_best.mate
                if dif_mate >= self.conf.x_eval_difmate_blunder:
                    xadd = self.conf.x_eval_blunder
                elif dif_mate >= self.conf.x_eval_difmate_mistake:
                    xadd = self.conf.x_eval_mistake
                elif dif_mate >= self.conf.x_eval_difmate_inaccuracy:
                    xadd = self.conf.x_eval_inaccuracy
                else:
                    xadd = 0

            return self.lv_dif(self.conf.x_eval_limit_score, rm_player.puntos) + xadd

        elif rm_best.mate == 0 and rm_player.mate < 0:
            return max(self.lv_dif(rm_best.centipawns_abs(), rm_player.centipawns_abs()), self.conf.x_eval_mistake)

        else:
            dif_mate = rm_best.mate - rm_player.mate
            if dif_mate >= self.conf.x_eval_difmate_blunder:
                return self.conf.x_eval_blunder
            if dif_mate >= self.conf.x_eval_difmate_mistake:
                return self.conf.x_eval_mistake
            if dif_mate >= self.conf.x_eval_difmate_inaccuracy:
                return self.conf.x_eval_mistake
            return 0

    def evaluate(self, rm_best, rm_player):
        dif = self.evaluate_dif(rm_best, rm_player)

        if dif >= self.conf.x_eval_blunder:
            return BLUNDER
        if dif >= self.conf.x_eval_mistake:
            return MISTAKE
        if dif >= self.conf.x_eval_inaccuracy:
            return INACCURACY
        return NO_RATING

    def elo(self, rm_best, rm_player):
        dif = self.evaluate_dif(rm_best, rm_player)
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

    def elo_bad_vbad(self, rm_best, rm_player):
        elo = self.elo(rm_best, rm_player)
        ev = self.evaluate(rm_best, rm_player)
        bad = ev == MISTAKE
        vbad = ev == BLUNDER
        quest = ev == INACCURACY
        return elo, quest, bad, vbad

    @staticmethod
    def calc_accuracy_game(game):
        n_jg = n_jg_w = n_jg_b = 0
        porc_t = porc_w = porc_b = 0

        for num, move in enumerate(game.li_moves):
            if move.analysis:
                mrm, pos = move.analysis
                is_white = move.is_white()
                pts = mrm.li_rm[pos].centipawns_abs()
                pts0 = mrm.li_rm[0].centipawns_abs()
                lostp_abs = pts0 - pts

                porc = 100 - lostp_abs if lostp_abs < 100 else 0
                porc_t += porc

                n_jg += 1
                if is_white:
                    n_jg_w += 1
                    porc_w += porc
                else:
                    n_jg_b += 1
                    porc_b += porc

        porc_t = porc_t * 1.0 / n_jg if n_jg else None
        porc_w = porc_w * 1.0 / n_jg_w if n_jg_w else None
        porc_b = porc_b * 1.0 / n_jg_b if n_jg_b else None

        return porc_w, porc_b, porc_t
