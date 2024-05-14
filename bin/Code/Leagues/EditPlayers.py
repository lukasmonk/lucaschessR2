from Code.Engines import SelectEngines
from Code.QT import Colocacion
from Code.QT import Grid, Columnas, Delegados
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WEditPlayers(LCDialog.LCDialog):
    def __init__(self, owner, li_players):
        self.owner = owner
        icono = Iconos.Player()
        extparam = "WEditPlayers"
        LCDialog.LCDialog.__init__(self, owner, _("Players"), icono, extparam)

        self.li_players = li_players

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NAME", _("Name"), 150, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("ENGINE", _("Engine"), 200)
        self.grid = Grid.Grid(self, o_columns, is_editable=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        tb = QTVarios.LCTB(self)
        tb.new(_("Save"), Iconos.Aceptar(), self.save)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancel)

        layout = Colocacion.V()
        layout.control(tb).control(self.grid)
        self.setLayout(layout)

        self.register_grid(self.grid)

        self.restore_video(altoDefecto=560)
        self.grid.setFocus()
        self.changed = False

    def aceptar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.save_video()

    def grid_num_datos(self, grid):
        return len(self.li_players)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        player = self.li_players[row]
        if col == "NAME":
            return player.name()
        return _("Human") if player.is_human() else player.opponent.path_exe

    def grid_setvalue(self, grid, row, o_column, value):
        col = o_column.key
        player = self.li_players[row]
        value = value.strip()
        if col != "NAME" or not value:
            return
        player.set_name(value)
        self.changed = True

    def grid_doble_click(self, grid, row, o_column):
        col = o_column.key
        if col == "ENGINE":
            select = SelectEngines.SelectEngines(self)
            engine = select.menu(self)
            if engine:
                player = self.li_players[row]
                player.set_engine(engine)
                self.changed = True

    def grid_right_button(self, grid, row, o_column, modif):
        col = o_column.key
        if row < 0:
            return
        player = self.li_players[row]
        if col == "NAME":
            resp = QTUtil2.read_simple(self, _("Name"), _("Name"), player.name(), width=400)
            if resp is not None:
                self.grid_setvalue(grid, row, o_column, resp)
        elif col == "ENGINE":
            self.grid_doble_click(grid, row, o_column)
            return

    def save(self):
        self.save_video()
        self.accept()

    def cancel(self):
        self.save_video()
        self.reject()
