import time

from PySide2 import QtGui

import Code
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.TurnOnLights import TurnOnLights


class WTurnOnLights(LCDialog.LCDialog):
    def __init__(self, procesador, name, title, icono, folder, li_tam_blocks, one_line):
        self.one_line = one_line
        if one_line:
            self.tol = TurnOnLights.read_oneline_tol()
        else:
            self.tol = TurnOnLights.read_tol(name, title, folder, li_tam_blocks)
        self.reinit = False

        titulo = _("Turn on the lights") + ": " + title
        if self.tol.is_calculation_mode():
            tipo = _("Calculation mode")
            background = "#88AA3A"
        else:
            tipo = _("Memory mode")
            background = "#BDDBE8"

        self.procesador = procesador
        extparam = "tol%s-%d" % (name, self.tol.work_level)

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        self.colorTheme = QTUtil.qtColor("#F0F0F0")

        lb = Controles.LB(self, tipo)
        lb.set_background(background).align_center().ponTipoLetra(puntos=14)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        anterior, siguiente, terminado = self.tol.prev_next()
        if anterior:
            tb.new(_("Previous"), Iconos.Anterior(), self.goto_previous)
        if siguiente:
            tb.new(_("Next"), Iconos.Siguiente(), self.goto_next)
        tb.new(_("Config"), Iconos.Configurar(), self.config)
        tb.new(_("Information"), Iconos.Informacion(), self.colors)
        if terminado:
            tb.new(_("Rebuild"), Iconos.Reindexar(), self.rebuild)

        # Lista
        o_columns = Columnas.ListaColumnas()
        work_level = self.tol.work_level + 1
        o_columns.nueva("THEME", _("Level %d/%d") % (work_level, self.tol.num_levels), 175)

        edicionIconos = Delegados.PmIconosColor()
        self.dicIconos = {}
        for k, pm in edicionIconos.dicpmIconos.items():
            self.dicIconos[k] = QtGui.QIcon(pm)

        for x in range(self.tol.num_blocks):
            o_columns.nueva("BLOCK%d" % x, "%d" % (x + 1,), 42, align_center=True, edicion=edicionIconos)

        self.grid = grid = Grid.Grid(self, o_columns, altoFila=42, background="white")
        self.grid.setAlternatingRowColors(False)
        self.grid.tipoLetra(puntos=10, peso=500)
        nAnchoPgn = self.grid.anchoColumnas() + 20
        self.grid.setMinimumWidth(nAnchoPgn)
        self.register_grid(grid)

        # Colocamos ---------------------------------------------------------------
        ly = Colocacion.V().control(lb).control(tb).control(self.grid)

        self.setLayout(ly)

        alto = self.tol.num_themes * 42 + 146
        self.restore_video(siTam=True, altoDefecto=alto, anchoDefecto=max(nAnchoPgn, 480))

    def terminar(self):
        self.save_video()
        self.reject()

    def grid_num_datos(self, grid):
        return self.tol.num_themes

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "THEME":
            return "  " + self.tol.nom_theme(row)
        elif col.startswith("BLOCK"):
            block = int(col[5:])
            return self.tol.val_block(row, block)

    def grid_color_fondo(self, grid, row, o_column):
        col = o_column.key
        if col == "THEME":
            return self.colorTheme
        return None

    def grid_doble_click(self, grid, row, o_column):
        col = o_column.key
        if col.startswith("BLOCK"):
            block = int(col[5:])
            self.num_theme = row
            self.num_block = block
            self.save_video()
            self.accept()

    def grid_right_button(self, grid, row, o_column, modificadores):
        col = o_column.key
        num_theme = row
        if col.startswith("BLOCK"):
            num_block = int(col[5:])
            self.right_button_block(num_theme, num_block)
        else:
            self.right_button_theme(num_theme)

    def right_button_theme(self, num_theme):
        tt = 0
        te = 0
        ta = 0
        nm = 0
        lt = 0
        for num_block in range(self.tol.num_blocks):
            block = self.tol.get_block(num_theme, num_block)
            litimes = block.times
            if not litimes and not block.reinits:
                continue
            lt += len(litimes)
            nm += block.num_moves()
            if litimes:
                for segs, fecha, time_used, errores, hints in litimes:
                    tt += time_used
                    te += errores
                    ta += hints
            if block.reinits:
                for segs, fecha, errores, hints in block.reinits:
                    tt += segs
                    te += errores
                    ta += hints
        menu = QTVarios.LCMenu(self)
        menu.ponTipoLetra(name=Code.font_mono, puntos=10)

        menu.separador()
        menu.opcion(None, "%16s %6d" % (_("Errors"), te))
        menu.separador()
        menu.opcion(None, "%16s %6d" % (_("Hints"), ta))
        menu.separador()
        menu.opcion(None, "%16s %15.02f  %s" % (_("Total time"), tt, time.strftime("%H:%M:%S", time.gmtime(tt))))
        menu.lanza()

    def right_button_block(self, num_theme, num_block):
        block = self.tol.get_block(num_theme, num_block)
        litimes = block.times
        nmoves = block.num_moves()
        if not litimes and not block.reinits:
            return
        menu = QTVarios.LCMenu(self)
        menu.ponTipoLetra(name=Code.font_mono, puntos=10)
        tt = 0
        te = 0
        ta = 0
        mixed_results = False
        for dato in litimes:
            segs, fecha, time_used, errores, hints = dato
            txt, ico = TurnOnLights.qualification(segs, self.tol.is_calculation_mode())
            menu.opcion(
                None,
                "%d-%02d-%02d %02d:%02d %6.02f  %6.02f  %s"
                % (fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, segs, time_used, txt),
                self.dicIconos[ico],
            )
            tt += time_used
            te += errores
            ta += hints

        if litimes:
            menu.separador()
            menu.opcion(None, "%16s %6.02f" % (_("Average"), tt / (nmoves * len(litimes))))
            menu.separador()
        plant = "%16s %15.02f  %s"
        if block.reinits:
            tr = 0.0
            for dato in block.reinits:
                segs, fecha, errores, hints = dato
                tr += segs
                tt += segs
                te += errores
                ta += hints
            menu.separador()
            menu.opcion(None, plant % (_("Restarts"), tr, time.strftime("%H:%M:%S", time.gmtime(tr))))
        if not mixed_results:
            menu.separador()
            menu.opcion(None, "%16s %6d" % (_("Errors"), te))
            menu.separador()
            menu.opcion(None, "%16s %6d" % (_("Hints"), ta))
        menu.separador()
        menu.opcion(None, plant % (_("Total time"), tt, time.strftime("%H:%M:%S", time.gmtime(tt))))

        menu.lanza()

    def goto_previous(self):
        self.tol.work_level -= 1
        TurnOnLights.write_tol(self.tol)
        self.reinit = True
        self.save_video()
        self.accept()

    def goto_next(self):
        self.tol.work_level += 1
        TurnOnLights.write_tol(self.tol)
        self.reinit = True
        self.save_video()
        self.accept()

    def config(self):
        menu = QTVarios.LCMenu(self)
        if self.one_line:
            menu.opcion("change", _("Change options and create new training"), Iconos.TOLchange())
            menu.separador()
        smenu = menu.submenu(_("What to do after solving"), Iconos.Tacticas())
        go_fast = self.tol.go_fast
        dico = {True: Iconos.Aceptar(), False: Iconos.PuntoAmarillo()}
        smenu.opcion("t_False", _("Stop"), dico[go_fast is False])
        smenu.opcion("t_True", _("Jump to the next"), dico[go_fast is True])
        smenu.opcion("t_None", _("Jump to the next from level 2"), dico[go_fast is None])
        menu.separador()
        menu.opcion("remove", _("Remove all results of all levels"), Iconos.Cancelar())

        resp = menu.lanza()
        if resp:
            if resp.startswith("t_"):
                self.tol.go_fast = eval(resp[2:])
                TurnOnLights.write_tol(self.tol)
            elif resp == "remove":
                self.rebuild()
            elif resp == "change":
                self.cambiar_one_line()

    def rebuild(self):
        if not QTUtil2.pregunta(
            self, _("Are you sure you want to delete all results of all levels and start again from scratch?")
        ):
            return
        if self.one_line:
            self.tol.new()
        else:
            TurnOnLights.remove_tol(self.tol)
        self.reinit = True
        self.save_video()
        self.accept()

    def cambiar_one_line(self):
        resp = configOneLine(self, self.procesador)
        if resp:
            self.reinit = True
            self.save_video()
            self.accept()

    def colors(self):
        menu = QTVarios.LCMenu(self)
        num, ultimo = TurnOnLights.numColorMinimum(self.tol)
        snum = str(num)
        thinkMode = self.tol.is_calculation_mode()
        for txt, key, secs, secsThink in TurnOnLights.QUALIFICATIONS:
            label = '%s < %0.2f"' % (_F(txt), secsThink if thinkMode else secs)
            if key == snum and not ultimo:
                label += " = %s" % _("Minimum to access next level")
            menu.opcion(None, label, self.dicIconos[key])
            menu.separador()
        menu.lanza()


def windowTurnOnLigths(procesador, name, title, icono, folder, li_tam_blocks, one_line):
    while True:
        w = WTurnOnLights(procesador, name, title, icono, folder, li_tam_blocks, one_line)
        if w.exec_():
            if not w.reinit:
                return w.num_theme, w.num_block, w.tol
        else:
            break
    return None


class WConfigOneLineTOL(LCDialog.LCDialog):
    def __init__(self, owner, procesador):

        title = _("In one line")
        titulo = _("Turn on the lights") + ": " + title
        extparam = "tolconfoneline"
        icono = Iconos.TOLchange()
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.tol = TurnOnLights.read_oneline_tol()
        self.procesador = procesador

        lbNumPos = Controles.LB2P(self, _("Number of positions"))
        liBlocks = [(str(x), x) for x in range(6, 60, 6)]
        self.cbNumPos = Controles.CB(self, liBlocks, self.tol.num_pos)

        lbtipo = Controles.LB2P(self, _("Mode"))
        liTipos = [(_("Calculation mode"), True), (_("Memory mode"), False)]
        self.cbTipo = Controles.CB(self, liTipos, self.tol.calculation_mode)

        lbfile = Controles.LB2P(self, _("File"))
        pbfile = Controles.PB(self, "", self.newfile).ponIcono(Iconos.Buscar())
        self.lbshowfile = Controles.LB(self, self.tol.fns)
        lyfile = Colocacion.H().control(pbfile).control(self.lbshowfile).relleno(1)

        self.chbauto = Controles.CHB(self, _("Redo each day automatically"), self.tol.auto_day)

        tb = QTVarios.LCTB(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)

        # Colocamos ---------------------------------------------------------------
        ly = Colocacion.G()
        ly.controld(lbNumPos, 1, 0).control(self.cbNumPos, 1, 1)
        ly.controld(lbtipo, 2, 0).control(self.cbTipo, 2, 1)
        ly.controld(lbfile, 3, 0).otro(lyfile, 3, 1)
        ly.control(self.chbauto, 4, 0, 1, 2)

        layout = Colocacion.V().control(tb).espacio(10).otro(ly)

        self.setLayout(layout)

        self.restore_video(siTam=True)

    def aceptar(self):
        num_positions = self.calc_lines_fns(self.tol.fns)
        if num_positions < self.cbNumPos.valor():
            QTUtil2.message_error(self, _("This file has %d solved positions").replace("%d", str(num_positions)))
            return
        self.tol.set_num_pos(self.cbNumPos.valor())
        self.tol.calculation_mode = self.cbTipo.valor()
        self.tol.auto_day = self.chbauto.valor()
        self.tol.new()
        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def calc_lines_fns(self, fns):
        nl = 0
        with open(fns, "rt", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                li = linea.split("|")
                if len(li) >= 3:
                    nl += 1
        return nl

    def newfile(self):
        fns = self.procesador.selectOneFNS(self)
        if fns:
            num_positions = self.calc_lines_fns(fns)
            if num_positions < self.cbNumPos.valor():
                QTUtil2.message_error(self, _("This file has %d solved positions").replace("%d", str(num_positions)))
                return
            self.tol.fns = fns
            self.lbshowfile.setText(fns)


def configOneLine(owner, procesador):
    w = WConfigOneLineTOL(owner, procesador)
    return w.exec_()
