import Code
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import ENG_WICKER, BOOK_RANDOM_UNIFORM
from Code.Books import Books
from Code.Engines import EngineManager, EngineResponse


class EngineManagerWicker(EngineManager.EngineManager):
    def __init__(self, conf_engine, direct=False):
        EngineManager.EngineManager.__init__(self, conf_engine, direct)
        self.is_ending = False
        self.xbook = None

    def check_is_ending(self, game):
        last_position: Position.Position = game.last_position
        if self.is_ending or len(game) < last_position.num_moves:
            return

        dic_pieces = last_position.dic_pieces()

        def count(str_pz):
            return sum(dic_pieces.get(pz, 0) for pz in str_pz)

        ok = False

        if last_position.is_white:
            if count("pnbrq") == 0:
                ok = count('QR') >= 1
        else:
            if count("PNBRQ") == 0:
                ok = count('qr') >= 1

        if not ok:
            return

        engine = self.engine

        engine.set_option("UCI_LimitStrength", "true")
        engine.set_option("UCI_Elo", "2300")
        engine.set_option("Hash", "16")
        exe = engine.exe
        if "rodentii" in exe:
            engine.set_option("NpsLimit", "10000")
        elif "greko98" in exe:
            # Greko98 cannot mate when RandomEval or MultiPV are too high.
            engine.set_option("RandomEval", "2")
            engine.set_option("MultiPV", "1")
        elif "maia" in exe:
            # Maia doesn't understand UCI_Elo and needs a high NPS value.
            engine.set_option("NodesPerSecondLimit", "170")
        elif "irina" in exe:
            # Irina doesn't understand UCI_Elo.
            engine.set_option("NpsLimit", "25000")

        self.is_ending = True

    def check_book(self, game):
        if len(game) <= 2 and self.xbook is None:
            if self.confMotor.book and Util.exist_file(self.confMotor.book):
                self.xbook = Books.Book("P", self.confMotor.book, self.confMotor.book, True)
                self.xbook.polyglot()
            else:
                self.xbook = None

        if self.xbook:
            bdepth = self.confMotor.book_max_plies
            if bdepth == 0 or len(game) < bdepth:
                fen = game.last_fen()
                rr = self.confMotor.book_rr
                pv = self.xbook.eligeJugadaTipo(fen, rr)
                if pv:
                    rm_rival = EngineResponse.EngineResponse("Opening", game.last_position.is_white)
                    rm_rival.from_sq = pv[:2]
                    rm_rival.to_sq = pv[2:4]
                    rm_rival.promotion = pv[4:]
                    return rm_rival
            self.xbook = None

        return None

    def play_time(self, game, seconds_white, seconds_black, seconds_move, adjusted=0):
        self.check_engine()

        rm = self.check_book(game)
        if rm:
            return rm
        else:
            self.check_is_ending(game)

        return EngineManager.EngineManager.play_time(self, game, seconds_white, seconds_black, seconds_move, adjusted)

    def play_time_tourney(self, game, seconds_white, seconds_black, seconds_move):
        self.check_engine()

        rm = self.check_book(game)
        if rm:
            return rm
        else:
            self.check_is_ending(game)

        if self.mstime_engine or self.depth_engine:
            mrm = self.engine.bestmove_game(game, self.mstime_engine, self.depth_engine)
        else:
            mseconds_white = int(seconds_white * 1000)
            mseconds_black = int(seconds_black * 1000)
            mseconds_move = int(seconds_move * 1000) if seconds_move else 0
            mrm = self.engine.bestmove_time(game, mseconds_white, mseconds_black, mseconds_move)
        return mrm


def read_wicker_engines():
    configuration = Code.configuration
    file = Code.path_resource("IntFiles", "wicker.ini")

    dic_wicker = Util.ini2dic(file)
    li = []
    for alias, dic in dic_wicker.items():
        nom_base_engine = dic["ENGINE"]
        id_info = dic["IDINFO"]
        li_info = [_F(x.strip()) for x in id_info.split(",")]
        id_info = "\n".join(li_info)
        elo = int(dic["ELO"])
        li_uci = [v.split(":") for k, v in dic.items() if k.startswith("OPTION")]
        nom_book = dic["BOOK"]
        book_rr = dic.get("BOOKRR", BOOK_RANDOM_UNIFORM)
        book = configuration.path_book(nom_book)
        max_plies = int(dic.get("BOOKMAXPLY", 0))
        if max_plies == 0:
            if elo >= 2200:
                max_plies = 9999
            else:
                max_plies = round((elo / 1000) + 3.5 * (elo / 1000) * (elo / 1000))

        engine = configuration.dic_engines.get(nom_base_engine)
        if engine:
            eng = engine.clona()
            eng.name = _SP(alias)
            eng.id_info = id_info
            eng.alias = alias
            eng.elo = elo
            eng.liUCI = li_uci
            eng.book = book
            eng.book_max_plies = max_plies
            eng.book_rr = book_rr
            eng.type = ENG_WICKER
            li.append(eng)

    li.sort(key=lambda uno: uno.elo)
    return li
