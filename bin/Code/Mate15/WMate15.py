from Code import Util
from Code.QT import Colocacion, Columnas, Controles, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog

from Code.Mate15 import Mate15, WRunMate15


class WMate15(LCDialog.LCDialog):
    def __init__(self, procesador):
        configuration = procesador.configuration
        path = configuration.file_mate15()
        title = _X(_("Mate in %1"), "1½")
        icon = Iconos.Mate15()
        extconfig = "mate15"
        self.db = Mate15.DBMate15(path)

        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("POS", _("N."), 70, centered=True)
        o_columns.nueva("DATE", _("Date"), 120, centered=True)
        o_columns.nueva("INFO", _("Information"), 360)
        o_columns.nueva("TRIES", _("Tries"), 70, centered=True)
        o_columns.nueva("RESULT", _("Result"), 70, centered=True)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, altoFila=configuration.x_pgn_rowheight)
        f = Controles.TipoLetra(puntos=configuration.x_pgn_fontpoints)
        self.glista.ponFuente(f)

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
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.glista).margen(4)

        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 30)

        self.glista.gotop()

    def grid_doble_click(self, grid, row, o_column):
        self.play()

    def repetir(self):
        recno = self.glista.recno()
        if recno >= 0:
            mate15 = self.db.mate15(recno)
            self.db.repeat(mate15)
            self.glista.refresh()

    def new(self):
        self.db.create_new()
        self.glista.refresh()
        self.glista.gotop()
        self.play()

    def borrar(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to delete all selected records?")
            if QTUtil2.pregunta(self, mens):
                self.db.remove_mate15(li)
                recno = self.glista.recno()
                self.glista.refresh()
                if recno >= self.grid_num_datos(None):
                    self.glista.gotop()

    def grid_num_datos(self, grid):
        return len(self.db)

    def grid_dato(self, grid, row, o_column):
        m15 = self.db.mate15(row)
        col = o_column.key
        if col == "DATE":
            return Util.dtostr_hm(m15.date)
        elif col == "POS":
            return "%d" % (m15.pos + 1,)
        elif col == "INFO":
            return m15.info
        elif col == "TRIES":
            return "%d" % m15.num_tries()
        elif col == "RESULT":
            num_tries = m15.num_tries()
            if num_tries == 0:
                return ""
            else:
                min_tm = m15.result()
                return '%.01f"' % min_tm if min_tm else ""

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    def play(self):
        recno = self.glista.recno()
        if recno >= 0:
            m15 = self.db.mate15(recno)
            w = WRunMate15.WRunMate15(self, self.db, m15)
            w.exec_()
            self.glista.refresh()
