import os
import random
import sys
import time

import Code
from Code import Util
from Code.Base import Game
from Code.Base.Constantes import RESULT_WIN_WHITE, RESULT_WIN_BLACK, RESULT_DRAW, ENGINE, HUMAN, WHITE, BLACK
from Code.Engines import Engines
from Code.SQL import UtilSQL


def create_journeys(num_opponents: int) -> list:
    li_opponents = list(range(num_opponents))
    if num_opponents % 2:
        li_opponents.append(None)
        num_opponents += 1

    ################################################################################################################
    # https://stackoverflow.com/questions/11245746/swiss-fixture-generator-in-python/48039377#48039377
    # https://stackoverflow.com/users/9157436/carlos-fern%c3%a1ndez
    matches = []
    journeys = []
    for xopp in range(1, num_opponents):
        for i in range(num_opponents // 2):
            x = li_opponents[i]
            y = li_opponents[num_opponents - 1 - i]
            if not (x is None or y is None):
                matches.append((x, y))
        li_opponents.insert(1, li_opponents.pop())
        journeys.insert(len(journeys) // 2, matches)
        matches = []
    ################################################################################################################

    # A continuación se ordenan las jornadas para que se juegue una vez con blancas y la siguiente con negras

    for opponent in li_opponents:
        last = None
        for journey in journeys:
            for xpos, (w, b) in enumerate(journey):
                if w == opponent:
                    if last == WHITE:
                        journey[xpos] = (b, w)
                        last = BLACK
                    else:
                        last = WHITE
                elif b == opponent:
                    if last == BLACK:
                        journey[xpos] = (b, w)
                        last = WHITE
                    else:
                        last = BLACK

    min_uniones = sys.maxsize
    li_minimo = None
    t = time.time()
    k_time = max(len(li_opponents) / 10, 1.0)
    while (time.time() - t) < k_time:
        dr = {xr: "" for xr in li_opponents}
        for journey in journeys:
            for xpos, (w, b) in enumerate(journey):
                if dr[w].endswith("W"):
                    journey[xpos] = (b, w)
                elif dr[b].endswith("B"):
                    journey[xpos] = (b, w)
                w, b = journey[xpos]
                dr[w] += "W"
                dr[b] += "B"

        uniones = 0
        for x in range(len(li_opponents)):
            if x in dr:
                if "WWWWW" in dr[x] or "BBBBB" in dr[x]:
                    uniones += 100000000000000
                elif "WWWW" in dr[x] or "BBBB" in dr[x]:
                    uniones += 10000000
                elif dr[x].startswith(("BB", "WW")):
                    uniones += 1000
                elif dr[x].endswith(("BB", "WW")):
                    uniones += 1000
                elif "WWW" in dr[x] or "BBB" in dr[x]:
                    uniones += 1000
                else:
                    for xpos, xc in enumerate(dr[x]):
                        if xpos:
                            if xc == dr[x][xpos - 1]:
                                uniones += 1
        if uniones < min_uniones:
            li_minimo = [[(b, w) for w, b in journey] for journey in journeys]
            min_uniones = uniones
            t = time.time()
        random.shuffle(journeys)

    journeys_with_returns = li_minimo[:]
    for journey in li_minimo:
        new_journey = [(b, w) for w, b in journey]
        random.shuffle(new_journey)
        journeys_with_returns.append(new_journey)

    return journeys_with_returns


class Human:
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo

    def save(self):
        return {"NAME": self.name, "ELO": self.elo}

    def restore(self, dic):
        self.name = dic.get("NAME", self.name)
        self.elo = dic.get("ELO", self.elo)


class Opponent:
    def __init__(self):
        self.type = None
        self.opponent = None
        self.xid = Util.huella()
        self.white = 0
        self.black = 0
        self.last_played = None
        self.win = 0
        self.lost = 0
        self.draw = 0
        self.byes = 0
        self.li_rival_win = []
        self.li_rival_draw = []
        self.li_rival_lost = []

    def set_engine(self, engine):
        self.type = ENGINE
        self.opponent = engine

    def set_human(self, name, elo):
        self.type = HUMAN
        self.opponent = Human(name, elo)

    def name(self):
        return self.opponent.name

    def elo(self):
        return self.opponent.elo

    def set_elo(self, elo):
        self.opponent.elo = elo

    def set_name(self, name):
        self.opponent.name = name

    def is_human(self):
        return self.type == HUMAN

    def save(self):
        dic = {
            "TYPE": self.type,
            "XID": self.xid,
            "OPPONENT": self.opponent.save(),
            "WHITE": self.white,
            "BLACK": self.black,
            "LAST_PLAYED": self.last_played,
            "WIN": self.win,
            "LOST": self.lost,
            "DRAW": self.draw,
            "BYES": self.byes,
            "LI_RIVAL_WIN": self.li_rival_win,
            "LI_RIVAL_DRAW": self.li_rival_draw,
            "LI_RIVAL_LOST": self.li_rival_lost,
        }
        return dic

    def restore(self, dic):
        self.type = dic.get("TYPE", self.type)
        self.xid = dic.get("XID", self.xid)
        t = dic.get("OPPONENT")
        if t:
            if self.type == HUMAN:
                self.opponent = Human(None, None)
                self.opponent.restore(t)
            else:
                self.opponent = Engines.Engine()
                self.opponent.restore(t)
        self.white = dic.get("WHITE", 0)
        self.black = dic.get("BLACK", 0)
        self.last_played = dic.get("LAST_PLAYED")
        self.win = dic.get("WIN", 0)
        self.lost = dic.get("LOST", 0)
        self.draw = dic.get("DRAW", 0)
        self.byes = dic.get("BYES", 0)
        self.li_rival_win = dic.get("LI_RIVAL_WIN", [])
        self.li_rival_draw = dic.get("LI_RIVAL_DRAW", [])
        self.li_rival_lost = dic.get("LI_RIVAL_LOST", [])

    def score(self) -> int:
        return self.win * 10 + self.draw * 5

    def desempate(self, swiss):
        fn = swiss.opponent_by_xid
        score_rival_win = sum(fn(xrival).score() for xrival in self.li_rival_win)
        score_rival_draw = sum(fn(xrival).score() for xrival in self.li_rival_draw)
        score_sum_rival = score_rival_win * 10 + score_rival_draw * 5
        return f"{self.score():04d}{score_sum_rival:05d}{self.win:03d}{self.draw:03d}{self.elo:04d}"

    def next_side(self):
        if self.white < self.black:
            return WHITE
        elif self.white > self.black:
            return BLACK
        elif self.last_played is not None:
            return WHITE if self.last_played == BLACK else BLACK
        else:
            return None


class Match:
    def __init__(self, xid_white: str, xid_black: str):
        self.xid = Util.huella()
        self.xid_white: str = xid_white
        self.xid_black: str = xid_black
        self.result = None

    def save(self):
        return {"XID": self.xid, "XID_WHITE": self.xid_white, "XID_BLACK": self.xid_black, "RESULT": self.result}

    def restore(self, dic):
        self.xid = dic.get("XID", self.xid)
        self.xid_white = dic.get("XID_WHITE")
        self.xid_black = dic.get("XID_BLACK")
        self.result = dic.get("RESULT")

    def is_engine_vs_engine(self, swiss):
        opw, opb = self.get_opponents(swiss)
        return not (opw.is_human() or opb.is_human())

    def is_human_vs_engine(self, swiss):
        opw, opb = self.get_opponents(swiss)
        return (opw.is_human() and not opb.is_human()) or (not opw.is_human() and opb.is_human())

    def is_human_vs_human(self, swiss):
        opw, opb = self.get_opponents(swiss)
        return opw.is_human() and opb.is_human()

    def side_human(self, swiss):
        opw, opb = self.get_opponents(swiss)
        if opw.is_human():
            return WHITE
        if opb.is_human():
            return BLACK
        return None

    def get_engine(self, swiss, side):
        return swiss.opponent_by_xid(self.xid_white if side == WHITE else self.xid_black)

    def get_opponents(self, swiss):
        return swiss.opponent_by_xid(self.xid_white), swiss.opponent_by_xid(self.xid_black)


class Round:
    def __init__(self, li_players):
        self.li_matches = []
        self.li_players = li_players
        self.with_byes = len(li_players) % 2 == 1

    def save(self):
        return [xmatch.save() for xmatch in self.li_matches]

    def restore(self, li_saved):
        self.li_matches = []
        for dic_saved in li_saved:
            xmatch = Match("", "")
            xmatch.restore(dic_saved)
            self.li_matches.append(xmatch)

    def add_results(self, dic, score_win, score_draw, score_lost):
        for xmatch in self.li_matches:
            if xmatch.result is None:
                continue
            result = xmatch.result
            xid_white, xid_black = xmatch.xid_white, xmatch.xid_black
            pts_white = pts_black = score_lost
            dic[xid_white]["PL"] += 1
            dic[xid_black]["PL"] += 1
            resn_w, resn_b = 0, 0
            if result == RESULT_DRAW:
                dic[xid_white]["DRAW"] += 1
                dic[xid_black]["DRAW"] += 1
                pts_white = pts_black = score_draw
            elif result == RESULT_WIN_WHITE:
                dic[xid_white]["WIN"] += 1
                dic[xid_black]["LOST"] += 1
                pts_white = score_win
                resn_w, resn_b = +1, -1
            elif result == RESULT_WIN_BLACK:
                dic[xid_white]["LOST"] += 1
                dic[xid_black]["WIN"] += 1
                pts_black = score_win
                resn_w, resn_b = -1, +1
            dic[xid_white]["PTS"] += pts_white
            dic[xid_black]["PTS"] += pts_black

            elo_w = dic[xid_white]["ACT_ELO"]
            elo_b = dic[xid_black]["ACT_ELO"]
            dic[xid_white]["ACT_ELO"] = max(
                self.MIN_ELO, dic[xid_white]["ACT_ELO"] + Util.fideELO(elo_w, elo_b, resn_w)
            )
            dic[xid_black]["ACT_ELO"] = max(
                self.MIN_ELO, dic[xid_black]["ACT_ELO"] + Util.fideELO(elo_b, elo_w, resn_b)
            )

    def add_results_crosstabs(self, dic):
        for xmatch in self.li_matches:
            result = xmatch.result
            xid_white, xid_black = xmatch.xid_white, xmatch.xid_black
            dic[xid_white][xid_black] = result

    def get_all_matches(self):
        return self.li_matches


class Swiss:
    def __init__(self, name):
        self.li_opponents = []
        self.__name = name
        self.__path = os.path.join(Code.configuration.folder_swiss(), name + ".swiss")
        self.resign = 350
        self.slow_pieces = False
        self.draw_min_ply = 50
        self.draw_range = 10
        self.adjudicator_active = True
        self.adjudicator = Code.configuration.tutor_default
        self.adjudicator_time = 5.0
        self.time_engine_human = (15.0, 6)
        self.time_engine_engine = (3.0, 0)

        self.current_num_season = None

        self.dic_opponents = None
        self.restore()

    def get_current_season(self):
        if self.current_num_season is None:
            self.create_season_0()
        return self.current_num_season

    def is_editable(self):
        return self.current_num_season is None

    def opponent_by_xid(self, xid):
        if self.dic_opponents is None:
            self.dic_opponents = {opponent.xid: opponent for opponent in self.li_opponents}
        return self.dic_opponents[xid]

    def path(self):
        return self.__path

    def remove_seasons(self):
        self.current_num_season = None
        self.save()
        li_tables = UtilSQL.list_tables(self.path())
        for name in li_tables:
            if name.startswith("SEASON"):
                UtilSQL.remove_table(self.path(), name)

    def folder_work(self):
        return os.path.join(Code.configuration.folder_swiss(), self.__name)

    def name(self):
        return self.__name

    def dic_names(self):
        return {opponent.xid: opponent.name() for opponent in self.li_opponents}

    def add_engine(self, engine):
        op = Opponent()
        op.set_engine(engine)
        self.li_opponents.append(op)

    def add_human(self, name, elo):
        op = Opponent()
        op.set_human(name, elo)
        self.li_opponents.append(op)

    def num_opponents(self):
        return len(self.li_opponents)

    def name_opponent(self, num_opponent):
        return self.li_opponents[num_opponent].name()

    def elo_opponent(self, num_opponent):
        return self.li_opponents[num_opponent].elo()

    def opponent(self, num_opponent):
        return self.li_opponents[num_opponent]

    def correct_opponents(self):
        minimo = max(self.migration * 2, 3)
        li_ndiv = self.list_numdivision(reduced=True)
        for ndiv in li_ndiv:
            if ndiv < minimo:
                return False
        return len(li_ndiv) > 0

    def exist_name(self, name):
        for opponent in self.li_opponents:
            if opponent.name().upper() == name.upper():
                return True
        return False

    def remove_opponent(self, num_opponent):
        del self.li_opponents[num_opponent]

    def list_engines(self):
        return [opponent.opponent for opponent in self.li_opponents if opponent.type == ENGINE]

    def set_engines(self, li_engines):
        st_xhash = set(engine.xhash() for engine in li_engines)
        li_opp = []
        st_ya = set()
        for opponent in self.li_opponents:
            if opponent.type == ENGINE:
                xhash = opponent.opponent.xhash()
                if xhash in st_xhash:
                    li_opp.append(opponent)
                    st_ya.add(opponent.opponent.xhash())
            else:
                li_opp.append(opponent)
        self.li_opponents = li_opp
        for engine in li_engines:
            if engine.xhash() not in st_ya:
                self.add_engine(engine)

    def exist_engine(self, engine):
        for opponent in self.li_opponents:
            if opponent.type == ENGINE and opponent.opponent == engine:
                return True
        return False

    def sort_list(self, modo):
        if modo == "division":
            self.li_opponents.sort(key=lambda x: x.initialdivision * 10000 + (10000 - x.opponent.elo))
        else:
            self.li_opponents.sort(key=lambda x: x.opponent.elo * 100 + (100 - x.initialdivision))

    def save(self):
        dic = {
            "RESIGN": self.resign,
            "SLOW_PIECES": self.slow_pieces,
            "DRAW_MIN_PLY": self.draw_min_ply,
            "DRAW_RANGE": self.draw_range,
            "ADJUDICATOR_ACTIVE": True,  # self.adjudicator_active,
            "ADJUDICATOR": self.adjudicator,
            "ADJUDICATOR_TIME": self.adjudicator_time,
            "TIME_ENGINE_HUMAN": self.time_engine_human,
            "TIME_ENGINE_ENGINE": self.time_engine_engine,
            "MIGRATION": self.migration,
            "SAVED_OPPONENTS": [opponent.save() for opponent in self.li_opponents],
            "CURRENT_NUM_SEASON": self.current_num_season,
            "SCORE_WIN": self.score_win,
            "SCORE_DRAW": self.score_draw,
            "SCORE_LOST": self.score_lost,
        }
        with UtilSQL.DictRawSQL(self.path(), "LEAGUE") as dbl:
            for key, value in dic.items():
                dbl[key] = value

    def restore(self):
        with UtilSQL.DictRawSQL(self.path(), "LEAGUE") as dbl:
            dic_data = dbl.as_dictionary()

        self.resign = dic_data.get("RESIGN", self.resign)
        self.slow_pieces = dic_data.get("SLOW_PIECES", self.slow_pieces)
        self.draw_min_ply = dic_data.get("DRAW_MIN_PLY", self.draw_min_ply)
        self.draw_range = dic_data.get("DRAW_RANGE", self.draw_range)
        self.adjudicator_active = True  # dic_data.get("ADJUDICATOR_ACTIVE", self.adjudicator_active)
        self.adjudicator = dic_data.get("ADJUDICATOR", self.adjudicator)
        self.adjudicator_time = dic_data.get("ADJUDICATOR_TIME", self.adjudicator_time)
        self.time_engine_human = dic_data.get("TIME_ENGINE_HUMAN", self.time_engine_human)
        self.time_engine_engine = dic_data.get("TIME_ENGINE_ENGINE", self.time_engine_engine)
        self.migration = dic_data.get("MIGRATION", self.migration)
        self.current_num_season = dic_data.get("CURRENT_NUM_SEASON", self.current_num_season)
        self.score_win = dic_data.get("SCORE_WIN", self.score_win)
        self.score_draw = dic_data.get("SCORE_DRAW", self.score_draw)
        self.score_lost = dic_data.get("SCORE_LOST", self.score_lost)
        self.li_opponents = []
        for saved in dic_data.get("SAVED_OPPONENTS", []):
            op = Opponent()
            op.restore(saved)
            self.li_opponents.append(op)

    def create_season_0(self):
        season = Season(self, 0)
        season.create_first_season()
        season.save()
        self.current_num_season = 0
        self.save()
        return season

    def read_season(self):
        if self.current_num_season is None:
            return self.create_season_0()
        season = Season(self, self.current_num_season)
        season.restore()
        return season

    def set_current_season(self, num_season):
        self.current_num_season = num_season
        self.save()


class Season:
    li_divisions: list
    current_journey: int = 0
    num_season: int
    swiss: League
    stop_work_journey: bool = False

    def __init__(self, swiss, num_season):
        self.swiss = swiss
        self.num_season = num_season

        self.path = swiss.path()
        self.table = "SEASON_%d" % num_season

    def is_finished(self):
        last_journey = self.get_max_journeys() - 1
        return not self.is_pendings_matches(last_journey)

    def list_seasons(self):
        li = []
        for table in UtilSQL.list_tables(self.path):
            if table.startswith("SEASON_"):
                s = int(table[7:])
                li.append(s)
        return li

    def list_games(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            dic = dbs.as_dictionary()
            li = []
            for k, saved in dic.items():
                try:
                    g = Game.Game()
                    g.restore(saved)
                    li.append(g)
                except TypeError:
                    pass
            return li

    def list_sorted_opponents(self):
        li_opponents = [opponent for opponent in self.swiss.li_opponents]
        li_opponents.sort(key=lambda op: op.name())
        li = []
        for division in self.li_divisions:
            li_xid = division.get_opponents_xid()
            li_div = [op for op in li_opponents if op.xid in li_xid]
            li.append(li_div)
        return li

    def dic_raw_games(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            return dbs.as_dictionary()

    def test_next(self):
        li = UtilSQL.list_tables(self.path)
        next = "SEASON_%d" % (self.num_season + 1,)
        if next not in li:
            season_next = Season(self.swiss, self.num_season + 1)
            season_next.create_from(self)
            season_next.save()

    def num_divisions(self):
        return self.swiss.num_divisions()

    def create_from(self, season_previous):
        num_divisions = self.num_divisions()
        li_panels, dic_xid_order = season_previous.gen_panels_classification()

        li_xid_divisions = [set() for x in range(num_divisions)]
        dic_elo_todos = {}
        for num_division in range(num_divisions):
            d_panel = li_panels[num_division]

            num_opponents = len(d_panel)
            num_migration = self.swiss.migration
            for pos_opponent in range(num_opponents):
                if pos_opponent < num_migration:
                    num_div_new = num_division - 1 if num_division else num_division
                elif pos_opponent < num_opponents - num_migration:
                    num_div_new = num_division
                else:
                    if num_division == (num_divisions - 1):
                        num_div_new = num_division
                    else:
                        num_div_new = num_division + 1

                xid = d_panel[pos_opponent]["XID"]
                li_xid_divisions[num_div_new].add(xid)
                dic_elo_todos[xid] = d_panel[pos_opponent]["ACT_ELO"]

        self.li_divisions = []

        for num_division in range(num_divisions):
            d = Division()
            dic_elo = {xid: elo for xid, elo in dic_elo_todos.items() if xid in li_xid_divisions[num_division]}
            d.set_opponents(dic_elo)
            self.li_divisions.append(d)

    def create_first_season(self):
        self.li_divisions = []
        ndivisions = self.num_divisions()

        for numdivision in range(ndivisions):
            d = Division()
            dic_elo = {
                opponent.xid: opponent.elo()
                for opponent in self.swiss.li_opponents
                if opponent.initialdivision == numdivision
            }
            d.set_opponents(dic_elo)
            self.li_divisions.append(d)
            self.num_season = 0

    def save(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            dbs["LI_SAVED_DIVISIONS"] = [division.save() for division in self.li_divisions]
            dbs["CURRENT_JOURNEY"] = self.current_journey
            dbs["STOP_WORK_JOURNEY"] = self.stop_work_journey

    def restore(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            self.current_journey = dbs.get("CURRENT_JOURNEY", 0)
            self.stop_work_journey = dbs.get("STOP_WORK_JOURNEY", self.stop_work_journey)
            li_saved_divisions = dbs.get("LI_SAVED_DIVISIONS", [])
            self.li_divisions = []
            for saved in li_saved_divisions:
                d = Division()
                d.restore(saved)
                self.li_divisions.append(d)

    def division(self, num):
        return self.li_divisions[num]

    def gen_panels_classification(self):
        li_panels = []
        dic_xid_order = {}
        for division in self.li_divisions:
            li_panels.append(division.gen_panel(self.swiss, dic_xid_order))
        return li_panels, dic_xid_order

    def gen_panels_crosstabs(self):
        li_panels = []
        for division in self.li_divisions:
            li_panels.append(division.gen_dic_crosstabs())
        return li_panels

    def xmatch(self, division, journey, pos):
        return self.li_divisions[division].xmatch(journey, pos)

    def is_pendings_matches(self, journey):
        for xmatch in self.get_all_matches_journey(journey):
            if xmatch.result is None:
                return True
        return False

    def get_current_journey(self):
        max_journeys = self.get_max_journeys()
        for journey in range(self.current_journey, max_journeys):
            if self.is_pendings_matches(journey):
                if journey != self.current_journey:
                    self.current_journey = journey
                    self.save()
                return journey

        return max_journeys

    def get_max_journeys(self):
        t = 0
        for division in self.li_divisions:
            t1 = division.get_num_journeys()
            if t1 > t:
                t = t1
        return t

    def get_all_matches(self):
        return self.get_all_matches_journey(self.current_journey)

    def get_all_matches_journey(self, journey):
        li = []
        for ndivision, division in enumerate(self.li_divisions):
            li_matches = division.get_all_matches(journey)
            for xmatch in li_matches:
                xmatch.label_division = str(ndivision + 1)
            li.extend(li_matches)
        return li

    def get_all_matches_opponent(self, num_division, xid_opponent):
        li = []
        division = self.li_divisions[num_division]
        for journey in range(self.current_journey + 1):
            li_matches = division.get_all_matches(journey)
            for xmatch in li_matches:
                if xid_opponent in (xmatch.xid_black, xmatch.xid_white) and xmatch.result:
                    li.append(xmatch)
        return li

    def get_match(self, num_division, xid_white, xid_black):
        division = self.li_divisions[num_division]
        for journey in range(self.current_journey + 1):
            li_matches = division.get_all_matches(journey)
            for xmatch in li_matches:
                if xid_white == xmatch.xid_white and xid_black == xmatch.xid_black:
                    return xmatch if xmatch.result else None
        return None

    def new_journey(self, swiss: League):
        self.current_journey += 1
        self.save()
        return self.current_journey

    def put_match_done(self, xmatch, game):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbl:
            dbl[xmatch.xid] = game.save()

    def get_game_match(self, xmatch):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbl:
            game_saved = dbl[xmatch.xid]
            if game_saved:
                game = Game.Game()
                game.restore(game_saved)
                return game
            else:
                return None

    def get_division_journey_match(self, xmatch):
        for num_division, division in enumerate(self.li_divisions):
            journey = division.journey_match(xmatch)
            if journey is not None:
                return num_division, journey
