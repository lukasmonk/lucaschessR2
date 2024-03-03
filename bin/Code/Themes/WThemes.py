import Code
from Code.Base import Move
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.Themes import Themes


class WThemes(LCDialog.LCDialog):
    def __init__(self, owner, themes: Themes.Themes, current_move: Move.Move):
        title = _("Select themes")
        extparam = "selelectthemes"

        self.owner = owner
        self.current_move = current_move

        self.st_current_themes = set(self.current_move.li_themes)

        icono = Iconos.Themes()
        LCDialog.LCDialog.__init__(self, owner, title, icono, extparam)

        self.themes = themes

        self.themes.verify(self.st_current_themes)
        self.qt_custom = QTUtil.qtColor("#bf5b16")

        self.configuration = Code.configuration

        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Clear all"), Iconos.Borrar(), self.clear_themes),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options, icon_size=24)

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SELECTED", "", 20, is_ckecked=True)
        o_columns.nueva("THEME", "", 280)

        self.o_columnas = o_columns
        self.grid = Grid.Grid(self, o_columns, is_editable=True, altoCabecera=4)

        lb_right_click = Controles.LB(self, " * %s" % _("More options with right-click"))

        layout = Colocacion.V().control(tb).control(self.grid).control(lb_right_click).margen(3)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=self.grid.anchoColumnas() + 48)

    def clear_themes(self):
        self.st_current_themes.clear()
        self.grid.refresh()

    def aceptar(self):
        self.current_move.li_themes = self.themes.order_themes(self.st_current_themes)
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.themes)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "SELECTED":
            return self.themes.key_pos(row) in self.st_current_themes
        elif key == "THEME":
            return self.themes.name_pos(row)

    def grid_setvalue(self, grid, row, o_column, value):
        if o_column.key == "SELECTED":
            theme = self.themes.key_pos(row)
            if theme in self.st_current_themes:
                self.st_current_themes.remove(theme)
            else:
                self.st_current_themes.add(theme)
            self.grid.refresh()

    def grid_bold(self, grid, row, col):
        theme = self.themes.key_pos(row)
        return self.themes.in_head(theme)

    def grid_color_texto(self, grid, row, col):
        theme = self.themes.key_pos(row)
        if self.themes.is_custom(theme):
            return self.qt_custom

    def grid_right_button(self, grid, row, col, modif):
        key = self.themes.key_pos(row)
        in_head = self.themes.in_head(key)
        is_custom = self.themes.is_custom(key)
        menu = QTVarios.LCMenu(self)
        if row:
            menu.opcion("head", _("Send to the head"), Iconos.Arriba())
            menu.separador()
        if in_head:
            menu.opcion("rem_head", _("Remove from the head"), Iconos.Abajo())
            menu.separador()
        if is_custom:
            menu.opcion("rem_custom", _("Remove this theme"), Iconos.Borrar())
            menu.separador()
        menu.opcion("add_custom", _("Add a custom theme"), Iconos.NuevoMas())
        resp = menu.lanza()
        if resp == "head":
            self.themes.add_head(key)
            self.grid.refresh()

        elif resp == "rem_head":
            self.themes.rem_head(key)
            self.grid.refresh()

        elif resp == "rem_custom":
            self.themes.rem_custom(key)
            self.grid.refresh()

        elif resp == "add_custom":
            self.add_custom()

    def add_custom(self):
        li_gen = [(None, None)]
        li_gen.append((_("Name") + ":", ""))
        resultado = FormLayout.fedit(
            li_gen, title=_("Add a custom theme"), parent=self, anchoMinimo=560, icon=Iconos.Themes()
        )

        if resultado:
            accion, li_gen = resultado
            txt_custom = li_gen[0].strip()
            if txt_custom:
                self.themes.add_custom(txt_custom)
                self.grid.refresh()
