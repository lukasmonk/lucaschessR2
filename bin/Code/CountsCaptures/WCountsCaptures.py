import Code
from Code import Util
from Code.CountsCaptures import CountsCaptures, WRunCaptures, WRunCounts
from Code.Databases import DBgames, WindowDatabase
from Code.QT import Colocacion, Columnas, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog


class WCountsCaptures(LCDialog.LCDialog):
    def __init__(self, procesador, is_captures):
        self.configuration = procesador.configuration
        self.is_captures = is_captures
        if is_captures:
            path = self.configuration.file_captures()
            title = _("Captures and threats in a game")
            icon = Iconos.Captures()
            extconfig = "captures2"
        else:
            path = self.configuration.file_counts()
            title = _("Count moves")
            icon = Iconos.Count()
            extconfig = "counts2"

        self.db = CountsCaptures.DBCountCapture(path, is_captures)

        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE", _("Date"), 126, align_center=True)
        o_columns.nueva("CURRENT_MOVE", _("Current move"), 100, align_center=True)
        o_columns.nueva("MOVES", _("Moves"), 80, align_center=True)
        o_columns.nueva("%", _("Success"), 90, align_center=True)
        o_columns.nueva("TIME", _("Time"), 70, align_center=True)
        o_columns.nueva("AVG", _("Average"), 70, align_center=True)
        o_columns.nueva("GAME", _("Game"), 520)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        # f = Controles.FontType(puntos=self.configuration.x_font_points)
        # self.glista.set_font(f)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Play(), self.play),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
            (_("Repeat"), Iconos.Copiar(), self.repetir),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Options"), Iconos.Opciones(), self.options),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.glista).margen(4)

        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 32, altoDefecto=360)
        self.glista.gotop()

    def grid_doble_click(self, grid, row, o_column):
        self.play()

    def repetir(self):
        recno = self.glista.recno()
        if recno >= 0:
            capture = self.db.count_capture(recno)
            self.db.new_count_capture(capture.copy())
            self.glista.refresh()

    def new(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("random", _("Random"), Iconos.SQL_RAW())
        menu.separador()
        if not QTVarios.lista_db(Code.configuration, True).is_empty():
            menu.opcion("db", _("Game in a database"), Iconos.Database())
            menu.separador()
        menu.opcion("pgn", _("Game in a pgn"), Iconos.Filtrar())
        menu.separador()
        resp = menu.lanza()
        game = None
        if resp == "random":
            game = DBgames.get_random_game()
        elif resp == "pgn":
            game = Code.procesador.select_1_pgn(self)
        elif resp == "db":
            db = QTVarios.select_db(self, Code.configuration, True, False)
            if db:
                w = WindowDatabase.WBDatabase(self, Code.procesador, db, False, True)
                resp = w.exec_()
                if resp:
                    game = w.game
        if game is None:
            return
        capture = CountsCaptures.CountCapture(self.is_captures)
        capture.game = game
        self.db.new_count_capture(capture)
        self.glista.refresh()

    def borrar(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to delete all selected records?")
            if QTUtil2.pregunta(self, mens):
                self.db.remove_count_captures(li)
                recno = self.glista.recno()
                self.glista.refresh()
                if recno >= self.grid_num_datos(None):
                    self.glista.gobottom()

    def grid_num_datos(self, grid):
        return len(self.db)

    def grid_dato(self, grid, row, o_column):
        count_capture = self.db.count_capture(row)
        col = o_column.key
        if col == "DATE":
            return Util.dtostr_hm(count_capture.date)
        elif col == "GAME":
            return count_capture.game.titulo("DATE", "EVENT", "WHITE", "BLACK", "RESULT")
        elif col == "CURRENT_MOVE":
            if count_capture.is_finished():
                return _("Ended")
            return "%d+%d" % (count_capture.current_posmove, count_capture.current_depth)
        elif col == "MOVES":
            return "%d" % len(count_capture.game)
        elif col == "%":
            return count_capture.label_success()
        elif col == "TIME":
            return count_capture.label_time_used()
        elif col == "AVG":
            return count_capture.label_time_avg()
        else:
            return col

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    def play(self):
        recno = self.glista.recno()
        if recno >= 0:
            count_capture = self.db.count_capture(recno)
            if not count_capture.is_finished():
                if self.is_captures:
                    w = WRunCaptures.WRunCaptures(self, self.db, count_capture)
                else:
                    w = WRunCounts.WRunCounts(self, self.db, count_capture)
                w.exec_()

    def options(self):
        showall = self.configuration.x_captures_showall if self.is_captures else self.configuration.x_counts_showall
        menu = QTVarios.LCMenu(self)
        menu.opcion(True, _("Show all moves"), is_ckecked=showall)
        menu.separador()
        menu.opcion(False, _("Show last move"), is_ckecked=not showall)
        showall = menu.lanza()
        if showall is None:
            return

        if self.is_captures:
            self.configuration.x_captures_showall = showall
        else:
            self.configuration.x_counts_showall = showall
        self.configuration.graba()
