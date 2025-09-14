import collections

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios


class SelectUna(Controles.LB):
    def __init__(self, owner, pm_empty, add_text):
        self.owner = owner
        self.pixmap = None
        self.id = None
        self.tooltip = None
        self.seleccionada = False
        Controles.LB.__init__(self, owner)
        self.put_image(pm_empty)
        self.add_text = add_text
        self.set_style()

    def pon(self, pixmap, tooltip, xid):
        if pixmap:
            if pixmap.height() != 32:
                pixmap = pixmap.scaled(32, 32)
            self.put_image(pixmap)
        self.id = xid
        self.setToolTip(tooltip)
        self.pixmap = pixmap

    def seleccionar(self, si_seleccionada):
        if not self.add_text:
            self.seleccionada = si_seleccionada
            self.set_style()

    def set_style(self):
        color = Code.dic_colors["DIRECTOR_BANDA_BORDER_ENABLE"] if self.seleccionada else Code.dic_colors[
            "DIRECTOR_BANDA_BORDER_DISABLE"]
        self.setStyleSheet("border: 2px solid %s; padding:2px;" % color)

    def mousePressEvent(self, event):
        if self.add_text:
            self.owner.addText()
        else:
            eb = event.button()
            if self.id is None or eb == QtCore.Qt.RightButton:
                self.owner.edit(self)
            else:
                if eb == QtCore.Qt.LeftButton:
                    self.owner.seleccionar(self)


class SelectBanda(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self)

        num_elem, ancho = 10, 32
        self.owner = owner
        self.ancho = ancho
        self.seleccionada = None

        layout = Colocacion.G()
        layout.setSpacing(2)
        layout.margen(0)
        self.liLB = []
        self.liLB_F = []
        pm = Iconos.pmEnBlanco()
        if ancho != 32:
            pm = pm.scaled(ancho, ancho)
        self.pm_empty = pm
        for n in range(num_elem):
            lb_f = Controles.LB("F%d" % (n + 1,))
            lb_f.anchoFijo(32)
            lb_f.altoFijo(40)
            lb_f.align_center()
            layout.controlc(lb_f, n, 1)
            if n == 9:
                lb = SelectUna(self, Iconos.pmTexto().scaled(ancho, ancho), True)
                lb.addText = True
            else:
                lb = SelectUna(self, self.pm_empty, False)
                if n < 9:
                    lyV = Colocacion.V().relleno(1)

                    if n in (3, 4, 5):
                        lbct = Controles.LB(self).put_image(Iconos.pmControl())
                        lyV.control(lbct).espacio(-8)

                    if n in (1, 4, 7):
                        lbalt = Controles.LB(self).put_image(Iconos.pmAlt())
                        lyV.control(lbalt)
                    elif n in (2, 5, 8):
                        lbsh = Controles.LB(self).put_image(Iconos.pmShift())
                        lyV.control(lbsh)
                    elif n in (0, 6):
                        lbim = Controles.LB(self).put_image(Iconos.pmRightMouse())
                        lyV.control(lbim)

                    lyV.relleno(1).margen(0)

                    layout.otro(lyV, n, 2)

            lb_f.mousePressEvent = lb.mousePressEvent
            self.liLB.append(lb)
            self.liLB_F.append(lb_f)
            layout.controlc(lb, n, 0)
        lb_f = Controles.LB("%s F10\n%s" % (_("CTRL"), _("Changes")))
        lb_f.setToolTip(_("Shift-Alt with right button to create/remove pieces"))
        # Activa la posibilidad de mover las piezas con el ratón
        lb_f.altoFijo(36)
        lb_f.align_center()
        self.lb_change_graphics = lb_f
        lb_f.mousePressEvent = self.mousePressEventGraphics
        layout.controlc(lb_f, num_elem, 0, 1, 2)
        self.dic_data = collections.OrderedDict()
        self.setLayout(layout)

        st = "border: 2px solid %s; background-color:%s; color:%s;"
        border_enable = Code.dic_colors["DIRECTOR_BANDA_BORDER_ENABLE"]
        fore_enable = Code.dic_colors["DIRECTOR_BANDA_FOREGROUND_ENABLE"]
        back_enable = Code.dic_colors["DIRECTOR_BANDA_BACKGROUND_ENABLE"]
        border_disable = Code.dic_colors["DIRECTOR_BANDA_BORDER_DISABLE"]
        fore_disable = Code.dic_colors["DIRECTOR_BANDA_FOREGROUND_DISABLE"]
        back_disable = Code.dic_colors["DIRECTOR_BANDA_BACKGROUND_DISABLE"]

        self.style_f = {
            True: st % (border_enable, back_enable, fore_enable),
            False: st % (border_disable, back_disable, fore_disable),
        }
        lb_f.setStyleSheet(self.style_f[False])

        self.li_tipos = (
            (_("Arrows"), Iconos.Flechas(), self.owner.flechas),
            (_("Boxes"), Iconos.Marcos(), self.owner.marcos),
            (_("Circles"), Iconos.Circle(), self.owner.circles),
            (_("Images"), Iconos.SVGs(), self.owner.svgs),
            (_("Markers"), Iconos.Markers(), self.owner.markers),
        )

    def mousePressEventGraphics(self, event):
        self.seleccionar(None)

    def menu(self, lb, li_more=None):
        # Los dividimos por tipos
        dic = collections.OrderedDict()
        for xid, (nom, pm, tipo) in self.dic_data.items():
            if tipo not in dic:
                dic[tipo] = collections.OrderedDict()
            dic[tipo][xid] = (nom, pm)

        menu = QTVarios.LCMenu(self)
        dicmenu = {}
        for xid, (nom, pm, tp) in self.dic_data.items():
            if tp not in dicmenu:
                ico = Iconos.PuntoVerde()
                for txt, icot, rut in self.li_tipos:
                    if tp == txt:
                        ico = icot
                dicmenu[tp] = menu.submenu(tp, ico)
                menu.separador()
            dicmenu[tp].opcion(xid, nom, QtGui.QIcon(pm))

        menu.separador()
        if li_more:
            for txt, ico, rut in li_more:
                if isinstance(rut, list):
                    submenu = menu.submenu(txt, ico)
                    for stxt, sico, srut in rut:
                        submenu.opcion(srut, stxt, sico)
                        submenu.separador()
                else:
                    menu.opcion(rut, txt, ico)
                menu.separador()

        submenu = menu.submenu(_("Edit"), Iconos.Modificar())
        if lb and lb.id is not None:
            submenu_current = submenu.submenu(_("Current"), QtGui.QIcon(lb.pixmap))
            submenu_current.opcion(-1, _("Edit"), Iconos.Modificar())
            submenu_current.separador()
            submenu_current.opcion(-2, _("Remove"), Iconos.Delete())
            submenu.separador()

        for txt, ico, rut in self.li_tipos:
            submenu.opcion(rut, txt, ico)
            submenu.separador()

        return menu.lanza()

    def edit(self, lb):
        resp = self.menu(lb)
        if resp is not None:
            if resp == -1:
                self.owner.editBanda(lb.id)
                return
            if resp == -2:
                lb.pon(self.pm_empty, None, None)
                self.test_seleccionada()
                return
            for txt, ico, rut in self.li_tipos:
                if rut == resp:
                    rut()
                    return
            nom, pm, tp = self.dic_data[resp]
            lb.pon(pm, nom, resp)
            self.seleccionar(lb)

    def menuParaExterior(self, li_more=None):
        resp = self.menu(None, li_more)
        if resp is not None:
            for txt, ico, rut in self.li_tipos:
                if rut == resp:
                    rut()
                    return None
        return resp

    def iniActualizacion(self):
        self.setControl = set()

    def actualiza(self, xid, name, pixmap, tipo):
        self.dic_data[xid] = (name, pixmap, tipo)
        self.setControl.add(xid)

    def finActualizacion(self):
        st = set()
        for xid in self.dic_data:
            if xid not in self.setControl:
                st.add(xid)
        for xid in st:
            del self.dic_data[xid]

        for n, lb in enumerate(self.liLB):
            if lb.id is not None:
                if lb.id in st:
                    lb.pon(self.pm_empty, None, None)
                else:
                    self.pon(lb.id, n)

    def pon(self, xid, pos_en_banda):
        if pos_en_banda < len(self.liLB):
            if xid in self.dic_data:
                nom, pm, tipo = self.dic_data[xid]
                lb = self.liLB[pos_en_banda]
                lb.pon(pm, nom, xid)

    def idLB(self, num):
        if 0 <= num < len(self.liLB):
            return self.liLB[num].id
        else:
            return None

    def guardar(self):
        li = [(lb.id, n) for n, lb in enumerate(self.liLB) if lb.id is not None]
        return li

    def recuperar(self, li):
        for xid, a in li:
            self.pon(xid, a)

    def seleccionar(self, lb):
        for n in range(10):
            lbt = self.liLB[n]
            lb_f = self.liLB_F[n]
            ok = lb == lbt
            lbt.seleccionar(ok)
            lb_f.setStyleSheet(self.style_f[ok])

        self.lb_change_graphics.setStyleSheet(self.style_f[lb is None])
        self.seleccionada = lb
        self.owner.seleccionar(lb)

    def addText(self):
        self.owner.addText()

    def numSeleccionada(self):
        for n in range(10):
            lbt = self.liLB[n]
            if lbt == self.seleccionada:
                return n
        return None

    def seleccionarNum(self, num):
        lb = self.liLB[num]
        if lb.pixmap:
            self.seleccionar(lb)

    def test_seleccionada(self):
        if self.seleccionada and not self.seleccionada.id:
            self.seleccionada.seleccionar(False)
            self.seleccionada = None

    def get_pos(self, pos):
        return self.liLB[pos]


class DragUna(Controles.LB):
    def __init__(self, owner, pm_empty):
        self.owner = owner
        self.pixmap = None
        self.id = None
        self.tooltip = None
        Controles.LB.__init__(self, owner)
        self.put_image(pm_empty)

    def pon(self, pixmap, tooltip, xid):
        if pixmap:
            self.put_image(pixmap)
        self.id = xid
        self.setToolTip(tooltip)
        self.pixmap = pixmap

    def mousePressEvent(self, event):
        eb = event.button()
        if self.id is None or eb == QtCore.Qt.RightButton:

            self.owner.edit(self)

        else:
            if eb == QtCore.Qt.LeftButton:
                self.owner.startDrag(self)


class DragBanda(QtWidgets.QWidget):
    def __init__(self, owner, liElem, ancho, margen=None):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner
        self.ancho = ancho

        layout = Colocacion.G()
        self.liLB = []
        pm = Iconos.pmEnBlanco()
        if ancho != 32:
            pm = pm.scaled(ancho, ancho)
        self.pm_empty = pm
        for row, numElem in enumerate(liElem):
            for n in range(numElem):
                lb = DragUna(self, self.pm_empty)
                self.liLB.append(lb)
                layout.control(lb, row, n)
        if margen:
            layout.margen(margen)
        self.dic_data = collections.OrderedDict()
        self.setLayout(layout)

    def edit(self, lb):
        if not self.dic_data:
            return

        liTipos = (
            (_("Arrows"), Iconos.Flechas(), self.owner.flechas),
            (_("Boxes"), Iconos.Marcos(), self.owner.marcos),
            (_("Circles"), Iconos.Circle(), self.owner.circles),
            (_("Images"), Iconos.SVGs(), self.owner.svgs),
            (_("Markers"), Iconos.Markers(), self.owner.markers),
        )

        # Los dividimos por tipos
        dic = collections.OrderedDict()
        for xid, (nom, pm, tipo) in self.dic_data.items():
            if tipo not in dic:
                dic[tipo] = collections.OrderedDict()
            dic[tipo][xid] = (nom, pm)

        menu = QTVarios.LCMenu(self)
        dicmenu = {}
        for xid, (nom, pm, tp) in self.dic_data.items():
            if tp not in dicmenu:
                ico = Iconos.PuntoVerde()
                for txt, icot, rut in liTipos:
                    if tp == txt:
                        ico = icot
                dicmenu[tp] = menu.submenu(tp, ico)
                # menu.separador()
            dicmenu[tp].opcion(xid, nom, QtGui.QIcon(pm))

        menu.separador()
        submenu = menu.submenu(_("Edit"), Iconos.Modificar())
        if lb.id is not None:
            submenuCurrent = submenu.submenu(_("Current"), QtGui.QIcon(lb.pixmap))
            submenuCurrent.opcion(-1, _("Edit"), Iconos.Modificar())
            submenuCurrent.separador()
            submenuCurrent.opcion(-2, _("Remove"), Iconos.Delete())
            submenu.separador()

        for txt, ico, rut in liTipos:
            submenu.opcion(rut, txt, ico)
            submenu.separador()

        resp = menu.lanza()
        if resp is not None:
            if resp == -1:
                self.owner.editBanda(lb.id)
                return
            if resp == -2:
                lb.pon(self.pm_empty, None, None)
                return
            for txt, ico, rut in liTipos:
                if rut == resp:
                    rut()
                    return
            nom, pm, tp = self.dic_data[resp]
            lb.pon(pm, nom, resp)

    def menuParaExterior(self, masOpciones):
        if not self.dic_data:
            return None

        # Los dividimos por tipos
        dic = collections.OrderedDict()
        for xid, (nom, pm, tipo) in self.dic_data.items():
            if tipo not in dic:
                dic[tipo] = collections.OrderedDict()
            dic[tipo][xid] = (nom, pm)

        menu = QTVarios.LCMenu(self)
        dicmenu = {}
        for xid, (nom, pm, tp) in self.dic_data.items():
            if tp not in dicmenu:
                dicmenu[tp] = menu.submenu(tp, Iconos.PuntoVerde())
                menu.separador()
            dicmenu[tp].opcion((xid, tp), nom, QtGui.QIcon(pm))
        for key, name, icono in masOpciones:
            menu.separador()
            menu.opcion(key, name, icono)

        resp = menu.lanza()

        return resp

    def iniActualizacion(self):
        self.setControl = set()

    def actualiza(self, xid, name, pixmap, tipo):
        self.dic_data[xid] = (name, pixmap, tipo)
        self.setControl.add(xid)

    def finActualizacion(self):
        st = set()
        for xid in self.dic_data:
            if xid not in self.setControl:
                st.add(xid)
        for xid in st:
            del self.dic_data[xid]

        for n, lb in enumerate(self.liLB):
            if lb.id is not None:
                if lb.id in st:
                    lb.pon(self.pm_empty, None, None)
                else:
                    self.pon(lb.id, n)

    def pon(self, xid, a):
        if a < len(self.liLB):
            if xid in self.dic_data:
                nom, pm, tipo = self.dic_data[xid]
                lb = self.liLB[a]
                lb.pon(pm, nom, xid)

    def idLB(self, num):
        if 0 <= num < len(self.liLB):
            return self.liLB[num].id
        else:
            return None

    def guardar(self):
        li = [(lb.id, n) for n, lb in enumerate(self.liLB) if lb.id is not None]
        return li

    def recuperar(self, li):
        for xid, a in li:
            self.pon(xid, a)

    def startDrag(self, lb):
        pixmap = lb.pixmap
        dato = lb.id
        itemData = QtCore.QByteArray(str(dato))

        mimeData = QtCore.QMimeData()
        mimeData.setData("image/x-lc-dato", itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2))
        drag.setPixmap(pixmap)

        drag.exec_(QtCore.Qt.MoveAction)
