import FasterCode

import Code
from Code import Util
from Code.Base import Move, Position
from Code.Base.Constantes import (
    RESULT_DRAW,
    RESULT_UNKNOWN,
    RESULT_WIN_BLACK,
    RESULT_WIN_WHITE,
    OPENING,
    FEN_INITIAL,
    TERMINATION_MATE,
    TERMINATION_ADJUDICATION,
    TERMINATION_DRAW_AGREEMENT,
    TERMINATION_DRAW_50,
    TERMINATION_DRAW_MATERIAL,
    TERMINATION_DRAW_REPETITION,
    TERMINATION_DRAW_STALEMATE,
    TERMINATION_RESIGN,
    TERMINATION_UNKNOWN,
    TERMINATION_WIN_ON_TIME,
    TERMINATION_ENGINE_MALFUNCTION,
    STANDARD_TAGS,
    NONE,
    ALL,
    ONLY_BLACK,
    ONLY_WHITE,
    MIDDLEGAME,
    ENDGAME,
    ALLGAME,
    WHITE,
    BLACK,
    BEEP_DRAW,
    BEEP_DRAW_50,
    BEEP_DRAW_MATERIAL,
    BEEP_DRAW_REPETITION,
    BEEP_WIN_OPPONENT,
    BEEP_WIN_OPPONENT_TIME,
    BEEP_WIN_PLAYER,
    BEEP_WIN_PLAYER_TIME,
)
from Code.Nags.Nags import NAG_1, NAG_2, NAG_3, NAG_4, NAG_5, NAG_6
from Code.Openings import OpeningsStd, Opening


class Game:
    li_moves = None
    opening = None
    rotuloTablasRepeticion = None
    pending_opening = True
    termination = TERMINATION_UNKNOWN
    result = RESULT_UNKNOWN

    def __init__(self, first_position=None, fen=None, li_tags=None):
        self.first_comment = ""
        self.li_tags = li_tags if li_tags else []
        if fen:
            self.set_fen(fen)
        else:
            self.set_position(first_position)

    def reset(self):
        self.set_position(self.first_position)

    def set_fen(self, fen):
        if not fen or fen == FEN_INITIAL:
            return self.set_position(None)

        cp = Position.Position()
        cp.read_fen(fen)
        self.set_position(cp)

    def set_position(self, first_position=None):
        self.li_moves = []
        self.opening = None
        self.termination = TERMINATION_UNKNOWN
        self.result = RESULT_UNKNOWN
        self.del_tag("Termination")
        self.del_tag("Result")
        self.rotuloTablasRepeticion = None
        self.pending_opening = False

        if first_position:
            self.first_position = first_position.copia()
            fen_inicial = self.first_position.fen()
            es_inicial = self.pending_opening = fen_inicial == FEN_INITIAL
            if not es_inicial:
                self.set_tag("FEN", fen_inicial)
        else:
            self.first_position = Position.Position()
            self.first_position.set_pos_initial()
            self.pending_opening = True

    def is_mate(self):
        return self.termination == TERMINATION_MATE

    def set_termination_time(self):
        self.termination = TERMINATION_WIN_ON_TIME
        # Pierde el que le toca jugar, que se indica en position resultado del ultimo movimiento
        self.result = RESULT_WIN_BLACK if self.last_position.is_white else RESULT_WIN_WHITE
        self.set_extend_tags()

    def set_termination(self, termination, result):
        self.termination = termination
        self.result = result
        self.set_extend_tags()

    def set_unknown(self):
        self.set_termination(TERMINATION_UNKNOWN, RESULT_UNKNOWN)
        if self.get_tag("Result"):
            self.set_tag("Result", RESULT_UNKNOWN)

    def add_tag_timestart(self):
        t = Util.today()
        self.set_tag("TimeStart", str(t)[:19].replace("-", "."))

    def tag_timeend(self):
        t = Util.today()
        self.set_tag("TimeEnd", str(t)[:19].replace("-", "."))

    @property
    def last_position(self):
        if self.li_moves:
            position = self.li_moves[-1].position
        else:
            position = self.first_position
        return position.copia()

    @property
    def starts_with_black(self):
        return not self.first_position.is_white

    def save(self, with_litags=True):
        dic = {
            "first_position": self.first_position.fen(),
            "first_comment": self.first_comment,
            "li_moves": [move.save() for move in self.li_moves],
            "result": self.result,
            "termination": self.termination,
        }
        if with_litags and self.li_tags:
            dic["li_tags"] = self.li_tags

        return Util.var2zip(dic)

    def restore(self, btxt_save):
        dic = Util.zip2var(btxt_save)
        if not dic:
            return
        self.first_position = Position.Position()
        self.first_position.read_fen(dic["first_position"])
        self.first_comment = dic["first_comment"]
        self.result = dic["result"]
        self.termination = dic["termination"]
        self.li_moves = []
        cp = self.first_position.copia()
        for save_jg in dic["li_moves"]:
            move = Move.Move(self, position_before=cp)
            move.restore(save_jg)
            cp = move.position.copia()
            self.li_moves.append(move)
        self.assign_opening()
        self.si3repetidas()
        self.li_tags = dic.get("li_tags", [])

    def __eq__(self, other):
        return self.save() == other.save()

    def eq_body(self, other):
        return self.save(False) == other.save(False)

    def iswhite(self):
        return self.first_position.is_white

    def set_tags(self, litags):
        self.li_tags = litags[:]

    def get_tag(self, tag):
        tag = tag.upper()
        for k, v in self.li_tags:
            if k.upper() == tag:
                return v
        return ""

    def dicTags(self):
        return {k: v for k, v in self.li_tags}

    def order_tags(self):
        li_basic = ("EVENT", "SITE", "DATE", "ROUND", "WHITE", "BLACK", "RESULT", "ECO", "FEN", "WHITEELO", "BLACKELO")
        li_main = []
        li_resto = []
        dic = {k.upper(): (k, v) for k, v in self.li_tags}
        for k in li_basic:
            if k in dic:
                li_main.append(dic[k])
        for k in dic:
            if not (k in li_basic):
                li_resto.append(dic[k])
        self.li_tags = li_main
        self.li_tags.extend(li_resto)

    def set_tag(self, key, value):
        found = False
        for n, (xkey, xvalue) in enumerate(self.li_tags):
            if xkey == key:
                self.li_tags[n] = [key, value]
                found = True
                break
        if not found:
            self.li_tags.append([key, value])

    def del_tag(self, key):
        for n, (xkey, xvalue) in enumerate(self.li_tags):
            if xkey == key:
                del self.li_tags[n]
                return

    def set_extend_tags(self):
        if self.result:
            self.set_tag("Result", self.result)

        if self.termination:
            tm = self.get_tag("Termination")
            if not tm:
                txt = self.label_termination()
                if txt:
                    self.set_tag("Termination", txt)

        if self.siFenInicial():
            op = self.get_tag("OPENING")
            eco = self.get_tag("ECO")
            if not op or not eco:
                self.assign_opening()
                if self.opening:
                    if not op:
                        self.li_tags.append(["Opening", self.opening.tr_name])
                    if not eco:
                        self.li_tags.append(["ECO", self.opening.eco])
        else:
            self.set_tag("FEN", self.first_position.fen())

        if self.num_moves():
            self.set_tag("PlyCount", "%d" % self.num_moves())

    def sort_tags(self):
        st_hechos = set()
        li_nuevo = []
        for tag in STANDARD_TAGS:
            for k, v in self.li_tags:
                if k == tag:
                    st_hechos.add(tag)
                    li_nuevo.append((k, v))
                    break
        for k, v in self.li_tags:
            if k not in st_hechos:
                li_nuevo.append((k, v))
        self.li_tags = li_nuevo

    def readPGN(self, pgn):
        ok, game_tmp = pgn_game(pgn)
        self.restore(game_tmp.save())
        return self

    def pgn(self):
        li = ['[%s "%s"]\n' % (k, v) for k, v in self.li_tags]
        txt = "".join(li)
        txt += "\n%s" % self.pgn_base()
        return txt

    def pgn_tags(self):
        return "\n".join(['[%s "%s"]' % (k, v) for k, v in self.li_tags])

    def titulo(self, *litags, sep=" ∣ "):
        li = []
        for key in litags:
            tag = self.get_tag(key)
            tagi = tag.replace("?", "").replace(".", "")
            if tagi:
                li.append(tag)
        return sep.join(li)

    def window_title(self):
        white = ""
        black = ""
        event = ""
        site = ""
        date = ""
        result = ""
        for key, valor in self.li_tags:
            if key.upper() == "WHITE":
                white = valor
            elif key.upper() == "BLACK":
                black = valor
            elif key.upper() == "EVENT":
                event = valor
            elif key.upper() == "SITE":
                site = valor
            elif key.upper() == "DATE":
                date = valor.replace("?", "").replace(" ", "").strip(".")
            elif key.upper() == "RESULT":
                if valor in ("1-0", "0-1", "1/2-1/2"):
                    result = valor
        li = []
        if event:
            li.append(event)
        if site:
            li.append(site)
        if date:
            li.append(date)
        if result:
            li.append(result)
        titulo = "%s-%s" % (white, black)
        if li:
            titulo += " (%s)" % (" - ".join(li),)
        return titulo

    def primeraJugada(self):
        return self.first_position.num_moves

    def move(self, num):
        try:
            return self.li_moves[num]
        except:
            return self.li_moves[-1] if len(self) > 0 else None

    def verify(self):
        if self.pending_opening:
            self.assign_opening()
        if len(self.li_moves) == 0:
            return
        move = self.move(-1)
        if move.position.is_finished():
            if move.is_check:
                self.set_termination(
                    TERMINATION_MATE, RESULT_WIN_WHITE if move.position_before.is_white else RESULT_WIN_BLACK
                )
            else:
                self.set_termination(TERMINATION_DRAW_STALEMATE, RESULT_DRAW)

        elif self.si3repetidas():
            self.set_termination(TERMINATION_DRAW_REPETITION, RESULT_DRAW)

        elif self.last_position.mov_pawn_capt >= 100:
            self.set_termination(TERMINATION_DRAW_50, RESULT_DRAW)

        elif self.last_position.siFaltaMaterial():
            self.set_termination(TERMINATION_DRAW_MATERIAL, RESULT_DRAW)

    def add_move(self, move):
        self.li_moves.append(move)
        self.verify()

    def siFenInicial(self):
        return self.first_position.fen() == FEN_INITIAL

    def numJugadaPGN(self, njug):
        primera = int(self.first_position.num_moves)
        if self.starts_with_black:
            njug += 1
        return primera + njug / 2

    def num_moves(self):
        return len(self.li_moves)

    def __len__(self):
        return len(self.li_moves)

    def last_jg(self):
        return self.li_moves[-1] if self.li_moves else None

    def assign_other_game(self, otra):
        txt = otra.save()
        self.restore(txt)

    def si3repetidas(self):
        nJug = len(self.li_moves)
        if nJug > 5:
            fenBase = self.li_moves[nJug - 1].fenBase()
            liRep = [nJug - 1]
            for n in range(nJug - 1):
                if self.li_moves[n].fenBase() == fenBase:
                    liRep.append(n)
                    if len(liRep) == 3:
                        label = ""
                        for j in liRep:
                            label += "%d," % (j / 2 + 1,)
                        label = label.strip(",")
                        self.rotuloTablasRepeticion = label
                        return True
        return False

    def read_pv(self, pvBloque):
        return self.read_lipv(pvBloque.split(" "))

    def read_xpv(self, xpv):
        return self.read_pv(FasterCode.xpv_pv(xpv))

    def read_lipv(self, lipv):
        position = self.last_position
        pv = []
        for mov in lipv:
            if (
                    len(mov) >= 4
                    and mov[0] in "abcdefgh"
                    and mov[1] in "12345678"
                    and mov[2] in "abcdefgh"
                    and mov[3] in "12345678"
            ):
                pv.append(mov)
            else:
                break

        siB = self.is_white

        for mov in pv:
            from_sq = mov[:2]
            to_sq = mov[2:4]
            if len(mov) == 5:
                promotion = mov[4]
                if siB:
                    promotion = promotion.upper()
            else:
                promotion = None
            ok, mens, move = Move.get_game_move(self, position, from_sq, to_sq, promotion)
            if ok:
                self.li_moves.append(move)
                position = move.position
            siB = not siB
        return self

    def damePosicion(self, pos):
        nJugadas = len(self.li_moves)
        if nJugadas:
            return self.li_moves[pos].position
        else:
            return self.first_position

    def last_fen(self):
        return self.last_position.fen()

    def fensActual(self):
        resp = self.first_position.fen() + "\n"
        for move in self.li_moves:
            resp += move.position.fen() + "\n"

        return resp

    def is_white(self):
        return self.last_position.is_white

    def is_draw(self):
        return self.result == RESULT_DRAW

    def pgnBaseRAW(self, numJugada=None, translated=False):
        resp = ""
        if numJugada is None:
            if self.first_comment:
                resp = "{%s} " % self.first_comment
            numJugada = self.primeraJugada()
        if self.starts_with_black:
            resp += "%d... " % numJugada
            numJugada += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(self.li_moves):
            if n % 2 == salta:
                resp += " %d." % numJugada
                numJugada += 1
            if translated:
                resp += move.pgn_translated() + " "
            else:
                resp += move.pgnEN() + " "

        resp = resp.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
        while "  " in resp:
            resp = resp.replace("  ", " ")

        return resp

    def pgn_base(self, numJugada=None, translated=False):
        resp = self.pgnBaseRAW(numJugada, translated=translated)
        li = []
        ln = len(resp)
        pos = 0
        while pos < ln:
            while resp[pos] == " ":
                pos += 1
            final = pos + 80
            txt = resp[pos:final]
            if txt[-1] == " ":
                txt = txt[:-1]
            elif final < ln:
                if resp[final] == " ":
                    final += 1
                else:
                    while final > pos and resp[final - 1] != " ":
                        final -= 1
                    if final > pos:
                        txt = resp[pos:final]
                    else:
                        final = pos + 80
            li.append(txt)
            pos = final
        if li:
            li[-1] = li[-1].strip()
            return "\n".join(li)
        else:
            return ""

    def set_first_comment(self, txt, siReplace=False):
        if siReplace or not self.first_comment:
            self.first_comment = txt
        else:
            self.first_comment = "%s\n%s" % (self.first_comment.strip(), txt)

    def pgn_jg(self, move):
        pgn = move.pgnFigurinesSP() if Code.configuration.x_pgn_withfigurines else move.pgn_translated()
        if self.termination == TERMINATION_MATE and move == self.last_jg():
            pgn += "#"
        return pgn

    def pgn_translated(self, numJugada=None, hastaJugada=9999):
        if self.first_comment:
            resp = "{%s} " % self.first_comment
        else:
            resp = ""
        if numJugada is None:
            numJugada = self.primeraJugada()
        if self.starts_with_black:
            resp += "%d..." % numJugada
            numJugada += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(self.li_moves):
            if n > hastaJugada:
                break
            if n % 2 == salta:
                resp += "%d." % numJugada
                numJugada += 1

            pgn = move.pgn_translated()
            if n == len(self) - 1:
                if self.termination == TERMINATION_MATE and not pgn.endswith("#"):
                    pgn += "#"

            resp += pgn + " "

        return resp.strip()

    def pgn_html(self, numJugada=None, hastaJugada=9999, with_figurines=True):
        liResp = []
        if self.first_comment:
            liResp.append("{%s}" % self.first_comment)
        if numJugada is None:
            numJugada = self.primeraJugada()
        if self.starts_with_black:
            liResp.append('<span style="color:navy">%d...</span>' % numJugada)
            numJugada += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(self.li_moves):
            if n > hastaJugada:
                break
            if n % 2 == salta:
                x = '<span style="color:navy">%d.</span>' % numJugada
                numJugada += 1
            else:
                x = ""
            liResp.append(x + (move.pgn_html(with_figurines)))
        return " ".join(liResp)

    def is_finished(self):
        if self.termination != TERMINATION_UNKNOWN or self.result != RESULT_UNKNOWN:
            self.test_tag_result()
            return True
        if self.li_moves:
            move = self.li_moves[-1]
            if move.position.is_finished():
                if move.is_check:
                    self.result = RESULT_WIN_WHITE if move.position_before.is_white else RESULT_WIN_BLACK
                    self.termination = TERMINATION_MATE
                else:
                    self.result = RESULT_DRAW
                    self.termination = TERMINATION_DRAW_STALEMATE
                self.test_tag_result()
                return True
        return False

    def test_tag_result(self):
        if not self.get_tag("RESULT"):
            self.set_tag("Result", self.result)

    def resultado(self):
        if self.result == RESULT_UNKNOWN:
            x = self.get_tag("RESULT")
            if x:
                self.result = x
        return self.result

    def siEstaTerminada(self):
        return self.resultado() != RESULT_UNKNOWN

    def pv(self):
        return " ".join([move.movimiento() for move in self.li_moves])

    def xpv(self):
        resp = FasterCode.pv_xpv(self.pv())
        if not self.first_position.is_initial():
            resp = "|%s|%s" % (self.first_position.fen(), resp)
        return resp

    def all_pv(self, pv_previo, with_variations):
        li_pvc = []
        if pv_previo:
            pv_previo += " "
        for move in self.li_moves:
            if with_variations != NONE and move.variations:
                is_w = move.is_white()
                if (
                        (with_variations == ALL)
                        or (is_w and with_variations == ONLY_WHITE)
                        or (not is_w and with_variations == ONLY_BLACK)
                ):
                    for variation in move.variations.li_variations:
                        li_pvc.extend(variation.all_pv(pv_previo.strip(), with_variations))
            pv_previo += move.movimiento() + " "
            li_pvc.append(pv_previo.strip())
        return li_pvc

    def all_comments(self, with_variations):
        dic = {}
        for move in self.li_moves:
            if with_variations != NONE and move.variations:
                is_w = move.is_white()
                if (
                        (with_variations == ALL)
                        or (is_w and with_variations == ONLY_WHITE)
                        or (not is_w and with_variations == ONLY_BLACK)
                ):
                    for variation in move.variations.li_variations:
                        dicv = variation.all_comments(with_variations)
                        if dicv:
                            dic.update(dicv)
            if move.comment or move.li_nags:
                fenm2 = move.position.fenm2()
                d = {}
                if move.comment:
                    d["C"] = move.comment
                if move.li_nags:
                    d["N"] = move.li_nags
                dic[fenm2] = d
        return dic

    def lipv(self):
        return [move.movimiento() for move in self.li_moves]

    def pv_hasta(self, njug):
        return " ".join([move.movimiento() for move in self.li_moves[: njug + 1]])

    def anulaUltimoMovimiento(self, is_white):
        del self.li_moves[-1]
        self.set_unknown()
        ndel = 1
        if self.li_moves and self.li_moves[-1].position.is_white != is_white:
            del self.li_moves[-1]
            ndel += 1
        return ndel

    def anulaSoloUltimoMovimiento(self):
        if self.li_moves:
            move = self.li_moves[-1]
            del self.li_moves[-1]
            self.set_unknown()
            return move
        return None

    def copia(self, hastaJugada=None):
        p = Game()
        p.assign_other_game(self)
        if hastaJugada is not None:
            if hastaJugada == -1:
                p.li_moves = []
            elif hastaJugada < (p.num_moves() - 1):
                p.li_moves = p.li_moves[: hastaJugada + 1]
            if len(p) != len(self):
                p.set_unknown()
        return p

    def copy_until_move(self, seek_move):
        for pos, move in enumerate(self.li_moves):
            if seek_move == move:
                return self.copia(pos - 1)
        return self.copia(-1)

    def copiaDesde(self, desdeJugada):
        if desdeJugada == 0:
            cp = self.first_position
        else:
            cp = self.li_moves[desdeJugada - 1].position
        p = Game(cp)
        p.li_moves = self.li_moves[desdeJugada:]
        return p

    def pgnBaseRAWcopy(self, numJugada, hastaJugada):
        resp = ""
        if numJugada is None:
            numJugada = self.primeraJugada()
        if self.starts_with_black:
            resp += "%d... " % numJugada
            numJugada += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(self.li_moves[: hastaJugada + 1]):
            if n % 2 == salta:
                resp += " %d." % numJugada
                numJugada += 1

            resp += move.pgnEN() + " "

        resp = resp.replace("\n", " ").replace("\r", " ").replace("  ", " ").strip()

        return resp

    def resign(self, is_white):
        self.set_termination(TERMINATION_RESIGN, RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE)
        self.set_extend_tags()

    def borraCV(self):
        self.first_comment = ""
        for move in self.li_moves:
            move.borraCV()

    def remove_analysis(self):
        for move in self.li_moves:
            move.analysis = None

    def calc_elo_color(self, is_white):
        nummoves = {OPENING: 0, MIDDLEGAME: 0, ENDGAME: 0}
        sumelos = {OPENING: 0, MIDDLEGAME: 0, ENDGAME: 0}
        factormoves = {OPENING: 0, MIDDLEGAME: 0, ENDGAME: 0}
        last = OPENING
        for move in self.li_moves:
            if move.analysis and move.has_alternatives():
                if move.is_white() != is_white:
                    continue
                if last == ENDGAME:
                    std = ENDGAME
                else:
                    if move.is_book:
                        std = OPENING
                    else:
                        std = MIDDLEGAME
                        material = move.position_before.valor_material()
                        if material < 15:
                            std = ENDGAME
                        else:
                            pzW, pzB = move.position_before.numPiezasWB()
                            if pzW < 3 and pzB < 3:
                                std = ENDGAME
                move.stateOME = std
                last = std
                move.calc_elo()
                elo_factor = move.factor_elo()
                # if move.bad_move:
                #     elo_factor = Code.configuration.eval_mistake_factor
                # elif move.verybad_move:
                #     elo_factor = Code.configuration.eval_blunder_factor
                # elif move.questionable_move:
                #     elo_factor = Code.configuration.eval_inaccuracy_factor
                nummoves[std] += 1
                sumelos[std] += move.elo * elo_factor
                factormoves[std] += elo_factor

                xelos = {}
                for std in (OPENING, MIDDLEGAME, ENDGAME):
                    sume = sumelos[std]
                    numf = factormoves[std]
                    if numf:
                        xelos[std] = int(sume * 1.0 / numf)
                    else:
                        xelos[std] = 0

                sume = 0
                numf = 0
                for std in (OPENING, MIDDLEGAME, ENDGAME):
                    sume += sumelos[std]
                    numf += factormoves[std]

                if numf:
                    move.elo_avg = int(sume * 1.0 / numf)
                else:
                    move.elo_avg = 0

        elos = {}
        for std in (OPENING, MIDDLEGAME, ENDGAME):
            sume = sumelos[std]
            numf = factormoves[std]
            if numf:
                elos[std] = int(sume * 1.0 / numf)
            else:
                elos[std] = 0

        sume = 0
        numf = 0
        for std in (OPENING, MIDDLEGAME, ENDGAME):
            sume += sumelos[std]
            numf += factormoves[std]

        if numf:
            elos[ALLGAME] = int(sume * 1.0 / numf)
        else:
            elos[ALLGAME] = 0

        return elos

    def calc_elos(self, configuration):
        for move in self.li_moves:
            move.is_book = False
        if self.siFenInicial():
            ap = Opening.OpeningPol(999)
            for move in self.li_moves:
                move.is_book = ap.check_human(move.position_before.fen(), move.from_sq, move.to_sq)
                if not move.is_book:
                    break

        elos = {}
        for is_white in (True, False):
            elos[is_white] = self.calc_elo_color(is_white)

        elos[None] = {}
        for std in (OPENING, MIDDLEGAME, ENDGAME, ALLGAME):
            elos[None][std] = int((elos[True][std] + elos[False][std]) / 2.0)

        return elos

    def calc_elosFORM(self, configuration):
        for move in self.li_moves:
            move.is_book = False
        if self.siFenInicial():
            ap = Opening.OpeningPol(999)
            for move in self.li_moves:
                move.is_book = ap.check_human(move.position_before.fen(), move.from_sq, move.to_sq)
                if not move.is_book:
                    break

        elos = {}
        for is_white in (True, False):
            elos[is_white] = self.calc_elo_color(is_white)

        elos[None] = {}
        for std in (OPENING, MIDDLEGAME, ENDGAME, ALLGAME):
            w, b = elos[True][std], elos[False][std]

            divisor = 1.0 if w == 0 or b == 0 else 2.0
            elos[None][std] = int((w + b) / divisor)

        return elos

    def assign_opening(self):
        OpeningsStd.ap.assign_opening(self)

    def rotuloOpening(self):
        return self.opening.tr_name if hasattr(self, "opening") and self.opening is not None else None

    def test_apertura(self):
        if not hasattr(self, "opening") or self.pending_opening:
            self.assign_opening()

    def only_has_moves(self) -> bool:
        if self.first_comment:
            return False
        for move in self.li_moves:
            if not move.only_has_move():
                return False
        return True

    def dic_labels(self):
        return {key: value for key, value in self.li_tags}

    def label_resultado_player(self, player_side):
        nom_w = self.get_tag("White")
        nom_b = self.get_tag("Black")

        nom_other = nom_b if player_side == WHITE else nom_w

        mensaje = ""
        beep = None
        player_lost = False
        if (self.result == RESULT_WIN_WHITE and player_side == WHITE) or (
                self.result == RESULT_WIN_BLACK and player_side == BLACK
        ):
            if nom_other:
                mensaje = _X(_("Congratulations you have won against %1."), nom_other)
            else:
                mensaje = _("Congratulations you have won.")
            if self.termination == TERMINATION_WIN_ON_TIME:
                beep = BEEP_WIN_PLAYER_TIME
            else:
                beep = BEEP_WIN_PLAYER

        elif (self.result == RESULT_WIN_WHITE and player_side == BLACK) or (
                self.result == RESULT_WIN_BLACK and player_side == WHITE
        ):
            player_lost = True
            if nom_other:
                mensaje = _X(_("Unfortunately you have lost against %1."), nom_other)
            else:
                mensaje = _("Unfortunately you have lost.")
            if self.termination == TERMINATION_WIN_ON_TIME:
                beep = BEEP_WIN_OPPONENT_TIME
            else:
                beep = BEEP_WIN_OPPONENT

        elif self.result == RESULT_DRAW:
            if nom_other:
                mensaje = _X(_("Draw against %1."), nom_other)
            else:
                mensaje = _("Draw")
            beep = BEEP_DRAW
            if self.termination == TERMINATION_DRAW_REPETITION:
                beep = BEEP_DRAW_REPETITION
            elif self.termination == TERMINATION_DRAW_50:
                beep = BEEP_DRAW_50
            elif self.termination == TERMINATION_DRAW_MATERIAL:
                beep = BEEP_DRAW_MATERIAL

        if self.termination != TERMINATION_UNKNOWN:
            if self.termination == TERMINATION_WIN_ON_TIME and player_lost:
                label = _("Lost on time")
            else:
                label = self.label_termination()

            mensaje += "\n\n%s: %s" % (_("Result"), label)

        return mensaje, beep, beep in (BEEP_WIN_PLAYER_TIME, BEEP_WIN_PLAYER)

    def label_termination(self):
        return {
            TERMINATION_MATE: _("Mate"),
            TERMINATION_DRAW_STALEMATE: _("Stalemate"),
            TERMINATION_DRAW_REPETITION: _("Draw by threefold repetition"),
            TERMINATION_DRAW_MATERIAL: _("Draw by insufficient material"),
            TERMINATION_DRAW_50: _("Draw by fifty-move rule"),
            TERMINATION_DRAW_AGREEMENT: _("Draw by agreement"),
            TERMINATION_RESIGN: _("Resignation"),
            TERMINATION_ADJUDICATION: _("Adjudication"),
            TERMINATION_WIN_ON_TIME: _("Won on time"),
            TERMINATION_UNKNOWN: _("Unknown"),
            TERMINATION_ENGINE_MALFUNCTION: _("Engine malfunction"),
        }.get(self.termination, "")

    def shrink(self, until_move: int):
        self.li_moves = self.li_moves[: until_move + 1]

    def copy_raw(self, xto):
        g = Game(self.first_position)
        if xto not in (None, -1):
            pv = self.pv_hasta(xto)
            if pv:
                g.read_pv(pv)
        return g

    def skip_first(self):
        if len(self.li_moves) == 0:
            return
        move0 = self.li_moves[0]
        self.li_moves = self.li_moves[1:]
        self.first_position = move0.position
        fen_inicial = self.first_position.fen()
        self.set_tag("FEN", fen_inicial)

    def average_mstime_user(self, num):
        # solo se pregunta cuando le toca jugar al usuario
        is_white = self.last_position.is_white
        li = [move.time_ms for move in self.li_moves if move.is_white() == is_white and move.time_ms > 0]
        if len(li) > 0:
            li = li[-num:]
            return sum(li) / len(li)
        else:
            return 0


def pv_san(fen, pv):
    p = Game(fen=fen)
    p.read_pv(pv)
    move = p.move(0)
    return move.pgn_translated()


def pv_pgn(fen, pv):
    p = Game(fen=fen)
    p.read_pv(pv)
    return p.pgn_translated()


def pv_game(fen, pv):
    g = Game(fen=fen)
    g.read_pv(pv)
    g.assign_opening()
    return g


def lipv_lipgn(lipv):
    FasterCode.set_init_fen()
    li_pgn = []
    for pv in lipv:
        info = FasterCode.move_expv(pv[:2], pv[2:4], pv[4:])
        li_pgn.append(info._san.decode())
    return li_pgn


def pv_pgn_raw(fen, pv):
    p = Game(fen=fen)
    p.read_pv(pv)
    return p.pgnBaseRAW()


def pgn_game(pgn):
    game = Game()
    last_posicion = game.first_position
    jg_activa = None
    if type(pgn) == bytes:
        try:
            pgn, codec = Util.bytes_str_codec(pgn)
        except:
            pgn = pgn.decode("utf-8", errors="ignore")
    li = FasterCode.xparse_pgn(pgn)
    if li is None:
        return False, game

    si_fen = False
    dic_nags = {
        "!": NAG_1,
        "?": NAG_2,
        "!!": NAG_3,
        "‼": NAG_3,
        "??": NAG_4,
        "⁇": NAG_4,
        "!?": NAG_5,
        "⁉": NAG_5,
        "?!": NAG_6,
        "⁈": NAG_6,
    }
    FasterCode.set_init_fen()
    for elem in li:
        key = elem[0] if elem else ""
        if key == "[":
            kv = elem[1:].strip()
            pos = kv.find(" ")
            if pos > 0:
                lb = kv[:pos]
                vl = kv[pos + 1:].strip()
                lbup = lb.upper()
                if lbup == "FEN":
                    FasterCode.set_fen(vl)
                    if vl != FEN_INITIAL:
                        game.set_fen(vl)
                        last_posicion = game.first_position
                        game.set_tag(lb, vl)
                        si_fen = True
                elif lbup == "RESULT":
                    game.result = vl
                    game.set_tag("Result", vl)
                else:
                    game.set_tag(lb, vl)

        elif key == "M":
            a1h8 = elem[1:]
            posicion_base = last_posicion
            FasterCode.make_move(a1h8)
            last_posicion = Position.Position()
            last_posicion.read_fen(FasterCode.get_fen())
            jg_activa = Move.Move(game, posicion_base, last_posicion, a1h8[:2], a1h8[2:4], a1h8[4:])
            game.li_moves.append(jg_activa)

        elif key in "!?":
            if jg_activa:
                jg_activa.add_nag(dic_nags.get(elem, None))

        elif key == "$":
            if jg_activa:
                nag = elem[1:]
                if nag.isdigit():
                    nag = int(nag)
                    if 0 < nag < 256:
                        jg_activa.add_nag(nag)

        elif key in "{;":
            comment = elem[1:-1].strip()
            if comment:
                if jg_activa:
                    if jg_activa.comment:
                        jg_activa.comment += "\n"
                    jg_activa.comment += comment.replace("}", "]")
                else:
                    game.set_first_comment(comment)

        elif key == "(":
            variation = elem[1:-1].strip()
            if variation:
                if jg_activa:
                    fen = FasterCode.get_fen()
                    jg_activa.variations.add_pgn_variation(variation)
                    FasterCode.set_fen(fen)

        elif key == "R":
            if jg_activa:
                r1 = elem[1]
                if r1 == "1":
                    game.result = RESULT_WIN_WHITE
                elif r1 == "2":
                    game.result = RESULT_DRAW
                elif r1 == "3":
                    game.result = RESULT_WIN_BLACK
                elif r1 == "0":
                    game.result = RESULT_UNKNOWN
    if si_fen:
        game.pending_opening = False
    if jg_activa:
        game.verify()
    return True, game


def fen_game(fen, variation):
    pgn = '[FEN "%s"]\n\n%s' % (fen, variation)
    ok, p = pgn_game(pgn)
    return p


def read_games(pgnfile):
    with Util.OpenCodec(pgnfile) as f:
        siBCab = True
        lineas = []
        nbytes = 0
        last_line = ""
        for linea in f:
            nbytes += len(linea)
            if siBCab:
                if linea and linea[0] != "[":
                    siBCab = False
            else:
                if last_line == "" and linea.startswith("["):
                    ln = linea.strip()
                    if ln.endswith("]"):
                        ln = ln[:-1]
                        if ln.endswith('"') and ln.count('"') > 1:
                            ok, p = pgn_game("".join(lineas))
                            yield nbytes, p
                            lineas = []
                            siBCab = True
            lineas.append(linea)
            last_line = linea.strip()
        if lineas:
            ok, p = pgn_game("".join(lineas))
            yield nbytes, p


def calc_formula_elo(move):  # , limit=200.0):
    with open(Code.path_resource("IntFiles", "Formulas", "eloperformance.formula")) as f:
        formula = f.read().strip()

    # dataLG = []
    # titLG = []

    # def LG(key, value):
    #     titLG.append(key)
    #     dataLG.append(str(value))

    cp = move.position_before
    mrm, pos = move.analysis

    # LG("move", mrm.li_rm[pos].movimiento())

    pts = mrm.li_rm[pos].puntosABS_5()
    pts0 = mrm.li_rm[0].puntosABS_5()
    lostp_abs = pts0 - pts

    # LG("pts best", pts0)
    # LG("pts current", pts)
    # LG("xlostp", lostp_abs)

    piew = pieb = 0
    mat = 0.0
    matw = matb = 0.0
    dmat = {"k": 3.0, "q": 9.9, "r": 5.5, "b": 3.5, "n": 3.1, "p": 1.0}
    for k, v in cp.squares.items():
        if v:
            m = dmat[v.lower()]
            mat += m
            if v.isupper():
                piew += 1
                matw += m
            else:
                pieb += 1
                matb += m
    base = mrm.li_rm[0].centipawns_abs()
    is_white = cp.is_white

    gmo34 = gmo68 = gmo100 = 0
    for rm in mrm.li_rm:
        dif = abs(rm.centipawns_abs() - base)
        if dif < 34:
            gmo34 += 1
        elif dif < 68:
            gmo68 += 1
        elif dif < 101:
            gmo100 += 1
    gmo = float(gmo34) + float(gmo68) ** 0.8 + float(gmo100) ** 0.5
    plm = (cp.num_moves - 1) * 2
    if not is_white:
        plm += 1

    # xshow: Factor de conversion a puntos para mostrar
    xshow = +1 if is_white else -1
    xshow = 0.01 * xshow

    li = (
        ("xpiec", piew if is_white else pieb),
        ("xpie", piew + pieb),
        ("xeval", base if is_white else -base),
        ("xstm", +1 if is_white else -1),
        ("xplm", plm),
        ("xshow", xshow),
        ("xlost", lostp_abs),
    )
    for k, v in li:
        if k in formula:
            formula = formula.replace(k, "%d.0" % v)
    li = (("xgmo", gmo), ("xmat", mat), ("xpow", matw if is_white else matb))
    for k, v in li:

        # LG(k, v)

        if k in formula:
            formula = formula.replace(k, "%f" % v)
    # if "xcompl" in formula:
    #     formula = formula.replace("xcompl", "%f" % calc_formula_elo("complexity", cp, mrm))
    try:
        x = float(eval(formula))
        # if x < 0.0:
        #     x = -x
        # if x > limit:
        #     x = limit

        # LG("elo", int(min(3500, max(0, x))))
        # LG("other elo", int(move.elo))

        # with open("FormulaELO.csv", "a") as q:
        #     if firstLG[0]:
        #         firstLG[0] = False
        #         q.write(",".join(titLG) + "\r\n")
        #     q.write(",".join(dataLG) + "\r\n")

        return min(3500, x if x > 0 else 0)
    except:
        return 0.0
