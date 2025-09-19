import time

from PySide2 import QtCore, QtWidgets, QtGui

import Code
from Code.Base.Constantes import (GO_BACK, GO_END, GO_FORWARD, GO_START, GO_BACK2, GO_FORWARD2, ZVALUE_PIECE,
                                  ZVALUE_PIECE_MOVING, TOP_RIGHT,
                                  ON_TOOLBAR)
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios


def dic_keys():
    return {
        QtCore.Qt.Key.Key_Left: GO_BACK,
        QtCore.Qt.Key.Key_Right: GO_FORWARD,
        QtCore.Qt.Key.Key_Up: GO_BACK2,
        QtCore.Qt.Key.Key_Down: GO_FORWARD2,
        QtCore.Qt.Key.Key_Home: GO_START,
        QtCore.Qt.Key.Key_End: GO_END,
    }


class MensEspera(QtWidgets.QWidget):
    def __init__(
            self,
            parent,
            mensaje,
            with_cancel,
            show_now,
            opacity,
            physical_pos,
            fixed_size,
            tit_cancel,
            background,
            pm_image=None,
            puntos=None,
            with_image=True,
            if_parent_none=False,
    ):

        super(MensEspera, self).__init__(
            None if if_parent_none else parent
        )  # No se indica parent cuando le afecta el disable general, cuando se analiza posicion por ejemplo

        self.setWindowFlags(
            QtCore.Qt.Tool
            | QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.FramelessWindowHint
        )
        self.setStyleSheet("QWidget, QLabel { background: %s }" % background)

        lbi = None
        if with_image:
            lbi = QtWidgets.QLabel(self)
            lbi.setPixmap(pm_image if pm_image else Iconos.pmMensEspera())

        self.owner = parent

        self.physical_pos = physical_pos
        self.is_canceled = False

        if physical_pos == ON_TOOLBAR:
            fixed_size = parent.width()

        if puntos is None:
            puntos = Code.configuration.x_sizefont_messages

        self.lb = lb = (
            Controles.LB(parent, resalta(mensaje)).set_font(Controles.FontType(puntos=puntos)).align_center()
        )
        if fixed_size is not None:
            lb.set_wrap().relative_width(fixed_size - 60)

        if with_cancel:
            if not tit_cancel:
                tit_cancel = _("Cancel")
            self.btCancelar = (
                Controles.PB(self, tit_cancel, rutina=self.cancelar, plano=False).ponIcono(Iconos.Cancelar())
                # .relative_width(100)
            )
            self.btCancelar.setStyleSheet(
                """QPushButton {
    background-color: #1e749c;
    color: white;
    border-style: outset;
    border-width: 2px;
    border-radius: 8px;
    border-color: beige;
    font: bold 11pt;
    min-width: 10em;
    padding: 4px;
}
QPushButton:pressed {
    background-color: rgb(224, 0, 0);
    border-style: inset;
}"""
            )

        ly = Colocacion.G()
        if with_image:
            ly.control(lbi, 0, 0, 3, 1)
        ly.controlc(lb, 1, 1)
        if with_cancel:
            ly.controlc(self.btCancelar, 2, 1)

        ly.margen(24)
        self.setLayout(ly)
        self.key_pressed = None

        if fixed_size:
            self.setFixedWidth(fixed_size)

        self.setWindowOpacity(opacity)
        if show_now:
            self.muestra()

    def cancelar(self):
        self.is_canceled = True
        self.final()

    def cancelado(self):
        QTUtil.refresh_gui()
        return self.is_canceled

    def activate_cancel(self, ok):
        self.btCancelar.setVisible(ok)
        QTUtil.refresh_gui()
        return self

    def keyPressEvent(self, event):
        QtWidgets.QWidget.keyPressEvent(self, event)
        self.key_pressed = event.key()

    def label(self, nuevo):
        self.lb.set_text(resalta(nuevo))
        QTUtil.refresh_gui()

    def muestra(self):
        self.show()

        v = self.owner
        if v:
            if self.physical_pos == TOP_RIGHT:
                s = self.size()
                x = v.x() + v.width() - s.width()
                w_screen = QTUtil.desktop_width()
                if x + s.width() > w_screen:
                    x = w_screen - s.width() - 4
                y = v.y() + 4
                self.move(QtCore.QPoint(x, y))
            elif self.physical_pos == ON_TOOLBAR:
                x = v.x() + 4
                y = v.y() + 4
                self.move(QtCore.QPoint(x, y))
            else:
                QTUtil.center_on_widget(self)
        QTUtil.refresh_gui()
        return self

    def final(self):
        try:
            self.hide()
            self.close()
            self.destroy()
        except RuntimeError:
            pass
        QTUtil.refresh_gui()


class ControlWaitingMessage:
    def __init__(self):
        self.me = None
        self.ms = None

    def start(
            self,
            parent,
            mensaje,
            with_cancel=False,
            show_now=True,
            opacity=0.91,
            physical_pos="c",
            fixed_size=None,
            tit_cancel=None,
            background=None,
            pm_image=None,
            puntos=None,
            with_image=True,
            if_parent_none=False,
    ):
        if self.me:
            self.final()
        if background is None:
            background = Code.dic_colors["CONTROLMENSESPERA"]

        if puntos is None:
            puntos = Code.configuration.x_sizefont_messages

        self.me = MensEspera(
            parent,
            mensaje,
            with_cancel,
            show_now,
            opacity,
            physical_pos,
            fixed_size,
            tit_cancel,
            background,
            pm_image,
            puntos,
            with_image,
            if_parent_none=if_parent_none,
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

    def key_pressed(self, k):
        if self.me is None:
            return False
        if self.me.key_pressed:
            resp = self.me.key_pressed == k
            self.me.key_pressed = None
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


waiting_message = ControlWaitingMessage()


def one_moment_please(owner, mensaje=None, physical_pos=None):
    if mensaje is None:
        mensaje = _("One moment please...")
    return waiting_message.start(owner, mensaje, physical_pos=physical_pos)


def working(owner):
    return one_moment_please(owner, _("Working..."))


class OneMomentPlease:
    def __init__(self, owner, the_message=None, physical_pos=None, with_cancel=False):
        self.owner = owner
        self.the_message = _("One moment please...") if the_message is None else the_message
        self.physical_pos = physical_pos
        self.um = None
        self.with_cancel = with_cancel

    def __enter__(self):
        self.um = waiting_message.start(self.owner, self.the_message, physical_pos=self.physical_pos,
                                        with_cancel=self.with_cancel)
        QTUtil.refresh_gui()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.um:
            self.um.final()
            self.um = None

    def is_canceled(self):
        if self.um and self.um.cancelado():
            self.close()
            return True
        return self.um is None

    def label(self, mens):
        if self.um:
            self.um.label(mens)
            QTUtil.refresh_gui()


def analizando(owner, with_cancel=False):
    return waiting_message.start(owner, _("Analyzing the move...."), physical_pos=TOP_RIGHT, with_cancel=with_cancel)


def temporary_message(
        main_window,
        mensaje,
        seconds,
        background=None,
        pm_image=None,
        physical_pos="c",
        fixed_size=None,
        with_cancel=None,
        tit_cancel=None,
):
    if with_cancel is None:
        with_cancel = seconds > 3.0
    if tit_cancel is None:
        tit_cancel = _("Continue")
    me = waiting_message.start(
        main_window,
        mensaje,
        background=background,
        pm_image=pm_image,
        with_cancel=with_cancel,
        tit_cancel=tit_cancel,
        physical_pos=physical_pos,
        fixed_size=fixed_size,
    )
    if seconds:
        me.time(seconds)
    return me


def temporary_message_without_image(main_window, mensaje, seconds, background=None, puntos=None, physical_pos="c"):
    me = waiting_message.start(
        main_window,
        mensaje,
        physical_pos=physical_pos,
        with_image=False,
        puntos=puntos,
        fixed_size=None,
        background=background,
    )
    if seconds:
        me.time(seconds)
    return me


class BarraProgreso2(QtWidgets.QDialog):
    def __init__(self, owner, titulo, formato1="%v/%m", formato2="%v/%m", with_pause=False):
        QtWidgets.QDialog.__init__(self, owner)

        self.owner = owner
        self.is_closed = False

        self.with_pause = with_pause
        self._is_paused = False

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
        ly_bt = Colocacion.H().relleno()

        # pausa
        if with_pause:
            self.bt_pause = Controles.PB(self, _("Pause"), self.pausar_continuar, plano=False)
            ly_bt.control(self.bt_pause)

        ly_bt.control(bt)

        layout = Colocacion.V().control(self.gb1).control(self.gb2).otro(ly_bt)

        self.setLayout(layout)
        self._is_canceled = False

    def closeEvent(self, event):
        self._is_canceled = True
        self.cerrar()

    def mostrar(self):
        self.show()
        QTUtil.center_on_widget(self)
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

    def pausar_continuar(self):
        if self._is_paused:
            self.bt_pause.set_text(_("Pause"))
        else:
            self.bt_pause.set_text(_("Continue"))
        self._is_paused = not self._is_paused

    def check_pause(self):
        if self._is_paused:
            while self._is_paused and not self._is_canceled:
                time.sleep(0.05)
                QTUtil.refresh_gui()

    def is_paused(self):
        return False if self._is_canceled else self._is_paused

    def put_label(self, cual, texto):
        gb = self.gb1 if cual == 1 else self.gb2
        gb.set_text(texto)

    def set_total(self, cual, maximo):
        bp = self.bp1 if cual == 1 else self.bp2
        bp.setRange(0, maximo)

    def pon(self, cual, valor):
        bp = self.bp1 if cual == 1 else self.bp2
        bp.setValue(valor)
        if self.with_pause:
            self.check_pause()

    def is_canceled(self):
        QTUtil.refresh_gui()
        return self._is_canceled


class BarraProgreso1(QtWidgets.QDialog):
    def __init__(self, owner, titulo, formato1="%v/%m", show_time=False):
        QtWidgets.QDialog.__init__(self, owner)

        self.owner = owner
        self.show_time = show_time
        self.total = 0

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(titulo)

        # gb1 + progress
        self.bp1 = QtWidgets.QProgressBar()
        self.bp1.setFormat(formato1)
        ly = Colocacion.V().control(self.bp1)
        if show_time:
            self.li_times = []
            self.lb_time = Controles.LB(self)
            self.time_inicial = None
            self.valor_previo = 0
            ly.control(self.lb_time)
        self.gb1 = Controles.GB(self, "", ly)

        # cancelar
        bt = Controles.PB(self, _("Cancel"), self.cancelar, plano=False)
        ly_bt = Colocacion.H().relleno().control(bt)

        layout = Colocacion.V().control(self.gb1).otro(ly_bt)

        self.setMinimumWidth(480)

        self.setLayout(layout)
        self._is_canceled = False
        self._is_closed = False

    def closeEvent(self, event):
        self._is_canceled = True
        self.cerrar()

    def mostrar(self):
        self.show()
        QTUtil.center_on_widget(self)
        return self

    def show_top_right(self):
        self.move(self.owner.x() + self.owner.width() - self.width(), self.owner.y())
        self.show()
        return self

    def cerrar(self):
        if not self._is_closed:
            self.hide()
            self.reject()
            QTUtil.refresh_gui()
            self._is_closed = True

    def cancelar(self):
        self._is_canceled = True
        self.cerrar()

    def put_label(self, texto):
        self.gb1.set_text(texto)

    def set_total(self, maximo):
        self.total = maximo
        self.bp1.setRange(0, maximo)
        if self.show_time:
            self.li_times = []
            self.time_inicial = time.time()
            self.valor_previo = 0

    def pon(self, valor):
        self.bp1.setValue(valor)
        QTUtil.refresh_gui()
        if self.show_time:
            salto = valor - self.valor_previo
            if salto == 0:
                return
            time_actual = time.time()
            tm = (time_actual - self.time_inicial) / salto
            self.valor_previo = valor
            self.time_inicial = time_actual
            self.li_times.append(tm)
            tm = sum(self.li_times) / len(self.li_times)
            previsto = int(tm * (self.total - valor))
            xmessage = time_message(previsto)

            lb_pt = _("Pending time")
            self.lb_time.set_text(f"{lb_pt}: {xmessage}")

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

    def __init__(self, owner, titulo, mensaje, total, width=None):
        QtWidgets.QProgressDialog.__init__(self, mensaje, _("Cancel"), 0, total, owner)
        self.total = total
        self.actual = 0
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setWindowTitle(titulo)
        self.owner = owner
        self.setAutoClose(False)
        self.setAutoReset(False)
        if width:
            self.setFixedWidth(width)

    def mostrar(self):
        if self.owner:
            self.move(
                self.owner.x() + (self.owner.width() - self.width()) / 2,
                self.owner.y() + (self.owner.height() - self.height()) / 2,
            )
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

    def set_total(self, total):
        self.setMaximum(total)
        self.pon(0)

    def pon(self, valor):
        self.setValue(valor)
        self.actual = valor

    def inc(self):
        self.pon(self.actual + 1)


def resalta(mens, tipo=4):
    return ("<h%d>%s</h%d>" % (tipo, mens, tipo)).replace("\n", "<br>")


def lines_type():
    li = (
        (_("No pen"), 0),
        (_("Solid line"), 1),
        (_("Dash line"), 2),
        (_("Dot line"), 3),
        (_("Dash dot line"), 4),
        (_("Dash dot dot line"), 5),
    )
    return li


def list_zvalues():
    li = []
    for k in range(5, 30):
        txt = "%2d" % (k - 4,)
        if k == ZVALUE_PIECE:
            txt += " ≥ " + _("Piece")
        elif k == ZVALUE_PIECE_MOVING:
            txt += " ≥ " + _("Moving piece")

        li.append((txt, k))
    return li


def spinbox_lb(owner, valor, from_sq, to_sq, etiqueta=None, max_width=None, fuente=None):
    ed = Controles.SB(owner, valor, from_sq, to_sq)
    if fuente:
        ed.setFont(fuente)
    if max_width:
        ed.relative_width(max_width)
    if etiqueta:
        label = Controles.LB(owner, etiqueta + ": ")
        if fuente:
            label.setFont(fuente)
        return ed, label
    else:
        return ed


def combobox_lb(parent, li_options, valor, etiqueta=None):
    cb = Controles.CB(parent, li_options, valor)
    if etiqueta:
        return cb, Controles.LB(parent, etiqueta + ": ")
    else:
        return cb


def message(owner, texto, explanation=None, titulo=None, pixmap=None, px=None, py=None, si_bold=False, delayed=False):
    def send():
        msg = QtWidgets.QMessageBox(owner)
        if pixmap is None:
            msg.setIconPixmap(Iconos.pmMensInfo())
        else:
            msg.setIconPixmap(pixmap)
        msg.setText(texto)
        msg.setFont(Controles.FontType(puntos=Code.configuration.x_sizefont_messages, peso=300 if si_bold else 50))
        if explanation:
            msg.setInformativeText(explanation)
        msg.setWindowTitle(_("Message") if titulo is None else titulo)
        if px is not None:
            msg.move(px, py)  # topright: owner.x() + owner.width() - msg.width() - 46, owner.y()+4)
        msg.addButton(_("Continue"), QtWidgets.QMessageBox.ActionRole)
        msg.setFixedWidth(800)

        msg.exec_()

    if delayed:
        QtCore.QTimer.singleShot(50, send)
    else:
        send()


def message_accept(owner, texto, explanation=None, titulo=None, delayed=False):
    message(owner, texto, explanation=explanation, titulo=titulo, pixmap=Iconos.pmAceptar(), delayed=delayed)


def message_error(owner, texto, delayed=False):
    message(owner, texto, titulo=_("Error"), pixmap=Iconos.pmMensError(), delayed=delayed)


def message_error_control(owner, mens, control):
    px = owner.x() + control.x()
    py = owner.y() + control.y()
    message(owner, mens, titulo=_("Error"), pixmap=Iconos.pmCancelar(), px=px, py=py)


def message_bold(owner, mens, titulo=None, delayed=False):
    message(owner, mens, titulo=titulo, si_bold=True, delayed=delayed)


def message_information(window, txt):
    message(window, "<br><br><b><big><b>%s</b></big>" % txt, titulo=_("Information"), pixmap=Iconos.pmCheck())


def message_result_win(window, txt):
    message(window, "<br><br><b><big><b>%s</b></big>" % txt, titulo=_("Result"), pixmap=Iconos.pmTrophy())


def pregunta(parent, mens, label_yes=None, label_no=None, si_top=False, px=None, py=None):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, _("Question"), resalta(mens), parent=parent)
    if label_yes is None:
        label_yes = _("Yes")
    if label_no is None:
        label_no = _("No")
    si_button = msg_box.addButton(label_yes, QtWidgets.QMessageBox.YesRole)
    msg_box.setFont(Controles.FontType(puntos=Code.configuration.x_sizefont_messages))
    msg_box.addButton(label_no, QtWidgets.QMessageBox.NoRole)
    if si_top:
        msg_box.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    if px is not None:
        msg_box.move(px, py)  # topright: owner.x() + owner.width() - msg.width() - 46, owner.y()+4)
    msg_box.exec_()

    if msg_box.isVisible():
        msg_box.hide()
        QTUtil.refresh_gui()

    return msg_box.clickedButton() == si_button


def question_withcancel(parent, mens, si, no, cancel=None):
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, _("Question"), resalta(mens), parent=parent)
    si_button = msg_box.addButton(si, QtWidgets.QMessageBox.YesRole)
    no_button = msg_box.addButton(no, QtWidgets.QMessageBox.NoRole)
    msg_box.addButton(_("Cancel") if cancel is None else cancel, QtWidgets.QMessageBox.RejectRole)
    msg_box.setFont(Controles.FontType(puntos=Code.configuration.x_sizefont_messages))
    msg_box.exec_()
    cb = msg_box.clickedButton()
    if cb == si_button:
        resp = True
    elif cb == no_button:
        resp = False
    else:
        resp = None
    return resp


def question_withcancel_123(parent, title, mens, si, no, cancel):
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


def message_menu(owner, main, the_message, delayed, zzpos=True, dont_show=False):
    def show():

        previo = QtGui.QCursor.pos()
        if zzpos:
            p = owner.mapToGlobal(QtCore.QPoint(0, 0))
        else:
            p = previo
        QtGui.QCursor.setPos(p)

        menu = QTVarios.LCMenu(owner)

        Code.configuration.set_property(menu, "101")
        f = Controles.FontType(puntos=Code.configuration.x_font_points)
        menu.set_font(f)

        menu.separador()
        menu.opcion(None, main)
        menu.separador()
        menu.separador_blank()

        q = QtGui.QTextDocument(the_message, owner)
        q.setDefaultFont(f)
        q.setTextWidth(owner.width())
        q.setUseDesignMetrics(True)
        qto = QtGui.QTextOption()
        qto.setWrapMode(qto.WordWrap)
        q.setDefaultTextOption(qto)
        q.adjustSize()

        ret = []
        tb = q.begin()
        while tb.isValid():
            block_text = tb.text()
            if not tb.layout():
                continue
            for i in range(tb.layout().lineCount()):
                line = tb.layout().lineAt(i)
                ret.append(block_text[line.textStart(): line.textStart() + line.textLength()])
            tb = tb.next()

        for linea in ret:
            menu.opcion("k", linea)

        if dont_show:
            menu.separador_blank()
            menu.separador()
            pointsize = menu.font().pointSize() - 3
            menu.opcion("dontshow", _("Do not show again"), Iconos.PuntoRojo(), font_type=Controles.FontType(puntos=pointsize))

        def vuelve():
            QtGui.QCursor.setPos(previo)

        if zzpos:
            QtCore.QTimer.singleShot(50, vuelve)

        resp = menu.lanza()
        if resp == "dontshow":
            return True
        return False

    if delayed:
        QtCore.QTimer.singleShot(50, show)
    else:
        return show()


class SimpleWindow(QtWidgets.QDialog):
    def __init__(self, owner, title, label, valor, mas_info, width, in_cursor, li_values):
        QtWidgets.QDialog.__init__(self, owner)
        self.setWindowTitle(title)
        self.resultado = None
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        lb_clave = Controles.LB(self, label + ": ")
        self.with_list_values = li_values is not None
        if self.with_list_values:
            li_values = [(value, value) for value in li_values]
            li_values.insert(0, ("", ""))
            self.cb_clave = Controles.CB(self, li_values, valor, extend_seek=True)
            self.cb_clave.setEditable(True)
            self.cb_clave.setCurrentText(valor)
            field = self.cb_clave
        else:
            self.ed_clave = Controles.ED(self, valor)
            field = self.ed_clave

        field.setMinimumWidth(width if width else 100)

        lb_mas_info = Controles.LB(self, mas_info if mas_info else "").align_center()

        bt_aceptar = Controles.PB(self, _("Accept"), self.aceptar, plano=False).ponIcono(Iconos.AceptarPeque())
        bt_aceptar.setDefault(True)
        bt_cancelar = Controles.PB(self, _("Cancel"), self.reject, plano=False).ponIcono(Iconos.CancelarPeque())

        ly0 = Colocacion.H().relleno().control(lb_clave).control(field).relleno()
        ly = Colocacion.V().otro(ly0).control(lb_mas_info)

        ly_bt = Colocacion.H().relleno().control(bt_aceptar).relleno().control(bt_cancelar).relleno()

        layout = Colocacion.V().otro(ly).otro(ly_bt)
        self.setLayout(layout)

        field.setFocus()
        if in_cursor:
            pos = QtGui.QCursor().pos()
            self.show()
            self.move(pos)

    def aceptar(self):
        txt = self.cb_clave.currentText() if self.with_list_values else self.ed_clave.texto()
        self.resultado = txt.strip()
        self.accept()


def read_simple(owner, title, label, value, mas_info=None, width=None, in_cursor=False, li_values=None):
    v = SimpleWindow(owner, title, label, value, mas_info, width, in_cursor, li_values)
    if v.exec_():
        return v.resultado
    return None


def time_message(seconds):
    minutos = seconds // 60
    seconds = seconds % 60
    if minutos > 120:
        horas = minutos // 60
        lb_hr = _("hours")
        return f"{horas} {lb_hr}"
    elif minutos > 60:
        horas = minutos // 60
        minutos -= horas * 60
        lb_hr = _("hours") if horas > 1 else _("hour")
        lb_min = _("minutes") if minutos != 1 else _("minute")
        return f"{horas} {lb_hr}  {minutos} {lb_min}"

    elif minutos > 1:
        lb_min = _("minutes")
        return f"{minutos} {lb_min}"

    elif minutos == 1:
        lb_min = _("minute")
        lb_sec = _("seconds")
        return f"{minutos} {lb_min} {seconds} {lb_sec}"

    else:
        lb_sec = _("seconds")
        return f"{seconds} {lb_sec}"
