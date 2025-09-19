from PySide2 import QtCore, QtGui, QtWidgets

from Code.Board import BoardBlocks, BoardTypes


class DoubleBoxesSC(BoardBlocks.BloqueEspSC):
    expX: float
    expY: float

    def __init__(self, escena, bloque_flecha, routine_if_pressed=None):

        super(DoubleBoxesSC, self).__init__(escena, bloque_flecha)

        self.routine_if_pressed = routine_if_pressed
        self.routine_if_pressed_argum = None

        self.distBordes = 0.20 * bloque_flecha.width_square

        self.siMove = False
        self.tpSize = None

        self.bloquebox_from = BoardTypes.Marco()
        self.bloquebox_from.restore_dic(bloque_flecha.save_dic())
        self.bloquebox_from.a1h8 = bloque_flecha.a1h8[:2] * 2
        self.bloquebox_from.grosor = 0
        self.bloquebox_from.tipo = 0
        self.bloquebox_from.opacity = bloque_flecha.opacity * 0.7
        if self.bloquebox_from.colorinterior == -1:
            self.bloquebox_from.colorinterior = bloque_flecha.color

        self.bloquebox_to = BoardTypes.Marco()
        self.bloquebox_to.restore_dic(bloque_flecha.save_dic())
        self.bloquebox_to.a1h8 = bloque_flecha.a1h8[2:4] * 2
        self.bloquebox_to.grosor = 0
        self.bloquebox_to.tipo = 0
        if self.bloquebox_to.colorinterior == -1:
            self.bloquebox_to.colorinterior = bloque_flecha.color

        self.physical_pos2xy()

    def set_routine_if_pressed(self, rutina, carga):
        self.routine_if_pressed = rutina
        self.routine_if_pressed_argum = carga

    def reset(self):
        self.physical_pos2xy()
        bm = self.bloqueDatos
        self.setOpacity(bm.opacity)
        self.setZValue(bm.physical_pos.orden)
        self.update()

    def physical_pos2xy_bm(self, bm):
        physical_pos = bm.physical_pos
        ac = self.board.width_square
        tf = self.board.tamFrontera

        df, dc, hf, hc = self.board.a1h8_fc(bm.a1h8)

        if df > hf:
            df, hf = hf, df
        if dc > hc:
            dc, hc = hc, dc

        physical_pos.x = ac * (dc - 1) + tf / 2
        physical_pos.y = ac * (df - 1) + tf / 2
        physical_pos.ancho = (hc - dc + 1) * ac
        physical_pos.alto = (hf - df + 1) * ac

    def physical_pos2xy(self):
        self.physical_pos2xy_bm(self.bloquebox_from)
        self.physical_pos2xy_bm(self.bloquebox_to)

    def xy2physical_pos_bm(self, bm):
        physical_pos = bm.physical_pos
        ac = self.board.width_square
        tf = self.board.tamFrontera

        def f(xy):
            return int(round(float(xy) / float(ac), 0))

        dc = f(physical_pos.x - tf / 2) + 1
        df = f(physical_pos.y - tf / 2) + 1
        hc = f(physical_pos.x + physical_pos.ancho)
        hf = f(physical_pos.y + physical_pos.alto)

        def bien(fc):
            return (fc < 9) and (fc > 0)

        if bien(dc) and bien(df) and bien(hc) and bien(hf):
            bm.a1h8 = self.board.fc_a1h8(df, dc, hf, hc)

        self.physical_pos2xy_bm(bm)

    def xy2physical_pos(self):
        self.xy2physical_pos_bm(self.bloquebox_from)
        self.xy2physical_pos_bm(self.bloquebox_to)

    def set_a1h8(self, a1h8):
        self.bloqueDatos.a1h8 = a1h8
        self.bloquebox_from.a1h8 = a1h8[:2] * 2
        self.bloquebox_to.a1h8 = a1h8[2:4] * 2
        self.physical_pos2xy()

    @staticmethod
    def name():
        return _("Box")

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)
        self.mouse_press_ext(event)

        p = event.scenePos()
        self.expX = p.x()
        self.expY = p.y()

    def mouse_press_ext(self, event):
        """Needed in Scripts"""
        p = event.pos()
        p = self.mapFromScene(p)
        self.expX = p.x()
        self.expY = p.y()

    def paint_bm(self, bm, painter, option, widget):
        painter.setOpacity(bm.opacity)
        xk = float(self.board.width_square / 32.0)

        physical_pos = bm.physical_pos
        dx = physical_pos.x - 1
        dy = physical_pos.y - 1
        ancho = physical_pos.ancho
        alto = physical_pos.alto

        rect = QtCore.QRectF(dx, dy, ancho, alto)

        color = QtGui.QColor(bm.color)
        pen = QtGui.QPen()
        pen.setWidth(int(bm.grosor * xk))
        pen.setColor(color)
        pen.setStyle(bm.tipoqt())
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)

        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(bm.color))
        pen.setWidth(int(bm.grosor * xk))
        pen.setStyle(bm.tipoqt())
        painter.setPen(pen)
        if bm.colorinterior >= 0:
            color = QtGui.QColor(bm.colorinterior)
            if bm.colorinterior2 >= 0:
                color2 = QtGui.QColor(bm.colorinterior2)
                gradient = QtGui.QLinearGradient(0, 0, bm.physical_pos.ancho, bm.physical_pos.alto)
                gradient.setColorAt(0.0, color)
                gradient.setColorAt(1.0, color2)
                painter.setBrush(QtGui.QBrush(gradient))
            else:
                painter.setBrush(color)

        if bm.redEsquina:
            red = int(bm.redEsquina * xk)
            painter.drawRoundedRect(rect, red, red)
        else:
            painter.drawRect(rect)

    def paint(self, painter, option, widget):
        self.paint_bm(self.bloquebox_from, painter, option, widget)
        self.paint_bm(self.bloquebox_to, painter, option, widget)

    def boundingRect(self):
        physical_pos = self.bloquebox_from.physical_pos
        dx_from = physical_pos.x - 1
        dy_from = physical_pos.y - 1

        physical_pos = self.bloquebox_to.physical_pos
        dx_to = physical_pos.x - 1
        dy_to = physical_pos.y - 1

        dx = dx_from if dx_from < dx_to else dx_to
        dy = dy_from if dy_from < dy_to else dy_to
        ancho = abs(dx_from - dx_to) + physical_pos.ancho
        alto = abs(dy_from - dy_to) + physical_pos.alto
        self.rect = QtCore.QRectF(dx, dy, ancho, alto)
        x = self.bloqueDatos.grosor
        return QtCore.QRectF(self.rect).adjusted(-x, -x, x * 2, x * 2)
