import collections
import math
import random

import Code
from Code import Util
from Code.Base import Game
from Code.Base.Constantes import RESULT_WIN_WHITE, RESULT_WIN_BLACK, RESULT_DRAW, ENGINE, HUMAN, WHITE, BLACK
from Code.Engines import Engines
from Code.SQL import UtilSQL


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
        self.element = None
        self.xid = Util.huella()
        self.tiebreak = 0

        self.white = 0
        self.black = 0
        self.last_played = None
        self.byes = 0
        self.li_win = []  # rivales a los que ha ganado, se pueden repetir
        self.li_draw = []
        self.li_lost = []
        self.current_elo = 0

    def get_score(self, swiss):
        return len(self.li_win) * swiss.score_win + len(self.li_draw) * swiss.score_draw + len(
            self.li_lost) * swiss.score_lost + self.byes * swiss.score_byes

    def name(self):
        return self.element.name if self.element else ""

    def get_start_elo(self):
        return self.element.elo if self.element else 0

    def get_current_elo(self):
        return self.current_elo if self.current_elo else self.get_start_elo()

    def set_engine(self, engine):
        self.type = ENGINE
        self.element = engine
        self.current_elo = engine.elo

    def set_human(self, name, elo):
        self.type = HUMAN
        self.element = Human(name, elo)
        self.current_elo = elo

    def set_elo_start(self, elo):
        self.element.elo = elo

    # def set_elo_current(self, elo):
    #     self.current_elo = elo

    def set_name(self, name):
        self.element.name = name

    def is_human(self):
        return self.type == HUMAN

    def save(self):
        dic = {
            "TYPE": self.type,
            "XID": self.xid,
            "ELEMENT": self.element.save(),
            "TIEBREAK": self.tiebreak,
        }
        return dic

    def restore(self, dic):
        self.type = dic.get("TYPE", self.type)
        self.xid = dic.get("XID", self.xid)
        t = dic.get("ELEMENT")
        if t:
            if self.type == HUMAN:
                self.element = Human(None, None)
                self.element.restore(t)
            else:
                self.element = Engines.Engine()
                self.element.restore(t)
        self.tiebreak = dic.get("TIEBREAK", 0)

    def key_order(self, swiss):
        fn = swiss.opponent_by_xid
        score = int(self.get_score(swiss) * 100)

        score_rival_win = sum(fn(xrival).get_score(swiss) for xrival in self.li_win)
        score_rival_draw = sum(fn(xrival).get_score(swiss) for xrival in self.li_draw)
        score_sum_rival = int(score_rival_win * 10 + score_rival_draw * 5)
        # se indica current_elo y no get_current_elo(), porque inicialmente no hay un orden
        return (f"{score:04d}{score_sum_rival:05d}{len(self.li_win):03d}{len(self.li_draw):03d}"
                f"{self.current_elo:04d}{self.tiebreak:04d}")

    def next_side(self):
        if self.white < self.black:
            return WHITE
        elif self.white > self.black:
            return BLACK
        elif self.last_played is not None:
            return WHITE if self.last_played == BLACK else BLACK
        else:
            return None

    def reset(self):
        self.white = 0
        self.black = 0
        self.last_played = None
        self.byes = 0
        self.li_win = []
        self.li_draw = []
        self.li_lost = []
        self.current_elo = self.element.elo


class Match:
    # Variables temporales
    white_name = None
    black_name = None
    cjourney = None
    journey = None

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

    def __init__(self):
        self.li_matches = []

    def genera_matches(self, swiss, set_mached_played):
        self.li_matches = []

        li_opponents = swiss.li_opponents


        if len(li_opponents) % 2 == 1:  # hay un bye
            num_byes = 0
            while True:
                li_no_bye = [opponent for opponent in li_opponents if opponent.byes == num_byes]
                if len(li_no_bye) == 0:
                    num_byes += 1
                else:
                    break
            player_bye = random.choice(li_no_bye)
            player_bye.byes += 1
            li_opponents_play = [opponent for opponent in li_opponents if opponent != player_bye]
        else:
            li_opponents_play = li_opponents[:]

        dic_xid_oponents_played = collections.defaultdict(list)
        for xid1, xid2 in set_mached_played:
            dic_xid_oponents_played[xid1].append(xid2)
            dic_xid_oponents_played[xid2].append(xid1)

        if len(set_mached_played) == 0:
            random.shuffle(li_opponents)
        else:
            li_opponents_play.sort(key=lambda opponent: opponent.key_order(swiss), reverse=True)

        st_xid_playing = set()
        num_players_play = len(li_opponents_play)
        for first_pass in (True, False):
            for num in range(num_players_play - 1):
                player: Opponent = li_opponents_play[num]
                if player.xid in st_xid_playing:
                    continue

                li_opponents_played = dic_xid_oponents_played[player.xid]
                st_opponents_played = set(li_opponents_played)
                rival_select = None
                look_for = player.next_side()

                # 1. Buscamos uno con el que no haya jugado y que sea compatible con el side
                for pos in range(num + 1, num_players_play):
                    rival = li_opponents_play[pos]
                    if rival.xid in st_xid_playing:
                        continue
                    if rival.xid in st_opponents_played:
                        continue
                    look_for_rival = rival.next_side()
                    if look_for is None or look_for_rival is None:
                        rival_select = rival
                        break
                    if look_for_rival != look_for:
                        rival_select = rival
                        break

                # 2. Buscamos uno con el que no haya jugado aunque no sea compatible con el side
                if rival_select is None:
                    for pos in range(num + 1, num_players_play):
                        rival = li_opponents_play[pos]
                        if rival.xid in st_xid_playing:
                            continue
                        if rival.xid not in st_opponents_played:
                            rival_select = rival
                            break

                if rival_select is None and first_pass:  # no se repiten rivales en la primera pasada
                    continue

                # 3. Si no encuentra nada, que juegue contra el siguiente compatible con el side, que haya jugado menos
                if rival_select is None:
                    num_played = 1000
                    for pos in range(num + 1, num_players_play):
                        rival = li_opponents_play[pos]
                        if rival.xid in st_xid_playing:
                            continue
                        look_for_rival = rival.next_side()
                        if look_for_rival != look_for:
                            games_played = li_opponents_played.count(rival.xid)
                            if games_played < num_played:
                                rival_select = rival
                                num_played = games_played

                # 4. Si no encuentra nada, que juegue contra el que haya jugado menos
                if rival_select is None:
                    num_played = 1000
                    for pos in range(num + 1, num_players_play):
                        rival = li_opponents_play[pos]
                        if rival.xid in st_xid_playing:
                            continue
                        games_played = li_opponents_played.count(rival.xid)
                        if games_played < num_played:
                            rival_select = rival
                            num_played = games_played

                # 5. El primero que encuentre
                if rival_select is None:
                    for pos in range(num + 1, num_players_play):
                        rival = li_opponents_play[pos]
                        if rival.xid in st_xid_playing:
                            continue
                        rival_select = rival
                        break

                if look_for in (WHITE, BLACK):
                    if look_for == WHITE:
                        player_w, player_b = player, rival_select
                    else:
                        player_w, player_b = rival_select, player
                else:
                    look_for_rival = rival_select.next_side()
                    if look_for_rival == BLACK:
                        player_w, player_b = player, rival_select
                    elif look_for_rival == WHITE:
                        player_w, player_b = rival_select, player
                    else:
                        player_w, player_b = player, rival_select

                player_w.white += 1
                player_b.black += 1
                player_w.last_played = WHITE
                player_b.last_played = BLACK
                st_xid_playing.add(player_w.xid)
                st_xid_playing.add(player_b.xid)
                match = Match(player_w.xid, player_b.xid)
                self.li_matches.append(match)

    def save(self):
        return [xmatch.save() for xmatch in self.li_matches]

    def restore(self, li_saved):
        self.li_matches = []
        for dic_saved in li_saved:
            xmatch = Match("", "")
            xmatch.restore(dic_saved)
            self.li_matches.append(xmatch)

    def update_opponents(self, swiss):
        st_xid_opponents_play = set()  # to know byes

        for xmatch in self.li_matches:
            xid_white, xid_black = xmatch.xid_white, xmatch.xid_black
            st_xid_opponents_play.add(xid_white)
            st_xid_opponents_play.add(xid_black)
            if xmatch.result is None:
                continue

            op_white: Opponent = swiss.opponent_by_xid(xid_white)
            op_black: Opponent = swiss.opponent_by_xid(xid_black)

            op_white.last_played = WHITE
            op_black.last_played = BLACK

            result = xmatch.result

            op_white.white += 1
            op_black.black += 1

            resn_w, resn_b = 0, 0
            if result == RESULT_DRAW:
                op_white.li_draw.append(xid_black)
                op_black.li_draw.append(xid_white)

            elif result == RESULT_WIN_WHITE:
                op_white.li_win.append(xid_black)
                op_black.li_lost.append(xid_white)
                resn_w, resn_b = +1, -1

            elif result == RESULT_WIN_BLACK:
                op_white.li_lost.append(xid_black)
                op_black.li_win.append(xid_white)
                resn_w, resn_b = -1, +1

            elo_w = op_white.current_elo
            elo_b = op_black.current_elo
            op_white.current_elo = max(self.MIN_ELO, elo_w + Util.fideELO(elo_w, elo_b, resn_w))
            op_black.current_elo = max(self.MIN_ELO, elo_b + Util.fideELO(elo_b, elo_w, resn_b))

        for opponent in swiss.li_opponents:
            if opponent.xid not in st_xid_opponents_play:
                opponent.byes += 1

    def add_results_crosstabs(self, dic):
        for xmatch in self.li_matches:
            result = xmatch.result
            xid_white, xid_black = xmatch.xid_white, xmatch.xid_black
            dic[xid_white][xid_black] = result

    def get_all_matches(self):
        return self.li_matches


def num_matchesdays(n_opponents):
    return math.ceil(math.log2(n_opponents)) if n_opponents else 0


class Swiss:
    def __init__(self, name):
        self.li_opponents = []
        self.__name = name
        self.__path: str = str(Util.opj(Code.configuration.folder_swisses(), name + ".swiss"))
        self.resign = 350
        self.slow_pieces = False
        self.draw_min_ply = 50
        self.draw_range = 10
        self.adjudicator_active = True
        self.adjudicator = Code.configuration.analyzer_default
        self.adjudicator_time = 5.0
        self.time_engine_human = (15.0, 6)
        self.time_engine_engine = (3.0, 0)

        self.score_win = 3
        self.score_draw = 1
        self.score_lost = 0
        self.score_byes = 0

        self.num_matchdays = 0

        self.current_num_season = None

        self.dic_opponents = None
        self.restore()

    def path(self):
        return self.__path

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
            "SAVED_OPPONENTS": [opponent.save() for opponent in self.li_opponents],
            "CURRENT_NUM_SEASON": self.current_num_season,
            "SCORE_WIN": self.score_win,
            "SCORE_DRAW": self.score_draw,
            "SCORE_LOST": self.score_lost,
            "SCORE_BYES": self.score_byes,
            "NUM_MATCHDAYS": self.num_matchdays,
        }
        with UtilSQL.DictRawSQL(self.path(), "SWISS") as dbl:
            for key, value in dic.items():
                dbl[key] = value

    def restore(self):
        with UtilSQL.DictRawSQL(self.path(), "SWISS") as dbl:
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
        self.current_num_season = dic_data.get("CURRENT_NUM_SEASON", self.current_num_season)
        self.score_win = dic_data.get("SCORE_WIN", self.score_win)
        self.score_draw = dic_data.get("SCORE_DRAW", self.score_draw)
        self.score_lost = dic_data.get("SCORE_LOST", self.score_lost)
        self.score_byes = dic_data.get("SCORE_BYES", self.score_byes)
        self.num_matchdays = dic_data.get("NUM_MATCHDAYS", self.num_matchdays)

        self.li_opponents = []
        for saved in dic_data.get("SAVED_OPPONENTS", []):
            op = Opponent()
            op.restore(saved)
            self.li_opponents.append(op)

    def name(self):
        return self.__name

    def is_editable(self):
        return len(self.list_seasons()) == 0

    def list_seasons(self):
        li = []
        for table in UtilSQL.list_tables(self.__path):
            if table.startswith("SEASON_"):
                s = int(table[7:])
                li.append(s)
        return li

    def num_opponents(self):
        return len(self.li_opponents)

    def max_journeys(self):
        return num_matchesdays(len(self.li_opponents)) if self.num_matchdays == 0 else self.num_matchdays

    def sort_list_opponents(self):
        self.li_opponents.sort(key=lambda x: x.get_current_elo())

    def opponent(self, num_opponent):
        return self.li_opponents[num_opponent]

    def add_engine(self, engine):
        op = Opponent()
        op.set_engine(engine)
        self.li_opponents.append(op)
        self.set_tiebreak()

    def add_human(self, name, elo):
        op = Opponent()
        op.set_human(name, elo)
        self.li_opponents.append(op)
        self.set_tiebreak()

    def set_tiebreak(self):
        n_opponents = len(self.li_opponents)
        if n_opponents > 0:
            li = list(range(n_opponents))
            random.shuffle(li)
            for n_opponent in range(n_opponents):
                self.li_opponents[n_opponent].tiebreak = li[n_opponent]

    def name_opponent(self, num_opponent):
        return self.li_opponents[num_opponent].name()

    def elo_opponent(self, num_opponent):
        return self.li_opponents[num_opponent].get_current_elo()

    def exist_name(self, name):
        for opponent in self.li_opponents:
            if opponent.name().upper() == name.upper():
                return True
        return False

    def remove_opponent(self, num_opponent):
        del self.li_opponents[num_opponent]

    def enough_opponents(self):
        return len(self.li_opponents) >= 3

    def list_engines(self):
        return [opponent.element for opponent in self.li_opponents if opponent.type == ENGINE]

    def set_engines(self, li_engines):
        st_xhash = set(engine.xhash() for engine in li_engines)
        li_opp = []
        st_ya = set()
        for opponent in self.li_opponents:
            if opponent.type == ENGINE:
                xhash = opponent.element.xhash()
                if xhash in st_xhash:
                    li_opp.append(opponent)
                    st_ya.add(opponent.element.xhash())
            else:
                li_opp.append(opponent)
        self.li_opponents = li_opp
        for engine in li_engines:
            if engine.xhash() not in st_ya:
                self.add_engine(engine)

    def exist_engine(self, engine):
        for opponent in self.li_opponents:
            if opponent.type == ENGINE and opponent.element == engine:
                return True
        return False

    def remove_seasons(self):
        self.current_num_season = None
        self.save()
        li_tables = UtilSQL.list_tables(self.path())
        for name in li_tables:
            if name.startswith("SEASON"):
                UtilSQL.remove_table(self.path(), name)

    def read_season(self):
        if self.current_num_season is None:
            return self.create_season_0()
        season = Season(self, self.current_num_season)
        season.restore()
        if len(season.li_matchesdays) == 0:
            season.create_matches_day()
        return season

    def create_season_0(self):
        season = Season(self, 0)
        season.create_first_season()
        season.save()
        self.current_num_season = 0
        self.save()
        return season

    def set_current_season(self, num_season):
        self.current_num_season = num_season
        self.save()

    def opponent_by_xid(self, xid):
        if self.dic_opponents is None:
            self.dic_opponents = {opponent.xid: opponent for opponent in self.li_opponents}
        return self.dic_opponents[xid]

    def dic_names(self):
        return {opponent.xid: opponent.name() for opponent in self.li_opponents}


class Season:
    current_journey: int = 0
    num_season: int
    swiss: Swiss
    stop_work_journey: bool = False

    def __init__(self, swiss, num_season):
        self.swiss = swiss
        self.num_season = num_season

        self.li_matchesdays = []

        self.path = swiss.path()
        self.table = "SEASON_%d" % num_season

    def save(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            dbs["CURRENT_JOURNEY"] = self.current_journey
            dbs["STOP_WORK_JOURNEY"] = self.stop_work_journey
            dbs["LI_MATCHSDAYS"] = [matchesday.save() for matchesday in self.li_matchesdays]

    def restore(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            self.current_journey = dbs.get("CURRENT_JOURNEY", 0)
            self.stop_work_journey = dbs.get("STOP_WORK_JOURNEY", self.stop_work_journey)
            self.li_matchesdays = []
            for matchesday_saved in dbs.get("LI_MATCHSDAYS", []):
                matchesday = MatchsDay()
                matchesday.restore(matchesday_saved)
                self.li_matchesdays.append(matchesday)

    def create_first_season(self):
        self.create_matches_day()

    def create_matches_day(self):
        set_matches_played = {(match.xid_white, match.xid_black) for match in self.get_all_matches_played()}
        matches_day = MatchsDay()
        matches_day.genera_matches(self.swiss, set_matches_played)
        self.li_matchesdays.append(matches_day)
        self.save()

    def update_opponents(self):
        opponent: Opponent
        for opponent in self.swiss.li_opponents:
            opponent.reset()

        matchesday: MatchsDay
        for matchesday in self.li_matchesdays:
            matchesday.update_opponents(self.swiss)

    def gen_panel_classification(self):
        self.update_opponents()

        li_opponents = self.swiss.li_opponents[:]

        def comp(op):
            return op.key_order(self.swiss)

        li_opponents.sort(key=comp, reverse=True)
        dic_xid_pos = {op.xid: pos for pos, op in enumerate(li_opponents, 1)}

        dic_xid = {
            op.xid: {
                "XID": op.xid,
                "PL": op.white + op.black,
                "PLW": op.white,
                "PLB": op.black,
                "PTS": op.get_score(self.swiss),
                "WIN": len(op.li_win),
                "LOST": len(op.li_lost),
                "DRAW": len(op.li_draw),
                "TIEBREAK": op.tiebreak,
                "INI_ELO": op.element.elo,
                "ACT_ELO": op.current_elo
            }
            for op in li_opponents
        }

        li_panel = list(dic_xid.values())

        return li_panel, dic_xid_pos

    def gen_panel_crosstabs(self):
        li_xid_opponents = [opponent.xid for opponent in self.swiss.li_opponents]
        dic_xid = {xid_white: {xid_black: None for xid_black in li_xid_opponents} for xid_white in li_xid_opponents}
        matchesday: MatchsDay
        for matchesday in self.li_matchesdays:
            matchesday.add_results_crosstabs(dic_xid)
        return dic_xid

    def list_sorted_opponents(self):
        li_opponents = [opponent for opponent in self.swiss.li_opponents]
        li_opponents.sort(key=lambda op: op.name())
        return li_opponents

    def get_last_journey(self):
        return len(self.li_matchesdays) - 1

    def is_finished(self):
        last_journey = self.swiss.max_journeys() - 1
        if last_journey > self.get_last_journey():
            return False
        return not self.is_pendings_matches(last_journey)

    def is_pendings_matches(self, journey):
        for xmatch in self.get_all_matches_journey(journey):
            if xmatch.result is None:
                return True
        return False

    def get_all_matches(self, journey=None):
        if journey is None:
            journey = self.get_last_journey()
        return self.li_matchesdays[journey].li_matches

    def get_all_matches_journey(self, journey):
        return self.li_matchesdays[journey].li_matches if len(self.li_matchesdays) > journey else []

    def get_all_matches_last_journey(self):
        journey = self.get_last_journey()
        return self.li_matchesdays[journey].li_matches

    def get_all_matches_played(self):
        li_matches = []
        for matchesday in self.li_matchesdays:
            li_matches.extend(matchesday.li_matches)
        return li_matches

    def test_next(self):
        li = UtilSQL.list_tables(self.path)
        xnext = "SEASON_%d" % (self.num_season + 1,)
        if xnext not in li:
            season_next = Season(self.swiss, self.num_season + 1)
            season_next.create_from(self)
            season_next.save()

    @staticmethod
    def create_from(season_previous):
        d_panel, dic_xid_order = season_previous.gen_panel_classification()

        dic_elo_todos = {}

        num_opponents = len(d_panel)
        for pos_opponent in range(num_opponents):
            xid = d_panel[pos_opponent]["XID"]
            dic_elo_todos[xid] = d_panel[pos_opponent]["ACT_ELO"]

    def dic_raw_games(self):
        with UtilSQL.DictRawSQL(self.path, self.table) as dbs:
            return dbs.as_dictionary()

    def get_all_matches_opponent(self, xid_opponent):
        li = []
        for journey in range(self.current_journey + 1):
            li_matches = self.get_all_matches(journey)
            for xmatch in li_matches:
                if xid_opponent in (xmatch.xid_black, xmatch.xid_white) and xmatch.result:
                    li.append(xmatch)
        return li

    def get_match(self, xid_white, xid_black):
        for journey in range(self.current_journey + 1):
            li_matches = self.get_all_matches(journey)
            for xmatch in li_matches:
                if xid_white == xmatch.xid_white and xid_black == xmatch.xid_black:
                    return xmatch if xmatch.result else None
        return None

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
