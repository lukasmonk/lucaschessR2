import base64

from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil


class PhysicalPos:
    def __init__(self, x=0, y=0, ancho=0, alto=0, angulo=0, orden=15):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.angulo = angulo
        self.orden = int(orden)

    def copia(self):
        p = PhysicalPos(self.x, self.y, self.ancho, self.alto, self.angulo, self.orden)
        return p

    def __str__(self):
        txt = ""
        for var in ("x", "y", "ancho", "alto", "angulo", "orden"):
            txt += "%s : %s\n" % (var, str(getattr(self, var)))
        return txt

    def save_dic(self):
        dic = {}
        for var in ("x", "y", "ancho", "alto", "angulo", "orden"):
            dic[var] = getattr(self, var)
        return dic

    def restore_dic(self, dic):
        for var in ("x", "y", "ancho", "alto", "angulo", "orden"):
            setattr(self, var, dic[var])


class FontType:
    def __init__(self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False):
        self.name = name
        self.puntos = puntos
        self.peso = peso  # 50 = normal, 75 = negrita, 25 = light,...
        self.is_italic = is_italic
        self.is_underlined = is_underlined
        self.is_striked = is_striked

    def __str__(self):
        cursiva = 1 if self.is_italic else 0
        subrayado = 1 if self.is_underlined else 0
        tachado = 1 if self.is_striked else 0
        name = self.name
        if not name:
            name = QtGui.QFont().defaultFamily()
        return "%s,%d,-1,5,%d,%d,%d,%d,0,0" % (name, self.puntos, self.peso, cursiva, subrayado, tachado)

    def copia(self):
        t = FontType(self.name, self.puntos, self.peso, self.is_italic, self.is_underlined, self.is_striked)
        return t

    def save_dic(self):
        dic = {}
        for var in ("name", "puntos", "peso", "is_italic", "is_underlined", "is_striked"):
            dic[var] = getattr(self, var)
        return dic

    def restore_dic(self, dic):
        for var in ("name", "puntos", "peso", "is_italic", "is_underlined", "is_striked"):
            setattr(self, var, dic[var])


class Bloque:
    name: str
    ordenVista: int
    tipo: int

    def __init__(self, li_vars, dic=None):
        self.siMovible = True
        li_vars.append(("name", "c", ""))
        li_vars.append(("ordenVista", "n", 1))
        self.li_vars = li_vars
        for num, dato in enumerate(self.li_vars):
            var, tipo, ini = dato
            setattr(self, var, ini)
            self.li_vars[num] = (var, tipo)
        if dic:
            self.restore_dic(dic)

    def tipoqt(self):
        return {
            1: QtCore.Qt.SolidLine,
            2: QtCore.Qt.DashLine,
            3: QtCore.Qt.DotLine,
            4: QtCore.Qt.DashDotLine,
            5: QtCore.Qt.DashDotDotLine,
            0: QtCore.Qt.NoPen,
        }.get(self.tipo, QtCore.Qt.SolidLine)

    def __str__(self):
        txt = ""
        for var, tipo in self.li_vars:
            txt += "%s : %s\n" % (var, str(getattr(self, var)))
        return txt

    def save_dic(self):
        dic = {}
        for var, tipo in self.li_vars:
            value = getattr(self, var)
            if var == "png":
                if not value:
                    value = b""
                else:
                    value = base64.encodebytes(value)
            dic[var] = value.save_dic() if tipo == "o" else value
        dic["ordenVista"] = self.ordenVista
        return dic

    def restore_dic(self, dic):

        # Recuperando error de la anterior version
        if type(dic) != dict:
            if hasattr(dic, "save_dic"):
                dic = dic.save_dic()
            else:
                return

        for var, tipo in self.li_vars:
            if var in dic:
                value = dic[var]
                if tipo == "o":
                    xvar = getattr(self, var)
                    xvar.restore_dic(value)
                else:
                    if var == "png":
                        if type(value) == str:
                            value = value.encode()
                        value = base64.decodebytes(value)
                    setattr(self, var, value)


class Texto(Bloque):
    font_type: FontType
    physical_pos: PhysicalPos
    alineacion: str
    colorTexto: int
    colorFondo: int
    valor: str

    def __init__(self):
        li_vars = [
            ("font_type", "o", FontType()),
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 16, 0)),
            ("alineacion", "t", "i"),
            ("colorTexto", "n", 0),
            ("colorFondo", "n", 0xFFFFFF),
            ("valor", "tn", ""),
        ]
        Bloque.__init__(self, li_vars)

    def copia(self):
        t = Texto()
        t.font_type = self.font_type.copia()
        t.physical_pos = self.physical_pos.copia()
        t.alineacion = self.alineacion
        t.colorTexto = self.colorTexto
        t.colorFondo = self.colorFondo
        t.valor = self.valor
        return t


class Imagen(Bloque):
    physical_pos: PhysicalPos
    pixmap: str

    def __init__(self):
        li_vars = [("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0)), ("pixmap", "t", None)]
        Bloque.__init__(self, li_vars)

    def copia(self):
        t = Imagen()
        t.physical_pos = self.physical_pos.copia()
        t.pixmap = self.pixmap
        return t


class Caja(Bloque):
    physical_pos: PhysicalPos
    color: int
    colorRelleno: int
    grosor: int
    redEsquina: int
    tipo: int

    def __init__(self):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0)),
            ("color", "n", 0),
            ("colorRelleno", "n", -1),
            ("grosor", "n", 1),
            ("redEsquina", "n", 0),
            ("tipo", "n", 1),  # 1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine, 0=NoPen
        ]
        Bloque.__init__(self, li_vars)

    def copia(self):
        c = Caja()
        c.physical_pos = self.physical_pos.copia()
        c.color = self.color
        c.colorRelleno = self.colorRelleno
        c.grosor = self.grosor
        c.redEsquina = self.redEsquina
        c.tipo = self.tipo
        return c


class Circulo(Bloque):
    physical_pos: PhysicalPos
    color: int
    colorRelleno: int
    grosor: int
    grados: int
    tipo: int

    def __init__(self):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0)),
            ("color", "n", 0),
            ("colorRelleno", "n", -1),
            ("grosor", "n", 1),
            ("grados", "n", 0),
            ("tipo", "n", 1),  # 1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine, 0=Sin borde
        ]
        Bloque.__init__(self, li_vars)


class Pieza(Bloque):
    physical_pos: PhysicalPos
    pieza: str
    row: int
    column: int

    def __init__(self):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 1, 0)),
            ("pieza", "t", "p"),
            ("row", "n", 1),
            ("column", "n", 1),
        ]
        Bloque.__init__(self, li_vars)


class Flecha(Bloque):
    physical_pos: PhysicalPos
    a1h8: str
    grosor: int
    altocabeza: int
    tipo: int
    destino: str
    width_square: int
    color: int
    colorinterior: int
    colorinterior2: int
    opacity: int
    redondeos: bool
    forma: str
    ancho: int
    vuelo: int
    descuelgue: int
    png: str

    def __init__(self, dic=None):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 1, 0)),
            ("a1h8", "c", "a1h8"),
            ("grosor", "n", 1),  # ancho del trazo
            ("altocabeza", "n", 15),  # alto de la cabeza
            ("tipo", "n", 1),  # 1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine
            ("destino", "t", "c"),  # c = centro, m = minimo
            ("width_square", "n", 1),
            ("color", "n", 0),
            ("colorinterior", "n", -1),  # si es cerrada
            ("colorinterior2", "n", -1),  # para el gradiente
            ("opacity", "n", 1.0),
            ("redondeos", "l", False),
            ("forma", "t", "a"),
            # a = abierta -> ,  c = cerrada la cabeza, 1 = poligono cuadrado,
            #                   2 = poligono 1 punto base, 3 = poligono 1 punto base cabeza
            ("ancho", "n", 10),  # ancho de la base de la arrow si es un poligono
            ("vuelo", "n", 5),  # ancho adicional en la base
            ("descuelgue", "n", 2),  # angulo de la base de la cabeza
            ("png", "c", ""),  # png para usar como boton
        ]
        Bloque.__init__(self, li_vars, dic=dic)

    def copia(self):
        c = Flecha()
        c.physical_pos = self.physical_pos.copia()
        c.a1h8 = self.a1h8
        c.grosor = self.grosor
        c.altocabeza = self.altocabeza
        c.tipo = self.tipo
        c.destino = self.destino
        c.width_square = self.width_square
        c.color = self.color
        c.colorinterior = self.colorinterior
        c.colorinterior2 = self.colorinterior2
        c.opacity = self.opacity
        c.redondeos = self.redondeos
        c.forma = self.forma
        c.ancho = self.ancho
        c.vuelo = self.vuelo
        c.descuelgue = self.descuelgue
        c.png = getattr(self, "png", "")
        return c


class Marco(Bloque):
    physical_pos: PhysicalPos
    a1h8: str
    color: int
    colorinterior: int
    colorinterior2: int
    grosor: int
    redEsquina: int
    tipo: int
    opacity: int
    width_square: int
    png: str

    def __init__(self, dic=None):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0)),
            ("a1h8", "c", "a1h8"),
            ("color", "n", 0),
            ("colorinterior", "n", -1),
            ("colorinterior2", "n", -1),  # para el gradiente
            ("grosor", "n", 1),
            ("redEsquina", "n", 0),
            ("tipo", "n", 1),  # 1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine, 0=Sin borde
            ("opacity", "n", 1.0),
            ("width_square", "n", 1),
            ("png", "c", ""),  # png para usar como boton
        ]
        Bloque.__init__(self, li_vars, dic=dic)


class Circle(Bloque):
    physical_pos: PhysicalPos
    a1h8: str
    color: int
    colorinterior: int
    colorinterior2: int
    grosor: int
    redEsquina: int
    tipo: int
    opacity: int
    width_square: int
    png: str

    def __init__(self, dic=None):
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0)),
            ("a1h8", "c", "a1h8"),
            ("color", "n", 0),
            ("colorinterior", "n", -1),
            ("colorinterior2", "n", -1),  # para el gradiente
            ("grosor", "n", 1),
            ("redEsquina", "n", 0),
            ("tipo", "n", 1),  # 1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine, 0=Sin borde
            ("opacity", "n", 1.0),
            ("width_square", "n", 1),
            ("png", "c", ""),  # png para usar como boton
        ]
        Bloque.__init__(self, li_vars, dic=dic)


class SVG(Bloque):
    physical_pos: PhysicalPos
    fa1h8: str
    xml: str
    opacity: int
    width_square: int
    psize: int
    png: str

    def __init__(self, dic=None):
        # orden por debajo de las piezas
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0, 9)),
            ("fa1h8", "c", "0.0,0.0,0.0,0.0"),
            # se indica en unidades de ancho de square, podra tener valores negativos para que se pueda mover
            # fuera de main_window
            ("xml", "c", ""),
            ("opacity", "n", 1.0),
            ("width_square", "n", 1),
            ("psize", "n", 100),  # ajustetama_o
            ("png", "c", ""),  # png para usar como boton
        ]
        Bloque.__init__(self, li_vars, dic=dic)


class Marker(Bloque):
    physical_pos: PhysicalPos
    fa1h8: str
    xml: str
    opacity: int
    width_square: int
    psize: int
    poscelda: int
    png: str

    def __init__(self, dic=None):
        # orden por debajo de las piezas
        li_vars = [
            ("physical_pos", "o", PhysicalPos(0, 0, 80, 80, 0, 9)),
            ("fa1h8", "c", "0.0,0.0,0.0,0.0"),
            # se indica en unidades de ancho de square, podra tener valores negativos
            # para que se pueda mover fuera de main_window
            ("xml", "c", ""),
            ("opacity", "n", 1.0),
            ("width_square", "n", 1),
            ("psize", "n", 100),  # % ajustetama_o
            ("poscelda", "n", 1),  # 0 = Up-Left 1 = Up-Right 2 = Down-Right 3 = Down-Left
            ("png", "c", ""),  # png para usar como boton
        ]
        Bloque.__init__(self, li_vars, dic=dic)


class Pizarra(QtWidgets.QWidget):
    def __init__(self, guion, board, ancho, edit_mode=False, with_continue=False):
        QtWidgets.QWidget.__init__(self, board)

        self.guion = guion
        self.tarea = None

        self.mensaje = Controles.EM(self).set_font_type(puntos=Code.configuration.x_sizefont_infolabels)

        self.pb = None
        self.chb = None
        self.bloqueada = False
        if edit_mode:
            self.chb = Controles.CHB(self, _("With continue button"), False).capture_changes(self, self.save)
            self.mensaje.capturaCambios(self.save)
        elif with_continue:
            self.pb = Controles.PB(self, _("Continue"), self.continuar, plano=False)
            self.bloqueada = True
            self.mensaje.read_only()
        else:
            self.mensaje.read_only()

        self.pbLeft = Controles.PB(self, "", self.go_left).ponIcono(Iconos.AnteriorF()).anchoFijo(24)
        self.pbRight = Controles.PB(self, "", self.go_right).ponIcono(Iconos.SiguienteF()).anchoFijo(24)
        self.pbDown = Controles.PB(self, "", self.go_down).ponIcono(Iconos.Abajo()).anchoFijo(24)
        self.pbClose = Controles.PB(self, "", self.borrar).ponIcono(Iconos.CancelarPeque()).anchoFijo(24)

        cajon = QtWidgets.QWidget(self)
        ly = Colocacion.H()
        ly.control(self.pbLeft).control(self.pbDown)
        ly.control(self.pbRight).control(self.pbClose).margen(0)
        if self.pb:
            ly.control(self.pb)
        if self.chb:
            ly.control(self.chb)
        cajon.setLayout(ly)
        # cajon.setFixedHeight(20)

        layout = Colocacion.V().control(self.mensaje).espacio(-6).control(cajon).margen(0)

        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.ToolTip)

        pos_tabl = board.pos()
        pos_tabl_global = board.mapToGlobal(pos_tabl)
        self.anchoTabl = board.width()
        self.anchoPizarra = ancho
        self.x = pos_tabl_global.x() - pos_tabl.x()
        self.y = pos_tabl_global.y() - pos_tabl.y()

        if self.guion.posPizarra == "R":
            self.go_right()
        elif self.guion.posPizarra == "L":
            self.go_left()
        else:
            self.go_down()

        if edit_mode:
            self.clearFocus()
            self.mensaje.setFocus()

    def show_lrd(self, left, right, down):
        self.pbRight.setVisible(right)
        self.pbLeft.setVisible(left)
        self.pbDown.setVisible(down)

    def go_down(self):
        y = self.y + self.anchoTabl
        self.setGeometry(self.x, y, self.anchoTabl, self.anchoPizarra)
        self.show_lrd(True, True, False)
        self.guion.posPizarra = "D"

    def go_right(self):
        x = self.x + self.anchoTabl
        self.setGeometry(x, self.y, self.anchoPizarra, self.anchoTabl)
        self.show_lrd(True, False, True)
        self.guion.posPizarra = "R"

    def go_left(self):
        x = self.x - self.anchoPizarra
        self.setGeometry(x, self.y, self.anchoPizarra, self.anchoTabl)
        self.show_lrd(False, True, True)
        self.guion.posPizarra = "L"

    def write(self, tarea):
        self.mensaje.ponHtml(tarea.texto())
        self.tarea = tarea
        if self.chb:
            ok = self.tarea.continuar()
            self.chb.set_value(False if ok is None else ok)

    def save(self):
        if not self.tarea:
            return
        self.tarea.texto(self.mensaje.html())
        if self.chb:
            self.tarea.continuar(self.chb.valor())
        self.guion.savedPizarra()

    def is_blocked(self):
        if self.bloqueada:
            QTUtil.refresh_gui()
        return self.bloqueada

    def continuar(self):
        self.bloqueada = False
        self.pb.hide()

    def mousePressEvent(self, event):
        m = int(event.modifiers())
        si_ctrl = (m & QtCore.Qt.ControlModifier) > 0
        if si_ctrl and event.button() == QtCore.Qt.LeftButton:
            self.guion.borrarPizarraActiva()

    def borrar(self):
        self.guion.borrarPizarraActiva()
