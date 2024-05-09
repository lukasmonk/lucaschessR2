import operator
import os

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code.Analysis import WindowAnalysisConfig
from Code.Base.Constantes import (
    POS_TUTOR_VERTICAL,
    POS_TUTOR_HORIZONTAL_2_1,
    POS_TUTOR_HORIZONTAL_1_2,
    POS_TUTOR_HORIZONTAL,
    INACCURACY,
    MISTAKE,
    BLUNDER,
)
from Code.Engines import Engines, WEngines
from Code.Engines import Priorities, CheckEngines
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
from Code.QT import SelectFiles


class WConfEngines(LCDialog.LCDialog):
    def __init__(self, owner):
        icono = Iconos.ConfEngines()
        titulo = _("Engines configuration")
        extparam = "confEngines1"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.configuration = Code.configuration
        self.engine = None
        self.li_uci_options = []
        self.grid_conf = None

        # Toolbar
        li_acciones = [(_("Close"), Iconos.MainMenu(), self.terminar), None]
        tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=24)

        self.wexternals = WConfExternals(self)
        self.wconf_tutor = WConfTutor(self)
        self.wconf_analyzer = WConfAnalyzer(self)
        self.wothers = WOthers(self)

        self.w_current = None

        self.tab = Controles.Tab(self)
        self.tab.new_tab(self.wexternals, _("External engines"))
        self.tab.new_tab(self.wconf_tutor, _("Tutor"))
        self.tab.new_tab(self.wconf_analyzer, _("Analyzer"))
        self.tab.new_tab(self.wothers, _("Others"))
        self.tab.dispatchChange(self.cambiada_tab)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("OPTION", _("Label"), 180)
        o_columns.nueva("VALUE", _("Value"), 200, edicion=Delegados.MultiEditor(self))
        o_columns.nueva("DEFAULT", _("By default"), 90)
        self.grid_conf = Grid.Grid(self, o_columns, siSelecFilas=False, is_editable=True)
        self.register_grid(self.grid_conf)

        # Layout
        ly_left = Colocacion.V().control(tb).control(self.tab).margen(0)
        w = QtWidgets.QWidget()
        w.setLayout(ly_left)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(w)
        self.splitter.addWidget(self.grid_conf)
        self.register_splitter(self.splitter, "conf")
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        layout = Colocacion.H().control(self.splitter)
        self.setLayout(layout)

        dic_def = {"_SIZE_": "1209,540", "SP_conf": [719, 463]}
        self.restore_video(siTam=True, dicDef=dic_def)
        self.cambiada_tab(0)

    def cambiada_tab(self, num):
        if num == 0:
            w = self.wexternals
        elif num == 1:
            w = self.wconf_tutor
        elif num == 2:
            w = self.wconf_analyzer
        else:
            self.engine = None
            self.li_uci_options = None
            self.grid_conf.refresh()
            return
        w.activate_this()
        self.w_current = w

    def me_set_editor(self, parent):
        recno = self.grid_conf.recno()
        opcion = self.li_uci_options[recno]
        key = opcion.name
        value = opcion.valor
        for xkey, xvalue in self.engine.liUCI:
            if xkey == key:
                value = xvalue
                break
        if key is None:
            return None

        control = lista = minimo = maximo = None
        tipo = opcion.tipo
        if tipo == "spin":
            control = "sb"
            minimo = opcion.minimo
            maximo = opcion.maximo
        elif tipo in ("check", "button"):
            if value == "true":
                value = "false"
            else:
                value = "true"
            self.engine.set_uci_option(key, value)
            self.w_current.set_changed()
            self.grid_conf.refresh()
        elif tipo == "combo":
            lista = [(var, var) for var in opcion.li_vars]
            control = "cb"
        elif tipo == "string":
            control = "ed"

        self.me_control = control
        self.me_key = key

        if control == "ed":
            return Controles.ED(parent, value)
        elif control == "cb":
            return Controles.CB(parent, lista, value)
        elif control == "sb":
            return Controles.SB(parent, value, minimo, maximo)
        return None

    def set_engine(self, engine, with_multipv=True):
        self.engine = engine
        if self.grid_conf:
            if self.engine:
                self.li_uci_options = self.engine.li_uci_options_editable()
                if not with_multipv:
                    self.li_uci_options = [op for op in self.li_uci_options if op.name != "MultiPV"]
                self.grid_conf.refresh()
                self.grid_conf.gotop()
                self.grid_conf.show()
            else:
                self.grid_conf.refresh()

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
        opcion = self.li_uci_options[nfila]
        self.engine.set_uci_option(opcion.name, valor)
        self.w_current.set_changed()

    def save(self):
        self.wexternals.save()
        self.wconf_tutor.save()
        self.wconf_analyzer.save()
        self.configuration.graba()
        self.save_video()

    def terminar(self):
        self.save()
        self.accept()

    def closeEvent(self, event):
        self.save()

    def grid_num_datos(self, grid):
        return len(self.li_uci_options) if self.engine else 0

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        op = self.li_uci_options[row]
        if key == "OPTION":
            if op.minimo != op.maximo:
                if op.minimo < 0:
                    return op.name + " (%d - %+d)" % (op.minimo, op.maximo)
                else:
                    return op.name + " (%d - %d)" % (op.minimo, op.maximo)
            else:
                return op.name
        elif key == "DEFAULT":
            df = str(op.default)
            return df.lower() if op.tipo == "check" else df
        else:
            name = op.name
            valor = op.valor
            for xname, xvalue in self.engine.liUCI:
                if xname == name:
                    valor = xvalue
                    break
            valor = str(valor)
            return valor.lower() if op.tipo == "check" else valor

    def grid_bold(self, grid, row, o_column):
        op = self.li_uci_options[row]
        return op.default != op.valor


class WConfExternals(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self, owner)

        self.owner = owner

        self.lista_motores = Code.configuration.list_external_engines()
        self.is_changed = False

        # Toolbar
        li_acciones = [
            (_("New"), Iconos.TutorialesCrear(), self.nuevo),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Internal engines"), Iconos.MasDoc(), self.importar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            None,
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
            (_("Command"), Iconos.Terminal(), self.command),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ALIAS", _("Alias"), 114)
        o_columns.nueva("ENGINE", _("Engine"), 128)
        o_columns.nueva("AUTOR", _("Author"), 132)
        o_columns.nueva("INFO", _("Information"), 205)
        o_columns.nueva("ELO", _("Elo"), 64, align_center=True)
        o_columns.nueva("DEPTH", _("Depth"), 64, align_center=True)
        o_columns.nueva("TIME", _("Time"), 64, align_center=True)

        self.grid = None

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.owner.register_grid(self.grid)

        layout = Colocacion.V().control(tb).control(self.grid).margen(0)
        self.setLayout(layout)

        self.grid.gotop()
        self.grid.setFocus()

    def activate_this(self):
        row = self.grid.recno()
        if row >= 0:
            self.owner.set_engine(self.lista_motores[row])
        else:
            self.owner.set_engine(None)
        self.grid.setFocus()

    def set_changed(self):
        self.is_changed = True

    def grid_setvalue(self, grid, nfila, column, valor):
        opcion = self.engine.li_uci_options_editable()[nfila]
        self.engine.set_uci_option(opcion.name, valor)
        self.set_changed()

    def save(self):
        if self.is_changed:
            self.is_changed = False
            li = [eng.save() for eng in self.lista_motores]
            Util.save_pickle(Code.configuration.file_external_engines(), li)
            Code.configuration.relee_engines()

    def grid_cambiado_registro(self, grid, row, oCol):
        if grid == self.grid:
            if row >= 0:
                self.owner.set_engine(self.lista_motores[row])

    def grid_num_datos(self, grid):
        return len(self.lista_motores)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        me = self.lista_motores[row]
        if key == "AUTOR":
            return me.autor
        elif key == "ALIAS":
            return me.key
        elif key == "ENGINE":
            return me.name
        elif key == "INFO":
            return me.id_info.replace("\n", ", ")
        elif key == "ELO":
            return str(me.elo) if me.elo else "-"
        elif key == "DEPTH":
            return str(me.max_depth) if me.max_depth else "-"
        elif key == "TIME":
            return str(me.max_time) if me.max_time else "-"

    def command(self):
        separador = FormLayout.separador
        li_gen = [separador, ]
        config = FormLayout.Fichero(_("File"), "exe" if Code.is_windows else "*", False)
        li_gen.append((config, ""))

        for num in range(1, 11):
            li_gen.append(("%s:" % (_("Argument %d") % num), ""))
        li_gen.append(separador)
        resultado = FormLayout.fedit(li_gen, title=_("Command"), parent=self, anchoMinimo=600, icon=Iconos.Terminal())
        if resultado:
            nada, resp = resultado
            command = resp[0]
            liArgs = []
            if not command or not os.path.isfile(command):
                return
            for x in range(1, len(resp)):
                arg = resp[x].strip()
                if arg:
                    liArgs.append(arg)

            um = QTUtil2.one_moment_please(self)
            me = Engines.Engine(path_exe=command, args=liArgs)
            li_uci = me.read_uci_options()
            um.final()
            if not li_uci:
                QTUtil2.message_bold(self, _X(_("The file %1 does not correspond to a UCI engine type."), command))
                return None

            # Editamos
            w = WEngineFast(self, self.lista_motores, me)
            if w.exec_():
                self.lista_motores.append(me)
                self.grid.refresh()
                self.grid.gobottom(0)
                self.set_changed()

    def nuevo(self):
        me = WEngines.select_engine(self)
        if not me:
            return

        # Editamos
        w = WEngineFast(self, self.lista_motores, me)
        if w.exec_():
            self.lista_motores.append(me)

            self.grid.refresh()
            self.grid.gobottom(0)
            self.set_changed()

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key
        if key == "ALIAS":
            key = "key"
        elif key == "ENGINE":
            key = "name"
        elif key == "ELO":
            key = "elo"
        else:
            return
        self.lista_motores.sort(key=operator.attrgetter(key))
        self.grid.refresh()
        self.grid.gotop()
        self.set_changed()

    def modificar(self):
        if len(self.lista_motores):
            row = self.grid.recno()
            if row >= 0:
                me = self.lista_motores[row]
                # Editamos, y graba si hace falta
                w = WEngineFast(self, self.lista_motores, me)
                if w.exec_():
                    self.grid.refresh()
                    self.set_changed()

    def grid_doble_click(self, grid, row, o_column):
        self.modificar()

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            li = self.lista_motores
            a, b = li[row], li[row - 1]
            li[row], li[row - 1] = b, a
            self.grid.goto(row - 1, 0)
            self.grid.refresh()
            self.set_changed()

    def abajo(self):
        row = self.grid.recno()
        li = self.lista_motores
        if row < len(li) - 1:
            a, b = li[row], li[row + 1]
            li[row], li[row + 1] = b, a
            self.grid.goto(row + 1, 0)
            self.grid.refresh()
            self.set_changed()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), self.lista_motores[row].key)):
                del self.lista_motores[row]
                if row < len(self.lista_motores):
                    self.grid_cambiado_registro(self.grid, row, None)
                else:
                    self.grid.refresh()
                    self.grid.gobottom()
                self.set_changed()
            self.grid.setFocus()

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            me = self.lista_motores[row].clone()
            w = WEngineFast(self, self.lista_motores, me)
            if w.exec_():
                self.lista_motores.append(me)
                self.grid.refresh()
                self.grid.gobottom(0)
                self.set_changed()

    def importar(self):
        menu = QTVarios.LCMenu(self)
        lista = Code.configuration.combo_engines()
        nico = QTVarios.rondo_puntos()
        for name, key in lista:
            menu.opcion(key, name, nico.otro())

        resp = menu.lanza()
        if not resp:
            return

        me = Code.configuration.buscaRival(resp).clone()
        w = WEngineFast(self, self.lista_motores, me)
        if w.exec_():
            me.parent_external = me.key
            self.lista_motores.append(me)
            self.grid.refresh()
            self.grid.gobottom(0)
            self.set_changed()


class WEngineFast(QtWidgets.QDialog):
    def __init__(self, w_parent, list_engines, engine, is_tournament=False):

        super(WEngineFast, self).__init__(w_parent)

        self.setWindowTitle(engine.version)
        self.setWindowIcon(Iconos.Engine())
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        self.external_engine = engine
        self.list_engines = list_engines
        self.is_tournament = is_tournament
        self.imported = engine.parent_external is not None

        # Toolbar
        tb = QTVarios.tb_accept_cancel(self)

        lb_alias = Controles.LB2P(self, _("Alias"))
        self.edAlias = Controles.ED(self, engine.key).anchoMinimo(360)

        if not self.imported:
            lb_nombre = Controles.LB2P(self, _("Name"))
            self.edNombre = Controles.ED(self, engine.name).anchoMinimo(360)

        lb_info = Controles.LB(self, _("Information") + ": ")
        self.emInfo = Controles.EM(self, engine.id_info, siHTML=False).anchoMinimo(360).altoFijo(60)

        lb_elo = Controles.LB(self, "ELO: ")
        self.sbElo = Controles.SB(self, engine.elo, 0, 4000)

        lb_depth = Controles.LB(self, _("Max depth") + ": ")
        self.sbDepth = Controles.SB(self, engine.max_depth, 0, 50)

        lb_time = Controles.LB(self, _("Maximum seconds to think") + ": ")
        self.edTime = Controles.ED(self, "").ponFloat(engine.max_time).anchoFijo(60).align_right()

        lb_exe = Controles.LB(self, "%s: %s" % (_("File"), Code.relative_root(engine.path_exe)))

        # Layout
        ly = Colocacion.G()
        ly.controld(lb_alias, 0, 0).control(self.edAlias, 0, 1)
        if not self.imported:
            ly.controld(lb_nombre, 1, 0).control(self.edNombre, 1, 1)
        ly.controld(lb_info, 2, 0).control(self.emInfo, 2, 1)
        ly.controld(lb_elo, 3, 0).control(self.sbElo, 3, 1)
        ly.controld(lb_depth, 4, 0).control(self.sbDepth, 4, 1)
        ly.controld(lb_time, 5, 0).control(self.edTime, 5, 1)
        ly.control(lb_exe, 6, 0, 1, 2)

        layout = Colocacion.V().control(tb).otro(ly)

        self.setLayout(layout)

        self.edAlias.setFocus()

    def aceptar(self):
        alias = self.edAlias.texto().strip()
        if not alias:
            QTUtil2.message_error(self, _("You have not indicated any alias"))
            return

        # Comprobamos que no se repita el alias
        for engine in self.list_engines:
            if (self.external_engine != engine) and (engine.key == alias):
                QTUtil2.message_error(
                    self,
                    _(
                        "There is already another engine with the same alias, the alias must change in order to have both."
                    ),
                )
                return
        self.external_engine.key = alias
        if not self.imported:
            name = self.edNombre.texto().strip()
            self.external_engine.name = name if name else alias
        self.external_engine.id_info = self.emInfo.texto()
        self.external_engine.elo = self.sbElo.valor()
        self.external_engine.max_depth = self.sbDepth.valor()
        self.external_engine.max_time = self.edTime.textoFloat()

        self.accept()


class WConfTutor(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self, owner)

        self.configuration = Code.configuration

        self.owner = owner
        self.engine = self.configuration.engine_tutor()

        lb_engine = Controles.LB2P(self, _("Engine"))
        self.cb_engine = Controles.CB(self, self.configuration.help_multipv_engines(True), self.engine.key)
        self.cb_engine.capture_changes(self.changed_engine)

        lb_time = Controles.LB2P(self, _("Duration of tutor analysis (secs)"))
        self.ed_time = Controles.ED(self).tipoFloat(self.configuration.x_tutor_mstime / 1000.0).anchoFijo(40)

        lb_depth = Controles.LB2P(self, _("Depth"))
        self.ed_depth = Controles.ED(self).tipoInt(self.configuration.x_tutor_depth).anchoFijo(30)

        lb_multipv = Controles.LB2P(self, _("Number of variations evaluated by the engine (MultiPV)"))
        self.ed_multipv = Controles.ED(self).tipoIntPositive(self.configuration.x_tutor_multipv).anchoFijo(30)
        lb_maximum = Controles.LB(self, _("0 = Maximum"))
        ly_multi = Colocacion.H().control(self.ed_multipv).control(lb_maximum).relleno()

        self.chb_disabled = Controles.CHB(
            self, _("Disabled at the beginning of the game"), not self.configuration.x_default_tutor_active
        )
        self.chb_background = Controles.CHB(
            self, _("Work in the background, when possible"), not self.configuration.x_engine_notbackground
        )
        lb_priority = Controles.LB2P(self, _("Process priority"))
        self.cb_priority = Controles.CB(self, Priorities.priorities.combo(), self.configuration.x_tutor_priority)
        lb_tutor_position = Controles.LB2P(self, _("Tutor boards position"))
        li_pos_tutor = [
            (_("Horizontal"), POS_TUTOR_HORIZONTAL),
            (_("Horizontal") + " 2+1", POS_TUTOR_HORIZONTAL_2_1),
            (_("Horizontal") + " 1+2", POS_TUTOR_HORIZONTAL_1_2),
            (_("Vertical"), POS_TUTOR_VERTICAL),
        ]
        self.cb_board_position = Controles.CB(self, li_pos_tutor, self.configuration.x_tutor_view)

        lb_sensitivity = Controles.LB2P(self, _("Tutor appearance condition"))
        li_types = [
            (_("Always"), 0),
            (_("Dubious move") + " (?!)", INACCURACY),
            (_("Mistake") + " (?)", MISTAKE),
            (_("Blunder") + " (??)", BLUNDER),
        ]
        self.cb_type = Controles.CB(self, li_types, self.configuration.x_tutor_diftype)

        layout = Colocacion.G()
        layout.controld(lb_engine, 0, 0).control(self.cb_engine, 0, 1)
        layout.controld(lb_time, 1, 0).control(self.ed_time, 1, 1)
        layout.controld(lb_depth, 2, 0).control(self.ed_depth, 2, 1)
        layout.controld(lb_multipv, 3, 0).otro(ly_multi, 3, 1)
        layout.controld(lb_priority, 4, 0).control(self.cb_priority, 4, 1)
        layout.controld(lb_tutor_position, 5, 0).control(self.cb_board_position, 5, 1)
        layout.filaVacia(6, 30)
        layout.controld(lb_sensitivity, 7, 0).control(self.cb_type, 7, 1)
        layout.filaVacia(8, 30)
        layout.control(self.chb_disabled, 9, 0, numColumnas=2)
        layout.control(self.chb_background, 10, 0, numColumnas=2)

        ly = Colocacion.V().otro(layout).relleno(1)
        lyh = Colocacion.H().otro(ly).relleno(1).margen(30)

        self.setLayout(lyh)

        self.changed_engine()
        self.is_changed = False

        for control in (self.chb_background, self.chb_disabled):
            control.capture_changes(self, self.set_changed)

        for control in (
                self.cb_priority,
                self.cb_board_position,
                self.ed_time,
                self.ed_depth,
                self.ed_multipv,
                self.cb_type,
        ):
            control.capture_changes(self.set_changed)

    def changed_engine(self):
        key = self.cb_engine.valor()
        if key is None:
            key = "stockfish"
        self.engine = self.configuration.dic_engines[key].clone()
        self.engine.reset_uci_options()
        dic = self.configuration.read_variables("TUTOR_ANALYZER")
        for name, valor in dic.get("TUTOR", []):
            self.engine.set_uci_option(name, valor)
        self.owner.set_engine(self.engine, False)
        self.set_changed()

    def set_changed(self):
        self.is_changed = True

    def save(self):
        if self.is_changed:
            self.is_changed = False
            self.configuration.x_tutor_clave = self.engine.key
            self.configuration.x_tutor_mstime = self.ed_time.textoFloat() * 1000
            self.configuration.x_tutor_depth = self.ed_depth.textoInt()
            self.configuration.x_tutor_multipv = self.ed_multipv.textoInt()
            self.configuration.x_tutor_priority = self.cb_priority.valor()

            self.configuration.x_tutor_view = self.cb_board_position.valor()
            self.configuration.x_engine_notbackground = not self.chb_background.valor()
            self.configuration.x_default_tutor_active = not self.chb_disabled.valor()
            self.configuration.x_tutor_diftype = self.cb_type.valor()

            self.configuration.graba()

            dic = self.configuration.read_variables("TUTOR_ANALYZER")
            dic["TUTOR"] = self.engine.list_uci_changed()
            self.configuration.write_variables("TUTOR_ANALYZER", dic)
            Code.procesador.cambiaXTutor()

    def activate_this(self):
        valor = self.cb_engine.valor()
        self.cb_engine.rehacer(self.configuration.help_multipv_engines(True), valor)
        self.owner.set_engine(self.engine, False)


class WConfAnalyzer(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self, owner)

        self.configuration = Code.configuration

        self.owner = owner
        self.engine = self.configuration.engine_analyzer()
        self.is_changed = False

        lb_engine = Controles.LB2P(self, _("Engine"))
        self.cb_engine = Controles.CB(self, self.configuration.help_multipv_engines(False), self.engine.key)
        self.cb_engine.capture_changes(self.changed_engine)

        lb_time = Controles.LB2P(self, _("Duration of analysis (secs)"))
        self.ed_time = Controles.ED(self).tipoFloat(self.configuration.x_analyzer_mstime / 1000.0).anchoFijo(40)

        lb_depth = Controles.LB2P(self, _("Depth"))
        self.ed_depth = Controles.ED(self).tipoInt(self.configuration.x_analyzer_depth).anchoFijo(30)

        lb_multipv = Controles.LB2P(self, _("Number of variations evaluated by the engine (MultiPV)"))
        self.ed_multipv = Controles.ED(self).tipoIntPositive(self.configuration.x_analyzer_multipv).anchoFijo(30)
        lb_maximum = Controles.LB(self, _("0 = Maximum"))
        ly_multi = Colocacion.H().control(self.ed_multipv).control(lb_maximum).relleno()

        lb_priority = Controles.LB2P(self, _("Process priority"))
        self.cb_priority = Controles.CB(self, Priorities.priorities.combo(), self.configuration.x_analyzer_priority)

        bt_analysis_parameters = Controles.PB(
            self, _("Analysis configuration parameters"), rutina=self.config_analysis_parameters, plano=False
        )

        lb_analysis_bar = Controles.LB2P(self, _("Limits in the Analysis Bar (0=no limit)")).set_font_type(puntos=12,
                                                                                                           peso=700)
        lb_depth_ab = Controles.LB2P(self, _("Depth"))
        self.ed_depth_ab = Controles.ED(self).tipoInt(self.configuration.x_analyzer_depth_ab).anchoFijo(30)
        lb_time_ab = Controles.LB2P(self, _("Time in seconds"))
        self.ed_time_ab = Controles.ED(self).tipoFloat(self.configuration.x_analyzer_mstime_ab / 1000.0).anchoFijo(40)

        layout = Colocacion.G()
        layout.controld(lb_engine, 0, 0).control(self.cb_engine, 0, 1)
        layout.controld(lb_time, 1, 0).control(self.ed_time, 1, 1)
        layout.controld(lb_depth, 2, 0).control(self.ed_depth, 2, 1)
        layout.controld(lb_multipv, 3, 0).otro(ly_multi, 3, 1)
        layout.controld(lb_priority, 4, 0).control(self.cb_priority, 4, 1)
        layout.filaVacia(5, 20)
        layout.controld(lb_analysis_bar, 6, 0)
        layout.controld(lb_time_ab, 7, 0).control(self.ed_time_ab, 7, 1)
        layout.controld(lb_depth_ab, 8, 0).control(self.ed_depth_ab, 8, 1)

        ly = Colocacion.V().otro(layout).espacio(30).control(bt_analysis_parameters).relleno(1)
        lyh = Colocacion.H().otro(ly).relleno(1).margen(30)

        self.setLayout(lyh)

        for control in (
        self.cb_priority, self.ed_multipv, self.ed_depth, self.ed_time, self.ed_depth_ab, self.ed_time_ab):
            control.capture_changes(self.set_changed)

    def config_analysis_parameters(self):
        w = WindowAnalysisConfig.WConfAnalysis(self, self)
        w.exec_()

    def refresh_analysis(self):  # llamado por WConfAnalysis
        pass

    def changed_engine(self):
        key = self.cb_engine.valor()
        if key is None:
            key = self.configuration.x_analyzer_clave
        self.engine = self.configuration.dic_engines[key].clone()
        self.engine.reset_uci_options()
        dic = self.configuration.read_variables("TUTOR_ANALYZER")
        for name, valor in dic.get("ANALYZER", []):
            self.engine.set_uci_option(name, valor)
        self.owner.set_engine(self.engine, False)
        self.set_changed()

    def set_changed(self):
        self.is_changed = True

    def save(self):
        if self.is_changed:
            self.is_changed = False

            self.configuration.x_analyzer_clave = self.engine.key
            self.configuration.x_analyzer_mstime = self.ed_time.textoFloat() * 1000
            self.configuration.x_analyzer_depth = self.ed_depth.textoInt()
            self.configuration.x_analyzer_multipv = self.ed_multipv.textoInt()
            self.configuration.x_analyzer_priority = self.cb_priority.valor()
            self.configuration.x_analyzer_mstime_ab = self.ed_time_ab.textoFloat() * 1000
            self.configuration.x_analyzer_depth_ab = self.ed_depth_ab.textoInt()

            dic = self.configuration.read_variables("TUTOR_ANALYZER")
            dic["ANALYZER"] = self.engine.list_uci_changed()
            self.configuration.write_variables("TUTOR_ANALYZER", dic)
            Code.procesador.cambiaXAnalyzer()

    def activate_this(self):
        self.cb_engine.rehacer(self.configuration.help_multipv_engines(False), self.engine.key)
        self.owner.set_engine(self.engine, False)


class WOthers(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self, owner)

        self.configuration = Code.configuration

        self.owner = owner
        self.is_changed = False

        lb_maia = Controles.LB2P(self, _("Nodes used with Maia engines"))
        li_options = [
            (_("1 node as advised by the authors"), False),
            (_("From 1 (1100) to 450 nodes (1900), similar strength as other engines"), True),
        ]
        self.cb_maia = Controles.CB(self, li_options, Code.configuration.x_maia_nodes_exponential).capture_changes(
            self.save
        )
        self.cb_maia.set_multiline(440)

        lb_gaviota = Controles.LB2P(self, _("Gaviota Tablebases"))
        self.gaviota = Code.configuration.folder_gaviota()
        self.bt_gaviota = Controles.PB(self, self.gaviota, self.change_gaviota, plano=False)
        self.bt_gaviota_remove = Controles.PB(self, "", self.remove_gaviota).ponIcono(Iconos.Delete())
        ly_gav = Colocacion.H().control(self.bt_gaviota).control(self.bt_gaviota_remove).relleno()

        lb_stockfish = Controles.LB2P(self, "Stockfish")
        self.lb_stockfish_version = Controles.LB(self, CheckEngines.current_stockfish()).set_font_type(peso=500,
                                                                                                       puntos=11)
        self.lb_stockfish_version.setStyleSheet("border:1px solid gray;padding:3px")
        bt_stockfish = Controles.PB(self, "", self.change_stockfish).ponIcono(Iconos.Reiniciar()).ponToolTip(
            _("Update"))
        ly_stk = Colocacion.H().control(self.lb_stockfish_version).control(bt_stockfish).relleno()

        sep = 40
        layout = Colocacion.G()
        layout.controld(lb_maia, 0, 0)
        layout.control(self.cb_maia, 0, 1)
        layout.filaVacia(1, sep)
        layout.controld(lb_gaviota, 2, 0)
        layout.otro(ly_gav, 2, 1)
        layout.filaVacia(3, sep)
        layout.controld(lb_stockfish, 4, 0)
        layout.otro(ly_stk, 4, 1)

        layoutg = Colocacion.V().espacio(sep).otro(layout).relleno().margen(30)

        self.setLayout(layoutg)

        self.set_gaviota()

    def set_gaviota(self):
        self.bt_gaviota.set_text("   %s   " % Code.relative_root(self.gaviota))

    def change_gaviota(self):
        folder = SelectFiles.get_existing_directory(self, self.gaviota, _("Gaviota Tablebases"))
        if folder:
            self.gaviota = folder
            self.set_gaviota()
            self.save()

    def remove_gaviota(self):
        self.gaviota = Code.configuration.carpeta_gaviota_defecto()
        self.set_gaviota()
        self.save()

    def change_stockfish(self):
        self.lb_stockfish_version.set_text("")
        CheckEngines.check_stockfish(self.owner, True)
        self.lb_stockfish_version.set_text(CheckEngines.current_stockfish())

    def save(self):
        self.configuration.x_carpeta_gaviota = self.gaviota
        self.configuration.x_maia_nodes_exponential = self.cb_maia.valor()
        Code.configuration.graba()
