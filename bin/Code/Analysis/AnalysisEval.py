import Code
from Code import Util
from Code.Base.Constantes import (
    NO_RATING,
    BAD_MOVE,
    VERY_BAD_MOVE,
    QUESTIONABLE_MOVE,
)


class AnalysisEval:
    escala_1 = 100
    escala_2 = 300
    escala_3 = 800
    max_score = 3500
    max_mate = 15
    blunder = 2.0
    error = 1.0
    innacuracy = 0.3
    very_good_depth = 6
    good_depth = 3

    limit_max = 3500.0
    limit_min = 800.0
    lost_factor = 15.0
    lost_exp = 1.35

    questionable = 30
    very_bad_lostp = 200
    bad_lostp = 90
    bad_limit_min = 1200.0
    very_bad_factor = 8
    bad_factor = 2

    def __init__(self):
        path = Code.path_resource("IntFiles", "eval.ini")
        dic = Util.ini_base2dic(path)
        self.escala_1 = int(dic.get("EQUALITY", self.escala_1))
        self.escala_2 = int(dic.get("ADVANTAGE", self.escala_2))
        self.escala_3 = int(dic.get("WINNING", self.escala_3))
        self.max_score = int(dic.get("MAXSCORE", self.max_score))
        self.max_mate = int(dic.get("MAXMATE", self.max_mate))
        self.blunder = float(dic.get("BLUNDER", self.blunder))
        self.error = float(dic.get("ERROR", self.error))
        self.innacuracy = float(dic.get("INNACURACY", self.innacuracy))

        self.very_good_depth = int(dic.get("DEPTHVERYGOODMOVE", self.very_good_depth))
        self.good_depth = int(dic.get("DEPTHGOODMOVE", self.very_good_depth))

    def escala10(self, rm):
        if rm.mate:
            mt = min(abs(rm.mate), self.max_mate)
            v = (mt-1)/(self.max_mate-1)
            return (10.0 - v) if rm.mate > 0 else v

        pt = min(abs(rm.puntos), self.max_score)
        if pt <= self.escala_1:
            v = pt/self.escala_1
        elif pt <= self.escala_2:
            v = 1.0 + (pt-self.escala_1)/(self.escala_2-self.escala_1)
        elif pt <= self.escala_3:
            v = 2.0 + (pt-self.escala_2)/(self.escala_3-self.escala_2)
        else:
            v = 3.0 + (pt - self.escala_3) / (self.max_score - self.escala_3)

        return (5.0 + v) if rm.puntos > 0 else (5.0 - v)

    def evaluate(self, rm_j, rm_c):
        v_j = self.escala10(rm_j)
        v_c = self.escala10(rm_c)
        dif = v_j - v_c
        if dif >= self.blunder:
            return VERY_BAD_MOVE
        if dif >= self.error:
            return BAD_MOVE
        if dif >= self.innacuracy:
            return QUESTIONABLE_MOVE
        return NO_RATING

    def elo(self, rm_j, rm_c):
        v_j = self.escala10(rm_j)
        v_c = self.escala10(rm_c)
        return int((v_c*2700.0)/v_j + 800.0) if v_j > 0 else 3500.0

    def elo_bad_vbad(self, rm_j, rm_c):
        elo = self.elo(rm_j, rm_c)
        ev = self.evaluate(rm_j, rm_c)
        bad = ev == BAD_MOVE
        vbad = ev == VERY_BAD_MOVE
        quest = ev == QUESTIONABLE_MOVE
        return elo, quest, bad, vbad

    def limit(self, verybad, bad, nummoves):
        if verybad or bad:
            return int(
                max(
                    self.limit_max - self.very_bad_factor * 1000.0 * verybad / nummoves - self.bad_factor * 1000.0 * bad / nummoves,
                    self.bad_limit_min,
                )
            )
        else:
            return self.limit_max


