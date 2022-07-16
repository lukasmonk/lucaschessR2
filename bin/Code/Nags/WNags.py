import Code
from Code.Base import Move
from Code.Nags import Nags
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import LCDialog


class WNags(LCDialog.LCDialog):
    def __init__(self, owner, nags: Nags.Nags, current_move: Move.Move):
        title = _("Ratings")
        extparam = "selelectnags"

        self.owner = owner
        self.current_move = current_move

        self.st_current_nags = set(self.current_move.li_nags)

        self.nags = nags
        icono = self.nags.ico(14, 16)

        LCDialog.LCDialog.__init__(self, owner, title, icono, extparam)

        self.configuration = Code.configuration

        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Clear all"), Iconos.Borrar(), self.clear_nags),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options, icon_size=24)

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SELECTED", "", 20, siChecked=True)
        o_columns.nueva("ICON", "", 16, edicion=Delegados.PmIconosBMT(self, self.nags.dic_pm(), x=8))
        o_columns.nueva("NUMBER", "", 30, align_center=True)
        o_columns.nueva("TITLE", "", 240)

        self.o_columnas = o_columns
        self.grid = Grid.Grid(self, o_columns, is_editable=True, altoCabecera=4)
        font = Controles.TipoLetra(puntos=Code.configuration.x_pgn_fontpoints)
        self.grid.ponFuente(font)

        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=self.grid.anchoColumnas() + 48)

    def clear_nags(self):
        self.st_current_nags.clear()
        self.grid.refresh()

    def aceptar(self):
        self.current_move.li_nags = list(self.st_current_nags)
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.nags)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        nag = self.nags[row]
        if key == "SELECTED":
            return nag in self.st_current_nags
        elif key == "ICON":
            return str(nag)
        elif key == "NUMBER":
            return "$%d" % nag
        elif key == "TITLE":
            return self.nags.title(nag)

    def grid_setvalue(self, grid, row, o_column, value):
        if o_column.key == "SELECTED":
            nag = self.nags[row]
            if nag in self.st_current_nags:
                self.st_current_nags.remove(nag)
            else:
                self.st_current_nags.add(nag)
            self.grid.refresh()
