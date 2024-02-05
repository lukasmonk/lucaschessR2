from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code import Util
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTVarios


class WColors(LCDialog.LCDialog):
    def __init__(self, procesador):

        LCDialog.LCDialog.__init__(self, procesador.main_window, _("Colors"), Iconos.Colores(), "wcolors2")

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.qbackground_none = QtGui.QColor("#b3b3b3")
        self.qforeground_none = QtGui.QColor("#030303")

        file = "By default" if self.configuration.x_style_mode is None else self.configuration.x_style_mode
        path_original = Code.path_resource("Styles", file + ".colors")
        dic = Util.ini_base2dic(path_original)
        self.dic_original = {key: QTUtil.qtColor(value) for key, value in dic.items()}

        path_personal = self.configuration.file_colors()
        dic = Util.ini_base2dic(path_personal, rfind_equal=True)
        self.dic_personal = {key: QTUtil.qtColor(value) for key, value in dic.items()}

        self.li_colors = self.read_colors_template()
        self.li_colors.extend(self.read_qss())

        self.li_ctrl_z = []

        self.translation = {
            "border": _("Border"),
            "color": _("Color"),
            "border-color": _("Border"),
            "background-color": _("Background"),
            "background": _("Background"),
            "Background": _("Background"),
            "foreground": _("Foreground"),
            "Foreground": _("Foreground"),
            "No result": _("No result"),
            "Moves in PGN table": _("Moves in PGN table"),
            "Selected move in PGN table": _("Selected move in PGN table"),
            "Windows with PGN": _("Windows with PGN"),
            "Numbers": _("Numbers"),
            "Selected move": _("Selected move"),
            "Other moves": _("Other moves"),
            "Various": _("Various"),
            "Ephemeral message window": _("Ephemeral message window"),
            "alternate-background-color": _("Alternate background color"),
            "Links": _("Links"),
            "Brilliant move": _("Brilliant move"),
            "Good move": _("Good move"),
            "Interesting move": _("Interesting move"),
            "Dubious move": _("Dubious move"),
            "Mistake": _("Mistake"),
            "Blunder": _("Blunder"),
            "Messages in the middle of some boards (coordinate training/captures/...)": _(
                "Messages in the middle of some boards (coordinate training/captures/...)"),
            "Engines that change of division": _("Engines that change of division"),
            "Configuration, selected engines, 1st division": _("Configuration, selected engines, 1st division"),
            "Configuration, selected engines, 2nd division": _("Configuration, selected engines, 2nd division"),
            "Configuration, selected engines, 3rd division": _("Configuration, selected engines, 3rd division"),
            "Even lines": _("Even lines"),
            "Odd lines": _("Odd lines"),
            "Line numbers": _("Line numbers"),
            "Stage foreground": _("Stage foreground"),
            "Stage background": _("Stage background"),
            "Track foreground": _("Track foreground"),
            "Track background": _("Track background"),
            "State foreground": _("State foreground"),
            "State background": _("State background"),
            "Next task foreground": _("Next task foreground"),
            "Background colour of next task if playing": _("Background colour of next task if playing"),
            "Background colour of next task if endings": _("Background colour of next task if endings"),
            "Background colour of next task if tactical": _("Background colour of next task if tactical"),
            "Time foreground": _("Time foreground"),
            "Time background": _("Time background"),
            "Date foreground": _("Date foreground"),
            "Date background": _("Date background"),
            "Border when enable": _("Border when enable"),
            "Foreground when enable": _("Foreground when enable"),
            "Background when enable": _("Background when enable"),
            "Border when disable": _("Border when disable"),
            "Foreground when disable": _("Foreground when disable"),
            "Background when disable": _("Background when disable"),
            "Analysis Bar": _("Analysis Bar")
        }

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NAME", _("Name"), 340)
        o_columns.nueva("ORIGINAL", _("Original"), 120, align_center=True)
        o_columns.nueva("PERSONAL", _("Current"), 120, align_center=True)
        self.grid = Grid.Grid(self, o_columns, alternate=False, siCabeceraMovible=False)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        status = Controles.LB(
            self, "%s\n%s\n%s" % (_("[Mouse Double click] in column CURRENT to change color"),
                                  _("[Mouse double click] in column ORIGINAL to change all with this color"),
                                  _("[DEL key] in column CURRENT to remove change"))
        )

        # Tool bar
        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Remove all"), Iconos.Borrar(), self.remove_all),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        ly_tb = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(ly_tb).control(self.grid).control(status).margen(3)

        self.setLayout(ly)

        self.register_grid(self.grid)
        self.grid.resizeColumnToContents(0)
        self.restore_video(anchoDefecto=self.grid.anchoColumnas() + 24, altoDefecto=QTUtil.desktop_height() * 2 // 3)

        self.grid.gotop()
        for row, (is_head, key, value) in enumerate(self.li_colors):
            if is_head:
                self.grid.setSpan(row, 0, 1, 3)

    def grid_doble_click(self, grid, row, col):
        is_head, key, value = self.li_colors[row]
        if is_head:
            return

        if col.key == "PERSONAL":
            qcolor_previo = self.dic_personal.get(key)
            if qcolor_previo is None:
                qcolor_previo = self.dic_original[key]
            qcolor_nuevo = QtWidgets.QColorDialog.getColor(qcolor_previo, self, _("Choose a color"),
                                                           QtWidgets.QColorDialog.ShowAlphaChannel | QtWidgets.QColorDialog.DontUseNativeDialog)
            if qcolor_nuevo.isValid():
                if qcolor_previo.name() != qcolor_nuevo.name():
                    self.li_ctrl_z.append(["add", key, self.dic_personal.get(key)])
                    self.dic_personal[key] = qcolor_nuevo
                    self.grid.goto(row, 0)
                    self.grid.refresh()

        elif col.key == "ORIGINAL":
            qcolor_previo = self.dic_original[key]
            qcolor_nuevo = QtWidgets.QColorDialog.getColor(qcolor_previo, self, _("Choose a color"),
                                                           QtWidgets.QColorDialog.ShowAlphaChannel | QtWidgets.QColorDialog.DontUseNativeDialog)

            if qcolor_nuevo.isValid():
                color_original = qcolor_previo.name()
                remove = qcolor_previo.name() == qcolor_nuevo.name()
                self.li_ctrl_z.append(["end", None, None])
                for is_head, key, value in self.li_colors:
                    if is_head:
                        continue
                    if self.dic_original[key].name() == color_original:
                        if remove:
                            if self.dic_personal.get(key):
                                self.li_ctrl_z.append(["rem", key, self.dic_personal.get(key)])
                                del self.dic_personal[key]
                        else:
                            self.li_ctrl_z.append(["add", key, self.dic_personal.get(key)])
                            self.dic_personal[key] = QtGui.QColor(qcolor_nuevo.name())
                self.li_ctrl_z.append(["begin", None, None])
                self.grid.goto(row, 0)
                self.grid.refresh()

    def grid_alineacion(self, grid, row, column):
        is_head, key, value = self.li_colors[row]
        if column.key == "PERSONAL":
            return "c"
        if is_head:
            return "l"
        return "d"

    def grid_color_texto(self, grid, row, o_column):
        is_head, key, value = self.li_colors[row]
        if is_head:
            return QTUtil.qtColor("white")
        elif o_column.key == "PERSONAL":
            return self.qforeground_none

    def grid_bold(self, grid, row, o_column):
        is_head, key, value = self.li_colors[row]
        return is_head

    def grid_color_fondo(self, grid, row, o_column):
        is_head, key, value = self.li_colors[row]
        if is_head:
            return QTUtil.qtColor("darkcyan")
        if o_column.key == "ORIGINAL":
            return self.dic_original[key]
        elif o_column.key == "PERSONAL":
            return self.dic_personal.get(key, self.qbackground_none)

    def grid_num_datos(self, grid):
        return len(self.li_colors)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        is_head, key, value = self.li_colors[row]
        if col == "NAME":
            def trans(x):
                if Code.translations.is_key(x):
                    return _F(x)
                if x in self.translation:
                    return self.translation[x]
                for c in "|+ ":
                    if x.count(c) == 1:
                        uno, dos = x.split(c)
                        return trans(uno) + " - " + trans(dos)
                return _F(x)

            return trans(value)

        elif col == "PERSONAL":
            return "" if key in self.dic_personal else "--"

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):

        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            row = self.grid.recno()
            is_head, key, value = self.li_colors[row]
            if is_head or row < 0 or key not in self.dic_personal:
                return
            self.li_ctrl_z.append(["rem", key, self.dic_personal[key]])
            del self.dic_personal[key]
            self.grid.refresh()

        elif is_control and k == QtCore.Qt.Key_Z:
            if self.li_ctrl_z:
                action, key, previous = self.li_ctrl_z.pop()
                if action == "begin":
                    until_end = True
                    action, key, previous = self.li_ctrl_z.pop()
                else:
                    until_end = False
                while True:
                    if previous:
                        self.dic_personal[key] = previous
                    else:
                        del self.dic_personal[key]
                    if until_end:
                        action, key, previous = self.li_ctrl_z.pop()
                        if action == "end":
                            break
                    else:
                        break
                self.grid.refresh()
        return True

    def cancelar(self):
        self.save_video()
        self.reject()

    def aceptar(self):
        path_personal = self.configuration.file_colors()
        dic = {key: color.name() for key, color in self.dic_personal.items()}
        Util.dic2ini_base(path_personal, dic)
        self.save_video()
        self.accept()

    @staticmethod
    def read_colors_template():
        path_template = Code.path_resource("Styles", "colors.template")
        dic = Util.ini2dic(path_template)
        li = []
        for k, v in dic.items():
            li.append([True, k, k])
            for key, value in v.items():
                li.append([False, key, value])
        return li

    def read_qss(self):
        style = "By default" if self.configuration.x_style_mode is None else self.configuration.x_style_mode
        path_qss = Code.path_resource("Styles", style + ".qss")
        li = []
        with open(path_qss, "rt") as f:
            current = None
            with_elements = False
            for line in f:
                line = line.strip()
                if line and not line.startswith("/"):
                    if current is None:
                        current = line
                        with_elements = False
                    elif line == "}":
                        current = None
                    elif "#" in line:
                        key, value = line.split(":")
                        key = key.strip()
                        color = "#" + value.split("#")[1][:6]
                        key_gen = "%s|%s" % (current, key)
                        if style == "By default" and "[" not in current:
                            continue
                        if not with_elements:
                            with_elements = True
                            li.append([True, current, current])
                        li.append([False, key_gen, key])
                        self.dic_original[key_gen] = QTUtil.qtColor(color)
        return li

    def remove_all(self):
        self.li_ctrl_z.append(["end", None, None])
        for key, value in self.dic_personal.items():
            self.li_ctrl_z.append(["rem", key, value])
        self.li_ctrl_z.append(["begin", None, None])
        self.dic_personal = {}
        self.grid.refresh()
        self.grid.gotop()
        self.grid.setFocus()
