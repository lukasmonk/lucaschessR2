import gettext
_= gettext.gettext
import base64
import os

from PySide2 import QtCore, QtGui, QtWidgets

import Code
import Code.Nags.Nags
from Code import Util
from Code.Base import Position
from Code.Board import Board, BoardArrows, ConfBoards
from Code.Director import WindowTabVFlechas
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles


class BotonTema(QtWidgets.QPushButton):
    def __init__(self, parent, rutina):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setFixedSize(64, 64)
        self.qs = QtCore.QSize(64, 64)
        self.setIconSize(self.qs)

        self.rutina = rutina
        self.tema = None

    def pon_tema(self, tema):
        self.setVisible(tema is not None)
        self.tema = tema
        if not tema:
            return
        name = tema.get("NOMBRE")
        seccion = tema.get("SECCION")
        if seccion:
            name += "/%s" % seccion
        self.setToolTip(name)
        self.setIcon(iconoTema(tema, 64))

    def mousePressEvent(self, event):
        self.rutina(self.tema, event.button() == QtCore.Qt.LeftButton)


class BotonColor(QtWidgets.QPushButton):
    def __init__(self, parent, rut_actual, rut_actualiza):
        QtWidgets.QPushButton.__init__(self, parent)

        self.setFixedSize(32, 32)

        self.rut_actual = rut_actual
        self.rut_actualiza = rut_actualiza
        self.clicked.connect(self.pulsado)

        self.parent = parent

        self.set_color_foreground()

    def set_color_foreground(self):
        ncolor = self.rut_actual()
        self.setStyleSheet("QWidget { background: %s }" % QTUtil.qtColor(ncolor).name())

    def pulsado(self):
        ncolor = self.rut_actual()
        color = QTUtil.qtColor(ncolor)

        color = QtWidgets.QColorDialog.getColor(color, title=_("Choose a color"))
        if color.isValid():
            self.rut_actual(color.rgba())
            self.rut_actualiza()
            self.set_color_foreground()


class BotonImagen(Colocacion.H):
    def __init__(self, parent, rut_actual, rut_actualiza, bt_asociado):
        Colocacion.H.__init__(self)
        self.width = 32
        self.height = 32
        self.btImagen = Controles.PB(parent, "", self.cambiar)
        self.btImagen.setFixedSize(self.width, self.height)
        self.btQuitar = Controles.PB(parent, "", self.quitaImagen).ponIcono(Iconos.Motor_No())
        self.bt_asociado = bt_asociado
        self.parent = parent

        self.rut_actual = rut_actual
        self.rut_actualiza = rut_actualiza

        self.control(self.btImagen)
        self.control(self.btQuitar)

        self.ponImagen()

    def setDisabled(self, si):
        self.btImagen.setDisabled(si)
        self.btQuitar.setDisabled(si)

    def quitaImagen(self):
        self.rut_actual("")
        self.ponImagen()
        self.rut_actualiza()

    def ponImagen(self):
        png64 = self.rut_actual()
        if png64:

            pm = QtGui.QPixmap()
            png = base64.b64decode(png64)

            pm.loadFromData(QtCore.QByteArray(png))
            icono = QtGui.QIcon(pm)
            self.btImagen.ponPlano(True)
            self.btImagen.set_text("")
            self.bt_asociado.hide()
            self.btQuitar.show()
        else:
            icono = QtGui.QIcon()
            self.btImagen.ponPlano(False)
            self.btImagen.set_text("?")
            self.bt_asociado.show()
            self.btQuitar.hide()
        self.btImagen.setIcon(icono)
        self.btImagen.setIconSize(QtCore.QSize(self.width, self.height))

    def cambiar(self):
        configuration = Code.configuration
        dic = configuration.read_variables("WindowColores")
        folder_prev = dic.get("PNGfolder", "")
        resp = SelectFiles.leeFichero(self.parent, folder_prev, "png")
        if resp:
            folder = os.path.dirname(resp)
            if folder_prev != folder:
                dic["PNGfolder"] = folder
                configuration.write_variables("WindowColores", dic)
            with open(resp, "rb") as f:
                self.rut_actual(base64.b64encode(f.read()))
            self.ponImagen()
            self.rut_actualiza()


class BotonFlecha(Colocacion.H):
    def __init__(self, parent, rut_actual, rut_defecto, rut_actualiza):
        Colocacion.H.__init__(self)
        self.width = 128
        self.height = 32
        self.btFlecha = Controles.PB(parent, "", self.cambiar)
        self.btFlecha.setFixedSize(self.width, self.height)
        self.btQuitar = Controles.PB(parent, "", self.ponDefecto).ponIcono(Iconos.Motor_No())
        self.parent = parent

        self.rut_actual = rut_actual
        self.rut_defecto = rut_defecto
        self.rut_actualiza = rut_actualiza

        self.control(self.btFlecha)
        self.control(self.btQuitar)

        self.ponImagen()

    def setDisabled(self, si):
        self.btFlecha.setDisabled(si)
        self.btQuitar.setDisabled(si)

    def cambiaFlecha(self, nueva):
        self.rut_actual(nueva)
        self.ponImagen()
        self.rut_actualiza()

    def ponDefecto(self):
        self.cambiaFlecha(self.rut_defecto())

    def ponImagen(self):
        bf = self.rut_actual()
        p = bf.physical_pos
        p.x = 0
        p.y = self.height / 2
        p.ancho = self.width
        p.alto = self.height / 2

        pm = BoardArrows.pixmapArrow(bf, self.width, self.height)
        icono = QtGui.QIcon(pm)
        self.btFlecha.setIcon(icono)
        self.btFlecha.setIconSize(QtCore.QSize(self.width, self.height))

    def cambiar(self):
        w = WindowTabVFlechas.WTV_Flecha(self.parent, self.rut_actual(), False)
        if w.exec_():
            self.cambiaFlecha(w.regFlecha)


class DialNum(Colocacion.H):
    def __init__(self, parent, rut_actual, rut_actualiza):
        Colocacion.H.__init__(self)

        self.dial = QtWidgets.QSlider(QtCore.Qt.Horizontal, parent)
        self.dial.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.dial.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.dial.setTickInterval(10)
        self.dial.setSingleStep(1)
        self.dial.setMinimum(0)
        self.dial.setMaximum(99)

        self.dial.valueChanged.connect(self.movido)
        self.lb = QtWidgets.QLabel(parent)

        self.rut_actual = rut_actual
        self.rut_actualiza = rut_actualiza

        self.control(self.dial)
        self.control(self.lb)

        self.set_value()

    def set_value(self):
        nvalor = self.rut_actual()
        self.dial.setValue(nvalor)
        self.lb.setText("%2d%%" % nvalor)

    def movido(self, valor):
        self.rut_actual(valor)
        self.set_value()
        self.rut_actualiza()


class WBoardColors(LCDialog.LCDialog):
    def __init__(self, boardOriginal):
        main_window = boardOriginal.parent()
        titulo = _("Colors")
        icono = Iconos.EditarColores()
        extparam = "WColores"
        LCDialog.LCDialog.__init__(self, main_window, titulo, icono, extparam)

        self.boardOriginal = boardOriginal
        self.configuration = Code.configuration
        self.config_board = boardOriginal.config_board.copia(boardOriginal.config_board._id)
        self.is_base = boardOriginal.config_board._id == "BASE"

        # Temas #######################################################################################################
        li_options = [(_("Your themes"), self.configuration.ficheroTemas)]
        for entry in Util.listdir(Code.path_resource("Themes")):
            filename = entry.name
            if filename.endswith("lktheme3"):
                ctema = filename[:-9]
                li_options.append((ctema, Code.path_resource("Themes", filename)))

        self.cbTemas = Controles.CB(self, li_options, li_options[0][1]).capture_changes(self.cambiadoTema)
        self.lbSecciones = Controles.LB(self, _("Section") + ":")
        self.cbSecciones = Controles.CB(self, [], None).capture_changes(self.cambiadoSeccion)
        self.lb_help = Controles.LB(self, _("Left button to select, Right to show menu"))

        ly_temas = Colocacion.V()
        self.lista_bt_temas = []
        for i in range(24):
            ly = Colocacion.H()
            for j in range(5):
                bt = BotonTema(self, self.cambia_tema)
                ly.control(bt)
                bt.pon_tema(None)
                self.lista_bt_temas.append(bt)
            ly.relleno(1)
            ly_temas.otro(ly)
        ly_temas.relleno(1).margen(1)

        scroll = QtWidgets.QScrollArea()
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)
        w_themes = QtWidgets.QWidget()
        w_themes.setLayout(ly_temas)
        scroll.setWidget(w_themes)
        scroll.setFixedHeight((64 + 4) * 3 + 4)

        def crea_lb(txt):
            return Controles.LB(self, txt + ": ").align_right()

        # Casillas
        lbTrans = Controles.LB(self, _("Degree of transparency"))
        lbPNG = Controles.LB(self, _("Image"))

        # # Blancas
        lbBlancas = crea_lb(_("White squares"))
        self.btBlancas = BotonColor(self, self.config_board.colorBlancas, self.actualizaBoard)
        self.btBlancasPNG = BotonImagen(self, self.config_board.png64Blancas, self.actualizaBoard, self.btBlancas)
        self.dialBlancasTrans = DialNum(self, self.config_board.transBlancas, self.actualizaBoard)

        # # Negras
        lbNegras = crea_lb(_("Black squares"))
        self.btNegras = BotonColor(self, self.config_board.colorNegras, self.actualizaBoard)
        self.btNegrasPNG = BotonImagen(self, self.config_board.png64Negras, self.actualizaBoard, self.btNegras)
        self.dialNegrasTrans = DialNum(self, self.config_board.transNegras, self.actualizaBoard)

        # Background
        lbFondo = crea_lb(_("Background"))
        self.btFondo = BotonColor(self, self.config_board.colorFondo, self.actualizaBoard)
        self.btFondoPNG = BotonImagen(self, self.config_board.png64Fondo, self.actualizaBoard, self.btFondo)
        self.chbExtended = Controles.CHB(
            self, _("Extended to outer border"), self.config_board.extendedColor()
        ).capture_changes(self, self.extendedColor)

        # Actual
        self.chbTemas = Controles.CHB(self, _("By default"), self.config_board.siDefTema()).capture_changes(
            self, self.defectoTemas
        )
        if self.is_base:
            self.chbTemas.set_value(False)
            self.chbTemas.setVisible(False)
        # Exterior
        lbExterior = crea_lb(_("Outer Border"))
        self.btExterior = BotonColor(self, self.config_board.colorExterior, self.actualizaBoard)
        self.btExteriorPNG = BotonImagen(self, self.config_board.png64Exterior, self.actualizaBoard, self.btExterior)

        # Texto
        lbTexto = crea_lb(_("Coordinates"))
        self.btTexto = BotonColor(self, self.config_board.colorTexto, self.actualizaBoard)
        # Frontera
        lbFrontera = crea_lb(_("Inner Border"))
        self.btFrontera = BotonColor(self, self.config_board.colorFrontera, self.actualizaBoard)

        # Flechas
        lbFlecha = crea_lb(_("Move indicator"))
        self.lyF = BotonFlecha(
            self, self.config_board.fTransicion, self.config_board.flechaDefecto, self.actualizaBoard
        )
        lbFlechaAlternativa = crea_lb(_("Arrow alternative"))
        self.lyFAlternativa = BotonFlecha(
            self, self.config_board.fAlternativa, self.config_board.flechaAlternativaDefecto, self.actualizaBoard
        )
        lbFlechaActivo = crea_lb(_("Active moves"))
        self.lyFActual = BotonFlecha(
            self, self.config_board.fActivo, self.config_board.flechaActivoDefecto, self.actualizaBoard
        )
        lbFlechaRival = crea_lb(_("Opponent moves"))
        self.lyFRival = BotonFlecha(
            self, self.config_board.fRival, self.config_board.flechaRivalDefecto, self.actualizaBoard
        )

        lyActual = Colocacion.G()
        lyActual.control(self.chbTemas, 0, 0)
        lyActual.controlc(lbPNG, 0, 2).controlc(lbTrans, 0, 3)
        lyActual.controld(lbBlancas, 1, 0).control(self.btBlancas, 1, 1).otroc(self.btBlancasPNG, 1, 2).otroc(
            self.dialBlancasTrans, 1, 3
        )
        lyActual.controld(lbNegras, 2, 0).control(self.btNegras, 2, 1).otroc(self.btNegrasPNG, 2, 2).otroc(
            self.dialNegrasTrans, 2, 3
        )
        lyActual.controld(lbFondo, 3, 0).control(self.btFondo, 3, 1).otroc(self.btFondoPNG, 3, 2).control(
            self.chbExtended, 3, 3
        )
        lyActual.controld(lbExterior, 4, 0).control(self.btExterior, 4, 1).otroc(self.btExteriorPNG, 4, 2)
        lyActual.controld(lbTexto, 5, 0).control(self.btTexto, 5, 1)
        lyActual.controld(lbFrontera, 6, 0).control(self.btFrontera, 6, 1)
        lyActual.controld(lbFlecha, 7, 0).otro(self.lyF, 7, 1, 1, 4)
        lyActual.controld(lbFlechaAlternativa, 8, 0).otro(self.lyFAlternativa, 8, 1, 1, 4)
        lyActual.controld(lbFlechaActivo, 9, 0).otro(self.lyFActual, 9, 1, 1, 4)
        lyActual.controld(lbFlechaRival, 10, 0).otro(self.lyFRival, 10, 1, 1, 4)

        gbActual = Controles.GB(self, _("Active theme"), lyActual)

        lySecciones = Colocacion.H().control(self.lbSecciones).control(self.cbSecciones).control(self.lb_help).relleno()
        ly = Colocacion.V().control(self.cbTemas).otro(lySecciones).control(scroll).control(gbActual).relleno()
        gbTemas = Controles.GB(self, "", ly)
        gbTemas.setFlat(True)

        # mas options ################################################################################################
        def xDefecto(if_default):
            if self.is_base:
                if_default = False
            chb = Controles.CHB(self, _("By default"), if_default).capture_changes(self, self.defectoBoardM)
            if self.is_base:
                chb.setVisible(False)
            return chb

        def l2mas1(lyG, row, a, b, c):
            if a:
                ly = Colocacion.H().controld(a).control(b)
            else:
                ly = Colocacion.H().control(b)
            lyG.otro(ly, row, 0).control(c, row, 1)

        # Coordenadas
        lyG = Colocacion.G()
        # _nCoordenadas
        lbCoordenadas = crea_lb(_("Number"))
        li_options = [("0", 0), ("4", 4), ("2a", 2), ("2b", 3), ("2c", 5), ("2d", 6)]
        self.cbCoordenadas = Controles.CB(self, li_options, self.config_board.nCoordenadas()).capture_changes(
            self.actualizaBoardM
        )
        self.chbDefCoordenadas = xDefecto(self.config_board.siDefCoordenadas())
        l2mas1(lyG, 0, lbCoordenadas, self.cbCoordenadas, self.chbDefCoordenadas)

        # _tipoLetra
        lbTipoLetra = crea_lb(_("Font"))
        self.cbTipoLetra = QtWidgets.QFontComboBox()
        self.cbTipoLetra.setEditable(False)
        self.cbTipoLetra.setFontFilters(self.cbTipoLetra.ScalableFonts)
        self.cbTipoLetra.setCurrentFont(QtGui.QFont(self.config_board.tipoLetra()))
        self.cbTipoLetra.currentIndexChanged.connect(self.actualizaBoardM)
        self.chbDefTipoLetra = xDefecto(self.config_board.siDefTipoLetra())
        l2mas1(lyG, 1, lbTipoLetra, self.cbTipoLetra, self.chbDefTipoLetra)

        # _cBold
        self.chbBold = Controles.CHB(self, _("Bold"), self.config_board.siBold()).capture_changes(
            self, self.actualizaBoardM
        )
        self.chbDefBold = xDefecto(self.config_board.siDefBold())
        l2mas1(lyG, 2, None, self.chbBold, self.chbDefBold)

        # _tamLetra
        lbTamLetra = crea_lb(_("Size") + " %")
        self.sbTamLetra = (
            Controles.SB(self, self.config_board.tamLetra(), 1, 200).tamMaximo(50).capture_changes(self.actualizaBoardM)
        )
        self.chbDefTamLetra = xDefecto(self.config_board.siDefTamLetra())
        l2mas1(lyG, 3, lbTamLetra, self.sbTamLetra, self.chbDefTamLetra)

        # _sepLetras
        lbSepLetras = crea_lb(_("Separation") + " %")
        self.sbSepLetras = (
            Controles.SB(self, self.config_board.sepLetras(), -1000, 1000)
            .tamMaximo(50)
            .capture_changes(self.actualizaBoardM)
        )
        self.chbDefSepLetras = xDefecto(self.config_board.siDefSepLetras())
        l2mas1(lyG, 4, lbSepLetras, self.sbSepLetras, self.chbDefSepLetras)

        gbCoordenadas = Controles.GB(self, _("Coordinates"), lyG)

        ly_otros = Colocacion.G()
        # _nomPiezas
        li = []
        lbPiezas = crea_lb(_("Pieces"))
        for entry in Util.listdir(Code.path_resource("Pieces")):
            if entry.is_dir():
                li.append((entry.name, entry.name))
        li.sort(key=lambda x: x[0])
        self.cbPiezas = Controles.CB(self, li, self.config_board.nomPiezas()).capture_changes(self.actualizaBoardM)
        self.chbDefPiezas = xDefecto(self.config_board.siDefPiezas())
        l2mas1(ly_otros, 0, lbPiezas, self.cbPiezas, self.chbDefPiezas)

        # _tamRecuadro
        lbTamRecuadro = crea_lb(_("Outer Border Size") + " %")
        self.sbTamRecuadro = (
            Controles.SB(self, self.config_board.tamRecuadro(), 0, 10000)
            .tamMaximo(50)
            .capture_changes(self.actualizaBoardM)
        )
        self.chbDefTamRecuadro = xDefecto(self.config_board.siDefTamRecuadro())
        l2mas1(ly_otros, 1, lbTamRecuadro, self.sbTamRecuadro, self.chbDefTamRecuadro)

        # _tamFrontera
        lbTamFrontera = crea_lb(_("Inner Border Size") + " %")
        self.sbTamFrontera = (
            Controles.SB(self, self.config_board.tamFrontera(), 0, 10000)
            .tamMaximo(50)
            .capture_changes(self.actualizaBoardM)
        )
        self.chbDefTamFrontera = xDefecto(self.config_board.siDefTamFrontera())
        l2mas1(ly_otros, 2, lbTamFrontera, self.sbTamFrontera, self.chbDefTamFrontera)

        # _opacitySideIndicator
        lbSideIndicator = crea_lb(_("Playing side indicator transparency"))
        self.dialSideIndicatorTrans = DialNum(self, self.config_board.transSideIndicator, self.actualizaBoard)
        ly_h = Colocacion.H().control(lbSideIndicator).otro(self.dialSideIndicatorTrans)
        ly_otros.otro(ly_h, 3, 0)

        ly = Colocacion.V().control(gbCoordenadas).espacio(50).otro(ly_otros).relleno()

        gbOtros = Controles.GB(self, "", ly)
        gbOtros.setFlat(True)

        # Board #####################################################################################################
        cp = Position.Position().read_fen("2kr1b1r/2p1pppp/p7/3pPb2/1q3P2/2N1P3/PPP3PP/R1BQK2R w KQ - 0 1")
        self.board = Board.Board(self, self.config_board, siMenuVisual=False)
        self.board.permitidoResizeExterno(False)
        self.board.crea()
        self.board.set_position(cp)
        self.rehazFlechas()

        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            ("%s/%s" % (_("Save"), _("Save as")), Iconos.Grabar(), self.menu_save),
            None,
            (_("Import"), Iconos.Import8(), self.importar),
            None,
            (_("Export"), Iconos.Export8(), self.exportar),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # tam board
        self.lbTamBoard = Controles.LB(self, "%d px" % self.board.width())

        # Juntamos
        lyT = Colocacion.V().control(tb).control(self.board).controli(self.lbTamBoard).relleno(1).margen(3)

        self.tab = Controles.Tab()
        self.tab.new_tab(gbTemas, _("Themes"))
        self.tab.new_tab(gbOtros, _("Other options"))
        ly = Colocacion.H().otro(lyT).control(self.tab).margen(3)

        self.setLayout(ly)

        self.elegido = None

        self.li_themes = self.read_own_themes()
        self.current_theme = {
            "NOMBRE": "",
            "SECCION": "",
            "CHANGE_PIECES": True,
            "o_tema": self.config_board.grabaTema(),
            "o_base": self.config_board.grabaBase(),
        }
        self.own_theme_selected = False
        self.defectoTemas()

        self.extendedColor()

        self.siActualizando = False

        self.restore_video(siTam=False)

        self.show()  # necesario para que se vean bien la primera vez
        self.cambiadoTema()

    def extendedColor(self):
        siExt = self.chbExtended.valor()
        self.btExterior.setEnabled(not siExt)
        self.config_board.extendedColor(siExt)

        self.actualizaBoard()

    def rehazFlechas(self):
        self.board.remove_arrows()
        self.board.creaFlechaTmp("f2", "f4", True)
        self.board.creaFlechaTmp("d1", "d4", False)
        self.board.creaFlechaMov("f5", "d7", "ms100")
        self.board.creaFlechaMov("d6", "b4", "mt100")

    def cambiadoTema(self):
        file_theme = self.cbTemas.valor()
        self.read_themes(file_theme)
        self.own_theme_selected = file_theme == self.configuration.ficheroTemas
        self.lb_help.setVisible(self.own_theme_selected)

        if not self.li_themes:
            self.cbTemas.set_value(Code.path_resource("Themes", "Lucas.lktheme3"))
            self.cambiadoTema()
        else:
            self.ponSecciones()
            self.cambiadoSeccion()

    def ponSecciones(self):
        previo = self.cbSecciones.valor()
        li_options = []
        liFolders = []
        for n, uno in enumerate(self.li_themes):
            if uno:
                if "SECCION" in uno:
                    folder = uno["SECCION"]
                    if not (folder in liFolders):
                        liFolders.append(folder)
                        li_options.append((folder, folder))

        li_options.append((_("All"), None))

        select = previo if previo is None or previo in liFolders else li_options[0][1]
        self.cbSecciones.rehacer(li_options, select)
        siVisible = len(li_options) > 1
        self.cbSecciones.setVisible(siVisible)
        self.lbSecciones.setVisible(siVisible)

    def cambiadoSeccion(self):
        seccionBusca = self.cbSecciones.valor()
        maxtemas = len(self.lista_bt_temas)
        nPos = 0
        for nTema, tema in enumerate(self.li_themes):
            if tema:
                seccion = tema.get("SECCION", None)

                if (seccionBusca is None) or (seccion == seccionBusca):
                    self.lista_bt_temas[nPos].pon_tema(tema)
                    nPos += 1
                    if nPos == maxtemas:
                        break

        for x in range(nPos, maxtemas):
            self.lista_bt_temas[x].pon_tema(None)

    def defectoTemas(self):
        if_default = self.chbTemas.valor()
        self.config_board.ponDefTema(if_default)
        self.btExterior.setDisabled(if_default)

        self.btBlancas.setDisabled(if_default)
        self.btBlancasPNG.setDisabled(if_default)
        self.dialBlancasTrans.dial.setDisabled(if_default)

        self.btNegras.setDisabled(if_default)
        self.btNegrasPNG.setDisabled(if_default)
        self.dialNegrasTrans.dial.setDisabled(if_default)

        self.btTexto.setDisabled(if_default)
        self.btFrontera.setDisabled(if_default)

        self.lyF.setDisabled(if_default)
        self.lyFAlternativa.setDisabled(if_default)
        self.lyFActual.setDisabled(if_default)
        self.lyFRival.setDisabled(if_default)

        self.btFondo.setDisabled(if_default)
        self.btFondoPNG.setDisabled(if_default)

        self.btExterior.setDisabled(if_default)
        self.btExteriorPNG.setDisabled(if_default)

        self.actualizaBoard()

    def aceptar(self):
        self.config_board.guardaEnDisco()
        self.boardOriginal.reset(self.config_board)

        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def importar(self):
        dr = self.configuration.read_variables("PCOLORES")
        dirBase = dr["DIRBASE"] if dr else ""

        fich = SelectFiles.leeFichero(self, dirBase, "lktheme3")
        if fich:
            dr["DIRBASE"] = os.path.dirname(fich)
            self.configuration.write_variables("PCOLORES", dr)
            obj = Util.restore_pickle(fich)
            if obj:
                if type(obj) == dict:
                    li_temas = [obj]
                else:
                    li_temas = obj
                self.read_own_themes()
                self.li_themes.extend(li_temas)
                self.save_own_themes()
                self.ponSecciones()

    def exportar(self):
        dr = self.configuration.read_variables("PCOLORES")
        dirBase = dr["DIRBASE"] if dr else ""
        fich = SelectFiles.salvaFichero(self, _("Colors"), dirBase, "lktheme3", True)
        if fich:
            dr["DIRBASE"] = os.path.dirname(fich)
            self.configuration.write_variables("PCOLORES", dr)
            if not fich.lower().endswith("lktheme3"):
                fich += ".lktheme3"
            tema = {}
            if self.current_theme:
                tema["NOMBRE"] = self.current_theme.get("NOMBRE", "")
                tema["SECCION"] = self.current_theme.get("SECCION", "")
                tema["CHANGE_PIECES"] = self.current_theme.get("CHANGE_PIECES", False)
            tema["o_tema"] = self.config_board.grabaTema()
            tema["o_base"] = self.config_board.grabaBase()
            self.test_if_pieces(tema)
            Util.save_pickle(fich, tema)
            QTUtil2.mensajeTemporal(self, _("Saved"), 1.0)

    def cambia_tema(self, tema, si_left):
        if si_left:
            self.pon_tema(tema)
            self.current_theme = tema

        else:
            if self.own_theme_selected:
                menu = QTVarios.LCMenu(self)
                menu.opcion("rename", _("Change the name/section"), Iconos.Rename())
                menu.separador()
                menu.opcion("delete", _("Remove"), Iconos.Delete())
                menu.separador()
                resp = menu.lanza()
                if resp == "rename":
                    self.rename_theme(tema)
                    self.save_own_themes()
                elif resp == "delete":
                    name = tema.get("NOMBRE", "")
                    seccion = tema.get("SECCION", "")
                    if seccion:
                        name += "/" + seccion
                    if QTUtil2.pregunta(self, _("Are you sure you want to remove %s?") % name):
                        if tema in self.li_themes:
                            self.li_themes.remove(tema)
                            self.save_own_themes()
                            self.ponSecciones()

    def pon_tema(self, tema):
        ct = self.config_board
        self.chbTemas.set_value(False)
        self.defectoTemas()
        self.sinElegir = False
        ct.leeTema(tema["o_tema"])

        if "o_base" in tema:
            ct.leeBase(tema["o_base"])
        else:
            nomPiezas = ct.nomPiezas()
            ct.o_base.defecto()
            ct.cambiaPiezas(nomPiezas)

        ct = ct.copia(ct.id())  # para que los cambia captura no lo modifiquen

        self.btBlancasPNG.ponImagen()
        self.btNegrasPNG.ponImagen()
        self.btFondoPNG.ponImagen()
        self.btExteriorPNG.ponImagen()

        self.lyF.ponImagen()
        self.lyFAlternativa.ponImagen()
        self.lyFActual.ponImagen()
        self.lyFRival.ponImagen()

        self.cbCoordenadas.set_value(ct.nCoordenadas())
        self.chbDefCoordenadas.set_value(ct.siDefCoordenadas())
        self.cbTipoLetra.setCurrentFont(QtGui.QFont(ct.tipoLetra()))
        self.chbDefTipoLetra.set_value(ct.siDefTipoLetra())
        self.chbBold.set_value(ct.siBold())
        self.chbDefBold.set_value(ct.siDefBold())
        self.sbTamLetra.set_value(ct.tamLetra())
        self.chbDefTamLetra.set_value(ct.siDefTamLetra())
        self.sbSepLetras.set_value(ct.sepLetras())
        self.chbDefSepLetras.set_value(ct.siDefSepLetras())
        self.cbPiezas.set_value(ct.nomPiezas())
        self.chbDefPiezas.set_value(ct.siDefPiezas())
        self.sbTamRecuadro.set_value(ct.tamRecuadro())
        self.chbDefTamRecuadro.set_value(ct.siDefTamRecuadro())
        self.sbTamFrontera.set_value(ct.tamFrontera())
        self.chbDefTamFrontera.set_value(ct.siDefTamFrontera())
        self.dialBlancasTrans.dial.setValue(ct.transBlancas())
        self.dialNegrasTrans.dial.setValue(ct.transNegras())

        self.chbExtended.set_value(ct.extendedColor())

        self.actualizaBoard()

    def defectoBoardM(self):
        if self.siActualizando:
            return
        self.siActualizando = True

        self.actualizaBoardM()

        ct = self.config_board
        for chb, obj, xv in (
            (self.chbDefCoordenadas, self.cbCoordenadas, ct.nCoordenadas),
            (self.chbDefBold, self.chbBold, ct.siBold),
            (self.chbDefTamLetra, self.sbTamLetra, ct.tamLetra),
            (self.chbDefSepLetras, self.sbSepLetras, ct.sepLetras),
            (self.chbDefPiezas, self.cbPiezas, ct.nomPiezas),
            (self.chbDefTamRecuadro, self.sbTamRecuadro, ct.tamRecuadro),
            (self.chbDefTamFrontera, self.sbTamFrontera, ct.tamFrontera),
        ):
            if chb.valor():
                obj.set_value(xv())
                obj.setEnabled(False)
            else:
                obj.setEnabled(True)

        if self.chbDefTipoLetra.valor():
            self.cbTipoLetra.setCurrentFont(QtGui.QFont(ct.tipoLetra()))
            self.cbTipoLetra.setEnabled(False)
        else:
            self.cbTipoLetra.setEnabled(True)

        self.siActualizando = False

    def actualizaBoardM(self):
        ct = self.config_board

        ct.ponCoordenadas(None if self.chbDefCoordenadas.valor() else self.cbCoordenadas.valor())

        ct.ponTipoLetra(None if self.chbDefTipoLetra.valor() else self.cbTipoLetra.currentText())

        ct.ponBold(None if self.chbDefBold.valor() else self.chbBold.valor())

        ct.ponTamLetra(None if self.chbDefTamLetra.valor() else self.sbTamLetra.valor())

        ct.ponSepLetras(None if self.chbDefSepLetras.valor() else self.sbSepLetras.valor())

        ct.ponNomPiezas(None if self.chbDefPiezas.valor() else self.cbPiezas.valor())

        ct.ponTamRecuadro(None if self.chbDefTamRecuadro.valor() else self.sbTamRecuadro.valor())

        ct.ponTamFrontera(None if self.chbDefTamFrontera.valor() else self.sbTamFrontera.valor())

        self.actualizaBoard()

    def actualizaBoard(self):
        if hasattr(self, "board"):  # tras crear dial no se ha creado board
            # ct = self.config_board
            self.board.crea()
            self.rehazFlechas()
            self.btExterior.set_color_foreground()
            self.btBlancas.set_color_foreground()
            self.btNegras.set_color_foreground()
            self.btTexto.set_color_foreground()
            self.btFrontera.set_color_foreground()
            self.lbTamBoard.set_text("%dpx" % self.board.width())

    def read_own_themes(self):
        self.read_themes(self.configuration.ficheroTemas)

    def read_themes(self, file):
        self.li_themes = Util.restore_pickle(file)
        if self.li_themes is None:
            self.li_themes = []
        else:
            self.li_themes.sort(key=lambda x: "%20s%s" % (x.get("SECCION", ""), x.get("NOMBRE")))

    def test_if_pieces(self, theme):
        if not theme.get("CHANGE_PIECES", False):
            if "o_base" in theme and "x_nomPiezas" in theme["o_base"]:
                del theme["o_base"]["x_nomPiezas"]

    def menu_save(self):
        accion = "save_as"
        if self.own_theme_selected and self.current_theme.get("NOMBRE"):
            menu = QTVarios.LCMenu(self)
            menu.opcion("save", _("Save") + " " + self.current_theme.get("NOMBRE"), Iconos.Grabar())
            menu.separador()
            menu.opcion("save_as", _("Save as"), Iconos.GrabarComo())
            menu.separador()
            accion = menu.lanza()
            if accion is None:
                return

        if accion == "save":
            self.read_own_themes()
            png64 = self.board.thumbnail(64)
            self.config_board.png64Thumb(base64.b64encode(png64))
            self.current_theme["o_tema"] = self.config_board.grabaTema()
            self.current_theme["o_base"] = self.config_board.grabaBase()
            if not self.current_theme.get("CHANGE_PIECES", False):
                self.test_if_pieces(self.current_theme)
            for pos, theme in enumerate(self.li_themes):
                if theme.get("NOMBRE") == self.current_theme.get("NOMBRE"):
                    self.li_themes[pos] = self.current_theme

            self.save_own_themes()

        elif accion == "save_as":
            theme = dict(self.current_theme)
            if self.rename_theme(theme):
                self.read_own_themes()
                png64 = self.board.thumbnail(64)
                self.config_board.png64Thumb(base64.b64encode(png64))
                theme["o_tema"] = self.config_board.grabaTema()
                theme["o_base"] = self.config_board.grabaBase()
                self.test_if_pieces(theme)
                self.li_themes.append(theme)
                self.save_own_themes()
                self.current_theme = theme
                self.ponSecciones()

    def save_own_themes(self):
        Util.save_pickle(self.configuration.ficheroTemas, self.li_themes)
        if self.cbTemas.valor() != self.configuration.ficheroTemas:
            self.cbTemas.set_value(self.configuration.ficheroTemas)
            self.cambiadoTema()

    def rename_theme(self, tema):
        w = WNameTheme(self, tema, self.li_themes)
        return w.exec_()


def ponMenuTemas(menuBase, liTemas, baseResp):
    baseResp += "%d"

    dFolders = Util.SymbolDict()
    liRoot = []
    for n, uno in enumerate(liTemas):
        if uno:
            if "SECCION" in uno and uno["SECCION"]:
                folder = uno["SECCION"]
                if not (folder in dFolders):
                    dFolders[folder] = []
                dFolders[folder].append((uno, n))
            else:
                liRoot.append((uno, n))
    icoFolder = Iconos.DivisionF()
    for k in dFolders:
        mf = menuBase.submenu(k, icoFolder)
        for uno, n in dFolders[k]:
            mf.opcion(baseResp % n, uno["NOMBRE"], iconoTema(uno, 16))
    menuBase.separador()
    for uno, n in liRoot:
        menuBase.opcion(baseResp % n, uno.get("NOMBRE", "?"), iconoTema(uno, 16))
    menuBase.separador()


def eligeTema(parent, fichTema):
    liTemas = Util.restore_pickle(fichTema)
    if not liTemas:
        return None

    menu = QTVarios.LCMenu(parent)

    ponMenuTemas(menu, liTemas, "")

    resp = menu.lanza()

    return None if resp is None else liTemas[int(resp)]


# def nag2ico(nag, tam):
#     with open(Code.path_resource("IntFiles", "NAGs", "Color", "nag_%d.svg" % nag), "rb") as f:
#         dato = f.read()
#         color = getattr(Code.configuration, "x_color_nag%d" % nag)
#         dato = dato.replace(b"#3139ae", color.encode())
#     return QTVarios.svg2ico(dato, tam)


def iconoTema(tema, tam):
    svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   version="1.1"
   width="388pt"
   height="388pt"
   viewBox="0 0 388 388"
   id="svg2">
  <metadata
     id="metadata117">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <defs
     id="defs115" />
  <g
     id="layer3"
     style="display:inline">
    <rect
       width="486.81006"
       height="486.81006"
       x="0"
       y="-0.35689625"
       transform="scale(0.8,0.8)"
       id="rect4020"
       style="fill:FONDO;fill-opacity:1;fill-rule:nonzero;stroke:none" />
  </g>
  <g
     id="layer1"
     style="display:inline">
    <rect
       width="316.67606"
       height="317.12463"
       ry="0"
       x="35.708782"
       y="34.520344"
       id="rect3095"
       style="fill:WHITE;stroke:RECUADRO;stroke-width:4.54554987;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
  </g>
  <g
     id="layer2"
     style="display:inline">
    <rect
       width="38.841644"
       height="39.047188"
       x="154.92021"
       y="36.90279"
       id="rect3104"
       style="fill:BLACK;fill-opacity:1;stroke:BLACK;stroke-width:0.16;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0" />
    <use
       transform="translate(-78.883927,0)"
       id="use3887"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-118.64494,118.02342)"
       id="use3889"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-39.492576,196.10726)"
       id="use3891"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-118.64494,274.01176)"
       id="use3893"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(78.161342,3.0019919e-8)"
       id="use3903"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(156.08573,78.779427)"
       id="use3905"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-118.64494,196.10726)"
       id="use3907"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(38.395272,274.01176)"
       id="use3909"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(156.08573,3.0019984e-8)"
       id="use3919"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(0,78.779427)"
       id="use3921"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-78.883927,156.79797)"
       id="use3923"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-39.492576,274.01176)"
       id="use3925"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-118.64494,39.217809)"
       id="use3935"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(78.161342,78.779427)"
       id="use3937"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(0,156.79797)"
       id="use3939"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(0,235.54546)"
       id="use3941"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-39.492576,39.217809)"
       id="use3951"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-39.492576,118.02342)"
       id="use3953"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(38.395272,196.10726)"
       id="use3955"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(78.161342,235.54546)"
       id="use3957"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(38.395272,39.217809)"
       id="use3967"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(38.395272,118.02342)"
       id="use3969"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(78.161342,156.79797)"
       id="use3971"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(156.08573,235.54546)"
       id="use3973"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(116.52539,39.217809)"
       id="use3983"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(116.52539,118.02342)"
       id="use3985"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(116.52539,196.10726)"
       id="use3987"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(116.52539,274.01176)"
       id="use3989"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-78.883927,78.779427)"
       id="use3999"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(156.08573,156.79797)"
       id="use4001"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
    <use
       transform="translate(-78.883927,235.54546)"
       id="use4003"
       x="0"
       y="0"
       width="388"
       height="388"
       xlink:href="#rect3104" />
  </g>
</svg>
"""

    confTema = ConfBoards.ConfigTabTema()
    confTema.restore_dic(tema["o_tema"])

    thumbail = confTema.x_png64Thumb
    if thumbail:
        pm = QtGui.QPixmap()
        png = base64.b64decode(thumbail)
        pm.loadFromData(png)
        icono = QtGui.QIcon(pm)
        return icono

    def ccolor(ncolor):
        x = QtGui.QColor(ncolor)
        return x.name()

    svg = svg.replace("WHITE", ccolor(confTema.x_colorBlancas))
    svg = svg.replace("BLACK", ccolor(confTema.x_colorNegras))
    svg = svg.replace("FONDO", ccolor(confTema.x_colorExterior))
    svg = svg.replace("RECUADRO", ccolor(confTema.x_colorFrontera))

    return QTVarios.svg2ico(svg.encode("utf-8"), tam)


class WNameTheme(QtWidgets.QDialog):
    def __init__(self, owner, theme, your_themes):
        super(WNameTheme, self).__init__(owner)

        self.theme = theme
        li_sections = [theme["SECCION"] for theme in your_themes if "SECCION" in theme]
        self.li_sections = list(set(li_sections))
        self.li_sections.sort()

        self.setWindowTitle(_("Theme"))
        self.setWindowIcon(Iconos.Temas())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        lb_name = Controles.LB2P(self, _("Name"))
        self.ed_name = Controles.ED(self, theme.get("NOMBRE", ""))
        ly_name = Colocacion.H().control(lb_name).control(self.ed_name)

        lb_section = Controles.LB2P(self, _("Section"))
        self.ed_section = Controles.ED(self, theme.get("SECCION", ""))
        bt_section = (
            Controles.PB(self, "", self.mira_section).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Section lists"))
        )
        ly_section = (
            Colocacion.H().control(lb_section).control(self.ed_section).espacio(-10).control(bt_section).relleno(1)
        )

        self.chb_pieces_set = Controles.CHB(self, _("Change piece set"), theme.get("CHANGE_PIECES", True))

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_acciones)

        layout = Colocacion.V().control(self.tb).espacio(16)
        layout.otro(ly_name).espacio(16)
        layout.otro(ly_section).espacio(16)
        layout.control(self.chb_pieces_set)
        layout.margen(6)
        self.setLayout(layout)

        self.ed_name.setFocus()
        if not self.li_sections:
            bt_section.hide()

    def mira_section(self):
        menu = QTVarios.LCMenuRondo(self)
        for section in self.li_sections:
            menu.opcion(section, section)
        resp = menu.lanza()
        if resp:
            self.ed_section.set_text(resp)

    def aceptar(self):
        name = self.ed_name.texto().strip()
        if name:
            self.theme["NOMBRE"] = self.ed_name.texto()
            self.theme["SECCION"] = self.ed_section.texto().strip()
            self.theme["CHANGE_PIECES"] = self.chb_pieces_set.valor()
            self.accept()
