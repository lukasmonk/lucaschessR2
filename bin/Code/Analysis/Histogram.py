import math
import os

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Util
from Code.Base import Game
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.QT import SelectFiles


def escala_logaritmica(total_height, score):
    # Convertimos 0...30 en 0...10
    # La mitad de altura = 10
    assert -30 <= score <= 30
    v = 6.705 * math.log10(abs(score) + 1.0)
    mid = total_height / 2
    factor = 1.0 if score < 0 else -1.0
    return -(mid - v * mid * factor / 10)


class HSerie:
    def __init__(self):
        self.liPoints = []
        self.minimum = -30.0
        self.maximum = +30.0
        self.qcolor = {True: QtGui.QColor("#DACA99"), False: QtGui.QColor("#83C5F8")}

        # Elo para que 3400 - 1000 esten en los limites interiores
        self.maximum_elo = 3600
        self.minimum_elo = 0

    def addPoint(self, hpoint):
        hpoint.setGridPos(len(self.liPoints))
        self.liPoints.append(hpoint)

    def firstmove(self):
        return int(self.liPoints[0].nummove) if self.liPoints else 0

    def lastmove(self):
        return int(self.liPoints[-1].nummove) if self.liPoints else 0

    def lines(self):
        li = []
        for n in range(len(self.liPoints) - 1):
            li.append((self.liPoints[n], self.liPoints[n + 1]))
        return li

    def steps(self):
        return int(self.lastmove() - self.firstmove() + 1)

    def scenePoints(self, sz_width, sz_height, sz_left):
        ntotal_y = self.maximum - self.minimum
        self.factor = sz_height * 1.0 / ntotal_y
        ntotal_y_elo = self.maximum_elo - self.minimum_elo
        self.factor_elo = sz_height * 1.0 / ntotal_y_elo
        firstmove = self.firstmove()
        self.step = sz_width * 1.0 / self.steps()
        nmedia_x = len(self.liPoints) / 2
        for npoint, point in enumerate(self.liPoints):
            point.minmax_rvalue(self.minimum, self.maximum)
            dr = ("s" if point.value > 0 else "n") + ("e" if npoint < nmedia_x else "w")
            point.set_dir_tooltip(dr)
            rx = (point.nummove - firstmove) * self.step - sz_left
            ry = escala_logaritmica(sz_height, point.rvalue)

            ry_elo = -(point.elo - self.minimum_elo) * self.factor_elo
            point.set_rxy(rx, ry, ry_elo)


class HPoint:
    def __init__(self, nummove, value, lostp, lostp_abs, tooltip, elo):
        self.nummove = nummove
        self.rvalue = self.value = value
        self.tooltip = tooltip
        self.is_white = "..." not in tooltip
        self.dir_tooltip = ""
        self.rlostp = self.lostp = lostp
        self.lostp_abs = lostp_abs
        self.gridPos = None
        self.brush_color = self.setColor()
        self.elo = elo

    def setColor(self):
        # if self.lostp_abs > 80:
        #     return QtGui.QColor("#DC143C"), QtGui.QColor("#DC143C")
        if self.is_white:
            return QtCore.Qt.white, QtCore.Qt.black
        return QtCore.Qt.black, QtCore.Qt.black

    def setGridPos(self, grid_pos):
        self.gridPos = grid_pos

    def minmax_rvalue(self, minimum, maximum):
        if minimum > self.value:
            self.rvalue = minimum
        elif maximum < self.value:
            self.rvalue = maximum
        if self.rlostp > (maximum - minimum):
            self.rlostp = maximum - minimum

    def set_dir_tooltip(self, dr):
        self.dir_tooltip = dr

    def set_rxy(self, rx, ry, ry_elo):
        self.rx = rx
        self.ry = ry
        self.ry_elo = ry_elo

    def clone(self):
        return HPoint(self.nummove, self.value, self.lostp, self.lostp_abs, self.tooltip, self.elo)


class GraphPoint(QtWidgets.QGraphicsItem):
    def __init__(self, histogram, point, si_values):
        super(GraphPoint, self).__init__()

        self.histogram = histogram
        self.point = point

        self.setAcceptHoverEvents(True)

        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(2)

        self.tooltipping = False
        self.si_values = si_values

    def hoverLeaveEvent(self, event):
        self.histogram.hide_tooltip()
        self.tooltipping = False

    def hoverMoveEvent(self, event):
        if not self.tooltipping:
            self.tooltipping = True
            ry = self.point.ry if self.si_values else self.point.ry_elo
            self.histogram.show_tooltip(self.point.tooltip, self.point.rx, ry, self.point.dir_tooltip)
            self.tooltipping = False

    def ponPos(self):
        ry = self.point.ry if self.si_values else self.point.ry_elo
        self.setPos(self.point.rx + 4, ry + 4)

    def boundingRect(self):
        return QtCore.QRectF(-6, -6, 6, 6)

    def paint(self, painter, option, widget):
        brush, color = self.point.brush_color
        painter.setPen(color)
        painter.setBrush(QtGui.QBrush(brush))
        painter.drawEllipse(-6, -6, 6, 6)

    def mousePressEvent(self, event):
        self.histogram.dispatch(self.point.gridPos)

    def mouseDoubleClickEvent(self, event):
        self.histogram.dispatch_enter(self.point.gridPos)


class GraphToolTip(QtWidgets.QGraphicsItem):
    def __init__(self, graph):
        super(GraphToolTip, self).__init__()

        self.graph = graph
        self.texto = ""

        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(2)

    def setDispatch(self, dispatch):
        self.dispatch = dispatch

    def set_textPos(self, txt, x, y, dr):
        self.font = self.scene().font()
        self.font.setPointSize(12)
        self.metrics = QtGui.QFontMetrics(self.font)

        self.texto = txt
        self.dr = dr
        self.x = x
        self.y = y
        rancho = self.metrics.width(self.texto) + 10
        ralto = self.metrics.height() + 12

        rx = 10 if "e" in self.dr else -rancho
        ry = -ralto if "n" in self.dr else +ralto

        self.xrect = QtCore.QRectF(rx, ry, rancho, ralto)

        if "w" in self.dr:
            x -= 10
        if "n" in self.dr:
            y -= 10

        self.setPos(x, y)
        self.show()

    def boundingRect(self):
        return self.xrect

    def paint(self, painter, option, widget):
        painter.setFont(self.font)
        painter.setPen(QtGui.QColor("#545454"))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#F1EDED")))
        painter.drawRect(self.xrect)
        painter.drawText(self.xrect, QtCore.Qt.AlignCenter, self.texto)


class Histogram(QtWidgets.QGraphicsView):
    def __init__(self, owner, hserie, grid, ancho, si_values, elo_medio=None):
        super(Histogram, self).__init__()

        self.hserie = hserie

        self.owner = owner
        self.grid = grid

        self.elo_medio = elo_medio

        self.steps = hserie.steps()
        self.step = ancho / self.steps

        sz_width = self.steps * self.step
        sz_height = sz_left = ancho * 300 / 900

        scene = QtWidgets.QGraphicsScene(self)
        scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        scene.setSceneRect(-sz_height, -sz_height, sz_width, sz_height)
        self.setScene(scene)
        self.scene = scene
        # self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        hserie.scenePoints(sz_width, sz_height, sz_left)

        self.si_values = si_values

        for point in hserie.liPoints:
            node = GraphPoint(self, point, si_values)
            scene.addItem(node)
            node.ponPos()

        self.pointActive = 0

        self.tooltip = GraphToolTip(self)
        scene.addItem(self.tooltip)
        self.tooltip.hide()

        # self.scale(0.9, 0.8)

        self.setPointActive(0)

    def dispatch(self, grid_pos):
        self.grid.goto(grid_pos, 0)
        self.grid.setFocus()

    def setPointActive(self, num):
        self.pointActive = num
        self.scene.invalidate()

    def dispatch_enter(self, grid_pos):
        self.grid.setFocus()
        self.owner.grid_doble_click(self.grid, grid_pos, 0)

    def show_tooltip(self, txt, x, y, dr):
        self.tooltip.set_textPos(txt, x, y, dr)

    def hide_tooltip(self):
        self.tooltip.hide()

    def drawBackground(self, painter, rect):
        sr = scene_rect = self.sceneRect()
        width = sr.width()
        height = sr.height()
        left = sr.left()
        right = sr.right()
        top = sr.top()
        bottom = sr.bottom()
        serie = self.hserie

        firstmove = self.hserie.firstmove()

        painter.setBrush(QtCore.Qt.NoBrush)

        text_rect = QtCore.QRectF(left - 2, bottom + 4, width + 2, height)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        njg = self.steps + 1
        step = self.step

        # Numeros de move, en dos lineas
        for x in range(njg - 1):
            num = firstmove + x
            decimal = num // 10
            if decimal:
                painter.drawText(text_rect.translated(x * step, 0), str(decimal))
        for x in range(njg - 1):
            num = firstmove + x
            ent = num % 10
            painter.drawText(text_rect.translated(x * step, 12), str(ent))

        # Lineas verticales de referencia
        painter.setPen(QtGui.QColor("#D9D9D9"))
        for x in range(1, njg - 1):
            t = left + step * x
            painter.drawLine(t, top, t, bottom)

        # Eje de las y a la izquierda
        painter.setPen(QtGui.QColor("#545454"))
        align_right = QtCore.Qt.AlignRight
        h = 12
        x = left - 10
        w = 24
        if self.si_values:
            coord = [-15, -8, -4, -2, -0.8, 0, 0.8, +2, +4, +8, +15]
            plant = "%+0.1f"
            for d in coord:
                y = escala_logaritmica(height, d) - height / 42
                painter.drawText(x - 30, y, w + 10, h, align_right, plant % d)

            # Linea de referencia en la mitad-horizontal
            painter.setPen(QtCore.Qt.black)
            t = top + height * 0.50
            painter.drawLine(left, t, right, t)

            # Lineas referencia horizontal
            painter.setPen(QtGui.QColor("#D9D9D9"))
            for pos, d in enumerate(coord):
                if d:
                    t = escala_logaritmica(height, d)
                    painter.drawLine(left, t, right, t)

        else:
            coord = range(0, 3800, 200)
            for n, d in enumerate(coord):
                y = bottom - height * d / 3600 - height / 42
                rot = str(d)
                painter.drawText(x - 120, y, w + 100, h, align_right, rot)

            # Lineas referencia horizontal
            painter.setPen(QtGui.QColor("#D9D9D9"))
            for pos, d in enumerate(coord):
                if d:
                    t = bottom - height * d / 3600
                    painter.drawLine(left, t, right, t)

        # Barras de los puntos perdidos
        if self.owner.valorShowLostPoints():
            n = max(serie.step / 2.0 - 2, 4) / 2.0
            color = QtGui.QColor("#FFCECE")
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(color)
            for p in serie.liPoints:
                if p.rlostp:
                    y = bottom - p.rlostp * serie.factor
                    rect = QtCore.QRectF(p.rx - n, bottom - 1, n * 2, y)
                    painter.drawRect(rect)
                    p.rect_lost = rect

            painter.setBrush(QtGui.QBrush())

        # Lineas que unen los puntos
        pen = painter.pen()
        pen.setWidth(4)
        if self.si_values:
            for is_white in (True, False):
                pen.setColor(serie.qcolor[is_white])
                painter.setPen(pen)
                for p, p1 in serie.lines():
                    if p.is_white == is_white:
                        ry = p.ry
                        ry1 = p1.ry
                        painter.drawLine(p.rx + 1, ry, p1.rx, ry1)

        else:
            for is_white in (True, False):
                pen.setColor(serie.qcolor[is_white])
                painter.setPen(pen)
                previous = None
                next1 = None
                for p, p1 in serie.lines():
                    if p.is_white == is_white:
                        if previous:
                            painter.drawLine(previous.rx + 1, previous.ry_elo, p.rx, p.ry_elo)
                        previous = p
                    if p1:
                        next1 = p1

                if next1 and next1.is_white == is_white:
                    painter.drawLine(previous.rx + 1, previous.ry_elo, next1.rx, next1.ry_elo)

        painter.setBrush(QtGui.QBrush())

        # Caja exterior
        pen = painter.pen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor("#545454"))
        painter.setPen(pen)
        painter.drawRect(scene_rect)

        # Linea roja de la position actual
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor("#DE5044"))
        painter.setPen(pen)
        if 0 <= self.pointActive < len(self.hserie.liPoints):
            p = serie.liPoints[self.pointActive]
            painter.drawLine(p.rx, bottom, p.rx, top)

    def mousePressEvent(self, event):
        super(Histogram, self).mousePressEvent(event)
        ep = self.mapToScene(event.pos())
        if self.owner.valorShowLostPoints():
            for p in self.hserie.liPoints:
                if p.rlostp:
                    if p.rect_lost.contains(ep):
                        self.dispatch(p.gridPos)
        if event.button() == QtCore.Qt.RightButton:
            menu = QTVarios.LCMenu(self)
            menu.opcion("clip", _("Copy to clipboard"), Iconos.Clipboard())
            menu.separador()
            menu.opcion("file", _("Save") + " png", Iconos.GrabarFichero())
            resp = menu.lanza()
            if resp:
                pm = self.grab()
                if resp == "clip":
                    QTUtil.set_clipboard(pm, tipo="p")
                else:
                    configuration = Code.configuration
                    path = SelectFiles.salvaFichero(self, _("File to save"), configuration.save_folder(), "png", False)
                    if path:
                        pm.save(path, "png")
                        configuration.set_save_folder(os.path.dirname(path))

    def mouseDoubleClickEvent(self, event):
        super(Histogram, self).mouseDoubleClickEvent(event)
        ep = self.mapToScene(event.pos())
        for p in self.hserie.liPoints:
            if p.rlostp:
                if p.rect_lost.contains(ep):
                    self.dispatch_enter(p.gridPos)

    def wheelEvent(self, event):
        k = QtCore.Qt.Key_Left if event.delta() > 0 else QtCore.Qt.Key_Right
        self.owner.grid_tecla_control(self.grid, k, False, False, False)


def gen_histograms(game: Game.Game):
    hgame = HSerie()
    hwhite = HSerie()
    hblack = HSerie()

    lijg = []
    lijg_w = []
    lijg_b = []

    porc_t = 0
    porc_w = 0
    porc_b = 0

    if not game.is_fen_initial():
        pos_inicial = (game.first_position.num_moves-1)*2
        if game.starts_with_black:
            pos_inicial += 1
    else:
        pos_inicial = 0

    for num, move in enumerate(game.li_moves, pos_inicial):
        if move.analysis:
            mrm, pos = move.analysis
            is_white = move.is_white()
            pts = mrm.li_rm[pos].centipawns_abs()
            pts0 = mrm.li_rm[0].centipawns_abs()
            move.lostp_abs = lostp_abs = pts0 - pts

            porc = move.porcentaje = 100 - lostp_abs if lostp_abs < 100 else 0
            porc_t += porc

            lijg.append(move)
            if is_white:
                lijg_w.append(move)
                porc_w += porc
            else:
                pts = -pts
                pts0 = -pts0
                lijg_b.append(move)
                porc_b += porc

            pts /= 100.0
            pts0 /= 100.0
            lostp = abs(pts0 - pts)

            nj = num / 2.0 + 1.0
            label = "%d." % int(nj)
            if not is_white:
                label += ".."
            move.xnum = label
            label += move.pgn_translated()

            move.xsiW = is_white

            tooltip = label + " %+0.02f" % pts
            if lostp:
                tooltip += "  ↓%0.02f" % lostp

            avg = move.elo_avg if hasattr(move, "elo_avg") else 0
            # tooltip += " (%d)" % avg
            hp = HPoint(nj, pts, lostp, lostp_abs, tooltip, avg)
            hgame.addPoint(hp)
            if is_white:
                hwhite.addPoint(hp.clone())
            else:
                hblack.addPoint(hp.clone())

    alm = Util.Record()
    alm.hgame = hgame
    alm.hwhite = hwhite
    alm.hblack = hblack

    alm.lijg = lijg
    alm.lijgW = lijg_w
    alm.lijgB = lijg_b

    alm.porcT = porc_t * 1.0 / len(lijg) if len(lijg) else 0
    alm.porcW = porc_w * 1.0 / len(lijg_w) if len(lijg_w) else 0
    alm.porcB = porc_b * 1.0 / len(lijg_b) if len(lijg_b) else 0

    return alm
