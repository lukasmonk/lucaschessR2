import os

from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code import Util
from Code.Base import Move, Game
from Code.Base.Constantes import WHITE, BLACK
from Code.Openings import OpeningLines
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class LabelTreeDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self):
        self.with_figurines = Code.configuration.x_pgn_withfigurines
        QtWidgets.QStyledItemDelegate.__init__(self, None)
        self.font = Controles.FontType(Code.font_mono, puntos=Code.configuration.x_pgn_fontpoints)

    def paint(self, painter, option, index):
        txt = index.model().data(index, QtCore.Qt.DisplayRole)
        is_white = txt[0].isdigit()

        li = txt.split(" ")
        if is_white:
            number, pgn = li[0].split(".")
            number += "."
        else:
            number = ""
            pgn = li[0]
        resto = " ".join(li[1:]) if len(li) > 1 else ""

        ini_pz = None
        fin_pz = None
        salto_fin_pz = 0
        if self.with_figurines:
            if pgn[0] in "QBKRN":
                ini_pz = pgn[0] if is_white else pgn[0].lower()
                pgn = pgn[1:]
            elif pgn[-1] in "QBRN":
                fin_pz = pgn[-1] if is_white else pgn[-1].lower()
                pgn = pgn[:-1]
            elif pgn[-2] in "QBRN":
                fin_pz = pgn[-2] if is_white else pgn[-2].lower()
                pgn = pgn[:-2]
                salto_fin_pz = -6

        rect = option.rect
        x = rect.x()
        y = rect.y()

        painter.save()
        pen = painter.pen()
        pen.setWidth(1)
        painter.setPen(pen)
        ny = y + rect.height() - 2
        painter.drawLine(x, ny, rect.width() + x, ny)
        painter.restore()

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, Code.dic_qcolors["PGN_SELBACKGROUND"])
            color = Code.dic_colors["PGN_SELFOREGROUND"]
        else:
            color = Code.dic_colors["FOREGROUND"]

        if number:
            document = QtGui.QTextDocument()
            document.setDefaultFont(self.font)
            if color:
                number = '<font color="%s">%s</font>' % (color, number)
            document.setHtml(number)
            painter.save()
            painter.translate(x, y)
            document.drawContents(painter)
            painter.restore()
            x += document.idealWidth() - 5

        document_pgn = QtGui.QTextDocument()
        document_pgn.setDefaultFont(self.font)
        if color:
            pgn = '<font color="%s">%s</font>' % (color, pgn)
        document_pgn.setHtml(pgn)
        w_pgn = document_pgn.idealWidth()
        h_pgn = document_pgn.size().height()
        hx = h_pgn * 80 / 100
        wpz = int(hx * 0.8)

        ancho = w_pgn
        if ini_pz:
            ancho += wpz
        if fin_pz:
            ancho += wpz + salto_fin_pz

        if ini_pz:
            painter.save()
            painter.translate(x, y + 1)
            pm = Delegados.dicPZ[ini_pz]
            pm_rect = QtCore.QRectF(0, 0, hx, hx)
            pm.render(painter, pm_rect)
            painter.restore()
            x += wpz

        painter.save()
        painter.translate(x, y)
        document_pgn.drawContents(painter)
        painter.restore()

        if fin_pz:
            painter.save()
            painter.translate(x - 0.3 * wpz, y + 1)
            pm = Delegados.dicPZ[fin_pz]
            pm_rect = QtCore.QRectF(0, 0, hx, hx)
            pm.render(painter, pm_rect)
            painter.restore()
            x += wpz + salto_fin_pz

        x = rect.x() + Code.configuration.x_pgn_fontpoints * 7
        if resto:
            document_resto = QtGui.QTextDocument()
            document_resto.setDefaultFont(self.font)
            if color:
                resto = '<font color="%s">%s</font>' % (color, resto)
            document_resto.setHtml(resto)
            painter.save()
            painter.translate(x, y)
            document_resto.drawContents(painter)
            painter.restore()


class TreeMoves(QtWidgets.QTreeWidget):
    def __init__(self, owner):
        QtWidgets.QTreeWidget.__init__(self, owner)
        self.owner = owner

    def mousePressEvent(self, event):
        QtWidgets.QTreeWidget.mousePressEvent(self, event)
        self.resizeColumnToContents(0)
        self.owner.seleccionado()


class TabTree(QtWidgets.QWidget):
    def __init__(self, tabs_analisis, configuration):
        QtWidgets.QWidget.__init__(self)

        self.tabsAnalisis = tabs_analisis

        self.wlines = tabs_analisis.wlines
        self.tree = TreeMoves(self)

        self.tree_data = None

        self.tree.setAlternatingRowColors(True)

        self.tree.setUniformRowHeights(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.menu_context)
        self.tree.setStyleSheet(
            """
            QTreeView {
                font-family: %s;
                font-size: %d;
            }

            QTreeView::item {
                padding: 3px;
                margin-left:  -5px;
                border:  1px solid lightgray;
            }

            QTreeView::item:selected {
                background-color: #F1D369;
                color: #000000;
                padding: 1px;
            }
            """ % (Code.font_mono, Code.configuration.x_pgn_fontpoints)
        )

        self.tree.setFont(Controles.FontType(Code.font_mono, puntos=configuration.x_pgn_fontpoints))
        self.tree.setHeaderLabels((_("Moves"),))

        if Code.configuration.x_pgn_withfigurines:
            self.tree.setItemDelegate(LabelTreeDelegate())

        bt_act = Controles.PB(self, _("Update"), self.bt_update, plano=False).ponIcono(Iconos.Actualiza(), 16)
        bt_act.relative_width(QTUtil.get_width_text(bt_act, " " + _("Update")) + 50)

        gamebase = self.tabsAnalisis.dbop.getgamebase()
        if Code.configuration.x_pgn_withfigurines:
            d = Move.dicHTMLFigs
            lc = []
            white = True
            for c in gamebase.pgn_base_raw():
                if c == " ":
                    white = not white
                else:
                    if c.isupper() and c != "O":
                        c = d[c if white else c.lower()]
                lc.append(c)
            pgn = "".join(lc)
        else:
            translated = Code.configuration.x_translator != "en" and not Code.configuration.x_pgn_english
            pgn = gamebase.pgn_base_raw(translated=translated)

        self.pgn_initial = pgn
        self.lb_analisis = Controles.LB(self, self.pgn_initial)
        self.lb_analisis.set_font_type(puntos=configuration.x_pgn_fontpoints).set_wrap()
        Code.configuration.set_property(self.lb_analisis, "pgn")
        ly_act = Colocacion.H().control(bt_act).control(self.lb_analisis)

        layout = Colocacion.V().otro(ly_act).control(self.tree)
        self.setLayout(layout)

        self.dicItems = {}

    def seleccionado(self):
        item = self.tree.currentItem()
        if item:
            data_item = self.dicItems[str(item)]
            self.lb_analisis.set_text(data_item.game_figurines())
            lipv = data_item.list_pv()
            li_moves_childs = [xchild.move for xchild in data_item.dicHijos.values()]
            self.tabsAnalisis.wlines.goto_next_lipv(lipv, li_moves_childs)

    def bt_update(self):
        self.wlines.active_tb(False)
        with QTUtil2.OneMomentPlease(self, with_cancel=True) as um:
            self.tree.clear()

            dbop = self.tabsAnalisis.dbop
            levelbase = len(dbop.basePV.split(" "))

            def haz(trdata, iparent, nivel):
                if um.is_canceled():
                    return False
                for xmove, xhijo in trdata.dicHijos.items():
                    if um.is_canceled():
                        return False
                    item = QtWidgets.QTreeWidgetItem(iparent)
                    txt = xhijo.pgn + " " * (8 - len(xhijo.pgn)) + f"{max(xhijo.elements, 1):2d}"
                    if xhijo.opening:
                        txt += f"  {xhijo.opening}"
                    item.setText(0, txt)
                    xhijo.item = item
                    self.dicItems[str(item)] = xhijo
                    if not haz(xhijo, item, nivel + 1):
                        return False
                return True

            self.tree_data = self.tabsAnalisis.dbop.totree(um)

            tr = self.tree_data
            if dbop.basePV:
                for pos in range(levelbase):
                    for move, hijo in tr.dicHijos.items():
                        tr = hijo

            haz(tr, self.tree, 1)

            self.lb_analisis.set_text(self.pgn_initial)
        self.wlines.active_tb(True)

    def start(self):
        if len(self.dicItems) == 0:
            self.bt_update()

    def stop(self):
        pass

    def setData(self, data, pv):
        pass

    def menu_context(self, position):
        item = self.tree.currentItem()
        if not item:
            return

        menu = QTVarios.LCMenu(self)

        menu1 = menu.submenu(_("Expand"), Iconos.Mas22())
        menu1.opcion("expandall", _("All"), Iconos.PuntoVerde())
        menu1.separador()
        menu1.opcion("expandthis", _("This branch"), Iconos.PuntoAmarillo())
        menu.separador()
        menu1 = menu.submenu(_("Collapse"), Iconos.Menos22())
        menu1.opcion("collapseall", _("All"), Iconos.PuntoVerde())
        menu1.separador()
        menu1.opcion("collapsethis", _("This branch"), Iconos.PuntoAmarillo())

        menu.separador()
        menu1 = menu.submenu(_("Next position with more than one alternative"), Iconos.GoToNext())
        menu1.opcion("next>1_white", _("White"), Iconos.Blancas())
        menu1.separador()
        menu1.opcion("next>1_black", _("Black"), Iconos.Negras())

        menu.separador()
        menu.opcion("create", _("Create a new opening line from this branch"), Iconos.OpeningLines())

        menu.separador()
        menu.opcion("remove", _("Remove this branch"), Iconos.Delete())
        menu.separador()

        menu.opcion("analysis", _("Analysis"), Iconos.Analisis())
        resp = menu.lanza()
        if not resp:
            return
        if resp == "next>1_white":
            self.goto_next(item, WHITE)
            return
        if resp == "next>1_black":
            self.goto_next(item, BLACK)
            return
        if resp == "remove":
            self.remove_branch(item)
            return
        if resp.startswith("delbranches"):
            self.delbranches_num(item, "white" in resp)
            return
        if resp == "create":
            self.create_from_branch(item)
            return
        if resp == "analysis":
            self.tabsAnalisis.panelOpening.grid_doble_click(None, None, None)
            return

        quien = si_expand = None
        if resp == "expandthis":
            quien, si_expand = item, True

        elif resp == "expandall":
            quien, si_expand = None, True

        elif resp == "collapsethis":
            quien, si_expand = item, False

        elif resp == "collapseall":
            quien, si_expand = None, False

        with QTUtil2.OneMomentPlease(self.parent().parent().parent(), with_cancel=True) as um:

            def work(xdata):
                if um.is_canceled():
                    return False
                xitem = xdata.item
                if xitem:
                    xitem.setExpanded(si_expand)

                for uno, datauno in xdata.dicHijos.items():
                    if not work(datauno):
                        return False
                return True

            data = self.dicItems[str(quien)] if quien else self.tree_data
            work(data)

    def goto_next(self, item: QtWidgets.QTreeWidgetItem, side):
        def work(xdata: OpeningLines.ItemTree):
            if xdata.side_resp == side:
                if len(xdata.dicHijos) > 1:
                    return xdata

            for xdatauno in xdata.dicHijos.values():
                resp = work(xdatauno)
                if resp:
                    return resp

            return None

        def show_data(xfound):
            xitem = xfound.item
            xitem.setExpanded(True)
            self.tree.setCurrentItem(xitem)
            self.tree.show()
            QTUtil.refresh_gui()
            self.tree.setFocus()
            self.seleccionado()

        data_active = self.dicItems[str(item)] if item else self.tree_data

        while data_active:
            for datauno in data_active.dicHijos.values():
                found = work(datauno)
                if found:
                    show_data(found)
                    return
            # vamos al siguiente hermano ... hermano de padre ....
            data_active = data_active.next_in_parent()

        QTUtil2.message(self, _("Ended"))

    def create_from_branch(self, item: QtWidgets.QTreeWidgetItem):
        data_item = self.dicItems[str(item)]
        lipv = data_item.list_pv()
        a1h8 = " ".join(lipv)
        pgn = data_item.game_translated()

        name = QTUtil2.read_simple(self, _("Create a new opening line from this branch"), _("Name"), value=pgn,
                                   width=480, in_cursor=True)
        if not name:
            return

        filename = Util.valid_filename(name)
        if filename.endswith(".opk"):
            filename = filename[:-4]
        list_openings = OpeningLines.ListaOpenings()
        path_opening = Util.opj(list_openings.folder, filename + ".opk")
        if os.path.isfile(path_opening):
            QTUtil2.message_error(self, "%s\n%s" % (_("This file already exists"), filename + ".opk"))
            return
        with QTUtil2.OneMomentPlease(self):
            dbop_current: OpeningLines.Opening = self.tabsAnalisis.dbop
            dbop_new = OpeningLines.Opening(path_opening)
            game = Game.pv_game(None, a1h8)
            dbop_new.import_other(dbop_current.path_file, game)
            dbop_new.close()
            list_openings.new(filename + ".opk", a1h8, name, lines=len(dbop_new))
        QTUtil2.message_bold(self, _("Created") + ": " + name)

    def remove_branch(self, item: QtWidgets.QTreeWidgetItem):
        data_item = self.dicItems[str(item)]
        lipv = data_item.list_pv()
        a1h8 = " ".join(lipv)
        pgn = data_item.game_translated()
        if not self.tabsAnalisis.panelOpening.remove_pv(pgn, a1h8):
            return

        parent = item.parent()
        if parent is None:
            index = self.tree.indexOfTopLevelItem(item)
            if index != -1:
                self.tree.takeTopLevelItem(index)
            return

        parent.removeChild(item)
        del self.dicItems[str(item)]

        num_hijos = parent.childCount()
        while num_hijos == 0:
            parent_parent = parent.parent()
            if parent_parent is None:
                index = self.tree.indexOfTopLevelItem(parent)
                if index != -1:
                    self.tree.takeTopLevelItem(index)
                    del self.dicItems[str(parent)]
                break
            parent_parent.removeChild(parent)
            del self.dicItems[str(parent)]
            parent = parent_parent
            num_hijos = parent.childCount()
