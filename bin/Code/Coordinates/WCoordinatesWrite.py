import Code
from Code import Util
from Code.Base.Constantes import WHITE, BLACK
from Code.Coordinates import CoordinatesWrite
from Code.Coordinates import WRunCoordinatesWrite
from Code.QT import Colocacion, Columnas, Controles, Grid, Iconos, QTUtil2, QTVarios
from Code.QT import LCDialog


class WCoordinatesWrite(LCDialog.LCDialog):
    def __init__(self, procesador):
        configuration = procesador.configuration
        title = f'{_("Coordinates")}: {_("Visualise and write")}'
        icon = Iconos.CoordinatesWrite()
        extconfig = "coordinateswrite_7"
        LCDialog.LCDialog.__init__(self, procesador.main_window, title, icon, extconfig)

        self.key = "COORDINATES_WRITE"

        self.dic_config = Code.configuration.read_variables(self.key)

        pieces = self.dic_config.get("PIECES", 1)
        side = self.dic_config.get("SIDE", WHITE)
        self.db = CoordinatesWrite.DBCoordinatesWrite(pieces, side)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE", _("Date"), 140)
        o_columns.nueva("DONE", _("Done"), 120, align_center=True)
        o_columns.nueva("ERRORS", _("Errors"), 90, align_center=True)
        o_columns.nueva("TIME", _("Time"), 140, align_center=True)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        f = Controles.FontType(puntos=configuration.x_font_points)
        self.glista.set_font(f)

        self.tb = QTVarios.LCTB(self)
        self.tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        self.tb.new(_("New"), Iconos.Pelicula_Seguir(), self.xplay, sep=False)
        self.tb.new(_("Continue"), Iconos.Pelicula_Pausa(), self.xcontinue)
        self.tb.new(_("Remove"), Iconos.Borrar(), self.borrar)

        lb_pieces = Controles.LB2P(self, _("Pieces"))
        li_options = [("1", 1), ("2", 2), ("4", 4), ("8", 8)]
        self.cb_pieces = Controles.CB(self, li_options, pieces).capture_changes(self.changes)

        lb_side = Controles.LB2P(self, _("Side"))
        li_options = [(_("White"), WHITE), (_("Black"), BLACK)]
        self.cb_side = Controles.CB(self, li_options, side).capture_changes(self.changes)

        ly_orden = Colocacion.H().relleno().control(lb_pieces).control(self.cb_pieces).espacio(30)
        ly_orden.control(lb_side).control(self.cb_side).relleno()

        ly = Colocacion.V().control(self.tb).otro(ly_orden).control(self.glista).margen(4)

        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 30, altoDefecto=540)

        self.glista.gotop()
        self.glista.refresh()
        self.changes()

    def changes(self):
        self.dic_config["PIECES"] =pieces = self.cb_pieces.valor()
        self.dic_config["SIDE"] = side = self.cb_side.valor()
        Code.configuration.write_variables(self.key, self.dic_config)
        self.db = CoordinatesWrite.DBCoordinatesWrite(pieces, side)
        self.glista.refresh()
        pending = self.db.pending()
        self.tb.set_action_visible(self.xplay, not pending)
        self.tb.set_action_visible(self.xcontinue, pending)

    def xplay(self):
        coord = CoordinatesWrite.CoordinatesWrite()
        self.run(coord)

    def xcontinue(self):
        coord = self.db.coordinate(0)
        if coord:
            self.run(coord)

    def run(self, coord:CoordinatesWrite.CoordinatesWrite):
        if not coord.pending():
            return
        w = WRunCoordinatesWrite.WRunCoordinatesWrite(self, self.db, coord)
        w.exec_()
        self.db.refresh()
        self.glista.refresh()
        self.changes()

    def grid_doble_click(self, grid, row, o_column):
        if row == 0:
            coord = self.db.coordinate(row)
            if coord.pending():
                self.xcontinue()

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
                self.changes()

    def grid_num_datos(self, grid):
        return len(self.db)

    def grid_dato(self, grid, row, o_column):
        coordinate: CoordinatesWrite.CoordinatesWrite = self.db.coordinate(row)
        col = o_column.key
        if col == "DATE":
            mens = "🏆" if coordinate.is_record else ""
            return Util.dtostr_hm(coordinate.date) + mens
        elif col == "DONE":
            return coordinate.str_done(self.cb_pieces.valor())
        elif col == "ERRORS":
            return f"{coordinate.errors}"
        elif col == "TIME":
            return coordinate.str_time()

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

