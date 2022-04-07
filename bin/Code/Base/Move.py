import Code
import Code.Base.Game  # To prevent recursivity in Variations -> import direct
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import NAG_4, NAG_6, NAG_2, html_nag_txt
from Code.Engines import EngineResponse
from Code.Themes.Lichess import cook
from Code.Translations import TrListas


def crea_dic_html():
    base = '<span style="font-family:Chess Alpha 2"><big>%s</big></span>'
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

        self.is_book = False

        self.elo = None
        self.questionable_move = None
        self.bad_move = None
        self.verybad_move = None

    def set_time_ms(self, ms):
        self.time_ms = ms

    def only_has_move(self) -> bool:
        return not (
            self.variations or self.comment or len(self.li_nags) > 0 or self.analysis or len(self.li_themes) > 0
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

    @property
    def liMovs(self):
        liMovs = [("b", self.to_sq), ("m", self.from_sq, self.to_sq)]
        if self.position.li_extras:
            liMovs.extend(self.position.li_extras)
        return liMovs

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
        pgnBase = self.position_before.pgn(self.from_sq, self.to_sq, self.promotion)
        assert pgnBase is not None
        return pgnBase

    def add_nag(self, nag):
        if nag and not (nag in self.li_nags):
            if nag <= NAG_6:
                li = []
                for n in self.li_nags:
                    if n > NAG_6 and not (n in li):
                        li.append(n)
                li.append(nag)
                self.li_nags = li
            else:
                self.li_nags.append(nag)

    def del_nags(self):
        self.li_nags = []

    def del_variations(self):
        self.variations.zap()

    def del_comment(self):
        self.comment = ""

    def add_comment(self, comment):
        self.comment = comment

    def del_analysis(self):
        self.analysis = None

    def is_white(self):
        return self.position_before.is_white

    def fenBase(self):
        return self.position.fenBase()

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
        d_conv = TrListas.dConv()
        li = [d_conv.get(c, c) for c in self.pgnBase]
        return "".join(li)

    def pgnFigurinesSP(self):
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
        return "%d.%s %s" % (p.num_moves, "" if p.is_white else "...", self.pgn_translated())

    def numMove(self):
        return self.position_before.num_moves

    def listaSonidos(self):
        pgn = self.pgnBase
        liMedio = []
        liFinal = []
        if pgn[0] == "O":
            liInicial = [pgn]
        else:
            if "=" in pgn:
                ult = pgn[-1]
                if ult.lower() in "qrnb":
                    liFinal = ["=", pgn[-1]]
                    pgn = pgn[:-2]
                else:
                    liFinal = ["=", pgn[-2], pgn[-1]]
                    pgn = pgn[:-3]
            elif pgn.endswith("e.p."):
                pgn = pgn[:-4]
            liMedio = [pgn[-2], pgn[-1]]
            pgn = pgn[:-2]
            liInicial = list(pgn)
            # if (not liInicial) or (not liInicial[0].isupper()):
            #     liInicial.insert(0, "P")

        li = liInicial
        li.extend(liMedio)
        li.extend(liFinal)
        return li

    def pgnEN(self):
        return self.pgnBase + self.resto()

    def resto(self, with_variations=True):
        resp = ""
        if self.li_nags:
            resp += " ".join([html_nag_txt(nag) for nag in self.li_nags])

        comment = self.comment
        if self.li_themes:
            comment += "[%theme " + ",".join(self.li_themes) + "]"
        if comment:
            resp += " "
            for txt in comment.strip().split("\n"):
                if txt:
                    resp += "{%s}" % txt.strip()
        if with_variations and len(self.variations):
            resp += " " + self.variations.get_pgn()

        return (" %s" % resp.strip()) if resp else ""

    def analisis2variantes(self, almVariations, delete_previous):
        if not self.analysis:
            return
        mrm, pos = self.analysis
        if len(mrm.li_rm) == 0:
            return

        self.variations.analisis2variantes(mrm, almVariations, delete_previous)

    def borraCV(self):
        self.variations.clear()
        self.comment = ""
        self.li_nags = []

    def calc_elo(self):
        if self.analysis:
            mrm, pos = self.analysis
            rm_j = mrm.li_rm[0]
            rm_c = mrm.li_rm[pos]
            self.elo, self.questionable_move, self.bad_move, self.verybad_move = \
                Code.analysis_eval.elo_bad_vbad(rm_j, rm_c)

        else:
            self.elo = 0
            self.questionable_move = False
            self.bad_move = False
            self.verybad_move = False

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
        cp.mover(self.from_sq, self.to_sq, self.promotion)
        self.position = cp

        self.in_the_opening = dic["in_the_opening"]

        if "variations" in dic:
            self.variations.restore(dic["variations"])
        if "comment" in dic:
            self.comment = dic["comment"]
        if "time_ms" in dic:
            self.time_ms = dic["time_ms"]
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
        m.restore(self.save())
        return m

    def add_variation(self, game):
        self.variations.add_variation(game)

    def test_a1h8(self, a1h8):
        if a1h8 == self.movimiento():
            return True, False
        for variation in self.variations.li_variations:
            if variation.move(0) == a1h8:
                return False, True
        if self.position.is_mate():
            position = self.position_before.copia()
            position.moverPV(a1h8)
            if position.is_mate():
                return True, False
        return False, False

    def assign_themes_lichess(self):
        if self.analysis:
            for nag in self.li_nags:
                if nag in (NAG_2, NAG_4, NAG_6):
                    mrm, pos = self.analysis
                    rm: EngineResponse.EngineResponse = mrm.li_rm[pos]
                    li_pv = rm.getPV().split(" ")
                    if len(li_pv) < 3:
                        return
                    pv = " ".join(li_pv[1:])
                    li_themes = cook.get_tags(self.position.fen(), pv, rm.puntos)
                    if li_themes:
                        for theme in li_themes:
                            self.add_theme(theme)
                    return


def get_game_move(game, position_before, from_sq, to_sq, promotion):
    position = position_before.copia()

    ok, mens_error = position.mover(from_sq, to_sq, promotion)
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
        ok, p_var = Code.Base.Game.pgn_game(pgn_var)
        if ok:
            self.li_variations.append(p_var)

    def save(self):
        li = [variation.save() for variation in self.li_variations]
        return li

    def restore(self, li):
        self.li_variations = []
        for sv in li:
            v = Code.Base.Game.Game()
            v.restore(sv)
            self.li_variations.append(v)

    def __len__(self):
        return len(self.li_variations)

    def __copy__(self, other_variations):
        self.li_variations = other_variations.li_variations

    def get(self, num_variation):
        return self.li_variations[num_variation] if len(self.li_variations) > num_variation else None

    def get_pgn(self):
        if self.li_variations:
            return " ".join(["(%s)" % v.pgnBaseRAW() for v in self.li_variations])
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

    def analisis2variantes(self, mrm, almVariations, delete_previous):
        if delete_previous:
            self.clear()

        if almVariations.info_variation:
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
        if almVariations.best_variation:
            pv_base = self.move_base
            for rm in mrm.li_rm:
                if rm.movimiento() != pv_base:
                    self.analisis2variantesUno(
                        tmp_game, rm, eti_t, almVariations.one_move_variation, almVariations.si_pdt
                    )
                    break
        else:
            for rm in mrm.li_rm:
                self.analisis2variantesUno(tmp_game, rm, eti_t, almVariations.one_move_variation, almVariations.si_pdt)

    def analisis2variantesUno(self, tmp_game, rm, eti_t, si_un_move, si_pdt):
        tmp_game.set_position(self.move_base.position_before)
        tmp_game.read_pv(rm.pv)
        move = tmp_game.move(0)
        puntuacion = rm.abrTextoPDT() if si_pdt else rm.abrTexto()
        move.comment = "%s%s" % (puntuacion, eti_t)
        gm = tmp_game.copia(0 if si_un_move else None)
        self.li_variations.append(gm)

    def add_variation(self, game):
        pv_add = game.pv()
        pos_add = None
        for pos, variation in enumerate(self.li_variations):
            pv = variation.pv()
            if (pv_add == pv) or (pv.startswith(pv_add)):
                return
            if pv_add.startswith(pv):
                pos_add = pos
                break

        gm = game.copia()
        if pos_add is None:
            self.li_variations.append(gm)
        else:
            self.li_variations[pos_add] = gm

    def zap(self):
        self.li_variations = []
