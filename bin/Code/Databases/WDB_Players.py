import FasterCode
from PySide2 import QtWidgets, QtCore

import Code
from Code.Base import Game
from Code.Openings import OpeningsStd
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios

OPENINGS_WHITE, OPENINGS_BLACK, MOVES_WHITE, MOVES_BLACK = range(4)


class ToolbarMoves(QtWidgets.QWidget):
    def __init__(self, side, rutina):
        QtWidgets.QWidget.__init__(self)

        self.dispatch = rutina
        self.side = side
        self.setFont(Controles.TipoLetra())

        ancho = 54

        bt_all = Controles.PB(self, _("All"), self.run_all, plano=False).anchoFijo(ancho + 16)
        bt_e4 = Controles.PB(self, "e4", self.run_e4, plano=False).anchoFijo(ancho)
        bt_d4 = Controles.PB(self, "d4", self.run_d4, plano=False).anchoFijo(ancho)
        bt_c4 = Controles.PB(self, "c4", self.run_c4, plano=False).anchoFijo(ancho)
        bt_nf3 = Controles.PB(self, "Nf3", self.run_nf3, plano=False).anchoFijo(ancho)
        bt_other = Controles.PB(self, _("Others"), self.run_other, plano=False).anchoFijo(ancho + 16)

        ply1 = Controles.PB(self, "^1", self.run_p1, plano=False).anchoFijo(ancho)
        ply2 = Controles.PB(self, "^2", self.run_p2, plano=False).anchoFijo(ancho)
        ply3 = Controles.PB(self, "^3", self.run_p3, plano=False).anchoFijo(ancho)
        ply4 = Controles.PB(self, "^4", self.run_p4, plano=False).anchoFijo(ancho)
        ply5 = Controles.PB(self, "^5", self.run_p5, plano=False).anchoFijo(ancho)

        self.sbply = Controles.SB(self, 0, 0, 100)
        self.sbply.capture_changes(self.run_p)
        lbply = Controles.LB(self, _("Half-moves"))

        layout = Colocacion.H().relleno(1).control(bt_all)
        layout.control(bt_e4).control(bt_d4).control(bt_c4).control(bt_nf3).control(bt_other).relleno(1)
        layout.control(ply1).control(ply2).control(ply3).control(ply4).control(ply5)
        layout.control(lbply).control(self.sbply).relleno(1).margen(0)

        self.setLayout(layout)

    def run_all(self):
        self.dispatch(self.side, "all")

    def run_e4(self):
        self.dispatch(self.side, "e2e4")

    def run_d4(self):
        self.dispatch(self.side, "d2d4")

    def run_c4(self):
        self.dispatch(self.side, "c2c4")

    def run_nf3(self):
        self.dispatch(self.side, "g1f3")

    def run_other(self):
        self.dispatch(self.side, "other")

    def run_p1(self):
        self.dispatch(self.side, "p1")

    def run_p2(self):
        self.dispatch(self.side, "p2")

    def run_p3(self):
        self.dispatch(self.side, "p3")

    def run_p4(self):
        self.dispatch(self.side, "p4")

    def run_p5(self):
        self.dispatch(self.side, "p5")

    def run_p(self):
        v = self.sbply.valor()
        self.dispatch(self.side, "p%d" % v)


class WPlayer(QtWidgets.QWidget):
    def __init__(self, procesador, wb_database, dbGames):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.procesador = procesador
        self.data = [[], [], [], []]
        self.movesWhite = []
        self.movesBlack = []
        self.lastFilterMoves = {"white": "", "black": ""}
        self.configuration = procesador.configuration
        self.foreground = Code.dic_qcolors["SUMMARY_FOREGROUND"]

        self.infoMove = None  # <-- setInfoMove

        self.rebuilding = False

        self.ap = OpeningsStd.ap

        self.gridOpeningWhite = self.gridOpeningBlack = self.gridMovesWhite = self.gridMovesBlack = 0

        # GridOpening
        ancho = 54
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("opening", _("Opening"), 200)
        o_columns.nueva("games", _("Games"), ancho, align_right=True)
        o_columns.nueva("pgames", "% " + _("Games"), 70, align_right=True)
        o_columns.nueva("win", _("Win"), ancho, align_right=True)
        o_columns.nueva("draw", _("Draw"), ancho, align_right=True)
        o_columns.nueva("lost", _("Loss"), ancho, align_right=True)
        o_columns.nueva("pwin", "% " + _("Win"), ancho, align_right=True)
        o_columns.nueva("pdraw", "% " + _("Draw"), ancho, align_right=True)
        o_columns.nueva("plost", "% " + _("Loss"), ancho, align_right=True)
        o_columns.nueva("pdrawwin", "%% %s" % _("W+D"), ancho, align_right=True)
        o_columns.nueva("pdrawlost", "%% %s" % _("L+D"), ancho, align_right=True)

        self.gridOpeningWhite = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.gridOpeningBlack = Grid.Grid(self, o_columns, siSelecFilas=True)

        # GridWhite/GridBlack
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("games", _("Games"), ancho, align_right=True)
        o_columns.nueva("win", _("Win"), ancho, align_right=True)
        o_columns.nueva("draw", _("Draw"), ancho, align_right=True)
        o_columns.nueva("lost", _("Loss"), ancho, align_right=True)
        o_columns.nueva("pwin", "% " + _("Win"), ancho, align_right=True)
        o_columns.nueva("pdraw", "% " + _("Draw"), ancho, align_right=True)
        o_columns.nueva("plost", "% " + _("Loss"), ancho, align_right=True)

        ancho_col = 40
        with_figurines = self.configuration.x_pgn_withfigurines
        for x in range(1, 50):
            num = (x - 1) * 2
            o_columns.nueva(
                str(num),
                "%d." % x,
                ancho_col,
                align_center=True,
                edicion=Delegados.EtiquetaPOS(with_figurines, siLineas=False),
            )
            o_columns.nueva(
                str(num + 1),
                "...",
                ancho_col,
                align_center=True,
                edicion=Delegados.EtiquetaPOS(with_figurines, siLineas=False),
            )

        self.gridMovesWhite = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.gridMovesWhite.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.gridMovesBlack = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.gridMovesBlack.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)

        wWhite = QtWidgets.QWidget(self)
        tbmovesw = ToolbarMoves("white", self.dispatchMoves)
        ly = Colocacion.V().control(tbmovesw).control(self.gridMovesWhite).margen(3)
        wWhite.setLayout(ly)

        wblack = QtWidgets.QWidget(self)
        tbmovesb = ToolbarMoves("black", self.dispatchMoves)
        ly = Colocacion.V().control(tbmovesb).control(self.gridMovesBlack).margen(3)
        wblack.setLayout(ly)

        tabs = Controles.Tab(self)
        tabs.new_tab(self.gridOpeningWhite, _("White openings"))
        tabs.new_tab(self.gridOpeningBlack, _("Black openings"))
        tabs.new_tab(wWhite, _("White moves"))
        tabs.new_tab(wblack, _("Black moves"))

        # ToolBar
        liAccionesWork = [
            (_("Close"), Iconos.MainMenu(), wb_database.tw_terminar),
            None,
            ("", Iconos.Usuarios(), self.tw_changeplayer),
            None,
            (_("Rebuild"), Iconos.Reindexar(), self.tw_rebuild),
            None,
        ]

        self.tbWork = QTVarios.LCTB(self, liAccionesWork)
        self.tbWork.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        lyTB = Colocacion.H().control(self.tbWork)
        layout = Colocacion.V().otro(lyTB).control(tabs).margen(1)

        self.setLayout(layout)

        self.setdbGames(dbGames)
        self.setPlayer(self.leeVariable("PLAYER", ""))

    def dispatchMoves(self, side, opcion):
        dataSide = self.data[MOVES_WHITE if side == "white" else MOVES_BLACK]

        if opcion == "all":
            showData = range(len(dataSide))

        elif opcion in ("e2e4", "d2d4", "c2c4", "g1f3"):
            showData = [n for n in range(len(dataSide)) if dataSide[n]["pv"].startswith(opcion)]

        elif opcion == "other":
            showData = [
                n
                for n in range(len(dataSide))
                if not dataSide[n]["pv"].startswith("e2e4")
                   and not dataSide[n]["pv"].startswith("d2d4")
                   and not dataSide[n]["pv"].startswith("c2c4")
                   and not dataSide[n]["pv"].startswith("g1f3")
            ]

        else:  # if opcion.startswith("p"):
            num = int(opcion[1:])
            if num == 0:
                return self.dispatchMoves(side, "all")
            if self.lastFilterMoves[side].startswith("p"):
                showDataPrevio = range(len(dataSide))
            else:
                showDataPrevio = self.movesWhite if side == "white" else self.movesBlack
            showData = [n for n in showDataPrevio if dataSide[n]["pv"].count(" ") < num]

        if side == "white":
            self.movesWhite = showData
            self.gridMovesWhite.refresh()

        else:
            self.movesBlack = showData
            self.gridMovesBlack.refresh()

        self.lastFilterMoves[side] = opcion

    def setdbGames(self, dbGames):
        self.dbGames = dbGames
        self.setPlayer(self.leeVariable("PLAYER", ""))

    def setPlayer(self, player):
        self.player = player
        self.data = [[], [], [], []]
        accion = self.tbWork.li_acciones[1]
        accion.setIconText(self.player if self.player else _("Player"))

        self.gridOpeningWhite.refresh()
        self.gridOpeningBlack.refresh()
        self.gridMovesWhite.refresh()
        self.gridMovesBlack.refresh()
        self.gridOpeningWhite.setFocus()

    def setInfoMove(self, infoMove):
        self.infoMove = infoMove

    def dataGrid(self, grid):
        if grid == self.gridOpeningWhite:
            return self.data[OPENINGS_WHITE]
        elif grid == self.gridOpeningBlack:
            return self.data[OPENINGS_BLACK]
        elif grid == self.gridMovesWhite:
            return self.data[MOVES_WHITE]
        elif grid == self.gridMovesBlack:
            return self.data[MOVES_BLACK]

    def grid_num_datos(self, grid):
        if self.rebuilding:
            return 0
        if grid == self.gridOpeningWhite:
            return len(self.data[OPENINGS_WHITE])
        elif grid == self.gridOpeningBlack:
            return len(self.data[OPENINGS_BLACK])
        elif grid == self.gridMovesWhite:
            return len(self.movesWhite)
        elif grid == self.gridMovesBlack:
            return len(self.movesBlack)
        else:
            return 0

    def grid_dato(self, grid, nfila, ocol):
        if self.rebuilding:
            return ""
        key = ocol.key
        dt = self.dataGrid(grid)
        if grid == self.gridMovesWhite:
            nfila = self.movesWhite[nfila]
        elif grid == self.gridMovesBlack:
            nfila = self.movesBlack[nfila]
        return dt[nfila][key]

    def grid_cambiado_registro(self, grid, nfila, oCol):
        dt = self.dataGrid(grid)
        if grid == self.gridMovesWhite:
            nfila = self.movesWhite[nfila]
        elif grid == self.gridMovesBlack:
            nfila = self.movesBlack[nfila]
        if len(dt) > nfila >= 0:
            game = dt[nfila]["game"]
            if game is None:
                pv = dt[nfila]["pv"]
                game = Game.Game()
                game.read_pv(pv)
            self.infoMove.modoPartida(game, len(game) - 1)
            grid.setFocus()

    def grid_color_fondo(self, grid, nfila, ocol):
        dt = self.dataGrid(grid)
        if not dt:
            return
        if grid == self.gridMovesWhite:
            nfila = self.movesWhite[nfila]
        elif grid == self.gridMovesBlack:
            nfila = self.movesBlack[nfila]
        key = ocol.key + "c"
        color = dt[nfila].get(key, 99)
        if color == 0:
            return Code.dic_qcolors["SUMMARY_WIN"]
        if color == 2:
            return Code.dic_qcolors["SUMMARY_LOST"]

    def grid_color_texto(self, grid, nfila, ocol):
        dt = self.dataGrid(grid)
        if dt and self.foreground:
            key = ocol.key + "c"
            color = dt[nfila].get(key)
            if color:
                return self.foreground

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            self.infoMove.tecla_pulsada(k)
            row, col = grid.posActualN()
            if QtCore.Qt.Key_Right:
                if col > 0:
                    col -= 1
            elif QtCore.Qt.Key_Left:
                if col < len(grid.columnas().li_columns) - 1:
                    col += 1
            grid.goto(row, col)
        elif k == QtCore.Qt.Key_Home:
            grid.gotop()
        elif k == QtCore.Qt.Key_End:
            grid.gobottom()
        else:
            return True  # que siga con el resto de teclas

    def leeVariable(self, var, default=None):
        return self.dbGames.read_config(var, default)

    def escVariable(self, var, valor):
        self.dbGames.save_config(var, valor)

    def listaPlayers(self):
        return self.leeVariable("LISTA_PLAYERS", [])

    def rereadPlayers(self):
        um = QTUtil2.one_moment_please(self)
        lista = self.dbGames.players()
        self.escVariable("LISTA_PLAYERS", lista)
        um.final()

    def change_player(self, lp):
        li_gen = []
        lista = [(player, player) for player in lp]
        lista.insert(0, ("", ""))
        config = FormLayout.Combobox(_("Name"), lista, extend_seek=True)
        li_gen.append((config, self.leeVariable("PLAYER", "")))

        for nalias in range(1, 4):
            li_gen.append(FormLayout.separador)
            config = FormLayout.Combobox("%s %d" % (_("Alias"), nalias), lista, extend_seek=True)
            li_gen.append((config, self.leeVariable("ALIAS%d" % nalias, "")))

        resultado = FormLayout.fedit(li_gen, title=_("Player"), parent=self, anchoMinimo=200, icon=Iconos.Player())
        if resultado is None:
            return
        accion, li_gen = resultado
        name, alias1, alias2, alias3 = li_gen
        if not name:
            return
        self.escVariable("PLAYER", name)
        self.escVariable("ALIAS1", alias1)
        self.escVariable("ALIAS2", alias2)
        self.escVariable("ALIAS3", alias3)
        self.setPlayer(name)
        self.tw_rebuild()

    def test_players_in_db(self):
        if self.dbGames.has_field("WHITE") and self.dbGames.has_field("BLACK"):
            return True
        QTUtil2.message(self, _("This database has no players"))
        return False

    def tw_changeplayer(self):
        if not self.test_players_in_db():
            return
        lp = self.listaPlayers()
        if len(lp) == 0:
            self.rereadPlayers()
            lp = self.listaPlayers()
            if len(lp) == 0:
                return None

        menu = QTVarios.LCMenu(self)
        menu.opcion("change", _("Change"), Iconos.ModificarP())
        menu.separador()
        menu.opcion("reread", _("Reread the players list"), Iconos.Reindexar())

        resp = menu.lanza()
        if resp == "change":
            self.change_player(lp)

        elif resp == "reread":
            self.rereadPlayers()

    def tw_rebuild(self):
        if not self.test_players_in_db():
            return

        self.rebuilding = True
        pb = QTUtil2.BarraProgreso1(self, _("Working..."), formato1="%p%")
        pb.mostrar()
        liFields = ["RESULT", "XPV", "WHITE", "BLACK"]
        dicOpenings = {"white": {}, "black": {}}
        dicMoves = {"white": {}, "black": {}}
        dic_hap = {}
        name = self.player
        alias1 = self.leeVariable("ALIAS1")
        alias2 = self.leeVariable("ALIAS2")
        alias3 = self.leeVariable("ALIAS3")

        liplayer = (name, alias1, alias2, alias3)

        filtro = "WHITE = '%s' or BLACK = '%s'" % (name, name)
        for alias in (alias1, alias2, alias3):
            if alias:
                filtro += "or WHITE = '%s' or BLACK = '%s'" % (alias, alias)
        pb.set_total(self.dbGames.count_data(filtro))

        for n, alm in enumerate(self.dbGames.yield_data(liFields, filtro)):
            pb.pon(n)
            if pb.is_canceled():
                self.rebuilding = False
                return
            result = alm.RESULT
            if result in ("1-0", "0-1", "1/2-1/2"):
                white = alm.WHITE
                black = alm.BLACK

                resultw = "win" if result == "1-0" else ("lost" if result == "0-1" else "draw")
                resultb = "win" if result == "0-1" else ("lost" if result == "1-0" else "draw")

                if white in liplayer:
                    side = "white"
                    result = resultw
                elif black in liplayer:
                    side = "black"
                    result = resultb
                else:
                    continue
                xpv = alm.XPV
                if not xpv or "|" in xpv:
                    continue

                # openings
                ap = self.ap.base_xpv(xpv)
                hap = hash(ap)
                dco = dicOpenings[side]
                if not (hap in dic_hap):
                    dic_hap[hap] = ap
                if not (hap in dco):
                    dco[hap] = {"win": 0, "draw": 0, "lost": 0}
                dco[hap][result] += 1

                # moves
                listapvs = FasterCode.xpv_pv(xpv).split(" ")
                dcm = dicMoves[side]
                pvt = ""
                for pv in listapvs:
                    if pvt:
                        pvt += " " + pv
                    else:
                        pvt = pv
                    if not (pvt in dcm):
                        dcm[pvt] = {"win": 0, "draw": 0, "lost": 0, "games": 0}
                    dcm[pvt][result] += 1
                    dcm[pvt]["games"] += 1

        pb.close()

        um = QTUtil2.one_moment_please(self, _("Working..."), physical_pos="ad")

        def color3(x, y, z):
            if x > y and x > z:
                return 0
            if x < y and x < z:
                return 2
            return 1

        def color2(x, y):
            if x > y:
                return 0
            if x < y:
                return 2
            return 1

        def z(x):
            return "%0.2f" % x

        color = None
        info = None
        indicadorInicial = None
        li_nags = []
        siLine = False

        data = [[], [], [], []]
        for side in ("white", "black"):
            dtemp = []
            tt = 0
            for hap in dicOpenings[side]:
                dt = dicOpenings[side][hap]
                win, draw, lost = dt["win"], dt["draw"], dt["lost"]
                t = win + draw + lost
                tt += t
                ap = dic_hap[hap]
                dic = {
                    "opening": ap.tr_name,
                    "opening_obj": ap,
                    "games": t,
                    "win": win,
                    "draw": draw,
                    "lost": lost,
                    "pwin": z(win * 100.0 / t),
                    "pdraw": z(draw * 100.0 / t),
                    "plost": z(lost * 100.0 / t),
                    "pdrawlost": z((draw + lost) * 100.0 / t),
                    "pdrawwin": z((win + draw) * 100.0 / t),
                    "winc": color3(win, draw, lost),
                    "pwinc": color3(win, draw, lost),
                    "drawc": color3(draw, win, lost),
                    "pdrawc": color3(draw, win, lost),
                    "lostc": color3(lost, win, draw),
                    "plostc": color3(lost, win, draw),
                    "pdrawlostc": color2(draw + lost, draw + win),
                    "pdrawwinc": color2(draw + win, draw + lost),
                }
                p = Game.Game()
                p.read_pv(ap.a1h8)
                dic["game"] = p
                dtemp.append(dic)

            for draw in dtemp:
                draw["pgames"] = z(draw["games"] * 100.0 / tt)
            dtemp.sort(key=lambda x: "%5d%s" % (99999 - x["games"], x["opening"]), reverse=False)
            if side == "white":
                data[OPENINGS_WHITE] = dtemp
            else:
                data[OPENINGS_BLACK] = dtemp

            # moves
            dtemp = []
            dc = dicMoves[side]
            st_rem = set()

            listapvs = list(dicMoves[side].keys())
            listapvs.sort()

            sipar = 1 if side == "white" else 0

            for pv in listapvs:
                if dc[pv]["games"] == 1:
                    lipv = pv.split(" ")
                    nlipv = len(lipv)
                    if nlipv > 1:
                        pvant = " ".join(lipv[:-1])
                        if pvant in st_rem or dc[pvant]["games"] == 1 and (nlipv) % 2 == sipar:
                            st_rem.add(pv)

            for pv in st_rem:
                del dc[pv]

            listapvs = list(dicMoves[side].keys())
            listapvs.sort()
            antlipv = []
            for npv, pv in enumerate(listapvs):
                dt = dicMoves[side][pv]
                win, draw, lost = dt["win"], dt["draw"], dt["lost"]
                t = win + draw + lost
                tt += t
                lipv = pv.split(" ")
                nli = len(lipv)
                dic = {
                    "pv": pv,
                    "games": t,
                    "win": win,
                    "draw": draw,
                    "lost": lost,
                    "pwin": z(win * 100.0 / t),
                    "pdraw": z(draw * 100.0 / t),
                    "plost": z(lost * 100.0 / t),
                    "pdrawlost": z((draw + lost) * 100.0 / t),
                    "pdrawwin": z((win + draw) * 100.0 / t),
                    "nivel": nli,
                    "game": None,
                }
                li_pgn = Game.lipv_lipgn(lipv)
                nliant = len(antlipv)
                agrisar = True
                for x in range(100):
                    iswhite = (x % 2) == 0
                    pgn = li_pgn[x] if x < nli else ""
                    if agrisar:
                        if x >= nliant:
                            agrisar = False
                        elif x < nli:
                            if lipv[x] != antlipv[x]:
                                agrisar = False
                    dic[str(x)] = pgn, iswhite, color, info, indicadorInicial, li_nags, agrisar, siLine
                antlipv = lipv
                dic["winc"] = dic["pwinc"] = color3(win, draw, lost)
                dic["drawc"] = dic["pdrawc"] = color3(draw, win, lost)
                dic["lostc"] = dic["plostc"] = color3(lost, win, draw)
                dic["pdrawlostc"] = color2(draw + lost, draw + win)
                dic["pdrawwinc"] = color2(draw + win, draw + lost)
                dtemp.append(dic)

            liorder = []

            def ordena(empieza, nivel):
                li = []
                for n, uno in enumerate(dtemp):
                    if uno["nivel"] == nivel and uno["pv"].startswith(empieza):
                        li.append(uno)
                li.sort(key=lambda x: "%5d%5d" % (x["games"], x["win"]), reverse=True)
                for uno in li:
                    liorder.append(uno)
                    ordena(uno["pv"], nivel + 1)

            ordena("", 1)
            if side == "white":
                data[MOVES_WHITE] = liorder
                self.movesWhite = range(len(liorder))
            else:
                data[MOVES_BLACK] = liorder
                self.movesBlack = range(len(liorder))

        um.final()

        self.rebuilding = False
        self.data = data
        self.gridOpeningWhite.refresh()
        self.gridOpeningBlack.refresh()
        self.gridMovesWhite.refresh()
        self.gridMovesBlack.refresh()

        self.gridOpeningWhite.gotop()
        self.gridOpeningBlack.gotop()
        self.gridMovesWhite.gotop()
        self.gridMovesBlack.gotop()
        self.gridOpeningWhite.setFocus()
