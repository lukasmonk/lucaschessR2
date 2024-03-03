import random

from Code import Util
from Code.Base import Game, Position
from Code.SQL import UtilSQL


class Reinforcement:
    def __init__(self, tactica):
        self.tactica = tactica
        self.li_num_fens = []
        self.li_work_fens = []  # li_num_fens *cycles
        self.pos_active = -1
        self.active = False
        self.max_errors = tactica.reinforcement_errors
        self.cycles = tactica.reinforcement_cycles
        self.restore()

    def __len__(self):
        return len(self.li_num_fens)

    def list_positions(self):
        return self.li_work_fens

    def total_positions(self):
        return len(self.li_work_fens)

    def enabled(self):
        return self.max_errors > 0

    def add_error(self, num):
        if self.max_errors == 0:
            return
        if not (num in self.li_num_fens):
            self.li_num_fens.append(num)
            self.save()
            if len(self.li_num_fens) >= self.max_errors:
                self.activate()

    def add_working_error(self):
        if self.pos_active >= 0:
            self.activate()

    def get_working_position(self):
        return self.li_work_fens[self.pos_active]

    def activate(self):
        li = self.li_num_fens[:]
        random.shuffle(li)
        self.li_work_fens = []
        for cycle in range(self.cycles):
            self.li_work_fens.extend(li)
        self.active = True
        self.pos_active = -1
        self.save()

    def deactivate(self):
        self.li_work_fens = []
        self.li_num_fens = []
        self.pos_active = -1
        self.active = False
        self.save()

    def save(self):
        dic = {
            "li_num_fens": self.li_num_fens,
            "li_work_fens": self.li_work_fens,
            "pos_active": self.pos_active,
            "active": self.active,
        }
        with self.tactica.dbdatos() as db:
            db["DICREINFORCEMENT"] = dic

    def restore(self):
        with self.tactica.dbdatos() as db:
            dic = db["DICREINFORCEMENT"]
            if dic:
                self.li_num_fens = dic["li_num_fens"]
                self.li_work_fens = dic["li_work_fens"]
                self.pos_active = dic["pos_active"]
                self.active = dic["active"]
            else:
                self.li_num_fens = []
                self.li_work_fens = []
                self.pos_active = -1
                self.active = False

    def is_activated(self):
        if self.enabled():
            if not self.active and (len(self.li_num_fens) >= self.max_errors):
                self.activate()
            if self.active and self.pos_active == -1:
                self.pos_active = 0
            return self.active
        else:
            return False

    def current_position(self):
        return self.pos_active if self.active else None

    def set_current_position(self, pos):
        self.pos_active = pos
        if self.pos_active > len(self.li_work_fens):
            self.deactivate()
        else:
            self.save()

    def label(self):
        if self.is_activated():
            return _("Reinforcement"), ""
        elif self.enabled():
            if len(self.li_num_fens) > 0:
                return (
                    "",
                    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(%s%d/%d)"
                    % (_("Reinforcement")[0], len(self.li_num_fens), self.max_errors),
                )
        return "", ""

    def work_line_finished(self):
        self.pos_active += 1
        if self.pos_active == len(self.li_work_fens):
            self.deactivate()
        else:
            self.save()

    def remove_data(self):
        with self.tactica.dbdatos() as db:
            del db["DICREINFORCEMENT"]


class Tactics:
    """# Numero de puzzles en cada entrenamiento, menos si no hay tantos
    PUZZLES=100

    # Saltos de repeticion, 3 = entrenam1,otro,otro,otro,entrenam1, se cumple cuando se puede
    JUMPS=3,5,9,17

    # Repeticion, 0:No, 1:igual, 2:random
    REPEAT=1,2

    # Penalizacion en caso de error, se divide el total de puzzles por los grupos de penalizacion y se aplica
    # ej. 100 puzzles, 1-25:1, 26-50:2,....
    PENALIZATION=1,2,3,4

    SHOWTEXT=1

    FOLDER=../Resources/Trainings/Checkmates in GM games

    [ALIAS]
    M1=Mate in 1.fns
    M2=Mate in 2.fns
    M3=Mate in 3.fns
    M4=Mate in 4.fns
    M5=Mate in 5.fns
    M6=Mate in 6.fns
    M7=Mate in 7.fns

    [TACTIC1]
    MENU=Mate in 1
    # Fichero:Peso[:xfrom:xto]
    FILESW=M1:100

    [TACTIC2]
    MENU=Mate in 2
    FILESW=M2:100

    [TACTIC3]
    MENU=Mate in 3
    FILESW=M3:100
    """

    def __init__(self, tipo, name, carpeta, ini):

        self.tipo = tipo
        self.name = name
        self.folder = carpeta
        self.ini = ini

        self.dic = Util.ini2dic(self.ini)

        if "COMMON" in self.dic:
            self.folder = self.dic["COMMON"].get("FOLDER", self.folder)

    def listaMenus(self):
        liMenu = []
        for k in self.dic:
            if k.upper().startswith("TACTIC"):
                d = self.dic[k]
                menu = d["MENU"]
                liMenu.append((k, menu.split(",")))
        return liMenu

    def eligeTactica(self, resp, folder_data):
        return Tactic(self, resp, self.tipo, folder_data)


class Tactic:
    w_next_position: int

    def __init__(self, tactics, name, tipo, folder_user):
        self.tactics = tactics
        self.name = name
        self.tipo = tipo
        self.path_db = Util.relative_path(folder_user, "%s%s.tdb" % (self.tactics.name, tipo))

        # Default values ##########################################################################################
        # Max number of puzzles in each block
        self.puzzles = 100

        # Puzzle repetitions, each puzzle can be repeated, this field determine separations among replicates,
        # more repetitions are separated by comma
        self.jumps = [3, 5, 9, 17]

        # Block repetitions, Repetitions of total of puzzles, comma separated,
        # indicating order of repetition as 0=original, 1=random, 2=previous, eg 1,2,0=3 repetitions,
        # first is random, second repeat previous, and third original. Total field in blanck is the same as 0
        self.repeat = [0, 1]

        # Penalties, divided in blocks, by example 1,3,5,7 means first 25%
        # (100%/4) of puzzles has one position of penalty when error, second 25%
        # three and so on. Blank means no penalties.
        self.penalization = [1, 2, 3, 4]

        # Text while training, in blocks like penalties, 1,0,0,0, 25% Yes, rest No
        self.showtext = [1]

        # 0 = El que corresponda, 1 = White 2 = Black
        self.pointview = 0

        # Name of specific training
        self.reference = ""

        # When 10 positions are done with error, begin the cycle of reinforcement, repeat until no errors
        self.reinforcement_errors = 10

        # It needs 2 cycles without errors to continue the tactic
        self.reinforcement_cycles = 2

        self.title = ""

        self.filesw = []

        if "COMMON" in self.tactics.dic:
            self.read_dic(self.tactics.dic["COMMON"])

        self.advanced = False

        self.read_dic(self.tactics.dic[self.name])
        self.leeDatos()

    def title_extended(self):
        return self.tactics.name + " " + self.title

    def read_dic(self, dic):
        c = dic.get("PUZZLES")
        if c and c.isdigit():
            self.puzzles = int(c)

        c = dic.get("JUMPS")
        if c:
            self.jumps = [int(x) for x in c.replace(" ", "").split(",")]

        c = dic.get("REPEAT")
        if c:
            self.repeat = [int(x) for x in c.replace(" ", "").split(",")]

        c = dic.get("POINTVIEW")
        if c in ("0", "1", "2"):
            self.pointview = int(c)

        c = dic.get("REFERENCE")
        if c:
            self.reference = c

        c = dic.get("PENALIZATION")
        if c:
            self.penalization = [int(x) for x in c.replace(" ", "").split(",")]

        c = dic.get("SHOWTEXT")
        if c:
            self.showtext = [int(x) for x in c.replace(" ", "").split(",") if x in ("0", "1")]

        c = dic.get("REINFORCEMENT_ERRORS")
        if c and c.isdigit():
            self.reinforcement_errors = int(c)

        c = dic.get("REINFORCEMENT_CYCLES")
        if c and c.isdigit():
            self.reinforcement_cycles = int(c)

        c = dic.get("MENU")
        if c:
            li = c.split(",")
            for x in range(len(li)):
                li[x] = _F(li[x])
            self.title = "-".join(li)

        c = dic.get("FILESW")
        if c:
            li = c.split(",")
            self.filesw = []
            for x in li:
                li = x.split(":")
                nli = len(li)
                d = None
                h = None
                if nli == 2:
                    f, w = li
                    w = int(w)
                elif nli == 0:
                    f = x
                    w = 100
                elif nli == 4:
                    f, w, d, h = li
                    w = int(w)
                    d = int(d)
                    h = int(h)
                else:
                    f = li[0]
                    w = int(li[1])
                self.filesw.append((f, w, d, h))  # file, weight,from,to

        self.advanced = dic.get("ADVANCED", False)

    def dbdatos(self):
        return UtilSQL.DictSQL(self.path_db, tabla=self.name)

    def historico(self):
        with self.dbdatos() as db:
            liHisto = db["HISTO"]
            return [] if liHisto is None else liHisto

    def leeDatos(self):
        with self.dbdatos() as db:
            def read_db(key, default):
                v = db[key]
                if v is None:
                    v = db[key] = default
                return v

            self.liFNS = read_db("LIFNS", [])
            self.liOrder = read_db("ORDER", [])

            self.posActive = db["POSACTIVE"]

            self.showtext = read_db("SHOWTEXT", [1])

            read_db("ERRORS", 0)

            read_db("REFERENCE", "")

            self.penalization = read_db("PENALIZATION", [1, 2, 3, 4])

            self.reinforcement_errors = read_db("REINFORCEMENT_ERRORS", 10)
            self.reinforcement_cycles = read_db("REINFORCEMENT_CYCLES", 2)

        self.reinforcement = Reinforcement(self)

    def listaFicheros(self, key):
        dalias = self.tactics.dic.get("ALIAS", {})
        if key in dalias:
            return self.listaFicheros(dalias[key])
        lif = []
        if "," in key:
            for uno in key.split(","):
                lif.extend(self.listaFicheros(uno))
        elif "*" in key or "?" in key or "[" in key:
            li = Util.listfiles(self.tactics.folder, key)
            lif.extend(li)
        else:
            lif.append(Util.opj(self.tactics.folder, key))
        return lif

    def calculaTotales(self):
        li = []
        for f, w, d, h in self.filesw:
            t = 0
            for fich in self.listaFicheros(f):
                with Util.OpenCodec(fich, "rt") as q:
                    for linea in q:
                        linea = linea.strip()
                        if linea and "|" in linea:
                            t += 1
            li.append(t)
        return li

    def genera(self):
        with self.dbdatos() as db:
            num = self.puzzles

            # Determinamos la lista de fens, teniendo en cuenta el peso asociado a cada file
            lif = []

            wt = 0
            for f, w, d, h in self.filesw:
                lif0 = []
                for fich in self.listaFicheros(f):
                    with open(fich, "rt", encoding="utf-8", errors="ignore") as f:
                        for linea in f:
                            linea = linea.strip()
                            if linea and "|" in linea:
                                lif0.append(linea)
                if d and d <= h:
                    d -= 1
                    lif0 = lif0[d:h]
                lif.append([w, lif0])
                wt += w
            t = 0
            for li in lif:
                li[0] = int(li[0] * num / wt)
                t += li[0]
            t -= self.puzzles
            n = 0
            while t:
                lif[0][n] += 1
                t -= 1
                n += 1
                if n == len(lif):
                    n = 0

            liFNS = []
            for li in lif:
                n = li[0]
                lif0 = li[1]
                if len(lif0) < n:
                    n = len(lif0)
                lir = lif0[:n]
                for x in lir:
                    liFNS.append(x)

            db["LIFNS"] = liFNS
            self.liFNS = liFNS

            numPuzzles = len(liFNS)

            # Deteminamos la lista indice con el orden de cada fen en liFNS
            liJUMPS = self.jumps

            li = [None] * (len(liJUMPS) * 2 * numPuzzles)  # Creamos un list muy grande, mayor del que vamos a usar

            def busca(from_sq, salto):
                if salto == 0:
                    for x in range(from_sq, len(li)):
                        if li[x] is None:
                            return x
                    li.extend([None] * 1000)
                    return busca(from_sq, salto)
                else:
                    while salto:
                        from_sq = busca(from_sq + 1, 0)
                        salto -= 1
                    return from_sq

            for x in range(numPuzzles):
                n = busca(0, 0)
                li[n] = x
                for m in liJUMPS:
                    n = busca(n + 1, int(m))
                    li[n] = x

            li_base = []
            for x in li:
                if x is not None:
                    li_base.append(x)

            li_order = []

            li_nueva = li_base[:]
            for repeat in self.repeat:
                if repeat == 0:  # Original
                    li_nueva = li_base[:]
                elif repeat == 1:
                    li_nueva = li_base[:]
                    random.shuffle(li_nueva)
                else:
                    li_nueva = li_nueva[:]
                li_order.extend(li_nueva)

            db["ORDER"] = li_order
            self.liOrder = li_order

            db["POSACTIVE"] = 0

            db["SHOWTEXT"] = self.showtext

            db["POINTVIEW"] = self.pointview

            db["REFERENCE"] = self.reference

            db["PENALIZATION"] = self.penalization

            li_histo = db["HISTO"]
            if not li_histo:
                li_histo = []
            dicActual = {
                "FINICIAL": Util.today(),
                "FFINAL": None,
                "SECONDS": 0.0,
                "POS": self.total_positions(),
                "ERRORS": 0,
                "PUZZLES": self.puzzles,
                "FILESW": self.filesw,
                "JUMPS": self.jumps,
                "REPEAT": self.repeat,
                "SHOWTEXT": self.showtext,
                "PENALIZATION": self.penalization,
                "REINFORCEMENT_ERRORS": self.reinforcement_errors,
                "REINFORCEMENT_CYCLES": self.reinforcement_cycles,
                "ADVANCED": self.advanced,
            }
            li_histo.insert(0, dicActual)
            db["HISTO"] = li_histo
            db["SECONDS"] = 0.0
            db["ERRORS"] = 0
            db["REINFORCEMENT_ERRORS"] = self.reinforcement_errors
            db["REINFORCEMENT_CYCLES"] = self.reinforcement_cycles

            db.pack()

    def list_positions(self):
        return self.liOrder

    def with_automatic_jump(self):
        with self.dbdatos() as db:
            siauto = db["AUTOJUMP"]
            return False if siauto is None else siauto

    def set_automatic_jump(self, siSalto):
        with self.dbdatos() as db:
            db["AUTOJUMP"] = siSalto

    def set_advanced(self, enable):
        with self.dbdatos() as db:
            db["ADVANCED"] = enable

    def current_position(self):
        with self.dbdatos() as db:
            return db["POSACTIVE"]

    def finished(self):
        with self.dbdatos() as db:
            pactive = db["POSACTIVE"]
            return not self.historico() or pactive is None or pactive >= self.total_positions()

    def total_positions(self):
        return len(self.liOrder)

    def numFNS(self):
        return len(self.liFNS)

    def penalization_positions(self, current, total):
        if self.penalization:
            li = self.penalization
            n = total // len(li)
            if n == 0:
                return 0
            n1 = current // n
            if n1 >= len(li):
                n1 = len(li) - 1
            return li[n1]
        else:
            return 0

    def pointView(self):
        with self.dbdatos() as db:
            n = db["POINTVIEW"]
            if n is None:
                n = 0
            return int(n)

    def masSegundos(self, mas):
        with self.dbdatos() as db:
            if "SECONDS" in db:
                db["SECONDS"] += mas

    def segundosActivo(self):
        with self.dbdatos() as db:
            return db["SECONDS"]

    def referenciaActivo(self):
        with self.dbdatos() as db:
            return db["REFERENCE"]

    def erroresActivo(self):
        with self.dbdatos() as db:
            return db["ERRORS"]

    def end_training(self):
        with self.dbdatos() as db:
            liHisto = db["HISTO"]
            if not liHisto:
                liHisto = []
                dicActual = {
                    "FINICIAL": Util.today(),
                    "FFINAL": None,
                    "SECONDS": 0.0,
                    "POS": self.total_positions(),
                    "ERRORS": 0,
                }
                liHisto.insert(0, dicActual)
            liHisto[0]["FFINAL"] = Util.today()
            liHisto[0]["SECONDS"] = db["SECONDS"]
            liHisto[0]["ERRORS"] = db["ERRORS"]
            liHisto[0]["REFERENCE"] = db["REFERENCE"]

            db["HISTO"] = liHisto
            db["POSACTIVE"] = None

    def borraListaHistorico(self, liNum):
        with self.dbdatos() as db:
            liHisto = self.historico()
            liNueHisto = []
            for x in range(len(liHisto)):
                if not (x in liNum):
                    liNueHisto.append(liHisto[x])
            db["HISTO"] = liNueHisto
            if 0 in liNum:
                db["POSACTIVE"] = None
                del db["DICREINFORCEMENT"]

    def work_list_positions(self):
        if self.reinforcement.is_activated():
            return self.reinforcement.list_positions()
        else:
            return self.list_positions()

    def work_current_position(self):
        position = None
        if self.reinforcement.is_activated():
            position = self.reinforcement.current_position()
        if position is None:
            position = self.current_position()
        return position

    def work_reset_positions(self):
        self.w_error = False
        self.w_reinforcement_working = self.reinforcement.is_activated()
        if self.w_reinforcement_working:
            self.w_current_position = self.reinforcement.current_position()
            self.w_total_positions = self.reinforcement.total_positions()
        else:
            self.w_current_position = self.current_position()
            self.w_total_positions = self.total_positions()
        self.w_next_position = self.w_current_position + 1

    def work_read_position(self):
        if self.w_reinforcement_working:
            pos = self.reinforcement.get_working_position()
        else:
            pos = self.current_position()
        posfen = self.liOrder[pos]
        txt = self.liFNS[posfen]
        li = txt.split("|")

        fen = li[0]
        if fen.endswith(" 0"):
            fen = fen[:-1] + "1"
        label = li[1]
        solucion = li[2]
        ok, game_obj = Game.pgn_game('[FEN "%s"]\n%s' % (fen, solucion))

        game_base = None
        if len(li) > 3:
            txt = li[3].replace("]", "]\n").replace(" [", "[")
            ok, game_base = Game.pgn_game(txt)
            if ok:
                cp = Position.Position()
                cp.read_fen(fen)
                ok = False
                for n in range(len(game_base) - 1, -1, -1):
                    move = game_base.move(n)
                    if move.position == cp:
                        ok = True
                        if n + 1 != len(game_base):
                            game_base.li_moves = game_base.li_moves[: n + 1]
                        break
            if not ok:
                game_base = None

        if game_base:
            game_base.set_unknown()

        self.w_label = label

        return game_obj, game_base

    def work_must_showtext(self):
        n = len(self.showtext)
        if n == 0:
            return True
        current_position = (
            self.current_position()
        )  # debemos utilizar los estandar y no los work ya que no serían correctos si reinforcing
        total_positions = self.total_positions()
        bloque = total_positions * 1.0 / n
        ns = int(current_position / bloque)
        if ns >= n:
            ns = n - 1
        return self.showtext[ns] == 1

    def work_info(self, is_finished):
        if is_finished:
            return self.w_label
        else:
            return self.w_label if self.work_must_showtext() else ""

    def work_game_finished(self):
        if self.reinforcement.is_activated():
            return False
        else:
            return (self.w_next_position > self.w_total_positions) and len(self.reinforcement) == 0

    def work_info_position(self):
        reinforcement_title, reinforcement_state = self.reinforcement.label()
        title = ""

        if self.w_next_position == self.w_total_positions:
            if self.w_reinforcement_working:
                mens = _("End reinforcement")
                color = "blue"
                title = '<tr><td  align="center"><h4>%s</h4></td></tr>' % reinforcement_title
            else:
                mens = _("GAME OVER")
                color = "DarkMagenta"
            str_final = "%s: <big>%s</big>" % (_("Next"), mens)

        else:
            str_final = "%s: %d" % (_("Next"), self.w_next_position + 1)
            color = "red" if self.w_next_position <= self.w_current_position else "blue"

            if self.reinforcement.is_activated():
                if not self.w_reinforcement_working:
                    str_final = "%s: %s" % (_("Next"), _("Reinforcement"))
                else:
                    if reinforcement_title:
                        title = f'<tr><td  align="center"><h4>{reinforcement_title}</h4></td></tr>'
                    if reinforcement_state:
                        str_final += reinforcement_state
            elif reinforcement_state:
                str_final += reinforcement_state

        str_current = _("Current position")
        html = (
            '<table border="1" with="100%%" align="center" cellpadding="5" cellspacing="0">'
            f"{title}"
            '<tr><td  align="center">'
            f'<h4>{str_current}: {self.w_current_position + 1}/{self.w_total_positions}'
            f'<br><font color="{color}">{str_final}</font></h4>'
            '</td></tr>'
            "</table>"
        )
        return html

    def work_add_error(self):
        if self.w_error:
            return
        self.w_error = True
        if self.w_reinforcement_working:
            self.reinforcement.add_working_error()
            self.w_next_position = 0
        else:
            self.reinforcement.add_error(self.w_current_position)
            self.w_next_position = self.w_current_position - self.penalization_positions(
                self.w_current_position, self.w_total_positions
            )
            if self.w_next_position < 0:
                self.w_next_position = 0

        with self.dbdatos() as db:
            db["ERRORS"] += 1
            if not self.w_reinforcement_working:
                db["POSACTIVE"] = self.w_next_position

    def work_line_finished(self):
        if not self.w_reinforcement_working:
            with self.dbdatos() as db:
                db["POSACTIVE"] = self.w_next_position
        else:
            if not self.w_error:
                self.reinforcement.work_line_finished()
        self.work_reset_positions()

    def work_set_current_position(self, pos):
        if self.reinforcement.is_activated():
            self.reinforcement.set_current_position(pos)
        else:
            with self.dbdatos() as db:
                db["POSACTIVE"] = self.w_next_position

    def remove_reinforcement(self):
        self.reinforcement.remove_data()
