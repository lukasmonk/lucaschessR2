import FasterCode

from Code import Util
from Code.Base import Game
from Code.SQL import Base


def str_file(file):
    with open(file) as f:
        return eval(f.read())


def gen_list(txt):  # tolerance and tries in 12
    if "," in txt:
        xmin, xmax = txt.split(",")
    else:
        xmin, xmax = txt.split("-")
    xmin = int(xmin.strip())
    xmax = int(xmax.strip())
    dif = (xmax - xmin) / 11.0
    li = [xmax, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, xmin]
    for x in range(1, 11):
        xmax -= dif
        li[x] = int(round(xmax, 0))
    return li


def pos_lidistribution(lidistribution, pos):
    from_sq = 0
    for n, x in enumerate(lidistribution):
        to_sq = from_sq + x - 1
        if from_sq <= pos <= to_sq:
            return n, pos - from_sq
        from_sq = to_sq + 1


class Expedition:
    def __init__(self, configuration, recno):
        ex = Expeditions(configuration)
        self.reg = ex.goto(recno)
        ex.close()
        self.configuration = configuration
        self.recno = recno

    def gen_routes(self):
        ev = Everest()
        li_distribution = eval(self.reg.DISTRIBUTION)
        done_game = self.reg.NEXT_GAME - 1
        height, svg = ev.svg(li_distribution, done_game)
        tries = gen_list(self.reg.TRIES)
        tolerances = gen_list(self.reg.TOLERANCE)
        times = eval(self.reg.TIMES)
        li_p = ev.li_points
        li_routes = []
        xgame = done_game + 1
        xcurrent = None
        xtrayecto = ""
        for x in range(12):
            d = {}
            d["ROUTE"] = "%s - %s" % (li_p[x][4], li_p[x + 1][4])
            xc = li_distribution[x]
            d["GAMES"] = str(xc)
            done = xgame if xc >= xgame else xc
            xgame -= xc
            if xcurrent is None and xgame < 0:
                xcurrent = x
                xtrayecto = d["ROUTE"]

            d["DONE"] = str(done if done > 0 else "0")
            d["TRIES"] = str(tries[x])
            d["TOLERANCE"] = str(tolerances[x])
            seconds = times[x][0]
            d["TIME"] = "%d' %d\"" % (seconds / 60, seconds % 60)
            mseconds = seconds / done if done > 0 else 0
            d["MTIME"] = "%d' %d\"" % (mseconds / 60, mseconds % 60)
            d["MPOINTS"] = "%d" % (int(times[x][1] / done) if done else 0)
            li_routes.append(d)

        label = (self.reg.NAME, xtrayecto, "%s: %d" % (_("Altitude"), int(height)))

        return li_routes, xcurrent, svg, label

    def run(self):
        # num game
        game = self.reg.GAMES[self.reg.NEXT_GAME]

        # label
        labels = game["LABELS"]
        event = ""
        site = ""
        date = ""
        white = ""
        black = ""
        result = ""
        fen = ""
        for key, value in labels:
            key = key.lower()
            if key == "event":
                event = value
            elif key == "site":
                site = value
            elif key == "date":
                date = value.replace(".?", "").replace("?", "")
            elif key == "white":
                white = value
            elif key == "black":
                black = value
            elif key == "result":
                result = value
            elif key == "fen":
                fen = value
        txt = ""
        if date:
            txt += "%s " % date
        if event or site:
            txt += "%s - %s" % (event, site)
            txt = txt.strip().strip("-") + "\n"
        if white or black:
            txt += "%s - %s\n" % (white, black)
        self.label_base = txt

        # color
        if self.reg.COLOR == "D":
            self.is_white = True
            if result == "0-1":
                self.is_white = False
            elif result == "1/2-1/2":
                self.is_white = False
            elif fen:
                self.is_white = "w" in fen
        else:
            self.is_white = self.reg.COLOR == "W"
        self.name = white if self.is_white else black

        pv = FasterCode.xpv_pv(game["XPV"])
        self.game = Game.Game(fen=fen)
        self.game.read_pv(pv)
        self.game.set_tags(labels)

        li_distribution = eval(self.reg.DISTRIBUTION)
        tries = gen_list(self.reg.TRIES)
        tolerances = gen_list(self.reg.TOLERANCE)

        self.tramo, self.pos_tramo = pos_lidistribution(li_distribution, self.reg.NEXT_GAME)
        self.max_tries = tries[self.tramo]
        self.tolerance = tolerances[self.tramo]

        self.tries_used = self.reg.TRIES_USED

    def label(self):
        return "%s%s: %d/%d - %s: %d %s" % (
            self.label_base,
            _("Tries"),
            self.tries_used + 1,
            self.max_tries + 1,
            _("Tolerance"),
            self.tolerance,
            _("centipawns"),
        )

    def add_try(self, ok, seconds, points):
        ex = Expeditions(self.configuration)

        change_game = False

        next_game = self.reg.NEXT_GAME
        if ok:
            next_game += 1
            change_game = True
            self.tries_used = 0
        else:
            self.tries_used += 1
            if self.tries_used > self.max_tries:
                self.tries_used = 0
                if self.pos_tramo:
                    next_game -= 1
                    change_game = True

        times = eval(self.reg.TIMES)
        times[self.tramo][0] += seconds
        times[self.tramo][1] -= points

        ex.save_next(self.recno, next_game, self.tries_used, times)

        self.reg = ex.goto(self.recno)
        if len(self.reg.GAMES) >= self.reg.NEXT_GAME:
            is_last = True
            is_last_last = self.tramo == 11
        else:
            is_last = False
            is_last_last = False
            self.run()

        ex.close()

        return change_game, is_last, is_last_last


class Expeditions:
    def __init__(self, configuration):
        self.configuration = configuration

        path_file = configuration.ficheroExpeditions

        self.db = Base.DBBase(path_file)
        self.tabla = "Expeditions"
        if not self.db.existeTabla(self.tabla):
            self.creaTabla()

        li_fields = (
            "DATE_INIT",
            "NAME",
            "DATE_END",
            "TIMES",
            "NUM_GAMES",
            "NEXT_GAME",
            "TRIES_USED",
            "DISTRIBUTION",
            "TOLERANCE",
            "TRIES",
            "COLOR",
        )  # , "GAMES" Games no se lee en cache, leeOtroCampo,
        # o al escribir un reg
        self.dbf = self.db.dbf(self.tabla, ",".join(li_fields), orden="DATE_INIT DESC")
        self.dbf.leer()

    def close(self):
        if self.dbf:
            self.dbf.cerrar()
            self.dbf = None
        if self.db:
            self.db.cerrar()
            self.db = None

    def reccount(self):
        return self.dbf.reccount()

    def creaTabla(self):
        tb = Base.TablaBase(self.tabla)
        tb.nuevoCampo("DATE_INIT", "VARCHAR", notNull=True, primaryKey=True)
        tb.nuevoCampo("NAME", "VARCHAR")
        tb.nuevoCampo("DATE_END", "VARCHAR")
        tb.nuevoCampo("TIMES", "VARCHAR")
        tb.nuevoCampo("NUM_GAMES", "INTEGER")
        tb.nuevoCampo("NEXT_GAME", "INTEGER")
        tb.nuevoCampo("TRIES_USED", "INTEGER")
        tb.nuevoCampo("DISTRIBUTION", "VARCHAR")
        tb.nuevoCampo("TOLERANCE", "VARCHAR")
        tb.nuevoCampo("TRIES", "VARCHAR")
        tb.nuevoCampo("COLOR", "VARCHAR")
        tb.nuevoCampo("GAMES", "BLOB")
        self.db.generarTabla(tb)

    def goto(self, num):
        self.dbf.goto(num)
        reg = self.dbf.registroActual()
        reg.GAMES = Util.zip2var(self.dbf.leeOtroCampo(num, "GAMES"))
        return reg

    def field(self, nfila, name):
        try:
            self.dbf.goto(nfila)
            reg = self.dbf.registroActual()
            return getattr(reg, name)
        except:
            return ""

    def new(self, reg_base):
        def distribution(num):
            lipesos = []
            t = 1
            for x in range(12):
                t += x + 3 / (x + 1)
                lipesos.append(t)

            pt = num
            li_resp = []
            for n, peso in enumerate(lipesos[:-1]):
                elem = int(peso * pt * 100.0 / sum(lipesos[n:]))
                v = elem // 100
                if elem % 100:
                    v += 1

                li_resp.append(v)
                pt -= v
            li_resp.append(pt)
            return li_resp[::-1]

        games = reg_base.tourney["GAMES"]
        reg = Util.Record()
        reg.DATE_INIT = Util.dtosext(Util.today())
        reg.DATE_END = ""
        reg.NAME = _FO(reg_base.tourney["TOURNEY"])
        reg.TIMES = str([[0, 0]] * 12)
        reg.NUM_GAMES = ngames = len(games)
        reg.NEXT_GAME = 0
        reg.TRIES_USED = 0
        reg.DISTRIBUTION = str(distribution(ngames))
        reg.TOLERANCE = "%d - %d" % (reg_base.tolerance_min, reg_base.tolerance_max)
        reg.TRIES = "%d - %d" % (reg_base.tries_min, reg_base.tries_max)
        reg.COLOR = reg_base.color
        reg.GAMES = Util.var2zip(games)

        self.dbf.insertarReg(reg, True)

    def save_next(self, recno, next_game, tries_used, times):
        reg = Util.Record()
        reg.NEXT_GAME = next_game
        reg.TRIES_USED = tries_used
        reg.TIMES = str(times)
        self.dbf.modificarReg(recno, reg)

    def borrar_lista(self, lirecnos):
        self.dbf.remove_list_recnos(lirecnos)
        self.dbf.pack()
        self.dbf.leer()


class Everest:
    def __init__(self):
        self.li_points = (
            ("Kathmandu", 1317, 116.4, 477.94, _("Kathmandu")),  # loc, height, x, y
            ("Phakding", 2610, 192.4, 399.94, _("Phakding")),
            ("Namche Bazaar", 3440, 268.4, 349.94, _("Namche Bazaar")),
            ("Tengboche", 3867, 344.4, 323.94, _("Tengboche")),
            ("Pheriche", 4250, 420.4, 299.94, _("Pheriche")),
            ("Lobuche", 4930, 496.4, 259.94, _("Lobuche")),
            ("Gorakshep", 5170, 572.4, 243.94, _("Gorakshep")),
            ("Base Camp", 5364, 648.4, 233.94, _("Base Camp")),
            ("Camp 1", 5943, 724.4, 199.94, _("Camp 1")),
            ("Camp 2", 6400, 800.4, 169.94, _("Camp 2")),
            ("Camp 3", 7162, 876.4, 127.94, _("Camp 3")),
            ("Camp 4", 8000, 952.4, 73.94, _("Camp 4")),
            ("Everest", 8848, 1028.4, 23.94, _("Everest")),
        )

    def _svg(self, height):
        c_svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" height="517.48px" width="1169.9px" version="1.1" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" viewBox="0 0 1169.8729 517.47516">
 <defs>
  <linearGradient id="linearGradient4458" x1="593.87" gradientUnits="userSpaceOnUse" y1="908.21" gradientTransform="matrix(1.0069 0 0 .99999 -11.397 -884.63)" x2="593.87" y2="1402.4">
   <stop stop-color="#9dc7da" offset="0"/>
   <stop stop-color="#4a99bb" stop-opacity="0" offset="1"/>
  </linearGradient>
  <linearGradient id="linearGradient4466" x1="907.56" gradientUnits="userSpaceOnUse" y1="946.11" gradientTransform="translate(1.1001 -887.26)" x2="907.56" y2="1397.2">
   <stop stop-color="#c38e46" offset="0"/>
   <stop stop-color="#b68441" offset=".092467"/>
   <stop stop-color="#3b2a13" offset="1"/>
  </linearGradient>
  <linearGradient id="linearGradient4475" x1="647.65" gradientUnits="userSpaceOnUse" y1="932.55" gradientTransform="matrix(.99999 0 0 .99999 2.3913 -884.61)" x2="647.65" y2="1398.5">
   <stop stop-color="#f00e0e" offset="0"/>
   <stop stop-color="#eecf00" offset=".25697"/>
   <stop stop-color="#2c960f" offset=".6082"/>
   <stop stop-color="#2121f3" offset="1"/>
  </linearGradient>
 </defs>
 <metadata>
  <rdf:RDF>
   <cc:Work rdf:about="">
    <dc:format>image/svg+xml</dc:format>
    <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
    <dc:title/>
   </cc:Work>
  </rdf:RDF>
 </metadata>
 <style type="text/css">#P0,P1 {stroke:#000;stroke-width:.99999958}
#P0 {fill:url(#L0)}
#P1 {fill:url(#R0)}
#P2 {fill:#fff}</style>
 <rect height="517.48" width="1169.9" y="-1.1959e-14" x="-.0081176" fill="url(#linearGradient4458)"/>
 <path stroke="#000" stroke-width="1.8" d="m1131.9 510.25 0.7615-365.77-6.5478-5.8979c-3.9743-12.949-16.812-19.63-23.068-31.364-0.5198-0.5997-1.5792-1.7591-2.099-2.3588-0.4997-11.454-12.754-9.5552-14.633-20.21-0.1199-0.85957-0.3398-2.5787-0.4597-3.4583-0.9596-2.1189-1.7791-4.4178-3.5383-6.037-8.8355-6.2569-14.053-18.011-24.128-21.769-2.0989 1.0795-4.078 2.3388-6.077 3.5582-2.9185 0.15992-4.2778 1.6992-4.0779 4.5977-1.5392 1.999-2.9785 4.058-4.5178 6.037-13.753 9.3153-27.366 18.891-41.339 27.846-2.4988 0.04-4.9975 0.08-7.4763 0.13993-2.6787-0.17991-4.2978 1.0795-4.8576 3.7781l-7.2076 7.2456c-10.015 1.899-12.942 0.83029-22.678 3.589l-1.7191 0.5997c-3.6382 1.1794-7.1364 2.6387-10.555 4.3378l-1.5192 0.6796c-3.1984 2.5187-5.7971 5.6772-8.3758 8.7956l-1.6192 0.2599c-2.7408 2.213-2.2048 2.2937-3.918 4.5377l0.08 1.4793c-2.2988 1.8591-4.6577 3.6382-6.7166 5.7571-1.4992 1.7391-3.6001 2.4358-4.9194 4.2949-18.171 12.514-26.665 47.839-54.451 36.405-15.692 4.4978-22.805 29.32-43.678 26.348-20.97 4.1179-37.833 2.5131-53.196 19.117-20.423 10.551-41.26 21.274-62.213 34.402-0.91954-0.06-8.0141 4.1383-8.0141 4.1383-3.4982-0.02-8.8093 1.3578-14.693 2.5006-0.95952 0.1199-11.211 3.5857-13.17 5.1049-9.7951 4.5177-31.448 6.3716-42.903 7.136-15.387 0.06-17.911 0.9995-20.31 1.6792-7.6474-1.6662-15.552 5.5938-33.081 6.171-5.6572 2.7986-26.658 0.6834-31.955 4.1017-1.919 0.5997-19.879 4.8976-21.758 5.5972-5.6972 1.8791-19.487 11.98-27.843 20.955-0.63968 0.2799-29.51 15.145-30.13 15.425-4.2179 1.0636-78.078 20.785-82.099 23.465-14.054 6.5141-24.608 7.9605-41.621 15.152l-42.579 14.099c-12.943 5.5701-34.336 24.213-40.613 35.148-18.926 17.802-41.209 3.3252-62.534 42.295-14.751 18.854-24.309 23.353-37.76 47.136-2.4388 0.7796-4.0557 2.5613-6.5145 3.341-1.4193 0.06-6.7996 1.2522-6.7996 1.2522 495.43 0.8909 498.58 0.1359 989.12-1.6328z" fill="url(#linearGradient4466)"/>
 <g fill="#9a4420" transform="matrix(1.7345 0 0 .96105 -15.506 -5.3903)" fill-opacity=".65373">
  <g fill="#000" transform="translate(-25.864 -9.6799)" fill-opacity="1">
   <path d="m57.75 21.178c28.05-0.08 56.09 0.01 84.14-0.04-0.01 0.74-0.01 2.22-0.02 2.96-1.38 0.05-2.76 0.1-4.15 0.16 0.05 5.53 0.23 11.07-0.18 16.59-1.5-0.71-2.35-2.08-2.21-3.74-0.18-4.29 0.01-8.6 0.03-12.89-1.82-0.02-3.65-0.03-5.48-0.04 0.02 5.32 0.01 10.64 0.02 15.96-0.58-0.01-1.74-0.05-2.31-0.06-0.03-2.32-0.05-4.63-0.07-6.95-2.16 0.03-4.33 0.07-6.49 0.11-1.13 1.83-1.63 4.94-4.34 4.92-2.82 0.06-4.02-3.34-3.12-5.63 1.31-1.29 2.88-2.28 4.13-3.63 0.29-1.56 0.35-3.14 0.48-4.72-3.56-0.02-7.11-0.02-10.66-0.02 0.04 3.72-0.15 7.57-2.27 10.77 1.84 1.98 3.56 4.12 4.7 6.59-4.66-2.22-8.3-6.28-10.36-10.98 1.72 0.57 3.45 1.11 5.18 1.65 0.19-2.67 0.33-5.33 0.47-8-3.29-0.03-6.57-0.04-9.85-0.03-0.04 5.3-0.04 10.59 0.01 15.89-0.55 0.03-1.66 0.08-2.21 0.11-0.04-5.31-0.07-10.61 0.03-15.92-1.73-0.02-3.46-0.03-5.19-0.04-0.14 3.47 0.62 7.21-0.76 10.5-2.16 2.89-7.23 1.1-6.94-2.57-0.31-3.03 3.17-3.66 5.3-4.52 0.07-1.13 0.14-2.26 0.21-3.4-3.48-0.05-6.97-0.06-10.45-0.06-0.04 5.31-0.04 10.61 0.02 15.92-0.56 0.01-1.68 0.04-2.25 0.06 0.02-2.33 0.03-4.65 0.07-6.97-3.17-0.19-6.35 0.01-9.35 1.12 1.54 2.33 3.04 4.69 4.21 7.23-4.16-2.54-8.39-6.22-9.24-11.28 1.57 1.01 3.13 2.05 4.71 3.05 0.34-3.02 0.56-6.05 0.69-9.09-2.18-0.04-4.36-0.07-6.53-0.11 0.01-0.73 0.02-2.17 0.03-2.9m8.66 2.94c-0.02 2.02-0.03 4.05-0.05 6.07 2.29-0.05 4.58-0.1 6.87-0.16-0.02-1.92-0.02-3.84 0-5.76-2.27-0.06-4.54-0.1-6.82-0.15m53.99 0.04c-0.01 1.99-0.02 3.98-0.01 5.98l7.17-0.03c-0.01-1.97-0.01-3.95 0-5.92-2.39-0.01-4.78-0.02-7.16-0.03m-37.49 7.19c-1.19 1.5 1.44 3 2.42 1.57 1.2-1.5-1.45-3-2.42-1.57m32.91 1.98c-0.52 1.62 0.04 2.16 1.69 1.62 0.51-1.61-0.05-2.15-1.69-1.62z"/>
   <path d="m142.67 25.068c-0.29-4.7 6.79-5.06 8.29-1.18 1.66 3.64-1.23 6.86-3.36 9.49 2.58-0.31 5.45-0.12 7.67-1.72 1.58-3.58-0.1-7.52-2.3-10.42 5.54-0.13 11.09-0.11 16.64-0.05 0.02 0.71 0.05 2.14 0.06 2.86-1.43 0.06-2.86 0.11-4.28 0.17-0.03 5.29-0.03 10.58 0 15.87-0.61-0.02-1.83-0.05-2.44-0.06 0.06-5.3 0.06-10.59-0.01-15.88-1.67 0.03-3.33 0.07-4.99 0.11 0.14 5.29 0.09 10.59 0.08 15.89-0.57-0.02-1.7-0.04-2.26-0.06 0.01-1.86 0.02-3.72 0.03-5.57-2.24 0.68-4.51 1.89-6.91 1.41-2.68-0.31-4.63-2.31-6.71-3.81 2.73-0.81 5.28-2.12 7.27-4.19-2.37-0.24-6.67 0.7-6.78-2.86m2.69-0.74c-0.41 1.43 2.01 1.82 2.52 0.64 0.4-1.43-2.01-1.81-2.52-0.64z"/>
  </g>
 </g>
 <g transform="matrix(.52131 .17864 -.17864 .52131 1056.9 25.253)">
  <g transform="matrix(1.0685 -.36616 .36616 1.0685 -7.5294 -3.63)">
   <path stroke-linejoin="round" d="m31.062-20.323 10.172 3.9753c4.474 2.6387 8.1185 4.5215 13.331 6.2471 6.3893 1.3105 9.3354-0.36322 13.889-0.92005l12.409-4.037-20.064 19.121c-6.921 6.876-17.424 12.49-26.353 10.593-6.827-5.7392-15.495 0.623-22.598 1.68-2.0317-10.883-1.2-21.791-0.836-32.771 6.1285-2.7621 13.13-3.3213 20.05-3.5292" stroke="#000" stroke-linecap="round" stroke-width="2.8919" fill="#2b7d15"/>
   <path d="m-1.8383-21.002c2.6833 0.31198 5.358 0.65251 8.037 0.97869-1.6642 21.964 2.6934 43.893 1.0564 65.819l-3.6739 0.129c-3.3793-21.252-2.984-45.036-5.8106-65.657z"/>
  </g>
 </g>
 <g transform="matrix(.13759 0 0 .13759 116.4 477.94)" fill="#504416">
  <path d="m138.45 1.69c13.49-2.99 27.7 8.47 27.57 22.28 0.72 12.57-10.45 24.15-23.03 23.92-11.99 0.42-23.03-9.87-23.43-21.87-1.01-11.39 7.71-22.36 18.89-24.33z"/>
  <path d="m84.34 51.44c4.39-0.86 9.79-1.32 13.3 1.98 3.2 3.27 2.04 8.26 0.92 12.18-5.41 16.64-10.7 33.33-16.02 50-1.32 4.13-3.92 8.19-8.17 9.75-6.72 2.73-14.02 0.25-20.4-2.3-4.85-2.01-9.93-4.89-12.13-9.93-2.07-4.95-0.82-10.52 0.85-15.4 4.51-12.37 12.54-23.08 21.02-33 5.24-6.47 12.41-11.51 20.63-13.28z"/>
  <path d="m110.37 65.39c1.12-3.43 2.65-7.92 6.75-8.54 4.29-0.18 8.36 1.49 12.45 2.55 6.92 2.1 14.43 3.18 20.35 7.64 6.54 4.82 13.12 9.58 19.62 14.45 2.79 1.99 5.37 4.48 8.66 5.63 6.35-1.61 12.25-4.91 17.83-8.31 0.49-5.42-0.25-10.92 0.66-16.29 0.81-4.61 8.21-5.3 9.9-1.01 1.06 3.8 0.76 7.81 1.01 11.71 2.86 0.07 5.79-0.17 8.6 0.56 2.6 1.37 3.85 4.97 2.34 7.59-2.28 4.59-7.36 6.7-10.43 10.61-1.39 4.16-0.59 8.7-0.73 13.02 0.14 47.35-0.07 94.71 0.11 142.05-0.01 3.12-1.02 6.09-2.14 8.95h-6.73c-1.54-2.72-2.48-5.78-2.46-8.92 0.21-47.03-0.02-94.06 0.13-141.08-0.03-2.35-0.12-4.69-0.26-7.04-6.02 2.75-11.06 7.23-17.11 9.93-3.95 1.78-8.34 0.12-11.7-2.15-7.93-5.31-15.2-11.56-23.3-16.64-3.46 11.27-5.61 22.88-8.61 34.27-1.1 5.13-3.19 10.14-3.22 15.44 0.98 2.49 3.12 4.27 4.93 6.17 7.51 7.14 14.72 14.61 22.2 21.79 3.02 3.02 6.35 6.24 7.21 10.61 0.91 5.01 0 10.11-0.93 15.05-2.95 14.81-5.72 29.66-8.58 44.49-1.23 5.23-2.32 10.93-6.09 15.01-2.98 3.35-8.81 1.4-10.09-2.61-1.84-5.56-1.34-11.55-0.96-17.3 1.09-11.23 2.34-22.44 3.61-33.65 0.19-2.28 0.5-4.6 0.08-6.87-0.97-1.93-2.71-3.31-4.29-4.71-11.2-9.09-22.08-18.56-33.21-27.73-5.93-5-11.85-11.11-13.08-19.1-1.37-9.49 1.72-18.82 4.22-27.85 4.47-15.9 8.86-31.81 13.26-47.72z"/>
  <path d="m89.35 160.99c6.27 8.64 14.54 15.44 23.18 21.57-1.05 6.98-3.45 13.79-7.21 19.77-6.02 9.89-12.4 19.56-18.65 29.31-4.06 6.14-8.11 12.48-13.87 17.19-2.33 1.87-5.33 3.48-8.41 2.78-1.37-0.33-3.02-1.26-3.08-2.84-0.47-4.91 1.67-9.53 3.53-13.93 5.7-12.62 11.65-25.14 17.18-37.84 5.55-11.18 5.06-23.99 7.33-36.01z"/>
 </g>
 <path d="m1057.2 50.349c-5.9261-0.19915-6.5417 9.3784-0.6387 9.9375 5.6511 1.1718 8.0445-7.8065 2.5527-9.6035-0.6101-0.2281-1.2622-0.34955-1.914-0.33399zm-76.131 51.367c-5.9254-0.19866-6.5403 9.3766-0.63868 9.9375 5.6501 1.1706 8.046-7.804 2.5547-9.6035-0.61129-0.22932-1.2625-0.3516-1.916-0.33398zm-76.126 50.76c-5.8004-0.096-6.5105 9.3609-0.60742 9.9356 5.6569 1.1955 8.0095-7.833 2.5078-9.6328-0.29368-0.087-0.90855-0.24053-1.3066-0.2715zm-76.032 46.16c-5.9232-0.2159-6.5646 9.3581-0.66601 9.9355 5.6565 1.1914 7.9132-7.9427 2.5996-9.6015-0.60548-0.2283-1.2388-0.3525-1.8868-0.334zm-76.092 27.68c-5.9155-0.197-6.5444 9.3594-0.65235 9.9355 5.6527 1.1908 8.0693-7.801 2.5684-9.5976-0.60895-0.2342-1.2636-0.3528-1.916-0.3379zm-76.078 35.068c-5.9263-0.2007-6.5456 9.3768-0.64258 9.9395 6.3208 1.2698 7.9234-9.2135 1.5039-9.8809-0.28469-0.045-0.57323-0.067-0.86133-0.059zm-76.082 11.752c-5.9258-0.2004-6.5411 9.3788-0.63867 9.9375 5.6522 1.1738 8.0483-7.8062 2.5547-9.6035-0.61127-0.229-1.2626-0.3517-1.916-0.334zm-76.088 14.539c-5.9251-0.1999-6.5441 9.3751-0.64258 9.9394 5.6522 1.1728 7.9246-7.883 2.4316-9.6836-0.61068-0.229-1.0893-0.24203-1.6954-0.25578zm-76.068 41.191c-5.9339-0.218-6.5633 9.3776-0.65234 9.9375 5.6514 1.1724 8.0478-7.806 2.5547-9.6036-0.60679-0.2279-1.2536-0.3501-1.9023-0.3339zm-76.094 23.199c-5.9154-0.2015-6.5461 9.3607-0.6543 9.9355 5.657 1.1936 8.0703-7.8021 2.5684-9.6015-0.61065-0.2288-1.2613-0.3515-1.9141-0.334zm-76.064 25.871c-5.925-0.2191-6.569 9.3608-0.66602 9.9336 5.6539 1.1904 8.0655-7.8005 2.5664-9.5996-0.60613-0.2247-1.2212-0.3544-1.8692-0.334zm-76.105 50.268c-5.9245-0.1972-6.5432 9.378-0.64063 9.9394 6.3221 1.2699 7.9233-9.216 1.502-9.8809-0.28469-0.045-0.57323-0.067-0.86133-0.058zm-76.08 78.33c-5.9257-0.1988-6.5408 9.3792-0.63867 9.9395 6.3184 1.2648 7.9192-9.2122 1.502-9.8809-0.28532-0.046-0.57454-0.067-0.86328-0.059z" stroke="#000" stroke-width="1.8" fill="url(#linearGradient4475)"/>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="15px" y="507.18439" x="167.25752" font-family="sans-serif" line-height="125%" fill="#000000"><tspan style="letter-spacing:0px" font-size="20px" y="507.18439" x="167.25752" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff">1317 Kathmandu</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="15px" y="1332.8939" x="389.13068" font-family="sans-serif" line-height="125%" fill="#000000"><tspan y="1332.8939" x="389.13068"/></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="1303.772" x="374.35864" font-family="&apos;Fira Sans&apos;" line-height="125%" fill="#000000"><tspan y="1303.772" x="374.35864"/></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="447.98709" x="228.09822" font-family="&apos;Fira Sans&apos;" line-height="125%" fill="#000000"><tspan style="letter-spacing:0px" font-size="20px" y="447.98709" x="228.09822" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff">2610 Phakding</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="397.5148" x="302.8645" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff"><tspan style="letter-spacing:0px" font-size="20px" y="397.5148" x="302.8645" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff">3440 Namche Bazaar</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="128.60736" x="977.59131" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan font-size="20px" y="128.60736" x="977.59131" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff">8000 Camp 4</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="166.5094" x="914.02338" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="166.5094" x="914.02338" font-size="20px" fill="#ffffff">7162 Camp 3</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="22.5px" y="212.1709" x="846.87421" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="212.1709" x="846.87421" font-size="20px" fill="#ffffff">6400 Camp 2</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="58.17897" x="1077.7659" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="58.17897" x="1077.7659">8848</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="75.905479" x="1089.5835" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="75.905479" x="1089.5835">Everest</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="244.10388" x="764.20593" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff"><tspan y="244.10388" x="764.20593">5943 Camp 1</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="273.35135" x="705.26385" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff"><tspan y="273.35135" x="705.26385">5364 Base Camp</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="294.54056" x="608.86737" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="294.54056" x="608.86737" fill="#ffffff">5170 Gorokshep</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="312.59622" x="524.11011" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="312.59622" x="524.11011" fill="#ffffff">4930 Lobuche</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="347.66324" x="456.21469" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#000000"><tspan y="347.66324" x="456.21469" fill="#ffffff">4250 Pheriche</tspan></text>
 <text style="word-spacing:0px;letter-spacing:0px" xml:space="preserve" font-size="20px" y="370.34464" x="382.49976" font-family="&apos;Open Sans&apos;" line-height="125%" fill="#ffffff"><tspan y="370.34464" x="382.49976">3867 Tengboche</tspan></text>
</svg>"""
        x = y = 0
        for n, uno in enumerate(self.li_points):
            c_svg = c_svg.replace(uno[0], uno[4])
            c_h = uno[1]
            if height == c_h:
                x = uno[2]
                y = uno[3]
                break
            elif height < c_h:
                n_0, h_0, x_0, y_0, n_t1 = self.li_points[n - 1]
                n_1, h_1, x_1, y_1, n_t2 = self.li_points[n]
                porc = (height - h_0) * 1.0 / (h_1 - h_0)
                x = (x_1 - x_0) * porc + x_0
                y = y_0 - (y_0 - y_1) * porc
                break

        n_0, h_0, x_0, y_0, n_1 = self.li_points[0]
        x_base, y_base = 116.4, 477.94
        x_dif = x_base - x_0
        y_dif = y_base - y_0
        x += x_dif
        y += y_dif

        nv = "%0.02f %0.02f" % (x, y)
        return c_svg.replace("116.4 477.94", nv).encode("utf-8")

    def svg(self, distribution, done_game):
        num_game = done_game + 1

        for tramo, num in enumerate(distribution):
            if num_game <= num:
                n_0, h_0, x_0, y_0, n_t1 = self.li_points[tramo]
                n_1, h_1, x_1, y_1, n_t2 = self.li_points[tramo + 1]
                h = h_0 + (h_1 - h_0) * num_game / num
                return h, self._svg(h)
            num_game -= num
