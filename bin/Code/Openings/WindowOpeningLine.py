import copy
import operator
import os
import os.path

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Analysis import Analysis
from Code.Base import Game
from Code.Base.Constantes import BOOK_BEST_MOVE, BOOK_RANDOM_UNIFORM, BOOK_RANDOM_PROPORTIONAL
from Code.Base.Constantes import NONE, ALL, ONLY_BLACK, ONLY_WHITE
from Code.Books import Books, Polyglot, WBooks
from Code.Databases import DBgames
from Code.Engines import EnginesBunch
from Code.Engines import Priorities
from Code.Openings import WindowOpenings, POLAnalisis, POLBoard, OpeningLines, OpeningsStd
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.QT import WindowSavePGN
from Code.Voyager import Voyager


class WLines(LCDialog.LCDialog):
    def __init__(self, dbop):
        self.dbop: OpeningLines.Opening = dbop
        self.title = dbop.gettitle()
        self.procesador = Code.procesador
        self.configuration = self.procesador.configuration
        self.gamebase = self.dbop.getgamebase()
        if len(self.gamebase) > 0:
            self.title += f" ({self.gamebase.pgn_translated()})"
        self.num_jg_inicial = self.gamebase.num_moves()
        self.num_jg_actual = None
        self.game = None

        LCDialog.LCDialog.__init__(self, self.procesador.main_window, self.title, Iconos.OpeningLines(), "studyOpening")

        self.resultado = None
        with_figurines = self.configuration.x_pgn_withfigurines

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Remove"), Iconos.Borrar(), self.remove),
            None,
            (_("Import"), Iconos.Import8(), self.importar),
            None,
            (_("Export"), Iconos.Export8(), self.exportar),
            None,
            (_("Utilities"), Iconos.Utilidades(), self.utilities),
            None,
            (_("Train"), Iconos.Study(), self.train),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("LINE", _("Line"), 45, edicion=Delegados.EtiquetaPOS(False, True))
        start = self.gamebase.num_moves() // 2 + 1
        ancho_col = int(((self.configuration.x_pgn_width - 35 - 20) / 2) * 80 / 100)
        for x in range(start, 75):
            o_columns.nueva(str(x), str(x), ancho_col, edicion=Delegados.EtiquetaPOS(with_figurines, True))
        self.glines = Grid.Grid(self, o_columns, siCabeceraMovible=False)
        self.glines.setAlternatingRowColors(False)
        self.glines.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.glines.ponAltoFila(self.configuration.x_pgn_rowheight)

        self.pboard = POLBoard.BoardLines(self, self.configuration)

        self.tabsanalisis = POLAnalisis.TabsAnalisis(self, self.procesador, self.configuration)

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color:lightgray;")
        widget_layout = Colocacion.V().control(self.glines)
        widget_layout.margen(3)
        widget.setLayout(widget_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(widget)
        splitter.addWidget(self.tabsanalisis)

        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        splitter.setSizePolicy(sp)

        self.register_splitter(splitter, "SPLITTER")

        layout_down = Colocacion.H().control(self.pboard).control(splitter).margen(3)
        layout = Colocacion.V().control(self.tb).otro(layout_down).margen(3)
        self.setLayout(layout)

        self.colorPar = Code.dic_qcolors["WLINES_PAR"]
        self.colorNon = Code.dic_qcolors["WLINES_NON"]
        self.colorLine = Code.dic_qcolors["WLINES_LINE"]

        self.game = self.gamebase

        self.pboard.MoverFinal()

        self.restore_video()

        self.last_numlines = -1
        self.show_lines()

    def refresh_glines(self):
        self.glines.refresh()

    def show_lines(self):
        numlines = len(self.dbop)
        if numlines != self.last_numlines:
            self.setWindowTitle("%s [%d]" % (self.title, numlines))
            self.last_numlines = numlines
            self.tb.set_action_visible(self.train, len(self.dbop) > 0)

    def refresh_lines(self):
        self.glines.refresh()
        self.show_lines()

    def exportar(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("PGN Format"), Iconos.PGN())
        r = "%s %%s" % _("Result")
        submenu.opcion("1-0", r % "1-0", Iconos.Blancas8())
        submenu.opcion("0-1", r % "0-1", Iconos.Negras8())
        submenu.opcion("1/2-1/2", r % "1/2-1/2", Iconos.Tablas8())
        submenu.opcion("", _("Without Result"), Iconos.Gris())
        resp = menu.lanza()
        if resp is not None:
            w = WindowSavePGN.WSaveVarios(self, self.configuration)
            if w.exec_():
                ws = WindowSavePGN.FileSavePGN(self, w.dic_result)
                if ws.open():
                    self.dbop.exportarPGN(ws, resp)
                    ws.close()
                    ws.um_final()

    def utilities(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.ta_massive, _("Mass analysis"), Iconos.Analizar())
        menu.separador()
        menu.opcion(self.ta_transpositions, _("Complete with transpositions"), Iconos.Arbol())
        menu.separador()

        list_history = self.dbop.list_history()
        if list_history:
            menu.separador()
            submenu = menu.submenu(_("Backups"), Iconos.Copiar())
            rondo = QTVarios.rondoPuntos()
            for history in list_history[:20]:
                h = history
                if len(h) > 70:
                    h = h[:70] + "..."
                submenu.opcion(history, h, rondo.otro())
                submenu.separador()
            submenu.opcion(self.ta_remove_backups, _("Remove all backups"), Iconos.Delete())

        resp = menu.lanza()
        if resp:
            if isinstance(resp, str):
                if QTUtil2.pregunta(self, _("Are you sure you want to restore backup %s ?") % ("\n%s" % resp)):
                    um = QTUtil2.working(self)
                    self.dbop.recovering_history(resp)
                    self.refresh_lines()
                    um.final()
            else:
                resp()

    def ta_remove_backups(self):
        if QTUtil2.pregunta(self, "%s\n%s" % (_("Remove all backups"), _("Are you sure?"))):
            self.dbop.remove_all_history()

    def ta_transpositions(self):
        um = QTUtil2.working(self)
        self.dbop.transpositions()
        self.refresh_lines()
        self.glines.gotop()
        um.final()

    def ta_massive(self):
        dicVar = self.configuration.read_variables("MASSIVE_OLINES")

        form = FormLayout.FormLayout(self, _("Mass analysis"), Iconos.Analizar(), anchoMinimo=460)
        form.separador()

        form.combobox(
            _("Engine"),
            self.configuration.combo_engines_multipv10(4),
            dicVar.get("ENGINE", self.configuration.engine_tutor()),
        )
        form.separador()

        form.float(
            _("Duration of engine analysis (secs)"),
            dicVar.get("SEGUNDOS", float(self.configuration.x_tutor_mstime / 1000.0)),
        )

        liDepths = [("--", 0)]
        for x in range(1, 51):
            liDepths.append((str(x), x))
        form.combobox(_("Depth"), liDepths, dicVar.get("DEPTH", self.configuration.x_tutor_depth))
        form.separador()

        li = [(_("Maximum"), 0)]
        for x in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40, 50, 75, 100, 150, 200):
            li.append((str(x), x))
        form.combobox(
            _("Number of variations evaluated by the engine (MultiPV)"),
            li,
            dicVar.get("MULTIPV", self.configuration.x_tutor_multipv),
        )
        form.separador()

        liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK"), (_("White & Black"), "BOTH")]
        form.combobox(_("Analyze color"), liJ, dicVar.get("COLOR", "BOTH"))
        form.separador()

        form.combobox(
            _("Process priority"), Priorities.priorities.combo(), dicVar.get("PRIORITY", Priorities.priorities.normal)
        )
        form.separador()

        form.checkbox(_("Redo any existing prior analysis (if they exist)"), dicVar.get("REDO", False))
        form.separador()

        resultado = form.run()
        if resultado is None:
            return

        claveMotor, vtime, depth, multiPV, color, priority, redo = resultado[1]
        ms = int(vtime * 1000)
        if ms == 0 and depth == 0:
            return

        dicVar["ENGINE"] = claveMotor
        dicVar["SEGUNDOS"] = vtime
        dicVar["DEPTH"] = depth
        dicVar["MULTIPV"] = multiPV
        dicVar["COLOR"] = color
        dicVar["PRIORITY"] = priority
        dicVar["REDO"] = redo
        self.configuration.write_variables("MASSIVE_OLINES", dicVar)

        um = QTUtil2.one_moment_please(self)
        st_fens_m2 = self.dbop.get_all_fen()
        stfen = set()
        for fenm2 in st_fens_m2:
            if color == "WHITE":
                if " b " in fenm2:
                    continue
            elif color == "BLACK":
                if " w " in fenm2:
                    continue
            stfen.add(fenm2)

        if redo is False:
            li_borrar = []
            for fenm2 in stfen:
                dic = self.dbop.getfenvalue(fenm2)
                if "ANALISIS" in dic:
                    li_borrar.append(fenm2)
            for fenm2 in li_borrar:
                stfen.remove(fenm2)

        conf_engine = copy.deepcopy(self.configuration.buscaRival(claveMotor))
        conf_engine.update_multipv(multiPV)
        xmanager = self.procesador.creaManagerMotor(conf_engine, ms, depth, True, priority=priority)

        um.final()

        mensaje = _("Move") + "  %d/" + str(len(stfen))
        tmpBP = QTUtil2.BarraProgreso(self, _("Mass analysis"), "", len(stfen))
        tmpBP.setFixedWidth(450)
        tmpBP.mostrar()

        for done, fenm2 in enumerate(stfen, 1):
            if tmpBP.is_canceled():
                break

            tmpBP.inc()
            tmpBP.mensaje(mensaje % done)

            mrm = xmanager.analiza(fenm2 + " 0 1")
            dic = self.dbop.getfenvalue(fenm2)
            dic["ANALISIS"] = mrm
            self.dbop.setfenvalue(fenm2, dic)

        tmpBP.cerrar()

    def train(self):
        menu = QTVarios.LCMenu(self)
        trSSP, trEng = self.train_test()
        if trSSP:
            menu.opcion("tr_sequential", _("Sequential"), Iconos.TrainSequential())
            menu.separador()
            menu.opcion("tr_static", _("Static"), Iconos.TrainStatic())
            menu.separador()
            menu.opcion("tr_positions", _("Positions"), Iconos.TrainPositions())
            menu.separador()
        if trEng:
            menu.opcion("tr_engines", _("With engines"), Iconos.TrainEngines())
            menu.separador()
        submenu = menu.submenu(_("Configuration"), Iconos.Configurar())
        if trEng or trSSP:
            submenu.opcion("update", _("Update current trainings"), Iconos.Reindexar())
            submenu.separador()
        submenu1 = submenu.submenu(_("Create trainings"), Iconos.Modificar())
        submenu1.opcion(
            "new_ssp", "%s - %s - %s" % (_("Sequential"), _("Static"), _("Positions")), Iconos.TrainSequential()
        )
        submenu1.opcion("new_eng", _("With engines"), Iconos.TrainEngines())

        resp = menu.lanza()
        if resp is None:
            return
        if resp.startswith("tr_"):
            self.resultado = resp
            self.terminar()
        elif resp == "new_ssp":
            self.trainNewSSP()
        elif resp == "new_eng":
            self.trainNewEngines()
        elif resp == "update":
            self.trainUpdateAll()

    def train_test(self):
        if len(self.dbop) == 0:
            return False, False
        training = self.dbop.training()
        trainingEng = self.dbop.trainingEngines()
        return training is not None, trainingEng is not None

    def trainNewSSP(self):
        training = self.dbop.training()
        color = "WHITE"
        random_order = False
        max_moves = 0

        if training is not None:
            color = training["COLOR"]
            random_order = training["RANDOM"]
            max_moves = training["MAXMOVES"]

        separador = FormLayout.separador
        li_gen = [separador]

        liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK")]
        config = FormLayout.Combobox(_("Side you play with"), liJ)
        li_gen.append((config, color))

        li_gen.append(separador)
        li_gen.append((_("Random order"), random_order))

        li_gen.append(separador)
        li_gen.append((_("Maximum number of movements (0=all)"), max_moves))

        resultado = FormLayout.fedit(li_gen, title=_("New training"), parent=self, anchoMinimo=360, icon=Iconos.Study())
        if resultado is None:
            return

        accion, liResp = resultado

        reg = {}

        reg["COLOR"], reg["RANDOM"], reg["MAXMOVES"] = liResp

        self.dbop.createTrainingSSP(reg, self.procesador)

        QTUtil2.message_bold(self, _("The trainings of this opening has been created"))

    def trainNewEngines(self):
        training = self.dbop.trainingEngines()
        color = "WHITE"
        basepv = self.dbop.basePV
        mandatory = basepv.count(" ") + 1 if len(basepv) > 0 else 0
        control = 10
        lost_points = 20
        engine_control = self.configuration.x_tutor_clave
        engine_time = 5.0
        num_engines = 20
        key_engine = "alaric"
        ext_engines = []
        auto_analysis = True
        ask_movesdifferent = False
        times = [500, 1000, 2000, 4000, 8000]
        books = ["", "", "", "", ""]
        books_sel = ["", "", "", "", ""]

        if training is not None:
            color = training["COLOR"]
            mandatory = training.get("MANDATORY", mandatory)
            control = training.get("CONTROL", control)
            lost_points = training.get("LOST_POINTS", lost_points)
            engine_control = training.get("ENGINE_CONTROL", engine_control)
            engine_time = training.get("ENGINE_TIME", engine_time)
            num_engines = training.get("NUM_ENGINES", num_engines)
            key_engine = training.get("KEY_ENGINE", key_engine)
            ext_engines = training.get("EXT_ENGINES", ext_engines)
            auto_analysis = training.get("AUTO_ANALYSIS", auto_analysis)
            ask_movesdifferent = training.get("ASK_MOVESDIFFERENT", ask_movesdifferent)
            times = training.get("TIMES", times)
            books = training.get("BOOKS", books)
            books_sel = training.get("BOOKS_SEL", books_sel)

        separador = FormLayout.separador
        li_gen = [separador]

        liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK")]
        config = FormLayout.Combobox(_("Side you play with"), liJ)
        li_gen.append((config, color))

        li_gen.append((_("Mandatory movements") + ":", mandatory))
        li_gen.append(separador)
        li_gen.append((_("Movements until the control") + ":", control))
        li_gen.append(separador)
        li_gen.append((_("Maximum number of lost centipawns to pass control") + ":", lost_points))
        li_gen.append(separador)

        dic_engines = self.configuration.dic_engines
        li_engines = EnginesBunch.lista(dic_engines)
        config = FormLayout.Spinbox(
            "%s: %s" % (_("Automatic selection"), _("number of engines")), 0, len(li_engines), 50
        )
        li_gen.append((config, num_engines))

        likeys = [("%s %d" % (_("Group"), pos), x) for pos, x in enumerate(li_engines, 1) if x in dic_engines]
        config = FormLayout.Combobox("%s: %s" % (_("Automatic selection"), _("bunch of engines")), likeys)
        li_gen.append((config, key_engine))
        li_gen.append(separador)

        config = FormLayout.Combobox(_("Engine that does the control"), self.configuration.combo_engines())
        li_gen.append((config, engine_control))
        li_gen.append((_("Duration of analysis (secs)") + ":", float(engine_time)))

        li_gen.append(separador)

        li_gen.append((_("Automatic analysis") + ":", auto_analysis))

        li_gen.append(separador)

        li_gen.append((_("Ask when the moves are different from the line") + ":", ask_movesdifferent))

        li = [("--", "")]
        for key, cm in self.configuration.dic_engines.items():
            li.append((cm.nombre_ext(), key))
        li = sorted(li, key=operator.itemgetter(1))

        li_ext = []

        for x in range(16):
            config = FormLayout.Combobox("%s %d" % (_("Engine"), x + 1), li)
            key = ext_engines[x] if len(ext_engines) > x else ""
            li_ext.append((config, key))

        liLevels = [separador]
        list_books = Books.ListBooks()
        libooks = [(bookx.name, bookx) for bookx in list_books.lista]
        libooks.insert(0, ("--", None))
        li_books_sel = (
            ("", ""),
            (_("Uniform random"), BOOK_RANDOM_UNIFORM),
            (_("Proportional random"), BOOK_RANDOM_PROPORTIONAL),
            (_("Always the highest percentage"), BOOK_BEST_MOVE),
        )
        for level in range(5):
            n = level + 1
            title = "%s %d" % (_("Level"), n)
            # liLevels.append((None, title))
            tm = times[level] / 1000.0 if len(times) > level else 0.0
            liLevels.append(("%s. %s:" % (title, _("Time engines think in seconds")), tm))

            bk = books[level] if len(books) > level else ""
            book = list_books.seek_book(bk) if bk else None
            config = FormLayout.Combobox(_("Book"), libooks)
            liLevels.append((config, book))

            config = FormLayout.Combobox(_("Book selection mode"), li_books_sel)
            liLevels.append((config, books_sel[level]))

        lista = []
        lista.append((li_gen, _("Basic data"), ""))
        lista.append((li_ext, _("Manual engine selection"), ""))
        lista.append((liLevels, _("Levels"), ""))

        resultado = FormLayout.fedit(lista, title=_("With engines"), parent=self, anchoMinimo=360, icon=Iconos.Study())
        if resultado is None:
            return

        accion, liResp = resultado

        selMotoresExt = []
        li_gen, li_ext, liLevels = liResp

        for key in li_ext:
            if key:
                selMotoresExt.append(key)

        reg = {}

        (
            reg["COLOR"],
            reg["MANDATORY"],
            reg["CONTROL"],
            reg["LOST_POINTS"],
            reg["NUM_ENGINES"],
            reg["KEY_ENGINE"],
            reg["ENGINE_CONTROL"],
            reg["ENGINE_TIME"],
            reg["AUTO_ANALYSIS"],
            reg["ASK_MOVESDIFFERENT"],
        ) = li_gen
        reg["EXT_ENGINES"] = selMotoresExt

        if (len(selMotoresExt) + reg["NUM_ENGINES"]) == 0:
            reg["NUM_ENGINES"] = 1

        times = []
        books = []
        books_sel = []
        for x in range(5):
            tm = int(liLevels[x * 3] * 1000)
            bk = liLevels[x * 3 + 1]
            bk_mode = liLevels[x * 3 + 2]
            if tm:
                times.append(tm)
                books.append(bk.name if bk else "")
                books_sel.append(bk_mode)
        if len(times) == 0:
            times.append(500)
            books.append(None)
        reg["TIMES"] = times
        reg["BOOKS"] = books
        reg["BOOKS_SEL"] = books_sel

        self.dbop.createTrainingEngines(reg, self.procesador)

        QTUtil2.message_bold(self, _("Created"))

    def trainUpdateAll(self):
        self.dbop.updateTraining(self.procesador)
        self.dbop.updateTrainingEngines()
        QTUtil2.message_bold(self, _("The trainings have been updated"))

    def addPartida(self, game):
        if game.pv().startswith(self.gamebase.pv()):
            siNueva, num_linea, siAppend = self.dbop.posPartida(game)
            if siNueva:
                self.dbop.append(game)
            else:
                if siAppend:
                    self.dbop[num_linea] = game
            self.glines.refresh()
        else:
            QTUtil2.message_error(self, _X("New line must begin with %1", self.gamebase.pgn_translated()))
        self.show_lines()

    def gameActual(self):
        game = Game.Game()
        if len(self.dbop) == 0:
            game.assign_other_game(self.gamebase)
            return game
        numcol = self.glines.posActualN()[1]
        game.assign_other_game(self.game if self.game and numcol > 0 else self.gamebase)
        if self.num_jg_actual is not None and self.num_jg_inicial <= self.num_jg_actual < len(game):
            game.li_moves = game.li_moves[: self.num_jg_actual + 1]
        return game

    def voyager2(self, game):
        ptxt = Voyager.voyager_game(self, game)
        if ptxt:
            game = Game.Game()
            game.restore(ptxt)
            self.addPartida(game)
            self.show_lines()

    def importar(self):
        menu = QTVarios.LCMenu(self)

        def haz_menu(frommenu, game_base, all=True):
            if all:
                li_op = self.dbop.get_others(self.configuration, game_base)
                if li_op:
                    otra = frommenu.submenu(_("Other opening lines"), Iconos.OpeningLines())
                    for file, titulo in li_op:
                        otra.opcion(("ol", (file, game_base)), titulo, Iconos.PuntoVerde())
                    frommenu.separador()
            frommenu.opcion(("pgn", game_base), _("PGN with variations"), Iconos.Board())
            frommenu.separador()
            frommenu.opcion(("polyglot", game_base), _("Polyglot book"), Iconos.Libros())
            frommenu.separador()
            frommenu.opcion(("summary", game_base), _("Database opening explorer"), Iconos.Database())
            frommenu.separador()

            if all:
                frommenu.separador()
                frommenu.opcion(("voyager2", game_base), _("Voyager 2"), Iconos.Voyager())
                frommenu.separador()
                frommenu.opcion(("opening", game_base), _("Opening"), Iconos.Opening())

        game = self.gameActual()
        if len(game) > len(self.gamebase):
            sub2 = menu.submenu(_("From base position"), Iconos.MoverInicio())
            haz_menu(sub2, self.gamebase)
            menu.separador()
            sub1 = menu.submenu(_("From current position"), Iconos.MoverLibre())
            haz_menu(sub1, game)
            menu.separador()
            sub1 = menu.submenu(_("From all end positions"), Iconos.MoverFinal())
            sub1.opcion(("polyglot", None), _("Polyglot book"), Iconos.Libros())
            menu.separador()
        else:
            haz_menu(menu, self.gamebase)

        menu.separador()
        comments_import = menu.submenu(_("Comments"), Iconos.Comment())
        comments_import.opcion(("comments", self.ta_import_pgn_comments), _("PGN with variations"), Iconos.Board())
        comments_import.separador()
        comments_import.opcion(("comments", self.ta_import_other_comments), _("Other opening lines"),
                               Iconos.OpeningLines())

        resp = menu.lanza()
        if resp is None:
            return
        tipo, game = resp
        if tipo == "pgn":
            self.import_pgn(game)
        elif tipo == "polyglot":
            self.import_polyglot(game)
        elif tipo == "summary":
            self.import_dbopening_explorer(game)
        elif tipo == "voyager2":
            self.voyager2(game)
        elif tipo == "opening":
            self.importarOpening(game)
        elif tipo == "ol":
            file, game = game
            self.import_other(file, game)
        elif tipo == "comments":
            rutina = game
            rutina()
            return
        self.dbop.clean()
        self.show_lines()

    def import_other(self, file, game):
        um = QTUtil2.one_moment_please(self)
        pathFichero = os.path.join(self.configuration.folder_openings(), file)
        self.dbop.import_other(pathFichero, game)
        um.final()
        self.glines.refresh()
        self.glines.gotop()

    def importarOpening(self, game):
        game.assign_opening()
        w = WindowOpenings.WOpenings(self, self.configuration, game.opening)
        if w.exec_():
            ap = w.resultado()
            game = Game.Game()
            game.read_pv(ap.a1h8)
            self.addPartida(game)

    def import_param_books(self, titulo, with_excltrans):
        dicData = self.dbop.getconfig("IMPORTAR_LEEPARAM")
        if not dicData:
            dicData = {}

        form = FormLayout.FormLayout(self, titulo, Iconos.Naranja(), anchoMinimo=360)
        form.separador()

        form.apart(_("Select the number of half-moves <br> for each game to be considered"))
        form.spinbox(_("Depth"), 3, 999, 50, dicData.get("DEPTH", 30))
        form.separador()

        li = [
            (_("Only white best movements"), True),
            (_("Only black best movements"), False),
        ]  # , (_("All moves"), None) ] -> se va al infinito
        form.combobox(_("Moves"), li, dicData.get("SIWHITE", True))
        form.separador()

        li = [(_("Only one best move"), True), (_("All best moves"), False)]
        form.combobox(_("Best move"), li, dicData.get("ONLYONE", True))
        form.separador()

        form.spinbox(_("Minimum movements must have each line"), 0, 99, 50, dicData.get("MINMOVES", 0))
        form.separador()

        if with_excltrans:
            form.checkbox(_("Exclude transpositions"), dicData.get("EXCLTRANSPOSITIONS", True))

        resultado = form.run()
        if resultado:
            accion, liResp = resultado
            if with_excltrans:
                depth, siWhite, onlyone, minMoves, excltraspositions = liResp
                dicData["EXCLTRANSPOSITIONS"] = excltraspositions
            else:
                depth, siWhite, onlyone, minMoves = liResp
            dicData["DEPTH"] = depth
            dicData["SIWHITE"] = siWhite
            dicData["ONLYONE"] = onlyone
            dicData["MINMOVES"] = minMoves

            self.dbop.setconfig("IMPORTAR_LEEPARAM", dicData)
            self.configuration.write_variables("WBG_MOVES", dicData)
            return dicData
        return None

    def import_dbopening_explorer(self, game):
        nomfichgames = QTVarios.select_db(self, self.configuration, True, False)
        if nomfichgames:
            dicData = self.import_param_books(_("Database opening explorer"), False)
            if dicData:
                db = DBgames.DBgames(nomfichgames)  # por el problema de los externos
                ficheroSummary = db.db_stat.nom_fichero
                db.close()
                depth, siWhite, onlyone, minMoves = (
                    dicData["DEPTH"],
                    dicData["SIWHITE"],
                    dicData["ONLYONE"],
                    dicData["MINMOVES"],
                )
                self.dbop.import_dbopening_explorer(self, game, ficheroSummary, depth, siWhite, onlyone, minMoves)
                self.glines.refresh()
                self.glines.gotop()

    def import_polyglot(self, game):
        w = WImportPolyglot(self, game)
        if w.exec_():
            self.glines.refresh()
            self.glines.gotop()

    def import_pgn(self, game):
        key_var = "OPENINGLINES"
        previo = self.configuration.read_variables(key_var)
        carpeta = previo.get("CARPETAPGN", "")

        fichero_pgn = SelectFiles.leeFichero(self, carpeta, "pgn", titulo=_("File to import"))
        if not fichero_pgn:
            return
        previo["CARPETAPGN"] = os.path.dirname(fichero_pgn)

        form = FormLayout.FormLayout(self, os.path.basename(fichero_pgn), Iconos.PGN_Importar(), anchoMinimo=460)
        form.separador()

        form.apart(_("Select the number of half-moves <br> for each game to be considered"))

        form.spinbox(_("Depth"), 3, 999, 50, previo.get("IPGN_DEPTH", 30))
        form.separador()

        liVariations = ((_("All"), ALL), (_("None"), NONE), (_("White"), ONLY_WHITE), (_("Black"), ONLY_BLACK))
        form.combobox(_("Include variations"), liVariations, previo.get("IPGN_VARIATIONSMODE", "A"))
        form.separador()

        form.checkbox(_("Include comments"), previo.get("IPGN_COMMENTS", True))
        form.separador()

        resultado = form.run()

        if resultado:
            accion, liResp = resultado
            previo["IPGN_DEPTH"] = depth = liResp[0]
            previo["IPGN_VARIATIONSMODE"] = variations = liResp[1]
            previo["IPGN_COMMENTS"] = comments = liResp[2]
            self.configuration.write_variables(key_var, previo)

            self.dbop.import_pgn(self, game, fichero_pgn, depth, variations, comments)
            self.glines.refresh()
            self.glines.gotop()

    def ta_import_pgn_comments(self):
        key_var = "OPENINGLINES"
        dic_var = self.configuration.read_variables(key_var)
        carpeta = dic_var.get("CARPETAPGN", "")

        fichero_pgn = SelectFiles.leeFichero(self, carpeta, "pgn", titulo=_("File to import"))
        if not fichero_pgn:
            return
        dic_var["CARPETAPGN"] = os.path.dirname(fichero_pgn)
        self.configuration.write_variables(key_var, dic_var)

        self.dbop.import_pgn_comments(self, fichero_pgn)
        self.glines.refresh()
        self.glines.gotop()

    def ta_import_other_comments(self):
        current_path = self.dbop.nom_fichero

        file_opk = SelectFiles.leeFichero(self, os.path.dirname(current_path), "opk", titulo=_("Opening lines"))
        if not file_opk or Util.same_path(current_path, file_opk):
            return

        self.dbop.import_other_comments(file_opk)

        self.glines.refresh()
        self.glines.gotop()

    def grid_color_fondo(self, grid, row, o_column):
        col = o_column.key
        if col == "LINE":
            return self.colorLine
        else:
            linea = row // 2
            return self.colorPar if linea % 2 == 1 else self.colorNon

    def grid_cambiado_registro(self, grid, row, o_column):
        col = o_column.key
        linea = row // 2
        self.game = self.dbop[linea]
        iswhite = row % 2 == 0
        if col.isdigit():
            njug = (int(col) - 1) * 2
            if not iswhite:
                njug += 1
        else:
            njug = -1
        self.num_jg_actual = njug
        self.pboard.ponPartida(self.game)
        self.pboard.colocatePartida(njug)
        self.glines.setFocus()

    def setJugada(self, njug):
        """Recibimos informacion del panel del board"""
        if njug >= 0:
            self.tabsanalisis.setPosicion(self.game, njug)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        linea = row // 2
        iswhite = (row % 2) == 0
        color = Code.dic_colors["WLINES_PGN"]
        info = None
        indicadorInicial = None
        li_nags = []
        siLine = False
        agrisar = False

        if col == "LINE":
            pgn = str(linea + 1) if iswhite else ""
            siLine = True

        else:
            njug = (int(col) - 1) * 2
            if not iswhite:
                njug += 1
            game = self.dbop[linea]
            if self.num_jg_inicial <= njug < len(game):
                move = game.move(njug)
                pgn = move.pgnFigurinesSP() if self.configuration.x_pgn_withfigurines else move.pgn_translated()

                if linea:
                    game_ant = self.dbop[linea - 1]
                    if game_ant.pv_hasta(njug) == game.pv_hasta(njug):
                        agrisar = True
                dic = self.dbop.getfenvalue(move.position.fenm2())
                if dic:
                    if "COMENTARIO" in dic:
                        v = dic["COMENTARIO"]
                        if v:
                            indicadorInicial = "C"
                    if "VALORACION" in dic:
                        v = dic["VALORACION"]
                        if v:
                            li_nags.append(str(v))
                    if "VENTAJA" in dic:
                        v = dic["VENTAJA"]
                        if v:
                            li_nags.append(str(v))
            else:
                pgn = ""

        return pgn, iswhite, color, info, indicadorInicial, li_nags, agrisar, siLine

    def grid_num_datos(self, grid):
        return len(self.dbop) * 2

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        row, pos = self.glines.posActualN()

        if k == QtCore.Qt.Key_Left:
            if pos > 1:
                if row % 2 == 0:
                    self.glines.goto(row + 1, pos - 1)
                else:
                    self.glines.goto(row - 1, pos)
                return

        elif k == QtCore.Qt.Key_Right:
            if pos >= 1:
                if row % 2 == 0:
                    self.glines.goto(row + 1, pos)
                else:
                    self.glines.goto(row - 1, pos + 1)
                return

        elif k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            row, col = self.glines.current_position()
            if col.key == "LINE":
                self.borrar()
            else:
                self.borrar_move()

        elif k == QtCore.Qt.Key_Up:
            if row > 0:
                self.glines.goto(row - 1, pos)

        elif k == QtCore.Qt.Key_Down:
            if row < self.grid_num_datos(None) - 1:
                self.glines.goto(row + 1, pos)

    def grid_doble_click(self, grid, row, o_column):
        game = self.gameActual()
        if game is not None:
            self.procesador.cambiaXAnalyzer()
            xanalyzer = self.procesador.xanalyzer
            move = game.move(-1)
            fenm2 = move.position_before.fenm2()
            dic = self.dbop.getfenvalue(fenm2)
            if "ANALISIS" in dic:
                mrm = dic["ANALISIS"]
                move.analysis = mrm, 0
            else:
                me = QTUtil2.waiting_message.start(self, _("Analyzing the move...."), physical_pos="ad")

                move.analysis = xanalyzer.analizaJugadaPartida(
                    game, len(game) - 1, xanalyzer.mstime_engine, xanalyzer.depth_engine, window=self
                )
                me.final()
            Analysis.show_analysis(
                self.procesador, xanalyzer, move, self.pboard.board.is_white_bottom, len(game) - 1, main_window=self
            )

            dic = self.dbop.getfenvalue(fenm2)
            dic["ANALISIS"] = move.analysis[0]
            self.dbop.setfenvalue(fenm2, dic)

    def borrar_move(self):
        row, col = self.glines.current_position()
        linea = row // 2
        if 0 <= linea < len(self.dbop):
            game = self.dbop[linea]
            njug = (int(col.key) - 1) * 2
            if row % 2 == 1:
                njug += 1
            if linea:
                game_ant = self.dbop[linea - 1]
                if game_ant.pv_hasta(njug - 1) == game.pv_hasta(njug - 1):
                    return self.borrar()
            if linea < len(self.dbop) - 1:
                game_sig = self.dbop[linea + 1]
                if game_sig.pv_hasta(njug - 1) == game.pv_hasta(njug - 1):
                    return self.borrar()

            if njug == self.num_jg_inicial:
                return self.borrar()

            siUltimo = njug == len(game) - 1  # si es el ultimo no se pregunta
            if siUltimo or QTUtil2.pregunta(self, _("Do you want to eliminate this move?")):
                game.li_moves = game.li_moves[:njug]
                self.dbop[linea] = game

                self.goto_end_line()
        self.show_lines()

    def remove(self):
        tam_dbop = len(self.dbop)
        if tam_dbop == 0:
            return
        menu = QTVarios.LCMenu(self)
        current = self.glines.recno() // 2
        if 0 <= current < tam_dbop:
            menu.opcion("current", "%s %d" % (_("Remove line"), current + 1), Iconos.Mover())
            menu.separador()
        if tam_dbop > 1:
            menu.opcion("lines", _("Remove a list of lines"), Iconos.MoverLibre())
            menu.separador()
            menu.opcion("worst", _("Remove worst lines"), Iconos.Borrar())
            menu.separador()
            menu.opcion("opening", _("Opening"), Iconos.Opening())
            menu.separador()

        submenu = menu.submenu(_("Remove last move if the line ends with"), Iconos.Final())
        submenu.opcion("last_white", _("White"), Iconos.Blancas())
        submenu.separador()
        submenu.opcion("last_black", _("Black"), Iconos.Negras())
        menu.separador()

        menu.opcion("info", _("Remove comments/ratings/analysis"), Iconos.Delete())

        resp = menu.lanza()

        if resp == "current":
            self.dbop.save_history(_("Remove line %d") % (current + 1,))
            del self.dbop[current]
            self.goto_inilinea()

        elif resp == "lines":
            li_gen = [FormLayout.separador]
            config = FormLayout.Editbox(
                '<div align="right">' + _("Lines") + "<br>" + _("By example:") + " -5,8-12,14,19-", rx=r"[0-9,\-,\,]*"
            )
            li_gen.append((config, ""))
            resultado = FormLayout.fedit(
                li_gen, title=_("Remove a list of lines"), parent=self, anchoMinimo=460, icon=Iconos.OpeningLines()
            )
            if resultado:
                accion, liResp = resultado
                clista = liResp[0]
                if clista:
                    ln = Util.ListaNumerosImpresion(clista)
                    li = ln.selected(range(1, tam_dbop + 1))
                    sli = []
                    cad = ""
                    for num in li:
                        if cad:
                            cad += "," + str(num)
                        else:
                            cad = str(num)
                        if len(cad) > 80:
                            if len(sli) == 4:
                                sli.append("...")
                            elif len(sli) < 4:
                                sli.append(cad)
                            cad = ""
                    if cad:
                        sli.append(cad)
                    cli = "\n".join(sli)
                    if QTUtil2.pregunta(self, _("Do you want to remove the next lines?") + "\n\n" + cli):
                        um = QTUtil2.working(self)
                        self.dbop.remove_list_lines([x - 1 for x in li], cli)
                        self.glines.refresh()
                        self.goto_inilinea()
                        um.final()
        elif resp == "worst":
            self.remove_worst()
        elif resp == "opening":
            self.remove_opening()
        elif resp == "last_white":
            self.remove_lastmove(True)
        elif resp == "last_black":
            self.remove_lastmove(False)
        elif resp == "info":
            self.remove_info()
        self.show_lines()

    def remove_lastmove(self, iswhite):
        um = QTUtil2.working(self)
        self.dbop.remove_lastmove(
            iswhite, "%s %s" % (_("Remove last move if the line ends with"), _("White") if iswhite else _("Black"))
        )
        um.final()

    def remove_worst(self):
        key = "REMOVEWORSTLINES"
        dic_data = Code.configuration.read_variables(key)

        form = FormLayout.FormLayout(self, _("Remove worst lines"), Iconos.OpeningLines())
        form.separador()
        liJ = [(_("White"), "WHITE"), (_("Black"), "BLACK")]
        form.combobox(_("Side"), liJ, "WHITE" if self.pboard.board.is_white_bottom else "BLACK")
        form.separador()

        list_books = Books.ListBooks()
        libooks = [(bookx.name, bookx) for bookx in list_books.lista]
        libooks.insert(0, ("--", None))

        book_name = dic_data.get("BOOK_NAME", None)
        book_selected = None
        for name, book in libooks:
            if name == book_name:
                book_selected = book
                break

        form.combobox(_("Book"), libooks, book_selected)
        form.separador()

        tm = float(self.configuration.x_tutor_mstime / 1000.0)

        form.float(_("Duration of engine analysis (secs)"), dic_data.get("SECS", tm if tm > 0.0 else 3.0))
        form.separador()

        resultado = form.run()
        if resultado:
            um = QTUtil2.working(self)
            color, book, segs = resultado[1]
            ms = int(segs * 1000)
            if ms < 0.01:
                return
            if book:
                book.polyglot()

            dic_data["SECS"] = segs
            dic_data["BOOK_NAME"] = book.name if book else None
            Code.configuration.write_variables(key, dic_data)

            si_white = color == "WHITE"
            dic = self.dbop.dicRepeFen(si_white)
            mensaje = _("Move") + "  %d/" + str(len(dic))
            xmanager = self.procesador.creaManagerMotor(self.configuration.engine_tutor(), ms, 0, siMultiPV=False)
            xmanager.set_multipv(10)

            st_borrar = set()

            ok = True

            um.final()

            tmp_bp = QTUtil2.BarraProgreso(self, _("Remove worst lines"), "", len(dic), width=460)
            tmp_bp.mostrar()

            for n, fen in enumerate(dic, 1):
                if tmp_bp.is_canceled():
                    ok = False
                    break

                tmp_bp.inc()
                tmp_bp.mensaje(mensaje % n)

                dic_a1h8 = dic[fen]
                st_a1h8 = set(dic_a1h8.keys())
                li = []
                if book:
                    li_moves = book.get_list_moves(fen)
                    if li_moves:
                        # (from_sq, to_sq, promotion, "%-5s -%7.02f%% -%7d" % (pgn, pc, w), 1.0 * w / maxim))
                        li = [(m[0] + m[1] + m[2], m[4]) for m in li_moves if m[0] + m[1] + m[2] in st_a1h8]
                        if li:
                            li.sort(key=lambda x: x[1], reverse=True)
                            st_ya = set(x[0] for x in li)
                            for a1h8 in st_a1h8:
                                if a1h8 not in st_ya:
                                    li.append((a1h8, 0))

                if len(li) == 0:
                    mrm = xmanager.analiza(fen)
                    for a1h8 in dic_a1h8:
                        rm, pos = mrm.buscaRM(a1h8)
                        li.append((a1h8, pos if pos >= 0 else 999))
                    li.sort(key=lambda x: x[1])

                for a1h8, pos in li[1:]:
                    for num_linea in dic_a1h8[a1h8]:
                        st_borrar.add(num_linea)

            tmp_bp.cerrar()

            xmanager.terminar()

            if ok:
                li_borrar = list(st_borrar)
                n = len(li_borrar)
                if n:
                    self.dbop.remove_list_lines(li_borrar, _("Remove worst lines"))
                    self.dbop.pack_database()
                    QTUtil2.message_bold(self, _("Removed %d lines") % n)
                else:
                    QTUtil2.message_bold(self, _("Done"))
                self.refresh_lines()
                self.goto_inilinea()

    def remove_opening(self):
        me = QTUtil2.one_moment_please(self)
        op = OpeningsStd.Opening("")
        op.a1h8 = self.dbop.basePV
        w = WindowOpenings.WOpenings(self, self.configuration, op)
        me.final()
        if w.exec_():
            op = w.resultado()
            self.remove_pv(op.pgn, op.a1h8)

    def remove_pv(self, pgn, a1h8):
        if QTUtil2.pregunta(self, _("Do you want to remove all lines beginning with %s?").replace("%s", pgn)):
            um = QTUtil2.working(self)
            self.dbop.remove_pv(pgn, a1h8)
            self.refresh_lines()
            self.goto_inilinea()
            um.final()

    def remove_info(self):
        form = FormLayout.FormLayout(self, _("Remove"), Iconos.Delete(), font_txt=Controles.TipoLetra(puntos=10))

        form.separador()
        form.checkbox(_("All"), False)
        form.separador()

        form.checkbox(_("Comments"), False)
        form.checkbox(_("Ratings"), False)
        form.checkbox(_("Analysis"), False)

        resultado = form.run()

        if resultado:
            accion, li_resp = resultado
            is_all, is_comments, is_ratings, is_analysis = li_resp
            if is_all:
                is_comments = is_ratings = is_analysis = True
            if is_comments or is_ratings or is_analysis:
                QTUtil.refresh_gui()
                um = QTUtil2.working(self)
                self.tabsanalisis.tabengine.current_mrm = None
                self.dbop.remove_info(is_comments, is_ratings, is_analysis)
                self.refresh_lines()
                self.glines.gotop()
                um.final()

    def goto_inilinea(self):
        nlines = len(self.dbop)
        if nlines == 0:
            return

        linea = self.glines.recno() // 2
        if linea >= nlines:
            linea = nlines - 1

        row = linea * 2
        ncol = 0
        self.glines.goto(row, ncol)
        self.glines.refresh()

    def goto_end_line(self):
        nlines = len(self.dbop)
        if nlines == 0:
            return

        linea = self.glines.recno() // 2
        if linea >= nlines:
            linea = nlines - 1

        game = self.dbop[linea]

        row = linea * 2
        njug = len(game)
        if njug % 2 == 0:
            row += 1

        ncol = njug // 2
        if njug % 2 == 1:
            ncol += 1

        ncol -= self.num_jg_inicial // 2
        self.glines.goto(row, ncol)
        self.glines.refresh()

    def goto_next_lipv(self, lipv):
        li = self.dbop.get_numlines_pv(lipv, base=0)
        linea_actual = self.glines.recno() // 2

        if linea_actual in li:
            linea = linea_actual
        else:
            li.sort()
            linea = None
            for l in li:
                if l > linea_actual:
                    linea = l
                    break
            if linea is None and li:
                linea = li[0]

        njug = len(lipv)

        row = linea * 2
        if njug % 2 == 0:
            row += 1

        ncol = njug // 2
        if njug % 2 == 1:
            ncol += 1

        ncol -= self.num_jg_inicial // 2
        self.glines.goto(row, ncol)
        self.glines.refresh()

    def final_processes(self):
        board = self.pboard.board
        board.dbVisual.saveMoviblesBoard(board)
        self.dbop.setconfig("WHITEBOTTOM", board.is_white_bottom)
        self.tabsanalisis.saveConfig()
        self.save_video()
        self.procesador.stop_engines()

    def terminar(self):
        self.final_processes()
        self.accept()

    def closeEvent(self, event):
        self.final_processes()

    def player_has_moved(self, game):
        # Estamos en la misma linea ?
        # recno = self.glines.recno()
        # Buscamos en las lineas si hay alguna que el pv sea parcial o totalmente igual
        game.pending_opening = True
        siNueva, num_linea, siAppend = self.dbop.posPartida(game)
        is_white = game.move(-1).is_white()
        ncol = (len(game) - self.num_jg_inicial + 1) // 2
        if self.num_jg_inicial % 2 == 1 and is_white:
            ncol += 1
        if siNueva:
            self.dbop.append(game)
        else:
            if siAppend:
                self.dbop[num_linea] = game
        if not siAppend:
            siNueva, num_linea, siAppend = self.dbop.posPartida(game)

        row = num_linea * 2
        if not is_white:
            row += 1

        self.glines.refresh()
        self.glines.goto(row, ncol)
        self.show_lines()


def study(file):
    procesador = Code.procesador
    with QTUtil.EscondeWindow(procesador.main_window):
        dbop = OpeningLines.Opening(os.path.join(procesador.configuration.folder_openings(), file))
        w = WLines(dbop)
        w.exec_()
        dbop.close()
        return w.resultado


class WImportPolyglot(LCDialog.LCDialog):
    def __init__(self, w_parent, game):
        titulo = _("Polyglot book")
        icono = Iconos.Book()
        self.dbop: OpeningLines.Opening = w_parent.dbop

        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, "ol_import_polyglot")

        self.list_books = Books.ListBooks()
        self.game = game
        dic_data = self.read_dic_data()

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Books"), Iconos.Book(), self.register_books)

        # Books
        li_books = [(x.name, x) for x in self.list_books.lista]
        li_modes = [(name, key) for key, name in Polyglot.dic_modes().items()]

        def book_obj(key):
            dic_book: dict = dic_data.get(key)
            if dic_book:
                path = dic_book["path"]
                for name, book in li_books:
                    if path == book.path:
                        return book
            return None

        self.cb_white = Controles.CB(self, li_books, book_obj("BOOK_WHITE"))
        self.cb_mode_white = Controles.CB(self, li_modes, dic_data.get("MODE_WHITE"))
        lb_white_porc_min = Controles.LB2P(self, _("Minimum percentage")).ponTipoLetra(puntos=8)
        self.ed_white_porc_min = (Controles.ED(self).anchoFijo(60).
                                  tipoFloat(decimales=3, valor=dic_data.get("PORC_WHITE", 0.0)).ponTipoLetra(puntos=8))
        lb_white_weight_min = Controles.LB2P(self, _("Minimum weight")).ponTipoLetra(puntos=8)
        self.ed_white_weight_min = (Controles.ED(self).anchoFijo(60).
                                  tipoInt(dic_data.get("WEIGHT_WHITE", 0)).ponTipoLetra(puntos=8))

        ly_arr = Colocacion.H().control(self.cb_white).control(self.cb_mode_white)
        ly_abj = (Colocacion.H().relleno().control(lb_white_porc_min).control(self.ed_white_porc_min)
                  .espacio(10)
                  .control(lb_white_weight_min).control(self.ed_white_weight_min))
        ly_book = Colocacion.V().otro(ly_arr).otro(ly_abj)

        gb_white = Controles.GB(self, _("White book"), ly_book)

        # Black
        self.cb_black = Controles.CB(self, li_books, book_obj("BOOK_BLACK"))
        self.cb_mode_black = Controles.CB(self, li_modes, dic_data.get("MODE_BLACK"))
        lb_black_min = Controles.LB2P(self, _("Minimum percentage")).ponTipoLetra(puntos=8)
        self.ed_black_min = (Controles.ED(self).anchoFijo(60).
                             tipoFloat(decimales=3, valor=dic_data.get("PORC_BLACK", 0.0)).ponTipoLetra(puntos=8))
        lb_black_weight_min = Controles.LB2P(self, _("Minimum weight")).ponTipoLetra(puntos=8)
        self.ed_black_weight_min = (Controles.ED(self).anchoFijo(60).
                                  tipoInt(dic_data.get("WEIGHT_BLACK", 0)).ponTipoLetra(puntos=8))

        ly_arr = Colocacion.H().control(self.cb_black).control(self.cb_mode_black)
        ly_abj = (Colocacion.H().relleno().control(lb_black_min).control(self.ed_black_min)
                  .espacio(10)
                  .control(lb_black_weight_min).control(self.ed_black_weight_min))
        ly_book = Colocacion.V().otro(ly_arr).otro(ly_abj)

        gb_black = Controles.GB(self, _("Black book"), ly_book)

        layout_books = Colocacion.H().control(gb_white).control(gb_black)

        # Limits
        lb_limit_depth = Controles.LB2P(self, _("Max depth"))
        self.sb_limit_depth = Controles.SB(self, dic_data.get("MAX_DEPTH", 0), 0, 999)
        lb_limit_lines = Controles.LB2P(self, _("Max lines to parse"))
        self.sb_limit_lines = Controles.SB(self, dic_data.get("MAX_LINES", 0), 0, 99999)
        ly = Colocacion.G()
        ly.controld(lb_limit_depth, 0, 0)
        ly.control(self.sb_limit_depth, 0, 1)
        ly.controld(lb_limit_lines, 0, 2)
        ly.control(self.sb_limit_lines, 0, 3)

        no_limits = _("0=no limit")

        lb_info1 = Controles.LB(self, no_limits).ponTipoLetra(puntos=8)
        lb_info2 = Controles.LB(self, no_limits).ponTipoLetra(puntos=8)
        ly.control(lb_info1, 1, 1)
        ly.control(lb_info2, 1, 3)

        gb_limits = Controles.GB(self, _("Limits"), ly)

        for gb in (gb_white, gb_black, gb_limits):
            Code.configuration.set_property(gb, "1")

        vlayout = Colocacion.V()
        vlayout.otro(layout_books).espacio(15)
        vlayout.control(gb_limits)
        vlayout.margen(30)

        layout = Colocacion.V().control(tb).otro(vlayout).margen(3)

        self.setLayout(layout)

        self.restore_video()

    @staticmethod
    def read_dic_data():
        return Code.configuration.read_variables("OL_IMPORTPOLYGLOT")

    def write_dic_data(self):
        dic = {
            "BOOK_WHITE": self.cb_white.valor().to_dic(),
            "MODE_WHITE": self.cb_mode_white.valor(),
            "PORC_WHITE": self.ed_white_porc_min.textoFloat(),
            "WEIGHT_WHITE": self.ed_white_weight_min.textoInt(),
            "BOOK_BLACK": self.cb_black.valor().to_dic(),
            "MODE_BLACK": self.cb_mode_black.valor(),
            "PORC_BLACK": self.ed_black_min.textoFloat(),
            "WEIGHT_BLACK": self.ed_black_weight_min.textoInt(),
            "MAX_DEPTH": self.sb_limit_depth.valor(),
            "MAX_LINES": self.sb_limit_depth.valor(),
        }
        Code.configuration.write_variables("OL_IMPORTPOLYGLOT", dic)

    def aceptar(self):
        self.write_dic_data()
        if self.gen_lines():
            self.save_video()
            self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def register_books(self):
        WBooks.registered_books(self)
        self.list_books = Books.ListBooks()
        self.list_books.save()
        li = [(x.name, x) for x in self.list_books.lista]
        self.cb_white.rehacer(li, self.cb_white.valor())
        self.cb_black.rehacer(li, self.cb_black.valor())

    def gen_lines(self):
        book_w: Books.Book = self.cb_white.valor()
        book_b: Books.Book = self.cb_black.valor()
        mode_w = self.cb_mode_white.valor()
        mode_b = self.cb_mode_black.valor()
        limit_lines = self.sb_limit_lines.valor()
        limit_depth = self.sb_limit_depth.valor()
        start_fen = self.game.last_position.fen()

        porc_min_white = self.ed_white_porc_min.textoFloat()
        weight_min_white = self.ed_white_weight_min.textoInt()
        porc_min_black = self.ed_black_min.textoFloat()
        weight_min_black = self.ed_black_weight_min.textoInt()

        mens_work = _("Working...")
        mens_depth = _("Depth")
        mens_lines = _("Lines")
        um = QTUtil2.waiting_message.start(self, mens_work, if_cancel=True)
        um.end_with_canceled = False

        def dispatch(xdepth, xlines):
            if xlines:
                um.label(f"{mens_work}<br>{mens_depth}: {xdepth:d}<br>{mens_lines}: {xlines:d}")
            if um.cancelado():
                um.end_with_canceled = True
                return False
            return True

        lines = Polyglot.gen_lines(book_w.path, book_b.path, mode_w, mode_b,
                                   limit_lines, limit_depth, start_fen, dispatch,
                                   porc_min_white=porc_min_white, porc_min_black=porc_min_black,
                                   weight_min_white=weight_min_white, weight_min_black=weight_min_black)
        um.final()

        if um.end_with_canceled:
            return False

        if len(lines) == 0:
            QTUtil2.message_error(self, _("There is no lines"))
            return False

        um = QTUtil2.working(self)
        pv_init = self.game.pv()
        if pv_init:
            pv_init += " "

        li_pv = [pv_init + str(line) for line in lines]
        self.dbop.import_polyglot(li_pv)

        um.final()

        return True
