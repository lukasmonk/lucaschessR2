import copy
import os

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Board import Board
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
from Code.QT import QTVarios
from Code.QT import SelectFiles


class WTV_Marker(QtWidgets.QDialog):
    def __init__(self, owner, regMarker, xml=None, name=None):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Marker"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = Code.configuration

        if regMarker is None:
            regMarker = TabVisual.PMarker()
            regMarker.xml = xml
            if name:
                regMarker.name = name

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.grabar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Board
        config_board = owner.board.config_board
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Datos generales
        li_gen = []

        # name del svg que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        li_gen.append((config, regMarker.name))

        # ( "opacity", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        li_gen.append((config, 100 - int(regMarker.opacity * 100)))

        # ( "psize", "n", 100 ),
        config = FormLayout.Spinbox(_("Size") + " %", 1, 1600, 50)
        li_gen.append((config, regMarker.psize))

        # ( "poscelda", "n", 1 ),
        li = (
            ("%s-%s" % (_("Top"), _("Left")), 0),
            ("%s-%s" % (_("Top"), _("Right")), 1),
            ("%s-%s" % (_("Bottom"), _("Left")), 2),
            ("%s-%s" % (_("Bottom"), _("Right")), 3),
        )
        config = FormLayout.Combobox(_("Position in the square"), li)
        li_gen.append((config, regMarker.poscelda))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.list_zvalues())
        li_gen.append((config, regMarker.physical_pos.orden))

        self.form = FormLayout.FormWidget(li_gen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.board)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regMarker.a1h8 = a1h8
            regMarker.siMovible = True
            marker = self.board.creaMarker(regMarker, siEditando=True)
            self.liEjemplos.append(marker)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, marker in enumerate(self.liEjemplos):
                regMarker = marker.bloqueDatos
                regMarker.name = li[0]
                regMarker.opacity = (100.0 - float(li[1])) / 100.0
                regMarker.psize = li[2]
                regMarker.poscelda = li[3]
                regMarker.physical_pos.orden = li[4]
                marker.setOpacity(regMarker.opacity)
                marker.setZValue(regMarker.physical_pos.orden)
                marker.update()
            self.board.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regMarker = self.liEjemplos[0].bloqueDatos
        name = regMarker.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        pm = self.liEjemplos[0].pixmapX()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        regMarker.png = bytes(bf.buffer())

        self.regMarker = regMarker
        self.accept()


class WTV_Markers(LCDialog.LCDialog):
    def __init__(self, owner, list_markers, dbMarkers):

        titulo = _("Markers")
        icono = Iconos.Markers()
        extparam = "markers"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.FontType(puntos=8)

        self.configuration = Code.configuration
        self.liPMarkers = list_markers
        self.dbMarkers = dbMarkers

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 60, align_center=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="M", siSelecFilas=True)

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.mas),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            None,
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)
        tb.setFont(flb)

        ly = Colocacion.V().control(tb).control(self.grid)

        # Board
        config_board = self.configuration.config_board("EDIT_GRAPHICS", 48)
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Layout
        layout = Colocacion.H().otro(ly).control(self.board)
        self.setLayout(layout)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPMarkers)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "NUMBER":
            return str(row + 1)
        elif key == "NOMBRE":
            return self.liPMarkers[row].name

    def grid_doble_click(self, grid, row, o_column):
        self.modificar()

    def grid_cambiado_registro(self, grid, row, o_column):
        if row >= 0:
            regMarker = self.liPMarkers[row]
            self.board.borraMovibles()
            # Ejemplos
            liMovs = ["g4h3", "e2e4", "d6f4"]
            for a1h8 in liMovs:
                regMarker.a1h8 = a1h8
                regMarker.siMovible = True
                self.board.creaMarker(regMarker, siEditando=True)
            self.board.escena.update()

    def mas(self):

        menu = QTVarios.LCMenu(self)

        def seek_folder(submenu, folder):
            for entry in os.scandir(folder):
                if entry.is_dir():
                    smenu = submenu.submenu(entry.name, Iconos.Carpeta())
                    seek_folder(smenu, entry.path)
            for entry in os.scandir(folder):
                if entry.is_file() and entry.name.lower().endswith(".svg"):
                    ico = QTVarios.fsvg2ico(entry.path, 32)
                    if ico:
                        submenu.opcion(entry.path, entry.name[:-4], ico)

        seek_folder(menu, Code.path_resource("Imgs"))

        menu.separador()

        menu.opcion("@", _X(_("To seek %1 file"), "Marker"), Iconos.Fichero())

        resp = menu.lanza()

        if resp is None:
            return

        if resp == "@":
            file = SelectFiles.leeFichero(self, "imgs", "svg", titulo=_("Image"))
            if not file:
                return
        else:
            file = resp
        with open(file, "rt", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
        name = os.path.basename(file)[:-4]
        w = WTV_Marker(self, None, xml=contenido, name=name)
        if w.exec_():
            regMarker = w.regMarker
            regMarker.id = Util.huella_num()
            regMarker.ordenVista = (self.liPMarkers[-1].ordenVista + 1) if self.liPMarkers else 1
            self.dbMarkers[regMarker.id] = regMarker.save_dic()
            self.liPMarkers.append(regMarker)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), self.liPMarkers[row].name)):
                regMarker = self.liPMarkers[row]
                str_id = regMarker.id
                del self.liPMarkers[row]
                del self.dbMarkers[str_id]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        row = self.grid.recno()
        if row >= 0:
            w = WTV_Marker(self, self.liPMarkers[row])
            if w.exec_():
                regMarker = w.regMarker
                str_id = regMarker.id
                self.liPMarkers[row] = regMarker
                self.dbMarkers[str_id] = regMarker.save_dic()
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, row, None)

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            regMarker = copy.deepcopy(self.liPMarkers[row])
            n = 1

            def siEstaNombre(name):
                for rf in self.liPMarkers:
                    if rf.name == name:
                        return True
                return False

            name = "%s-%d" % (regMarker.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regMarker.name, n)
            regMarker.name = name
            regMarker.id = Util.huella_num()
            regMarker.ordenVista = self.liPMarkers[-1].ordenVista + 1
            self.dbMarkers[regMarker.id] = regMarker
            self.liPMarkers.append(regMarker)
            self.grid.refresh()
            self.grid.setFocus()

    def interchange(self, fila1, fila2):
        regMarker1, regMarker2 = self.liPMarkers[fila1], self.liPMarkers[fila2]
        regMarker1.ordenVista, regMarker2.ordenVista = regMarker2.ordenVista, regMarker1.ordenVista
        self.dbMarkers[regMarker1.id] = regMarker1
        self.dbMarkers[regMarker2.id] = regMarker2
        self.liPMarkers[fila1], self.liPMarkers[fila2] = self.liPMarkers[fila1], self.liPMarkers[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            self.interchange(row, row - 1)

    def abajo(self):
        row = self.grid.recno()
        if 0 <= row < (len(self.liPMarkers) - 1):
            self.interchange(row, row + 1)
