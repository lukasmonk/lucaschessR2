import time

from PySide2 import QtCore, QtWidgets

import Code
from Code.Base.Constantes import (
    GO_BACK,
    GO_END,
    GO_FORWARD,
    GO_START,
    ZVALUE_PIECE,
    ZVALUE_PIECE_MOVING
)
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios


def dic_keys():
    return {QtCore.Qt.Key.Key_Left: GO_BACK,
            QtCore.Qt.Key.Key_Right: GO_FORWARD,
            QtCore.Qt.Key.Key_Up: GO_BACK,
            QtCore.Qt.Key.Key_Down: GO_FORWARD,
            QtCore.Qt.Key.Key_Home: GO_START,
            QtCore.Qt.Key.Key_End: GO_END}


class MensEspera(QtWidgets.QWidget):
    def __init__(
        self,
        parent,
        mensaje,
        siCancelar,
        siMuestraYa,
        opacity,
        physical_pos,
        fixedSize,
        titCancelar,
        background,
        pmImagen=None,
        puntos=12,
        conImagen=True,
        siParentNone=False
    ):

        super(MensEspera, self).__init__(None if siParentNone else parent)  # No se indica parent cuando le afecta el disable general, cuando se analiza posicion por ejemplo

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet("QWidget, QLabel { background: %s }" % background)
        if conImagen:
            lbi = QtWidgets.QLabel(self)
            lbi.setPixmap(pmImagen if pmImagen else Iconos.pmMensEspera())

        self.owner = parent

        self.physical_pos = physical_pos
        self.is_canceled = False

        if physical_pos == "tb":
            fixedSize = parent.width()

        self.lb = lb = Controles.LB(parent, resalta(mensaje)).ponFuente(Controles.TipoLetra(puntos=puntos)).align_center()
        if fixedSize is not None:
            lb.set_wrap().anchoFijo(fixedSize - 60)

        if siCancelar:
            if not titCancelar:
                titCancelar = _("Cancel")
            self.btCancelar = Controles.PB(self, titCancelar, rutina=self.cancelar, plano=False).ponIcono(Iconos.Cancelar()).anchoFijo(100)

        ly = Colocacion.G()
        if conImagen:
            ly.control(lbi, 0, 0, 3, 1)
        ly.controlc(lb, 1, 1)
        if siCancelar:
            ly.controlc(self.btCancelar, 2, 1)

        ly.margen(24)
        self.setLayout(ly)
        self.teclaPulsada = None

        if fixedSize:
            self.setFixedWidth(fixedSize)

        self.setWindowOpacity(opacity)
        if siMuestraYa:
            self.muestra()

    def cancelar(self):
        self.is_canceled = True
        self.final()

    def cancelado(self):
        QTUtil.refresh_gui()
        return self.is_canceled

    def activarCancelar(self, siActivar):
        self.btCancelar.setVisible(siActivar)
        QTUtil.refresh_gui()
        return self

    def keyPressEvent(self, event):
        QtWidgets.QWidget.keyPressEvent(self, event)
        self.teclaPulsada = event.key()

    def label(self, nuevo):
        self.lb.set_text(resalta(nuevo))
        QTUtil.refresh_gui()

    def muestra(self):
        self.show()

        v = self.owner
        s = self.size()
        if self.physical_pos == "ad":
            x = v.x() + v.width() - s.width()
            y = v.y() + 4
        elif self.physical_pos == "tb":
            x = v.x() + 4
            y = v.y() + 4
        else:
            x = v.x() + (v.width() - s.width()) // 2
            y = v.y() + (v.height() - s.height()) // 2

        # p = self.owner.mapToGlobal(QtCore.QPoint(x,y))
        p = QtCore.QPoint(x,y)
        self.move(p)
        QTUtil.refresh_gui()
        return self

    def final(self):
        QTUtil.refresh_gui()
        self.hide()
        self.close()
        self.destroy()
        QTUtil.refresh_gui()


class ControlMensEspera:
    def __init__(self):
        self.me = None

    def start(
        self,
        parent,
        mensaje,
        siCancelar=False,
        siMuestraYa=True,
        opacity=0.90,
        physical_pos="c",
        fixedSize=None,
        titCancelar=None,
        background=None,
        pmImagen=None,
        puntos=11,
        conImagen=True,
        siParentNone=False
    ):
        if self.me:
            self.final()
        if background is None:
            background = "#D3E3EC"
        self.me = MensEspera(
            parent, mensaje, siCancelar, siMuestraYa, opacity, physical_pos, fixedSize, titCancelar, background, pmImagen, puntos, conImagen, siParentNone=siParentNone
        )
        QTUtil.refresh_gui()
        return self

    def final(self):
        if self.me:
            self.me.final()
            self.me = None

    def label(self, txt):
        self.me.label(txt)

    def cancelado(self):
        if self.me:
            return self.me.cancelado()
        return True

    def teclaPulsada(self, k):
        if self.me is None:
            return False
        if self.me.teclaPulsada:
            resp = self.me.teclaPulsada == k
            self.me.teclaPulsada = None
            return resp
        else:
            return False

    def time(self, secs):
        def test():
            if not self.me:
                return
            self.ms -= 100
            if self.cancelado() or self.ms <= 0:
                self.ms = 0
                self.final()
                return
            QtCore.QTimer.singleShot(100, test)

        self.ms = secs * 1000
        QtCore.QTimer.singleShot(100, test)
        QTUtil.refresh_gui()


mensEspera = ControlMensEspera()


def mensajeTemporal(
    main_window, mensaje, seconds, background=None, pmImagen=None, physical_pos="c", fixedSize=None, siCancelar=None, titCancelar=None
):
    if siCancelar is None:
        siCancelar = seconds > 3.0
    if titCancelar is None:
        titCancelar = _("Continue")
    me = mensEspera.start(
        main_window,
        mensaje,
        background=background,
        pmImagen=pmImagen,
        siCancelar=siCancelar,
        titCancelar=titCancelar,
        physical_pos=physical_pos,
        fixedSize=fixedSize,
    )
    if seconds:
        me.time(seconds)
    return me


def mensajeTemporalSinImagen(main_window, mensaje, seconds, background=None, puntos=12, physical_pos="c"):
    me = mensEspera.start(
        main_window, mensaje, physical_pos=physical_pos, conImagen=False, puntos=puntos, fixedSize=None, background=background
    )
    if seconds:
        me.time(seconds)
    return me


class BarraProgreso2(QtWidgets.QDialog):
    def __init__(self, owner, titulo, formato1="%v/%m", formato2="%v/%m"):
        QtWidgets.QDialog.__init__(self, owner)

        self.owner = owner
        self.is_closed = False

        # self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(titulo)

        # gb1 + progress
        self.bp1 = QtWidgets.QProgressBar()
        self.bp1.setFormat(formato1)
        ly = Colocacion.H().control(self.bp1)
        self.gb1 = Controles.GB(self, "", ly)

        # gb2 + progress
        self.bp2 = QtWidgets.QProgressBar()
        self.bp2.setFormat(formato2)
        ly = Colocacion.H().control(self.bp2)
        self.gb2 = Controles.GB(self, "", ly)

        # cancelar
        bt = Controles.PB(self, _("Cancel"), self.cancelar, plano=False)  # .ponIcono( Iconos.Delete() )
        lyBT = Colocacion.H().relleno().control(bt)

        layout = Colocacion.V().control(self.gb1).control(self.gb2).otro(lyBT)

        self.setLayout(layout)
        self._is_canceled = False

    def closeEvent(self, event):
        self._is_canceled = True
        self.cerrar()

    def mostrar(self):
        self.move(self.owner.x() + (self.owner.width() - self.width()) / 2, self.owner.y() + (self.owner.height() - self.height()) / 2)
        self.show()
        return self

    def show_top_right(self):
        self.move(self.owner.x() + self.owner.width() - self.width(), self.owner.y())
        self.show()
        return self

    def cerrar(self):
        if not self.is_closed:
            self.reject()
            self.is_closed = True
        QTUtil.refresh_gui()

    def cancelar(self):
        self._is_canceled = True
        self.cerrar()

    def ponRotulo(self, cual, texto):
        gb = self.gb1 if cual == 1 else self.gb2
        gb.set_text(texto)

    def ponTotal(self, cual, maximo):
        bp = self.bp1 if cual == 1 else self.bp2
        bp.setRange(0, maximo)

    def pon(self, cual, valor):
        bp = self.bp1 if cual == 1 else self.bp2
        bp.setValue(valor)

    def is_canceled(self):
        QTUtil.refresh_gui()
        return self._is_canceled


class BarraProgreso1(QtWidgets.QDialog):
    def __init__(self, owner, titulo, formato1="%v/%m"):
        QtWidgets.QDialog.__init__(self, owner)

        self.owner = owner

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(titulo)

        # gb1 + progress
        self.bp1 = QtWidgets.QProgressBar()
        self.bp1.setFormat(formato1)
        ly = Colocacion.H().control(self.bp1)
        self.gb1 = Controles.GB(self, "", ly)

        # cancelar
        bt = Controles.PB(self, _("Cancel"), self.cancelar, plano=False)
        lyBT = Colocacion.H().relleno().control(bt)

        layout = Colocacion.V().control(self.gb1).otro(lyBT)

        self.setLayout(layout)
        self._is_canceled = False

    def closeEvent(self, event):
        self._is_canceled = True
        self.cerrar()

    def mostrar(self):
        self.move(self.owner.x() + (self.owner.width() - self.width()) / 2, self.owner.y() + (self.owner.height() - self.height()) / 2)
        self.show()
        return self

    def show_top_right(self):
        self.move(self.owner.x() + self.owner.width() - self.width(), self.owner.y())
        self.show()
        return self

    def cerrar(self):
        self.hide()
        self.reject()
        QTUtil.refresh_gui()

    def cancelar(self):
        self._is_canceled = True
        self.cerrar()

    def ponRotulo(self, texto):
        self.gb1.set_text(texto)

    def ponTotal(self, maximo):
        self.bp1.setRange(0, maximo)

    def pon(self, valor):
        self.bp1.setValue(valor)
        QTUtil.refresh_gui()

    def is_canceled(self):
        QTUtil.refresh_gui()
        return self._is_canceled


class BarraProgreso(QtWidgets.QProgressDialog):
    # ~ bp = QTUtil2.BarraProgreso( self, "me", 5 ).mostrar()
    # ~ n = 0
    # ~ for n in range(5):
    # ~ prlk( n )
    # ~ bp.pon( n )
    # ~ time.sleep(1)
    # ~ if bp.is_canceled():
    # ~ break
    # ~ bp.cerrar()

    def __init__(self, owner, titulo, mensaje, total):
        QtWidgets.QProgressDialog.__init__(self, mensaje, _("Cancel"), 0, total, owner)
        self.total = total
        self.actual = 0
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setWindowTitle(titulo)
        self.owner = owner
        self.setAutoClose(False)
        self.setAutoReset(False)

    def mostrar(self):
        if self.owner:
            self.move(self.owner.x() + (self.owner.width() - self.width()) / 2, self.owner.y() + (self.owner.height() - self.height()) / 2)
        self.show()
        return self

    def show_top_right(self):
        if self.owner:
            self.move(self.owner.x() + self.owner.width() - self.width(), self.owner.y())
        self.show()
        return self

    def cerrar(self):
        self.setValue(self.total)
        self.close()

    def mensaje(self, mens):
        self.setLabelText(mens)

    def is_canceled(self):
        QTUtil.refresh_gui()
        return self.wasCanceled()

    def ponTotal(self, total):
        self.setMaximum(total)
        self.pon(0)

    def pon(self, valor):
        self.setValue(valor)
        self.actual = valor

    def inc(self):
        self.pon(self.actual + 1)


def resalta(mens, tipo=4):
    return ("<h%d>%s</h%d>" % (tipo, mens, tipo)).replace("\n", "<br>")


def tbAcceptCancel(parent, if_default=False, siReject=True):
    li_acciones = [
        (_("Accept"), Iconos.Aceptar(), parent.aceptar),
        None,
        (_("Cancel"), Iconos.Cancelar(), parent.reject if siReject else parent.cancelar),
    ]
    if if_default:
        li_acciones.append(None)
        li_acciones.append((_("Default"), Iconos.Defecto(), parent.defecto))
    li_acciones.append(None)

    return QTVarios.LCTB(parent, li_acciones)


def tiposDeLineas():
    li = (
        (_("No pen"), 0),
        (_("Solid line"), 1),
        (_("Dash line"), 2),
        (_("Dot line"), 3),
        (_("Dash dot line"), 4),
        (_("Dash dot dot line"), 5),
    )
    return li


def listaOrdenes():
    li = []
    for k in range(5, 30):
        txt = "%2d" % (k - 4,)
        if k == ZVALUE_PIECE:
            txt += " => " + _("Piece")
        elif k == ZVALUE_PIECE_MOVING:
            txt += " => " + _("Moving piece")

        li.append((txt, k))
    return li


def spinBoxLB(owner, valor, from_sq, to_sq, etiqueta=None, maxTam=None, fuente=None):
    ed = Controles.SB(owner, valor, from_sq, to_sq)
    if fuente:
        ed.setFont(fuente)
    if maxTam:
        ed.tamMaximo(maxTam)
    if etiqueta:
        label = Controles.LB(owner, etiqueta + ": ")
        if fuente:
            label.setFont(fuente)
        return ed, label
    else:
        return ed


def comboBoxLB(parent, li_options, valor, etiqueta=None):
    cb = Controles.CB(parent, li_options, valor)
    if etiqueta:
        return cb, Controles.LB(parent, etiqueta + ": ")
    else:
        return cb


def unMomento(owner, mensaje=None, physical_pos=None):
    if mensaje is None:
        mensaje = _("One moment please...")
    return mensEspera.start(owner, mensaje, physical_pos=physical_pos)


def analizando(owner):
    return mensEspera.start(owner, _("Analyzing the move...."), physical_pos="ad")


def ponIconosMotores(lista):
    liResp = []
    for titulo, key in lista:
        liResp.append((titulo, key, Iconos.PuntoEstrella() if key.startswith("*") else Iconos.PuntoVerde()))
    return liResp


def message(owner, texto, explanation=None, titulo=None, pixmap=None, px=None, py=None, si_bold=False):
    msg = QtWidgets.QMessageBox(owner)
    if pixmap is None:
        msg.setIconPixmap(Iconos.pmMensInfo())
    else:
        msg.setIconPixmap(pixmap)
    msg.setText(texto)
    msg.setFont(Controles.TipoLetra(puntos=Code.configuration.x_menu_points, peso=300 if si_bold else 50))
    if explanation:
        msg.setInformativeText(explanation)
    if titulo is None:
        titulo = _("Message")
    msg.setWindowTitle(titulo)
    if px is not None:
        msg.move(px, py)  # topright: owner.x() + owner.width() - msg.width() - 46, owner.y()+4)
    msg.addButton(_("Continue"), QtWidgets.QMessageBox.ActionRole)
    msg.exec_()


def message_accept(owner, texto, explanation=None, titulo=None):
    message(owner, texto, explanation=explanation, titulo=titulo, pixmap=Iconos.pmAceptar())


def message_error(owner, texto):
    message(owner, texto, titulo=_("Error"), pixmap=Iconos.pmMensError())


def message_error_control(owner, mens, control):
    px = owner.x() + control.x()
    py = owner.y() + control.y()
    message(owner, mens, titulo=_("Error"), pixmap=Iconos.pmCancelar(), px=px, py=py)


def message_bold(owner, mens, titulo=None):
    message(owner, mens, titulo=titulo, si_bold=True)


class QWMessage(QtWidgets.QWidget):
    def __init__(self, owner, message):
        QtWidgets.QWidget.__init__(self, owner)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        lb = Controles.LB(self, message)
        lb.setFont(Controles.TipoLetra(puntos=Code.configuration.x_menu_points, peso=300))
        titulo = _("Message")
        self.setWindowTitle(titulo)
        bt = Controles.PB(self, _("Continue"), self.continuar, plano=False)
        layout = Colocacion.V().control(lb).espacio(20).control(bt)
        self.setLayout(layout)
        self.activo = True

    def continuar(self):
        self.close()
        self.activo = False


def message_nomodal(owner, message):
    w = QWMessage(owner, message)
    w.show()
    while w.activo:
        QTUtil.refresh_gui()
        time.sleep(0.1)


def pregunta(parent, mens, label_yes=None, label_no=None, si_top=False, px=None, py=None):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, _("Question"), resalta(mens), parent=parent)
    if label_yes is None:
        label_yes = _("Yes")
    if label_no is None:
        label_no = _("No")
    si_button = msg_box.addButton(label_yes, QtWidgets.QMessageBox.YesRole)
    msg_box.setFont(Controles.TipoLetra(puntos=Code.configuration.x_menu_points))
    msg_box.addButton(label_no, QtWidgets.QMessageBox.NoRole)
    if si_top:
        msg_box.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    if px is not None:
        msg_box.move(px, py)  # topright: owner.x() + owner.width() - msg.width() - 46, owner.y()+4)
    msg_box.exec_()

    return msg_box.clickedButton() == si_button


def preguntaCancelar(parent, mens, si, no):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, _("Question"), resalta(mens), parent=parent)
    si_button = msg_box.addButton(si, QtWidgets.QMessageBox.YesRole)
    no_button = msg_box.addButton(no, QtWidgets.QMessageBox.NoRole)
    msg_box.addButton(_("Cancel"), QtWidgets.QMessageBox.RejectRole)
    msg_box.setFont(Controles.TipoLetra(puntos=Code.configuration.x_menu_points))
    msg_box.exec_()
    cb = msg_box.clickedButton()
    if cb == si_button:
        resp = True
    elif cb == no_button:
        resp = False
    else:
        resp = None
    return resp


def preguntaCancelar123(parent, title, mens, si, no, cancel):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, title, resalta(mens), parent=parent)
    si_button = msg_box.addButton(si, QtWidgets.QMessageBox.YesRole)
    no_button = msg_box.addButton(no, QtWidgets.QMessageBox.NoRole)
    cancel_button = msg_box.addButton(cancel, QtWidgets.QMessageBox.RejectRole)
    msg_box.exec_()
    cb = msg_box.clickedButton()
    if cb == si_button:
        resp = 1
    elif cb == no_button:
        resp = 2
    elif cb == cancel_button:
        resp = 3
    else:
        resp = 0
    return resp


