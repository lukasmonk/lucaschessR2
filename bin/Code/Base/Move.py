import Code
import Code.Base.Game  # To prevent recursivity in Variations -> import direct
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import HIGHEST_VARIATIONS, BETTER_VARIATIONS
from Code.Engines import EngineResponse
from Code.Nags.Nags import NAG_0, NAG_3, NAG_6, html_nag_txt, html_nag_symbol
from Code.Translations import TrListas


def crea_dic_html():
    base = '<span style="font-family:Chess Merida;"><big>%s</big></span>'
    return {x: base % x for x in "pnbrqkPNBRQK"}


dicHTMLFigs = crea_dic_html()


class Move:
    def __init__(self, game, position_before=None, position=None, from_sq=None, to_sq=None, promotion=""):
        self.game = game
        self.analysis = None
        self.position_before = position_before
        self.position = position
        self.in_the_opening = False
        self.from_sq = from_sq if from_sq else ""
        self.to_sq = to_sq if to_sq else ""
        self.promotion = promotion if promotion else ""

        self.variations = Variations(self)
        self.comment = ""
        self.li_themes = []

        self.li_nags = []
        self.time_ms = 0
        self.clock_ms = 0

        self.is_book = False

        self.elo = None
        self.questionable_move = None
        self.bad_move = None
        self.verybad_move = None

        self.elo_avg = 0

    def set_time_ms(self, ms):
        self.time_ms = ms

    def set_clock_ms(self, ms):
        self.clock_ms = ms if ms > 0 else 0

    def only_has_move(self) -> bool:
        return not (
                self.variations
                or self.comment
                or len(self.li_nags) > 0
                or self.analysis
                or len(self.li_themes) > 0
                or self.time_ms
        )

    @property
    def get_themes(self) -> []:
        return self.li_themes

    def has_themes(self) -> bool:
        return len(self.get_themes) > 0

    def add_theme(self, theme):
        if theme not in self.get_themes:
            self.li_themes.append(theme)

    def clear_themes(self):
        self.li_themes = []

    def get_points_lost(self):
        if self.analysis is None:
            return None
        mrm, pos = self.analysis
        pts = mrm.li_rm[pos].centipawns_abs()
        pts0 = mrm.li_rm[0].centipawns_abs()
        return pts0 - pts

    def get_points_lost_mate(self):
        if self.analysis is None:
            return None, None
        mrm, pos = self.analysis
        if pos == 0:
            return None, None
        rm_best = mrm.li_rm[0]
        rm_user = mrm.li_rm[pos]
        pts = mrm.li_rm[pos].centipawns_abs()
        pts0 = mrm.li_rm[0].centipawns_abs()
        dif = pts0 - pts
        if dif:
            if rm_user.mate != 0 and rm_best.mate != 0:
                return 0, rm_best.mate - rm_user.mate
            elif rm_user.mate != 0 or rm_best.mate != 0:
                return dif, rm_best.mate - rm_user.mate

        return dif, None

    @property
    def liMovs(self):
        li_movs = [("b", self.to_sq), ("m", self.from_sq, self.to_sq)]
        if self.position.li_extras:
            li_movs.extend(self.position.li_extras)
        return li_movs

    @property
    def is_check(self):
        return self.position.is_check()

    @property
    def is_mate(self):
        return self.position.is_mate()

    @property
    def is_draw(self):
        return self.game.is_draw() and self.game.last_jg() == self

    @property
    def pgnBase(self):
        xpgn_base = self.position_before.pgn(self.from_sq, self.to_sq, self.promotion)
        return xpgn_base

    def add_nag(self, nag):
        if nag in (None, ""):
            return
        if nag <= NAG_6:
            for pos, n in enumerate(self.li_nags):
                if n <= NAG_6:
                    del self.li_nags[pos]
            if nag == NAG_0:
                return
        else:
            for pos, n in enumerate(self.li_nags):
                if nag == n:
                    return
        self.li_nags.append(nag)

    def is_brilliant(self):
        return NAG_3 in self.li_nags

    def del_nags(self):
        self.li_nags = []

    def del_variations(self):
        self.variations.clear()

    def del_comment(self):
        self.comment = ""

    def set_comment(self, comment):
        self.comment = comment.replace("}", "]").replace("{", "]")

    def add_comment(self, comment):
        if self.comment:
            self.comment += "\n"
        self.comment += comment.replace("}", "]").replace("{", "]")

    def del_analysis(self):
        self.analysis = None

    def del_themes(self):
        self.li_themes = []

    def is_white(self):
        return self.position_before.is_white

    def fen_base(self):
        return self.position.fen_base()

    def pv2dgt(self):
        return self.position_before.pv2dgt(self.from_sq, self.to_sq, self.promotion)

    def siCaptura(self):
        if self.to_sq:
            return self.position_before.squares.get(self.to_sq) is not None
        else:
            return False

    def movimiento(self):
        return self.from_sq + self.to_sq + self.promotion

    def pgn_translated(self):
        d_conv = TrListas.dic_conv()
        li = [d_conv.get(c, c) for c in self.pgnBase]
        return "".join(li)

    def pgn_figurines(self):
        return self.pgnBase

    def pgn_html_base(self, with_figurines):
        is_white = self.is_white()
        if with_figurines:
            li = []
            for c in self.pgnBase:
                if c in "NBRQK":
                    c = dicHTMLFigs[c if is_white else c.lower()]
                li.append(c)
            resp = "".join(li)
        else:
            resp = self.pgn_translated()
        return resp

    def pgn_html(self, with_figurines):
        return self.pgn_html_base(with_figurines) + self.resto()

    def etiquetaSP(self):
        p = self.position_before
        return "%d.%s%s" % (p.num_moves, "" if p.is_white else "...", self.pgn_translated())

    def numMove(self):
        return self.position_before.num_moves

    def sounds_list(self):
        pgn = self.pgnBase
        li_medio = []
        li_final = []
        if pgn[0] == "O":
            if pgn[-1] in "#+":
                li_final = [pgn[-1],]
                pgn = pgn[:-1]
            li_inicial = [pgn]

        else:
            if "=" in pgn:
                ult = pgn[-1]
                if ult.lower() in "qrnb":
                    li_final = ["=", pgn[-1]]
                    pgn = pgn[:-2]
                else:
                    li_final = ["=", pgn[-2], pgn[-1]]
                    pgn = pgn[:-3]
            elif pgn.endswith("e.p."):
                pgn = pgn[:-4]
            li_medio = [pgn[-2], pgn[-1]]
            pgn = pgn[:-2]
            li_inicial = list(pgn)

        li = li_inicial
        li.extend(li_medio)
        li.extend(li_final)
        return li

    def pgnEN(self):
        resto = self.resto()
        if resto:
            if not (resto[0] in "?!"):
                resto = " " + resto
            return self.pgnBase + resto
        else:
            return self.pgnBase

    def resto(self, with_variations=True, with_nag_symbols=False):
        resp = ""
        if self.li_nags:
            self.li_nags.sort()
            if with_nag_symbols:
                resp += " ".join([html_nag_symbol(nag) for nag in self.li_nags])
            else:
                resp += " ".join([html_nag_txt(nag) for nag in self.li_nags])

        comment = self.comment
        if self.li_themes:
            comment += "[%theme " + ",".join(self.li_themes) + "]"
        if comment:
            resp += " "
            for txt in comment.strip().split("\n"):
                if txt:
                    resp += "{%s}" % txt.strip()
        if self.time_ms:
            s = self.time_ms / 1000
            if int(s * 100) > 0:
                h = int(s // 3600)
                s -= h * 3600
                m = int(s // 60)
                s -= m * 60
                resp += "{[%%emt %02d:%02d:%02.2f]}" % (h, m, s)
        if self.clock_ms:
            s = self.clock_ms / 1000
            if int(s * 100) > 0:
                h = int(s // 3600)
                s -= h * 3600
                m = int(s // 60)
                s -= m * 60
                resp += "{[%%clk %02d:%02d:%02.2f]}" % (h, m, s)
        if with_variations and len(self.variations):
            resp += " " + self.variations.get_pgn()

        resp = resp.strip()
        return " " + resp if resp else ""

    def analisis2variantes(self, alm_variations, delete_previous):
        if not self.analysis:
            return False
        mrm, pos = self.analysis
        if len(mrm.li_rm) == 0:
            return False

        return self.variations.analisis2variantes(mrm, pos, alm_variations, delete_previous)

    def remove_all_variations(self):
        self.variations.remove_all()

    def has_alternatives(self):
        return len(self.position_before.get_exmoves()) > 1

    def borraCV(self):
        self.variations.clear()
        self.comment = ""
        self.li_nags = []

    def calc_elo(self):
        if self.analysis:
            mrm, pos = self.analysis
            rm_best = mrm.li_rm[0]
            rm_player = mrm.li_rm[pos]
            self.elo, self.questionable_move, self.bad_move, self.verybad_move = Code.analysis_eval.elo_bad_vbad(
                rm_best, rm_player
            )

        else:
            self.elo = 0
            self.questionable_move = False
            self.bad_move = False
            self.verybad_move = False

    def factor_elo(self):
        elo_factor = 1
        if self.analysis:
            if self.bad_move:
                elo_factor = Code.configuration.x_eval_elo_mistake_factor
            elif self.verybad_move:
                elo_factor = Code.configuration.x_eval_elo_blunder_factor
            elif self.questionable_move:
                elo_factor = Code.configuration.x_eval_elo_inaccuracy_factor
        return elo_factor

    def distancia(self):
        return Position.distancia(self.from_sq, self.to_sq)

    def save(self):
        dic = {"move": self.movimiento(), "in_the_opening": self.in_the_opening}
        if len(self.variations):
            dic["variations"] = self.variations.save()
        if self.comment:
            dic["comment"] = self.comment
        if self.time_ms:
            dic["time_ms"] = self.time_ms
        if self.clock_ms:
            dic["clock_ms"] = self.clock_ms
        if self.li_nags:
            dic["li_nags"] = self.li_nags
        if self.li_themes:
            dic["li_themes"] = self.li_themes
        if self.analysis:
            mrm, pos = self.analysis
            save_mrm = mrm.save()
            dic["analysis"] = [save_mrm, pos]
        return Util.var2zip(dic)

    def restore(self, block):
        dic = Util.zip2var(block)

        move = dic["move"]
        self.from_sq, self.to_sq, self.promotion = move[:2], move[2:4], move[4:]

        cp = self.position_before.copia()
        cp.play(self.from_sq, self.to_sq, self.promotion)
        self.position = cp

        self.in_the_opening = dic["in_the_opening"]

        if "variations" in dic:
            self.variations.restore(dic["variations"])
        if "comment" in dic:
            self.comment = dic["comment"]
        if "time_ms" in dic:
            self.time_ms = dic["time_ms"]
        if "clock_ms" in dic:
            self.clock_ms = dic["clock_ms"]
        if "li_nags" in dic:
            self.li_nags = dic["li_nags"]
        if "li_themes" in dic:
            self.li_themes = dic["li_themes"]
        if "analysis" in dic:
            save_mrm, pos = dic["analysis"]
            mrm = EngineResponse.MultiEngineResponse("", True)
            mrm.restore(save_mrm)
            self.analysis = mrm, pos
        else:
            self.analysis = None

    def clone(self, other_game):
        m = Move(other_game)
        m.position_before = self.position_before.copia()
        m.position = self.position.copia()
        m.restore(self.save())
        return m

    def add_variation(self, game):
        return self.variations.add_variation(game)

    def test_a1h8(self, a1h8):
        if a1h8 == self.movimiento():
            return True, False
        if self.position.is_mate():
            position = self.position_before.copia()
            position.play_pv(a1h8)
            if position.is_mate():
                return True, False
        for variation in self.variations.li_variations:
            move = variation.move(0)
            if move and move.movimiento() == a1h8:
                return False, True
        return False, False

    def list_all_moves(self):
        # Analysis including variations
        pos_current_move = 0
        for pos_move, move in enumerate(self.game.li_moves):
            if move == self:
                pos_current_move = pos_move
                break
        li = [(self, self.game, pos_current_move)]
        for game in self.variations.list_games():
            for move in game.li_moves:
                li.extend(move.list_all_moves())
        return li

    def refresh_nags(self):
        if not self.analysis:
            return

        mrm, pos = self.analysis
        rm = mrm.li_rm[pos]
        nag, color = mrm.set_nag_color(rm)
        self.add_nag(nag)
        for game in self.variations.list_games():
            for move in game.li_moves:
                move.refresh_nags()

    def convert_variation_mainline(self, num_variation):
        self.game.convert_variation_mainline(self, num_variation)


def get_game_move(game, position_before, from_sq, to_sq, promotion):
    position = position_before.copia()

    ok, mens_error = position.play(from_sq, to_sq, promotion)
    if ok:
        move = Move(game, position_before, position, from_sq, to_sq, promotion)
        return True, None, move
    else:
        return False, mens_error, None


class Variations:
    def __init__(self, move_base):
        self.move_base = move_base
        self.li_variations = []

    def add_pgn_variation(self, pgn):
        pgn_var = '[FEN "%s"]\n%s' % (self.move_base.position_before.fen(), pgn)
        ok, game = Code.Base.Game.pgn_game(pgn_var)
        if ok:
            self.li_variations.append(game)

    def save(self):
        li = [variation.save() for variation in self.li_variations]
        return li

    def restore(self, li):
        self.li_variations = []
        for sv in li:
            game = Code.Base.Game.Game()
            game.restore(sv)
            self.li_variations.append(game)

    def __len__(self):
        return len(self.li_variations)

    def __copy__(self, other_variations):
        self.li_variations = other_variations.li_variations

    def get(self, num_variation):
        return self.li_variations[num_variation] if len(self.li_variations) > num_variation else None

    def get_pgn(self):
        if self.li_variations:
            return " ".join(["(%s)" % v.pgn_base_raw() for v in self.li_variations])
        return ""

    def clear(self):
        self.li_variations = []

    def list_games(self):
        return self.li_variations

    def list_movimientos(self):
        return [variation.move(0).movimiento() for variation in self.li_variations]

    def change(self, num_variation, game):
        if num_variation == -1:
            self.li_variations.append(game.copia())
        else:
            self.li_variations[num_variation] = game.copia()

    def remove(self, num):
        del self.li_variations[num]

    def remove_all(self):
        self.li_variations = []

    def up_variation(self, num):
        if num:
            self.li_variations[num], self.li_variations[num - 1] = self.li_variations[num - 1], self.li_variations[num]

    def down_variation(self, num):
        if num < len(self.li_variations) - 1:
            self.li_variations[num], self.li_variations[num + 1] = self.li_variations[num + 1], self.li_variations[num]

    def analisis2variantes(self, mrm, pos_move, alm_variations, delete_previous):
        if delete_previous:
            self.clear()

        if alm_variations.info_variation:
            name = mrm.name
            if mrm.max_time:
                t = "%0.2f" % (float(mrm.max_time) / 1000.0,)
                t = t.rstrip("0")
                if t[-1] == ".":
                    t = t[:-1]
                eti_t = "%s %s" % (_("Second(s)"), t)
            elif mrm.max_depth:
                eti_t = "%s %d" % (_("Depth"), mrm.max_depth)
            else:
                eti_t = ""
            eti_t = " " + name + " " + eti_t
        else:
            eti_t = ""

        tmp_game = Code.Base.Game.Game()
        what_variations = alm_variations.what_variations
        include_played = alm_variations.include_played
        highest_score = mrm.li_rm[0].centipawns_abs()
        move_score = mrm.li_rm[pos_move].centipawns_abs()

        si_un_move, si_pdt = alm_variations.one_move_variation, alm_variations.si_pdt

        position_before = self.move_base.position_before
        limit_score = alm_variations.limit_include_variations

        added_variations = False

        for pos, rm in enumerate(mrm.li_rm):
            if pos == pos_move:
                if not include_played:
                    continue
            elif limit_score and (highest_score - rm.centipawns_abs()) > limit_score:
                continue
            elif what_variations == HIGHEST_VARIATIONS:
                if rm.centipawns_abs() < highest_score:
                    continue
            elif what_variations == BETTER_VARIATIONS:
                if rm.centipawns_abs() < move_score:
                    continue
            tmp_game.set_position(position_before)
            tmp_game.read_pv(rm.pv)
            move = tmp_game.move(0)
            if move:
                puntuacion = rm.abbrev_text_pdt() if si_pdt else rm.abbrev_text()
                move.set_comment("%s%s" % (puntuacion, eti_t))
                gm = tmp_game.copia(0 if si_un_move else None)
                self.li_variations.append(gm)
                added_variations = True

        return added_variations

    def add_variation(self, game):
        pv_add = game.pv()
        pos_add = None
        for pos, variation in enumerate(self.li_variations):
            pv = variation.pv()
            if (pv_add == pv) or (pv.startswith(pv_add)):
                return pos
            if pv_add.startswith(pv):
                pos_add = pos
                break

        gm = game.copia()
        if pos_add is None:
            self.li_variations.append(gm)
            return len(self.li_variations)-1
        else:
            self.li_variations[pos_add] = gm
            return pos_add
