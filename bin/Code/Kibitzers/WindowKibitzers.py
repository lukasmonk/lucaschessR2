from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code.Base.Constantes import KIB_CANDIDATES, KIB_INDEXES, KIB_POLYGLOT, KIB_GAVIOTA, KIB_DATABASES

KIB_BEFORE_MOVE, KIB_AFTER_MOVE = True, False

from Code.Books import Books, WBooks
from Code.Engines import Priorities
from Code.Kibitzers import Kibitzers
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
        self.grid_values = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", is_editable=True)
        # self.grid_values.font_type(puntos=self.configuration.x_pgn_fontpoints)
        self.register_grid(self.grid_values)

        w = QtWidgets.QWidget()
        ly = Colocacion.V().control(self.grid_values).margen(0)
        w.setLayout(ly)
        self.splitter.addWidget(w)

        self.splitter.setSizes([259, 562])  # por defecto

        ly = Colocacion.V().control(tb).control(self.splitter)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=849, altoDefecto=400)

        self.grid_kibitzers.gotop()

    def me_set_editor(self, parent):
        recno = self.grid_values.recno()
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
        elif key == "max_depth":
            control = "ed"
            valor = str(kibitzer.max_depth)
        elif key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(key[7:])]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.minimo
                maximo = opcion.maximo
            elif tipo in ("check", "button"):
                if valor == "true":
                    valor = "false"
                else:
                    valor = "true"
                kibitzer.set_uci_option(opcion.name, valor)
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

    def me_readvalue(self, editor):
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
        elif self.me_key == "max_depth":
            try:
                kibitzer.max_depth = int(valor)
            except ValueError:
                pass
        elif self.me_key.startswith("opcion"):
            opcion = kibitzer.li_uci_options_editable()[int(self.me_key[7:])]
            opcion.valor = valor
            kibitzer.set_uci_option(opcion.name, valor)
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
        rondo = QTVarios.rondo_puntos()
        for book in list_books.lista:
            submenu.opcion(("book", book), book.name, rondo.otro())
            submenu.separador()
        submenu.opcion(("installbook", None), _("Registered books"), Iconos.Nuevo())
        menu.separador()

        si_gaviota = True
        si_index = True
        for kib in self.kibitzers.lista:
            if kib.tipo == KIB_GAVIOTA:
                si_gaviota = False
            elif kib.tipo == KIB_INDEXES:
                si_index = False
        if si_index:
            menu.opcion(("index", None), _("Indexes") + " - RodentII", Iconos.Camara())
            menu.separador()
        if si_gaviota:
            menu.opcion(("gaviota", None), _("Gaviota Tablebases"), Iconos.Finales())
            menu.separador()

        submenu = menu.submenu(_("Database"), Iconos.Database())
        QTVarios.menuDB(submenu, Code.configuration, True, )
        menu.separador()

        resp = menu.lanza()
        if resp:
            if type(resp) == str:
                resp = ("database", resp)

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
            elif orden == "database":
                num = self.kibitzers.nuevo_database(extra)
                self.goto(num)
            elif orden in "installbook":
                self.polyglot_install()

    def polyglot_install(self):
        WBooks.registered_books(self)

    def nuevo_engine(self):
        form = FormLayout.FormLayout(self, _("Kibitzer"), Iconos.Kibitzer(), anchoMinimo=340)

        form.edit(_("Name"), "")
        form.separador()

        form.combobox(_("Engine"), self.configuration.combo_engines(), "stockfish")
        form.separador()

        li_tipos = Kibitzers.Tipos().comboSinIndices()
        form.combobox(_("Type"), li_tipos, KIB_CANDIDATES)
        form.separador()

        form.combobox(_("Process priority"), Priorities.priorities.combo(), Priorities.priorities.normal)
        form.separador()

        form.combobox(_("Point of view"), Kibitzers.cb_pointofview_options(), KIB_AFTER_MOVE)
        form.separador()

        form.float("%s (0=%s)" % (_("Fixed time in seconds"), _("all the time thinking")), 0.0)
        form.separador()

        form.editbox(_("Fixed depth"), ancho=30 * Code.factor_big_fonts, tipo=int, init_value=0)
        form.separador()

        resultado = form.run()

        if resultado:
            accion, resp = resultado

            name, engine, tipo, prioridad, pointofview, fixed_time, fixed_depth = resp

            # Indexes only with Rodent II
            if tipo == "I":
                engine = "rodentii"
                if not name:  # para que no repita rodent II
                    name = _("Indexes") + " - RodentII"

            name = name.strip()
            if not name:
                for label, key in li_tipos:
                    if key == tipo:
                        name = "%s: %s" % (label, engine)
            num = self.kibitzers.nuevo_engine(name, engine, tipo, prioridad, pointofview, fixed_time, fixed_depth)
            self.goto(num)

    def remove(self):
        if self.kibitzers.lista:
            num = self.krecno()
            kib = self.kibitzers.kibitzer(num)
            if QTUtil2.pregunta(self, _("Are you sure you want to remove %s?") % kib.name):
                self.kibitzers.remove(num)
                self.grid_kibitzers.refresh()
                nk = len(self.kibitzers)
                if nk > 0:
                    if num > nk:
                        num = nk - 1
                    self.goto(num)
                else:
                    self.liKibActual = []
                    self.grid_values.refresh()

    def copy(self):
        num = self.krecno()
        if num >= 0:
            num = self.kibitzers.clonar(num)
            self.goto(num)

    def goto(self, num):
        if self.grid_kibitzers:
            self.grid_kibitzers.goto(num, 0)
            self.grid_kibitzers.refresh()
            self.act_kibitzer()
            self.grid_values.refresh()

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

    def act_kibitzer(self):
        self.liKibActual = []
        row = self.krecno()
        if row < 0:
            return

        me = self.kibitzers.kibitzer(row)
        tipo = me.tipo
        self.liKibActual.append((_("Name"), me.name, "name"))

        if not (tipo in (KIB_POLYGLOT, KIB_GAVIOTA, KIB_INDEXES, KIB_DATABASES)):
            self.liKibActual.append((_("Type"), me.ctipo(), "tipo"))
            self.liKibActual.append((_("Priority"), me.cpriority(), "prioridad"))

        self.liKibActual.append((_("Visible in menu"), str(me.visible), "visible"))
        self.liKibActual.append((_("Point of view"), me.cpointofview(), "pointofview"))

        if not (tipo in (KIB_POLYGLOT, KIB_GAVIOTA, KIB_INDEXES, KIB_DATABASES)):
            self.liKibActual.append((_("Engine"), me.name, None))

        if not (tipo in (KIB_POLYGLOT, KIB_DATABASES)):
            self.liKibActual.append((_("Author"), me.autor, None))

        if not (tipo in (KIB_GAVIOTA, KIB_INDEXES)):
            self.liKibActual.append((_("File"), me.path_exe, None))

        if not (tipo in (KIB_POLYGLOT, KIB_GAVIOTA, KIB_INDEXES, KIB_DATABASES)):
            self.liKibActual.append((_("Information"), me.id_info, "info"))
            self.liKibActual.append((_("Fixed time in seconds"), me.max_time, "max_time"))
            self.liKibActual.append((_("Fixed depth"), me.max_depth, "max_depth"))

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
        self.grid_values = Grid.Grid(self, o_columns, siSelecFilas=False, xid="val", is_editable=True)
        self.grid_values.font_type(puntos=self.configuration.x_pgn_fontpoints)
        self.register_grid(self.grid_values)

        ly = Colocacion.V().control(tb).control(self.grid_values)
        self.setLayout(ly)

        self.restore_video(anchoDefecto=600, altoDefecto=400)

        self.grid_values.gotop()

        # self.grid_values.resizeRowsToContents()

    def leeOpciones(self):
        li = []
        li.append([_("Priority"), self.kibitzer.cpriority(), "prioridad"])
        li.append([_("Point of view"), self.kibitzer.cpointofview(), "pointofview"])
        li.append([_("Fixed time in seconds"), self.kibitzer.max_time, "max_time"])
        li.append([_("Fixed depth"), self.kibitzer.max_depth, "max_depth"])
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
        xpointofview = None
        xposicionBase = None
        xmax_time = self.kibitzer.max_time
        xmax_depth = self.kibitzer.max_depth
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
                elif key == "max_depth":
                    xmax_depth = self.kibitzer.max_depth
                else:
                    opcion = self.kibitzer.li_uci_options_editable()[int(key)]
                    lidif_opciones.append((opcion.name, opcion.valor))

        self.result_opciones = lidif_opciones
        self.result_xprioridad = xprioridad
        self.result_xpointofview = xpointofview
        self.result_posicionBase = xposicionBase
        self.result_max_time = xmax_time
        self.result_max_depth = xmax_depth
        self.save_video()
        self.accept()

    def me_set_editor(self, parent):
        recno = self.grid_values.recno()
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
        elif key == "max_depth":
            control = "ed"
            valor = str(self.kibitzer.max_depth)
        else:
            opcion = self.kibitzer.li_uci_options_editable()[int(key)]
            tipo = opcion.tipo
            valor = opcion.valor
            if tipo == "spin":
                control = "sb"
                minimo = opcion.minimo
                maximo = opcion.maximo
            elif tipo in ("check", "button"):
                if valor == "true":
                    valor = "false"
                else:
                    valor = "true"
                opcion.valor = valor
                self.li_options[recno][1] = opcion.valor
                self.grid_values.refresh()
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

    def me_readvalue(self, editor):
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

        elif self.me_key == "max_depth":
            try:
                self.kibitzer.max_depth = int(valor)
                self.li_options[3][1] = self.kibitzer.max_depth
            except ValueError:
                pass

        else:
            nopcion = int(self.me_key)
            opcion = self.kibitzer.li_uci_options_editable()[nopcion]
            opcion.valor = valor
            self.li_options[nopcion + 4][1] = valor
            self.kibitzer.set_uci_option(opcion.name, valor)

    def grid_num_datos(self, grid):
        return len(self.li_options)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        li = self.li_options[row]
        if column == "CAMPO":
            return li[0]
        else:
            return li[1]
