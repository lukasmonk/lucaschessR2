from PySide2 import QtCore, QtGui, QtWidgets

from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class EditCols(QtWidgets.QDialog):
    def __init__(self, grid_owner, configuration, work):
        QtWidgets.QDialog.__init__(self, grid_owner)
        self.setWindowTitle(_("Edit columns"))
        self.setWindowIcon(Iconos.EditColumns())

        self.grid_owner = grid_owner
        self.o_columnas_base = grid_owner.columnas()
        self.o_columnas = self.o_columnas_base.clone()

        self.configuration = configuration
        self.work = work

        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
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
        o_columns.nueva("SIMOSTRAR", "", 20, siChecked=True)
        o_columns.nueva("CLAVE", _("Key"), 80, centered=True)
        o_columns.nueva("CABECERA", _("Title"), 150, edicion=Delegados.LineaTexto())
        o_columns.nueva("ANCHO", _("Width"), 60, edicion=Delegados.LineaTexto(siEntero=True), siDerecha=True)

        self.liAlin = [_("Left"), _("Center"), _("Right")]
        o_columns.nueva("ALINEACION", _("Alignment"), 100, centered=True, edicion=Delegados.ComboBox(self.liAlin))
        o_columns.nueva("CTEXTO", _("Foreground"), 80, centered=True)
        o_columns.nueva("CFONDO", _("Background"), 80, centered=True)
        self.grid = Grid.Grid(self, o_columns, siEditable=True)

        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.resize(self.grid.anchoColumnas() + 48, 360)
        self.grid.goto(0, 1)

    def tw_up(self):
        pos = self.grid.recno()
        if pos > 0:
            lic = self.o_columnas.li_columns
            lic[pos], lic[pos - 1] = lic[pos - 1], lic[pos]
            for n, col in enumerate(lic):
                col.position = n

            self.grid.goto(pos - 1, 1)
            self.grid.refresh()

    def tw_down(self):
        pos = self.grid.recno()
        lic = self.o_columnas.li_columns
        if pos < len(lic) - 1:
            lic[pos], lic[pos + 1] = lic[pos + 1], lic[pos]
            self.grid.goto(pos + 1, 1)
            self.grid.refresh()
            for n, col in enumerate(lic):
                col.position = n

    def configurations(self):
        dic_conf = self.configuration.read_variables(self.work)
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Save"), Iconos.ManualSave())
        submenu.opcion("save_name", _("Save with name"), Iconos.Grabar())
        submenu.separador()
        submenu.opcion("save_default", _("Save as default"), Iconos.Defecto())
        menu.separador()
        menu.opcion("reinit", _("Reinit"), Iconos.Reiniciar())
        menu.separador()
        if dic_conf:
            menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
            for name in dic_conf:
                menu.opcion(name, name, Iconos.PuntoAzul())

        resp = menu.lanza()
        if resp is None:
            return

        elif resp == "save_name":
            form = FormLayout.FormLayout(self, _("Name"), Iconos.Opciones(), anchoMinimo=240)
            form.separador()

            form.edit(_("Name"), "")

            resultado = form.run()
            if resultado:
                accion, resp = resultado
                name = resp[0].strip()
                if name:
                    dic_current = self.o_columnas.save_dic(self.grid_owner)
                    dic_conf[name] = dic_current
                    self.configuration.write_variables(self.work, dic_conf)

        elif resp == "save_default":
            key = "databases_columns_default"
            dic_current = self.o_columnas.save_dic(self.grid_owner)
            self.configuration.write_variables(key, dic_current)

        elif resp == "reinit":
            dic_current = self.o_columnas_base.save_dic(self.grid_owner)
            self.o_columnas.restore_dic(dic_current, self.grid_owner)
            self.o_columnas.li_columns.sort(key=lambda x: x.position)
            self.grid.refresh()

        else:
            if menu.siDer:
                if QTUtil2.pregunta(self, _X(_("Delete %1?"), resp)):
                    del dic_conf[resp]
                    self.configuration.write_variables(self.work, dic_conf)
            else:
                dic_current = dic_conf[resp]
                self.o_columnas.restore_dic(dic_current, self.grid_owner)
                self.o_columnas.li_columns.sort(key=lambda x: x.position)
                self.grid.refresh()

    def aceptar(self):
        self.grid_owner.o_columns = self.o_columnas
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.o_columnas.li_columns)

    def grid_dato(self, grid, row, o_column):
        column = self.o_columnas.li_columns[row]
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
        column = self.o_columnas.li_columns[row]
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
        column = self.o_columnas.li_columns[row]
        if col.key in ("CTEXTO", "CFONDO"):
            color = column.rgbTexto
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_color_fondo(self, grid, row, col):
        column = self.o_columnas.li_columns[row]
        if col.key in ("CTEXTO", "CFONDO"):
            color = column.rgbFondo
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_doble_click(self, grid, row, column):
        key = column.key
        column = self.o_columnas.li_columns[row]
        if key in ["CTEXTO", "CFONDO"]:
            with_text = key == "CTEXTO"
            if with_text:
                negro = QtCore.Qt.black
                rgb = column.rgbTexto
                color = negro if rgb == -1 else QtGui.QColor(rgb)
                color = QtWidgets.QColorDialog.getColor(color, self)
                if color.isValid():
                    column.rgbTexto = -1 if color == negro else color.rgb()
            else:
                blanco = QtCore.Qt.white
                rgb = column.rgbFondo
                color = blanco if rgb == -1 else QtGui.QColor(rgb)
                color = QtWidgets.QColorDialog.getColor(color, self)
                if color.isValid():
                    column.rgbFondo = -1 if color == blanco else color.rgb()
            column.ponQT()

    def grid_right_button(self, grid, row, col, modif):
        key = col.key
        col = self.o_columnas.li_columns[row]
        if key in ["CTEXTO", "CFONDO"]:
            with_text = key == "CTEXTO"
            if with_text:
                col.rgbTexto = -1
            else:
                col.rgbFondo = -1
            col.ponQT()
