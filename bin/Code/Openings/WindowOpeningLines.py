import os
import os.path

from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Base import Game
from Code.Openings import WindowOpenings, OpeningLines
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WOpeningLines(LCDialog.LCDialog):
    def __init__(self, procesador):

        self.procesador = procesador
        self.configuration = procesador.configuration
        self.resultado = None
        self.listaOpenings = OpeningLines.ListaOpenings(self.configuration)

        LCDialog.LCDialog.__init__(
            self, procesador.main_window, self.getTitulo(), Iconos.OpeningLines(), "openingLines"
        )

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("TITLE", _("Name"), 240)
        o_columns.nueva("BASEPV", _("First moves"), 280)
        o_columns.nueva("NUMLINES", _("Lines"), 80, align_center=True)
        o_columns.nueva("FILE", _("File"), 200)
        self.glista = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)

        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Edit"), Iconos.Modificar(), self.modificar),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
            (_("Copy"), Iconos.Copiar(), self.copy),
            None,
            (_("Rename"), Iconos.Modificar(), self.renombrar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
            (_("Remove"), Iconos.Borrar(), self.grid_remove),
            None,
            (_("Update"), Iconos.Reiniciar(), self.reiniciar),
            None,
            (_("Folder"), Iconos.File(), self.changeFolder),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        tb.setSizePolicy(sp)

        li_acciones = (
            (_("Sequential"), Iconos.TrainSequential(), self.tr_sequential),
            None,
            (_("Static"), Iconos.TrainStatic(), self.tr_static),
            None,
            (_("Positions"), Iconos.TrainPositions(), self.tr_positions),
            None,
            (_("With engines"), Iconos.TrainEngines(), self.tr_engines),
        )
        self.tbtrain = tbtrain = Controles.TBrutina(self, li_acciones, with_text=False)

        lbtrain = Controles.LB(self, _("Trainings")).align_center()
        lbtrain.setStyleSheet("*{border: 1px solid #bababa;}")
        lytrain = Colocacion.V().control(lbtrain).control(tbtrain).margen(0)
        self.wtrain = QtWidgets.QWidget()
        self.wtrain.setLayout(lytrain)

        lytb = Colocacion.H().control(tb).control(self.wtrain).margen(0)
        wtb = QtWidgets.QWidget()
        wtb.setFixedHeight(66)
        wtb.setLayout(lytb)

        ly = Colocacion.V().control(wtb).control(self.glista).margen(4)

        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 20, altoDefecto=640)

        self.wtrain.setVisible(False)
        self.glista.gotop()
        self.glista.setFocus()

    def getTitulo(self):
        return "%s [%s]" % (_("Opening lines"), Code.relative_root(self.listaOpenings.folder))

    def tr_(self, tipo):
        recno = self.glista.recno()
        op = self.listaOpenings[recno]
        op["TRAIN"] = tipo
        self.resultado = op
        self.terminar()

    def tr_sequential(self):
        self.tr_("sequential")

    def tr_static(self):
        self.tr_("static")

    def tr_positions(self):
        self.tr_("positions")

    def tr_engines(self):
        self.tr_("engines")

    def reiniciar(self):
        self.listaOpenings.reiniciar()
        self.glista.refresh()
        self.glista.gotop()
        if len(self.listaOpenings) == 0:
            self.wtrain.setVisible(False)

    def changeFolder(self):
        nof = _("New opening folder")
        base = self.configuration.folder_base_openings
        li = [x for x in os.listdir(base) if os.path.isdir(os.path.join(base, x))]
        menu = QTVarios.LCMenu(self)
        rondo = QTVarios.rondoFolders()
        menu.opcion("", _("Home folder"), Iconos.Home())
        menu.separador()
        for x in li:
            menu.opcion(x, x, rondo.otro())
        menu.separador()
        menu.opcion(":n", nof, Iconos.Nuevo())
        if Code.is_windows:
            menu.separador()
            menu.opcion(":m", _("Direct maintenance"), Iconos.Configurar())

        resp = menu.lanza()
        if resp is not None:
            if resp == ":m":
                Code.startfile(base)
                return

            elif resp == ":n":
                name = ""
                error = ""
                while True:
                    li_gen = [FormLayout.separador]
                    li_gen.append((nof + ":", name))
                    if error:
                        li_gen.append(FormLayout.separador)
                        li_gen.append((None, error))

                    resultado = FormLayout.fedit(
                        li_gen, title=nof, parent=self, icon=Iconos.OpeningLines(), anchoMinimo=460
                    )
                    if resultado:
                        accion, liResp = resultado
                        name = liResp[0].strip()
                        if name:
                            path = os.path.join(base, name)
                            try:
                                os.mkdir(path)
                            except:
                                error = _("Unable to create the folder")
                                continue
                            if not os.path.isdir(path):
                                continue
                            break
                    else:
                        return
            else:
                path = os.path.join(base, resp)

            path = Util.relative_path(path)
            self.configuration.set_folder_openings(path)
            self.configuration.graba()
            self.listaOpenings = OpeningLines.ListaOpenings(self.configuration)
            self.glista.refresh()
            self.glista.gotop()
            if len(self.listaOpenings) == 0:
                self.wtrain.setVisible(False)
            self.setWindowTitle(self.getTitulo())

    def arriba(self):
        row = self.glista.recno()
        if self.listaOpenings.arriba(row):
            self.glista.goto(row - 1, 0)
            self.glista.refresh()

    def abajo(self):
        row = self.glista.recno()
        if self.listaOpenings.abajo(row):
            self.glista.goto(row + 1, 0)
            self.glista.refresh()

    def modificar(self):
        recno = self.glista.recno()
        if recno >= 0:
            self.resultado = self.listaOpenings[recno]
        else:
            self.resultado = None
        self.save_video()
        self.accept()

    def grid_doble_click(self, grid, row, o_column):
        recno = self.glista.recno()
        if recno >= 0:
            self.modificar()

    def new(self):
        si_expl = len(self.listaOpenings) < 4
        if si_expl:
            QTUtil2.message_bold(self, _("In the next dialog box, play the initial fixed moves for your opening."))
        w = WindowOpenings.WOpenings(self, self.configuration, None)
        if w.exec_():
            ap = w.resultado()
            pv = ap.a1h8 if ap else ""
            name = ap.tr_name if ap else ""
        else:
            return

        if si_expl:
            QTUtil2.message_bold(self, _("Now choose a name for this opening."))

        name = self.get_nombre(name)
        if name:
            file = self.listaOpenings.select_filename(name)
            self.listaOpenings.new(file, pv, name)
            self.resultado = self.listaOpenings[-1]
            self.save_video()
            self.accept()

    def copy(self):
        recno = self.glista.recno()
        if recno >= 0:
            self.listaOpenings.copy(recno)
            self.glista.refresh()

    def get_nombre(self, name):
        li_gen = [(None, None)]
        li_gen.append((_("Opening studio name") + ":", name))
        resultado = FormLayout.fedit(
            li_gen, title=_("Opening studio name"), parent=self, icon=Iconos.OpeningLines(), anchoMinimo=460
        )
        if resultado:
            accion, liResp = resultado
            name = liResp[0].strip()
            if name:
                return name
        return None

    def renombrar(self):
        row = self.glista.recno()
        if row >= 0:
            op = self.listaOpenings[row]
            name = self.get_nombre(op["title"])
            if name:
                self.listaOpenings.change_title(row, name)
                self.glista.refresh()

    def grid_remove(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to delete all selected records?")
            mens += "\n"
            for num, row in enumerate(li, 1):
                mens += "\n%d. %s" % (num, self.listaOpenings[row]["title"])
            if QTUtil2.pregunta(self, mens):
                self.wtrain.setVisible(False)
                li.sort(reverse=True)
                for row in li:
                    del self.listaOpenings[row]
                recno = self.glista.recno()
                self.glista.refresh()
                if recno >= len(self.listaOpenings):
                    self.glista.gobottom()

    def grid_num_datos(self, grid):
        return len(self.listaOpenings)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        op = self.listaOpenings[row]
        if col == "TITLE":
            return op["title"]
        elif col == "FILE":
            return op["file"]
        elif col == "NUMLINES":
            return op["lines"]
        elif col == "BASEPV":
            pv = op["pv"]
            if pv:
                p = Game.Game()
                p.read_pv(pv)
                return p.pgnBaseRAW()
            else:
                return ""

    def grid_cambiado_registro(self, grid, row, column):
        ok_ssp = False
        ok_eng = False
        if row >= 0:
            op = self.listaOpenings[row]
            num = op["lines"]
            num = int(num) if num else 0
            ok_ssp = op.get("withtrainings", False) and num > 0
            ok_eng = op.get("withtrainings_engines", False) and num > 0

        if ok_ssp or ok_eng:
            self.wtrain.setVisible(True)
            self.tbtrain.set_action_visible(self.tr_sequential, ok_ssp)
            self.tbtrain.set_action_visible(self.tr_static, ok_ssp)
            self.tbtrain.set_action_visible(self.tr_positions, ok_ssp)
            self.tbtrain.set_action_visible(self.tr_engines, ok_eng)
        else:
            self.wtrain.setVisible(False)

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()


class WStaticTraining(LCDialog.LCDialog):
    def __init__(self, procesador, dbop):
        self.training = dbop.training()
        self.ligames = self.training["LIGAMES_STATIC"]
        self.num_games = len(self.ligames)
        self.elems_fila = 10
        if self.num_games < self.elems_fila:
            self.elems_fila = self.num_games
        self.num_filas = (self.num_games - 1) / self.elems_fila + 1
        self.seleccionado = None

        titulo = "%s - %s" % (_("Opening lines"), _("Static training"))

        extparam = "openlines_static_%s" % dbop.nom_fichero

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, Iconos.TrainStatic(), extparam)

        lb = Controles.LB(self, dbop.gettitle())
        lb.set_background("#BDDBE8").align_center().ponTipoLetra(puntos=14)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)

        # Lista
        ancho = 42
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("FILA", "", 36, align_center=True)
        for x in range(self.elems_fila):
            o_columns.nueva("COL%d" % x, "%d" % (x + 1,), ancho, align_center=True, edicion=Delegados.PmIconosWeather())

        self.grid = Grid.Grid(self, o_columns, altoFila=ancho, background="white")
        self.grid.setAlternatingRowColors(False)
        self.grid.tipoLetra(puntos=10, peso=500)
        nAnchoPgn = self.grid.anchoColumnas() + 20
        self.grid.setMinimumWidth(nAnchoPgn)

        ly = Colocacion.V().control(lb).control(tb).control(self.grid)
        self.setLayout(ly)

        alto = self.num_filas * ancho + 146
        self.restore_video(siTam=True, altoDefecto=alto, anchoDefecto=nAnchoPgn)

    def terminar(self):

        self.save_video()
        self.reject()

    def grid_num_datos(self, grid):
        return self.num_filas

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "FILA":
            return "%d" % row
        elif col.startswith("COL"):
            num = row * self.elems_fila + int(col[3:])
            if num >= self.num_games:
                return None
            game = self.ligames[num]
            sinerror = game["NOERROR"]
            return str(sinerror) if sinerror < 4 else "4"

    def grid_doble_click(self, grid, row, o_column):
        col = o_column.key
        if col.startswith("COL"):
            num = row * self.elems_fila + int(col[3:])
            if num >= self.num_games:
                return
            self.seleccionado = num
            self.save_video()
            self.accept()


def select_static_line(procesador, dbop):
    w = WStaticTraining(procesador, dbop)
    w.exec_()
    return w.seleccionado


def openingLines(procesador):
    w = WOpeningLines(procesador)
    return w.resultado if w.exec_() else None


def select_line(owner):
    path = Code.configuration.folder_base_openings
    is_openings = False
    entry: os.DirEntry
    menu = QTVarios.LCMenuRondo(owner)
    for entry in os.scandir(path):
        if entry.is_dir():
            path_ini = os.path.join(entry.path, "openinglines.pk")
            lista = Util.restore_pickle(path_ini, [])
            if lista:
                is_openings = True
                submenu = menu.submenu(entry.name, Iconos.FolderAnil())
                for dic in lista:
                    dic["folder"] = entry.name
                    submenu.opcion(dic, dic["title"])

    path_ini = os.path.join(path, "openinglines.pk")
    lista = Util.restore_pickle(path_ini, [])
    if lista:
        is_openings = True
        for dic in lista:
            menu.opcion(dic, dic["title"])
    if is_openings:
        return menu.lanza()

    return None
