import os

import FasterCode
from PySide2 import QtWidgets, QtCore

from Code.Base import Game, Position
from Code.Books import Books, WBooks
from Code.Databases import WDB_Summary, DBgamesST, WDB_Games, DBgames
from Code.Openings import POLAnalisisTree
from Code.QT import Colocacion, FormLayout
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios


class TabEngine(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, procesador, configuration):
        QtWidgets.QWidget.__init__(self)

        self.analyzing = False
        self.position = None
        self.li_analysis = []
        self.manager_motor = None
        self.current_mrm = None
        self.pv = None

        self.dbop = tabsAnalisis.dbop

        self.procesador = procesador
        self.configuration = configuration

        self.with_figurines = configuration.x_pgn_withfigurines

        self.tabsAnalisis = tabsAnalisis
        self.bt_start = Controles.PB(self, "", self.start).ponIcono(Iconos.Pelicula_Seguir(), 32)
        self.bt_stop = Controles.PB(self, "", self.stop).ponIcono(Iconos.Pelicula_Pausa(), 32)
        self.bt_stop.hide()

        self.lb_engine = Controles.LB(self, _("Engine") + ":")
        list_engines = configuration.combo_engines()  # (name, key)
        default = configuration.x_tutor_clave
        engine = self.dbop.getconfig("ENGINE", default)
        if len([key for name, key in list_engines if key == engine]) == 0:
            engine = default
        self.cb_engine = Controles.CB(self, list_engines, engine).capture_changes(self.reset_motor)

        multipv = self.dbop.getconfig("ENGINE_MULTIPV", 5)
        lb_multipv = Controles.LB(self, _("Multi PV") + ": ")
        self.sb_multipv = Controles.SB(self, multipv, 1, 500).tamMaximo(50)

        self.lb_analisis = Controles.LB(self, "").set_font_type(puntos=configuration.x_pgn_fontpoints).set_wrap()
        self.configuration.set_property(self.lb_analisis, "pgn")

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("PDT", "", 120, align_center=True)
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        o_columns.nueva("SOL", "", 100, align_center=True, edicion=delegado)
        o_columns.nueva("PGN", _("Solution"), 860)

        self.grid_analysis = Grid.Grid(self, o_columns, siSelecFilas=True, altoCabecera=4)
        self.grid_analysis.font_type(puntos=configuration.x_pgn_fontpoints)
        self.grid_analysis.ponAltoFila(configuration.x_pgn_rowheight)
        # self.register_grid(self.grid_analysis)

        ly_lin1 = Colocacion.H().control(self.bt_start).control(self.bt_stop).control(self.lb_engine)
        ly_lin1.control(self.cb_engine)
        ly_lin1.espacio(50).control(lb_multipv).control(self.sb_multipv).relleno()
        ly = Colocacion.V().otro(ly_lin1).control(self.lb_analisis).control(self.grid_analysis).margen(3)

        self.setLayout(ly)

        self.reset_motor()

    def saveCurrent(self):
        if self.current_mrm:
            fenm2 = self.current_posicion.fenm2()
            dic = self.dbop.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                mrm_ant = dic["ANALISIS"]
                if mrm_ant.getdepth0() > self.current_mrm.getdepth0():
                    return
            dic["ANALISIS"] = self.current_mrm
            self.dbop.setfenvalue(fenm2, dic)

    def setData(self, label, position, pv):
        self.saveCurrent()
        self.position = position
        self.pv = pv
        self.lb_analisis.set_text(label)
        if self.analyzing:
            self.analyzing = False
            self.manager_motor.ac_final(0)
            game = Game.Game(self.position)
            self.manager_motor.ac_inicio(game)
            self.analyzing = True
            QtCore.QTimer.singleShot(1000, self.lee_analisis)
        else:
            fenm2 = position.fenm2()
            dic = self.dbop.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                self.show_analisis(dic["ANALISIS"])
            else:
                self.li_analysis = []
                self.grid_analysis.refresh()

    def start(self):
        self.current_mrm = None
        self.current_posicion = None
        self.sb_multipv.setDisabled(True)
        self.cb_engine.setDisabled(True)
        self.analyzing = True
        self.sb_multipv.setDisabled(True)
        self.show_stop()
        multipv = self.sb_multipv.valor()
        self.manager_motor.update_multipv(multipv)
        game = Game.Game(self.position)
        self.manager_motor.ac_inicio(game)
        QtCore.QTimer.singleShot(1000, self.lee_analisis)

    def show_start(self):
        self.bt_stop.hide()
        self.bt_start.show()

    def show_stop(self):
        self.bt_start.hide()
        self.bt_stop.show()

    def show_analisis(self, mrm):
        self.current_mrm = mrm
        self.current_posicion = self.position
        li = []
        for rm in mrm.li_rm:
            game = Game.Game(self.position)
            game.read_pv(rm.pv)
            pgn = game.pgnBaseRAW(translated=False)
            lit = pgn.split(" ")
            is_white = self.position.is_white
            if is_white:
                pgn0 = lit[0].split(".")[-1]
                pgn1 = " ".join(lit[1:])
            else:
                pgn0 = lit[1]
                pgn1 = " ".join(lit[2:])

            if self.with_figurines:
                game.ms_sol = pgn0, is_white, None, None, None, None, False, False
            else:
                game.ms_sol = pgn0
            game.ms_pgn = pgn1
            game.ms_pdt = rm.abbrev_text_pdt()
            li.append(game)
        self.li_analysis = li
        self.grid_analysis.refresh()

    def lee_analisis(self):
        if self.analyzing:
            mrm = self.manager_motor.ac_estado()
            self.show_analisis(mrm)
            QtCore.QTimer.singleShot(2000, self.lee_analisis)

    def stop(self):
        self.saveCurrent()
        self.sb_multipv.setDisabled(False)
        self.cb_engine.setDisabled(False)
        self.analyzing = False
        self.show_start()
        if self.manager_motor:
            self.manager_motor.ac_final(0)

    def reset_motor(self):
        self.saveCurrent()
        key = self.cb_engine.valor()
        if not key:
            return
        self.analyzing = False
        if self.manager_motor:
            self.manager_motor.terminar()
        self.stop()
        conf_engine = self.configuration.buscaRival(key)

        multipv = self.sb_multipv.valor()
        self.manager_motor = self.procesador.creaManagerMotor(conf_engine, 0, 0, has_multipv=multipv > 1)

    def grid_num_datos(self, grid):
        return len(self.li_analysis)

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "PDT":
            return self.li_analysis[row].ms_pdt
        elif o_column.key == "SOL":
            return self.li_analysis[row].ms_sol
        else:
            return self.li_analysis[row].ms_pgn

    def grid_right_button(self, grid, row, o_column, modif):
        if row < 0:
            return
        menu = QTVarios.LCMenu(self)
        menu.opcion("current", _("Add current"), Iconos.This())
        menu.separador()
        if len(self.li_analysis) > 1:
            menu.opcion("all", _("Add all"), Iconos.All())
            menu.separador()
            if row > 1:
                menu.opcion("previous", _("Add previous"), Iconos.Previous())
                menu.separador()
        menu.separador()
        menu.opcion("more", _("More options"), Iconos.More())
        tp = menu.lanza()
        if tp is None:
            return
        plies = 1
        if tp == "more":
            dic = self.configuration.read_variables("OL_ENGINE_VAR")
            tp = dic.get("TYPE", "current")
            plies = dic.get("PLIES", 1)

            form = FormLayout.FormLayout(self, _("More options"), Iconos.More())
            form.separador()
            li_options = [(_("Current"), "current")]
            if len(self.li_analysis) > 1:
                li_options.append((_("All"), "all"))
                if len(self.li_analysis) > 2 and row > 0:
                    li_options.append((_("Previous"), "previous"))
            form.combobox(_("Variations to add"), li_options, tp)
            form.separador()
            form.spinbox(_("Movements to add in each variation"), 0, 999, 50, plies)
            form.apart_simple_np("    %s = 0" % _("Full line"))
            form.separador()
            resp = form.run()
            if resp is None:
                return

            x, li_gen = resp
            tp, plies = li_gen
            dic = {"TYPE": tp, "PLIES": plies}
            self.configuration.write_variables("OL_ENGINE_VAR", dic)

        if tp == "current":
            lst_rows = [row]
        elif tp == "all":
            lst_rows = list(range(len(self.li_analysis)))
        else:
            lst_rows = list(range(row))

        refresh = False
        for row in lst_rows:
            g = self.li_analysis[row]
            if len(g) > 0:
                pv = self.pv
                if plies == 0:
                    pv += " " + g.pv()
                else:
                    for n in range(plies):
                        pv += " " + g.move(n).movimiento()
                if self.dbop.append_pv(pv.strip()):
                    refresh = True

        if refresh:
            self.tabsAnalisis.refresh_lines()

    def saveConfig(self):
        self.dbop.setconfig("ENGINE", self.cb_engine.valor())
        self.dbop.setconfig("ENGINE_MULTIPV", self.sb_multipv.valor())


class TabBook(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, book, configuration):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis
        self.position = None
        self.leido = False
        self.pv = None

        self.dbop = tabsAnalisis.dbop

        self.book = book
        book.polyglot()
        self.li_moves = []

        self.with_figurines = configuration.x_pgn_withfigurines

        o_columns = Columnas.ListaColumnas()
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        for x in range(20):
            o_columns.nueva(x, "", 80, align_center=True, edicion=delegado)
        self.grid_moves = Grid.Grid(
            self, o_columns, siSelecFilas=True, siCabeceraMovible=False, siCabeceraVisible=False
        )
        self.grid_moves.font_type(puntos=configuration.x_pgn_fontpoints)
        self.grid_moves.ponAltoFila(configuration.x_pgn_rowheight)

        ly = Colocacion.V().control(self.grid_moves).margen(3)

        self.setLayout(ly)

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, row, o_column):
        mv = self.li_moves[row]
        li = mv.dato
        key = int(o_column.key)
        pgn = li[key]
        if self.with_figurines:
            is_white = " w " in mv.fen
            return pgn, is_white, None, None, None, None, False, True
        else:
            return pgn

    def grid_doble_click(self, grid, row, o_column):
        alm_base = self.li_moves[row]
        if row != len(self.li_moves) - 1:
            alm_base1 = self.li_moves[row + 1]
            if alm_base.nivel < alm_base1.nivel:
                if self.borra_subnivel(row + 1):
                    self.grid_moves.refresh()
                return

        self.lee_subnivel(row)
        self.grid_moves.refresh()

    def grid_right_button(self, grid, row, column, modificadores):
        if row < 0:
            return
        menu = QTVarios.LCMenu(self)
        menu.opcion("current", _("Add current"), Iconos.This())
        menu.separador()

        if len(self.li_moves) > 1:
            menu.opcion("all", _("Add all"), Iconos.All())
            menu.separador()

            if row > 1:
                menu.opcion("previous", _("Add previous"), Iconos.Previous())
                menu.separador()

            slevel = set()
            for alm in self.li_moves:
                slevel.add(alm.nivel)
            if len(slevel) > 1:
                menu.opcion("level", _("Add all of current level"), Iconos.Arbol())
                menu.separador()

        resp = menu.lanza()
        if resp is None:
            return

        if resp == "all":
            lst_rows = list(range(len(self.li_moves)))
        elif resp == "previous":
            lst_rows = list(range(row))
        elif resp == "level":
            lst_rows = [row]
            lv = self.li_moves[row].nivel
            for r in range(row - 1, -1, -1):
                alm = self.li_moves[r]
                if alm.nivel == lv:
                    lst_rows.append(r)
                elif alm.nivel < lv:
                    break
            for r in range(row + 1, len(self.li_moves)):
                alm = self.li_moves[r]
                if alm.nivel == lv:
                    lst_rows.append(r)
                elif alm.nivel < lv:
                    break
        else:
            lst_rows = [row]

        refresh = False
        for row in lst_rows:
            pv = self.li_moves[row].pv
            lv = self.li_moves[row].nivel
            for r in range(row - 1, -1, -1):
                alm = self.li_moves[r]
                if alm.nivel < lv:
                    pv = alm.pv + " " + pv
                    lv = alm.nivel
            pv = self.pv + " " + pv
            if self.dbop.append_pv(pv.strip()):
                refresh = True

        if refresh:
            self.tabsAnalisis.refresh_lines()

    def setData(self, position, pv):
        self.position = position
        self.pv = pv
        self.start()

    def borra_subnivel(self, row):
        alm = self.li_moves[row]
        nv = alm.nivel
        if nv == 0:
            return False
        li = []
        for x in range(row, 0, -1):
            alm1 = self.li_moves[x]
            if alm1.nivel < nv:
                break
            li.append(x)
        for x in range(row + 1, len(self.li_moves)):
            alm1 = self.li_moves[x]
            if alm1.nivel < nv:
                break
            li.append(x)
        li.sort(reverse=True)
        for x in li:
            del self.li_moves[x]

        return True

    def lee_subnivel(self, row):
        alm_base = self.li_moves[row]
        if alm_base.nivel >= 17:
            return
        FasterCode.set_fen(alm_base.fen)
        if FasterCode.move_pv(alm_base.from_sq, alm_base.to_sq, alm_base.promotion):
            fen = FasterCode.get_fen()
            for alm in self.book.alm_list_moves(fen):
                nv = alm.nivel = alm_base.nivel + 1
                alm.dato = [""] * 20
                alm.dato[nv] = alm.pgn
                alm.dato[nv + 1] = alm.porc
                alm.dato[nv + 2] = "%d" % alm.weight
                row += 1
                self.li_moves.insert(row, alm)

    def lee(self):
        if not self.leido and self.position:
            fen = self.position.fen()
            self.li_moves = self.book.alm_list_moves(fen)
            for alm in self.li_moves:
                alm.nivel = 0
                alm.dato = [""] * 20
                alm.dato[0] = alm.pgn
                alm.dato[1] = alm.porc
                alm.dato[2] = "%d" % alm.weight
            self.leido = True

    def start(self):
        self.leido = False
        self.lee()
        self.grid_moves.refresh()

    def stop(self):
        pass


class TabDatabaseSummary(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, procesador, dbstat):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis

        self.pv = None

        self.dbstat = dbstat

        self.wsummary = WDB_Summary.WSummaryBase(procesador, dbstat)

        layout = Colocacion.H().control(self.wsummary)
        self.setLayout(layout)

    def setData(self, position, pv):
        self.pv = pv
        self.position = position
        self.wsummary.actualizaPV(self.pv)

    def start(self):
        self.wsummary.actualizaPV(self.pv)

    def stop(self):
        self.dbstat.close()


class InfoMoveReplace:
    def __init__(self, owner):
        self.tab_database = owner
        self.board = self.tab_database.tabsAnalisis.panelOpening.pboard.board

    def modoPartida(self, x, y):
        return True


class TabDatabase(QtWidgets.QWidget):
    def __init__(self, tabsAnalisis, procesador, db):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabsAnalisis
        self.is_temporary = False

        self.pv = None

        self.db = db

        self.wgames = WDB_Games.WGames(self, db, None, False)
        self.wgames.tbWork.hide()
        self.wgames.status.hide()
        self.wgames.infoMove = InfoMoveReplace(self)

        layout = Colocacion.H().control(self.wgames)
        self.setLayout(layout)

    def tw_terminar(self):
        return

    def setData(self, position, pv):
        self.position = position
        self.set_pv(pv)

    def set_pv(self, pv):
        self.pv = pv
        self.db.filter_pv(pv)
        self.wgames.grid.refresh()
        self.wgames.grid.gotop()

    def start(self):
        self.set_pv(self.pv)

    def stop(self):
        self.db.close()


class TabsAnalisis(QtWidgets.QWidget):
    def __init__(self, panelOpening, procesador, configuration):
        QtWidgets.QWidget.__init__(self)

        self.panelOpening = panelOpening
        self.dbop = panelOpening.dbop

        self.procesador = procesador
        self.configuration = configuration
        self.game = None
        self.njg = None

        self.tabtree = POLAnalisisTree.TabTree(self, configuration)
        self.tabengine = TabEngine(self, procesador, configuration)

        self.li_tabs = [("engine", self.tabengine), ("tree", self.tabtree)]
        self.tabActive = 0

        self.tabs = Controles.Tab(panelOpening)
        self.tabs.set_font_type(puntos=self.configuration.x_pgn_fontpoints)
        self.tabs.setTabIcon(0, Iconos.Engine())
        self.tabs.new_tab(self.tabengine, _("Engine"))
        self.tabs.new_tab(self.tabtree, _("Tree"))
        self.tabs.setTabIcon(1, Iconos.Arbol())

        self.tabs.dispatchChange(self.tabChanged)

        tabButton = QtWidgets.QToolButton(self)
        tabButton.setIcon(Iconos.Nuevo())
        tabButton.clicked.connect(self.creaTab)
        li = [(_("Analysis of next move"), True), (_("Analysis of current move"), False)]
        self.cb_nextmove = Controles.CB(self, li, True).capture_changes(self.changedNextMove)

        corner_widget = QtWidgets.QWidget(self)
        lyCorner = Colocacion.H().control(self.cb_nextmove).control(tabButton).margen(0)
        corner_widget.setLayout(lyCorner)

        self.tabs.setCornerWidget(corner_widget)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabCloseRequested)

        self.tabs.quita_x(0)
        self.tabs.quita_x(1)

        layout = Colocacion.V()
        layout.control(self.tabs).margen(0)
        self.setLayout(layout)

    def changedNextMove(self):
        if self.game is not None:
            self.setPosicion(self.game, self.njg)

    def tabChanged(self, ntab):
        self.tabActive = ntab
        if ntab > 0:
            tipo, wtab = self.li_tabs[ntab]
            wtab.start()

    def tabCloseRequested(self, ntab):
        tipo, wtab = self.li_tabs[ntab]
        wtab.stop()
        if ntab > 1:
            del self.li_tabs[ntab]
            self.tabs.removeTab(ntab)
            del wtab

    def creaTab(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("book", _("Polyglot book"), Iconos.Libros())
        menu.separador()
        menu.opcion("database", _("Database"), Iconos.Database())
        menu.separador()
        menu.opcion("summary", _("Database opening explorer"), Iconos.Arbol())
        resp = menu.lanza()
        pos = 0
        if resp == "book":
            book = self.seleccionaLibro()
            if book:
                tabbook = TabBook(self, book, self.configuration)
                self.li_tabs.append((resp, tabbook))
                pos = len(self.li_tabs) - 1
                self.tabs.new_tab(tabbook, book.name, pos)
                self.tabs.setTabIcon(pos, Iconos.Libros())
                self.setPosicion(self.game, self.njg, pos)

        elif resp == "summary":
            nomfichgames = QTVarios.select_db(self, self.configuration, True, False)
            if nomfichgames:
                db_stat = DBgamesST.TreeSTAT(nomfichgames + ".st1")
                tabdb = TabDatabaseSummary(self, self.procesador, db_stat)
                self.li_tabs.append((resp, tabdb))
                pos = len(self.li_tabs) - 1
                self.setPosicion(self.game, self.njg, pos)
                name = os.path.basename(nomfichgames)[:-5]
                self.tabs.new_tab(tabdb, name, pos)
                self.tabs.setTabIcon(pos, Iconos.Arbol())

        elif resp == "database":
            nomfichgames = QTVarios.select_db(self, self.configuration, True, False)
            if nomfichgames:
                db = DBgames.DBgames(nomfichgames)
                tabdb = TabDatabase(self, self.procesador, db)
                self.li_tabs.append((resp, tabdb))
                pos = len(self.li_tabs) - 1
                self.setPosicion(self.game, self.njg, pos)
                name = os.path.basename(nomfichgames)[:-5]
                self.tabs.new_tab(tabdb, name, pos)
                self.tabs.setTabIcon(pos, Iconos.Database())
        self.tabs.activa(pos)

    def setPosicion(self, game, njg, numTab=None):
        if game is None:
            return
        move = game.move(njg)
        self.game = game
        self.njg = njg
        next = self.cb_nextmove.valor()
        if move:
            if njg == 0:
                pv = game.pv_hasta(njg) if next else ""
            else:
                pv = game.pv_hasta(njg if next else njg - 1)
            position = move.position if next else move.position_before
        else:
            position = Position.Position().set_pos_initial()
            pv = ""

        for ntab, (tipo, tab) in enumerate(self.li_tabs):
            if ntab == 0:
                p = Game.Game()
                p.read_pv(pv)
                tab.setData(p.pgn_html(with_figurines=self.configuration.x_pgn_withfigurines), position, pv)
            else:
                if numTab is not None:
                    if ntab != numTab:
                        continue
                if ntab > 1:
                    tab.setData(position, pv)
                    tab.start()

    def seleccionaLibro(self):
        list_books = Books.ListBooks()
        menu = QTVarios.LCMenu(self)
        rondo = QTVarios.rondo_puntos()
        for book in list_books.lista:
            menu.opcion(("x", book), book.name, rondo.otro())
            menu.separador()
        menu.opcion(("n", None), _("Registered books"), Iconos.Nuevo())
        resp = menu.lanza()
        if resp:
            orden, book = resp
            if orden == "x":
                pass
            elif orden == "n":
                WBooks.registered_books(self)
        else:
            book = None
        return book

    def saveConfig(self):
        for tipo, wtab in self.li_tabs:
            if tipo == "engine":
                wtab.saveConfig()

    def refresh_lines(self):
        self.panelOpening.refresh_lines()
