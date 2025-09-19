from PySide2 import QtCore, QtGui

import Code
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class EditCols(LCDialog.LCDialog):
    def __init__(self, grid_owner, work, col_reinit):

        LCDialog.LCDialog.__init__(self, grid_owner, _("Configure the columns"), Iconos.EditColumns(), "edit_columns")

        self.grid_owner = grid_owner
        self.o_columns_base = grid_owner.columnas()
        self.o_columns = self.o_columns_base.clone()
        self.o_columns_reinit = col_reinit

        self.configuration = Code.configuration
        self.work = work

        li_options = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Up"), Iconos.Arriba(), self.tw_up),
            (_("Down"), Iconos.Abajo(), self.tw_down),
            None,
            (_("Configurations"), Iconos.Configurar(), self.configurations),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options)

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SIMOSTRAR", "", 20, is_checked=True)
        o_columns.nueva("CLAVE", _("Key"), 80, align_center=True)
        o_columns.nueva("CABECERA", _("Title"), 150, edicion=Delegados.LineaTexto())
        o_columns.nueva("ANCHO", _("Width"), 60, edicion=Delegados.LineaTexto(is_integer=True), align_right=True)

        self.liAlin = [_("Left"), _("Center"), _("Right")]
        o_columns.nueva("ALINEACION", _("Alignment"), 100, align_center=True, edicion=Delegados.ComboBox(self.liAlin))
        o_columns.nueva("CTEXTO", _("Foreground"), 80, align_center=True)
        o_columns.nueva("CFONDO", _("Background"), 80, align_center=True)
        self.grid = Grid.Grid(self, o_columns, is_editable=True)

        self.register_grid(self.grid)

        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.resize(self.grid.anchoColumnas() + 48, 360)
        self.grid.goto(0, 1)

        self.restore_video()

    def tw_up(self):
        pos = self.grid.recno()
        if pos > 0:
            lic = self.o_columns.li_columns
            lic[pos], lic[pos - 1] = lic[pos - 1], lic[pos]
            for n, col in enumerate(lic):
                col.position = n

            self.grid.goto(pos - 1, 1)
            self.grid.refresh()

    def tw_down(self):
        pos = self.grid.recno()
        lic = self.o_columns.li_columns
        if pos < len(lic) - 1:
            lic[pos], lic[pos + 1] = lic[pos + 1], lic[pos]
            self.grid.goto(pos + 1, 1)
            self.grid.refresh()
            for n, col in enumerate(lic):
                col.position = n

    def configurations(self):
        dic_conf = self.configuration.read_variables(self.work)
        menu = QTVarios.LCMenu(self)
        menu.opcion(("new", None), _("Save with name"), Iconos.Grabar())
        menu.separador()
        if dic_conf:
            for pos, name in enumerate(dic_conf):
                submenu = menu.submenu(name, Iconos.PuntoAzul())
                submenu.opcion(("select", name), _("Choose"), Iconos.SelectAccept())
                submenu.opcion(("save", name), _("Save current"), Iconos.ModificarP())
                if pos:
                    submenu.opcion(("up", name), _("Up"), Iconos.Arriba())
                submenu.separador()
                submenu.opcion(("remove", name), _("Remove"), Iconos.Delete())
            menu.separador()
        if self.o_columns_reinit:
            menu.opcion(("reinit", None), _("Reinit"), Iconos.Reiniciar())
            menu.separador()

        resp = menu.lanza()
        if resp is None:
            return

        order, elem = resp
        if order == "reinit":
            self.o_columns = self.o_columns_reinit.clone()
            self.grid.refresh()

        elif order == "new":
            li_names = list(dic_conf.keys())
            name = QTUtil2.read_simple(self, _("Save"), _("Name"), "", width=240, li_values=li_names)
            if name:
                name = name.strip()
                if name:
                    if name in dic_conf:
                        if not QTUtil2.pregunta(
                                self,
                                name + "<br>" + _("This name already exists, what do you want to do?"),
                                label_yes=_("Overwrite"),
                                label_no=_("Cancel")
                        ):
                            return
                    dic_current = self.o_columns.save_dic(self.grid_owner)
                    dic_conf[name] = dic_current
                    self.configuration.write_variables(self.work, dic_conf)

        elif order == "remove":
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), elem)):
                del dic_conf[elem]
                Code.configuration.write_variables(self.work, dic_conf)

        elif order == "save":
            dic_current = self.o_columns.save_dic(self.grid_owner)
            dic_conf[elem] = dic_current
            self.configuration.write_variables(self.work, dic_conf)
            QTUtil2.temporary_message(self, _("Saved"), 1.0)

        elif order == "select":
            dic_current = dic_conf[elem]
            self.o_columns.restore_dic(dic_current, self.grid_owner)
            self.o_columns.li_columns.sort(key=lambda x: x.position)
            self.grid.refresh()

        elif order == "up":
            li_ord = list(dic_conf.keys())
            pos = li_ord.index(elem)
            li_ord[pos], li_ord[pos - 1] = li_ord[pos - 1], li_ord[pos]
            dic_nue = {key: dic_conf[key] for key in li_ord}
            Code.configuration.write_variables(self.work, dic_nue)

    def aceptar(self):
        self.save_video()
        self.grid_owner.o_columns = self.o_columns
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def closeEvent(self, event):
        self.save_video()

    def grid_num_datos(self, grid):
        return len(self.o_columns.li_columns)

    def grid_dato(self, grid, row, o_column):
        column = self.o_columns.li_columns[row]
        key = o_column.key
        if key == "SIMOSTRAR":
            return column.must_show
        elif key == "CLAVE":
            return column.key
        elif key == "CABECERA":
            return column.head
        elif key == "ALINEACION":
            pos = "icd".find(column.alineacion)
            return self.liAlin[pos]
        elif key == "ANCHO":
            return str(column.ancho)

        return _("Test")

    def grid_setvalue(self, grid, row, o_column, value):
        column = self.o_columns.li_columns[row]
        key = o_column.key
        if key == "SIMOSTRAR":
            column.must_show = not column.must_show
        elif key == "CABECERA":
            column.head = value
        elif key == "ALINEACION":
            pos = self.liAlin.index(value)
            column.alineacion = "icd"[pos]
        elif key == "ANCHO":
            ancho = int(value) if value else 0
            if ancho > 0:
                column.ancho = ancho

    def grid_color_texto(self, grid, row, col):
        column = self.o_columns.li_columns[row]
        if col.key in ("CTEXTO", "CFONDO"):
            color = column.rgb_foreground
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_color_fondo(self, grid, row, col):
        column = self.o_columns.li_columns[row]
        if col.key in ("CTEXTO", "CFONDO"):
            color = column.rgb_background
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_doble_click(self, grid, row, column):
        key = column.key
        column = self.o_columns.li_columns[row]
        if key in ["CTEXTO", "CFONDO"]:
            with_text = key == "CTEXTO"
            if with_text:
                negro = QtCore.Qt.black
                rgb = column.rgb_foreground
                color = negro if rgb == -1 else QtGui.QColor(rgb)
                color = QTVarios.select_color(color)
                if color:
                    column.rgb_foreground = -1 if color == negro else color.rgb()
            else:
                blanco = QtCore.Qt.white
                rgb = column.rgb_background
                color = blanco if rgb == -1 else QtGui.QColor(rgb)
                color = QTVarios.select_color(color)
                if color:
                    column.rgb_background = -1 if color == blanco else color.rgb()
            column.set_qt()

    def grid_right_button(self, grid, row, col, modif):
        key = col.key
        col = self.o_columns.li_columns[row]
        if key in ["CTEXTO", "CFONDO"]:
            with_text = key == "CTEXTO"
            if with_text:
                col.rgb_foreground = -1
            else:
                col.rgb_background = -1
            col.set_qt()
