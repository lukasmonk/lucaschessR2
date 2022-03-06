from Code import Util
from Code.QT import Colocacion, Columnas, Controles, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog

from Code.Coordinates import CoordinatesBasic
from Code.Coordinates import WRunCoordinatesBasic


class WCoordinatesBasic(LCDialog.LCDialog):
    def __init__(self, procesador):
        configuration = procesador.configuration
        path = configuration.file_coordinates()
        title = _("Coordinates")
        icon = Iconos.West()
        extconfig = "coordinatesbasic"
        self.db = CoordinatesBasic.DBCoordinatesBasic(path)

        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE", _("Date"), 140, centered=True)
        o_columns.nueva("SIDE", _("Side"), 100, centered=True)
        o_columns.nueva("SCORE", _("Score"), 90, centered=True)
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
        coordinate: CoordinatesBasic.CoordinatesBasic = self.db.coordinate(row)
        col = o_column.key
        if col == "DATE":
            return Util.dtostr_hm(coordinate.date)
        elif col == "SIDE":
            return coordinate.str_side()
        elif col == "SCORE":
            return "%d" % coordinate.score

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    def play(self):
        is_white = QTVarios.blancasNegras(self)
        if is_white is None:
            return
        w = WRunCoordinatesBasic.WRunCoordinatesBasic(self, self.db, is_white)
        w.exec_()
        self.db.refresh()
        self.glista.refresh()
