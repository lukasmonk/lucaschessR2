import os
import random

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
    # https://stackoverflow.com/questions/11245746/league-fixture-generator-in-python/48039377#48039377
    # https://stackoverflow.com/users/9157436/carlos-fern%c3%a1ndez
    matches = []
    journeys = []
    return_matches = []
    for xopp in range(1, num_opponents):
        for i in range(num_opponents // 2):
            x = li_opponents[i]
            y = li_opponents[num_opponents - 1 - i]
            if not (x is None or y is None):
                matches.append((x, y))
                return_matches.append((y, x))
        li_opponents.insert(1, li_opponents.pop())
        journeys.insert(len(journeys) // 2, matches)
        journeys.append(return_matches)
        matches = []
        return_matches = []
    ################################################################################################################

    # A continuación se ordenan las jornadas para que se juegue una vez con blancas y la siguiente con negras
    dsides = {num: [0, 0] for num in range(num_opponents)}

    def t_journey(journey):
        t = 0
        for w, b in journey:
            t += (dsides[w][0] + 1 - dsides[w][1]) ** 2
            t += (dsides[b][0] - dsides[b][1] - 1) ** 2
        return t

    num_journeys = len(journeys)
    for njourney in range(num_journeys):
        tmin = 9999999
        nj = -1
        for njourney1 in range(njourney, num_journeys):
            t = t_journey(journeys[njourney1])
            if t < tmin:
                tmin = t
                nj = njourney1
        if nj != njourney:
            journeys[njourney], journeys[nj] = journeys[nj], journeys[njourney]
        for w, b in journeys[njourney]:
            dsides[w][0] += 1
            dsides[b][1] += 1
    return journeys


class Human:
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo

    def save(self):
        return {
            "NAME": self.name,
            "ELO": self.elo,
        }

    def restore(self, dic):
        self.name = dic.get("NAME", self.name)
        self.elo = dic.get("ELO", self.elo)


class Opponent:
    def __init__(self):
        self.type = None
        self.opponent = None
        self.xid = Util.huella()
        self.initialdivision = 0

    def set_engine(self, engine):
        self.type = ENGINE
        self.opponent = engine

    def set_human(self, name, elo):
        self.type = HUMAN
        self.opponent = Human(name, elo)

    def set_initialdivision(self, division):
        self.initialdivision = division

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
            "INITIALDIVISION": self.initialdivision,
        }
        return dic

    def restore(self, dic):
        self.type = dic.get("TYPE", self.type)
        self.xid = dic.get("XID", self.xid)
        self.initialdivision = dic.get("INITIALDIVISION", 0)
        t = dic.get("OPPONENT")
        if t:
            if self.type == HUMAN:
                self.opponent = Human(None, None)
                self.opponent.restore(t)
            else:
                self.opponent = Engines.Engine()
                self.opponent.restore(t)


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

    def is_engine_vs_engine(self, league):
        opw, opb = self.get_opponents(league)
        return not (opw.is_human() or opb.is_human())

    def is_human_vs_engine(self, league):
        opw, opb = self.get_opponents(league)
        return (opw.is_human() and not opb.is_human()) or (not opw.is_human() and opb.is_human())

    def is_human_vs_human(self, league):
        opw, opb = self.get_opponents(league)
        return opw.is_human() and opb.is_human()

    def side_human(self, league):
        opw, opb = self.get_opponents(league)
        if opw.is_human():
            return WHITE
        if opb.is_human():
            return BLACK
        return None

    def get_engine(self, league, side):
        return league.opponent_by_xid(self.xid_white if side == WHITE else self.xid_black)

    def get_opponents(self, league):
        return league.opponent_by_xid(self.xid_white), league.opponent_by_xid(self.xid_black)


class MatchsDay:
    MIN_ELO = 10

    def __init__(self, blk1: list, ida: bool, li_xid_opponents: list):
        self.li_matches = []
        for x, y in blk1:
            xid = li_xid_opponents[x]
            yid = li_xid_opponents[y]
            match = Match(xid, yid) if ida else Match(yid, xid)
            self.li_matches.append(match)

    def save(self):
        return [match.save() for match in self.li_matches]

    def restore(self, li_saved):
        self.li_matches = []
        for dic_saved in li_saved:
            match = Match("", "")
            match.restore(dic_saved)
            self.li_matches.append(match)

    def add_results(self, dic):
        for match in self.li_matches:
            if match.result is None:
                continue
            result = match.result
            xid_white, xid_black = match.xid_white, match.xid_black
            pts_white = pts_black = 0
            dic[xid_white]["PL"] += 1
            dic[xid_black]["PL"] += 1
            resn_w, resn_b = 0, 0
            if result == RESULT_DRAW:
                dic[xid_white]["DRAW"] += 1
                dic[xid_black]["DRAW"] += 1
                pts_white = pts_black = 1
            elif result == RESULT_WIN_WHITE:
                dic[xid_white]["WIN"] += 1
                dic[xid_black]["LOST"] += 1
                pts_white = 3
                resn_w, resn_b = +1, -1
            elif result == RESULT_WIN_BLACK:
                dic[xid_white]["LOST"] += 1
                dic[xid_black]["WIN"] += 1
                pts_black = 3
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

    def get_all_matches(self):
        return self.li_matches


class Division:
    def __init__(self):
        self.dic_elo_opponents = {}  # xid: elo
        self.li_matchdays = []
        self.dic_tiebreak = {}

    def set_opponents(self, dic_elo_opponents):
        self.dic_elo_opponents = dic_elo_opponents
        li_xid_opponents = list(self.dic_elo_opponents.keys())
        random.shuffle(li_xid_opponents)
        for pos, xid in enumerate(li_xid_opponents):
            self.dic_tiebreak[xid] = pos
        self.li_matchdays = []
        li_journeys = create_journeys(len(dic_elo_opponents))
        for ida in (True, False):
            for li_nmatch in li_journeys:
                self.li_matchdays.append(MatchsDay(li_nmatch, ida, li_xid_opponents))

    def save(self):
        return {
            "DIC_ELO_OPPONENTS": self.dic_elo_opponents,
            "DIC_TIEBREAK": self.dic_tiebreak,
            "LI_MATCHDAYS": [matchday.save() for matchday in self.li_matchdays],
        }

    def restore(self, dic):
        self.dic_elo_opponents = dic["DIC_ELO_OPPONENTS"]
        self.dic_tiebreak = dic["DIC_TIEBREAK"]
        self.li_matchdays = []
        li_xid_opponents = list(self.dic_elo_opponents.keys())
        for matchday_saved in dic["LI_MATCHDAYS"]:
            matchday = MatchsDay([], False, li_xid_opponents)
            matchday.restore(matchday_saved)
            self.li_matchdays.append(matchday)

    def gen_panel(self):
        li_xid_opponents = list(self.dic_elo_opponents.keys())
        dic_xid = {
            xid: {
                "XID": xid,
                "PL": 0,
                "PTS": 0,
                "WIN": 0,
                "LOST": 0,
                "DRAW": 0,
                "TB": self.dic_tiebreak[xid],
                "INI_ELO": self.dic_elo_opponents[xid],
                "ACT_ELO": self.dic_elo_opponents[xid],
            }
            for xid in li_xid_opponents
        }
        for matchday in self.li_matchdays:
            matchday.add_results(dic_xid)
        li_panel = list(dic_xid.values())

        def comp(x):
            xdif_elo = "%04d" % (x["ACT_ELO"] - x["INI_ELO"] + 1000)
            xelo = "%04d" % (9999 - x["ACT_ELO"])
            xpts = "%03d" % x["PTS"]
            xwin = "%03d" % x["WIN"]
            xtb = "%d" % x["TB"]
            return xpts + xwin + xdif_elo + xelo + xtb

        li_panel.sort(key=comp, reverse=True)
        return li_panel

    def match(self, journey, pos):
        matchday = self.li_matchdays[journey]
        return matchday.li_matches[pos]

    def get_all_matches(self, journey):
        return self.li_matchdays[journey].get_all_matches() if len(self.li_matchdays) > journey else []

    def get_num_journeys(self):
        return len(self.li_matchdays)


class League:
    def __init__(self, name):
        self.li_opponents = []
        self.__name = name
        self.__path = os.path.join(Code.configuration.folder_leagues(), name + ".league")

        self.resign = 350
        self.slow_pieces = False
        self.draw_min_ply = 50
        self.draw_range = 10
        self.adjudicator_active = True
        self.adjudicator = Code.configuration.tutor_default
        self.adjudicator_time = 5.0
        self.time_engine_human = (15.0, 6)
        self.time_engine_engine = (3.0, 0)
        self.migration = 3

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
        return os.path.join(Code.configuration.folder_leagues(), self.__name)

    def name(self):
        return self.__name

    def next_division(self, opponent_new: Opponent):
        elo = opponent_new.elo()
        dv = 999
        for opponent in self.li_opponents:
            if opponent.elo() <= elo:
                if opponent.initialdivision < dv:
                    dv = opponent.initialdivision
        return dv if dv < 999 else 0

    def dic_names(self):
        return {opponent.xid: opponent.name() for opponent in self.li_opponents}

    def add_engine(self, engine):
        op = Opponent()
        op.set_engine(engine)
        op.set_initialdivision(self.next_division(op))
        self.li_opponents.append(op)

    def add_human(self, name, elo):
        op = Opponent()
        op.set_human(name, elo)
        op.set_initialdivision(self.next_division(op))
        self.li_opponents.append(op)

    def list_numdivision(self, reduced=False):
        li_ndiv = [0] * 100
        for opponent in self.li_opponents:
            li_ndiv[opponent.initialdivision] += 1
        if reduced:
            while li_ndiv and li_ndiv[-1] == 0:
                li_ndiv.pop()
        return li_ndiv

    def num_divisions(self):
        return len(self.list_numdivision(True))

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
    league: League

    def __init__(self, league, num_season):
        self.league = league
        self.num_season = num_season

        self.path = league.path()
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
            for saved in dic.values():
                try:
                    g = Game.Game()
                    g.restore(saved)
                    li.append(g)
                except TypeError:
                    pass
            return li

    def test_next(self):
        li = UtilSQL.list_tables(self.path)
        next = "SEASON_%d" % (self.num_season + 1,)
        if next not in li:
            season_next = Season(self.league, self.num_season + 1)
            season_next.create_from(self)
            season_next.save()

    def num_divisions(self):
        return self.league.num_divisions()

    def create_from(self, season_previous):
        num_divisions = self.num_divisions()
        li_panels = season_previous.gen_panels_classification()

        li_xid_divisions = [set() for x in range(num_divisions)]
        dic_elo_todos = {}
        for num_division in range(num_divisions):
            d_panel = li_panels[num_division]

            num_opponents = len(d_panel)
            num_migration = self.league.migration
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
                for opponent in self.league.li_opponents
                if opponent.initialdivision == numdivision
            }
            d.set_opponents(dic_elo)
            self.li_divisions.append(d)
            self.num_season = 0

    def save(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            dbs["LI_SAVED_DIVISIONS"] = [division.save() for division in self.li_divisions]
            dbs["CURRENT_JOURNEY"] = self.current_journey

    def restore(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            self.current_journey = dbs.get("CURRENT_JOURNEY", 0)
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
        for division in self.li_divisions:
            li_panels.append(division.gen_panel())
        return li_panels

    def match(self, division, journey, pos):
        return self.li_divisions[division].match(journey, pos)

    def is_pendings_matches(self, journey):
        for match in self.get_all_matches_journey(journey):
            if match.result is None:
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
            for match in li_matches:
                match.label_division = str(ndivision + 1)
            li.extend(li_matches)
        return li

    def new_journey(self, league: League):
        self.current_journey += 1
        self.save()
        return self.current_journey

    def put_match_done(self, match, game):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbl:
            dbl[match.xid] = game.save()

    def get_game_match(self, match):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbl:
            game_saved = dbl[match.xid]
            if game_saved:
                game = Game.Game()
                game.restore(game_saved)
                return game
            else:
                return None