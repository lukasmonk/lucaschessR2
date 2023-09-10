# import datetime
from PySide2 import QtCore, QtGui, QtWidgets


class ED(QtWidgets.QLineEdit):
    """
    Control de entrada de texto en una linea.
    """

    def __init__(self, parent, texto=None):
        """
        @param parent: ventana propietaria.
        @param texto: texto inicial.
        """
        if texto:
            QtWidgets.QLineEdit.__init__(self, texto, parent)
        else:
            QtWidgets.QLineEdit.__init__(self, parent)
        self.parent = parent

        self.decimales = 1

        self.menu = None

    def read_only(self, sino):
        self.setReadOnly(sino)
        return self

    def password(self):
        self.setEchoMode(QtWidgets.QLineEdit.Password)
        return self

    def set_disabled(self, sino):
        self.setDisabled(sino)
        return self

    def capture_enter(self, rutina):
        self.returnPressed.connect(rutina)
        return self

    def capture_changes(self, rutina):
        self.textEdited.connect(rutina)
        return self

    def set_text(self, texto):
        self.setText(texto)

    def texto(self):
        txt = self.text()
        return txt

    def align_center(self):
        self.setAlignment(QtCore.Qt.AlignHCenter)
        return self

    def align_right(self):
        self.setAlignment(QtCore.Qt.AlignRight)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def anchoMaximo(self, px):
        self.setMaximumWidth(px)
        return self

    def caracteres(self, num):
        self.setMaxLength(num)
        self.numCaracteres = num
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def controlrx(self, regexpr):
        rx = QtCore.QRegExp(regexpr)
        validator = QtGui.QRegExpValidator(rx, self)
        self.setValidator(validator)
        return self

    # def invalid_characters(self, c_invalid):
    #     def validador(x):
    #         for c in x:
    #             if c in c_invalid:
    #                 return False
    #         return True
    #
    #     self.setValidator(validador)
    #     return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def tipoFloat(self, valor: float = 0.0, from_sq: float = -36000.0, to_sq: float = 36000.0, decimales: int = None):
        """
        Valida los caracteres suponiendo que es un tipo decimal con unas condiciones
        @param valor: valor inicial
        @param from_sq: valor minimo
        @param to_sq: valor maximo
        @param decimales: num. decimales
        """
        if from_sq is None:
            self.setValidator(QtGui.QDoubleValidator(self))
        else:
            if decimales is None:
                decimales = self.decimales
            else:
                self.decimales = decimales
            self.setValidator(QtGui.QDoubleValidator(from_sq, to_sq, decimales, self))
        self.setAlignment(QtCore.Qt.AlignRight)
        self.ponFloat(valor)
        return self

    def ponFloat(self, valor):
        fm = "%0." + str(self.decimales) + "f"
        self.set_text(fm % valor)
        return self

    def textoFloat(self):
        txt = self.text()
        if "," in txt:
            txt = txt.replace(",", ".")
        return round(float(txt), self.decimales) if txt else 0.0

    def tipoInt(self, valor=0):
        """
        Valida los caracteres suponiendo que es un tipo entero con unas condiciones
        @param valor: valor inicial
        """
        self.setValidator(QtGui.QIntValidator(self))
        self.setAlignment(QtCore.Qt.AlignRight)
        self.ponInt(valor)
        return self

    def tipoIntPositive(self, valor):
        self.controlrx("^[0-9]+$")
        self.ponInt(valor)
        self.align_right()
        return self

    def ponInt(self, valor):
        self.set_text(str(valor))
        return self

    def textoInt(self):
        txt = self.text()
        return int(txt) if txt else 0


class SB(QtWidgets.QSpinBox):
    """
    SpinBox: Entrada de numeros enteros, con control de incremento o reduccion
    """

    def __init__(self, parent, valor, from_sq, to_sq):
        """
        @param valor: valor inicial
        @param from_sq: limite inferior
        @param to_sq: limite superior
        """
        QtWidgets.QSpinBox.__init__(self, parent)
        self.setRange(from_sq, to_sq)
        self.setSingleStep(1)
        self.setValue(int(valor))

    def tamMaximo(self, px):
        self.setFixedWidth(px)
        return self

    def valor(self):
        return self.value()

    def set_value(self, valor):
        self.setValue(int(valor) if valor else 0)

    def capture_changes(self, rutina):
        self.valueChanged.connect(rutina)
        return self

    def ponFuente(self, font):
        self.setFont(font)
        return self


class CB(QtWidgets.QComboBox):
    """
    ComboBox : entrada de una lista de options = etiqueta,key[,icono]
    """

    def __init__(self, parent, li_options, valorInicial, extend_seek=False):
        """
        @param li_options: lista de (etiqueta,key)
        @param valorInicial: valor inicial
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self.rehacer(li_options, valorInicial)
        if extend_seek:
            self.setEditable(True)
            self.setInsertPolicy(self.NoInsert)

    def valor(self):
        return self.itemData(self.currentIndex())

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def rehacer(self, li_options, valorInicial):
        self.li_options = li_options
        self.clear()
        nindex = 0
        for n, opcion in enumerate(li_options):
            if len(opcion) == 2:
                etiqueta, key = opcion
                self.addItem(etiqueta, key)
            else:
                etiqueta, key, icono = opcion
                self.addItem(icono, etiqueta, key)
            if key == valorInicial:
                nindex = n
        self.setCurrentIndex(nindex)

    def set_value(self, valor):
        for n, opcion in enumerate(self.li_options):
            key = opcion[1]
            if key == valor:
                self.setCurrentIndex(n)
                break

    def set_width(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self

    def set_widthFijo(self, px):
        self.setFixedWidth(px)
        return self

    def set_widthMinimo(self):
        self.setSizeAdjustPolicy(self.AdjustToMinimumContentsLengthWithIcon)
        return self

    def capture_changes(self, rutina):
        self.currentIndexChanged.connect(rutina)
        return self

    def set_multiline(self, max_px):
        self.setFixedWidth(max_px)
        listView = QtWidgets.QListView()
        # Turn On the word wrap
        listView.setWordWrap(True)
        # set popup view widget into the combo box
        self.setView(listView)
        return self


class CHB(QtWidgets.QCheckBox):
    """
    CheckBox : entrada de una campo seleccionable
    """

    def __init__(self, parent, etiqueta, valorInicial):
        """
        @param etiqueta: label mostrado
        @param valorInicial: valor inicial : True/False
        """
        QtWidgets.QCheckBox.__init__(self, etiqueta, parent)
        self.setChecked(valorInicial)

    def set_value(self, si):
        self.setChecked(si)
        return self

    def valor(self):
        return self.isChecked()

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def capture_changes(self, owner, rutina):
        self.clicked.connect(rutina)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self


class LB(QtWidgets.QLabel):
    """
    Etiquetas de texto.
    """

    def __init__(self, parent, texto=None):
        """
        @param texto: texto inicial.
        """
        if texto:
            QtWidgets.QLabel.__init__(self, texto, parent)
        else:
            QtWidgets.QLabel.__init__(self, parent)

        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction | QtCore.Qt.TextSelectableByMouse)

    def set_text(self, texto):
        self.setText(texto)

    def texto(self):
        return self.text()

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def align_center(self):
        self.setAlignment(QtCore.Qt.AlignCenter)
        return self

    def align_right(self):
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        return self

    def anchoMaximo(self, px):
        self.setMaximumWidth(px)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def altoMinimo(self, px):
        self.setMinimumHeight(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def ponAlto(self, px):
        rec = self.geometry()
        rec.setHeight(px)
        self.setGeometry(rec)
        return self

    def alineaY(self, otroLB):
        rec = self.geometry()
        rec.setY(otroLB.geometry().y())
        self.setGeometry(rec)
        return self

    def ponImagen(self, pm):
        self.setPixmap(pm)
        return self

    def set_color_background(self, color):
        return self.set_background(color.name())

    def set_background(self, txt_color: str):
        self.setStyleSheet("QWidget { background-color: %s }" % txt_color)
        return self

    def set_color_foreground(self, color):
        return self.set_foreground(color.name())

    def set_foreground(self, txt_color: str):
        self.setStyleSheet("QWidget { color: %s }" % txt_color)
        return self

    def set_foreground_backgound(self, color, fondo):
        self.setStyleSheet("QWidget { color: %s; background-color: %s}" % (color, fondo))
        return self

    def set_wrap(self):
        self.setWordWrap(True)
        return self

    def set_width(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self


def LB2P(parent, texto):
    return LB(parent, texto + ": ")


class PB(QtWidgets.QPushButton):
    """
    Boton.
    """

    def __init__(self, parent, texto, rutina=None, plano=True):
        """
        @param parent: ventana propietaria, necesario para to_connect una rutina.
        @param texto: etiqueta inicial.
        @param rutina: rutina a la que se conecta el boton.
        """
        QtWidgets.QPushButton.__init__(self, texto, parent)
        self.w_parent = parent
        self.setFlat(plano)
        if rutina:
            self.to_connect(rutina)

    def ponIcono(self, icono, icon_size=16):
        self.setIcon(icono)
        self.setIconSize(QtCore.QSize(icon_size, icon_size))
        return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def cuadrado(self, px):
        self.setFixedSize(px, px)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def to_connect(self, rutina):
        self.clicked.connect(rutina)
        return self

    def set_background(self, txtFondo):
        self.setStyleSheet("QWidget { background: %s }" % txtFondo)
        return self

    def ponPlano(self, siPlano):
        self.setFlat(siPlano)
        return self

    def ponToolTip(self, txt):
        self.setToolTip(txt)
        return self

    def set_text(self, txt):
        self.setText(txt)


class RB(QtWidgets.QRadioButton):
    """
    RadioButton: lista de alternativas
    """

    def __init__(self, w_parent, texto, rutina=None):
        QtWidgets.QRadioButton.__init__(self, texto, w_parent)
        if rutina:
            self.clicked.connect(rutina)

    def activa(self, siActivar=True):
        self.setChecked(siActivar)
        return self


class GB(QtWidgets.QGroupBox):
    """
    GroupBox: Recuadro para agrupamiento de controles
    """

    def __init__(self, w_parent, texto, layout):
        QtWidgets.QGroupBox.__init__(self, texto, w_parent)
        self.setLayout(layout)
        self.w_parent = w_parent

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def align_center(self):
        self.setAlignment(QtCore.Qt.AlignHCenter)
        return self

    def to_connect(self, rutina):
        self.setCheckable(True)
        self.setChecked(False)
        self.clicked.connect(rutina)
        return self

    def set_text(self, text):
        self.setTitle(text)
        return self


class EM(QtWidgets.QTextEdit):
    """
    Control de entrada de texto en varias lineas.
    """

    def __init__(self, parent, texto=None, siHTML=True):
        """
        @param texto: texto inicial.
        """
        QtWidgets.QTextEdit.__init__(self, parent)
        self.parent = parent

        self.menu = None  # menu de contexto
        self.rutinaDobleClick = None

        self.setAcceptRichText(siHTML)

        if texto:
            if siHTML:
                self.setText(texto)
            else:
                self.insertPlainText(texto)

    def ponHtml(self, texto):
        self.setHtml(texto)
        return self

    def insertarHtml(self, texto):
        self.insertHtml(texto)
        return self

    def insertarTexto(self, texto):
        self.insertPlainText(texto)
        return self

    def read_only(self):
        self.setReadOnly(True)
        return self

    def texto(self):
        return self.toPlainText()

    def set_text(self, txt):
        self.setText("")
        self.insertarTexto(txt)

    def html(self):
        return self.toHtml()

    def set_width(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def altoMinimo(self, px):
        self.setMinimumHeight(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def set_wrap(self, siPoner):
        self.setWordWrapMode(QtGui.QTextOption.WordWrap if siPoner else QtGui.QTextOption.NoWrap)
        return self

    def capturaCambios(self, rutina):
        self.textChanged.connect(rutina)
        return self

    def capturaDobleClick(self, rutina):
        self.rutinaDobleClick = rutina
        return self

    def mouseDoubleClickEvent(self, event):
        if self.rutinaDobleClick:
            self.rutinaDobleClick(event)

    def position(self):
        return self.textCursor().position()


class Menu(QtWidgets.QMenu):
    """
    Menu popup.

    Ejemplo::

        menu = Controles.Menu(window)

        menu.opcion( "op1", "Primera opcion", icono )
        menu.separador()
        menu.opcion( "op2", "Segunda opcion", icono1 )
        menu.separador()

        menu1 = menu.submenu( "Submenu", icono2 )
        menu1.opcion( "op3_1", "opcion 1", icono3 )
        menu1.separador()
        menu1.opcion( "op3_2", "opcion 2", icono3 )
        menu1.separador()

        resp = menu.lanza()

        if resp:
            if resp == "op1":
                ..........

            elif resp == "op2":
                ................
    """

    def __init__(self, parent, titulo=None, icono=None, is_disabled=False, puntos=None, siBold=True):

        self.parent = parent
        QtWidgets.QMenu.__init__(self, parent)

        if titulo:
            self.setTitle(titulo)
        if icono:
            self.setIcon(icono)

        if is_disabled:
            self.setDisabled(True)

        if puntos:
            tl = TipoLetra(puntos=puntos, peso=75) if siBold else TipoLetra(puntos=puntos)
            self.setFont(tl)

        app = QtWidgets.QApplication.instance()
        style = app.style().metaObject().className()
        self.si_separadores = style != "QFusionStyle"

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def opcion(self, key, label, icono=None, is_disabled=False, tipoLetra=None, siChecked=False, toolTip: str = ""):
        if icono:
            accion = QtWidgets.QAction(icono, label, self)
        else:
            accion = QtWidgets.QAction(label, self)
        accion.key = key
        if is_disabled:
            accion.setDisabled(True)
        if tipoLetra:
            accion.setFont(tipoLetra)
        if siChecked is not None:
            accion.setCheckable(True)
            accion.setChecked(siChecked)
        if toolTip != "":
            accion.setToolTip(toolTip)

        self.addAction(accion)
        return accion

    def submenu(self, label, icono=None, is_disabled=False):
        menu = Menu(self, label, icono, is_disabled)
        menu.setFont(self.font())
        self.addMenu(menu)
        return menu

    def mousePressEvent(self, event):
        self.siIzq = event.button() == QtCore.Qt.LeftButton
        self.siDer = event.button() == QtCore.Qt.RightButton
        resp = QtWidgets.QMenu.mousePressEvent(self, event)
        return resp

    def separador(self):
        if self.si_separadores:
            self.addSeparator()

    def lanza(self):
        QtCore.QCoreApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        resp = self.exec_(QtGui.QCursor.pos())
        if resp:
            return resp.key
        else:
            return None


class TB(QtWidgets.QToolBar):
    """
    Crea una barra de tareas simple.

    @param li_acciones: lista de acciones, en forma de tupla = titulo, icono, key
    @param with_text: si muestra texto
    @param icon_size: tama_o del icono
    @param rutina: rutina que se llama al pulsar una opcion. Por defecto sera parent.process_toolbar().
        Y la key enviada se obtiene de self.sender().key
    """

    def __init__(self, parent, li_acciones, with_text=True, icon_size=32, rutina=None, puntos=None, background=None):

        QtWidgets.QToolBar.__init__(self, "BASIC", parent)

        self.setIconSize(QtCore.QSize(icon_size, icon_size))

        self.parent = parent

        self.rutina = parent.process_toolbar if rutina is None else rutina

        if with_text:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.f = TipoLetra(puntos=puntos) if puntos else None

        if background:
            self.setStyleSheet("QWidget { background: %s }" % background)

        self.ponAcciones(li_acciones)

    def ponAcciones(self, li_acciones):
        self.dic_toolbar = {}
        lista = []
        for datos in li_acciones:
            if datos:
                if type(datos) == int:
                    self.addWidget(LB("").anchoFijo(datos))
                else:
                    titulo, icono, key = datos
                    accion = QtWidgets.QAction(titulo, self.parent)
                    accion.setIcon(icono)
                    accion.setIconText(titulo)
                    accion.triggered.connect(self.rutina)
                    accion.key = key
                    if self.f:
                        accion.setFont(self.f)
                    lista.append(accion)
                    self.addAction(accion)
                    self.dic_toolbar[key] = accion
            else:
                self.addSeparator()
        self.li_acciones = lista

    def reset(self, li_acciones):
        self.clear()
        self.ponAcciones(li_acciones)
        self.update()

    def vertical(self):
        self.setOrientation(QtCore.Qt.Vertical)
        return self

    def set_action_visible(self, key, value):
        for accion in self.li_acciones:
            if accion.key == key:
                accion.setVisible(value)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            if hasattr(self.parent, "toolbar_rightmouse"):
                self.parent.toolbar_rightmouse()
                return
        QtWidgets.QToolBar.mousePressEvent(self, event)


class TBrutina(QtWidgets.QToolBar):
    """
    Crea una barra de tareas simple.

    @param li_acciones: lista de acciones, en forma de tupla = titulo, icono, key
    @param with_text: si muestra texto
    @param icon_size: tama_o del icono
        Y la key enviada se obtiene de self.sender().key
    """

    def __init__(
            self, parent, li_acciones=None, with_text=True, icon_size=None, puntos=None, background=None, style=None
    ):

        QtWidgets.QToolBar.__init__(self, "BASIC", parent)
        if style:
            self.setToolButtonStyle(style)
            if style != QtCore.Qt.ToolButtonTextUnderIcon and icon_size is None:
                icon_size = 16
        elif with_text:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        tam = 32 if icon_size is None else icon_size
        self.setIconSize(QtCore.QSize(tam, tam))

        self.parent = parent

        self.f = TipoLetra(puntos=puntos) if puntos else None

        if background:
            self.setStyleSheet("QWidget { background: %s }" % background)

        if li_acciones:
            self.ponAcciones(li_acciones)

        else:
            self.dic_toolbar = {}
            self.li_acciones = []

    def new(self, titulo, icono, key, sep=True, tool_tip=None):
        accion = QtWidgets.QAction(titulo, self.parent)
        accion.setIcon(icono)
        accion.setIconText(titulo)
        if tool_tip:
            accion.setToolTip(tool_tip)

        accion.triggered.connect(key)
        if self.f:
            accion.setFont(self.f)
        self.li_acciones.append(accion)
        self.addAction(accion)
        self.dic_toolbar[key] = accion
        if sep:
            self.addSeparator()

    def ponAcciones(self, liAcc):
        self.dic_toolbar = {}
        self.li_acciones = []
        for datos in liAcc:
            if datos:
                if type(datos) == int:
                    self.addWidget(LB("").anchoFijo(datos))
                elif len(datos) == 3:
                    titulo, icono, key = datos
                    self.new(titulo, icono, key, False)
                else:
                    titulo, icono, key, tool_tip = datos
                    self.new(titulo, icono, key, False, tool_tip=tool_tip)
            else:
                self.addSeparator()

    def reset(self, li_acciones):
        self.clear()
        self.ponAcciones(li_acciones)
        self.update()

    def vertical(self):
        self.setOrientation(QtCore.Qt.Vertical)
        return self

    def set_pos_visible(self, pos, value):
        self.li_acciones[pos].setVisible(value)

    def set_action_visible(self, key, value):
        accion = self.dic_toolbar.get(key, None)
        if accion:
            accion.setVisible(value)

    def set_action_enabled(self, key, value):
        accion = self.dic_toolbar.get(key, None)
        if accion:
            accion.setEnabled(value)

    def set_action_title(self, key, title):
        accion: QtWidgets.QAction
        accion = self.dic_toolbar.get(key, None)
        if accion:
            accion.setIconText(title)
            accion.setToolTip(title)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        QtWidgets.QToolBar.mousePressEvent(self, event)


class TipoLetra(QtGui.QFont):
    def __init__(self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None):
        QtGui.QFont.__init__(self)
        if txt is None:
            cursiva = 1 if is_italic else 0
            subrayado = 1 if is_underlined else 0
            tachado = 1 if is_striked else 0
            if not name:
                app = QtWidgets.QApplication.instance()
                font = app.font()
                name = font.family()
            txt = "%s,%d,-1,5,%d,%d,%d,%d,0,0" % (name, puntos, peso, cursiva, subrayado, tachado)
        self.fromString(txt)


class Tab(QtWidgets.QTabWidget):
    def new_tab(self, widget, texto, pos=None):
        if pos is None:
            self.addTab(widget, texto)
            pos = self.currentIndex()
        else:
            self.insertTab(pos, widget, texto)
        self.set_tooltip_x(pos, "")

    def set_tooltip_x(self, pos, txt):
        p = self.tabBar().tabButton(pos, QtWidgets.QTabBar.RightSide)
        if p:
            p.setToolTip(txt)

    def current_position(self):
        return self.currentIndex()

    def set_value(self, cual, valor):
        self.setTabText(cual, valor)

    def activa(self, cual):
        self.setCurrentIndex(cual)

    def set_position(self, pos):
        rpos = self.North
        if pos == "S":
            rpos = self.South
        elif pos == "E":
            rpos = self.East
        elif pos == "W":
            rpos = self.West
        self.setTabPosition(rpos)
        return self

    def ponIcono(self, pos, icono):
        if icono is None:
            icono = QtGui.QIcon()
        self.setTabIcon(pos, icono)

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(
            self, name="", puntos=8, peso=50, is_italic=False, is_underlined=False, is_striked=False, txt=None
    ):
        f = TipoLetra(name, puntos, peso, is_italic, is_underlined, is_striked, txt)
        self.setFont(f)
        return self

    def dispatchChange(self, dispatch):
        self.currentChanged.connect(dispatch)

    def quita_x(self, pos):
        self.tabBar().tabButton(pos, QtWidgets.QTabBar.RightSide).hide()

        # def formaTriangular( self ):
        # self.setTabShape(self.Triangular)


class SL(QtWidgets.QSlider):
    def __init__(self, parent, minimo, maximo, nvalor, dispatch, tick=10, step=1):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)

        self.setMinimum(minimo)
        self.setMaximum(maximo)

        self.dispatch = dispatch
        if tick:
            self.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.setTickInterval(tick)
        self.setSingleStep(step)

        self.setValue(nvalor)

        self.valueChanged.connect(self.movido)

    def set_value(self, nvalor):
        self.setValue(nvalor)
        return self

    def movido(self, valor):
        if self.dispatch:
            self.dispatch()

    def valor(self):
        return self.value()

    def set_width(self, px):
        self.setFixedWidth(px)
        return self

    # class PRB(QtWidgets.QProgressBar):
    # def __init__(self, minimo, maximo):
    # QtWidgets.QProgressBar.__init__(self)
    # self.setMinimum(minimo)
    # self.setMaximum(maximo)

    # def ponFormatoValor(self):
    # self.setFormat("%v")
    # return self

    # class Fecha(QtWidgets.QDateTimeEdit):
    # def __init__(self, fecha=None):
    # QtWidgets.QDateTimeEdit.__init__(self)

    # self.setDisplayFormat("dd-MM-yyyy")

    # self.setCalendarPopup(True)
    # calendar = QtWidgets.QCalendarWidget()
    # calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
    # calendar.setGridVisible(True)
    # self.setCalendarWidget(calendar)

    # if fecha:
    # self.ponFecha(fecha)

    # def fecha2date(self, fecha):
    # date = QtCore.QDate()
    # date.setDate(fecha.year, fecha.month, fecha.day)
    # return date

    # def ponFecha(self, fecha):
    # self.setDate(self.fecha2date(fecha))
    # return self

    # def fecha(self):
    # date = self.date()
    # fecha = datetime.date(date.year(), date.month(), date.day())
    # return fecha

    # def minima(self, fecha):
    # previa = self.date()
    # fecha = self.fecha2date(fecha)

    # if previa < fecha:
    # self.ponFecha(fecha)

    # self.setMinimumDate(fecha)
    # return self

    # def maxima(self, fecha):
    # previa = self.date()
    # fecha = self.fecha2date(fecha)
    # if previa > fecha:
    # self.ponFecha(fecha)

    # self.setMaximumDate(fecha)
    # return self
