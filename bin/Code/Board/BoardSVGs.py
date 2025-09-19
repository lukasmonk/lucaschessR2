from PySide2 import QtCore, QtGui, QtWidgets, QtSvg

from Code.Board import BoardBlocks


class SVGSC(BoardBlocks.BloqueEspSC):
    def __init__(self, escena, bloqueImgSVG, routine_if_pressed=None, siEditando=False):

        super(SVGSC, self).__init__(escena, bloqueImgSVG)

        self.routine_if_pressed = routine_if_pressed
        self.routine_if_pressed_argum = None

        self.distBordes = 0.30 * bloqueImgSVG.width_square

        self.pixmap = QtSvg.QSvgRenderer(QtCore.QByteArray(bloqueImgSVG.xml.encode("utf-8")))

        self.physical_pos2xy()

        self.siMove = False
        self.tpSize = None

        self.siRecuadro = False
        if siEditando:
            self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.siRecuadro = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.siRecuadro = False
        self.update()

    def set_routine_if_pressed(self, rutina, carga):
        self.routine_if_pressed = rutina
        self.routine_if_pressed_argum = carga

    def reset(self):
        self.physical_pos2xy()
        bm = self.bloqueDatos
        self.pixmap = QtSvg.QSvgRenderer(QtCore.QByteArray(bm.xml.encode()))
        self.setOpacity(bm.opacity)
        self.setZValue(bm.physical_pos.orden)
        self.update()

    def set_a1h8(self, a1h8):
        self.bloqueDatos.a1h8 = a1h8
        self.physical_pos2xy()

    def physical_pos2xy(self):
        bm = self.bloqueDatos
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

    def coordinaPosicionOtro(self, otroSVG):
        bs = self.bloqueDatos
        bso = otroSVG.bloqueDatos

        xk = float(bs.width_square * 1.0 / bso.width_square)
        physical_pos = bs.physical_pos
        posiciono = bso.physical_pos
        physical_pos.x = int(posiciono.x * xk)
        physical_pos.y = int(posiciono.y * xk)
        physical_pos.ancho = int(posiciono.ancho * xk)
        physical_pos.alto = int(posiciono.alto * xk)

    def contain(self, p):
        p = self.mapFromScene(p)

        def distancia(p1, p2):
            t = p2 - p1
            return ((t.x()) ** 2 + (t.y()) ** 2) ** 0.5

        physical_pos = self.bloqueDatos.physical_pos
        dx = physical_pos.x
        dy = physical_pos.y
        ancho = physical_pos.ancho
        alto = physical_pos.alto

        self.rect = rect = QtCore.QRectF(dx, dy, ancho, alto)
        dicEsquinas = {"tl": rect.topLeft(), "tr": rect.topRight(), "bl": rect.bottomLeft(), "br": rect.bottomRight()}

        db = self.distBordes
        self.tpSize = None
        for k, v in dicEsquinas.items():
            if distancia(p, v) <= db:
                self.tpSize = k
                return True
        self.siMove = self.rect.contains(p)
        return self.siMove

    def name(self):
        return _("Image")

    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)
        p = event.scenePos()
        self.expX = p.x()
        self.expY = p.y()

    def mouse_press_ext(self, event):
        p = event.pos()
        p = self.mapFromScene(p)
        self.expX = p.x()
        self.expY = p.y()

    def mouseMoveEvent(self, event):
        event.ignore()
        if not (self.siMove or self.tpSize):
            return

        p = event.pos()
        p = self.mapFromScene(p)
        x = p.x()
        y = p.y()

        dx = x - self.expX
        dy = y - self.expY

        self.expX = x
        self.expY = y

        physical_pos = self.bloqueDatos.physical_pos
        if self.siMove:
            physical_pos.x += dx
            physical_pos.y += dy
        else:
            tp = self.tpSize
            if tp == "br":
                physical_pos.ancho += dx
                physical_pos.alto += dy
            elif tp == "bl":
                physical_pos.x += dx
                physical_pos.ancho -= dx
                physical_pos.alto += dy
            elif tp == "tr":
                physical_pos.y += dy
                physical_pos.ancho += dx
                physical_pos.alto -= dy
            elif tp == "tl":
                physical_pos.x += dx
                physical_pos.y += dy
                physical_pos.ancho -= dx
                physical_pos.alto -= dy

        self.escena.update()

    def mouseReleaseEvent(self, event):
        QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)
        if self.siActivo:
            if self.siMove or self.tpSize:
                self.escena.update()
                self.siMove = False
                self.tpSize = None
            self.activa(False)

        if self.routine_if_pressed:
            if self.routine_if_pressed_argum:
                self.routine_if_pressed(self.routine_if_pressed_argum)
            else:
                self.routine_if_pressed()

    def mouseReleaseExt(self):
        if self.siActivo:
            if self.siMove or self.tpSize:
                self.escena.update()
                self.siMove = False
                self.tpSize = None
            self.activa(False)

    def pixmapX(self):
        bm = self.bloqueDatos

        p = bm.physical_pos

        p.x = 0
        p.y = 0
        p.ancho = 32
        ant_psize = bm.psize
        bm.psize = 100

        p.alto = p.ancho

        pm = QtGui.QPixmap(p.ancho + 1, p.ancho + 1)
        pm.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter()
        painter.begin(pm)
        self.paint(painter, None, None)
        painter.end()

        self.set_a1h8(bm.a1h8)
        bm.psize = ant_psize

        return pm

    def paint(self, painter, option, widget):
        bm = self.bloqueDatos

        physical_pos = bm.physical_pos
        dx = physical_pos.x - 1
        dy = physical_pos.y - 1
        ancho = physical_pos.ancho
        alto = physical_pos.alto

        psize = bm.psize
        if psize != 100:
            anchon = ancho * psize / 100
            dx += (ancho - anchon) / 2
            ancho = anchon
            alton = alto * psize / 100
            dy += (alto - alton) / 2
            alto = alton

        self.rect = rect = QtCore.QRectF(dx, dy, ancho, alto)

        self.pixmap.render(painter, rect)

        if self.siRecuadro:
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor("blue"))
            pen.setWidth(2)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)


class SVGCandidate(SVGSC):
    def physical_pos2xy(self):

        bm = self.bloqueDatos
        physical_pos = bm.physical_pos
        ac = self.board.width_square

        df, dc, hf, hc = self.board.a1h8_fc(bm.a1h8)

        if df > hf:
            df, hf = hf, df
        if dc > hc:
            dc, hc = hc, dc

        ancho = self.board.width_square * 0.3
        physical_pos.x = ac * (dc - 1)
        physical_pos.y = ac * (df - 1)

        posCuadro = bm.posCuadro
        if posCuadro == 1:
            physical_pos.x += ac - ancho
        elif posCuadro == 2:
            physical_pos.y += ac - ancho
        elif posCuadro == 3:
            physical_pos.y += ac - ancho
            physical_pos.x += ac - ancho

        physical_pos.ancho = ancho
        physical_pos.alto = ancho
