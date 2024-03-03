"""
formlayout adapted to Lucas Chess
=================================

Original formlayout License Agreement (MIT License)
---------------------------------------------------

Copyright (c) 2009 Pierre Raybaut

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
__license__ = __doc__

import os

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles

separador = (None, None)
SPINBOX, COMBOBOX, COLORBOX, DIAL, EDITBOX, FICHERO, CARPETA, FONTCOMBOBOX, CHSPINBOX = range(9)


class FormLayout:
    def __init__(self, parent, title, icon, with_default=False, anchoMinimo=None, dispatch=None, font_txt=None):
        self.parent = parent
        self.title = title
        self.icon = icon
        self.font_txt = font_txt
        self.with_default = with_default
        self.anchoMinimo = anchoMinimo
        self.dispatch = dispatch

        self.li_gen = []
        self.li_tabs = []

    def separador(self):
        self.li_gen.append(separador)

    def base(self, config, valor):
        self.li_gen.append((config, valor))

    def eddefault(self, label: str, init_value):
        self.li_gen.append((label + ":", init_value))

    def edit_np(self, label: str, init_value):
        self.li_gen.append((label, init_value))

    def edit(self, label: str, init_value: str):
        self.eddefault(label, init_value)

    def editbox(self, label, ancho=None, rx=None, tipo=str, siPassword=False, alto=1, decimales=1, init_value=None):
        self.li_gen.append((Editbox(label, ancho, rx, tipo, siPassword, alto, decimales), init_value))

    def combobox(self, label, lista, init_value, is_editable=False, tooltip=None):
        self.li_gen.append((Combobox(label, lista, is_editable, tooltip), init_value))

    def checkbox(self, label: str, init_value: bool):
        self.eddefault(label, init_value)

    def float(self, label: str, init_value: float):
        self.eddefault(label, float(init_value) if init_value else 0.0)

    def spinbox(self, label, minimo, maximo, ancho, init_value):
        self.li_gen.append((Spinbox(label, minimo, maximo, ancho), init_value))

    def font(self, label, init_value):
        self.li_gen.append((FontCombobox(label), init_value))

    def file(
            self, label, extension, siSave, init_value, siRelativo=True, anchoMinimo=None, ficheroDefecto="",
            li_histo=None
    ):
        self.li_gen.append(
            (Fichero(label, extension, siSave, siRelativo, anchoMinimo, ficheroDefecto, li_histo), init_value)
        )

    def filename(self, label: str, init_value: str):
        self.li_gen.append((Editbox(label, rx="[^\\:/|?*^%><()]*"), init_value))

    def folder(self, label, init_value, carpetaDefecto):
        self.li_gen.append((Carpeta(label, carpetaDefecto), init_value))

    def dial(self, label, minimo, maximo, init_value, siporc=True):
        self.li_gen.append((Dial(label, minimo, maximo, siporc), init_value))

    def apart(self, title):
        self.li_gen.append((None, title + ":"))

    def apart_np(self, title):
        self.li_gen.append((None, title))

    def apart_simple(self, title):
        self.li_gen.append((None, "$" + title + ":"))

    def apart_simple_np(self, title):
        self.li_gen.append((None, "$" + title))

    def apart_nothtml_np(self, title):
        self.li_gen.append((None, "@|" + title))

    def add_tab(self, title):
        self.li_tabs.append((self.li_gen, title, ""))
        self.li_gen = []

    def run(self):
        li = self.li_tabs if self.li_tabs else self.li_gen

        return fedit(
            li,
            title=self.title,
            parent=self.parent,
            anchoMinimo=self.anchoMinimo,
            icon=self.icon,
            if_default=self.with_default,
            dispatch=self.dispatch,
            font=self.font_txt,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Spinbox:
    def __init__(self, label, minimo, maximo, ancho):
        self.tipo = SPINBOX
        self.label = label + ":"
        self.minimo = minimo
        self.maximo = maximo
        self.ancho = ancho


class CHSpinbox:
    def __init__(self, label, minimo, maximo, ancho, chlabel):
        self.tipo = CHSPINBOX
        self.label = label + ":"
        self.chlabel = chlabel
        self.minimo = minimo
        self.maximo = maximo
        self.ancho = ancho


class Combobox:
    def __init__(self, label, lista, is_editable=False, tooltip=None, extend_seek=False):
        self.tipo = COMBOBOX
        self.lista = lista  # (key,titulo),....
        self.label = label + ":"
        self.is_editable = is_editable
        self.extend_seek = extend_seek
        self.tooltip = tooltip


class FontCombobox:
    def __init__(self, label):
        self.tipo = FONTCOMBOBOX
        self.label = label + ":"


class Colorbox:
    def __init__(self, label, ancho, alto, is_ckecked=False, siSTR=False):
        self.tipo = COLORBOX
        self.ancho = ancho
        self.alto = alto
        self.is_ckecked = is_ckecked
        self.siSTR = siSTR
        self.label = label + ":"


class Editbox:
    def __init__(self, label, ancho=None, rx=None, tipo=str, siPassword=False, alto=1, decimales=1):
        self.tipo = EDITBOX
        self.label = label + ":"
        self.ancho = ancho
        self.rx = rx
        self.tipoCampo = tipo
        self.siPassword = siPassword
        self.alto = alto
        self.decimales = decimales


class Casillabox(Editbox):
    def __init__(self, label):
        Editbox.__init__(self, label, ancho=24, rx="[a-h][1-8]")


class Dial:
    def __init__(self, label, minimo, maximo, siporc=True):
        self.tipo = DIAL
        self.minimo = minimo
        self.maximo = maximo
        self.siporc = siporc
        self.label = "\n" + label + ":"


class Carpeta:
    def __init__(self, label, carpetaDefecto):
        self.tipo = CARPETA
        self.label = label + ":"
        self.carpetaDefecto = carpetaDefecto


class Fichero:
    def __init__(self, label, extension, siSave, siRelativo=True, anchoMinimo=None, ficheroDefecto="", li_histo=None):
        self.tipo = FICHERO
        self.extension = extension
        self.siSave = siSave
        self.label = label + ":"
        self.siRelativo = siRelativo
        self.anchoMinimo = anchoMinimo
        self.ficheroDefecto = ficheroDefecto
        self.li_histo = li_histo


class BotonFichero(QtWidgets.QPushButton):
    def __init__(self, file, extension, siSave, siRelativo, anchoMinimo, ficheroDefecto):
        QtWidgets.QPushButton.__init__(self)
        self.clicked.connect(self.cambiaFichero)
        self.file = file
        self.extension = extension
        self.siSave = siSave
        self.siRelativo = siRelativo
        self.anchoMinimo = anchoMinimo
        if anchoMinimo:
            self.setMinimumWidth(anchoMinimo)
        self.qm = QtGui.QFontMetrics(self.font())
        self.file = file
        self.ficheroDefecto = ficheroDefecto
        self.is_first_time = True

    def cambiaFichero(self):
        titulo = _("File to save") if self.siSave else _("File to read")
        fbusca = self.file if self.file else self.ficheroDefecto
        if self.siSave:
            resp = SelectFiles.salvaFichero(self, titulo, fbusca, self.extension, True)
        else:
            resp = SelectFiles.leeFichero(self, fbusca, self.extension, titulo=titulo)
        if resp:
            self.ponFichero(resp)

    def ponFichero(self, txt):
        self.file = txt
        if txt:
            txt = os.path.realpath(txt)
            if self.siRelativo:
                txt = Code.relative_root(txt)
            tamTxt = self.qm.boundingRect(txt).width()
            tmax = self.width() - 10
            if self.is_first_time:
                self.is_first_time = False
                tmax = self.anchoMinimo if self.anchoMinimo else tmax

            while tamTxt > tmax:
                txt = txt[1:]
                tamTxt = self.qm.boundingRect(txt).width()

        self.setText(txt)


class LBotonFichero(QtWidgets.QHBoxLayout):
    def __init__(self, parent, config, file):
        QtWidgets.QHBoxLayout.__init__(self)

        if config.li_histo and not config.ficheroDefecto:
            config.ficheroDefecto = os.path.dirname(config.li_histo[0])

        self.boton = BotonFichero(
            file, config.extension, config.siSave, config.siRelativo, config.anchoMinimo, config.ficheroDefecto
        )
        btCancelar = Controles.PB(parent, "", self.cancelar)
        btCancelar.ponIcono(Iconos.Delete()).anchoFijo(16)
        self.parent = parent

        self.addWidget(self.boton)
        self.addWidget(btCancelar)

        if config.li_histo:
            btHistorico = Controles.PB(parent, "", self.historico).ponIcono(Iconos.Favoritos())
            self.addWidget(btHistorico)
            self.li_histo = config.li_histo
        self.boton.ponFichero(file)

    def historico(self):
        if self.li_histo:
            menu = Controles.Menu(self.parent, puntos=8)
            menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
            for file in self.li_histo:
                menu.opcion(file, file, Iconos.PuntoAzul())

            resp = menu.lanza()
            if resp:
                if menu.siIzq:
                    self.boton.ponFichero(resp)
                elif menu.siDer:
                    if QTUtil2.pregunta(self.parent, _("Do you want to remove file %s from the list?") % resp):
                        del self.li_histo[self.li_histo.index(resp)]

    def cancelar(self):
        self.boton.ponFichero("")


class LBotonCarpeta(QtWidgets.QHBoxLayout):
    def __init__(self, parent, config, carpeta):
        QtWidgets.QHBoxLayout.__init__(self)

        self.config = config
        self.parent = parent

        self.carpeta = carpeta
        self.boton = Controles.PB(parent, self.carpeta, self.cambiarCarpeta, plano=False)
        btCancelar = Controles.PB(parent, "", self.cancelar)
        btCancelar.ponIcono(Iconos.Delete()).anchoFijo(16)
        self.parent = parent

        self.addWidget(self.boton)
        self.addWidget(btCancelar)

    def cambiarCarpeta(self):
        carpeta = SelectFiles.get_existing_directory(self.parent, self.carpeta, self.config.label)
        if carpeta:
            self.carpeta = os.path.abspath(carpeta)
            self.boton.set_text(carpeta)

    def cancelar(self):
        self.carpeta = self.config.carpetaDefecto
        self.boton.set_text(self.carpeta)


class BotonColor(QtWidgets.QPushButton):
    def __init__(self, parent, ancho, alto, siSTR, dispatch):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setFixedSize(ancho, alto)

        self.clicked.connect(self.pulsado)

        self.xcolor = "" if siSTR else -1

        self.siSTR = siSTR

        self.dispatch = dispatch

    def set_color_foreground(self, xcolor):

        self.xcolor = xcolor

        if self.siSTR:
            color = QtGui.QColor(xcolor)
        else:
            color = QtGui.QColor()
            color.setRgba(xcolor)
        self.setStyleSheet("QWidget { background-color: %s }" % color.name())

    def pulsado(self):
        if self.siSTR:
            color = QtGui.QColor(self.xcolor)
        else:
            color = QtGui.QColor()
            color.setRgba(self.xcolor)
        color = QtWidgets.QColorDialog.getColor(
            color,
            self.parentWidget(),
            _("Color"),
            QtWidgets.QColorDialog.ShowAlphaChannel | QtWidgets.QColorDialog.DontUseNativeDialog,
        )
        if color.isValid():
            if self.siSTR:
                self.set_color_foreground(color.name())
            else:
                self.set_color_foreground(color.rgba())
        if self.dispatch:
            self.dispatch()

    def value(self):
        return self.xcolor


class BotonCheckColor(QtWidgets.QHBoxLayout):
    def __init__(self, parent, ancho, alto, dispatch):
        QtWidgets.QHBoxLayout.__init__(self)

        self.boton = BotonColor(parent, ancho, alto, False, dispatch)
        self.checkbox = QtWidgets.QCheckBox(parent)
        self.checkbox.setFixedSize(20, 20)

        self.checkbox.clicked.connect(self.pulsado)

        self.dispatch = dispatch

        self.addWidget(self.checkbox)
        self.addWidget(self.boton)

    def set_color_foreground(self, ncolor):
        if ncolor == -1:
            self.boton.hide()
            self.checkbox.setChecked(False)
        else:
            self.boton.show()
            self.checkbox.setChecked(True)
            self.boton.set_color_foreground(ncolor)

    def value(self):
        if self.checkbox.isChecked():
            return self.boton.xcolor
        else:
            return -1

    def pulsado(self):
        if self.checkbox.isChecked():
            if self.boton.xcolor == -1:
                self.boton.set_color_foreground(0)
                self.boton.pulsado()
            else:
                self.boton.set_color_foreground(self.boton.xcolor)
            self.boton.show()
        else:
            self.boton.hide()
        if self.dispatch:
            self.dispatch()


class Edit(Controles.ED):
    def __init__(self, parent, config, dispatch):
        Controles.ED.__init__(self, parent)
        if dispatch:
            self.textChanged.connect(dispatch)

        if config.rx:
            self.controlrx(config.rx)
        if config.ancho:
            self.anchoFijo(config.ancho)
        if config.siPassword:
            self.setEchoMode(QtWidgets.QLineEdit.Password)
        self.tipo = config.tipoCampo
        self.decimales = config.decimales

    def valor(self):
        if self.tipo == int:
            v = self.textoInt()
        elif self.tipo == float:
            v = self.textoFloat()
        else:
            v = self.texto()
        return v


class TextEdit(Controles.EM):
    def __init__(self, parent, config, dispatch):
        Controles.EM.__init__(self, parent)
        if dispatch:
            self.textChanged.connect(dispatch)

        self.altoMinimo(config.alto)

    def valor(self):
        return self.texto()


class DialNum(QtWidgets.QHBoxLayout):
    def __init__(self, parent, config, dispatch):
        QtWidgets.QHBoxLayout.__init__(self)

        self.dial = QtWidgets.QDial(parent)
        self.dial.setMinimum(config.minimo)
        self.dial.setMaximum(config.maximo)
        self.dial.setNotchesVisible(True)
        self.dial.setFixedSize(40, 40)
        self.lb = QtWidgets.QLabel(parent)

        self.dispatch = dispatch

        self.siporc = config.siporc

        self.dial.valueChanged.connect(self.movido)

        self.addWidget(self.dial)
        self.addWidget(self.lb)

    def set_value(self, nvalor):
        self.dial.setValue(nvalor)
        self.ponLB()

    def ponLB(self):
        txt = "%d" % self.dial.value()
        if self.siporc:
            txt += "%"
        self.lb.setText(txt)

    def movido(self, valor):
        self.ponLB()
        if self.dispatch:
            self.dispatch()

    def value(self):
        return self.dial.value()


class FormWidget(QtWidgets.QWidget):
    def __init__(self, data, comment="", parent=None, dispatch=None):
        super(FormWidget, self).__init__(parent)
        self.data = data
        self.widgets = []
        self.labels = []
        self.formlayout = QtWidgets.QFormLayout(self)
        if comment:
            self.formlayout.addRow(QtWidgets.QLabel(comment, self))
            self.formlayout.addRow(QtWidgets.QLabel(" ", self))

        self.setup(dispatch)

    def setup(self, dispatch):
        for label, value in self.data:

            # Separador
            if label is None and value is None:
                self.formlayout.addRow(QtWidgets.QLabel(" ", self), QtWidgets.QLabel(" ", self))
                self.widgets.append(None)
                self.labels.append(None)

            # Comentario
            elif label is None:
                if value.startswith("$"):
                    lb = Controles.LB(self, value[1:])
                elif value.startswith("@|"):
                    lb = Controles.LB(self, value[2:])
                    lb.setTextFormat(QtCore.Qt.PlainText)
                    lb.setWordWrap(True)
                else:
                    lb = Controles.LB(self, QTUtil2.resalta(value, 3))
                self.formlayout.addRow(lb)
                self.widgets.append(None)
                self.labels.append(None)

            else:
                # Otros tipos
                if not isinstance(label, (bytes, str)):
                    config = label
                    tipo = config.tipo
                    if tipo == SPINBOX:
                        field = QtWidgets.QSpinBox(self)
                        field.setMinimum(config.minimo)
                        field.setMaximum(config.maximo)
                        field.setValue(value)
                        field.setFixedWidth(config.ancho)
                        if dispatch:
                            field.valueChanged.connect(dispatch)
                    elif tipo == COMBOBOX:
                        field = Controles.CB(self, config.lista, value, extend_seek=config.extend_seek)
                        if config.is_editable:
                            field.setEditable(True)
                        if config.tooltip:
                            field.setToolTip(config.tooltip)

                        field.lista = config.lista
                        if dispatch:
                            field.currentIndexChanged.connect(dispatch)
                            # field = QtWidgets.QComboBox(self)
                            # for n, tp in enumerate(config.lista):
                            # if len(tp) == 3:
                            # field.addItem( tp[2], tp[0], tp[1] )
                            # else:
                            # field.addItem( tp[0], tp[1] )
                            # if tp[1] == value:
                            # field.setCurrentIndex( n )
                            # if dispatch:
                            # field.currentIndexChanged.connect( dispatch )
                    elif tipo == FONTCOMBOBOX:
                        field = QtWidgets.QFontComboBox(self)
                        if value:
                            font = Controles.TipoLetra(value)
                            field.setCurrentFont(font)
                    elif tipo == COLORBOX:
                        if config.is_ckecked:
                            field = BotonCheckColor(self, config.ancho, config.alto, dispatch)
                        else:
                            field = BotonColor(self, config.ancho, config.alto, config.siSTR, dispatch)
                        field.set_color_foreground(value)

                    elif tipo == DIAL:
                        field = DialNum(self, config, dispatch)
                        field.set_value(value)

                    elif tipo == EDITBOX:
                        if config.alto == 1:
                            field = Edit(self, config, dispatch)
                            tp = config.tipoCampo
                            if tp == str:
                                field.set_text(value)
                            elif tp == int:
                                field.tipoInt()
                                field.ponInt(value)
                            elif tp == float:
                                field.tipoFloat(0.0)
                                field.ponFloat(value)
                        else:
                            field = TextEdit(self, config, dispatch)
                            field.set_text(value)

                    elif tipo == FICHERO:
                        field = LBotonFichero(self, config, value)

                    elif tipo == CARPETA:
                        field = LBotonCarpeta(self, config, value)

                    label = config.label

                # Fichero
                elif isinstance(value, dict):
                    file = value["FICHERO"]
                    extension = value.get("EXTENSION", "pgn")
                    siSave = value.get("SISAVE", True)
                    siRelativo = value.get("SIRELATIVO", True)
                    field = BotonFichero(file, extension, siSave, siRelativo, 250, file)
                # Texto
                elif isinstance(value, (bytes, str)):
                    field = QtWidgets.QLineEdit(value, self)

                # Combo
                elif isinstance(value, (list, tuple)):
                    selindex = value.pop(0)
                    field = QtWidgets.QComboBox(self)
                    if isinstance(value[0], (list, tuple)):
                        keys = [key for key, _val in value]
                        value = [val for _key, val in value]
                    else:
                        keys = value
                    field.addItems(value)
                    if selindex in value:
                        selindex = value.index(selindex)
                    elif selindex in keys:
                        selindex = keys.index(selindex)
                    else:
                        selindex = 0
                    field.setCurrentIndex(selindex)

                # Checkbox
                elif isinstance(value, bool):
                    field = QtWidgets.QCheckBox(self)
                    field.setCheckState(QtCore.Qt.Checked if value else QtCore.Qt.Unchecked)
                    if dispatch:
                        field.stateChanged.connect(dispatch)

                # Float seconds
                elif isinstance(value, float):  # Para los seconds
                    v = "%0.1f" % value
                    field = QtWidgets.QLineEdit(v, self)
                    field.setValidator(QtGui.QDoubleValidator(0.0, 36000.0, 1, field))  # Para los seconds
                    field.setAlignment(QtCore.Qt.AlignRight)
                    field.setFixedWidth(40)

                # Numero
                elif isinstance(value, int):
                    field = QtWidgets.QSpinBox(self)
                    field.setMaximum(9999)
                    field.setValue(value)
                    field.setFixedWidth(80)

                # Linea
                else:
                    field = QtWidgets.QLineEdit(repr(value), self)

                self.formlayout.addRow(label, field)
                self.formlayout.setLabelAlignment(QtCore.Qt.AlignRight)
                self.widgets.append(field)
                self.labels.append(label)

    def get(self):
        valuelist = []
        for index, (label, value) in enumerate(self.data):
            field = self.widgets[index]
            if label is None:
                # Separator / Comment
                continue
            elif not isinstance(label, (bytes, str)):
                config = label
                tipo = config.tipo
                if tipo == SPINBOX:
                    value = int(field.value())
                elif tipo == COMBOBOX:
                    n = field.currentIndex()
                    value = field.lista[n][1]
                elif tipo == FONTCOMBOBOX:
                    value = field.currentFont().family()
                elif tipo == COLORBOX:
                    value = field.value()
                elif tipo == DIAL:
                    value = field.value()
                elif tipo == EDITBOX:
                    value = field.valor()
                elif tipo == FICHERO:
                    value = field.boton.file
                elif tipo == CARPETA:
                    value = field.carpeta

            elif isinstance(value, (bytes, str)):
                value = field.text()
            elif isinstance(value, dict):
                value = field.file
            elif isinstance(value, (list, tuple)):
                index = int(field.currentIndex())
                if isinstance(value[0], (list, tuple)):
                    value = value[index][0]
                else:
                    value = value[index]
            elif isinstance(value, bool):
                value = field.checkState() == QtCore.Qt.Checked
            elif isinstance(value, float):
                value = float(field.text())
            elif isinstance(value, int):
                value = int(field.value())
            else:
                value = field.text()
            valuelist.append(value)
        return valuelist

    def getWidget(self, number):
        n = -1
        for index in range(len(self.data)):
            field = self.widgets[index]
            if field is not None:
                n += 1
                if n == number:
                    return field
        return None


class FormComboWidget(QtWidgets.QWidget):
    def __init__(self, datalist, comment="", parent=None):
        super(FormComboWidget, self).__init__(parent)
        layout = Colocacion.V()
        self.setLayout(layout)
        self.combobox = QtWidgets.QComboBox(self)
        layout.control(self.combobox)

        self.stackwidget = QtWidgets.QStackWidget(self)
        layout.control(self.stackwidget)
        self.connect(
            self.combobox,
            QtCore.SIGNAL("currentIndexChanged(int)"),
            self.stackwidget,
            QtCore.SLOT("setCurrentIndex(int)"),
        )

        self.widgetlist = []
        for data, title, comment in datalist:
            self.combobox.addItem(title)
            widget = FormWidget(data, comment=comment, parent=self)
            self.stackwidget.addWidget(widget)
            self.widgetlist.append(widget)

    def get(self):
        return [widget.get() for widget in self.widgetlist]


class FormTabWidget(QtWidgets.QWidget):
    def __init__(self, datalist, comment="", parent=None, dispatch=None):
        super(FormTabWidget, self).__init__(parent)
        layout = Colocacion.V()
        self.tabwidget = QtWidgets.QTabWidget()
        layout.control(self.tabwidget)
        self.setLayout(layout)
        self.widgetlist = []
        for data, title, comment in datalist:
            if len(data[0]) == 3:
                widget = FormComboWidget(data, comment=comment, parent=self)
            else:
                widget = FormWidget(data, comment=comment, parent=self, dispatch=dispatch)
            index = self.tabwidget.addTab(widget, title)
            self.tabwidget.setTabToolTip(index, comment)
            self.widgetlist.append(widget)

    def get(self):
        return [widget.get() for widget in self.widgetlist]

    def getWidget(self, numTab, number):
        return self.widgetlist[numTab].getWidget(number)


class FormDialog(QtWidgets.QDialog):
    def __init__(self, data, title="", comment="", icon=None, parent=None, if_default=True, dispatch=None):
        super(FormDialog, self).__init__(parent, QtCore.Qt.Dialog)
        flags = self.windowFlags()
        flags &= ~QtCore.Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        # Form
        if isinstance(data[0][0], (list, tuple)):
            self.formwidget = FormTabWidget(data, comment=comment, parent=self, dispatch=dispatch)
            if dispatch:
                dispatch(self.formwidget)
        elif len(data[0]) == 3:
            self.formwidget = FormComboWidget(data, comment=comment, parent=self)
        else:
            self.formwidget = FormWidget(data, comment=comment, parent=self, dispatch=dispatch)
            if dispatch:
                dispatch(self.formwidget)  # enviamos el form de donde tomar datos cuando hay cambios

        tb = QTVarios.tb_accept_cancel(self, if_default, with_cancel=False)

        layout = Colocacion.V()
        layout.control(tb)
        layout.control(self.formwidget)
        layout.margen(3)

        self.setLayout(layout)

        self.setWindowTitle(title)
        if not isinstance(icon, QtGui.QIcon):
            icon = QtWidgets.QWidget().style().standardIcon(QtWidgets.QStyle.SP_MessageBoxQuestion)
        self.setWindowIcon(icon)

    def aceptar(self):
        self.accion = "aceptar"
        self.data = self.formwidget.get()
        self.accept()

    def defecto(self):
        self.accion = "defecto"
        if not QTUtil2.pregunta(self, _("Are you sure you want to set the default configuration?")):
            return
        self.data = self.formwidget.get()
        self.accept()

    def cancelar(self):
        self.data = None
        self.reject()

    def get(self):
        """Return form result"""
        return self.accion, self.data


def fedit(
        data, title="", comment="", icon=None, parent=None, if_default=False, anchoMinimo=None, dispatch=None, font=None
):
    """
    Create form dialog and return result
    (if Cancel button is pressed, return None)

    data: datalist, datagroup

    datalist: list/tuple of (field_name, field_value)
    datagroup: list/tuple of (datalist *or* datagroup, title, comment)

    -> one field for each member of a datalist
    -> one tab for each member of a top-level datagroup
    -> one page (of a multipage widget, each page can be selected with a combo
       box) for each member of a datagroup inside a datagroup

    Supported types for field_value:
      - int, float, str, unicode, bool
      - colors: in Qt-compatible text form, i.e. in hex format or name (red,...)
                (automatically detected from a string)
      - list/tuple:
          * the first element will be the selected index (or value)
          * the other elements can be couples (key, value) or only values
    """
    dialog = FormDialog(data, title, comment, icon, parent, if_default, dispatch)
    if font:
        dialog.setFont(font)
    if anchoMinimo:
        dialog.setMinimumWidth(anchoMinimo)
    if dialog.exec_():
        QtCore.QCoreApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        return dialog.get()
