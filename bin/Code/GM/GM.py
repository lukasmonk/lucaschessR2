import operator
import os
import shutil

import FasterCode

import Code
from Code import Util
from Code.Base import Move
from Code.Base.Constantes import RESULT_DRAW, RESULT_WIN_BLACK, RESULT_WIN_WHITE, WHITE, BLACK


class GMgame:
    def __init__(self, linea):
        self.xpv, self.event, self.oponent, self.date, self.opening, self.result, self.color = linea.split("|")
        self.li_pv = FasterCode.xpv_pv(self.xpv).split(" ")
        self.len_pv = len(self.li_pv)

    def toline(self):
        return "%s|%s|%s|%s|%s|%s|%s" % (
            self.xpv,
            self.event,
            self.oponent,
            self.date,
            self.opening,
            self.result,
            self.color,
        )

    def is_white(self, is_white):
        if is_white:
            return "W" in self.color
        else:
            return "B" in self.color

    def is_valid_move(self, ply, move):
        if ply < self.len_pv:
            return self.li_pv[ply] == move
        else:
            return False

    def is_finished(self, ply):
        return ply >= self.len_pv

    def move(self, ply):
        return None if self.is_finished(ply) else self.li_pv[ply]

    def label(self, is_gm=True):
        if is_gm:
            return _("Opponent") + ": <b>%s (%s)</b>" % (self.oponent, self.date)
        else:
            return "%s (%s)" % (self.oponent, self.date)

    def basic_label(self, is_gm=True):
        if is_gm:
            return _("Opponent") + ": %s (%s)" % (self.oponent, self.date)
        else:
            return "%s (%s)" % (self.oponent, self.date)


class GM:
    def __init__(self, carpeta, gm):
        self.gm = gm
        self.carpeta = carpeta

        self.dicAciertos = {}

        self.li_gm_games = self.read()

        self.ply = 0
        self.last_game = None

    def __len__(self):
        return len(self.li_gm_games)

    def get_last_game(self):
        return self.last_game

    def read(self):
        # (kupad fix) linux is case sensitive and can't find the xgm file because ficheroGM is all lower-case, but all
        # the xgm files have the first letter capitalized (including ones recently downloaded)
        fichero_gm = "%s%s.xgm" % (self.gm[0].upper(), self.gm[1:])
        with open(Util.opj(self.carpeta, fichero_gm), "rt", encoding="utf-8", errors="ignore") as f:
            li = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    li.append(GMgame(linea))
        return li

    def filter_side(self, is_white):
        self.li_gm_games = [gmp for gmp in self.li_gm_games if gmp.is_white(is_white)]

    def play(self, move):
        move = move.lower()

        li_games = []
        ok = False
        next_ply = self.ply + 1
        for gmPartida in self.li_gm_games:
            if gmPartida.is_valid_move(self.ply, move):
                self.last_game = gmPartida  # - Siempre hay una ultima
                ok = True
                if not gmPartida.is_finished(next_ply):
                    li_games.append(gmPartida)

        self.li_gm_games = li_games
        self.ply += 1
        return ok

    def is_valid_move(self, move):
        move = move.lower()

        for gmPartida in self.li_gm_games:
            if gmPartida.is_valid_move(self.ply, move):
                return True
        return False

    def is_finished(self):
        for gmp in self.li_gm_games:
            if not gmp.is_finished(self.ply):
                return False
        return True

    def alternativas(self):
        li = []
        for gmPartida in self.li_gm_games:
            move = gmPartida.move(self.ply)
            if move and not (move in li):
                li.append(move)
        return li

    def get_moves_txt(self, position_before, is_gm):
        li = []
        d_repeticiones = {}
        for gmPartida in self.li_gm_games:
            move = gmPartida.move(self.ply)
            if move:
                if not (move in d_repeticiones):
                    d_repeticiones[move] = [len(li), 1]
                    from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]
                    ok, mens, move = Move.get_game_move(gmPartida, position_before, from_sq, to_sq, promotion)
                    li.append([from_sq, to_sq, promotion, gmPartida.basic_label(is_gm), move.pgn_translated()])
                else:
                    d_repeticiones[move][1] += 1
                    pos = d_repeticiones[move][0]
                    li[pos][3] = _("%d games") % d_repeticiones[move][1]
        return li

    def label_game_if_unique(self, is_gm=True):
        if len(self.li_gm_games) == 1:
            return self.li_gm_games[0].label(is_gm)
        else:
            return ""

    def resultado(self, game):
        last_game = self.last_game
        opening = game.opening.tr_name if game.opening else last_game.opening

        txt = _("Opponent") + " : <b>" + last_game.oponent + "</b><br>"
        event = last_game.event
        if event:
            txt += _("Event") + " : <b>" + event + "</b><br>"
        txt += _("Date") + " : <b>" + last_game.date + "</b><br>"
        txt += _("Opening") + " : <b>" + opening + "</b><br>"
        txt += _("Result") + " : <b>" + last_game.result + "</b><br>"
        txt += "<br>" * 2
        aciertos = 0
        for v in self.dicAciertos.values():
            if v:
                aciertos += 1
        total = len(self.dicAciertos)
        if total:
            porc = int(aciertos * 100.0 / total)
            txt += _("Hints") + " : <b>%d%%</b>" % porc
        else:
            porc = 0

        event = " - %s" % event if event else ""
        txt_summary = "%s%s - %s - %s" % (last_game.oponent, event, last_game.date, last_game.result)

        return txt, porc, txt_summary

    def set_game_selected(self, num_game):
        self.li_gm_games = [self.li_gm_games[num_game]]

    def gen_toselect(self):
        li_regs = []
        for num, part in enumerate(self.li_gm_games):
            dic = dict(
                NOMBRE=part.oponent, FECHA=part.date, ECO=part.opening, RESULT=part.result, NUMBER=num,
                EVENT=part.event, NUMMOVES=f"{len(part.li_pv):3d}"
            )
            li_regs.append(dic)
        return li_regs

    def write(self):
        fichero_gm = self.gm + ".xgm"
        with open(Util.opj(self.carpeta, fichero_gm), "wt", encoding="utf-8", errors="ignore") as q:
            for part in self.li_gm_games:
                q.write(part.toline() + "\n")

    def remove(self, num):
        del self.li_gm_games[num]
        self.write()


def get_folder_gm():
    return Util.opj(Code.configuration.carpeta, "GM")


def dic_gm():
    folder_gm = get_folder_gm()
    if not os.path.isdir(folder_gm):
        folder_ori_gm = Code.path_resource("GM")
        shutil.copytree(folder_ori_gm, folder_gm)
    dic = {}
    path_list = Code.path_resource("GM", "_listaGM.txt")
    with open(path_list, "rt", encoding="utf-8", errors="ignore") as f:
        for linea in f:
            if linea:
                li = linea.split("|")
                gm = li[0].lower()
                name = li[1]
                dic[gm] = name
        return dic


def lista_gm():
    dic = dic_gm()
    li = []

    for entry in Util.listdir(get_folder_gm()):
        fich = entry.name.lower()
        if fich.endswith(".xgm"):
            gm = fich[:-4].lower()
            li.append((dic.get(gm, gm), gm, True, True))
    if len(li) == 0:
        folder_gm = get_folder_gm()
        folder_ori_gm = Code.path_resource("GM")
        for entry in os.scandir(folder_ori_gm):
            shutil.copy(entry.path, folder_gm)
        return lista_gm()

    li = sorted(li, key=operator.itemgetter(0))
    return li


def lista_gm_personal(carpeta):
    li = []
    for entry in Util.listdir(carpeta):
        fich = entry.name
        if fich.lower().endswith(".xgm"):
            gm = fich[:-4]

            si_w = si_b = False
            with open(Util.opj(carpeta, fich), "rt", encoding="utf-8", errors="ignore") as f:
                for linea in f:
                    try:
                        gm_game = GMgame(linea.strip())
                    except:
                        continue
                    if not si_w:
                        si_w = gm_game.is_white(True)
                    if not si_b:
                        si_b = gm_game.is_white(False)
                    if si_w and si_b:
                        break
            if si_w or si_b:
                li.append((gm, gm, si_w, si_b))
    li = sorted(li)
    return li


class FabGM:
    def __init__(self, training_name, li_players, side, result):
        self.training_path = Util.opj(Code.configuration.personal_training_folder, training_name) + ".xgm"
        self.li_players = li_players

        self.f = None

        self.added = 0

        self.st_xpv = self.check_previous()

        self.side = side
        self.result = result

    def check_previous(self):
        st_xpv = set()
        if Util.exist_file(self.training_path):
            with open(self.training_path, "rt", encoding="utf-8", errors="ignore") as f:
                for linea in f:
                    li_sp = linea.split("|")
                    if len(li_sp) > 1:
                        st_xpv.add(li_sp[0])
        return st_xpv

    def write(self, txt):
        if self.f is None:
            self.f = open(self.training_path, "at", encoding="utf-8", errors="ignore")
        self.f.write(txt)
        self.added += 1

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def other_game(self, game):
        dic = game.dic_tags()

        if self.li_players:
            is_white = False
            is_black = False

            for x in ["Black", "White"]:
                if x in dic:
                    player = dic[x].upper()
                    ok = False
                    for uno in self.li_players:
                        startswith = uno.endswith("*")
                        endswith = uno.startswith("*")
                        uno = uno.replace("*", "").strip().upper()
                        if endswith:
                            if player.endswith(uno):
                                ok = True
                            if startswith:  # form apara poner siA y siZ
                                ok = uno in player
                        if startswith:
                            if player.startswith(uno):
                                ok = True
                        if uno == player:
                            ok = True
                        if ok:
                            break
                    if ok:
                        if x == "Black":
                            is_black = True
                        else:
                            is_white = True

        else:
            is_white = True
            is_black = True

        if is_white and (self.side in (WHITE, None)):
            self.other_game_side(dic, game, True)
        if is_black and (self.side in (BLACK, None)):
            self.other_game_side(dic, game, False)

    def other_game_side(self, dic, game, is_white):
        if self.result:
            result = game.resultado()
            draw = result == RESULT_DRAW
            win = result == (RESULT_WIN_WHITE if is_white else RESULT_WIN_BLACK)
            lost = not win
            if self.result == "Win":
                ok = win
            elif self.result == "Win+Draw":
                ok = win or draw
            elif self.result == "Lost":
                ok = lost
            elif self.result == "Lost+Draw":
                ok = lost or draw
            else:
                ok = True
            if not ok:
                return

        pv = game.pv()

        event = dic.get("Event", "-")
        oponente = dic.get("White", "?") + "-" + dic.get("Black", "?")
        date = dic.get("Date", "-").replace("?", "").strip(".")
        eco = dic.get("Eco", "-")
        result = dic.get("Result", "-")
        color = "W" if is_white else "B"

        def nopipe(txt):
            return txt.replace("|", " ").strip() if "|" in txt else txt

        xpv = FasterCode.pv_xpv(pv)
        if xpv not in self.st_xpv:
            self.write(
                "%s|%s|%s|%s|%s|%s|%s\n" % (xpv, nopipe(event), nopipe(oponente), nopipe(date), eco, result, color)
            )
            self.st_xpv.add(xpv)

    def xprocesa(self):
        self.close()
        return self.added
