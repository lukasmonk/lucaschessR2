from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SingularMoves import SingularMoves


class WSingularM(LCDialog.LCDialog):
    def __init__(self, owner, configuration):
        self.configuration = configuration
        titulo = "%s: %s" % (_("Singular moves"), _("Calculate your strength"))
        icono = Iconos.Strength()
        extparam = "singularmoves"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.sm = SingularMoves.SingularMoves(configuration.ficheroSingularMoves)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.cerrar),
            None,
            (_("New"), Iconos.Empezar(), self.nuevo),
            None,
            (_("Repeat"), Iconos.Pelicula_Repetir(), self.repetir),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("N", _("N."), 60, align_center=True)
        o_columns.nueva("DATE", _("Date"), 120, align_center=True)
        o_columns.nueva("STRENGTH", _("Strength"), 80, align_center=True)
        o_columns.nueva("REPETITIONS", _("Repetitions"), 80, align_center=True)
        o_columns.nueva("BEST", _("Best repetition"), 120, align_center=True)
        self.grid = grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        grid.coloresAlternados()
        self.register_grid(grid)

        ly = Colocacion.V().control(tb).control(grid).margen(3)

        self.setLayout(ly)

        grid.gotop()
        self.restore_video(anchoDefecto=510, altoDefecto=640)

    def cerrar(self):
        self.save_video()
        self.reject()

    def nuevo(self):
        self.save_video()
        self.sm.current = -1
        self.sm.nuevo_bloque()
        self.accept()

    def repetir(self):
        row = self.grid.recno()
        if row >= 0:
            self.save_video()
            self.sm.repite(row)
            self.accept()

    def borrar(self):
        li = self.grid.recnosSeleccionados()
        if li and QTUtil2.pregunta(self, _("Are you sure?")):
            self.sm.borra_db(li)
            self.grid.refresh()
            self.grid.goto(li[0] if li[0] < self.sm.len_db() else 0, 0)

    def grid_num_datos(self, grid):
        return self.sm.len_db()

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "N":
            return "%d" % (row + 1,)
        if col == "DATE":
            key = self.sm.db_keys[row]
            return "%s-%s-%s %s:%s" % (key[:4], key[4:6], key[6:8], key[8:10], key[10:12])
        registro = self.sm.reg_db(row)
        if col == "STRENGTH":
            return "%0.2f" % registro.get("STRENGTH", 0.0)
        if col == "BEST":
            rep = registro.get("REPETITIONS", [])
            if len(rep):
                return "%0.2f" % registro.get("BEST", 0.0)
            else:
                return ""
        if col == "REPETITIONS":
            rep = registro.get("REPETITIONS", [])
            return len(rep) if len(rep) else ""

    def grid_doble_click(self, grid, row, column):
        self.repetir()
