import gettext
_ = gettext.gettext
import os
import random

from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code import Util
from Code.Engines import Engines
from Code.Engines import EnginesMicElo
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles


def selectEngine(wowner):
    """
    :param wowner: window
    :return: MotorExterno / None=error
    """
    # Pedimos el ejecutable
    folderEngines = Code.configuration.read_variables("FOLDER_ENGINES")
    extension = "exe" if Code.is_windows else "*"
    exeMotor = SelectFiles.leeFichero(wowner, folderEngines if folderEngines else ".", extension, _("Engine"))
    if not exeMotor:
        return None
    folderEngines = Util.relative_path(os.path.dirname(exeMotor))
    Code.configuration.write_variables("FOLDER_ENGINES", folderEngines)

    # Leemos el UCI
    um = QTUtil2.unMomento(wowner)
    me = Engines.read_engine_uci(exeMotor)
    um.final()
    if not me:
        QTUtil2.message_bold(wowner, _X(_("The file %1 does not correspond to a UCI engine type."), exeMotor))
        return None
    return me


class WSelectEngineElo(LCDialog.LCDialog):
    def __init__(self, manager, elo, titulo, icono, tipo):
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, tipo.lower())

        self.siMicElo = tipo == "MICELO"
        self.siMicPer = tipo == "MICPER"
        self.siMic = self.siMicElo or self.siMicPer

        self.manager = manager

        self.colorNoJugable = QTUtil.qtColorRGB(241, 226, 226)
        self.colorMenor = QTUtil.qtColorRGB(245, 245, 245)
        self.colorMayor = None
        self.elo = elo
        self.tipo = tipo

        # Toolbar
        li_acciones = [
            (_("Choose"), Iconos.Aceptar(), self.elegir),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Random opponent"), Iconos.FAQ(), self.selectRandom),
            None,
        ]
        if self.siMicElo:
            li_acciones.append((_("Reset"), Iconos.Reiniciar(), self.reset))
            li_acciones.append(None)

        self.tb = QTVarios.LCTB(self, li_acciones)

        self.liMotores = self.manager.list_engines(elo)
        self.liMotoresActivos = self.liMotores

        liFiltro = (
            ("---", None),
            (">=", ">"),
            ("<=", "<"),
            ("+-100", "100"),
            ("+-200", "200"),
            ("+-400", "400"),
            ("+-800", "800"),
        )

        self.cbElo = Controles.CB(self, liFiltro, None).capture_changes(self.filtrar)

        minimo = 9999
        maximo = 0
        for mt in self.liMotores:
            if mt.siJugable:
                if mt.elo < minimo:
                    minimo = mt.elo
                if mt.elo > maximo:
                    maximo = mt.elo
        self.sbElo, lbElo = QTUtil2.spinBoxLB(self, elo, minimo, maximo, maxTam=50, etiqueta=_("Elo"))
        self.sbElo.capture_changes(self.filtrar)

        if self.siMic:
            liCaract = []
            st = set()
            for mt in self.liMotores:
                mt.liCaract = li = mt.id_info.split("\n")
                mt.txtCaract = ", ".join([_F(x) for x in li])
                for x in li:
                    if not (x in st):
                        st.add(x)
                        liCaract.append((_F(x), x))
            liCaract.sort(key=lambda x: x[1])
            liCaract.insert(0, ("---", None))
            self.cbCaract = Controles.CB(self, liCaract, None).capture_changes(self.filtrar)

        ly = Colocacion.H().control(lbElo).control(self.cbElo).control(self.sbElo)
        if self.siMic:
            ly.control(self.cbCaract)
        ly.relleno(1)
        gbRandom = Controles.GB(self, "", ly)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 35, align_center=True)
        o_columns.nueva("ENGINE", _("Name"), 140)
        o_columns.nueva("ELO", _("Elo"), 60, align_right=True)
        if not self.siMicPer:
            o_columns.nueva("GANA", _("Win"), 80, align_center=True)
            o_columns.nueva("TABLAS", _("Draw"), 80, align_center=True)
            o_columns.nueva("PIERDE", _("Loss"), 80, align_center=True)
        if self.siMic:
            o_columns.nueva("INFO", _("Information"), 300, align_center=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siCabeceraMovible=False, altoFila=24)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)

        f = Controles.TipoLetra(puntos=9)
        self.grid.ponFuente(f)

        self.grid.gotop()

        # Layout
        lyH = Colocacion.H().control(self.tb).control(gbRandom)
        layout = Colocacion.V().otro(lyH).control(self.grid).margen(3)
        self.setLayout(layout)

        self.filtrar()

        self.restore_video()

    def removeReset(self):
        self.tb.set_action_visible(self.reset, False)

    def filtrar(self):
        cb = self.cbElo.valor()
        elo = self.sbElo.valor()
        if cb is None:
            self.liMotoresActivos = self.liMotores
            self.sbElo.setDisabled(True)
        else:
            self.sbElo.setDisabled(False)
            if cb == ">":
                self.liMotoresActivos = [x for x in self.liMotores if x.elo >= elo]
            elif cb == "<":
                self.liMotoresActivos = [x for x in self.liMotores if x.elo <= elo]
            elif cb in ("100", "200", "400", "800"):
                mx = int(cb)
                self.liMotoresActivos = [x for x in self.liMotores if abs(x.elo - elo) <= mx]
        if self.siMic:
            cc = self.cbCaract.valor()
            if cc:
                self.liMotoresActivos = [mt for mt in self.liMotoresActivos if cc in mt.liCaract]
        self.grid.refresh()

    def reset(self):
        if not QTUtil2.pregunta(self, _("Are you sure you want to set the original elo of all engines?")):
            return

        self.manager.configuration.write_variables("DicMicElos", {})
        self.cancelar()

    def cancelar(self):
        self.resultado = None
        self.save_video()
        self.reject()

    def elegir(self):
        f = self.grid.recno()
        mt = self.liMotoresActivos[f]
        if mt.siJugable:
            self.resultado = mt
            self.save_video()
            self.accept()
        else:
            QTUtil.beep()

    def selectRandom(self):
        li = []
        for mt in self.liMotoresActivos:
            if mt.siJugable:
                li.append(mt)
        if li:
            n = random.randint(0, len(li) - 1)
            self.resultado = li[n]
            self.save_video()
            self.accept()
        else:
            QTUtil2.message_error(self, _("There is not a playable engine between these values"))

    def grid_doble_click(self, grid, row, o_column):
        self.elegir()

    def grid_num_datos(self, grid):
        return len(self.liMotoresActivos)

    def grid_wheel_event(self, quien, forward):
        n = len(self.liMotoresActivos)
        f, c = self.grid.posActualN()
        f += -1 if forward else +1
        if 0 <= f < n:
            self.grid.goto(f, c)

    def grid_color_fondo(self, grid, row, o_column):
        mt = self.liMotoresActivos[row]
        if mt.siOut:
            return self.colorNoJugable
        else:
            return self.colorMenor if mt.elo < self.elo else self.colorMayor

    def grid_dato(self, grid, row, o_column):
        mt = self.liMotoresActivos[row]
        key = o_column.key
        if key == "NUMBER":
            valor = "%2d" % mt.number
        elif key == "ENGINE":
            valor = " " + mt.alias
        elif key == "ELO":
            valor = "%d " % mt.elo
        elif key == "INFO":
            valor = mt.txtCaract
        else:
            if not mt.siJugable:
                return "x"
            if key == "GANA":
                pts = mt.pgana
            elif key == "TABLAS":
                pts = mt.ptablas
            elif key == "PIERDE":
                pts = mt.ppierde

            valor = "%+d" % pts

        return valor


def select_engine_elo(manager, elo):
    titulo = _("Lucas-Elo") + ". " + _("Choose the opponent")
    icono = Iconos.Elo()
    w = WSelectEngineElo(manager, elo, titulo, icono, "ELO")
    if w.exec_():
        return w.resultado
    else:
        return None


def select_engine_micelo(manager, elo):
    titulo = _("Club players competition") + ". " + _("Choose the opponent")
    icono = Iconos.EloTimed()
    w = WSelectEngineElo(manager, elo, titulo, icono, "MICELO")
    if w.exec_():
        return w.resultado
    else:
        return None


def select_engine_entmaq(main_window):
    titulo = _("Choose the opponent")
    icono = Iconos.EloTimed()

    class ManagerTmp:
        def __init__(self):
            self.main_window = main_window
            self.configuration = Code.configuration

        def list_engines(self, elo):
            li = EnginesMicElo.all_engines()
            numX = len(li)
            for num, mt in enumerate(li):
                mt.siJugable = True
                mt.siOut = False
                mt.number = numX - num
            return li

    w = WSelectEngineElo(ManagerTmp(), 1600, titulo, icono, "MICPER")
    if w.exec_():
        return w.resultado
    else:
        return None


class WEngineExtend(QtWidgets.QDialog):
    def __init__(self, w_parent, listaMotores, engine, siTorneo=False):

        super(WEngineExtend, self).__init__(w_parent)

        self.setWindowTitle(engine.version)
        self.setWindowIcon(Iconos.Engine())
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        scrollArea = wgen_options_engine(self, engine)

        self.motorExterno = engine
        self.liMotores = listaMotores
        self.siTorneo = siTorneo

        # Toolbar
        tb = QTVarios.tbAcceptCancel(self)

        lb_alias = Controles.LB2P(self, _("Alias"))
        self.edAlias = Controles.ED(self, engine.key).anchoMinimo(360)

        lb_nombre = Controles.LB2P(self, _("Name"))
        self.edNombre = Controles.ED(self, engine.name).anchoMinimo(360)

        lb_info = Controles.LB(self, _("Information") + ": ")
        self.emInfo = Controles.EM(self, engine.id_info, siHTML=False).anchoMinimo(360).altoFijo(60)

        lb_elo = Controles.LB(self, "ELO: ")
        self.sbElo = Controles.SB(self, engine.elo, 0, 4000)

        lb_exe = Controles.LB(self, "%s: %s" % (_("File"), Util.relative_path(engine.path_exe)))

        if siTorneo:
            lb_depth = Controles.LB(self, _("Max depth") + ": ")
            self.sbDepth = Controles.SB(self, engine.depth, 0, 50)

            lb_time = Controles.LB(self, _("Maximum seconds to think") + ": ")
            self.edTime = Controles.ED(self, "").ponFloat(engine.time).anchoFijo(60).align_right()

            lb_book = Controles.LB(self, _("Opening book") + ": ")
            fvar = Code.configuration.file_books
            self.list_books = Books.ListBooks()
            self.list_books.restore_pickle(fvar)
            # # Comprobamos que todos esten accesibles
            self.list_books.verify()
            li = [(x.name, x.path) for x in self.list_books.lista]
            li.insert(0, ("* " + _("None"), "-"))
            li.insert(0, ("* " + _("By default"), "*"))
            self.cbBooks = Controles.CB(self, li, engine.book)
            bt_nuevo_book = Controles.PB(self, "", self.nuevoBook, plano=False).ponIcono(Iconos.Nuevo(), icon_size=16)
            # # Respuesta rival
            li = (
                (_("Uniform random"), "au"),
                (_("Proportional random"), "ap"),
                (_("Always the highest percentage"), "mp"),
            )
            self.cbBooksRR = QTUtil2.comboBoxLB(self, li, engine.bookRR)
            ly_book = (
                Colocacion.H()
                .control(lb_book)
                .control(self.cbBooks)
                .control(self.cbBooksRR)
                .control(bt_nuevo_book)
                .relleno()
            )
            ly_dt = (
                Colocacion.H()
                .control(lb_depth)
                .control(self.sbDepth)
                .espacio(40)
                .control(lb_time)
                .control(self.edTime)
                .relleno()
            )
            ly_torneo = Colocacion.V().otro(ly_dt).otro(ly_book)

        # Layout
        ly = Colocacion.G()
        ly.controld(lb_alias, 0, 0).control(self.edAlias, 0, 1)
        ly.controld(lb_nombre, 1, 0).control(self.edNombre, 1, 1)
        ly.controld(lb_info, 2, 0).control(self.emInfo, 2, 1)
        ly.controld(lb_elo, 3, 0).control(self.sbElo, 3, 1)
        ly.control(lb_exe, 4, 0, 1, 2)

        if siTorneo:
            ly.otro(ly_torneo, 5, 0, 1, 2)

        layout = Colocacion.V().control(tb).espacio(30).otro(ly).control(scrollArea)
        self.setLayout(layout)

        self.edAlias.setFocus()

    def nuevoBook(self):
        fbin = SelectFiles.leeFichero(self, self.list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.list_books.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            b = Books.Book("P", name, fbin, False)
            self.list_books.nuevo(b)
            fvar = Code.configuration.file_books
            self.list_books.save_pickle(fvar)
            li = [(x.name, x.path) for x in self.list_books.lista]
            li.insert(0, ("* " + _("Engine book"), "-"))
            li.insert(0, ("* " + _("By default"), "*"))
            self.cbBooks.rehacer(li, b.path)

    def aceptar(self):
        alias = self.edAlias.texto().strip()
        if not alias:
            QTUtil2.message_error(self, _("You have not indicated any alias"))
            return

        # Comprobamos que no se repita el alias
        for engine in self.liMotores:
            if (self.motorExterno != engine) and (engine.key == alias):
                QTUtil2.message_error(
                    self,
                    _(
                        "There is already another engine with the same alias, the alias must change in order to have both."
                    ),
                )
                return
        self.motorExterno.key = alias
        name = self.edNombre.texto().strip()
        self.motorExterno.name = name if name else alias
        self.motorExterno.id_info = self.emInfo.texto()
        self.motorExterno.elo = self.sbElo.valor()

        if self.siTorneo:
            self.motorExterno.depth = self.sbDepth.valor()
            self.motorExterno.time = self.edTime.textoFloat()
            pbook = self.cbBooks.valor()
            self.motorExterno.book = pbook
            self.motorExterno.bookRR = self.cbBooksRR.valor()

        # Grabamos options
        wsave_options_engine(self.motorExterno)

        self.accept()


def wgen_options_engine(owner, engine):
    fil = 0
    col = 0
    layout = Colocacion.G()
    for opcion in engine.li_uci_options_editable():
        tipo = opcion.tipo
        lb = Controles.LB(owner, opcion.name + ":").align_right()
        if tipo == "spin":
            control = QTUtil2.spinBoxLB(
                owner, opcion.valor, opcion.minimo, opcion.maximo, maxTam=50 if opcion.maximo < 1000 else 80
            )
            lb.set_text("%s [%d-%d] :" % (opcion.name, opcion.minimo, opcion.maximo))
        elif tipo == "check":
            control = Controles.CHB(owner, " ", opcion.valor)
        elif tipo == "combo":
            li_vars = []
            for var in opcion.li_vars:
                li_vars.append((var, var))
            control = Controles.CB(owner, li_vars, opcion.valor)
        elif tipo == "string":
            control = Controles.ED(owner, opcion.valor)
        # elif tipo == "button":
        #     control = Controles.CHB(owner, " ", opcion.valor)

        layout.controld(lb, fil, col).control(control, fil, col + 1)
        col += 2
        if col > 2:
            fil += 1
            col = 0
        opcion.control = control

    w = QtWidgets.QWidget(owner)
    w.setLayout(layout)
    scrollArea = QtWidgets.QScrollArea()
    scrollArea.setBackgroundRole(QtGui.QPalette.Light)
    scrollArea.setWidget(w)
    scrollArea.setWidgetResizable(True)

    return scrollArea


def wsave_options_engine(engine):
    liUCI = engine.liUCI = []
    for opcion in engine.li_uci_options_editable():
        tipo = opcion.tipo
        control = opcion.control
        if tipo == "spin":
            valor = control.value()
        elif tipo == "check":
            valor = control.isChecked()
        elif tipo == "combo":
            valor = control.valor()
        elif tipo == "string":
            valor = control.texto()
        else:
            valor = True
        # elif tipo == "button":
        #     valor = control.isChecked()
        if valor != opcion.default:
            liUCI.append((opcion.name, valor))
            opcion.valor = valor
        if opcion.name == "MultiPV":
            engine.maxMultiPV = opcion.maximo
