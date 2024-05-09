import os

from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code import Util
from Code.Board import BoardTypes
from Code.Director import (
    TabVisual,
    WindowTab,
    WindowTabVFlechas,
    WindowTabVMarcos,
    WindowTabVMarkers,
    WindowTabVSVGs,
    WindowTabVCircles,
)
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.Translations import TrListas


class WPanelDirector(LCDialog.LCDialog):
    def __init__(self, owner, board):
        self.owner = owner
        self.position = board.last_position
        self.board = board
        self.configuration = board.configuration
        self.fenm2 = self.position.fenm2()
        self.origin_new = None

        self.dbManager = board.dbVisual
        self.leeRecursos()

        titulo = _("Director")
        icono = Iconos.Script()
        extparam = "tabvisualscript1"
        LCDialog.LCDialog.__init__(self, board, titulo, icono, extparam)

        self.ant_foto = None

        self.guion = TabVisual.Guion(board, self)

        # Guion
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            (_("Save"), Iconos.Grabar(), self.grabar),
            (_("New"), Iconos.Nuevo(), self.gnuevo),
            (_("Insert"), Iconos.Insertar(), self.ginsertar),
            (_("Remove"), Iconos.Remove1(), self.gborrar, _("Remove") + " - %s" % _("Backspace key")),
            (_("Remove all"), Iconos.Borrar(), self.borraTodos, _("Remove all") + " - %s" % _("Delete key")),
            None,
            (_("Up"), Iconos.Arriba(), self.garriba),
            (_("Down"), Iconos.Abajo(), self.gabajo),
            None,
            (_("Mark"), Iconos.Marcar(), self.gmarcar),
            None,
            (_("Config"), Iconos.Configurar(), self.gconfig),
            None,
        ]
        self.tb = Controles.TBrutina(self, li_acciones, icon_size=24)
        if self.guion is None:
            self.tb.set_action_visible(self.grabar, False)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 20, align_center=True)
        o_columns.nueva("MARCADO", "", 20, align_center=True, is_ckecked=True)
        o_columns.nueva("TYPE", _("Type"), 50, align_center=True)
        o_columns.nueva("NOMBRE", _("Name"), 100, align_center=True, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("INFO", _("Information"), 100, align_center=True)
        self.g_guion = Grid.Grid(self, o_columns, siCabeceraMovible=False, is_editable=True, siSeleccionMultiple=True)

        self.register_grid(self.g_guion)

        self.chbSaveWhenFinished = Controles.CHB(
            self, _("Save when finished"), self.dbConfig.get("SAVEWHENFINISHED", False)
        )

        # Visuales
        self.selectBanda = WindowTab.SelectBanda(self)

        ly_g = Colocacion.V().control(self.g_guion).control(self.chbSaveWhenFinished)
        ly_sg = Colocacion.H().control(self.selectBanda).otro(ly_g)
        layout = Colocacion.V().control(self.tb).otro(ly_sg).margen(3)

        self.setLayout(layout)

        self.restore_video()

        self.recuperar()
        self.ant_foto = self.foto()

        self.actualizaBandas()
        li = self.dbConfig["SELECTBANDA"]
        if li:
            self.selectBanda.recuperar(li)
        num_lb = self.dbConfig["SELECTBANDANUM"]
        if num_lb is not None:
            self.selectBanda.seleccionarNum(num_lb)

        self.ultDesde = "d4"
        self.ultHasta = "e5"

        self.g_guion.gotop()

    def addText(self):
        self.guion.cierraPizarra()
        tarea = TabVisual.GT_Texto(self.guion)
        row = self.guion.nuevaTarea(tarea, -1)
        self.ponMarcado(row, True)
        self.guion.pizarra.show()
        self.guion.pizarra.mensaje.setFocus()

    def cambiadaPosicion(self):
        self.position = self.board.last_position
        self.fenm2 = self.position.fenm2()
        self.origin_new = None
        self.recuperar()

    def seleccionar(self, lb):
        if lb is None:
            self.owner.setChange(True)
            self.board.enable_all()
        else:
            self.owner.setChange(False)
            self.board.disable_all()

    def funcion(self, number, is_ctrl=False):
        if number == 9:
            if is_ctrl:
                self.selectBanda.seleccionar(None)
            else:
                if self.guion.pizarra:
                    self.guion.cierraPizarra()
                else:
                    self.addText()
        elif number == 0 and is_ctrl:  # Ctrl+F1
            self.borraUltimo()
        elif number == 1 and is_ctrl:  # Ctrl+F2
            self.borraTodos()
        else:
            self.selectBanda.seleccionarNum(number)

    def grabar(self):
        if self.guion is not None:
            li = self.guion.guarda()
            self.board.dbVisual_save(self.fenm2, li)
            QTUtil2.temporary_message(None, _("Saved"), 1.2)

    def recuperar(self):
        self.guion.recupera()
        self.ant_foto = self.foto()
        self.refresh_guion()

    def boardCambiadoTam(self):
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.show()
        QTUtil.refresh_gui()
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "NUMBER":
            return "%d" % (row + 1,)
        if key == "MARCADO":
            return self.guion.marcado(row)
        elif key == "TYPE":
            return self.guion.txt_tipo(row)
        elif key == "NOMBRE":
            return self.guion.name(row)
        elif key == "INFO":
            return self.guion.info(row)

    def creaTareaBase(self, tp, xid, a1h8, row):
        tpid = tp, xid
        if tp == "P":
            tarea = TabVisual.GT_PiezaMueve(self.guion)
            from_sq, to_sq = a1h8[:2], a1h8[2:]
            borra = self.board.dameNomPiezaEn(to_sq)
            tarea.desdeHastaBorra(from_sq, to_sq, borra)
            self.board.enable_all()
        elif tp == "C":
            tarea = TabVisual.GT_PiezaCrea(self.guion)
            borra = self.board.dameNomPiezaEn(a1h8)
            tarea.from_sq(a1h8, borra)
            tarea.pieza(xid)
            self.board.enable_all()
        elif tp == "B":
            tarea = TabVisual.GT_PiezaBorra(self.guion)
            tarea.from_sq(a1h8)
            tarea.pieza(xid)
        else:
            xid = str(xid)
            if tp == TabVisual.TP_FLECHA:
                dicFlecha = self.dbFlechas[xid]
                if dicFlecha is None:
                    return None, None
                regFlecha = BoardTypes.Flecha()
                regFlecha.restore_dic(dicFlecha)
                regFlecha.tpid = tpid
                regFlecha.a1h8 = a1h8
                sc = self.board.creaFlecha(regFlecha)
                tarea = TabVisual.GT_Flecha(self.guion)
            elif tp == TabVisual.TP_MARCO:
                dicMarco = self.dbMarcos[xid]
                if dicMarco is None:
                    return None, None
                regMarco = BoardTypes.Marco()
                regMarco.restore_dic(dicMarco)
                regMarco.tpid = tpid
                regMarco.a1h8 = a1h8
                sc = self.board.creaMarco(regMarco)
                tarea = TabVisual.GT_Marco(self.guion)
            elif tp == TabVisual.TP_CIRCLE:
                dic_circle = self.dbCircles[xid]
                if dic_circle is None:
                    return None, None
                reg_circle = BoardTypes.Circle()
                reg_circle.restore_dic(dic_circle)
                reg_circle.tpid = tpid
                reg_circle.a1h8 = a1h8
                sc = self.board.creaCircle(reg_circle)
                tarea = TabVisual.GT_Circle(self.guion)
            elif tp == TabVisual.TP_SVG:
                dicSVG = self.dbSVGs[xid]
                if dicSVG is None:
                    return None, None
                regSVG = BoardTypes.SVG()
                regSVG.restore_dic(dicSVG)
                regSVG.tpid = tpid
                regSVG.a1h8 = a1h8
                sc = self.board.creaSVG(regSVG, siEditando=True)
                tarea = TabVisual.GT_SVG(self.guion)
            elif tp == TabVisual.TP_MARKER:
                dicMarker = self.dbMarkers[xid]
                if dicMarker is None:
                    return None, None
                regMarker = BoardTypes.Marker()
                regMarker.restore_dic(dicMarker)
                regMarker.tpid = tpid
                regMarker.a1h8 = a1h8
                sc = self.board.creaMarker(regMarker, siEditando=True)
                tarea = TabVisual.GT_Marker(self.guion)
            else:
                return
            sc.ponRutinaPulsada(None, tarea.id())
            tarea.itemSC(sc)

        tarea.marcado(True)
        tarea.registro((tp, xid, a1h8))
        if self.guion is None:
            row = 0
        else:
            row = self.guion.nuevaTarea(tarea, row)

        return tarea, row

    def creaTarea(self, tp, xid, a1h8, row):
        tarea, row = self.creaTareaBase(tp, xid, a1h8, row)
        if tarea is None:
            return None, None
        tarea.registro((tp, xid, a1h8))

        self.g_guion.goto(row, 0)

        self.ponMarcado(row, True)

        return tarea, row

    def editaNombre(self, name):
        li_gen = [(None, None)]
        config = FormLayout.Editbox(_("Name"), ancho=160)
        li_gen.append((config, name))
        ico = Iconos.Grabar()

        resultado = FormLayout.fedit(li_gen, title=_("Name"), parent=self, icon=ico)
        if resultado:
            accion, li_resp = resultado
            name = li_resp[0]
            return name
        return None

    def borrarPizarraActiva(self):
        for n in range(len(self.guion)):
            tarea = self.guion.tarea(n)
            if tarea and tarea.tp() == TabVisual.TP_TEXTO:
                if tarea.marcado():
                    self.borrar_lista([n])

    def gmarcar(self):
        if len(self.guion):
            menu = QTVarios.LCMenu(self)
            f = Controles.FontType(puntos=8, peso=75)
            menu.set_font(f)
            menu.opcion(1, _("All"), Iconos.PuntoVerde())
            menu.opcion(2, _("None"), Iconos.PuntoNaranja())
            resp = menu.lanza()
            if resp:
                siTodos = resp == 1
                for n in range(len(self.guion)):
                    tarea = self.guion.tarea(n)
                    if tarea.tp() in (TabVisual.TP_TEXTO, TabVisual.TP_ACTION, TabVisual.TP_CONFIGURATION):
                        continue
                    siMarcado = tarea.marcado()
                    if siTodos:
                        if not siMarcado:
                            self.grid_setvalue(None, n, None, True)
                    else:
                        if siMarcado:
                            self.grid_setvalue(None, n, None, False)
                self.refresh_guion()

    def desdeHasta(self, titulo, from_sq, to_sq):
        li_gen = [(None, None)]

        config = FormLayout.Casillabox(_("From square"))
        li_gen.append((config, from_sq))

        config = FormLayout.Casillabox(_("To square"))
        li_gen.append((config, to_sq))

        resultado = FormLayout.fedit(li_gen, title=titulo, parent=self)
        if resultado:
            resp = resultado[1]
            self.ultDesde = from_sq = resp[0]
            self.ultHasta = to_sq = resp[1]
            return from_sq, to_sq
        else:
            return None, None

    def gconfig(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("remall", _("Reset everything to factory defaults"), Iconos.Delete())
        menu.separador()
        menu.opcion("remfen", _("Remove all graphics associated with positions"), Iconos.Borrar())
        resp = menu.lanza()
        if resp == "remall":
            if QTUtil2.pregunta(self, _("Are you sure you want to reset graphics in Director to factory defaults?")):
                # self.cierraRecursos()
                fich_recursos = Code.configuration.ficheroRecursos
                fmt_recursos = fich_recursos.replace(".dbl", "%d.dbl")
                pos = 0
                while Util.exist_file(fmt_recursos % pos):
                    pos += 1
                Util.file_copy(Code.configuration.ficheroRecursos, fmt_recursos % pos)
                self.close()
                self.board.dbVisual.reset()
                self.board.lanzaDirector()

        if resp == "remfen":
            if QTUtil2.pregunta(self, _("Are you sure you want to remove all graphics associated with positions?")):
                self.borraTodos()
                self.cierraRecursos()
                self.close()
                self.board.dbVisual.remove_fens()
                self.board.lanzaDirector()

    def gmas(self, insert):
        ta = TabVisual.GT_Action(None)
        liActions = [(_F(txt), Iconos.PuntoRojo(), "GTA_%s" % action) for action, txt in ta.dicTxt.items()]

        liMore = [(_("Text"), Iconos.Texto(), TabVisual.TP_TEXTO), (_("Actions"), Iconos.Run(), liActions)]
        resp = self.selectBanda.menuParaExterior(liMore)
        if resp:
            xid = resp
            row = self.g_guion.recno() if insert else -1
            if xid == TabVisual.TP_TEXTO:
                tarea = TabVisual.GT_Texto(self.guion)
                row = self.guion.nuevaTarea(tarea, row)
                self.ponMarcado(row, True)
            elif resp.startswith("GTA_"):
                self.creaAction(resp[4:], row)
            else:
                li = xid.split("_")
                tp = li[1]
                xid = li[2]
                from_sq, to_sq = self.desdeHasta(_("Director"), self.ultDesde, self.ultHasta)
                if from_sq:
                    self.creaTarea(tp, xid, from_sq + to_sq, row)
            if insert:
                self.g_guion.goto(row, 0)
            else:
                self.g_guion.gobottom()

    def creaAction(self, action, row):
        tarea = TabVisual.GT_Action(self.guion)
        tarea.action(action)
        row = self.guion.nuevaTarea(tarea, row)
        self.refresh_guion()

    def gnuevo(self):
        self.gmas(False)

    def ginsertar(self):
        self.gmas(True)

    def borraUltimo(self):
        row = len(self.guion) - 1
        if row >= 0:
            lista = [row]
            self.borrar_lista(lista)

    def borraTodos(self):
        num = len(self.guion)
        if num:
            self.borrar_lista(list(range(num)))

    def borrar_lista(self, lista=None):
        li = self.g_guion.recnosSeleccionados() if lista is None else lista
        if li:
            li.sort(reverse=True)
            for row in li:
                self.ponMarcado(row, False)
                sc = self.guion.itemTarea(row)
                if sc:
                    self.board.borraMovible(sc)
                else:
                    tarea = self.guion.tarea(row)
                    if tarea and tarea.tp() == TabVisual.TP_TEXTO:
                        self.guion.cierraPizarra()
                self.guion.borra(row)
            if row >= len(self.guion):
                row = len(self.guion) - 1
            self.g_guion.goto(row, 0)
            self.refresh_guion()

    def gborrar(self):
        li = self.g_guion.recnosSeleccionados()
        if li:
            self.borrar_lista(li)

    def garriba(self):
        row = self.g_guion.recno()
        if self.guion.arriba(row):
            self.g_guion.goto(row - 1, 0)
            self.refresh_guion()

    def gabajo(self):
        row = self.g_guion.recno()
        if self.guion.abajo(row):
            self.g_guion.goto(row + 1, 0)
            self.refresh_guion()

    def grid_doble_click(self, grid, row, col):
        key = col.key
        if key == "INFO":
            tarea = self.guion.tarea(row)
            if tarea is None:
                return
            sc = self.guion.itemTarea(row)
            if sc:
                if tarea.tp() == TabVisual.TP_SVG:
                    return

                else:
                    a1h8 = tarea.a1h8()
                    from_sq, to_sq = self.desdeHasta(tarea.txt_tipo() + " " + tarea.name(), a1h8[:2], a1h8[2:])
                    if from_sq:
                        sc = tarea.itemSC()
                        sc.ponA1H8(from_sq + to_sq)
                        self.board.refresh()

            mo = tarea.marcadoOwner()
            if mo:
                self.ponMarcadoOwner(row, mo)
            self.refresh_guion()

    def keyPressEvent(self, event):
        self.owner.keyPressEvent(event)

    def foto(self):
        gn = self.guion.name
        gi = self.guion.info
        gt = self.guion.txt_tipo
        return [(gn(f), gi(f), gt(f)) for f in range(len(self.guion))]

    def refresh_guion(self):
        self.g_guion.refresh()
        nueva = self.foto()
        nv = len(nueva)
        if self.ant_foto is None or nv != len(self.ant_foto):
            self.ant_foto = nueva
        else:
            for n in range(nv):
                if self.ant_foto[n] != nueva[n]:
                    self.ant_foto = nueva
                    break

    def grid_num_datos(self, grid):
        return len(self.guion) if self.guion else 0

    def clonaItemTarea(self, row):
        tarea = self.guion.tarea(row)
        bloqueDatos = tarea.bloqueDatos()
        tp = tarea.tp()
        if tp == TabVisual.TP_FLECHA:
            sc = self.board.creaFlecha(bloqueDatos)
        elif tp == TabVisual.TP_MARCO:
            sc = self.board.creaMarco(bloqueDatos)
        elif tp == TabVisual.TP_CIRCLE:
            sc = self.board.creaCircle(bloqueDatos)
        elif tp == TabVisual.TP_SVG:
            sc = self.board.creaSVG(bloqueDatos)
        elif tp == TabVisual.TP_MARKER:
            sc = self.board.creaMarker(bloqueDatos)
        else:
            return None
        return sc

    def ponMarcado(self, row, si_marcado):
        if self.guion:
            if row < len(self.guion.liGTareas):
                self.guion.cambiaMarcaTarea(row, si_marcado)
                item_sc = self.guion.itemTarea(row)
                self.ponMarcadoItem(row, self.board, item_sc, si_marcado)
            self.refresh_guion()

    def ponMarcadoItem(self, row, board, itemSC, siMarcado):
        if itemSC:
            itemSC.setVisible(siMarcado)

        else:
            tarea = self.guion.tarea(row)
            if isinstance(tarea, TabVisual.GT_PiezaMueve):
                from_sq, to_sq, borra = tarea.desdeHastaBorra()
                if siMarcado:
                    board.muevePieza(from_sq, to_sq)
                    board.put_arrow_sc(from_sq, to_sq)
                else:
                    board.muevePieza(to_sq, from_sq)
                    if borra:
                        board.creaPieza(borra, to_sq)
                    if board.flechaSC:
                        board.flechaSC.hide()
                board.enable_all()

            elif isinstance(tarea, TabVisual.GT_PiezaCrea):
                from_sq, pz_borrada = tarea.from_sq()
                if siMarcado:
                    board.cambiaPieza(from_sq, tarea.pieza())
                else:
                    board.borraPieza(from_sq)
                    if pz_borrada:
                        board.creaPieza(pz_borrada, from_sq)
                board.enable_all()

            elif isinstance(tarea, TabVisual.GT_PiezaBorra):
                if siMarcado:
                    board.borraPieza(tarea.from_sq())
                else:
                    board.cambiaPieza(tarea.from_sq(), tarea.pieza())
                board.enable_all()

            elif isinstance(tarea, TabVisual.GT_Texto):
                self.guion.cierraPizarra()
                if siMarcado:
                    self.guion.writePizarra(tarea)
                for recno in range(len(self.guion)):
                    tarea = self.guion.tarea(recno)
                    if tarea.tp() == TabVisual.TP_TEXTO and row != recno:
                        self.guion.cambiaMarcaTarea(recno, False)

            elif isinstance(tarea, TabVisual.GT_Action):
                if siMarcado:
                    tarea.run()
                    self.guion.cambiaMarcaTarea(row, False)

    def grid_setvalue(self, grid, row, o_column, valor):
        key = o_column.key if o_column else "MARCADO"
        if key == "MARCADO":
            self.ponMarcado(row, valor > 0)
        elif key == "NOMBRE":
            tarea = self.guion.tarea(row)
            tarea.name(valor.strip())

    def editBanda(self, cid):
        li = cid.split("_")
        tp = li[1]
        xid = li[2]
        if tp == TabVisual.TP_FLECHA:
            regFlecha = BoardTypes.Flecha(dic=self.dbFlechas[xid])
            w = WindowTabVFlechas.WTV_Flecha(self, regFlecha, True)
            if w.exec_():
                self.dbFlechas[xid] = w.regFlecha.save_dic()
        elif tp == TabVisual.TP_MARCO:
            regMarco = BoardTypes.Marco(dic=self.dbMarcos[xid])
            w = WindowTabVMarcos.WTV_Marco(self, regMarco)
            if w.exec_():
                self.dbMarcos[xid] = w.regMarco.save_dic()
        elif tp == TabVisual.TP_CIRCLE:
            reg_circle = BoardTypes.Circle(dic=self.dbCircles[xid])
            w = WindowTabVCircles.WTV_Circle(self, reg_circle)
            if w.exec_():
                self.dbCircles[xid] = w.reg_circle.save_dic()
        elif tp == TabVisual.TP_SVG:
            reg_svg = BoardTypes.SVG(dic=self.dbSVGs[xid])
            w = WindowTabVSVGs.WTV_SVG(self, reg_svg)
            if w.exec_():
                self.dbSVGs[xid] = w.regSVG.save_dic()
        elif tp == TabVisual.TP_MARKER:
            reg_marker = BoardTypes.Marker(dic=self.dbMarkers[xid])
            w = WindowTabVMarkers.WTV_Marker(self, reg_marker)
            if w.exec_():
                self.dbMarkers[xid] = w.regMarker.save_dic()

    def test_siGrabar(self):
        if self.chbSaveWhenFinished.valor():
            self.grabar()

    def closeEvent(self, event):
        self.cierraRecursos()

    def terminar(self):
        self.cierraRecursos()
        self.close()

    def cancelar(self):
        self.terminar()

    def portapapeles(self):
        self.board.save_as_img()
        txt = _("Clipboard")
        QTUtil2.temporary_message(self, _X(_("Saved to %1"), txt), 0.8)

    def grabarFichero(self):
        dirSalvados = self.configuration.save_folder()
        resp = SelectFiles.salvaFichero(self, _("File to save"), dirSalvados, "png", False)
        if resp:
            self.board.save_as_img(resp, "png")
            txt = resp
            QTUtil2.temporary_message(self, _X(_("Saved to %1"), txt), 0.8)
            direc = os.path.dirname(resp)
            if direc != dirSalvados:
                self.configuration.set_save_folder(direc)

    def flechas(self):
        w = WindowTabVFlechas.WTV_Flechas(self, self.list_arrows(), self.dbFlechas)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def list_arrows(self):
        dic = self.dbFlechas.as_dictionary()
        li = []
        for k, dicFlecha in dic.items():
            arrow = BoardTypes.Flecha(dic=dicFlecha)
            arrow.id = k
            li.append(arrow)

        li.sort(key=lambda x: x.ordenVista)
        return li

    def marcos(self):
        w = WindowTabVMarcos.WTV_Marcos(self, self.list_boxes(), self.dbMarcos)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def circles(self):
        w = WindowTabVCircles.WTV_Circles(self, self.list_circles(), self.dbCircles)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def list_boxes(self):
        dic = self.dbMarcos.as_dictionary()
        li = []
        for k, dicMarco in dic.items():
            box = BoardTypes.Marco(dic=dicMarco)
            box.id = k
            li.append(box)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def list_circles(self):
        dic = self.dbCircles.as_dictionary()
        li = []
        for k, dicCircle in dic.items():
            circle = BoardTypes.Circle(dic=dicCircle)
            circle.id = k
            li.append(circle)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def svgs(self):
        w = WindowTabVSVGs.WTV_SVGs(self, self.list_svgs(), self.dbSVGs)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def list_svgs(self):
        dic = self.dbSVGs.as_dictionary()
        li = []
        for k, dicSVG in dic.items():
            if type(dicSVG) != dict:
                continue
            svg = BoardTypes.SVG(dic=dicSVG)
            svg.id = k
            li.append(svg)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def markers(self):
        w = WindowTabVMarkers.WTV_Markers(self, self.list_markers(), self.dbMarkers)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def list_markers(self):
        dic = self.dbMarkers.as_dictionary()
        li = []
        for k, dic_marker in dic.items():
            marker = BoardTypes.Marker(dic=dic_marker)
            marker.id = k
            li.append(marker)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def leeRecursos(self):
        self.dbConfig = self.dbManager.dbConfig
        self.dbFlechas = self.dbManager.dbFlechas
        self.dbMarcos = self.dbManager.dbMarcos
        self.dbCircles = self.dbManager.dbCircles
        self.dbSVGs = self.dbManager.dbSVGs
        self.dbMarkers = self.dbManager.dbMarkers

    def cierraRecursos(self):
        if self.guion is not None:
            self.guion.cierraPizarra()
            if not self.dbConfig.is_closed():
                self.dbConfig["SELECTBANDA"] = self.selectBanda.guardar()
                self.dbConfig["SELECTBANDANUM"] = self.selectBanda.numSeleccionada()
                self.dbConfig["SAVEWHENFINISHED"] = self.chbSaveWhenFinished.valor()
            self.dbManager.close()

            self.save_video()
            self.guion.restoreBoard()
            self.test_siGrabar()
            self.guion = None

    def actualizaBandas(self):
        self.selectBanda.iniActualizacion()

        tipo = _("Arrows")
        for arrow in self.list_arrows():
            pm = QtGui.QPixmap()
            pm.loadFromData(arrow.png, "PNG")
            xid = "_F_%s" % arrow.id
            name = arrow.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Boxes")
        for box in self.list_boxes():
            pm = QtGui.QPixmap()
            pm.loadFromData(box.png, "PNG")
            xid = "_M_%s" % box.id
            name = box.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Circles")
        for circle in self.list_circles():
            pm = QtGui.QPixmap()
            pm.loadFromData(circle.png, "PNG")
            xid = "_D_%s" % circle.id
            name = circle.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Images")
        for svg in self.list_svgs():
            pm = QtGui.QPixmap()
            pm.loadFromData(svg.png, "PNG")
            xid = "_S_%s" % svg.id
            name = svg.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Markers")
        for marker in self.list_markers():
            pm = QtGui.QPixmap()
            pm.loadFromData(marker.png, "PNG")
            xid = "_X_%s" % marker.id
            name = marker.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        self.selectBanda.finActualizacion()

        dicCampos = {
            TabVisual.TP_FLECHA: (
                "name",
                "altocabeza",
                "tipo",
                "destino",
                "color",
                "colorinterior",
                "colorinterior2",
                "opacity",
                "redondeos",
                "forma",
                "ancho",
                "vuelo",
                "descuelgue",
            ),
            TabVisual.TP_MARCO: (
                "name",
                "color",
                "colorinterior",
                "colorinterior2",
                "grosor",
                "redEsquina",
                "tipo",
                "opacity",
            ),
            TabVisual.TP_CIRCLE: ("name", "color", "colorinterior", "colorinterior2", "grosor", "tipo", "opacity"),
            TabVisual.TP_SVG: ("name", "opacity"),
            TabVisual.TP_MARKER: ("name", "opacity"),
        }
        dicDB = {
            TabVisual.TP_FLECHA: self.dbFlechas,
            TabVisual.TP_MARCO: self.dbMarcos,
            TabVisual.TP_CIRCLE: self.dbCircles,
            TabVisual.TP_SVG: self.dbSVGs,
            TabVisual.TP_MARKER: self.dbMarkers,
        }
        for k, sc in self.board.dicMovibles.items():
            bd = sc.bloqueDatos
            try:
                tp, xid = bd.tpid
                bdn = dicDB[tp][xid]
                for campo in dicCampos[tp]:
                    setattr(bd, campo, getattr(bdn, campo))
                sc.update()
            except:
                pass
        self.refresh_guion()

    def muevePieza(self, from_sq, to_sq):
        self.creaTarea("P", None, from_sq + to_sq, -1)
        self.board.muevePieza(from_sq, to_sq)

    def boardPress(self, event, origin, siRight, is_shift, is_alt, is_ctrl):
        if origin:
            if not siRight:
                lb_sel = self.selectBanda.seleccionada
            else:
                if is_ctrl:
                    if is_alt:
                        pos = 4
                    elif is_shift:
                        pos = 5
                    else:
                        pos = 3
                else:
                    if is_alt:
                        pos = 1
                    elif is_shift:
                        pos = 2
                    else:
                        pos = 0
                lb_sel = self.selectBanda.get_pos(pos)
            if lb_sel:
                nada, tp, nid = lb_sel.id.split("_")
                nid = int(nid)
                if tp == TabVisual.TP_FLECHA:
                    self.siGrabarInicio = True
                self.datos_new = self.creaTarea(tp, nid, origin + origin, -1)
                self.tp_new = tp
                if tp in (TabVisual.TP_FLECHA, TabVisual.TP_MARCO):
                    self.origin_new = origin
                    sc = self.datos_new[0].itemSC()
                    sc.mousePressExt(event)
                else:
                    self.origin_new = None

    def boardMove(self, event):
        if self.origin_new:
            sc = self.datos_new[0].itemSC()
            sc.mouseMoveExt(event)

    def boardRelease(self, a1, siRight, is_shift, is_alt, is_ctrl):
        if self.origin_new:
            tarea, row = self.datos_new
            sc = tarea.itemSC()
            sc.mouseReleaseExt()
            self.g_guion.goto(row, 0)
            if siRight:
                if a1 == self.origin_new and not is_ctrl:
                    if is_shift:
                        pos = 8
                    elif is_alt:
                        pos = 7
                    else:
                        pos = 6
                    self.borrar_lista()
                    lb = self.selectBanda.get_pos(pos)
                    if not lb.id:
                        return
                    nada, tp, nid = lb.id.split("_")
                    nid = int(nid)
                    self.datos_new = self.creaTarea(tp, nid, a1 + a1, -1)
                    self.tp_new = tp
                self.refresh_guion()
                # li = self.guion.borraRepeticionUltima()
                # if li:
                #     self.borrar_lista(li)
                #     self.origin_new = None
                #     return

            else:
                if a1 is None or (a1 == self.origin_new and self.tp_new == TabVisual.TP_FLECHA):
                    self.borrar_lista()

                else:
                    self.refresh_guion()

            self.origin_new = None

    def boardRemove(self, itemSC):
        tarea, n = self.guion.tareaItem(itemSC)
        if tarea:
            self.g_guion.goto(n, 0)
            self.borrar_lista()


class Director:
    def __init__(self, board):
        self.board = board
        self.ultTareaSelect = None
        self.director = False
        self.directorItemSC = None
        self.w = WPanelDirector(self, board)
        self.w.show()
        self.guion = self.w.guion

    def show(self):
        self.w.show()

    def cambiadaPosicionAntes(self):
        self.guion.cierraPizarra()
        self.w.test_siGrabar()

    def cambiadaPosicionDespues(self):
        self.w.cambiadaPosicion()
        self.guion.saveBoard()

    def cambiadoMensajero(self):
        self.w.test_siGrabar()
        self.w.terminar()

    def muevePieza(self, from_sq, to_sq, promotion=""):
        self.w.creaTarea("P", None, from_sq + to_sq, -1)
        self.board.muevePieza(from_sq, to_sq)
        return True

    def setChange(self, ok):
        self.director = ok
        self.ultTareaSelect = None
        self.directorItemSC = None

    def keyPressEvent(self, event):
        m = int(event.modifiers())
        is_ctrl = (m & QtCore.Qt.ControlModifier) > 0
        k = event.key()
        if k == QtCore.Qt.Key_Backspace:
            self.w.borraUltimo()
            return True
        if k == QtCore.Qt.Key_Delete:
            self.w.borraTodos()
            return True
        if QtCore.Qt.Key_F1 <= k <= QtCore.Qt.Key_F10:
            f = k - QtCore.Qt.Key_F1
            self.w.funcion(f, is_ctrl)
            return True
        else:
            return False

    def mousePressEvent(self, event):
        is_right = event.button() == QtCore.Qt.RightButton
        is_left = event.button() == QtCore.Qt.LeftButton

        if is_left:
            if self.board.event2a1h8(event) is None:
                return False
            if self.director:
                QtWidgets.QGraphicsView.mousePressEvent(self.board, event)

        p = event.pos()
        a1h8 = self.punto2a1h8(p)
        m = int(event.modifiers())
        is_ctrl = (m & QtCore.Qt.ControlModifier) > 0
        is_shift = (m & QtCore.Qt.ShiftModifier) > 0
        is_alt = (m & QtCore.Qt.AltModifier) > 0

        li_tareas = self.guion.tareasPosicion(p)

        if is_right and is_shift and is_alt:
            pz_borrar = self.board.dameNomPiezaEn(a1h8)
            menu = Controles.Menu(self.board)
            dicPieces = TrListas.dic_nom_pieces()
            icoPiece = self.board.piezas.icono

            if pz_borrar or len(li_tareas):
                mrem = menu.submenu(_("Remove"), Iconos.Delete())
                if pz_borrar:
                    label = dicPieces[pz_borrar.upper()]
                    mrem.opcion(("rem_pz", None), label, icoPiece(pz_borrar))
                    mrem.separador()
                for pos_guion, tarea in li_tareas:
                    label = "%s - %s - %s" % (tarea.txt_tipo(), tarea.name(), tarea.info())
                    mrem.opcion(("rem_gr", pos_guion), label, Iconos.Delete())
                    mrem.separador()
                menu.separador()

            for pz in "KQRBNPkqrbnp":
                if pz != pz_borrar:
                    if pz == "k":
                        menu.separador()
                    menu.opcion(("create", pz), dicPieces[pz.upper()], icoPiece(pz))
            resp = menu.lanza()
            if resp is not None:
                orden, arg = resp
                if orden == "rem_gr":
                    self.w.g_guion.goto(arg, 0)
                    self.w.borrar_lista()
                elif orden == "rem_pz":
                    self.w.creaTarea("B", pz_borrar, a1h8, -1)

                elif orden == "create":
                    self.w.creaTarea("C", arg, a1h8, -1)
            return True

        if self.director:
            return self.mousePressEvent_Drop(event)

        self.w.boardPress(event, a1h8, is_right, is_shift, is_alt, is_ctrl)

        return True

    def mousePressEvent_Drop(self, event):
        p = event.pos()
        li_tareas = self.guion.tareasPosicion(p)  # (pos_guion, tarea)...
        nli_tareas = len(li_tareas)
        if nli_tareas > 0:
            if nli_tareas > 1:  # Guerra
                posic = None
                for x in range(nli_tareas):
                    if self.ultTareaSelect == li_tareas[x][1]:
                        posic = x
                        break
                if posic is None:
                    posic = 0
                else:
                    posic += 1
                    if posic >= nli_tareas:
                        posic = 0
            else:
                posic = 0

            tarea_elegida = li_tareas[posic][1]

            if self.ultTareaSelect:
                self.ultTareaSelect.itemSC().activa(False)
            self.ultTareaSelect = tarea_elegida
            itemSC = self.ultTareaSelect.itemSC()
            itemSC.activa(True)
            itemSC.mousePressExt(event)
            self.directorItemSC = itemSC

            return True
        else:
            self.ultTareaSelect = None
            return False

    def punto2a1h8(self, punto):
        xc = 1 + int(float(punto.x() - self.board.margenCentro) / self.board.width_square)
        yc = 1 + int(float(punto.y() - self.board.margenCentro) / self.board.width_square)

        if self.board.is_white_bottom:
            yc = 9 - yc
        else:
            xc = 9 - xc

        if not ((1 <= xc <= 8) and (1 <= yc <= 8)):
            return None

        f = chr(48 + yc)
        c = chr(96 + xc)
        a1h8 = c + f
        return a1h8

    def mouseMoveEvent(self, event):
        if self.director:
            if self.directorItemSC:
                self.directorItemSC.mouseMoveEvent(event)
            return False
        self.w.boardMove(event)
        return True

    def mouseReleaseEvent(self, event):
        if self.director:
            if self.directorItemSC:
                self.directorItemSC.mouseReleaseExt()
                self.directorItemSC.activa(False)
                self.directorItemSC = None
                self.w.refresh_guion()
                return True
            else:
                return False

        a1h8 = self.punto2a1h8(event.pos())
        if a1h8:
            siRight = event.button() == QtCore.Qt.RightButton
            m = int(event.modifiers())
            is_shift = (m & QtCore.Qt.ShiftModifier) > 0
            is_alt = (m & QtCore.Qt.AltModifier) > 0
            is_ctrl = (m & QtCore.Qt.ControlModifier) > 0
            self.w.boardRelease(a1h8, siRight, is_shift, is_alt, is_ctrl)
        return True

    def terminar(self):
        if self.w:
            self.w.terminar()
            self.w = None
