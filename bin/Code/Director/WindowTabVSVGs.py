import copy
import os

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
from Code.QT import QTVarios
from Code.QT import SelectFiles

estrellaSVG = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   version="1.1"
   width="64"
   height="64"
   id="svg2996">
  <defs
     id="defs2998" />
  <metadata
     id="metadata3001">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     id="layer1">
    <path
       d="M 27.169733,29.728386 C 25.013244,32.2821 14.66025,23.129153 11.578235,24.408078 8.4962206,25.687003 6.6393909,39.1341 3.3071401,38.993129 -0.02511049,38.852157 0.91445325,26.949682 -1.9446847,25.158604 c -2.8591381,-1.791078 -15.0810253,3.34372 -17.0117283,0.569017 -1.930702,-2.774702 8.403637,-10.308248 8.19374,-13.566752 -0.209897,-3.2585049 -10.936253,-10.0036344 -9.712288,-13.06583173 1.223964,-3.06219717 12.0590479,-0.21386597 14.474209,-2.52953107 2.4151612,-2.3156652 0.7741756,-15.3362732 3.9137487,-16.2517622 3.139573,-0.915489 6.1950436,10.0329229 9.4593203,10.280471 3.264277,0.2475482 11.944248,-8.425366 14.803863,-6.774742 2.859615,1.650623 -1.726822,13.0796387 0.03239,15.84516339 1.759209,2.76552481 12.739744,3.15253011 13.354311,6.42891241 0.614567,3.2763822 -10.178057,6.5799722 -11.316244,9.7437452 -1.138187,3.163774 5.079588,11.337377 2.923098,13.891092 z"
       transform="matrix(1.0793664,0,0,1.021226,24.134217,21.975315)"
       id="path3024"
       style="fill:none;stroke:#136ad6;stroke-width:2.29143548;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
  </g>
</svg>"""


class WTV_SVG(QtWidgets.QDialog):
    def __init__(self, owner, regSVG, xml=None, name=None):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Image"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuration = Code.configuration

        if not regSVG:
            regSVG = TabVisual.PSVG()
            regSVG.xml = xml
            if name:
                regSVG.name = name

        tb = Controles.TBrutina(self)
        tb.new(_("Save"), Iconos.Aceptar(), self.grabar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.reject)

        # Board
        config_board = owner.board.config_board
        self.board = Board.Board(self, config_board, with_director=False)
        self.board.crea()
        self.board.copiaPosicionDe(owner.board)

        # Datos generales
        li_gen = []

        # name del svg que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        li_gen.append((config, regSVG.name))

        # ( "opacity", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        li_gen.append((config, 100 - int(regSVG.opacity * 100)))

        # ( "psize", "n", 100 ),
        config = FormLayout.Spinbox(_("Size") + " %", 1, 1600, 50)
        li_gen.append((config, regSVG.psize))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.list_zvalues())
        li_gen.append((config, regSVG.physical_pos.orden))

        self.form = FormLayout.FormWidget(li_gen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.board)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regSVG.a1h8 = a1h8
            regSVG.siMovible = True
            svg = self.board.creaSVG(regSVG, siEditando=True)
            self.liEjemplos.append(svg)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, svg in enumerate(self.liEjemplos):
                regSVG = svg.bloqueDatos
                regSVG.name = li[0]
                regSVG.opacity = (100.0 - float(li[1])) / 100.0
                regSVG.psize = li[2]
                regSVG.physical_pos.orden = li[3]
                svg.setOpacity(regSVG.opacity)
                svg.setZValue(regSVG.physical_pos.orden)
                svg.update()
            self.board.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regSVG = self.liEjemplos[0].bloqueDatos
        name = regSVG.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        self.regSVG = regSVG

        pm = self.liEjemplos[0].pixmapX()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        self.regSVG.png = bytes(bf.buffer())

        self.accept()


class WTV_SVGs(LCDialog.LCDialog):
    def __init__(self, owner, list_svgs, dbSVGs):

        titulo = _("Images")
        icono = Iconos.SVGs()
        extparam = "svgs"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.FontType(puntos=8)

        self.configuration = Code.configuration
        self.liPSVGs = list_svgs
        self.dbSVGs = dbSVGs

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 60, align_center=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="M", siSelecFilas=True)

        tb = Controles.TBrutina(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("New"), Iconos.Nuevo(), self.mas)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)
        tb.new(_("Modify"), Iconos.Modificar(), self.modificar)
        tb.new(_("Copy"), Iconos.Copiar(), self.copiar)
        tb.new(_("Up"), Iconos.Arriba(), self.arriba)
        tb.new(_("Down"), Iconos.Abajo(), self.abajo)
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

        # Ejemplos
        liMovs = ["g4h3", "e2e2", "d6f4"]
        self.liEjemplos = []
        regSVG = BoardTypes.SVG()
        for a1h8 in liMovs:
            regSVG.a1h8 = a1h8
            regSVG.xml = estrellaSVG
            regSVG.siMovible = True
            svg = self.board.creaSVG(regSVG, siEditando=True)
            self.liEjemplos.append(svg)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPSVGs)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "NUMBER":
            return str(row + 1)
        elif key == "NOMBRE":
            return self.liPSVGs[row].name

    def grid_doble_click(self, grid, row, o_column):
        self.modificar()

    def grid_cambiado_registro(self, grid, row, o_column):
        if row >= 0:
            regSVG = self.liPSVGs[row]
            for ejemplo in self.liEjemplos:
                a1h8 = ejemplo.bloqueDatos.a1h8
                bd = copy.deepcopy(regSVG)
                bd.a1h8 = a1h8
                bd.width_square = self.board.width_square
                ejemplo.bloqueDatos = bd
                ejemplo.reset()
            self.board.escena.update()

    def mas(self):

        menu = QTVarios.LCMenu(self)

        def look_folder(submenu, base, dr):
            if base:
                pathCarpeta = base + dr + "/"
                smenu = submenu.submenu(dr, Iconos.Carpeta())
            else:
                pathCarpeta = dr + "/"
                smenu = submenu
            li = []
            for fich in os.listdir(pathCarpeta):
                pathFich = pathCarpeta + fich
                if os.path.isdir(pathFich):
                    look_folder(smenu, pathCarpeta, fich)
                elif pathFich.lower().endswith(".svg"):
                    li.append((pathFich, fich))

            for pathFich, fich in li:
                ico = QTVarios.fsvg2ico(pathFich, 32)
                if ico:
                    smenu.opcion(pathFich, fich[:-4], ico)

        look_folder(menu, Code.folder_resources + "/", "imgs")

        menu.separador()

        menu.opcion("@", _X(_("To seek %1 file"), "SVG"), Iconos.Fichero())

        resp = menu.lanza()

        if resp is None:
            return

        if resp == "@":
            key = "SVG_GRAPHICS"
            dic = self.configuration.read_variables(key)
            folder = dic.get("FOLDER", self.configuration.carpeta)
            file = SelectFiles.leeFichero(self, folder, "svg", titulo=_("Image"))
            if not file or not os.path.isfile(file):
                return
            dic["FOLDER"] = os.path.dirname(file)
            self.configuration.write_variables(key, dic)
        else:
            file = resp
        with open(file, "rt", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
        name = os.path.basename(file)[:-4]
        w = WTV_SVG(self, None, xml=contenido, name=name)
        if w.exec_():
            reg_svg = w.regSVG
            reg_svg.id = Util.huella_num()
            reg_svg.ordenVista = (self.liPSVGs[-1].ordenVista + 1) if self.liPSVGs else 1
            self.dbSVGs[reg_svg.id] = reg_svg.save_dic()
            self.liPSVGs.append(reg_svg)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), self.liPSVGs[row].name)):
                regSVG = self.liPSVGs[row]
                str_id = regSVG.id
                del self.liPSVGs[row]
                del self.dbSVGs[str_id]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        row = self.grid.recno()
        if row >= 0:
            w = WTV_SVG(self, self.liPSVGs[row])
            if w.exec_():
                regSVG = w.regSVG
                str_id = regSVG.id
                self.liPSVGs[row] = regSVG
                self.dbSVGs[str_id] = regSVG.save_dic()
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, row, None)

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            regSVG = copy.deepcopy(self.liPSVGs[row])
            n = 1

            def siEstaNombre(name):
                for rf in self.liPSVGs:
                    if rf.name == name:
                        return True
                return False

            name = "%s-%d" % (regSVG.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regSVG.name, n)
            regSVG.name = name
            regSVG.id = Util.huella_num()
            regSVG.ordenVista = self.liPSVGs[-1].ordenVista + 1
            self.dbSVGs[regSVG.id] = regSVG
            self.liPSVGs.append(regSVG)
            self.grid.refresh()
            self.grid.setFocus()

    def interchange(self, fila1, fila2):
        regSVG1, regSVG2 = self.liPSVGs[fila1], self.liPSVGs[fila2]
        regSVG1.ordenVista, regSVG2.ordenVista = regSVG2.ordenVista, regSVG1.ordenVista
        self.dbSVGs[regSVG1.id] = regSVG1
        self.dbSVGs[regSVG2.id] = regSVG2
        self.liPSVGs[fila1], self.liPSVGs[fila2] = self.liPSVGs[fila1], self.liPSVGs[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            self.interchange(row, row - 1)

    def abajo(self):
        row = self.grid.recno()
        if 0 <= row < (len(self.liPSVGs) - 1):
            self.interchange(row, row + 1)
