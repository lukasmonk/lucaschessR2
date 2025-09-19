import Code
from Code.Base import Move
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WThemes(LCDialog.LCDialog):
    def __init__(self, owner, current_move: Move.Move):
        title = _("Select themes")
        extparam = "selelectthemes"

        self.owner = owner
        self.current_move = current_move

        self.st_current_themes = set(self.current_move.li_themes)

        icono = Iconos.Themes()
        LCDialog.LCDialog.__init__(self, owner, title, icono, extparam)

        self.themes = Code.get_themes()

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
        o_columns.nueva("SELECTED", "", 20, is_checked=True)
        o_columns.nueva("THEME", "", 280)
        o_columns.nueva("SHOW", "", 30, edicion=Delegados.EtiquetaPGN(None))

        self.o_columnas = o_columns
        self.grid = Grid.Grid(self, o_columns, is_editable=True, altoCabecera=4)

        lb_right_click = Controles.LB(self, " * %s" % _("More options with right-click"))

        layout = Colocacion.V().control(tb).control(self.grid).control(lb_right_click).margen(3)
        self.setLayout(layout)

        self.restore_video(default_width=self.grid.anchoColumnas() + 48, default_height=640)

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
        elif key == "SHOW":
            return "", "", "", "|" + self.themes.key_pos(row), None

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
        menu.separador()
        menu.opcion("change_abbr", _("Change abbreviation"), Iconos.Abreviatura())
        menu.separador()
        menu.opcion("change_color", _("Change colour"), Iconos.Colores())
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

        elif resp == "change_abbr":
            self.change_abbreviation(key)

        elif resp == "change_color":
            self.change_color(key)

    def change_abbreviation(self, theme_key):
        abbr = self.themes.get_letters(theme_key)
        new = QTUtil2.read_simple(self, _("Change abbreviation"), _("Abbreviation"), abbr)
        if new is None:
            return
        self.themes.change_custom_letters(theme_key, new.strip())

    def change_color(self, theme_key):
        color_prev = self.themes.get_color(theme_key)
        color = QTVarios.select_color(color_prev)
        if color:
            self.themes.change_custom_color(theme_key, color)

    def add_custom(self):
        txt_custom = QTUtil2.read_simple(self, _("Add a custom theme"), _("Name"), "")
        if txt_custom and txt_custom.strip():
            self.themes.add_custom(txt_custom.strip())
            self.grid.refresh()
