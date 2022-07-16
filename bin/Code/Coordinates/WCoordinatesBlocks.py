from Code import Util
from Code.QT import Colocacion, Columnas, Controles, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog

from Code.Coordinates import CoordinatesBlocks
from Code.Coordinates import WRunCoordinatesBlocks


class WCoordinatesBlocks(LCDialog.LCDialog):
    def __init__(self, procesador):
        configuration = procesador.configuration
        path = configuration.file_coordinates()
        title = _("Coordinates by blocks")
        icon = Iconos.Blocks()
        extconfig = "coordinatesbyblocks"
        self.db = CoordinatesBlocks.DBCoordinatesBlocks(path)

        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE_INI", _("Initial date"), 140, align_center=True)
        o_columns.nueva("DATE_END", _("End date"), 140, align_center=True)
        o_columns.nueva("DONE", _("Done"), 100, align_center=True)
        o_columns.nueva("TRIES", _("Tries"), 90, align_center=True)
        o_columns.nueva("SCORE", _("Score"), 90, align_center=True)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        f = Controles.TipoLetra(puntos=configuration.x_menu_points)
        self.glista.ponFuente(f)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Play(), self.play),
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

    def borrar(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to delete all selected records?")
            if QTUtil2.pregunta(self, mens):
                self.db.remove(li)
                recno = self.glista.recno()
                self.glista.refresh()
                if recno >= self.grid_num_datos(None):
                    self.glista.gotop()

    def grid_num_datos(self, grid):
        return len(self.db)

    def grid_dato(self, grid, row, o_column):
        coordinate: CoordinatesBlocks.CoordinatesBlocks = self.db.coordinate(row)
        col = o_column.key
        if col == "DATE_INI":
            return Util.dtostr_hm(coordinate.date_ini)
        elif col == "DATE_END":
            return Util.dtostr_hm(coordinate.date_end) if coordinate.date_end else ""
        elif col == "TRIES":
            return "%d" % coordinate.tries
        elif col == "DONE":
            return "%d/%d" % (coordinate.current_block, coordinate.num_blocks())
        elif col == "SCORE":
            return coordinate.min_score

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    def play(self):
        coord = self.db.last_coordinate()
        w = WRunCoordinatesBlocks.WRunCoordinatesBlocks(self, self.db, coord)
        w.exec_()
        self.db.refresh()
        self.glista.refresh()
