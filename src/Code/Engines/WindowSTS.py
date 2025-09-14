import os
import shutil
import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util
from Code.Base import Position
from Code.Board import Board
from Code.Engines import WEngines, STS, SelectEngines
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios


class WRun(LCDialog.LCDialog):
    def __init__(self, w_parent, sts, work, procesador, with_board):
        titulo = "%s - %s - %s" % (sts.name, work.ref, work.path_to_exe())
        icono = Iconos.STS()
        extparam = "runsts"
        if with_board:
            extparam += "2"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.work = work
        self.sts = sts
        self.ngroup = -1
        self.xengine = procesador.creaManagerMotor(work.config_engine(), work.seconds * 1000, work.depth)
        if not with_board:
            self.xengine.set_direct()
        self.playing = False
        self.configuration = procesador.configuration
        self.with_board = with_board

        # Toolbar
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.cerrar),
            None,
            (_("Run"), Iconos.Run(), self.run),
            (_("Pause"), Iconos.Pelicula_Pausa(), self.pause),
            None,
        ]
        self.tb = tb = Controles.TBrutina(self, li_acciones, icon_size=24)

        if with_board:
            # Board
            config_board = self.configuration.config_board("STS", 32)
            self.board = Board.Board(self, config_board)
            self.board.crea()

        # Area resultados
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("GROUP", _("Group"), 180)
        o_columns.nueva("DONE", _("Done"), 100, align_center=True)
        o_columns.nueva("WORK", work.ref, 120, align_center=True)

        self.dworks = self.read_works()
        self.calc_max()
        for x in range(len(self.sts.works) - 1, -1, -1):
            work = self.sts.works.get_work(x)
            if work != self.work:
                key = "OTHER%d" % x
                reg = self.dworks[key]
                o_columns.nueva(key, reg.title, 120, align_center=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)

        self.colorMax = QTUtil.qtColor("#840C24")
        self.colorOth = QTUtil.qtColor("#4668A6")

        layout = Colocacion.H()
        if with_board:
            layout.control(self.board)
        layout.control(self.grid)
        layout.margen(3)

        ly = Colocacion.V().control(tb).otro(layout)

        self.setLayout(ly)

        self.restore_video(with_tam=True, default_width=800, default_height=430)

        resp = self.sts.siguiente_posicion(self.work)
        if resp:
            self.tb.set_action_visible(self.pause, False)
            self.tb.set_action_visible(self.run, True)
        else:
            self.tb.set_action_visible(self.pause, False)
            self.tb.set_action_visible(self.run, False)

    def cerrar(self):
        self.sts.save()
        self.xengine.terminar()
        self.save_video()
        self.playing = False
        self.accept()

    def closeEvent(self, event):
        self.cerrar()

    def run(self):
        self.tb.set_action_visible(self.pause, True)
        self.tb.set_action_visible(self.run, False)
        QTUtil.refresh_gui()
        self.playing = True
        while self.playing:
            self.siguiente()

    def pause(self):
        self.tb.set_action_visible(self.pause, False)
        self.tb.set_action_visible(self.run, True)
        QTUtil.refresh_gui()
        self.playing = False
        self.sts.save()

    def siguiente(self):
        resp = self.sts.siguiente_posicion(self.work)
        if resp:
            ngroup, self.nfen, self.elem = resp
            if ngroup != self.ngroup:
                self.calc_max()
                self.grid.refresh()
                self.ngroup = ngroup
            xpt, xa1h8 = self.elem.best_a1_h8()
            if self.with_board:
                cp = Position.Position()
                cp.read_fen(self.elem.fen)
                self.board.set_position(cp)
                self.xengine.set_gui_dispatch(self.dispatch)
                self.board.remove_arrows()
                self.board.put_arrow_sc(xa1h8[:2], xa1h8[2:4])
                QTUtil.refresh_gui()
            if not self.playing:
                return
            t0 = time.time()
            mrm = self.xengine.analiza(self.elem.fen)
            t1 = time.time() - t0
            if mrm:
                rm = mrm.best_rm_ordered()
                if rm:
                    mov = rm.movimiento()
                    if mov:
                        if self.with_board:
                            self.board.creaFlechaTmp(rm.from_sq, rm.to_sq, False)
                        self.sts.set_result(self.work, self.ngroup, self.nfen, mov, t1)
                        self.grid.refresh()
            else:
                self.pause()

        else:
            self.sts.save()
            self.calc_max()
            self.grid.refresh()
            self.tb.set_action_visible(self.pause, False)
            self.tb.set_action_visible(self.run, False)
            self.playing = False

        QTUtil.refresh_gui()

    def dispatch(self, rm):
        if rm.from_sq:
            self.board.creaFlechaTmp(rm.from_sq, rm.to_sq, False)
        QTUtil.refresh_gui()
        return self.playing

    def grid_num_datos(self, grid):
        return len(self.sts.groups)

    def grid_bold(self, grid, row, o_column):
        column = o_column.key
        if column.startswith("OTHER") or column == "WORK":
            return self.dworks[column].labels[row].is_max
        return False

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        group = self.sts.groups.group(row)
        if column == "GROUP":
            return group.name
        elif column == "DONE":
            return self.sts.done_positions(self.work, row)
        elif column == "WORK":
            return self.sts.done_points(self.work, row)
        elif column.startswith("OTHER"):
            return self.dworks[column].labels[row].label

    def read_work(self, work):
        tm = '%d"' % work.seconds if work.seconds else ""
        dp = "%d^" % work.depth if work.depth else ""
        r = Util.Record()
        r.title = "%s %s%s" % (work.ref, tm, dp)
        r.labels = []
        for ng in range(len(self.sts.groups)):
            rl = Util.Record()
            rl.points = self.sts.xdone_points(work, ng)
            rl.label = self.sts.done_points(work, ng)
            rl.is_max = False
            r.labels.append(rl)
        return r

    def read_works(self):
        d = {}
        nworks = len(self.sts.works)
        for xw in range(nworks):
            work = self.sts.works.get_work(xw)
            key = "OTHER%d" % xw if work != self.work else "WORK"
            d[key] = self.read_work(work)
        return d

    def calc_max(self):
        self.dworks["WORK"] = self.read_work(self.work)
        ngroups = len(self.sts.groups)
        for ng in range(ngroups):
            mx = 0
            st = set()
            for key, r in self.dworks.items():
                rl = r.labels[ng]
                pt = rl.points
                if pt > mx:
                    mx = pt
                    st = {key}
                elif pt > 0 and pt == mx:
                    st.add(key)
            for key, r in self.dworks.items():
                r.labels[ng].is_max = key in st


class WWork(QtWidgets.QDialog):
    def __init__(self, w_parent, sts, work):
        super(WWork, self).__init__(w_parent)

        self.work = work

        self.setWindowTitle(work.path_to_exe())
        self.setWindowIcon(Iconos.Engine())
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        tb = QTVarios.tb_accept_cancel(self)

        # Tabs
        tab = Controles.Tab()

        # Tab-basic --------------------------------------------------
        lbRef = Controles.LB(self, _("Reference") + ": ")
        self.edRef = Controles.ED(self, work.ref).anchoMinimo(360)

        lbInfo = Controles.LB(self, _("Information") + ": ")
        self.emInfo = Controles.EM(self, work.info, siHTML=False).anchoMinimo(360).altoFijo(60)

        lbDepth = Controles.LB(self, _("Max depth") + ": ")
        self.sbDepth = Controles.ED(self).tipoInt(work.depth).anchoFijo(30)

        lbSeconds = Controles.LB(self, _("Maximum seconds to think") + ": ")
        self.sbSeconds = Controles.ED(self).tipoFloat(float(work.seconds), decimales=3).anchoFijo(60)

        lbSample = Controles.LB(self, _("Sample") + ": ")
        self.sbIni = Controles.SB(self, work.ini + 1, 1, 100).capture_changes(self.changeSample)
        self.sbIni.isIni = True
        lbGuion = Controles.LB(self, _("to"))
        self.sbEnd = Controles.SB(self, work.end + 1, 1, 100).capture_changes(self.changeSample)
        self.sbEnd.isIni = False

        # self.lbError = Controles.LB(self).set_font_type(peso=75).set_foreground("red")
        # self.lbError.hide()

        lySample = Colocacion.H().control(self.sbIni).control(lbGuion).control(self.sbEnd)
        ly = Colocacion.G()
        ly.controld(lbRef, 0, 0).control(self.edRef, 0, 1)
        ly.controld(lbInfo, 1, 0).control(self.emInfo, 1, 1)
        ly.controld(lbDepth, 2, 0).control(self.sbDepth, 2, 1)
        ly.controld(lbSeconds, 3, 0).control(self.sbSeconds, 3, 1)
        ly.controld(lbSample, 4, 0).otro(lySample, 4, 1)

        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tab.new_tab(w, _("Basic data"))

        # Tab-Engine
        scrollArea = WEngines.wgen_options_engine(self, work.me)
        tab.new_tab(scrollArea, _("Engine options"))

        # Tab-Groups
        btAll = Controles.PB(self, _("All"), self.setAll, plano=False)
        btNone = Controles.PB(self, _("None"), self.setNone, plano=False)
        lyAN = Colocacion.H().control(btAll).espacio(10).control(btNone)
        self.liGroups = []
        ly = Colocacion.G()
        ly.columnaVacia(1, 10)
        num = len(sts.groups)
        mitad = num / 2 + num % 2

        for x in range(num):
            group = sts.groups.group(x)
            chb = Controles.CHB(self, _F(group.name), work.liGroupActive[x])
            self.liGroups.append(chb)
            col = 0 if x < mitad else 2
            fil = x % mitad

            ly.control(chb, fil, col)
        ly.otroc(lyAN, mitad, 0, numColumnas=3)

        w = QtWidgets.QWidget()
        w.setLayout(ly)
        tab.new_tab(w, _("Groups"))

        layout = Colocacion.V().control(tb).control(tab).margen(8)
        self.setLayout(layout)

        self.edRef.setFocus()

    def changeSample(self):
        vIni = self.sbIni.valor()
        vEnd = self.sbEnd.valor()
        p = self.sender()
        if vEnd < vIni:
            if p.isIni:
                self.sbEnd.set_value(vIni)
            else:
                self.sbIni.set_value(vEnd)

    def setAll(self):
        for group in self.liGroups:
            group.set_value(True)

    def setNone(self):
        for group in self.liGroups:
            group.set_value(False)

    def aceptar(self):
        self.work.ref = self.edRef.texto()
        self.work.info = self.emInfo.texto()
        self.work.depth = self.sbDepth.textoInt()
        self.work.seconds = self.sbSeconds.textoFloat()
        self.work.ini = self.sbIni.valor() - 1
        self.work.end = self.sbEnd.valor() - 1
        me = self.work.me
        WEngines.wsave_options_engine(me)
        for n, group in enumerate(self.liGroups):
            self.work.liGroupActive[n] = group.valor()
        self.accept()


class WUnSTS(LCDialog.LCDialog):
    def __init__(self, w_parent, sts, procesador):
        titulo = sts.name
        icono = Iconos.STS()
        extparam = "unsts"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.select_engines = SelectEngines.SelectEngines(w_parent)

        # Datos
        self.sts = sts
        self.procesador = procesador

        # Toolbar
        tb = Controles.TBrutina(self, icon_size=24)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("Run"), Iconos.Run(), self.wkRun, sep=False)
        tb.new("+%s" % _("Board"), Iconos.Run2(), self.wkRun2)
        tb.new(_("New"), Iconos.NuevoMas(), self.wkNew)
        tb.new(_("Import"), Iconos.Import8(), self.wkImport)
        tb.new(_("Edit"), Iconos.Modificar(), self.wkEdit)
        tb.new(_("Copy"), Iconos.Copiar(), self.wkCopy)
        tb.new(_("Remove"), Iconos.Borrar(), self.wkRemove)
        tb.new(_("Up"), Iconos.Arriba(), self.up, sep=False)
        tb.new(_("Down"), Iconos.Abajo(), self.down)
        tb.new(_("Export"), Iconos.Grabar(), self.export)
        tb.new(_("Config"), Iconos.Configurar(), self.configurar)

        # # Grid works
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("POS", _("N."), 30, align_center=True)
        o_columns.nueva("REF", _("Reference"), 100)
        o_columns.nueva("TIME", _("Time"), 50, align_center=True)
        o_columns.nueva("DEPTH", _("Depth"), 50, align_center=True)
        o_columns.nueva("SAMPLE", _("Sample"), 50, align_center=True)
        o_columns.nueva("RESULT", _("Result"), 150, align_center=True)
        o_columns.nueva("ELO", _("Elo"), 80, align_center=True)
        o_columns.nueva("WORKTIME", _("Work time"), 80, align_center=True)
        for x in range(len(sts.groups)):
            group = sts.groups.group(x)
            o_columns.nueva("T%d" % x, group.name, 140, align_center=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.restore_video(with_tam=True, default_width=800, default_height=430)

        self.grid.gotop()

    def terminar(self):
        self.procesador.close_engines()
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.procesador.close_engines()
        self.save_video()

    def configurar(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("formula", _("Formula to calculate elo"), Iconos.STS())
        resp = menu.lanza()
        if resp:
            formula = self.sts.formula
            formula_general = STS.Formula()

            form = FormLayout.FormLayout(self, _("Formula to calculate elo"), Iconos.Elo(), with_default=False)
            form.apart_np(f'{_("Elo")} = X * {_("Result")} + K')
            form.separador()
            form.checkbox(f'<center><b>{_("By default")}</b></center>' + f'X={formula_general.x_default:.04f} K={formula_general.k_default:.04f}', False)
            form.separador()
            form.editbox("X", 100, tipo=float, decimales=4, init_value=formula.x, negatives=True)
            form.editbox("K", 100, tipo=float, decimales=4, init_value=formula.k, negatives=True)
            resultado = form.run()
            if resultado:
                resp, valor = resultado
                by_default, x, k = valor
                if by_default:
                    x = formula_general.x_default
                    k = formula_general.k_default
                formula.change(x, k)
                self.sts.save()
                self.grid.refresh()

    def export(self):
        resp = SelectFiles.salvaFichero(self, _("CSV file"), Code.configuration.save_folder(), "csv", True)
        if resp:
            self.sts.write_csv(resp)

    def up(self):
        row = self.grid.recno()
        if self.sts.up(row):
            self.grid.goto(row - 1, 0)
            self.grid.refresh()

    def down(self):
        row = self.grid.recno()
        if self.sts.down(row):
            self.grid.goto(row + 1, 0)
            self.grid.refresh()

    def wkRun(self):
        row = self.grid.recno()
        if row >= 0:
            work = self.sts.get_work(row)
            w = WRun(self, self.sts, work, self.procesador, False)
            w.exec_()

    def wkRun2(self):
        row = self.grid.recno()
        if row >= 0:
            work = self.sts.get_work(row)
            w = WRun(self, self.sts, work, self.procesador, True)
            w.exec_()

    def grid_doble_click(self, grid, row, column):
        self.wkRun()

    def wkEdit(self):
        row = self.grid.recno()
        if row >= 0:
            work = self.sts.get_work(row)
            w = WWork(self, self.sts, work)
            if w.exec_():
                self.sts.save()

    def wkNew(self, work=None):
        if work is None or not work:
            me = WEngines.select_engine(self)
            if not me:
                return
            work = self.sts.create_work(me)
        else:
            work.workTime = 0.0

        w = WWork(self, self.sts, work)
        if w.exec_():
            self.sts.add_work(work)
            self.sts.save()
            self.grid.refresh()
            self.grid.gobottom()
        return work

    def wkImport(self, work=None):
        if work is None or not work:
            me = self.select_engines.menu(self)
            if not me:
                return
            work = self.sts.create_work(me)
            work.ref = me.name
            work.info = me.id_info

        else:
            work.workTime = 0.0

        w = WWork(self, self.sts, work)
        if w.exec_():
            self.sts.add_work(work)
            self.sts.save()
            self.grid.refresh()
            self.grid.gobottom()
        return work

    def wkCopy(self):
        row = self.grid.recno()
        if row >= 0:
            work = self.sts.get_work(row)
            self.wkNew(work.clone())

    def wkRemove(self):
        li = self.grid.recnosSeleccionados()
        if li:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                li.sort(reverse=True)
                for row in li:
                    self.sts.remove_work(row)
                self.sts.save()
                self.grid.refresh()

    def grid_num_datos(self, grid):
        return len(self.sts.works)

    def grid_dato(self, grid, row, o_column):
        work = self.sts.works.lista[row]
        column = o_column.key
        if column == "POS":
            return str(row + 1)
        if column == "REF":
            return work.ref
        if column == "TIME":
            return str(work.seconds) if work.seconds else "-"
        if column == "DEPTH":
            return str(work.depth) if work.depth else "-"
        if column == "SAMPLE":
            return "%d-%d" % (work.ini + 1, work.end + 1)
        if column == "RESULT":
            return str(self.sts.all_points(work))
        if column == "ELO":
            return self.sts.elo(work)
        if column == "WORKTIME":
            secs = work.work_time
            if secs == 0.0:
                return "-"
            d = int(secs * 10) % 10
            s = int(secs) % 60
            m = int(secs) // 60
            return "%d' %02d.%d\"" % (m, s, d)
        test = int(column[1:])
        return self.sts.done_points(work, test)

    def grid_doubleclick_header(self, grid, oCol):
        if oCol.key != "POS":
            self.sts.orden_works(oCol.key)
            self.sts.save()
            self.grid.refresh()
            self.grid.gotop()


class WSTS(LCDialog.LCDialog):
    def __init__(self, w_parent, procesador):

        titulo = _("STS: Strategic Test Suite")
        icono = Iconos.STS()
        extparam = "sts"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        # Datos
        self.procesador = procesador
        self.carpetaSTS = procesador.configuration.carpetaSTS
        self.lista = self.leeSTS()

        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("Select"), Iconos.Seleccionar(), self.modificar)
        tb.new(_("New"), Iconos.NuevoMas(), self.crear)
        tb.new(_("Rename"), Iconos.Rename(), self.rename)
        tb.new(_("Copy"), Iconos.Copiar(), self.copiar)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)
        tb.new(_("Config"), Iconos.Configurar(), self.configurar)
        if len(self.lista) == 0:
            for x in (self.modificar, self.borrar, self.copiar, self.rename):
                tb.set_action_visible(x, False)

        # grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 340)
        o_columns.nueva("FECHA", _("Date"), 120, align_center=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.register_grid(self.grid)

        lb = Controles.LB(
            self,
            'STS %s: <b>Dann Corbit & Swaminathan</b> <a href="https://sites.google.com/site/strategictestsuite/about-1">%s</a>'
            % (_("Authors"), _("More info")),
        )

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).control(lb).margen(8)
        self.setLayout(layout)

        self.restore_video(with_tam=True, default_width=400, default_height=500)

        self.grid.gotop()

    def leeSTS(self):
        li = []
        Util.create_folder(self.carpetaSTS)
        for entry in Util.listdir(self.carpetaSTS):
            x = entry.name
            if x.lower().endswith(".sts"):
                st = entry.stat()
                li.append((x, st.st_ctime, st.st_mtime))

        li.sort(key=lambda x: x[2], reverse=True)  # por ultima modificacin y al reves
        return li

    def grid_num_datos(self, grid):
        return len(self.lista)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        name, fcreacion, fmanten = self.lista[row]
        if column == "NOMBRE":
            return name[:-4]
        elif column == "FECHA":
            tm = time.localtime(fmanten)
            return "%d-%02d-%d, %2d:%02d" % (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_hour, tm.tm_min)

    def terminar(self):
        self.save_video()
        self.accept()

    def grid_doble_click(self, grid, row, column):
        self.modificar()

    def modificar(self):
        n = self.grid.recno()
        if n >= 0:
            name = self.lista[n][0][:-4]
            sts = STS.STS(name)
            self.trabajar(sts)

    def nombreNum(self, num):
        return self.lista[num][0][:-4]

    def crear(self):
        name = self.editNombre("", True)
        if name:
            sts = STS.STS(name)
            sts.save()
            self.grid.refresh()
            self.reread()
            self.trabajar(sts)

    def reread(self):
        self.lista = self.leeSTS()
        self.grid.refresh()

    def rename(self):
        n = self.grid.recno()
        if n >= 0:
            nombreOri = self.nombreNum(n)
            nombreDest = self.editNombre(nombreOri)
            if nombreDest:
                pathOri = Util.opj(self.carpetaSTS, nombreOri + ".sts")
                pathDest = Util.opj(self.carpetaSTS, nombreDest + ".sts")
                shutil.move(pathOri, pathDest)
                self.reread()

    def editNombre(self, previo, siNuevo=False):
        while True:
            li_gen = [(None, None)]
            li_gen.append((_("Name") + ":", previo))
            resultado = FormLayout.fedit(li_gen, title=_("STS: Strategic Test Suite"), parent=self, icon=Iconos.STS())
            if resultado:
                accion, li_gen = resultado
                name = Util.valid_filename(li_gen[0].strip())
                if name:
                    if not siNuevo and previo == name:
                        return None
                    path = Util.opj(self.carpetaSTS, name + ".sts")
                    if os.path.isfile(path):
                        QTUtil2.message_error(self, _("The file %s already exist") % name)
                        continue
                    return name
                else:
                    return None
            else:
                return None

    def trabajar(self, sts):
        w = WUnSTS(self, sts, self.procesador)
        w.exec_()

    def borrar(self):
        n = self.grid.recno()
        if n >= 0:
            name = self.nombreNum(n)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), name)):
                path = Util.opj(self.carpetaSTS, name + ".sts")
                os.remove(path)
                self.reread()

    def copiar(self):
        n = self.grid.recno()
        if n >= 0:
            nombreBase = self.nombreNum(n)
            name = self.editNombre(nombreBase, True)
            if name:
                sts = STS.STS(nombreBase)
                sts.save_copy_new(name)
                sts = STS.STS(name)
                self.reread()
                self.trabajar(sts)

    def configurar(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("formula", _("Formula to calculate elo"), Iconos.STS())
        resp = menu.lanza()
        if resp:
            formula = STS.Formula()

            form = FormLayout.FormLayout(self, _("Formula to calculate elo"), Iconos.Elo(), with_default=False)
            form.apart_np(f'{_("Elo")} = X * {_("Result")} + K')
            form.separador()
            form.checkbox(f'<center><b>{_("Initial")}<b></center>' + f'X={formula.x_default_base:.04f} K={formula.k_default_base:.04f}', False)
            form.separador()
            form.editbox("X", 100, tipo=float, decimales=4, init_value=formula.x_default, negatives=True)
            form.editbox("K", 100, tipo=float, decimales=4, init_value=formula.k_default, negatives=True)
            resultado = form.run()
            if resultado:
                resp, valor = resultado
                by_default, x, k = valor
                if by_default:
                    x, k = formula.x_default_base, formula.k_default_base
                formula.change_default(x, k)


def sts(procesador, parent):
    w = WSTS(parent, procesador)
    w.exec_()
