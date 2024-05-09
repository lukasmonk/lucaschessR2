import copy

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Board import Board, BoardTypes
from Code.Director import TabVisual
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2


class WTV_Marco(QtWidgets.QDialog):
    def __init__(self, owner, regMarco):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Box"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        if not regMarco:
            regMarco = TabVisual.PMarco()

        li_acciones = [(_("Save"), Iconos.Aceptar(), "grabar"), None, (_("Cancel"), Iconos.Cancelar(), "reject"), None]
        tb = Controles.TB(self, li_acciones)

        # Board
        config_board = Code.configuration.config_board("EDIT_GRAPHICS", 32)
        config_board = owner.board.config_board
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Datos generales
        li_gen = []

        # name del box que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        li_gen.append((config, regMarco.name))

        # ( "tipo", "n", Qt.SolidLine ), #1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine
        config = FormLayout.Combobox(_("Line Type"), QTUtil2.lines_type())
        li_gen.append((config, regMarco.tipo))

        # ( "color", "n", 0 ),
        config = FormLayout.Colorbox(_("Color"), 80, 20)
        li_gen.append((config, regMarco.color))

        # ( "colorinterior", "n", -1 ),
        config = FormLayout.Colorbox(_("Internal color"), 80, 20, is_ckecked=True)
        li_gen.append((config, regMarco.colorinterior))

        # ( "opacity", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        li_gen.append((config, 100 - int(regMarco.opacity * 100)))

        # ( "grosor", "n", 1 ), # ancho del trazo
        config = FormLayout.Spinbox(_("Thickness"), 1, 20, 50)
        li_gen.append((config, regMarco.grosor))

        # ( "redEsquina", "n", 0 ),
        config = FormLayout.Spinbox(_("Rounded corners"), 0, 100, 50)
        li_gen.append((config, regMarco.redEsquina))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.list_zvalues())
        li_gen.append((config, regMarco.physical_pos.orden))

        self.form = FormLayout.FormWidget(li_gen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.board)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regMarco.a1h8 = a1h8
            regMarco.siMovible = True
            box = self.board.creaMarco(regMarco)
            self.liEjemplos.append(box)

    def process_toolbar(self):
        accion = self.sender().key
        eval("self.%s()" % accion)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, box in enumerate(self.liEjemplos):
                regMarco = box.bloqueDatos
                regMarco.name = li[0]
                regMarco.tipo = li[1]
                regMarco.color = li[2]
                regMarco.colorinterior = li[3]
                # regMarco.colorinterior2 = li[]
                regMarco.opacity = (100.0 - float(li[4])) / 100.0
                regMarco.grosor = li[5]
                regMarco.redEsquina = li[6]
                regMarco.physical_pos.orden = li[7]
                box.setOpacity(regMarco.opacity)
                box.setZValue(regMarco.physical_pos.orden)
                box.update()
            self.board.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regMarco = self.liEjemplos[0].bloqueDatos
        name = regMarco.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        self.regMarco = regMarco
        pm = self.liEjemplos[0].pixmap()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        self.regMarco.png = bytes(bf.buffer())

        self.accept()


class WTV_Marcos(LCDialog.LCDialog):
    def __init__(self, owner, list_boxes, dbMarcos):

        titulo = _("Boxes")
        icono = Iconos.Marcos()
        extparam = "marcos"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.FontType(puntos=8)

        self.liPMarcos = list_boxes
        self.configuration = Code.configuration

        self.dbMarcos = dbMarcos

        self.liPMarcos = owner.list_boxes()

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 60, align_center=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="M", siSelecFilas=True)

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), "terminar"),
            None,
            (_("New"), Iconos.Nuevo(), "mas"),
            None,
            (_("Remove"), Iconos.Borrar(), "borrar"),
            None,
            (_("Modify"), Iconos.Modificar(), "modificar"),
            None,
            (_("Copy"), Iconos.Copiar(), "copiar"),
            None,
            (_("Up"), Iconos.Arriba(), "arriba"),
            None,
            (_("Down"), Iconos.Abajo(), "abajo"),
            None,
        ]
        tb = Controles.TB(self, li_acciones)
        tb.setFont(flb)

        ly = Colocacion.V().control(tb).control(self.grid)

        # Board
        config_board = Code.configuration.config_board("EDIT_GRAPHICS", 48)
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Layout
        layout = Colocacion.H().otro(ly).control(self.board)
        self.setLayout(layout)

        self.register_grid(self.grid)
        self.restore_video()

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        regMarco = BoardTypes.Marco()
        for a1h8 in liMovs:
            regMarco.a1h8 = a1h8
            regMarco.siMovible = True
            box = self.board.creaMarco(regMarco)
            self.liEjemplos.append(box)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPMarcos)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "NUMBER":
            return str(row + 1)
        elif key == "NOMBRE":
            return self.liPMarcos[row].name

    def grid_doble_click(self, grid, row, o_column):
        self.modificar()

    def grid_cambiado_registro(self, grid, row, o_column):
        if row >= 0:
            regMarco = self.liPMarcos[row]
            for ejemplo in self.liEjemplos:
                a1h8 = ejemplo.bloqueDatos.a1h8
                bd = copy.deepcopy(regMarco)
                bd.a1h8 = a1h8
                bd.width_square = self.board.width_square
                ejemplo.bloqueDatos = bd
                ejemplo.reset()
            self.board.escena.update()

    def process_toolbar(self):
        accion = self.sender().key
        eval("self.%s()" % accion)

    def mas(self):
        w = WTV_Marco(self, None)
        if w.exec_():
            regMarco = w.regMarco
            regMarco.id = Util.huella_num()
            regMarco.ordenVista = (self.liPMarcos[-1].ordenVista + 1) if self.liPMarcos else 1
            self.dbMarcos[regMarco.id] = regMarco.save_dic()
            self.liPMarcos.append(regMarco)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete box %1?"), self.liPMarcos[row].name)):
                regMarco = self.liPMarcos[row]
                str_id = regMarco.id
                del self.dbMarcos[str_id]
                del self.liPMarcos[row]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        row = self.grid.recno()
        if row >= 0:
            w = WTV_Marco(self, self.liPMarcos[row])
            if w.exec_():
                regMarco = w.regMarco
                str_id = regMarco.id
                self.liPMarcos[row] = regMarco
                self.dbMarcos[str_id] = regMarco.save_dic()
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, row, None)

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            regMarco = copy.deepcopy(self.liPMarcos[row])

            def siEstaNombre(name):
                for rf in self.liPMarcos:
                    if rf.name == name:
                        return True
                return False

            n = 1
            name = "%s-%d" % (regMarco.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regMarco.name, n)
            regMarco.name = name
            regMarco.id = Util.huella_num()
            regMarco.ordenVista = self.liPMarcos[-1].ordenVista + 1
            self.dbMarcos[regMarco.id] = regMarco
            self.liPMarcos.append(regMarco)
            self.grid.refresh()
            self.grid.setFocus()

    def interchange(self, fila1, fila2):
        regMarco1, regMarco2 = self.liPMarcos[fila1], self.liPMarcos[fila2]
        regMarco1.ordenVista, regMarco2.ordenVista = regMarco2.ordenVista, regMarco1.ordenVista
        self.dbMarcos[regMarco1.id] = regMarco1
        self.dbMarcos[regMarco2.id] = regMarco2
        self.liPMarcos[fila1], self.liPMarcos[fila2] = self.liPMarcos[fila1], self.liPMarcos[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            self.interchange(row, row - 1)

    def abajo(self):
        row = self.grid.recno()
        if 0 <= row < (len(self.liPMarcos) - 1):
            self.interchange(row, row + 1)
