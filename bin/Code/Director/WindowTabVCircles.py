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


class WTV_Circle(QtWidgets.QDialog):
    def __init__(self, owner, reg_circle):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Circle"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        if not reg_circle:
            reg_circle = TabVisual.PCircle()
        self.reg_circle = reg_circle

        li_acciones = [(_("Save"), Iconos.Aceptar(), "grabar"), None, (_("Cancel"), Iconos.Cancelar(), "reject"), None]
        tb = Controles.TB(self, li_acciones)

        # Board
        # config_board = Code.configuration.config_board("EDIT_GRAPHICS", 32)
        config_board = owner.board.config_board
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Datos generales
        li_gen = []

        # name del box que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        li_gen.append((config, reg_circle.name))

        # ( "tipo", "n", Qt.SolidLine ), #1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine
        config = FormLayout.Combobox(_("Line Type"), QTUtil2.lines_type())
        li_gen.append((config, reg_circle.tipo))

        # ( "color", "n", 0 ),
        config = FormLayout.Colorbox(_("Color"), 80, 20)
        li_gen.append((config, reg_circle.color))

        # ( "colorinterior", "n", -1 ),
        config = FormLayout.Colorbox(_("Internal color"), 80, 20, is_ckecked=True)
        li_gen.append((config, reg_circle.colorinterior))

        # ( "opacity", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        li_gen.append((config, 100 - int(reg_circle.opacity * 100)))

        # ( "grosor", "n", 1 ), # ancho del trazo
        config = FormLayout.Spinbox(_("Thickness"), 1, 20, 50)
        li_gen.append((config, reg_circle.grosor))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.list_zvalues())
        li_gen.append((config, reg_circle.physical_pos.orden))

        self.form = FormLayout.FormWidget(li_gen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.board)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            reg_circle.a1h8 = a1h8
            reg_circle.siMovible = True
            box = self.board.creaCircle(reg_circle)
            self.liEjemplos.append(box)

    def process_toolbar(self):
        accion = self.sender().key
        eval("self.%s()" % accion)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, box in enumerate(self.liEjemplos):
                reg_circle = box.bloqueDatos
                reg_circle.name = li[0]
                reg_circle.tipo = li[1]
                reg_circle.color = li[2]
                reg_circle.colorinterior = li[3]
                reg_circle.opacity = (100.0 - float(li[4])) / 100.0
                reg_circle.grosor = li[5]
                reg_circle.physical_pos.orden = li[6]
                box.setOpacity(reg_circle.opacity)
                box.setZValue(reg_circle.physical_pos.orden)
                box.update()
            self.board.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        reg_circle = self.liEjemplos[0].bloqueDatos
        name = reg_circle.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        self.reg_circle = reg_circle
        pm = self.liEjemplos[0].pixmap()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        self.reg_circle.png = bytes(bf.buffer())

        self.accept()


class WTV_Circles(LCDialog.LCDialog):
    def __init__(self, owner, list_circles, db_circles):

        titulo = _("Circles")
        icono = Iconos.Circle()
        extparam = "circles"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.FontType(puntos=8)

        self.lip_circles = list_circles
        self.configuration = Code.configuration

        self.db_circles = db_circles

        self.lip_circles = owner.list_circles()

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
        reg_circle = BoardTypes.Circle()
        for a1h8 in liMovs:
            reg_circle.a1h8 = a1h8
            reg_circle.siMovible = True
            circle = self.board.creaCircle(reg_circle)
            self.liEjemplos.append(circle)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.lip_circles)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "NUMBER":
            return str(row + 1)
        elif key == "NOMBRE":
            return self.lip_circles[row].name

    def grid_doble_click(self, grid, row, o_column):
        self.modificar()

    def grid_cambiado_registro(self, grid, row, o_column):
        if row >= 0:
            reg_circle = self.lip_circles[row]
            for ejemplo in self.liEjemplos:
                a1h8 = ejemplo.bloqueDatos.a1h8
                bd = copy.deepcopy(reg_circle)
                bd.a1h8 = a1h8
                bd.width_square = self.board.width_square
                ejemplo.bloqueDatos = bd
                ejemplo.reset()
            self.board.escena.update()

    def process_toolbar(self):
        accion = self.sender().key
        eval("self.%s()" % accion)

    def mas(self):
        w = WTV_Circle(self, None)
        if w.exec_():
            reg_circle = w.reg_circle
            reg_circle.id = Util.huella_num()
            reg_circle.ordenVista = (self.lip_circles[-1].ordenVista + 1) if self.lip_circles else 1
            self.db_circles[reg_circle.id] = reg_circle.save_dic()
            self.lip_circles.append(reg_circle)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete circle %1?"), self.lip_circles[row].name)):
                reg_circle = self.lip_circles[row]
                str_id = reg_circle.id
                del self.db_circles[str_id]
                del self.lip_circles[row]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        row = self.grid.recno()
        if row >= 0:
            w = WTV_Circle(self, self.lip_circles[row])
            if w.exec_():
                reg_circle = w.reg_circle
                str_id = reg_circle.id
                self.lip_circles[row] = reg_circle
                self.db_circles[str_id] = reg_circle.save_dic()
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, row, None)

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            reg_circle = copy.deepcopy(self.lip_circles[row])

            def siEstaNombre(name):
                for rf in self.lip_circles:
                    if rf.name == name:
                        return True
                return False

            n = 1
            name = "%s-%d" % (reg_circle.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (reg_circle.name, n)
            reg_circle.name = name
            reg_circle.id = Util.huella_num()
            reg_circle.ordenVista = self.lip_circles[-1].ordenVista + 1
            self.db_circles[reg_circle.id] = reg_circle
            self.lip_circles.append(reg_circle)
            self.grid.refresh()
            self.grid.setFocus()

    def interchange(self, fila1, fila2):
        reg_circle1, reg_circle2 = self.lip_circles[fila1], self.lip_circles[fila2]
        reg_circle1.ordenVista, reg_circle2.ordenVista = reg_circle2.ordenVista, reg_circle1.ordenVista
        self.db_circles[reg_circle1.id] = reg_circle1
        self.db_circles[reg_circle2.id] = reg_circle2
        self.lip_circles[fila1], self.lip_circles[fila2] = self.lip_circles[fila1], self.lip_circles[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            self.interchange(row, row - 1)

    def abajo(self):
        row = self.grid.recno()
        if 0 <= row < (len(self.lip_circles) - 1):
            self.interchange(row, row + 1)
