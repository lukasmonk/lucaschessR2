import os

from PySide2 import QtWidgets, QtCore, QtGui

from Code.Engines import Priorities
from Code.Kibitzers import Kibitzers
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.QT import LCDialog


class WKibitzers(LCDialog.LCDialog):
    def __init__(self, w_parent, kibitzers_manager):
        titulo = _("Kibitzers")
        icono = Iconos.Kibitzer()
        extparam = "kibitzer"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.kibitzers_manager = kibitzers_manager
        self.configuration = kibitzers_manager.configuration
        self.procesador = kibitzers_manager.procesador

        self.tipos = Kibitzers.Tipos()

        self.kibitzers = Kibitzers.Kibitzers()
        self.liKibActual = []

        self.grid_kibitzers = None

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.nuevo),
            None,
            (_("Remove"), Iconos.Borrar(), self.remove),
            None,
            (_("Copy"), Iconos.Copiar(), self.copy),
            None,
            (_("Up"), Iconos.Arriba(), self.up),
            None,
            (_("Down"), Iconos.Abajo(), self.down),
            None,
            (_("Engines configuration"), Iconos.ConfEngines(), self.ext_engines),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        self.splitter = QtWidgets.QSplitter(self)
        self.register_splitter(self.splitter, "kibitzers")

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva(
            "TYPE", "", 30, align_center=True, edicion=Delegados.PmIconosBMT(self, dicIconos=self.tipos.dicDelegado())
        )
        o_columns.nueva("NOMBRE", _("Kibitzer"), 209)
        self.grid_kibitzers = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid="kib")
        self.grid_kibitzers.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.grid_kibitzers.setAlternatingRowColors(False)

        p = self.grid_kibitzers.palette()
        p.setColor(QtGui.QPalette.Active, QtGui.QPalette.Highlight, QtCore.Qt.darkCyan)
        p.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, QtCore.Qt.cyan)
        self.grid_kibitzers.setPalette(p)

        self.register_grid(self.grid_kibitzers)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.grid_kibitzers).margen(0)
        w.setLayout(ly)
        self.splitter.addWidget(w)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CAMPO", _("Label"), 152, align_right=True)
        o_columns.nueva("VALOR", _("Value"), 390, edicion=Delegados.MultiEditor(self))
        self.gridValores = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", is_editable=True)
        self.gridValores.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.register_grid(self.gridValores)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.gridValores).margen(0)
        w.setLayout(ly)
        self.splitter.addWidget(w)

        self.splitter.setSizes([259, 562])  # por defecto

        ly = Colocacion.V().control(tb).control(self.splitter)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=849, altoDefecto=400)

        self.grid_kibitzers.gotop()

    def me_set_editor(self, parent):
        recno = self.gridValores.recno()
        key = self.liKibActual[recno][2]
        nk = self.krecno()
        kibitzer = self.kibitzers.kibitzer(nk)
        valor = control = lista = minimo = maximo = None
        if key is None:
            return None
        elif key == "name":
            control = "ed"
            valor = kibitzer.name
        elif key == "prioridad":
            control = "cb"
            lista = Priorities.priorities.combo()
            valor = kibitzer.prioridad
        elif key == "pointofview":
            control = "cb"
            lista = Kibitzers.cb_pointofview_options()
            valor = kibitzer.pointofview
        elif key == "visible":
            kibitzer.visible = not kibitzer.visible
            self.kibitzers.save()
            self.goto(nk)
        elif key == "info":
            control = "ed"
            valor = kibitzer.id_info
        elif key == "max_time":
            control = "ed"
            valor = str(kibitzer.max_time)
        elif key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(key[7:])]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.minimo
                maximo = opcion.maximo
            elif tipo in ("check", "button"):
                kibitzer.ordenUCI(opcion.name, not valor)
                self.kibitzers.save()
                self.goto(nk)
            elif tipo == "combo":
                lista = [(var, var) for var in opcion.li_vars]
                control = "cb"
            elif tipo == "string":
                control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, valor)
        elif control == "cb":
            return Controles.CB(parent, lista, valor)
        elif control == "sb":
            return Controles.SB(parent, valor, minimo, maximo)
        return None

    def me_set_value(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.set_value(valor)

    def me_leeValor(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, column, valor):
        nk = self.krecno()
        kibitzer = self.kibitzers.kibitzer(nk)
        if self.me_key == "name":
            valor = valor.strip()
            if valor:
                kibitzer.name = valor
        elif self.me_key == "tipo":
            kibitzer.tipo = valor
        elif self.me_key == "prioridad":
            kibitzer.prioridad = valor
        elif self.me_key == "pointofview":
            kibitzer.pointofview = valor
        elif self.me_key == "info":
            kibitzer.id_info = valor.strip()
        elif self.me_key == "max_time":
            try:
                kibitzer.max_time = float(valor)
            except ValueError:
                pass
        elif self.me_key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(self.me_key[7:])]
            opcion.valor = valor
            kibitzer.ordenUCI(opcion.name, valor)
        self.kibitzers.save()
        self.goto(nk)

    def ext_engines(self):
        self.procesador.motoresExternos()

    def terminar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, QCloseEvent):
        self.save_video()

    def nuevo(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(("engine", None), _("Engine"), Iconos.Engine())
        menu.separador()

        submenu = menu.submenu(_("Polyglot book"), Iconos.Book())
        list_books = Books.ListBooks()
        list_books.restore_pickle(self.configuration.file_books)
        list_books.verify()
        rondo = QTVarios.rondoPuntos()
        for book in list_books.lista:
            submenu.opcion(("book", book), book.name, rondo.otro())
            submenu.separador()
        submenu.opcion(("installbook", None), _("Install new book"), Iconos.Nuevo())
        menu.separador()

        si_gaviota = True
        si_index = True
        for kib in self.kibitzers.lista:
            if kib.tipo == Kibitzers.KIB_GAVIOTA:
                si_gaviota = False
            elif kib.tipo == Kibitzers.KIB_INDEXES:
                si_index = False
        if si_index:
            menu.opcion(("index", None), _("Indexes") + " - RodentII", Iconos.Camara())
            menu.separador()
        if si_gaviota:
            menu.opcion(("gaviota", None), _("Gaviota Tablebases"), Iconos.Finales())

        resp = menu.lanza()
        if resp:
            orden, extra = resp

            if orden == "engine":
                self.nuevo_engine()
            elif orden in "book":
                num = self.kibitzers.nuevo_polyglot(extra)
                self.goto(num)
            elif orden == "gaviota":
                num = self.kibitzers.nuevo_gaviota()
                self.goto(num)
            elif orden == "index":
                num = self.kibitzers.nuevo_index()
                self.goto(num)
            elif orden in "installbook":
                self.polyglot_install(list_books)

    def polyglot_install(self, list_books):
        fbin = SelectFiles.leeFichero(self, list_books.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            list_books.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            book = Books.Book("P", name, fbin, True)
            list_books.nuevo(book)
            list_books.save_pickle(self.configuration.file_books)
            num = self.kibitzers.nuevo_polyglot(book)
            self.goto(num)

    def nuevo_engine(self):
        form = FormLayout.FormLayout(self, _("Kibitzer"), Iconos.Kibitzer(), anchoMinimo=340)

        form.edit(_("Name"), "")
        form.separador()

        form.combobox(_("Engine"), self.configuration.comboMotores(), "stockfish")
        form.separador()

        liTipos = Kibitzers.Tipos().comboSinIndices()
        form.combobox(_("Type"), liTipos, Kibitzers.KIB_CANDIDATES)
        form.separador()

        form.combobox(_("Process priority"), Priorities.priorities.combo(), Priorities.priorities.normal)
        form.separador()

        form.combobox(_("Point of view"), Kibitzers.cb_pointofview_options(), Kibitzers.KIB_AFTER_MOVE)
        form.separador()

        form.float("%s (0=%s)" % (_("Fixed time in seconds"), _("all the time thinking")), 0.0)
        form.separador()

        resultado = form.run()

        if resultado:
            accion, resp = resultado

            name, engine, tipo, prioridad, pointofview, fixed_time = resp

            # Indexes only with Rodent II
            if tipo == "I":
                engine = "rodentII"
                if not name:  # para que no repita rodent II
                    name = _("Indexes") + " - RodentII"

            name = name.strip()
            if not name:
                for label, key in liTipos:
                    if key == tipo:
                        name = "%s: %s" % (label, engine)
            num = self.kibitzers.nuevo_engine(name, engine, tipo, prioridad, pointofview, fixed_time)
            self.goto(num)

    def remove(self):
        if self.kibitzers.lista:
            num = self.krecno()
            kib = self.kibitzers.kibitzer(num)
            if QTUtil2.pregunta(self, _("Are you sure?") + "\n %s" % kib.name):
                self.kibitzers.remove(num)
                self.grid_kibitzers.refresh()
                nk = len(self.kibitzers)
                if nk > 0:
                    if num > nk:
                        num = nk - 1
                    self.goto(num)

    def copy(self):
        num = self.krecno()
        if num >= 0:
            num = self.kibitzers.clonar(num)
            self.goto(num)

    def goto(self, num):
        if self.grid_kibitzers:
            self.grid_kibitzers.goto(num, 0)
            self.grid_kibitzers.refresh()
            self.actKibitzer()
            self.gridValores.refresh()

    def krecno(self):
        return self.grid_kibitzers.recno()

    def up(self):
        num = self.kibitzers.up(self.krecno())
        if num is not None:
            self.goto(num)

    def down(self):
        num = self.kibitzers.down(self.krecno())
        if num is not None:
            self.goto(num)

    def grid_num_datos(self, grid):
        gid = grid.id
        if gid == "kib":
            return len(self.kibitzers)
        return len(self.liKibActual)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        gid = grid.id
        if gid == "kib":
            return self.gridDatoKibitzers(row, column)
        elif gid == "val":
            return self.gridDatoValores(row, column)

    def gridDatoKibitzers(self, row, column):
        me = self.kibitzers.kibitzer(row)
        if column == "NOMBRE":
            return me.name
        elif column == "TYPE":
            return me.tipo

    def gridDatoValores(self, row, column):
        li = self.liKibActual[row]
        if column == "CAMPO":
            return li[0]
        else:
            return li[1]

    def grid_cambiado_registro(self, grid, row, column):
        if grid.id == "kib":
            self.goto(row)

    def grid_doble_click(self, grid, row, column):
        if grid.id == "kib":
            self.terminar()
            kibitzer = self.kibitzers.kibitzer(row)
            self.kibitzers_manager.run_new(kibitzer.huella)

    def actKibitzer(self):
        self.liKibActual = []
        row = self.krecno()
        if row < 0:
            return

        me = self.kibitzers.kibitzer(row)
        tipo = me.tipo
        self.liKibActual.append((_("Name"), me.name, "name"))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Type"), me.ctipo(), "tipo"))
            self.liKibActual.append((_("Priority"), me.cpriority(), "prioridad"))

        self.liKibActual.append((_("Visible in menu"), str(me.visible), "visible"))
        self.liKibActual.append((_("Point of view"), me.cpointofview(), "pointofview"))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Engine"), me.name, None))

        if not (tipo in (Kibitzers.KIB_POLYGLOT,)):
            self.liKibActual.append((_("Author"), me.autor, None))

        if not (tipo in (Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("File"), me.path_exe, None))

        if not (tipo in (Kibitzers.KIB_POLYGLOT, Kibitzers.KIB_GAVIOTA, Kibitzers.KIB_INDEXES)):
            self.liKibActual.append((_("Information"), me.id_info, "info"))
            self.liKibActual.append((_("Fixed time in seconds"), me.max_time, "max_time"))

            for num, opcion in enumerate(me.li_uci_options_editable()):
                default = opcion.label_default()
                label_default = " (%s)" % default if default else ""
                valor = str(opcion.valor)
                if opcion.tipo in ("check", "button"):
                    valor = valor.lower()
                self.liKibActual.append(("%s%s" % (opcion.name, label_default), valor, "opcion,%d" % num))


class WKibitzerLive(LCDialog.LCDialog):
    def __init__(self, w_parent, configuration, numkibitzer):
        self.kibitzers = Kibitzers.Kibitzers()
        self.kibitzer = self.kibitzers.kibitzer(numkibitzer)
        titulo = self.kibitzer.name
        icono = Iconos.Kibitzer()
        extparam = "kibitzerlive"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.configuration = configuration

        self.li_options = self.leeOpciones()
        self.liOriginal = self.leeOpciones()

        li_acciones = (
            (_("Save"), Iconos.Grabar(), self.grabar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("CAMPO", _("Label"), 152, align_right=True)
        o_columns.nueva("VALOR", _("Value"), 390, edicion=Delegados.MultiEditor(self))
        self.gridValores = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", is_editable=True)
        self.gridValores.tipoLetra(puntos=self.configuration.x_pgn_fontpoints)
        self.register_grid(self.gridValores)

        ly = Colocacion.V().control(tb).control(self.gridValores)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=600, altoDefecto=400)

        self.gridValores.gotop()

        # self.gridValores.resizeRowsToContents()

    def leeOpciones(self):
        li = []
        li.append([_("Priority"), self.kibitzer.cpriority(), "prioridad"])
        li.append([_("Point of view"), self.kibitzer.cpointofview(), "pointofview"])
        li.append([_("Fixed time in seconds"), self.kibitzer.max_time, "max_time"])
        for num, opcion in enumerate(self.kibitzer.li_uci_options_editable()):
            default = opcion.label_default()
            label_default = " (%s)" % default if default else ""
            valor = str(opcion.valor)
            if opcion.tipo in ("check", "button"):
                valor = valor.lower()
            li.append(["%s%s" % (opcion.name, label_default), valor, "%d" % num])
        return li

    def grabar(self):
        self.kibitzers.save()
        lidif_opciones = []
        xprioridad = None
        xposicionBase = None
        xpointofview = None
        xmax_time = None
        for x in range(len(self.li_options)):
            if self.li_options[x][1] != self.liOriginal[x][1]:
                key = self.li_options[x][2]
                if key == "prioridad":
                    prioridad = self.kibitzer.prioridad
                    priorities = Priorities.priorities
                    xprioridad = priorities.value(prioridad)
                elif key == "pointofview":
                    xpointofview = self.kibitzer.pointofview
                elif key == "max_time":
                    xmax_time = self.kibitzer.max_time
                else:
                    opcion = self.kibitzer.li_uci_options_editable()[int(key)]
                    lidif_opciones.append((opcion.name, opcion.valor))

        self.result_xprioridad = xprioridad
        self.result_xpointofview = xpointofview
        self.result_opciones = lidif_opciones
        self.result_posicionBase = xposicionBase
        self.result_posicionBase = xposicionBase
        self.result_max_time = xmax_time
        self.save_video()
        self.accept()

    def me_set_editor(self, parent):
        recno = self.gridValores.recno()
        key = self.li_options[recno][2]
        control = lista = minimo = maximo = None
        if key == "prioridad":
            control = "cb"
            lista = Priorities.priorities.combo()
            valor = self.kibitzer.prioridad
        elif key == "pointofview":
            control = "cb"
            lista = Kibitzers.cb_pointofview_options()
            valor = self.kibitzer.pointofview
        elif key == "max_time":
            control = "ed"
            valor = str(self.kibitzer.max_time)
        else:
            opcion = self.kibitzer.li_uci_options_editable()[int(key)]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.minimo
                maximo = opcion.maximo
            elif tipo in ("check", "button"):
                opcion.valor = not valor
                self.li_options[recno][1] = opcion.valor
                self.gridValores.refresh()
            elif tipo == "combo":
                lista = [(var, var) for var in opcion.li_vars]
                control = "cb"
            elif tipo == "string":
                control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, valor)
        elif control == "cb":
            return Controles.CB(parent, lista, valor)
        elif control == "sb":
            return Controles.SB(parent, valor, minimo, maximo)
        return None

    def me_set_value(self, editor, valor):
        if self.me_control == "ed":
            editor.setText(str(valor))
        elif self.me_control in ("cb", "sb"):
            editor.set_value(valor)

    def me_leeValor(self, editor):
        if self.me_control == "ed":
            return editor.texto()
        elif self.me_control in ("cb", "sb"):
            return editor.valor()

    def grid_setvalue(self, grid, nfila, column, valor):
        if self.me_key == "prioridad":
            self.kibitzer.prioridad = valor
            self.li_options[0][1] = self.kibitzer.cpriority()
        elif self.me_key == "pointofview":
            self.kibitzer.pointofview = valor
            self.li_options[1][1] = self.kibitzer.cpointofview()
        elif self.me_key == "max_time":
            try:
                self.kibitzer.max_time = float(valor)
                self.li_options[2][1] = self.kibitzer.max_time
            except ValueError:
                pass

        else:
            nopcion = int(self.me_key)
            opcion = self.kibitzer.li_uci_options_editable()[nopcion]
            opcion.valor = valor
            self.li_options[nopcion + 3][1] = valor
            self.kibitzer.ordenUCI(opcion.name, valor)

    def grid_num_datos(self, grid):
        return len(self.li_options)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        li = self.li_options[row]
        if column == "CAMPO":
            return li[0]
        else:
            return li[1]
