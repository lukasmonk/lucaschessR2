from Code import Util
from Code.Coordinates import CoordinatesBasic
from Code.Coordinates import CoordinatesConfig
from Code.Coordinates import WRunCoordinatesBasic
from Code.QT import Colocacion, Columnas, Controles, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog


class WCoordinatesBasic(LCDialog.LCDialog):
    def __init__(self, procesador):
        configuration = procesador.configuration
        path = configuration.file_coordinates()
        title = _("Coordinates")
        icon = Iconos.West()
        extconfig = "coordinatesbasic_1"
        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        self.db = CoordinatesBasic.DBCoordinatesBasic(path)
        self.config = CoordinatesConfig.CoordinatesConfig()

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE", _("Date"), 140, align_center=True)
        o_columns.nueva("SIDE", _("Side"), 100, align_center=True)
        o_columns.nueva("SCORE", _("Score"), 90, align_center=True)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        f = Controles.FontType(puntos=configuration.x_font_points)
        self.glista.set_font(f)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Play(), self.play),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Config"), Iconos.Configurar(), self.config_change),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.glista).margen(4)

        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 30, altoDefecto=340)

        self.glista.gotop()

    def config_change(self):
        self.config.change(self)

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
        is_white = QTVarios.white_or_black(self, False)
        if is_white is None:
            return
        w = WRunCoordinatesBasic.WRunCoordinatesBasic(self, self.db, is_white, self.config)
        w.exec_()
        self.db.refresh()
        self.glista.refresh()
