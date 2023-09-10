import os

from PySide2 import QtCore, QtGui, QtWidgets, QtSvg

import Code
from Code import Util
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2


class BlancasNegras(QtWidgets.QDialog):
    def __init__(self, parent):
        super(BlancasNegras, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        icoP = Code.all_pieces.default_icon("K")
        icop = Code.all_pieces.default_icon("k")
        self.setWindowTitle(_("Choose a color"))
        self.setWindowIcon(icoP)

        btBlancas = Controles.PB(self, "", rutina=self.accept, plano=False).ponIcono(icoP, icon_size=64)
        btNegras = Controles.PB(self, "", rutina=self.negras, plano=False).ponIcono(icop, icon_size=64)

        self.resultado = True

        ly = Colocacion.H().control(btBlancas).control(btNegras)
        ly.margen(10)
        self.setLayout(ly)

    def negras(self):
        self.resultado = False
        self.accept()


def blancasNegras(owner):
    w = BlancasNegras(owner)
    if w.exec_():
        return w.resultado
    return None


class BlancasNegrasTiempo(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        icoP = Code.all_pieces.default_icon("K")
        icop = Code.all_pieces.default_icon("k")
        self.setWindowTitle(_("Choose a color"))
        self.setWindowIcon(icoP)
        self.key_saved = "BLANCASNEGRASTIEMPO"

        btBlancas = Controles.PB(self, "", rutina=self.blancas, plano=False).ponIcono(icoP, icon_size=64)
        btNegras = Controles.PB(self, "", rutina=self.negras, plano=False).ponIcono(icop, icon_size=64)

        # Tiempo
        self.edMinutos, self.lbMinutos = QTUtil2.spinbox_lb(self, 10, 0, 999, max_width=50, etiqueta=_("Total minutes"))
        self.edSegundos, self.lbSegundos = QTUtil2.spinbox_lb(
            self, 0, 0, 999, max_width=50, etiqueta=_("Seconds added per move")
        )
        ly = Colocacion.G()
        ly.controld(self.lbMinutos, 0, 0).control(self.edMinutos, 0, 1)
        ly.controld(self.lbSegundos, 0, 2).control(self.edSegundos, 0, 3)
        self.gbT = Controles.GB(self, _("Time"), ly).to_connect(self.change_time)

        self.chb_fastmoves = Controles.CHB(self, _("Fast moves"), False)

        self.color = None

        ly = Colocacion.H().control(btBlancas).control(btNegras)
        ly.margen(10)
        layout = Colocacion.V().otro(ly).espacio(10).control(self.gbT).control(self.chb_fastmoves).margen(5)
        self.setLayout(layout)

        self.read_saved()

    def read_saved(self):
        dic = Code.configuration.read_variables(self.key_saved)
        with_time = dic.get("WITH_TIME", False)
        minutes = dic.get("MINUTES", 10)
        seconds = dic.get("SECONDS", 0)
        fast_moves = dic.get("FAST_MOVES", False)
        self.gbT.setChecked(with_time)
        if with_time:
            self.edMinutos.set_value(minutes)
            self.edSegundos.set_value(seconds)
        self.chb_fastmoves.set_value(fast_moves)
        self.muestra_tiempo(with_time)

    def save(self):
        dic = {
            "WITH_TIME": self.gbT.isChecked(),
            "MINUTES": self.edMinutos.valor(),
            "SECONDS": self.edSegundos.valor(),
            "FAST_MOVES": self.chb_fastmoves.valor(),
        }
        Code.configuration.write_variables(self.key_saved, dic)

    def resultado(self):
        return (
            self.color,
            self.gbT.isChecked(),
            self.edMinutos.valor(),
            self.edSegundos.valor(),
            self.chb_fastmoves.valor(),
        )

    def change_time(self):
        self.muestra_tiempo(self.gbT.isChecked())

    def muestra_tiempo(self, si):
        for control in (self.edMinutos, self.lbMinutos, self.edSegundos, self.lbSegundos):
            control.setVisible(si)

    def blancas(self):
        self.color = True
        self.save()
        self.accept()

    def negras(self):
        self.color = False
        self.save()
        self.accept()


def blancasNegrasTiempo(owner):
    w = BlancasNegrasTiempo(owner)
    if w.exec_():
        return w.resultado()
    return None


class Tiempo(QtWidgets.QDialog):
    def __init__(self, parent, minMinutos, minSegundos, maxMinutos, max_seconds, default_minutes=10, default_seconds=0):
        super(Tiempo, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.setWindowTitle(_("Time"))
        self.setWindowIcon(Iconos.MoverTiempo())

        tb = tb_accept_cancel(self)

        f = Controles.TipoLetra(puntos=11)

        # Tiempo
        self.edMinutos, self.lbMinutos = QTUtil2.spinbox_lb(
            self, default_minutes, minMinutos, maxMinutos, max_width=50, etiqueta=_("Total minutes"), fuente=f
        )
        self.edSegundos, self.lbSegundos = QTUtil2.spinbox_lb(
            self, default_seconds, minSegundos, max_seconds, max_width=50, etiqueta=_("Seconds added per move"), fuente=f
        )

        # # Tiempo
        lyT = Colocacion.G()
        lyT.controld(self.lbMinutos, 0, 0).control(self.edMinutos, 0, 1)
        lyT.controld(self.lbSegundos, 1, 0).control(self.edSegundos, 1, 1).margen(20)

        ly = Colocacion.V().control(tb).espacio(20).otro(lyT)
        self.setLayout(ly)

    def aceptar(self):
        self.accept()

    def resultado(self):
        minutos = self.edMinutos.value()
        seconds = self.edSegundos.value()

        return minutos, seconds


def vtime(owner, minMinutos=1, minSegundos=0, maxMinutos=999, max_seconds=999, default_minutes=10, default_seconds=0):
    w = Tiempo(
        owner,
        minMinutos,
        minSegundos,
        maxMinutos,
        max_seconds,
        default_minutes=default_minutes,
        default_seconds=default_seconds,
    )
    if w.exec_():
        return w.resultado()
    return None


def ly_mini_buttons(
        owner,
        key,
        siLibre=True,
        siMas=False,
        siTiempo=True,
        must_save=False,
        siGrabarTodos=False,
        siJugar=False,
        rutina=None,
        icon_size=16,
        liMasAcciones=None,
):
    li_acciones = []

    def x(tit, tr, icono):
        li_acciones.append((tr, icono, key + tit))

    li_acciones.append(None)
    x("MoverInicio", _("Start position"), Iconos.MoverInicio())
    li_acciones.append(None)
    x("MoverAtras", _("Previous move"), Iconos.MoverAtras())
    li_acciones.append(None)
    x("MoverAdelante", _("Next move"), Iconos.MoverAdelante())
    li_acciones.append(None)
    x("MoverFinal", _("Last move"), Iconos.MoverFinal())
    li_acciones.append(None)
    if siLibre:
        x("MoverLibre", _("Analysis of variation"), Iconos.MoverLibre())
        li_acciones.append(None)
    if siJugar:
        x("MoverJugar", _("Play"), Iconos.MoverJugar())
        li_acciones.append(None)
    if siTiempo:
        x("MoverTiempo", _("Timed movement") + "\n%s" % _("Right click to change the interval"), Iconos.Pelicula16())
    li_acciones.append(None)
    if must_save:
        x("MoverGrabar", _("Save"), Iconos.MoverGrabar())
        li_acciones.append(None)
    if siGrabarTodos:
        li_acciones.append((_("Save") + "++", Iconos.MoverGrabarTodos(), key + "MoverGrabarTodos"))
        li_acciones.append(None)
    if siMas:
        x("MoverMas", _("New analysis"), Iconos.MoverMas())
        li_acciones.append(None)

    if liMasAcciones:
        for trad, tit, icono in liMasAcciones:
            li_acciones.append((trad, icono, key + tit))
            li_acciones.append(None)

    tb = Controles.TB(owner, li_acciones, False, icon_size=icon_size, rutina=rutina)
    tb.setMinimumHeight(icon_size + 4)
    ly = Colocacion.H().relleno().control(tb).relleno()
    return ly, tb


class LCNumero(QtWidgets.QWidget):
    def __init__(self, maxdigits):
        QtWidgets.QWidget.__init__(self)

        f = Controles.TipoLetra("", 11, 80, False, False, False, None)

        ly = Colocacion.H()
        self.liLB = []
        for x in range(maxdigits):
            lb = QtWidgets.QLabel(self)
            lb.setStyleSheet("* { border: 2px solid black; padding: 2px; margin: 0px;}")
            lb.setFont(f)
            ly.control(lb)
            self.liLB.append(lb)
            lb.hide()
            lb.setFixedWidth(32)
            lb.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(ly)

    def pon(self, number):
        c = str(number)
        n = len(c)
        for x in range(n):
            lb = self.liLB[x]
            lb.setText(c[x])
            lb.show()
        for x in range(n, len(self.liLB)):
            self.liLB[x].hide()


class TwoImages(QtWidgets.QLabel):
    def __init__(self, pmTrue, pmFalse):
        self.pm = {True: pmTrue, False: pmFalse}
        self.pmFalse = pmFalse
        QtWidgets.QLabel.__init__(self)
        self.valor(False)

    def valor(self, ok=None):
        if ok is None:
            return self._valor
        else:
            self._valor = ok
            self.setPixmap(self.pm[ok])

    def mousePressEvent(self, event):
        self.valor(not self._valor)


def svg2ico(svg, tam):
    pm = QtGui.QPixmap(tam, tam)
    pm.fill(QtCore.Qt.transparent)
    qb = QtCore.QByteArray(svg)
    render = QtSvg.QSvgRenderer(qb)
    painter = QtGui.QPainter()
    painter.begin(pm)
    render.render(painter)
    painter.end()
    ico = QtGui.QIcon(pm)
    return ico


def fsvg2ico(fsvg, tam):
    with open(fsvg, "rb") as f:
        svg = f.read()
        return svg2ico(svg, tam)


def svg2pm(svg, tam):
    pm = QtGui.QPixmap(tam, tam)
    pm.fill(QtCore.Qt.transparent)
    qb = QtCore.QByteArray(svg)
    render = QtSvg.QSvgRenderer(qb)
    painter = QtGui.QPainter()
    painter.begin(pm)
    render.render(painter)
    painter.end()
    return pm


def fsvg2pm(fsvg, tam):
    with open(fsvg, "rb") as f:
        svg = f.read()
        return svg2pm(svg, tam)


class LBPieza(Controles.LB):
    def __init__(self, owner, pieza, board, tam):
        self.pieza = pieza
        self.owner = owner
        pixmap = board.piezas.pixmap(pieza, tam=tam)
        self.dragpixmap = pixmap
        Controles.LB.__init__(self, owner)
        self.ponImagen(pixmap).anchoFijo(tam).altoFijo(tam)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.owner.startDrag(self)


class ListaPiezas(QtWidgets.QWidget):
    def __init__(self, owner, lista, board, tam=None, margen=None):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner
        # self.board = board = owner.board

        if tam is None:
            tam = board.anchoPieza

        liLB = []
        for row, valor in enumerate(lista.split(";")):
            for column, pieza in enumerate(valor.split(",")):
                lb = LBPieza(self, pieza, board, tam)
                liLB.append((lb, row, column))

        layout = Colocacion.G()
        for lb, row, column in liLB:
            layout.control(lb, row, column)
        if margen is not None:
            layout.margen(margen)

            # l1 = Colocacion.H().otro(layout).relleno()
            # if margen:
            # l1.margen(margen)
            # l2 = Colocacion.V().otro(l1)
            # if margen:
            # l2.margen(margen)

        self.setLayout(layout)

    def startDrag(self, lb):

        pixmap = lb.dragpixmap
        pieza = lb.pieza
        itemData = QtCore.QByteArray(pieza.encode("utf-8"))

        self.owner.ultimaPieza = pieza
        self.owner.ponCursor()

        mimeData = QtCore.QMimeData()
        mimeData.setData("image/x-lc-dato", itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() // 2, pixmap.height() // 2))
        drag.setPixmap(pixmap)

        drag.exec_(QtCore.Qt.MoveAction)


def rondoPuntos(shuffle=True):
    nico = Util.Rondo(
        Iconos.PuntoAmarillo(),
        Iconos.PuntoNaranja(),
        Iconos.PuntoVerde(),
        Iconos.PuntoAzul(),
        Iconos.PuntoMagenta(),
        Iconos.PuntoRojo(),
    )
    if shuffle:
        nico.shuffle()
    return nico


def rondoColores(shuffle=True):
    nico = Util.Rondo(
        Iconos.Amarillo(), Iconos.Naranja(), Iconos.Verde(), Iconos.Azul(), Iconos.Magenta(), Iconos.Rojo()
    )
    if shuffle:
        nico.shuffle()
    return nico


def rondoFolders(shuffle=True):
    nico = Util.Rondo(
        Iconos.FolderAnil(),
        Iconos.FolderBlack(),
        Iconos.FolderBlue(),
        Iconos.FolderGreen(),
        Iconos.FolderMagenta(),
        Iconos.FolderRed(),
    )
    if shuffle:
        nico.shuffle()
    return nico


class LCMenu(Controles.Menu):
    def __init__(self, parent, puntos=None):
        configuration = Code.configuration
        if not puntos:
            puntos = configuration.x_menu_points
        bold = configuration.x_menu_bold
        Controles.Menu.__init__(self, parent, puntos=puntos, siBold=bold)

    def opcion(self, key, label, icono=None, is_disabled=False, tipoLetra=None, siChecked=False, toolTip: str = ""):
        if icono is None:
            icono = Iconos.Empty()

        Controles.Menu.opcion(self, key, label, icono, is_disabled, tipoLetra, siChecked, toolTip)

    def separador_blank(self):
        self.opcion(None, "")


class LCMenuRondo(LCMenu):
    def __init__(self, parent, puntos=None):
        LCMenu.__init__(self, parent, puntos)
        self.rondo = rondoPuntos()

    def opcion(self, key, label, icono=None, is_disabled=False, tipoLetra=None, siChecked=None, toolTip: str = ""):
        if icono is None:
            icono = self.rondo.otro()
        LCMenu.opcion(self, key, label, icono, is_disabled, tipoLetra, siChecked, toolTip)

    # def submenu(self, label, icono=None, is_disabled=False):
    #     if icono is None:
    #         icono = self.rondo.otro()
    #     return LCMenu.submenu(self, label, icono, is_disabled)
    #


class LCMenuPiezas(Controles.Menu):
    def __init__(self, parent, titulo=None, icono=None, is_disabled=False, puntos=None, siBold=True):
        Controles.Menu.__init__(self, parent, titulo, icono, is_disabled, puntos, siBold)
        self.ponTipoLetra("Chess Alpha 2", 16)

    def opcion(self, key, label, icono=None, is_disabled=False, tipo_letra=None, siChecked=False):
        Controles.Menu.opcion(self, key, label, icono=icono, is_disabled=is_disabled, siChecked=siChecked)

    def submenu(self, label, icono=None, is_disabled=False):
        menu = LCMenuPiezas(self, label, icono, is_disabled)
        self.addMenu(menu)
        return menu


class ImportarFichero(QtWidgets.QDialog):
    def __init__(self, parent, titulo, siErroneos, siWorkDone, icono):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.setWindowTitle(titulo)
        self.setWindowIcon(icono)
        self.fontB = f = Controles.TipoLetra(puntos=10, peso=75)

        self.siErroneos = siErroneos
        self.siWorkDone = siWorkDone

        self.is_canceled = False

        lbRotLeidos = Controles.LB(self, _("Games read") + ":").ponFuente(f)
        self.lbLeidos = Controles.LB(self, "0").ponFuente(f)

        if siErroneos:
            lbRotErroneos = Controles.LB(self, _("Erroneous") + ":").ponFuente(f)
            self.lbErroneos = Controles.LB(self, "0").ponFuente(f)
        else:
            lbRotErroneos = None

        self.lbRotDuplicados = lbRotDuplicados = Controles.LB(self, _("Duplicated") + ":").ponFuente(f)
        self.lbDuplicados = Controles.LB(self, "0").ponFuente(f)

        self.lbRotImportados = lbRotImportados = Controles.LB(self, _("Imported") + ":").ponFuente(f)
        self.lbImportados = Controles.LB(self, "0").ponFuente(f)

        if self.siWorkDone:
            lbRotWorkDone = Controles.LB(self, _("Work done") + ":").ponFuente(f)
            self.lbWorkDone = Controles.LB(self, "0.00%").ponFuente(f)
        else:
            lbRotWorkDone = None

        self.btCancelarSeguir = Controles.PB(self, _("Cancel"), self.cancelar, plano=False).ponIcono(Iconos.Delete())

        ly = Colocacion.G().margen(20)
        ly.controld(lbRotLeidos, 0, 0).controld(self.lbLeidos, 0, 1)
        if siErroneos:
            ly.controld(lbRotErroneos, 1, 0).controld(self.lbErroneos, 1, 1)
        ly.controld(lbRotDuplicados, 2, 0).controld(self.lbDuplicados, 2, 1)
        ly.controld(lbRotImportados, 3, 0).controld(self.lbImportados, 3, 1)
        if self.siWorkDone:
            ly.controld(lbRotWorkDone, 4, 0).controld(self.lbWorkDone, 4, 1)

        lyBT = Colocacion.H().relleno().control(self.btCancelarSeguir)

        layout = Colocacion.V()
        layout.otro(ly)
        layout.espacio(20)
        layout.otro(lyBT)

        self.setLayout(layout)

    def pon_titulo(self, titulo):
        self.setWindowTitle(titulo)

    def hide_duplicates(self):
        self.lbRotDuplicados.hide()
        self.lbDuplicados.hide()

    def cancelar(self):
        self.is_canceled = True
        self.ponContinuar()

    def ponExportados(self):
        self.lbRotImportados.set_text(_("Exported") + ":")

    def ponSaving(self):
        self.btCancelarSeguir.setDisabled(True)
        self.btCancelarSeguir.set_text(_("Saving..."))
        self.btCancelarSeguir.ponFuente(self.fontB)
        self.btCancelarSeguir.ponIcono(Iconos.Grabar())
        QTUtil.refresh_gui()

    def ponContinuar(self):
        self.btCancelarSeguir.set_text(_("Continue"))
        self.btCancelarSeguir.to_connect(self.continuar)
        self.btCancelarSeguir.ponFuente(self.fontB)
        self.btCancelarSeguir.ponIcono(Iconos.Aceptar())
        self.btCancelarSeguir.setDisabled(False)
        QTUtil.refresh_gui()

    def continuar(self):
        self.accept()

    def actualiza(self, leidos, erroneos, duplicados, importados, workdone=0):
        def pts(x):
            return "{:,}".format(x).replace(",", ".")

        self.lbLeidos.set_text(pts(leidos))
        if self.siErroneos:
            self.lbErroneos.set_text(pts(erroneos))
        self.lbDuplicados.set_text(pts(duplicados))
        self.lbImportados.set_text(pts(importados))
        if self.siWorkDone:
            self.lbWorkDone.set_text("%d%%" % int(workdone))
        QTUtil.refresh_gui()
        return not self.is_canceled


class ImportarFicheroPGN(ImportarFichero):
    def __init__(self, parent):
        ImportarFichero.__init__(self, parent, _("A PGN file"), True, True, Iconos.PGN())


class ImportarFicheroFNS(ImportarFichero):
    def __init__(self, parent):
        ImportarFichero.__init__(self, parent, _("FNS file"), True, False, Iconos.Fichero())


class ImportarFicheroDB(ImportarFichero):
    def __init__(self, parent):
        ImportarFichero.__init__(self, parent, _("Database file"), False, True, Iconos.Database())

    def actualiza(self, leidos, erroneos, duplicados, importados, workdone=0):
        return ImportarFichero.actualiza(self, leidos, 0, duplicados, importados, workdone)


class MensajeFics(QtWidgets.QDialog):
    def __init__(self, parent, mens):
        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle(_("Fics-Elo"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowIcon(Iconos.Fics())
        self.setStyleSheet("QDialog, QLabel { background: #E3F1F9 }")

        lbm = Controles.LB(self, "<big><b>%s</b></big>" % mens)
        self.bt = Controles.PB(self, _("One moment please..."), rutina=self.final, plano=True)
        self.bt.setDisabled(True)
        self.siFinalizado = False

        ly = Colocacion.G().control(lbm, 0, 0).controlc(self.bt, 1, 0)

        ly.margen(20)

        self.setLayout(ly)

    def continua(self):
        self.bt.set_text(_("Continue"))
        self.bt.ponPlano(False)
        self.bt.setDisabled(False)
        self.mostrar()

    def colocaCentrado(self, owner):
        self.move(
            owner.x() + owner.width() // 2 - self.width() // 2, owner.y() + owner.height() // 2 - self.height() // 2
        )
        QTUtil.refresh_gui()
        self.show()
        QTUtil.refresh_gui()
        return self

    def mostrar(self):
        QTUtil.refresh_gui()
        self.exec_()
        QTUtil.refresh_gui()

    def final(self):
        if not self.siFinalizado:
            self.accept()
        self.siFinalizado = True
        QTUtil.refresh_gui()


class MensajeFide(QtWidgets.QDialog):
    def __init__(self, parent, mens):
        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle(_("Fide-Elo"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowIcon(Iconos.Fide())
        self.setStyleSheet("QDialog, QLabel { background: #E9E9E9 }")

        lbm = Controles.LB(self, "<big><b>%s</b></big>" % mens)
        self.bt = Controles.PB(self, _("One moment please..."), rutina=self.final, plano=True)
        self.bt.setDisabled(True)
        self.siFinalizado = False

        ly = Colocacion.G().control(lbm, 0, 0).controlc(self.bt, 1, 0)

        ly.margen(20)

        self.setLayout(ly)

    def continua(self):
        self.bt.set_text(_("Continue"))
        self.bt.ponPlano(False)
        self.bt.setDisabled(False)
        self.mostrar()

    def colocaCentrado(self, owner):
        self.move(owner.x() + owner.width() / 2 - self.width() / 2, owner.y() + owner.height() / 2 - self.height() / 2)
        QTUtil.refresh_gui()
        self.show()
        QTUtil.refresh_gui()
        return self

    def mostrar(self):
        QTUtil.refresh_gui()
        self.exec_()
        QTUtil.refresh_gui()

    def final(self):
        if not self.siFinalizado:
            self.accept()
        self.siFinalizado = True
        QTUtil.refresh_gui()


def list_irina():
    return (
        ("Monkey", _("Monkey"), Iconos.Monkey(), 108 * 1 + 50),
        ("Donkey", _("Donkey"), Iconos.Donkey(), 108 * 2 + 50),
        ("Bull", _("Bull"), Iconos.Bull(), 108 * 3 + 50),
        ("Wolf", _("Wolf"), Iconos.Wolf(), 108 * 4 + 50),
        ("Lion", _("Lion"), Iconos.Lion(), 108 * 5 + 50),
        ("Rat", _("Rat"), Iconos.Rat(), 108 * 6 + 50),
        ("Snake", _("Snake"), Iconos.Snake(), 108 * 7 + 50),
        ("Knight", _("Knight || Medieval knight"), Iconos.KnightMan(), 1200),
        ("Steven", _("Steven"), Iconos.Steven(), 1400),
    )


class ElemDB:
    def __init__(self, path, is_folder):
        self.is_folder = is_folder
        self.path = path

        self.is_autosave = Util.same_path(Code.configuration.file_autosave(), self.path)

        self.name = os.path.basename(path)
        if self.is_autosave:
            self.name = "%s: %s" % (_("Autosave"), self.name)
        if is_folder:
            self.li_elems = self.read(path)
        else:
            self.name = self.name[: self.name.rindex(".")]

    @staticmethod
    def read(folder):
        li = []
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isdir(path):
                li.append(ElemDB(path, True))
            elif f.endswith(".lcdb") or f.endswith(".lcdblink"):
                li.append(ElemDB(path, False))
        return li

    def remove(self, path):
        for n, elem in enumerate(self.li_elems):
            if elem.is_folder:
                elem.remove(path)
            elif Util.same_path(path, elem.path):
                del self.li_elems[n]
                return

    def is_empty(self):
        for n, elem in enumerate(self.li_elems):
            if elem.is_folder:
                if not elem.is_empty():
                    return False
            else:
                return False
        return True

    def remove_empties(self):
        li = []
        for n, elem in enumerate(self.li_elems):
            if elem.is_folder:
                elem.remove_empties()
                if elem.is_empty():
                    li.append(n)
        if len(li) > 0:
            li.sort(reverse=True)
            for n in li:
                del self.li_elems[n]

    def add_submenu(self, submenu, rondo, indicador_previo=None):
        self.li_elems.sort(key=lambda x: ("Z" if x.is_autosave else "A") + x.name.lower())
        previo = "" if indicador_previo is None else indicador_previo
        for elem in self.li_elems:
            if elem.is_folder:
                subsubmenu = submenu.submenu(elem.name, Iconos.Carpeta())
                elem.add_submenu(subsubmenu, rondo, indicador_previo)
        for elem in self.li_elems:
            if not elem.is_folder:
                submenu.opcion(previo + elem.path, elem.name, rondo.otro())


def lista_db(configuration, siAll, remove_autosave=False):
    lista = ElemDB(configuration.folder_databases(), True)
    if not siAll:
        lista.remove(configuration.get_last_database())
    if remove_autosave:
        lista.remove(configuration.file_autosave())
    lista.remove_empties()
    return lista


def select_db(owner, configuration, siAll, siNew, remove_autosave=False):
    lista = lista_db(configuration, siAll, remove_autosave=remove_autosave)
    if lista.is_empty() and not siNew:
        return None

    menu = LCMenu(owner)
    rp = rondoPuntos()
    if lista:
        lista.add_submenu(menu, rp)
    if siNew:
        menu.separador()
        menu.opcion(":n", _("Create new"), Iconos.DatabaseMas())
    return menu.lanza()


def menuDB(submenu, configuration, siAll, indicador_previo=None, remove_autosave=False, siNew=False):
    lista = lista_db(configuration, siAll, remove_autosave=remove_autosave)
    if lista.is_empty() and not siNew:
        return None

    rp = rondoPuntos()
    lista.add_submenu(submenu, rp, indicador_previo=indicador_previo)
    if siNew:
        submenu.separador()
        indicador = ":n"
        if indicador_previo:
            indicador = indicador_previo + indicador
        submenu.opcion(indicador, _("Create new"), Iconos.DatabaseMas())


class ReadAnnotation(QtWidgets.QDialog):
    def __init__(self, parent, objetivo):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)

        self.edAnotacion = Controles.ED(self, "").ponTipoLetra(puntos=Code.configuration.x_menu_points).anchoFijo(70)
        btAceptar = Controles.PB(self, "", rutina=self.aceptar).ponIcono(Iconos.Aceptar(), 32)
        btCancelar = Controles.PB(self, "", rutina=self.cancelar).ponIcono(Iconos.MainMenu(), 32)
        btAyuda = Controles.PB(self, "", rutina=self.get_help).ponIcono(Iconos.AyudaGR(), 32)

        self.objetivo = objetivo
        self.conAyuda = False
        self.errores = 0
        self.resultado = None

        layout = (
            Colocacion.H()
            .relleno(1)
            .control(btAyuda)
            .control(self.edAnotacion)
            .control(btAceptar)
            .control(btCancelar)
            .margen(3)
        )
        self.setLayout(layout)
        self.show()
        self.move(
            parent.x() + parent.board.width() - self.edAnotacion.width() - btAceptar.width() * 3 - 20,
            parent.y() + parent.board.y() - self.edAnotacion.height() + 8,
        )

    def aceptar(self):
        txt = self.edAnotacion.texto()
        txt = txt.strip().replace(" ", "").upper()

        if txt:
            if txt == self.objetivo.upper():
                self.resultado = self.conAyuda, self.errores
                self.accept()
            else:
                self.errores += 1
                self.edAnotacion.setStyleSheet("QWidget { color: red }")

    def cancelar(self):
        self.reject()

    def get_help(self):
        self.conAyuda = True
        self.edAnotacion.set_text(self.objetivo)


class LCTB(Controles.TBrutina):
    def __init__(
            self, parent, li_acciones=None, with_text=True, icon_size=None, puntos=None, background=None, style=None
    ):
        configuration = Code.configuration
        Controles.TBrutina.__init__(
            self,
            parent,
            li_acciones=li_acciones,
            with_text=with_text,
            icon_size=icon_size,
            puntos=configuration.x_tb_fontpoints if puntos is None else puntos,
            background=background,
            style=configuration.type_icons() if style is None else style,
        )


def change_interval(owner, configuration):
    form = FormLayout.FormLayout(owner, _("Replay game"), Iconos.Pelicula_Repetir(), anchoMinimo=250)
    form.separador()
    form.float(_("Number of seconds between moves"), configuration.x_interval_replay / 1000)
    form.separador()
    form.checkbox(_("Beep after each move"), configuration.x_beep_replay)
    form.separador()
    resultado = form.run()
    if resultado is None:
        return None
    accion, liResp = resultado
    vtime, beep = liResp
    if vtime > 0.01:
        configuration.x_interval_replay = int(vtime * 1000)
        configuration.x_beep_replay = beep
        configuration.graba()


def tb_accept_cancel(parent, if_default=False, with_cancel=True):
    li_acciones = [
        (_("Accept"), Iconos.Aceptar(), parent.aceptar),
        None,
        (_("Cancel"), Iconos.Cancelar(), parent.reject if with_cancel else parent.cancelar),
    ]
    if if_default:
        li_acciones.append(None)
        li_acciones.append((_("By default"), Iconos.Defecto(), parent.defecto))
    li_acciones.append(None)

    return LCTB(parent, li_acciones)


class WInfo(QtWidgets.QDialog):
    def __init__(self, wparent, titulo, head, txt, min_tam, pm_icon):
        super(WInfo, self).__init__(wparent)

        self.setWindowTitle(titulo)
        self.setWindowIcon(Iconos.Aplicacion64())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        f = Controles.TipoLetra(puntos=20)

        lb_ico = Controles.LB(self).ponImagen(pm_icon)
        lb_titulo = Controles.LB(self, head).align_center().ponFuente(f)
        lb_texto = Controles.LB(self, txt)
        lb_texto.setMinimumWidth(min_tam - 84)
        lb_texto.setWordWrap(True)
        lb_texto.setTextFormat(QtCore.Qt.RichText)
        bt_seguir = Controles.PB(self, _("Continue"), self.seguir).ponPlano(False)

        ly_v1 = Colocacion.V().control(lb_ico).relleno()
        ly_v2 = Colocacion.V().control(lb_titulo).control(lb_texto).espacio(10).control(bt_seguir)
        ly_h = Colocacion.H().otro(ly_v1).otro(ly_v2).margen(10)

        self.setLayout(ly_h)

    def seguir(self):
        self.close()


def info(parent: QtWidgets.QWidget, titulo: str, head: str, txt: str, min_tam: int, pm_icon: QtGui.QPixmap):
    w = WInfo(parent, titulo, head, txt, min_tam, pm_icon)
    w.exec_()
