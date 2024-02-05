import collections
import copy
import os
import time
import webbrowser
from io import BytesIO

import FasterCode
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

import Code
import Code.Board.WBoardColors as WBoardColors
from Code import Util, XRun
from Code.Base import Game
from Code.Base.Constantes import (
    WHITE,
    BLACK,
    TB_TAKEBACK,
    BLINDFOLD_CONFIG,
    ZVALUE_PIECE,
    BLINDFOLD_BLACK,
    BLINDFOLD_WHITE,
    BLINDFOLD_ALL,
)
from Code.Board import BoardElements, BoardMarkers, BoardBoxes, BoardSVGs, BoardTypes, BoardArrows, BoardCircles
from Code.Director import TabVisual, WindowDirector
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Iconos
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.Translations import TrListas


class RegKB:
    def __init__(self, key, flags):
        self.key = key
        self.flags = flags


class Board(QtWidgets.QGraphicsView):
    def __init__(self, parent, config_board, siMenuVisual=True, siDirector=True):
        super(Board, self).__init__(None)

        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(self.NoDrag)
        self.setInteractive(True)
        self.setTransformationAnchor(self.NoAnchor)
        self.escena = QtWidgets.QGraphicsScene(self)
        self.escena.setItemIndexMethod(self.escena.NoIndex)
        self.setScene(self.escena)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.main_window = parent
        self.configuration = Code.configuration

        self.variation_history = None

        self.siMenuVisual = siMenuVisual
        self.siDirector = siDirector and siMenuVisual
        self.siDirectorIcon = self.siDirector and self.configuration.x_director_icon
        self.dirvisual = None
        self.guion = None
        self.lastFenM2 = ""
        self.dbVisual = TabVisual.DBManagerVisual(
            self.configuration.ficheroRecursos, show_always=self.configuration.x_director_icon is False
        )
        self.current_graphlive = None
        self.dic_graphlive = None

        self.rutinaDropsPGN = None

        self.config_board = config_board

        self.blindfold = None
        self.blindfoldModoPosicion = False

        self.siInicializado = False

        self.last_position = None

        self.siF11 = False

        self._dispatchSize = None  # configuration en vivo, dirige a la rutina de la main_window afectada

        self.pendingRelease = None

        self.siPermitidoResizeExterno = True
        self.mensajero = None

        self.si_borraMovibles = True

        self.kb_buffer = []
        self.cad_buffer = ""
        self.dic_tr_keymoves = TrListas.dConv()

        self.hard_focus = True  # Controla que cada vez que se indique una posición active el foco al board

        self.allow_eboard = True

        self.minimum_size = 2

        self.active_premove = False

    def disable_hard_focus(self):
        self.hard_focus = False

    def init_kb_buffer(self):
        self.kb_buffer = []
        self.cad_buffer = ""

    def exec_kb_buffer(self, key, flags):
        if key == Qt.Key_Escape:
            self.init_kb_buffer()
            return

        if key in (Qt.Key_Enter, Qt.Key_Return):
            if self.kb_buffer:
                last = self.kb_buffer[-1]
                key = last.key
                flags = last.flags | QtCore.Qt.AltModifier
            else:
                return

        if key in (Qt.Key_Backspace, Qt.Key_Delete):
            if self.allow_takeback():
                self.main_window.manager.run_action(TB_TAKEBACK)
                return

        is_alt = (flags & QtCore.Qt.AltModifier) > 0
        is_shift = (flags & QtCore.Qt.ShiftModifier) > 0
        is_ctrl = (flags & QtCore.Qt.ControlModifier) > 0

        okseguir = False

        if is_alt or is_ctrl:

            # CTRL-C/ : copy fen al clipboard
            if key == Qt.Key_C:
                if (self.configuration.x_copy_ctrl and is_ctrl) or (not self.configuration.x_copy_ctrl and is_alt):
                    if is_shift:
                        if hasattr(self.main_window, "manager") and hasattr(
                                self.main_window.manager, "save_pgn_clipboard"
                        ):
                            self.main_window.manager.save_pgn_clipboard()
                    else:
                        QTUtil.ponPortapapeles(self.last_position.fen())
                        QTUtil2.message_bold(self, _("FEN is in clipboard"))

            # ALT-B : Menu visual
            elif is_alt and key == Qt.Key_B:
                self.lanzaMenuVisual()

            elif is_ctrl and (key in (Qt.Key_Plus, Qt.Key_Minus)):
                ap = self.config_board.anchoPieza()
                ap += 2 * (1 if key == Qt.Key_Plus else -1)
                if ap >= 10:
                    self.config_board.anchoPieza(ap)
                    self.config_board.guardaEnDisco()
                    self.cambiadoAncho()
                    return

            # ALT-F -> Rota board
            elif is_alt and key == Qt.Key_F:
                self.intentaRotarBoard(None)

            # ALT-I Save image to clipboard (CTRL->no border)
            elif key == Qt.Key_I:
                self.save_as_img(is_ctrl=is_ctrl, is_alt=is_alt)
                QTUtil2.temporary_message(self.main_window, _("Board image is in clipboard"), 1.2)

            # ALT-J Save image to file (CTRL->no border)
            elif key == Qt.Key_J:
                path = SelectFiles.salvaFichero(self, _("File to save"), self.configuration.x_save_folder, "png", False)
                if path:
                    self.save_as_img(path, "png", is_ctrl=is_ctrl, is_alt=is_alt)
                    self.configuration.x_save_folder = os.path.dirname(path)
                    self.configuration.graba()

            # ALT-K
            elif is_alt and key == Qt.Key_K:
                self.showKeys()

            # ALT-L
            elif is_alt and key == Qt.Key_L:
                webbrowser.open("https://lichess.org/analysis/standard/" + self.last_position.fen())

            # ALT-T
            elif is_alt and key == Qt.Key_T:
                webbrowser.open("https://old.chesstempo.com/gamedb/fen/" + self.last_position.fen())

            # ALT-X
            elif is_alt and key == Qt.Key_X:
                self.play_current_position()

            elif (
                    hasattr(self.main_window, "manager")
                    and self.main_window.manager
                    and key in (Qt.Key_P, Qt.Key_N, Qt.Key_C)
            ):
                # P -> show information
                if key == Qt.Key_P and hasattr(self.main_window.manager, "pgnInformacion"):
                    self.main_window.manager.pgnInformacion()
                # ALT-N -> non distract mode
                elif key == Qt.Key_N and hasattr(self.main_window.manager, "nonDistractMode"):
                    self.main_window.manager.nonDistractMode()
                # ALT-C -> show captures
                elif key == Qt.Key_C and hasattr(self.main_window.manager, "capturas"):
                    self.main_window.manager.capturas()
                else:
                    okseguir = True
        else:
            okseguir = True

        if not okseguir:
            if self.kb_buffer:
                self.kb_buffer = self.kb_buffer[:-1]
                self.cad_buffer = ""
            return

        if self.mensajero and self.pieces_are_active and not is_alt:
            # Entrada directa
            if 128 > key > 32:
                self.cad_buffer += chr(key)
            if len(self.cad_buffer) >= 2:
                FasterCode.set_fen(self.last_position.fen())
                li = FasterCode.get_exmoves()
                busca = self.cad_buffer.lower()

                exmove_ok = None

                for exmove in li:
                    a1h8 = exmove.move()
                    if busca.endswith(a1h8):
                        exmove_ok = exmove
                        break
                if exmove_ok is None:
                    for exmove in li:
                        san = exmove.san().replace("+", "").replace("#", "")
                        if len(san) > 2:
                            if san[-1].upper() in self.dic_tr_keymoves:
                                san = san[:-1] + self.dic_tr_keymoves[san[-1].upper()]
                            elif san[0].upper() in self.dic_tr_keymoves:
                                san = self.dic_tr_keymoves[san[0].upper()] + san[1:]
                        if (
                                busca.endswith(san.lower())
                                or busca.endswith(san.lower().replace("=", ""))
                                or (san == "O-O-O" and busca.endswith("o3"))
                                or (san == "O-O" and busca.endswith("o2"))
                        ):
                            if exmove_ok:
                                if len(san) > len(exmove_ok.san()):
                                    exmove_ok = exmove
                            else:
                                exmove_ok = exmove

                if exmove_ok:
                    self.init_kb_buffer()
                    self.mensajero(exmove_ok.xfrom(), exmove_ok.xto(), exmove_ok.promotion())

    def sizeHint(self):
        return QtCore.QSize(self.ancho + 6, self.ancho + 6)

    def xremoveItem(self, item):
        scene = item.scene()
        if scene:
            scene.removeItem(item)

    def keyPressEvent(self, event):
        k = event.key()
        m = int(event.modifiers())

        if Qt.Key_F1 <= k <= Qt.Key_F10:
            if self.dirvisual and self.dirvisual.keyPressEvent(event):
                return
            if (m & QtCore.Qt.ControlModifier) > 0:
                if k == Qt.Key_F1:
                    self.borraUltimoMovible()
                elif k == Qt.Key_F2:
                    self.borraMovibles()
            elif self.lanzaDirector():
                self.dirvisual.keyPressEvent(event)
            return

        event.ignore()

        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace) and len(self.dicMovibles) > 0:
            if self.dirvisual:
                self.dirvisual.keyPressEvent(event)
            else:
                if k == QtCore.Qt.Key_Backspace:
                    self.borraUltimoMovible()
                elif k == QtCore.Qt.Key_Delete:
                    self.borraMovibles()
            return

        self.exec_kb_buffer(k, m)

    def activaMenuVisual(self, siActivar):
        self.siMenuVisual = siActivar

    def permitidoResizeExterno(self, sino=None):
        if sino is None:
            return self.siPermitidoResizeExterno
        else:
            self.siPermitidoResizeExterno = sino

    def maximizaTam(self, activadoF11):
        self.siF11 = activadoF11
        self.config_board.anchoPieza(1000)
        self.config_board.guardaEnDisco()
        self.cambiadoAncho()

    def normalTam(self, xanchoPieza):
        self.siF11 = False
        self.config_board.anchoPieza(xanchoPieza)
        self.config_board.guardaEnDisco()
        self.cambiadoAncho()

    def cambiadoAncho(self):
        is_white_bottom = self.is_white_bottom
        self.set_width()
        if not is_white_bottom:
            self.intentaRotarBoard(None)
        if self._dispatchSize:
            self._dispatchSize()

    def siMaximizado(self):
        return self.config_board.anchoPieza() == 1000

    def crea(self):
        nom_pieces_ori = self.config_board.nomPiezas()
        if self.blindfold:
            self.piezas = Piezas.Blindfold(nom_pieces_ori, self.blindfold)
        else:
            self.piezas = Code.all_pieces.selecciona(nom_pieces_ori)
        self.anchoPieza = self.config_board.anchoPieza()
        self.margenPieza = 2

        self.colorBlancas = self.config_board.colorBlancas()
        self.colorNegras = self.config_board.colorNegras()
        self.colorFondo = self.config_board.colorFondo()
        self.png64Blancas = self.config_board.png64Blancas()
        self.png64Negras = self.config_board.png64Negras()
        self.png64Fondo = self.config_board.png64Fondo()
        self.png64Exterior = self.config_board.png64Exterior()
        self.transBlancas = self.config_board.transBlancas()
        self.transNegras = self.config_board.transNegras()
        self.transSideIndicator = self.config_board.transSideIndicator()

        self.extended_fondo = self.config_board.extendedColor()
        if self.extended_fondo:
            self.colorExterior = self.colorFondo
            self.png64Exterior = self.png64Fondo
        else:
            self.colorExterior = self.config_board.colorExterior()
            self.png64Exterior = self.png64Exterior

        self.colorTexto = self.config_board.colorTexto()

        self.colorFrontera = self.config_board.colorFrontera()

        self.exePulsadoNum = None
        self.exePulsadaLetra = None
        self.atajosRaton = None
        self.pieces_are_active = False  # Control adicional, para responder a eventos del raton
        self.side_pieces_active = None

        self.siPosibleRotarBoard = True

        self.is_white_bottom = True

        self.nCoordenadas = self.config_board.nCoordenadas()

        self.set_width()

    def calculaAnchoMXpieza(self):
        at = QTUtil.desktop_height() - 50 - 64
        if self.siF11:
            at += 50 + 64
        tr = 1.0 * self.config_board.tamRecuadro() / 100.0
        mp = self.margenPieza

        ap = int((1.0 * at - 16.0 * mp) / (8.0 + tr * 92.0 / 80))
        return ap

    def set_width(self):
        dTam = {16: (9, 23), 24: (10, 29), 32: (12, 33), 48: (14, 38), 64: (16, 42), 80: (18, 46)}

        ap = self.config_board.anchoPieza()
        if ap == 1000:
            ap = self.calculaAnchoMXpieza()
        if ap in dTam:
            self.puntos, self.margenCentro = dTam[ap]
        else:
            mx = 999999
            kt = 0
            for k in dTam:
                mt = abs(k - ap)
                if mt < mx:
                    mx = mt
                    kt = k
            pt, mc = dTam[kt]
            self.puntos = pt * ap // kt
            self.margenCentro = mc * ap // kt

        self.anchoPieza = ap

        self.width_square = ap + self.margenPieza * 2
        self.tamFrontera = self.margenCentro * 3.0 // 46.0

        self.margenCentro = self.margenCentro * self.config_board.tamRecuadro() // 100

        fx = self.config_board.tamFrontera()
        self.tamFrontera = int(self.tamFrontera * fx // 100)
        if fx > 0 and self.tamFrontera == 0:
            self.tamFrontera = 2
        if self.tamFrontera % 2 == 1:
            self.tamFrontera += 1

        self.puntos = self.puntos * self.config_board.tamLetra() * 12 // 1000

        # Guardamos las piezas

        if self.siInicializado:
            li_pz = []
            for cpieza, piezaSC, is_active in self.liPiezas:
                if is_active:
                    physical_pos = piezaSC.bloquePieza
                    f = physical_pos.row
                    c = physical_pos.column
                    posA1H8 = chr(c + 96) + str(f)
                    li_pz.append((cpieza, posA1H8))

            ap, apc = self.pieces_are_active, self.side_pieces_active
            siFlecha = self.flechaSC is not None

            self.rehaz()

            if li_pz:
                for cpieza, a1h8 in li_pz:
                    self.creaPieza(cpieza, a1h8)
            if ap:
                self.activate_side(apc)
                self.set_side_indicator(apc)

            if siFlecha:
                self.resetFlechaSC()

        else:
            self.rehaz()

        self.siInicializado = True
        self.init_kb_buffer()

    def rehaz(self):
        self.escena.clear()
        self.liPiezas = []
        self.liFlechas = []
        self.flechaSC = None
        self.dicMovibles = collections.OrderedDict()  # Flechas, Marcos, SVG
        self.idUltimoMovibles = 0
        self.side_indicator_sc = None

        self.is_white_bottom = True

        # Completo
        is_png = False
        if self.extended_fondo:
            if self.png64Fondo:
                cajon = BoardTypes.Imagen()
                cajon.pixmap = self.png64Fondo
                is_png = True
            else:
                cajon = BoardTypes.Caja()
                cajon.colorRelleno = self.colorFondo
        else:
            if self.png64Exterior:
                cajon = BoardTypes.Imagen()
                cajon.pixmap = self.png64Exterior
                is_png = True
            else:
                cajon = BoardTypes.Caja()
                cajon.colorRelleno = self.colorExterior
        self.ancho = ancho = cajon.physical_pos.alto = cajon.physical_pos.ancho = (
                self.width_square * 8 + self.margenCentro * 2 + self.tamFrontera * 2
        )
        cajon.physical_pos.orden = 1
        cajon.tipo = QtCore.Qt.NoPen
        self.setFixedSize(ancho, ancho)
        if is_png:
            self.cajonSC = BoardElements.PixmapSC(self.escena, cajon)
        else:
            self.cajonSC = BoardElements.CajaSC(self.escena, cajon)

        # Fondo squares
        if self.png64Fondo:
            baseCasillas = BoardTypes.Imagen()
            baseCasillas.pixmap = self.png64Fondo
        else:
            baseCasillas = BoardTypes.Caja()
            baseCasillas.colorRelleno = self.colorFondo
        baseCasillas.physical_pos.x = baseCasillas.physical_pos.y = self.margenCentro + self.tamFrontera / 2
        baseCasillas.physical_pos.alto = baseCasillas.physical_pos.ancho = self.width_square * 8
        baseCasillas.physical_pos.orden = 2
        baseCasillas.tipo = 0
        if self.png64Fondo:
            self.baseCasillasSC = BoardElements.PixmapSC(self.escena, baseCasillas)
        else:
            self.baseCasillasSC = BoardElements.CajaSC(self.escena, baseCasillas)
        if self.extended_fondo:
            self.baseCasillasSC.hide()

        # Frontera
        base_casillas_f = BoardTypes.Caja()
        base_casillas_f.grosor = self.tamFrontera
        base_casillas_f.physical_pos.x = base_casillas_f.physical_pos.y = self.margenCentro
        base_casillas_f.physical_pos.alto = base_casillas_f.physical_pos.ancho = (
                self.width_square * 8 + self.tamFrontera
        )
        base_casillas_f.physical_pos.orden = 3
        base_casillas_f.colorRelleno = -1
        base_casillas_f.color = self.colorFrontera
        base_casillas_f.redEsquina = 0  # self.tamFrontera
        base_casillas_f.tipo = 1

        if base_casillas_f.grosor > 0:
            self.baseCasillasFSC = BoardElements.CajaSC(self.escena, base_casillas_f)

        # squares
        def hazCasillas(tipo, png64, color, transparencia):
            with_pixmap = len(png64) > 0
            if with_pixmap:
                square = BoardTypes.Imagen()
                square.pixmap = png64
                pixmap = None
            else:
                square = BoardTypes.Caja()
                square.tipo = QtCore.Qt.NoPen
                square.colorRelleno = color
            square.physical_pos.orden = 4
            square.physical_pos.alto = square.physical_pos.ancho = self.width_square
            opacity = 100.0 - transparencia * 1.0
            for x in range(4):
                for y in range(8):
                    una = square.copia()

                    k1 = k = self.margenCentro + self.tamFrontera // 2
                    if y % 2 == tipo:
                        k += self.width_square
                    una.physical_pos.x = k + x * 2 * self.width_square
                    una.physical_pos.y = k1 + y * self.width_square
                    if with_pixmap:
                        casillaSC = BoardElements.PixmapSC(self.escena, una, pixmap=pixmap)
                        pixmap = casillaSC.pixmap
                    else:
                        casillaSC = BoardElements.CajaSC(self.escena, una)
                    if opacity != 100.0:
                        casillaSC.setOpacity(opacity / 100.0)

        hazCasillas(1, self.png64Blancas, self.colorBlancas, self.transBlancas)
        hazCasillas(0, self.png64Negras, self.colorNegras, self.transNegras)

        # Coordenadas
        self.liCoordenadasVerticales = []
        self.liCoordenadasHorizontales = []

        ancho_texto = self.puntos + 4
        if self.margenCentro >= self.puntos or self.config_board.sepLetras() < 0:
            coord = BoardTypes.Texto()
            tipo_letra = self.config_board.tipoLetra()
            peso = 75 if self.config_board.siBold() else 50
            coord.tipoLetra = BoardTypes.TipoLetra(tipo_letra, self.puntos, peso=peso)
            coord.physical_pos.ancho = ancho_texto
            coord.physical_pos.alto = ancho_texto
            coord.physical_pos.orden = 7
            coord.colorTexto = self.colorTexto

            p_casillas = baseCasillas.physical_pos
            p_frontera = base_casillas_f.physical_pos
            gap_casilla = (self.width_square - ancho_texto) / 2
            sep = (
                    self.margenCentro * self.config_board.sepLetras() * 38 / 50000
            )  # ancho = 38 -> sep = 5 -> sepLetras = 100

            def norm(x):
                if x < 0:
                    return 0
                if x > (ancho - ancho_texto):
                    return ancho - ancho_texto
                return x

            hx = norm(p_casillas.x + gap_casilla)
            hyS = norm(p_frontera.y + p_frontera.alto + sep)
            hyN = norm(p_frontera.y - ancho_texto - sep)

            vy = norm(p_casillas.y + gap_casilla)
            vxE = norm(p_frontera.x + p_frontera.ancho + sep)
            vxO = norm(p_frontera.x - ancho_texto - sep)

            for x in range(8):

                if self.nCoordenadas > 0:  # 2 o 3 o 4 o 5 o 6
                    d = {  # hS,     vO,     hN,     vE
                        2: (True, True, False, False),
                        3: (False, True, True, False),
                        4: (True, True, True, True),
                        5: (False, False, True, True),
                        6: (True, False, False, True),
                    }
                    li_co = d[self.nCoordenadas]
                    hor = coord.copia()
                    hor.valor = chr(97 + x)
                    hor.alineacion = "c"
                    hor.physical_pos.x = hx + x * self.width_square

                    if li_co[0]:
                        hor.physical_pos.y = hyS
                        horSC = BoardElements.TextoSC(self.escena, hor, self.pulsadaLetra)
                        self.liCoordenadasHorizontales.append(horSC)

                    if li_co[2]:
                        hor = hor.copia()
                        hor.physical_pos.y = hyN
                        horSC = BoardElements.TextoSC(self.escena, hor, self.pulsadaLetra)
                        self.liCoordenadasHorizontales.append(horSC)

                    ver = coord.copia()
                    ver.valor = chr(56 - x)
                    ver.alineacion = "c"
                    ver.physical_pos.y = vy + x * self.width_square

                    if li_co[1]:
                        ver.physical_pos.x = vxO
                        verSC = BoardElements.TextoSC(self.escena, ver, self.pulsadoNum)
                        self.liCoordenadasVerticales.append(verSC)

                    if li_co[3]:
                        ver = ver.copia()
                        ver.physical_pos.x = vxE
                        verSC = BoardElements.TextoSC(self.escena, ver, self.pulsadoNum)
                        self.liCoordenadasVerticales.append(verSC)

        # Indicador de color activo
        p_frontera = base_casillas_f.physical_pos
        pCajon = cajon.physical_pos
        ancho = pCajon.ancho - (p_frontera.x + p_frontera.ancho)
        gap = int(ancho / 8) * 2

        indicador = BoardTypes.Circulo()
        indicador.physical_pos.x = (p_frontera.x + p_frontera.ancho) + gap / 2
        indicador.physical_pos.y = (p_frontera.y + p_frontera.alto) + gap / 2
        indicador.physical_pos.ancho = indicador.physical_pos.alto = ancho - gap
        indicador.physical_pos.orden = 2
        indicador.color = self.colorFrontera
        indicador.grosor = 1
        indicador.tipo = 1
        indicador.sur = indicador.physical_pos.y
        indicador.norte = gap / 2
        self.side_indicator_sc = BoardElements.CirculoSC(self.escena, indicador, rutina=self.intentaRotarBoard)

        if self.transSideIndicator != 100.0:
            self.side_indicator_sc.setOpacity((100.0 - self.transSideIndicator * 1.0) / 100.0)

        # Lanzador de menu visual
        self.indicadorSC_menu = None
        self.scriptSC_menu = None
        if self.siMenuVisual:
            indicador_menu = BoardTypes.Imagen()
            indicador_menu.physical_pos.x = 2
            if self.configuration.x_position_tool_board == "B":
                indicador_menu.physical_pos.y = self.ancho - 24
            else:
                indicador_menu.physical_pos.y = 2

            indicador_menu.physical_pos.ancho = indicador_menu.physical_pos.alto = ancho - 2 * gap
            indicador_menu.physical_pos.orden = 2
            indicador_menu.color = self.colorFrontera
            indicador_menu.grosor = 1
            indicador_menu.tipo = 1
            indicador_menu.sur = indicador.physical_pos.y
            indicador_menu.norte = gap / 2
            self.indicadorSC_menu = BoardElements.PixmapSC(
                self.escena, indicador_menu, pixmap=Iconos.pmSettings(), rutina=self.lanzaMenuVisual
            )
            self.indicadorSC_menu.setOpacity(0.50 if self.configuration.x_opacity_tool_board == 10 else 0.01)

            if self.siDirectorIcon:
                script = BoardTypes.Imagen()
                script.physical_pos.x = p_frontera.x - ancho + ancho
                if self.configuration.x_position_tool_board == "B":
                    script.physical_pos.y = p_frontera.y + p_frontera.alto + 2 * gap
                else:
                    script.physical_pos.y = 0

                script.physical_pos.ancho = script.physical_pos.alto = ancho - 2 * gap
                script.physical_pos.orden = 2
                script.color = self.colorFrontera
                script.grosor = 1
                script.tipo = 1
                script.sur = indicador.physical_pos.y
                script.norte = gap / 2
                self.scriptSC_menu = BoardElements.PixmapSC(
                    self.escena, script, pixmap=Iconos.pmLampara(), rutina=self.lanzaGuionAuto
                )
                self.scriptSC_menu.hide()
                self.scriptSC_menu.setOpacity(0.70)

        self.init_kb_buffer()

        self.setSceneRect(0, 0, self.ancho, self.ancho)

    def setAcceptDropPGNs(self, rutinaDropsPGN):
        self.baseCasillasSC.setAcceptDrops(rutinaDropsPGN is not None)
        self.rutinaDropsPGN = rutinaDropsPGN

    def dropEvent(self, event):
        if self.rutinaDropsPGN is not None:
            mimeData = event.mimeData()
            if mimeData.hasUrls():
                li = mimeData.urls()
                if len(li) > 0:
                    self.rutinaDropsPGN(li[0].path().strip("/"))
        event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()

    def showKeys(self):
        def alt(key):
            return _("ALT") + " %s" % key

        def ctrl(key):
            return _("CTRL") + " %s" % key

        def ctrl_alt(key):
            return "%s %s %s" % (_("CTRL"), _("ALT"), key)

        li_keys = [
            (alt("B"), _("Board menu")),
            (None, None),
            (alt("F"), _("Flip the board")),
            (None, None),
            (ctrl("C") if Code.configuration.x_copy_ctrl else alt("C"), _("Copy FEN to clipboard")),
            (None, None),
            (alt("I"), _("Copy board as image to clipboard")),
            (ctrl("I"), _("Copy board as image to clipboard") + " (%s)" % _("without border")),
            (ctrl_alt("I"), _("Copy board as image to clipboard") + " (%s)" % _("without coordinates")),
            (alt("J"), _("Copy board as image to a file")),
            (ctrl("J"), _("Copy board as image to a file") + " (%s)" % _("without border")),
            (ctrl_alt("J"), _("Copy board as image to a file") + " (%s)" % _("without coordinates")),
        ]
        if self.pieces_are_active:
            li_keys.append((None, None))
            li_keys.append(("a1 ... h8", _("To indicate origin and destination of a move")))

        if hasattr(self.main_window, "manager") and self.main_window.manager:
            if hasattr(self.main_window.manager, "gridRightMouse"):
                li_keys.append((None, None))
                li_keys.append((alt("P"), _("Show/Hide PGN information")))
            li_keys.append((None, None))
            li_keys.append((alt("N"), _("Activate/Deactivate non distract mode")))

            if hasattr(self.main_window.manager, "listHelpTeclado"):
                li_keys.append((None, None))
                li_keys.extend(self.main_window.manager.listHelpTeclado())

        li_keys.append((None, None))
        li_keys.append((alt("L"), _("Open position in LiChess")))
        li_keys.append((alt("T"), _("Open position in ChessTempo")))
        li_keys.append((alt("X"), _("Play current position")))
        li_keys.append((None, None))
        li_keys.append(("F11", _("Full screen On/Off")))
        li_keys.append(("F12", _("Minimize to the tray icon")))

        if hasattr(self.main_window, "manager") and hasattr(self.main_window.manager, "save_pgn_clipboard"):
            li_keys.insert(
                5,
                (
                    "%s %s C"
                    % (_("CTRL") if Code.configuration.x_copy_ctrl else _("ALT"), _("SHIFT || From keyboard")),
                    _("Copy PGN to clipboard"),
                ),
            )

        rondo = QTVarios.rondoPuntos()
        menu = QTVarios.LCMenu(self)
        menu.opcion(None, _("Active keys"), Iconos.Rename())
        menu.separador()
        for key, mess in li_keys:
            if key is None:
                menu.separador()
            else:
                menu.opcion(None, "%s [%s]" % (mess, key), rondo.otro())
        menu.lanza()

    def lanzaMenuVisual(self, siIzquierdo=False):
        if not self.siMenuVisual:
            return

        menu = QTVarios.LCMenu(self)

        menu.opcion("colors", _("Colors"), Iconos.Colores())
        menu.separador()
        menu.opcion("pieces", _("Pieces"), self.piezas.icono("K"))
        menu.separador()
        if not self.main_window.isMaximized():
            menu.opcion("size", _("Change board size"), Iconos.ResizeBoard())
            menu.separador()

        submenu = menu.submenu(_("By default"), Iconos.Defecto())
        submenu.opcion("def_todo1", "1", Iconos.m1())
        submenu.opcion("def_todo2", "2", Iconos.m2())
        # menu.opcion("def_todo", _("By default"), Iconos.Defecto())

        menu.separador()
        if self.siDirector:
            menu.opcion("director", _("Director") + " [%s] " % _("F1-F10"), Iconos.Director())
            menu.separador()

        if self.siPosibleRotarBoard:
            menu.opcion("girar", _("Flip the board") + " [%s-F]" % _("ALT"), Iconos.JS_Rotacion())
            menu.separador()

        menu.opcion("keys", _("Active keys") + " [%s-K]" % _("ALT"), Iconos.Rename())
        menu.separador()

        resp = menu.lanza()
        if resp is None:
            return
        elif resp == "colors":
            menucol = QTVarios.LCMenu(self)
            menucol.opcion("edit", _("Edit"), Iconos.EditarColores())
            menucol.separador()
            liTemas = Util.restore_pickle(Code.configuration.ficheroTemas)
            if liTemas:
                WBoardColors.ponMenuTemas(menucol, liTemas, "tt_")
                menucol.separador()
            for entry in Util.listdir(Code.path_resource("Themes")):
                fich = entry.name
                if fich.lower().endswith(".lktheme3"):
                    self.fich_ = fich[:-9]
                    name = self.fich_
                    menucol.opcion("ot_" + fich, name, Iconos.Division())
            resp = menucol.lanza()
            if resp:
                if resp == "edit":
                    w = WBoardColors.WBoardColors(self)
                    w.exec_()
                else:
                    self.ponColores(liTemas, resp)

        elif resp == "pieces":
            menup = QTVarios.LCMenu(self)
            li = []
            for x in Util.listdir(Code.path_resource("Pieces")):
                try:
                    if x.is_dir():
                        ico = Code.all_pieces.icono("K", x.name)
                        li.append((x.name, ico))
                except:
                    pass
            li.sort(key=lambda x: x[0])
            for x, ico in li:
                menup.opcion(x, x, ico)
            resp = menup.lanza()
            if resp:
                self.cambiaPiezas(resp)

        elif resp == "size":
            self.cambiaSize()

        elif resp == "girar":
            self.rotaBoard()

        elif resp == "director":
            self.lanzaDirector()

        elif resp == "keys":
            self.showKeys()

        elif resp.startswith("def_todo"):
            self.configuration.change_theme_num(int(resp[-1]))
            self.config_board = self.configuration.resetConfBoard(
                self.config_board.id(), self.config_board.anchoPieza()
            )
            if self.config_board.is_base:
                nom_pieces_ori = self.config_board.nomPiezas()
                self.cambiaPiezas(nom_pieces_ori)
            self.reset(self.config_board)
            if hasattr(self.main_window.parent, "ajustaTam"):
                self.main_window.parent.ajustaTam()

    def lanzaDirector(self):
        if self.siDirector:
            if self.dirvisual:
                self.dirvisual.terminar()
                self.dirvisual = None
                return False
            else:
                self.dirvisual = WindowDirector.Director(self)
                self.dirvisual.guion.play(editing=True)
            return True
        else:
            return False

    def close_visual_script(self):
        if self.guion is not None:
            self.guion.cierraPizarra()
            self.guion.cerrado = True
            self.guion = None

    def lanzaGuionAuto(self):
        if self.guion is not None:
            self.guion.restoreBoard(siBorraMoviblesAhora=True)
        else:
            self.lanzaGuion()

    def lanzaGuion(self):
        if self.guion is not None:
            self.close_visual_script()
        else:
            self.guion = TabVisual.Guion(self)
            self.guion.recupera()
            self.guion.play()

    def cambiaSize(self):
        imp = WTamBoard(self)
        imp.colocate()
        imp.exec_()

    def cambiaPiezas(self, cual):
        self.config_board.cambiaPiezas(cual)
        self.config_board.guardaEnDisco()
        ap, apc = self.pieces_are_active, self.side_pieces_active
        siFlecha = self.flechaSC is not None
        atajosRaton = self.atajosRaton

        self.crea()
        if ap:
            self.activate_side(apc)
            self.set_side_indicator(apc)

        self.atajosRaton = atajosRaton

        if siFlecha:
            self.resetFlechaSC()

        self.init_kb_buffer()

        if self.config_board.is_base:
            nom_pieces_ori = self.config_board.nomPiezas()
            Code.all_pieces.save_all_png(nom_pieces_ori, 30)
            Delegados.generaPM(self.piezas)
            self.main_window.pgnRefresh()
            if hasattr(self.main_window.manager, "put_view"):
                self.main_window.manager.put_view()

    def ponColores(self, liTemas, resp):
        if resp.startswith("tt_"):
            tema = liTemas[int(resp[3:])]

        else:
            fich = Code.path_resource("Themes/%s" % resp[3:])
            tema = WBoardColors.eligeTema(self, fich)

        if tema:
            self.config_board.leeTema(tema["o_tema"])
            if "o_base" in tema:
                self.config_board.leeBase(tema["o_base"])

            self.config_board.guardaEnDisco()
            pac = self.pieces_are_active
            pac_sie = self.side_pieces_active
            self.crea()
            if pac and pac_sie is not None:
                self.activate_side(pac_sie)

    def reset(self, config_board):
        self.config_board = config_board
        for item in self.escena.items():
            self.xremoveItem(item)
            del item
        pac = self.pieces_are_active
        pac_sie = self.side_pieces_active
        self.crea()
        if pac and pac_sie is not None:
            self.activate_side(pac_sie)

    def key_current_graphlive(self, event):
        m = int(event.modifiers())
        key = ""
        if (m & QtCore.Qt.ControlModifier) > 0:
            key = "CTRL"
        if (m & QtCore.Qt.AltModifier) > 0:
            key += "ALT"
        if (m & QtCore.Qt.ShiftModifier) > 0:
            key += "SHIFT"
        return key

    def mousePressGraphLive(self, event, a1h8):
        if not self.configuration.x_direct_graphics:
            return
        key = self.key_current_graphlive(event)
        key += "MR"
        if self.dic_graphlive is None:
            self.dic_graphlive = self.readGraphLive()
        elem = self.dic_graphlive.get(key, None)
        if elem:
            elem.a1h8 = a1h8 + a1h8
            if TabVisual.TP_FLECHA == elem.TP:
                self.current_graphlive = self.creaFlecha(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_MARCO == elem.TP:
                self.current_graphlive = self.creaMarco(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_CIRCLE == elem.TP:
                self.current_graphlive = self.creaCircle(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_MARKER == elem.TP:
                self.current_graphlive = self.creaMarker(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_SVG == elem.TP:
                self.current_graphlive = self.creaSVG(elem, False)
                self.current_graphlive.mousePressExt(event)

            self.current_graphlive.TP = elem.TP

    def mouseMoveGraphLive(self, event):
        if not self.configuration.x_direct_graphics:
            return
        if self.current_graphlive.TP in (TabVisual.TP_FLECHA, TabVisual.TP_MARCO):
            self.current_graphlive.mouseMoveExt(event)
        self.current_graphlive.update()

    def readGraphLive(self):
        rel = {
            0: "MR",
            1: "ALTMR",
            2: "SHIFTMR",
            3: "CTRLMR",
            4: "CTRLALTMR",
            5: "CTRLSHIFTMR",
            6: "MR1",
            7: "ALTMR1",
            8: "SHIFTMR1",
        }
        dic = {}
        db = self.dbVisual
        li = self.dbVisual.dbConfig["SELECTBANDA"]
        if li:
            for xid, pos in li:
                if xid.startswith("_F"):
                    xdb = db.dbFlechas
                    tp = TabVisual.TP_FLECHA
                    obj = BoardTypes.Flecha()
                elif xid.startswith("_M"):
                    xdb = db.dbMarcos
                    tp = TabVisual.TP_MARCO
                    obj = BoardTypes.Marco()
                elif xid.startswith("_D"):
                    xdb = db.dbCircles
                    tp = TabVisual.TP_CIRCLE
                    obj = BoardTypes.Circle()
                elif xid.startswith("_S"):
                    xdb = db.dbSVGs
                    tp = TabVisual.TP_SVG
                    obj = BoardTypes.SVG()
                elif xid.startswith("_X"):
                    xdb = db.dbMarkers
                    tp = TabVisual.TP_MARKER
                    obj = BoardTypes.Marker()
                else:
                    continue
                if pos in rel:
                    cnum_id = xid[3:]
                    dic_current = xdb[cnum_id]
                    if dic_current:
                        obj.restore_dic(dic_current)
                    obj.TP = tp
                    obj.id = int(cnum_id)
                    obj.tpid = (tp, obj.id)
                    dic[rel[pos]] = obj
        return dic

    def remove_current_graphlive(self):
        if self.current_graphlive:
            self.current_graphlive.hide()
            del self.current_graphlive
            self.current_graphlive = None
            self.borraUltimoMovible()

    def mouseReleaseGraphLive(self, event):
        if not self.configuration.x_direct_graphics:
            return
        h8 = self.event2a1h8(event)
        if h8 is not None:
            a1 = self.current_graphlive.bloqueDatos.a1h8[:2]
            key = self.key_current_graphlive(event)
            if a1 == h8 and not key.startswith("CTRL"):
                self.remove_current_graphlive()
                key += "MR1"
                if key not in self.dic_graphlive:
                    return

                elem = self.dic_graphlive[key]
                elem.a1h8 = a1 + a1
                tp = elem.TP
                if tp == TabVisual.TP_SVG:
                    self.current_graphlive = self.creaSVG(elem)
                    self.current_graphlive.TP = tp
                elif tp == TabVisual.TP_MARCO:
                    self.current_graphlive = self.creaMarco(elem)
                    self.current_graphlive.TP = tp
                elif tp == TabVisual.TP_CIRCLE:
                    self.current_graphlive = self.creaCircle(elem)
                    self.current_graphlive.TP = tp
                elif tp == TabVisual.TP_MARKER:
                    self.current_graphlive = self.creaMarker(elem)
                    self.current_graphlive.TP = tp

            else:
                self.current_graphlive.ponA1H8(a1 + h8)
            keys = list(self.dicMovibles.keys())
            if len(keys) > 1:
                last = len(keys) - 1
                bd_last = self.current_graphlive.bloqueDatos
                st = set()
                for n, (pos, item) in enumerate(self.dicMovibles.items()):
                    if n != last:
                        bd = item.bloqueDatos
                        if (
                                hasattr(bd_last, "tpid")
                                and hasattr(bd, "tpid")
                                and bd_last.tpid == bd.tpid
                                and bd_last.a1h8 in (bd.a1h8, bd.a1h8[2:] + bd.a1h8[:2])
                        ):
                            st.add(self.current_graphlive)
                            st.add(item)
                for item in st:
                    self.borraMovible(item)

            self.refresh()
        self.current_graphlive = None

    def mouseMoveEvent(self, event):
        if self.dirvisual and self.dirvisual.mouseMoveEvent(event):
            return
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.width_square * 8)
        siDentro = (minimo < x < maximo) and (minimo < y < maximo)
        if siDentro and self.current_graphlive:
            return self.mouseMoveGraphLive(event)

        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.dirvisual and self.dirvisual.mouseReleaseEvent(event):
            return
        if self.pendingRelease:
            for objeto in self.pendingRelease:
                objeto.hide()
                del objeto
            self.escena.update()
            self.update()
            self.pendingRelease = None
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        if self.current_graphlive:
            self.mouseReleaseGraphLive(event)

    def event2a1h8(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.width_square * 8)
        if (minimo < x < maximo) and (minimo < y < maximo):
            xc = 1 + int(float(x - self.margenCentro) / self.width_square)
            yc = 1 + int(float(y - self.margenCentro) / self.width_square)

            if self.is_white_bottom:
                yc = 9 - yc
            else:
                xc = 9 - xc

            f = chr(48 + yc)
            c = chr(96 + xc)
            a1h8 = c + f
        else:
            a1h8 = None
        return a1h8

    def mousePressEvent(self, event):
        if self.dirvisual:
            self.dirvisual.mousePressEvent(event)
            return

        a1h8 = self.event2a1h8(event)

        si_right = event.button() == QtCore.Qt.RightButton
        if si_right:
            if a1h8:
                return self.mousePressGraphLive(event, a1h8)
            else:
                self.lanzaMenuVisual()
                return

        si_izq = event.button() == QtCore.Qt.LeftButton
        if si_izq and a1h8 is not None:
            self.borraMovibles()

            if self.active_premove:
                self.main_window.manager.remove_premove()
                self.active_premove = False

        self.blindfoldPosicion(False, None, None)
        if a1h8 is None:
            if self.atajosRaton:
                self.atajosRaton(self.last_position, None)
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
            return

        if self.atajosRaton:
            self.atajosRaton(self.last_position, a1h8)
            # Atajos raton lanza show_candidates si hace falta

        elif hasattr(self.main_window, "manager"):
            if hasattr(self.main_window.manager, "colect_candidates"):
                liC = self.main_window.manager.colect_candidates(a1h8)
                if liC:
                    self.show_candidates(liC)

        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def checkLEDS(self):
        if not hasattr(self, "dicXML"):
            def lee(fich):
                with open(
                        Code.path_resource("IntFiles/Svg", "%s.svg" % fich), "rt", encoding="utf-8", errors="ignore"
                ) as f:
                    resp = f.read()
                return resp

            self.dicXML = {}
            self.dicXML["C"] = lee("candidate")
            self.dicXML["P+"] = lee("player_check")
            self.dicXML["Px"] = lee("player_capt")
            self.dicXML["P#"] = lee("player_mate")
            self.dicXML["R+"] = lee("rival_check")
            self.dicXML["Rx"] = lee("rival_capt")
            self.dicXML["R#"] = lee("rival_mate")
            self.dicXML["R"] = lee("rival")

    def markPositionExt(self, a1, h8, tipo):
        self.checkLEDS()
        lista = []
        for posCuadro in range(4):
            regSVG = BoardTypes.SVG()
            regSVG.a1h8 = a1 + h8
            regSVG.xml = self.dicXML[tipo]
            regSVG.siMovible = False
            regSVG.posCuadro = posCuadro
            regSVG.width_square = self.width_square
            if a1 != h8:
                regSVG.width_square *= 7.64
            svg = BoardSVGs.SVGCandidate(self.escena, regSVG, False)
            lista.append(svg)
        self.escena.update()

        def quita():
            for objeto in lista:
                objeto.hide()
                del objeto
            self.update()

        QtCore.QTimer.singleShot(1600 if tipo == "C" else 500, quita)

    def markPosition(self, a1):
        self.markPositionExt(a1, a1, "C")

    def markError(self, a1):
        if a1:
            self.markPositionExt(a1, a1, "R")

    def show_candidates(self, liC):
        if not liC or not self.configuration.x_show_candidates:
            return
        self.checkLEDS()

        dicPosCuadro = {"C": 0, "P+": 1, "Px": 1, "P#": 1, "R+": 2, "R#": 2, "Rx": 3}
        self.pendingRelease = []
        for a1, tp in liC:
            regSVG = BoardTypes.SVG()
            regSVG.a1h8 = a1 + a1
            regSVG.xml = self.dicXML[tp]
            regSVG.siMovible = False
            regSVG.posCuadro = dicPosCuadro[tp]
            regSVG.width_square = self.width_square
            svg = BoardSVGs.SVGCandidate(self.escena, regSVG, False)
            self.pendingRelease.append(svg)
        self.escena.update()

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            if item == self.flechaSC:
                self.flechaSC.hide()

    def wheelEvent(self, event):
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if self.permitidoResizeExterno():
                salto = event.delta() < 0
                ap = self.config_board.anchoPieza()
                if ap > 500:
                    ap = 64
                ap += 2 * (+1 if salto else -1)
                if ap >= self.minimum_size:
                    self.config_board.anchoPieza(ap)
                    self.config_board.guardaEnDisco()
                    self.cambiadoAncho()
                    return

        elif hasattr(self.main_window, "boardWheelEvent"):
            self.main_window.boardWheelEvent(self, event.delta() < 0)

    def set_dispatcher(self, mensajero, atajosRaton=None):
        if self.dirvisual:
            self.dirvisual.cambiadoMensajero()
        self.mensajero = mensajero
        if atajosRaton:
            self.atajosRaton = atajosRaton
        self.init_kb_buffer()

    def dbvisual_set_file(self, file):
        self.dbVisual.set_file(file)

    def dbvisual_set_show_always(self, ok):
        self.dbVisual.show_always(ok)

    def dbvisual_set_save_always(self, ok):
        self.dbVisual.save_always(ok)

    def dbvisual_close(self):
        self.dbVisual.close()

    def dbvisual_contains(self, fenm2):
        return fenm2 in self.dbVisual.dbFEN and len(self.dbVisual.dbFEN[fenm2]) > 0

    def dbvisual_list(self, fenm2):
        return self.dbVisual.dbFEN[fenm2]

    def dbVisual_save(self, fenm2, lista):
        self.dbVisual.dbFEN[fenm2] = lista

    def saveVisual(self):
        alm = self.almSaveVisual = Util.Record()
        alm.siMenuVisual = self.siMenuVisual
        alm.siDirector = self.siDirector
        alm.siDirectorIcon = self.siDirectorIcon
        alm.dirvisual = self.dirvisual
        alm.guion = self.guion
        alm.lastFenM2 = self.lastFenM2
        alm.nomdbVisual = self.dbVisual.file
        alm.dbVisual_show_always = self.dbVisual.show_always()

    def restoreVisual(self):
        alm = self.almSaveVisual
        self.siMenuVisual = alm.siMenuVisual
        self.siDirector = alm.siDirector
        self.siDirectorIcon = alm.siDirectorIcon
        self.dirvisual = alm.dirvisual
        self.guion = alm.guion
        self.lastFenM2 = alm.lastFenM2
        self.dbVisual.set_file(alm.nomdbVisual)
        self.dbVisual.show_always(alm.dbVisual_show_always)

    def set_last_position(self, position):
        self.init_kb_buffer()
        self.close_visual_script()
        self.last_position = position
        if Code.eboard and Code.eboard.driver and self.allow_eboard:
            Code.eboard.set_position(position)
        if self.siDirectorIcon or self.dbVisual.show_always():
            fenm2 = position.fenm2()
            if self.lastFenM2 != fenm2:
                self.lastFenM2 = fenm2
                if self.dbvisual_contains(fenm2):
                    if self.siDirectorIcon:
                        self.scriptSC_menu.show()
                    if self.dbVisual.show_always():
                        self.lanzaGuion()
                elif self.siDirectorIcon:
                    self.scriptSC_menu.hide()

    def eboard_arrow(self, a1, h8, prom):
        if Code.eboard and Code.eboard.driver and self.allow_eboard:
            position = self.last_position.copia()
            position.mover(a1, h8, prom)
            Code.eboard.set_position(position)
            time.sleep(2.0)
            Code.eboard.set_position(self.last_position)

    def set_raw_last_position(self, position):
        if position != self.last_position:
            self.set_last_position(position)

    def set_position(self, position, siBorraMoviblesAhora=True, variation_history=None):
        self.active_premove = False
        if self.dirvisual:
            self.dirvisual.cambiadaPosicionAntes()
        elif self.dbVisual.save_always():
            self.dbVisual.saveMoviblesBoard(self)

        if self.si_borraMovibles and siBorraMoviblesAhora:
            self.borraMovibles()

        self.set_base_position(position, variation_history=variation_history)

        if self.dirvisual:
            if self.guion:
                self.guion.cierraPizarra()
            self.dirvisual.cambiadaPosicionDespues()

        if variation_history:
            self.activate_side(position.is_white)

    def removePieces(self):
        for x in self.liPiezas:
            if x[2]:
                self.xremoveItem(x[1])
        self.liPiezas = []

    def set_base_position(self, position, variation_history=None):
        self.blindfoldPosicion(True, position, self.last_position)

        self.variation_history = variation_history

        self.pieces_are_active = False
        self.removePieces()

        squares = position.squares

        for k in squares.keys():
            if squares[k]:
                self.ponPieza(squares[k], k)

        self.escena.update()
        if self.hard_focus:
            self.setFocus()
        self.set_side_indicator(position.is_white)
        if self.flechaSC:
            self.xremoveItem(self.flechaSC)
            del self.flechaSC
            self.flechaSC = None
            self.remove_arrows()
        self.init_kb_buffer()
        self.set_last_position(position)
        if self.variation_history:
            self.activate_side(position.is_white)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def fila2punto(self, row):
        factor = (8 - row) if self.is_white_bottom else (row - 1)
        # return factor * (self.anchoPieza + self.margenPieza * 2) + self.margenCentro + self.tamFrontera
        return factor * self.width_square + self.margenCentro + self.tamFrontera / 2 + self.margenPieza

    def columna2punto(self, column):
        factor = (column - 1) if self.is_white_bottom else (8 - column)
        # return factor * (self.anchoPieza + self.margenPieza * 2) + self.margenCentro + self.tamFrontera
        return factor * self.width_square + self.margenCentro + self.tamFrontera / 2 + self.margenPieza

    def punto2fila(self, pos):
        pos -= self.margenCentro + self.tamFrontera / 2 + self.margenPieza
        pos //= self.width_square
        if self.is_white_bottom:
            return int(8 - pos)
        else:
            return int(pos + 1)

    def punto2columna(self, pos):
        pos -= self.margenCentro + self.tamFrontera / 2 + self.margenPieza
        pos //= self.width_square
        if self.is_white_bottom:
            return int(pos + 1)
        else:
            return int(8 - pos)

    def colocaPieza(self, bloquePieza, posA1H8):
        bloquePieza.row = int(posA1H8[1])
        bloquePieza.column = ord(posA1H8[0]) - 96
        self.recolocaPieza(bloquePieza)

    def recolocaPieza(self, bloquePieza):
        physical_pos = bloquePieza.physical_pos
        physical_pos.x = self.columna2punto(bloquePieza.column)
        physical_pos.y = self.fila2punto(bloquePieza.row)

    def creaPieza(self, cpieza, posA1H8):
        bloque_pieza = BoardTypes.Pieza()
        p = bloque_pieza.physical_pos
        p.ancho = self.anchoPieza
        p.alto = self.anchoPieza
        p.orden = ZVALUE_PIECE
        bloque_pieza.pieza = cpieza
        self.colocaPieza(bloque_pieza, posA1H8)
        piezaSC = BoardElements.PiezaSC(self.escena, bloque_pieza, self)

        # piezaSC.setOpacity(self.opacity[0 if cpieza.isupper() else 1])

        self.liPiezas.append([cpieza, piezaSC, True])
        return piezaSC

    def ponPieza(self, pieza, posA1H8):
        for x in self.liPiezas:
            if not x[2] and x[0] == pieza:
                piezaSC = x[1]
                self.colocaPieza(piezaSC.bloquePieza, posA1H8)
                self.escena.addItem(piezaSC)
                piezaSC.update()
                x[2] = True
                return piezaSC

        return self.creaPieza(pieza, posA1H8)

    def mostrarPiezas(self, siW, siB):
        if siW and siB:
            self.blindfold = None
        elif siW and not siB:
            self.blindfold = BLINDFOLD_BLACK
        elif siB and not siW:
            self.blindfold = BLINDFOLD_WHITE
        else:
            self.blindfold = BLINDFOLD_ALL
        self.blindfoldReset()

    def blindfoldChange(self, modoPosicion):
        self.blindfold = None if self.blindfold else BLINDFOLD_CONFIG
        self.blindfoldReset()
        self.blindfoldModoPosicion = modoPosicion if self.blindfold else False

    def blindfoldReset(self):
        ap, apc = self.pieces_are_active, self.side_pieces_active
        siFlecha = self.flechaSC is not None

        is_white_bottom = self.is_white_bottom

        atajosRaton = self.atajosRaton

        self.crea()
        if not is_white_bottom:
            self.intentaRotarBoard(None)

        if ap:
            self.activate_side(apc)
            self.set_side_indicator(apc)

        if siFlecha:
            self.resetFlechaSC()

        self.atajosRaton = atajosRaton
        self.init_kb_buffer()

    def blindfoldQuitar(self):
        if self.blindfold:
            self.blindfold = None
            self.blindfoldReset()

    def blindfoldPosicion(self, start, nueposicion, ultposicion):
        if self.blindfoldModoPosicion:
            if start:
                if ultposicion and nueposicion.fen() != ultposicion.fen():
                    b = self.blindfold
                    self.blindfold = None
                    self.blindfoldReset()
                    self.blindfold = b
            else:
                self.blindfoldReset()

    def blindfoldConfig(self):
        nom_pieces_ori = self.config_board.nomPiezas()
        w = Piezas.WBlindfold(self, nom_pieces_ori)
        if w.exec_():
            self.blindfold = BLINDFOLD_CONFIG
            self.blindfoldReset()

    def buscaPieza(self, posA1H8):
        if posA1H8 is None:
            return -1
        row = int(posA1H8[1])
        column = ord(posA1H8[0]) - 96
        for num, x in enumerate(self.liPiezas):
            if x[2]:
                pieza = x[1].bloquePieza
                if pieza.row == row and pieza.column == column:
                    return num
        return -1

    def damePiezaEn(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            return self.liPiezas[npieza][1]
        return None

    def dameNomPiezaEn(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            return self.liPiezas[npieza][0]
        return None

    def muevePiezaTemporal(self, from_a1h8, to_a1h8):
        npieza = self.buscaPieza(from_a1h8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            row = int(to_a1h8[1])
            column = ord(to_a1h8[0]) - 96
            x = self.columna2punto(column)
            y = self.fila2punto(row)
            piezaSC.setPos(x, y)

    def muevePieza(self, from_a1h8, to_a1h8):
        npieza = self.buscaPieza(from_a1h8)
        if npieza >= 0:
            self.borraPieza(to_a1h8)
            piezaSC = self.liPiezas[npieza][1]
            self.colocaPieza(piezaSC.bloquePieza, to_a1h8)
            piezaSC.rehazPosicion()
            piezaSC.update()
            self.escena.update()

    # def muevePieza_timed(self, from_a1h8, to_a1h8, seconds):
    #     npieza = self.buscaPieza(from_a1h8)
    #     if npieza >= 0:
    #         def a1h8_xy(a1h8):
    #             row = int(a1h8[1])
    #             column = ord(a1h8[0]) - 96
    #             x = self.columna2punto(column)
    #             y = self.fila2punto(row)
    #             return x, y
    #
    #         piezaSC = self.liPiezas[npieza][1]
    #         anim = QtCore.QPropertyAnimation(piezaSC, b"geometry")
    #         anim.setDuration(seconds*1000)
    #         # anim.setStartValue(QtCore.QRect(150, 30, 100, 100))
    #         r: QtCore.QRectF = QtCore.QRectF(piezaSC.rect)
    #         x, y = a1h8_xy(to_a1h8)
    #         r.moveLeft(x)
    #         r.moveBottom(y)
    #
    #         anim.setEndValue(r)
    #         anim.start()

    def set_piece_again(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            piezaSC.rehazPosicion()
            piezaSC.update()
            self.escena.update()

    def borraPieza(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            self.xremoveItem(piezaSC)
            self.liPiezas[npieza][2] = False
            self.escena.update()

    def borraPiezaTipo(self, posA1H8, tipo):
        row = int(posA1H8[1])
        column = ord(posA1H8[0]) - 96
        for num, x in enumerate(self.liPiezas):
            if x[2]:
                pieza = x[1].bloquePieza
                if pieza.row == row and pieza.column == column and pieza.pieza == tipo:
                    piezaSC = self.liPiezas[num][1]
                    self.xremoveItem(piezaSC)
                    self.liPiezas[num][2] = False
                    self.escena.update()
                    return

    def cambiaPieza(self, posA1H8, nueva):
        self.borraPieza(posA1H8)
        return self.creaPieza(nueva, posA1H8)

    def activate_side(self, is_white):
        self.pieces_are_active = True
        self.side_pieces_active = is_white
        for pieza, piezaSC, is_active in self.liPiezas:
            if is_active:
                if is_white is None:
                    resp = True
                else:
                    if pieza.isupper():
                        resp = is_white
                    else:
                        resp = not is_white
                piezaSC.activa(resp)
        self.init_kb_buffer()

    def setDispatchMove(self, rutina):
        for pieza, piezaSC, is_active in self.liPiezas:
            if is_active:
                piezaSC.setDispatchMove(rutina)

    def enable_all(self):
        self.pieces_are_active = True
        for num, una in enumerate(self.liPiezas):
            pieza, piezaSC, is_active = una
            if is_active:
                piezaSC.activa(True)
        self.init_kb_buffer()

    def disable_all(self):
        self.pieces_are_active = False
        self.side_pieces_active = None
        for num, una in enumerate(self.liPiezas):
            pieza, piezaSC, is_active = una
            if is_active:
                piezaSC.activa(False)
        self.init_kb_buffer()

    def num2alg(self, row, column):
        return chr(96 + column) + str(row)

    def alg2num(self, a1):
        x = self.columna2punto(ord(a1[0]) - 96)
        y = self.fila2punto(ord(a1[1]) - 48)
        return x, y

    def intentaMover(self, piezaSC, posCursor, eventButton):
        pieza = piezaSC.bloquePieza
        from_sq = self.num2alg(pieza.row, pieza.column)

        x = int(posCursor.x())
        y = int(posCursor.y())
        cx = self.punto2columna(x)
        cy = self.punto2fila(y)

        if cx in range(1, 9) and cy in range(1, 9):
            to_sq = self.num2alg(cy, cx)

            x = self.columna2punto(cx)
            y = self.fila2punto(cy)
            piezaSC.setPos(x, y)
            if to_sq == from_sq:
                return

            if not self.mensajero(from_sq, to_sq):
                x, y = self.alg2num(from_sq)
                piezaSC.setPos(x, y)

            # -CONTROL-
            self.init_kb_buffer()

        piezaSC.rehazPosicion()
        piezaSC.update()
        self.escena.update()
        QTUtil.refresh_gui()

    def xy_a1h8(self, x, y):
        cy = self.punto2fila(y)
        cx = self.punto2columna(x)
        return self.num2alg(cy, cx)

    def a1h8_xy(self, a1h8):
        cx, cy = self.alg2num(a1h8)
        return self.columna2punto(cx), self.fila2punto(cy)

    def piece_out_position(self, position):
        si_changed = False
        for una in self.liPiezas:
            pieza, piezaSC, is_active = una
            if position.is_white == pieza.isupper():
                x = piezaSC.x()
                y = piezaSC.y()
                if int(x) != piezaSC.bloquePieza.physical_pos.x or int(y) != piezaSC.bloquePieza.physical_pos.y:
                    si_changed = True
                    cy = self.punto2fila(y)
                    cx = self.punto2columna(x)
                    to_sq = self.num2alg(cy, cx)
                    cy = self.punto2fila(piezaSC.bloquePieza.physical_pos.y)
                    cx = self.punto2columna(piezaSC.bloquePieza.physical_pos.x)
                    from_sq = self.num2alg(cy, cx)
                    if to_sq != from_sq:
                        return si_changed, from_sq, to_sq
        return si_changed, None, None

    def set_side_indicator(self, is_white):
        bd = self.side_indicator_sc.bloqueDatos
        if is_white:
            bd.colorRelleno = self.colorBlancas
            siAbajo = self.is_white_bottom
        else:
            bd.colorRelleno = self.colorNegras
            siAbajo = not self.is_white_bottom
        bd.physical_pos.y = bd.sur if siAbajo else bd.norte
        self.side_indicator_sc.mostrar()

    def resetFlechaSC(self):
        if self.flechaSC:
            a1h8 = self.flechaSC.bloqueDatos.a1h8
            self.put_arrow_sc(a1h8[:2], a1h8[2:])

    def put_arrow_sc(self, desdeA1h8, hastaA1h8):
        a1h8 = desdeA1h8 + hastaA1h8
        if self.flechaSC is None:
            self.flechaSC = self.creaFlechaSC(a1h8)
        self.flechaSC.show()
        self.flechaSC.ponA1H8(a1h8)
        self.flechaSC.update()

    def put_arrow_scvar(self, liArrows, destino=None, opacity=None):
        if destino is None:
            destino = "m"
        if opacity is None:
            opacity = 0.4
        for from_sq, to_sq in liArrows:
            if from_sq and to_sq:
                self.creaFlechaMulti(from_sq + to_sq, False, destino=destino, opacity=opacity)

    def pulsadaFlechaSC(self):
        self.flechaSC.hide()

    def creaFlechaMulti(self, a1h8, siMain, destino="c", opacity=0.9):
        bf = copy.deepcopy(self.config_board.fTransicion() if siMain else self.config_board.fAlternativa())
        bf.a1h8 = a1h8
        bf.destino = destino
        bf.opacity = opacity

        arrow = self.creaFlecha(bf)
        self.liFlechas.append(arrow)
        arrow.show()

    def creaFlechaSC(self, a1h8):
        bf = copy.deepcopy(self.config_board.fTransicion())
        bf.a1h8 = a1h8
        bf.width_square = self.width_square
        bf.siMovible = False

        return self.creaFlecha(bf, self.pulsadaFlechaSC)

    def creaFlechaTmp(self, desdeA1h8, hastaA1h8, siMain):
        bf = copy.deepcopy(self.config_board.fTransicion() if siMain else self.config_board.fAlternativa())
        bf.a1h8 = desdeA1h8 + hastaA1h8
        arrow = self.creaFlecha(bf)
        self.liFlechas.append(arrow)
        arrow.show()

    def creaFlechaPremove(self, xfrom, xto):
        self.active_premove = True
        bf = copy.deepcopy(self.config_board.fActivo())
        bf.a1h8 = xfrom + xto
        arrow = self.creaFlecha(bf)
        self.liFlechas.append(arrow)
        arrow.show()
        self.update()

    def creaFlechaTutor(self, desdeA1h8, hastaA1h8, factor):
        bf = copy.deepcopy(self.config_board.fTransicion())
        bf.a1h8 = desdeA1h8 + hastaA1h8
        bf.opacity = max(factor, 0.20)
        bf.ancho = max(bf.ancho * 2 * (factor ** 2.2), bf.ancho / 3)
        bf.altocabeza = max(bf.altocabeza * (factor ** 2.2), bf.altocabeza / 3)
        bf.vuelo = bf.altocabeza / 3
        bf.grosor = 1
        bf.redondeos = True
        bf.forma = "1"
        bf.physical_pos.orden = ZVALUE_PIECE + 1

        arrow = self.creaFlecha(bf)
        self.liFlechas.append(arrow)
        arrow.show()

    def ponFlechasTmp(self, lista, ms=None):
        self.ponFlechas(lista)

        def quitaFlechasTmp():
            self.remove_arrows()
            if self.flechaSC:
                self.flechaSC.show()

        if ms is None:
            ms = 2000 if len(lista) > 1 else 1400
        QtCore.QTimer.singleShot(ms, quitaFlechasTmp)

    def ponFlechas(self, lista):
        if self.flechaSC:
            self.flechaSC.hide()
        for from_sq, to_sq, siMain in lista:
            self.creaFlechaTmp(from_sq, to_sq, siMain)
        QTUtil.refresh_gui()

    def show_arrow_mov(self, desde_a1h8, hasta_a1h8, modo, opacity=None):
        bf = BoardTypes.Flecha()
        bf.physical_pos.orden = ZVALUE_PIECE + 1
        bf.color = self.config_board.fTransicion().color
        bf.redondeos = False
        bf.forma = "a"

        siPieza = self.buscaPieza(hasta_a1h8) > -1
        if modo == "m":  # movimientos
            bf.tipo = 2
            bf.grosor = 2
            bf.altocabeza = 6
            bf.destino = "m" if siPieza else "c"

        elif modo == "c":  # captura
            bf.tipo = 1
            bf.grosor = 2
            bf.altocabeza = 8
            bf.destino = "m" if siPieza else "c"


        elif modo == "tr":  # transición entre flechas
            bf.tipo = 3
            bf.grosor = 2
            bf.forma = "c"
            bf.altocabeza = 14
            bf.destino = "c"
            bf.ancho = 4
            bf.physical_pos.orden = ZVALUE_PIECE - 1

        elif modo == "2":  # m2
            bf = self.config_board.fTransicion().copia()
            bf.destino = "c"

        elif modo == "p":
            bf = self.config_board.fActivo().copia()
            bf.destino = "c"

        elif modo == "r":
            bf = self.config_board.fRival().copia()
            bf.destino = "c"

        elif modo == "pt":
            bf = self.config_board.fTransicion().copia()
            bf.destino = "c"

        elif modo == "rt":
            bf = self.config_board.fAlternativa().copia()
            bf.tipo = 1
            bf.destino = "c"

        elif modo == "rt":
            bf.grosor = 2
            bf.destino = "c"

        elif modo == "ms":
            bf = self.config_board.fActivo().copia()

        elif modo == "mt":
            bf = self.config_board.fRival().copia()

        elif modo == "tb":  # takeback eboard
            bf = self.config_board.fTransicion().copia()
            bf.destino = "m"
            bf.physical_pos.orden = ZVALUE_PIECE + 1

        if self.anchoPieza > 24:
            bf.grosor = bf.grosor * 15 / 10
            bf.altocabeza = bf.altocabeza * 15 / 10

        bf.a1h8 = desde_a1h8 + hasta_a1h8
        bf.width_square = self.width_square

        if opacity:
            bf.opacity = opacity

        arrow = self.creaFlecha(bf)
        self.liFlechas.append(arrow)
        arrow.show()

    def remove_arrows(self):
        for arrow in self.liFlechas:
            self.xremoveItem(arrow)
            arrow.hide()
            del arrow
        self.liFlechas = []
        self.update()

    def set_side_bottom(self, is_white_bottom):
        if self.is_white_bottom == is_white_bottom:
            return
        self.is_white_bottom = is_white_bottom
        for ver in self.liCoordenadasVerticales:
            ver.bloqueDatos.valor = str(9 - int(ver.bloqueDatos.valor))
            ver.update()

        for hor in self.liCoordenadasHorizontales:
            hor.bloqueDatos.valor = chr(97 + 104 - ord(hor.bloqueDatos.valor))
            hor.update()

        for pieza, piezaSC, siVisible in self.liPiezas:
            if siVisible:
                self.recolocaPieza(piezaSC.bloquePieza)
                piezaSC.rehazPosicion()
                piezaSC.update()

        self.escena.update()

    def show_coordinates(self, ok):
        for coord in self.liCoordenadasHorizontales:
            coord.setVisible(ok)
        for coord in self.liCoordenadasVerticales:
            coord.setVisible(ok)

    def peonCoronando(self, is_white):
        if self.configuration.x_autopromotion_q:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers != QtCore.Qt.AltModifier:
                return "Q" if is_white else "q"
        menu = QTVarios.LCMenu(self)
        for txt, pieza in ((_("Queen"), "Q"), (_("Rook"), "R"), (_("Bishop"), "B"), (_("Knight"), "N")):
            if not is_white:
                pieza = pieza.lower()
            menu.opcion(pieza, txt, self.piezas.icono(pieza))

        resp = menu.lanza()
        if resp:
            return resp
        else:
            return "q"

    def refresh(self):
        self.escena.update()
        QTUtil.refresh_gui()

    def pulsadoNum(self, siIzq, siActivar, number):
        if (
                not siIzq
        ):  # si es derecho lo dejamos para el menu visual, y el izquierdo solo muestra capturas, si se quieren ver movimientos, que active show candidates
            return
        if self.exePulsadoNum:
            self.exePulsadoNum(siActivar, int(number))

    def pulsadaLetra(self, siIzq, siActivar, letra):
        if (
                not siIzq
        ):  # si es derecho lo dejamos para el menu visual, y el izquierdo solo muestra capturas, si se quieren ver movimientos, que active show candidates
            return
        if self.exePulsadaLetra:
            self.exePulsadaLetra(siActivar, letra)

    def save_as_img(self, file=None, tipo=None, is_ctrl=False, is_alt=False):
        act_ind = act_scr = False
        if self.indicadorSC_menu:
            if self.indicadorSC_menu.isVisible():
                act_ind = True
                self.indicadorSC_menu.hide()
        if self.siDirectorIcon and self.scriptSC_menu:
            if self.scriptSC_menu.isVisible():
                act_scr = True
                self.scriptSC_menu.hide()

        if is_alt and not is_ctrl:
            pm = QtWidgets.QWidget.grab(self)
        else:
            x = 0
            y = 0
            w = self.width()
            h = self.height()
            if is_ctrl and not is_alt:
                x = self.tamFrontera
                y = self.tamFrontera
                w -= self.tamFrontera * 2
                h -= self.tamFrontera * 2
            elif is_alt and is_ctrl:
                x += self.margenCentro + self.tamFrontera
                y += self.margenCentro + self.tamFrontera
                w -= self.margenCentro * 2 + self.tamFrontera * 2
                h -= self.margenCentro * 2 + self.tamFrontera * 2
            r = QtCore.QRect(x, y, w, h)
            pm = QtWidgets.QWidget.grab(self, r)
        if file is None:
            QTUtil.ponPortapapeles(pm, tipo="p")
        else:
            pm.save(file, tipo)

        if act_ind:
            self.indicadorSC_menu.show()
        if act_scr:
            self.scriptSC_menu.show()

    def thumbnail(self, ancho):
        # escondemos piezas+flechas
        for pieza, pieza_sc, si_visible in self.liPiezas:
            if si_visible:
                pieza_sc.hide()
        for arrow in self.liFlechas:
            arrow.hide()
        if self.flechaSC:
            self.flechaSC.hide()

        pm = QtWidgets.QWidget.grab(self)
        thumb = pm.scaled(ancho, ancho, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        # mostramos piezas+flechas
        for pieza, pieza_sc, si_visible in self.liPiezas:
            if si_visible:
                pieza_sc.show()
        for arrow in self.liFlechas:
            arrow.show()
        if self.flechaSC:
            self.flechaSC.show()

        byte_array = QtCore.QByteArray()
        xbuffer = QtCore.QBuffer(byte_array)
        xbuffer.open(QtCore.QIODevice.WriteOnly)
        thumb.save(xbuffer, "PNG")

        bytes_io = BytesIO(byte_array)
        contents = bytes_io.getvalue()
        bytes_io.close()

        return contents

    def a1h8_fc(self, a1h8):
        df = int(a1h8[1])
        dc = ord(a1h8[0]) - 96
        hf = int(a1h8[3])
        hc = ord(a1h8[2]) - 96
        if self.is_white_bottom:
            df = 9 - df
            hf = 9 - hf
        else:
            dc = 9 - dc
            hc = 9 - hc

        return df, dc, hf, hc

    def fc_a1h8(self, df, dc, hf, hc):
        if self.is_white_bottom:
            df = 9 - df
            hf = 9 - hf
        else:
            dc = 9 - dc
            hc = 9 - hc

        a1h8 = chr(dc + 96) + str(df) + chr(hc + 96) + str(hf)

        return a1h8

    def creaMarco(self, bloqueMarco):
        bloqueMarcoN = copy.deepcopy(bloqueMarco)
        bloqueMarcoN.width_square = self.width_square

        return BoardBoxes.MarcoSC(self.escena, bloqueMarcoN)

    def creaCircle(self, bloque_circle):
        bloque_circle = copy.deepcopy(bloque_circle)
        bloque_circle.width_square = self.width_square

        return BoardCircles.CircleSC(self.escena, bloque_circle)

    def creaSVG(self, bloqueSVG, siEditando=False):
        bloqueSVGN = copy.deepcopy(bloqueSVG)
        bloqueSVGN.width_square = self.width_square

        return BoardSVGs.SVGSC(self.escena, bloqueSVGN, siEditando=siEditando)

    def creaMarker(self, bloqueMarker, siEditando=False):
        bloqueMarkerN = copy.deepcopy(bloqueMarker)
        bloqueMarkerN.width_square = self.width_square

        return BoardMarkers.MarkerSC(self.escena, bloqueMarkerN, siEditando=siEditando)

    def creaFlecha(self, bloqueFlecha, rutina=None):
        bloqueFlechaN = copy.deepcopy(bloqueFlecha)
        bloqueFlechaN.width_square = self.width_square
        bloqueFlechaN.tamFrontera = self.tamFrontera

        return BoardArrows.FlechaSC(self.escena, bloqueFlechaN, rutina)

    def intentaRotarBoard(self, siIzquierdo):
        if self.siPosibleRotarBoard:
            self.rotaBoard()

    def rotaBoard(self):
        self.set_side_bottom(not self.is_white_bottom)
        if self.flechaSC:
            # self.put_arrow_sc( self.ultMovFlecha[0], self.ultMovFlecha[1])
            self.resetFlechaSC()
        bd = self.side_indicator_sc.bloqueDatos
        self.set_side_indicator(bd.colorRelleno == self.colorBlancas)
        for k, uno in self.dicMovibles.items():
            uno.physical_pos2xy()
        for arrow in self.liFlechas:
            arrow.physical_pos2xy()
        self.escena.update()

        if hasattr(self.main_window, "capturas"):
            self.main_window.capturas.ponLayout(self.is_white_bottom)

    def registraMovible(self, bloqueSC):
        self.idUltimoMovibles += 1
        bloqueSC.idMovible = self.idUltimoMovibles
        self.dicMovibles[self.idUltimoMovibles] = bloqueSC

    def lista_movibles(self):
        if self.dicMovibles:
            li = []
            for k, v in self.dicMovibles.items():
                xobj = str(v)
                if "Marco" in xobj:
                    tp = TabVisual.TP_MARCO
                elif "Flecha" in xobj:
                    tp = TabVisual.TP_FLECHA
                elif "SVG" in xobj:
                    tp = TabVisual.TP_SVG
                elif "Circle" in xobj:
                    tp = TabVisual.TP_CIRCLE
                else:
                    continue
                li.append((tp, v.bloqueDatos))

            return li
        else:
            return []

    # def exportaMovibles(self):
    #     li = self.lista_movibles()
    #     return Util.var2txt(li) if li else ""
    #
    # def importaMovibles(self, xData):
    #     self.borraMovibles()
    #     if xData:
    #         liDatos = Util.txt2var(str(xData))
    #         for tp, bloqueDatos in liDatos:
    #             if tp == TabVisual.TP_MARCO:
    #                 self.creaMarco(bloqueDatos)
    #             elif tp == TabVisual.TP_CIRCLE:
    #                 self.creaCircle(bloqueDatos)
    #             elif tp == TabVisual.TP_FLECHA:
    #                 self.creaFlecha(bloqueDatos)
    #             elif tp == TabVisual.TP_SVG:
    #                 self.creaSVG(bloqueDatos)
    #             elif tp == TabVisual.TP_MARKER:
    #                 self.creaMarker(bloqueDatos)

    def borraMovible(self, itemSC):
        for k, uno in self.dicMovibles.items():
            if uno == itemSC:
                del self.dicMovibles[k]
                self.xremoveItem(uno)
                return

    def borraUltimoMovibleA1(self, a1):
        for k, uno in reversed(self.dicMovibles.items()):
            a1h8 = uno.bloqueDatos.a1h8
            if a1h8.startswith(a1) or a1h8.endswith(a1):
                self.borraMovible(uno)
                break

    def borraUltimoMovible(self):
        keys = list(self.dicMovibles.keys())
        if keys:
            self.xremoveItem(self.dicMovibles[keys[-1]])
            del self.dicMovibles[keys[-1]]

    def borraMovibles(self):
        for k, uno in self.dicMovibles.items():
            self.xremoveItem(uno)
        self.dicMovibles = collections.OrderedDict()
        self.lastFenM2 = None

    def bloqueaRotacion(self, siBloquea):  # se usa en la presentacion para que no rote
        self.siPosibleRotarBoard = not siBloquea

    def dispatchSize(self, rutinaControl):
        self._dispatchSize = rutinaControl

    # def boundingRect(self):
    #     return QtCore.QRect(0, 0, self.ancho, self.ancho)

    def fen_active(self):
        li = []
        for x in range(8):
            li.append(["", "", "", "", "", "", "", ""])

        for x in self.liPiezas:
            if x[2]:
                piezaSC = x[1]
                bp = piezaSC.bloquePieza
                li[8 - bp.row][bp.column - 1] = x[0]

        lineas = []
        for x in range(8):
            uno = ""
            num = 0
            for y in range(8):
                if li[x][y]:
                    if num:
                        uno += str(num)
                        num = 0
                    uno += li[x][y]
                else:
                    num += 1
            if num:
                uno += str(num)
            lineas.append(uno)

        bd = self.side_indicator_sc.bloqueDatos
        is_white = bd.colorRelleno == self.colorBlancas

        resto = "w" if is_white else "b"
        resto += " KQkq - 0 1"

        return "/".join(lineas) + " " + resto

    def copiaPosicionDe(self, otroBoard):
        for x in self.liPiezas:
            if x[2]:
                self.xremoveItem(x[1])
        self.liPiezas = []
        for cpieza, piezaSC, is_active in otroBoard.liPiezas:
            if is_active:
                physical_pos = piezaSC.bloquePieza
                f = physical_pos.row
                c = physical_pos.column
                posA1H8 = chr(c + 96) + str(f)
                self.creaPieza(cpieza, posA1H8)

        if not otroBoard.is_white_bottom:
            self.rotaBoard()

        if otroBoard.side_indicator_sc.isVisible():
            bdOT = otroBoard.side_indicator_sc.bloqueDatos
            is_white = bdOT.colorRelleno == otroBoard.colorBlancas
            siIndicadorAbajo = bdOT.physical_pos.y == bdOT.sur

            bd = self.side_indicator_sc.bloqueDatos
            bd.physical_pos.y = bd.sur if siIndicadorAbajo else bd.norte
            bd.colorRelleno = self.colorBlancas if is_white else self.colorNegras
            self.side_indicator_sc.mostrar()

        if otroBoard.flechaSC and otroBoard.flechaSC.isVisible():
            a1h8 = otroBoard.flechaSC.bloqueDatos.a1h8
            desdeA1h8, hastaA1h8 = a1h8[:2], a1h8[2:]
            self.put_arrow_sc(desdeA1h8, hastaA1h8)

        self.escena.update()
        self.setFocus()

    def terminar(self):
        if self.dirvisual:
            self.dirvisual.terminar()

    def allow_takeback(self):
        return (
                hasattr(self.main_window, "manager")
                and hasattr(self.main_window.manager, "run_action")
                and hasattr(self.main_window.manager, "takeback")
        )

    def set_tmp_position(self, position):
        self.pieces_are_active = False
        self.removePieces()

        squares = position.squares
        for k in squares.keys():
            if squares[k]:
                self.ponPieza(squares[k], k)

        self.escena.update()
        if self.hard_focus:
            self.setFocus()
        self.set_side_indicator(position.is_white)
        if self.flechaSC:
            self.xremoveItem(self.flechaSC)
            del self.flechaSC
            self.flechaSC = None
            self.remove_arrows()
        self.init_kb_buffer()
        self.pieces_are_active = True
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def try_eboard_takeback(self, side):
        if not self.allow_eboard:
            return 1
        if self.allow_takeback():
            game = self.main_window.manager.game

            against_engine = self.main_window.manager.xrival is not None
            if against_engine and hasattr(self.main_window.manager, "play_against_engine"):
                against_engine = self.main_window.manager.play_against_engine

            if against_engine:
                allow_human_takeback = Code.eboard.allowHumanTB and self.last_position.is_white == side
                two_moves = len(game) >= 2
            else:
                allow_human_takeback = True
                two_moves = False

            if allow_human_takeback:
                Code.eboard.allowHumanTB = False
                if self.main_window.manager.in_end_of_line():
                    self.exec_kb_buffer(Qt.Key_Backspace, 0)
                else:
                    self.main_window.key_pressed("T", QtCore.Qt.Key.Key_Left)
                    # self.exec_kb_buffer(Qt.Key_Left, 0)
                return 1

            if two_moves:
                m_1 = game.move(-1)
                self.set_tmp_position(m_1.position_before)
                m_2 = game.move(-2)
                if self.flechaSC:
                    self.flechaSC.hide()
                self.show_arrow_mov(m_2.to_sq, m_2.from_sq, "tb", opacity=0.50)

            Code.eboard.allowHumanTB = True
        return 0

    def dispatch_eboard(self, quien, a1h8):
        if self.mensajero and self.pieces_are_active and self.allow_eboard:

            if quien == "whiteMove":
                Code.eboard.allowHumanTB = False
                if not self.side_pieces_active:
                    return 0
            elif quien == "blackMove":
                Code.eboard.allowHumanTB = False
                if self.side_pieces_active:
                    return 0
            elif quien == "scan":
                QTUtil.ponPortapapeles(a1h8)
                return 1

            elif quien == "whiteTakeBack":
                return self.try_eboard_takeback(WHITE)

            elif quien == "blackTakeBack":
                return self.try_eboard_takeback(BLACK)

            elif quien == "stableBoard":
                return 1

            else:
                return 1

            if self.mensajero(a1h8[:2], a1h8[2:4], a1h8[4:]):
                return 1
            return 0

        return 1

    def disable_eboard_here(self):
        self.allow_eboard = False

    def enable_eboard_here(self):
        self.allow_eboard = True
        if Code.eboard and Code.eboard.driver:
            Code.eboard.set_position(self.last_position)

    def play_current_position(self):
        gm = Game.Game(first_position=self.last_position)
        dic = {"GAME": gm.save(), "ISWHITE": gm.last_position.is_white}
        fich = Util.relative_path(self.configuration.ficheroTemporal("pkd"))
        Util.save_pickle(fich, dic)

        XRun.run_lucas("-play", fich)


class WTamBoard(QtWidgets.QDialog):
    def __init__(self, board):

        QtWidgets.QDialog.__init__(self, board.parent())

        self.setWindowTitle(_("Change board size"))
        self.setWindowIcon(Iconos.ResizeBoard())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self._dispatchSize = board._dispatchSize
        self.board = board
        self.config_board = board.config_board

        ap = self.config_board.anchoPieza()

        self.antes = ap

        liTams = [
            (_("Very large"), 80),
            (_("Large"), 64),
            (_("Medium"), 48),
            (_("Medium-small"), 32),
            (_("Small"), 24),
            (_("Very small"), 16),
            (_("Custom size"), 0),
            (_("Initial size"), -1),
            (_("By default"), -2),
        ]

        self.cb = Controles.CB(self, liTams, self.anchoParaCB(ap)).capture_changes(self.cambiadoTamCB)

        minimo = self.board.minimum_size
        maximo = board.calculaAnchoMXpieza() + 30

        self.sb = Controles.SB(self, ap, minimo, maximo).capture_changes(self.cambiadoTamSB)

        self.sl = Controles.SL(self, minimo, maximo, ap, self.cambiadoTamSL, tick=0).set_width(180)

        btAceptar = Controles.PB(self, "", rutina=self.aceptar, plano=False).ponIcono(Iconos.Aceptar())

        layout = Colocacion.G()
        layout.control(btAceptar, 0, 0).control(self.cb, 0, 1).control(self.sb, 0, 2)
        layout.controlc(self.sl, 1, 0, 1, 3).margen(5)
        self.setLayout(layout)

        self.siOcupado = False
        self.siCambio = False
        self.board.permitidoResizeExterno(False)

    def anchoParaCB(self, ap):
        return ap if ap in (80, 64, 48, 32, 24, 16) else 0

    def colocate(self):
        self.show()  # Necesario para que calcule bien el tama_o antes de colocar
        pos = self.board.parent().mapToGlobal(self.board.pos())

        y = pos.y() - self.frameGeometry().height()
        if y < 0:
            y = 0
        pos.setY(y)
        self.move(pos)

    def aceptar(self):
        self.close()

    def cambiaAncho(self):
        is_white_bottom = self.board.is_white_bottom
        self.board.cambiadoAncho()
        if not is_white_bottom:
            self.board.intentaRotarBoard(None)

    def dispatch(self):
        t = self.board
        if t._dispatchSize:
            t._dispatchSize()
        self.siCambio = True

    def cambiadoTamCB(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        ct = self.config_board
        tam = self.cb.valor()

        if tam == 0:
            ct.anchoPieza(self.board.anchoPieza)
        elif tam == -1:
            tpz = self.antes
            ct.anchoPieza(tpz)
            self.cb.set_value(self.anchoParaCB(tpz))
            self.cambiaAncho()
        elif tam == -2:
            self.cb.set_value(self.anchoParaCB(ct.ponDefAnchoPieza()))
            self.cambiaAncho()
        else:
            ct.anchoPieza(tam)
            self.cambiaAncho()

        self.sb.set_value(self.board.anchoPieza)
        self.sl.set_value(self.board.anchoPieza)
        self.siOcupado = False
        self.dispatch()

    def cambiadoTamSB(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        tam = self.sb.valor()
        self.config_board.anchoPieza(tam)
        self.cb.set_value(self.anchoParaCB(tam))
        self.cambiaAncho()
        self.sl.set_value(tam)
        self.siOcupado = False
        self.dispatch()

    def cambiadoTamSL(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        tam = self.sl.valor()
        self.config_board.anchoPieza(tam)
        self.cb.set_value(self.anchoParaCB(tam))
        self.sb.set_value(tam)
        self.cambiaAncho()
        self.siOcupado = False
        self.dispatch()

    def closeEvent(self, event):
        self.config_board.guardaEnDisco()
        self.close()
        if self.siCambio:
            self.dispatch()
        if self.config_board.is_base:
            self.board.permitidoResizeExterno(self.config_board.is_base)


class PosBoard(Board):
    def enable_all(self):
        for pieza, piezaSC, is_active in self.liPiezas:
            piezaSC.activa(True)

    def keyPressEvent(self, event):
        k = event.key()
        if (96 > k > 64) and chr(k) in "PQKRNB":
            self.parent().cambiaPiezaSegun(chr(k))
        else:
            Board.keyPressEvent(self, event)
        event.ignore()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        cx = self.punto2columna(x)
        cy = self.punto2fila(y)
        siEvent = True
        if cx in range(1, 9) and cy in range(1, 9):
            a1h8 = self.num2alg(cy, cx)
            siIzq = event.button() == QtCore.Qt.LeftButton
            siDer = event.button() == QtCore.Qt.RightButton
            if self.squares.get(a1h8):
                self.parent().ultimaPieza = self.squares.get(a1h8)
                if hasattr(self.parent(), "ponCursor"):
                    self.parent().ponCursor()
                    # ~ if siIzq:
                    # ~ QtWidgets.QGraphicsView.mousePressEvent(self,event)
                if siDer:
                    if hasattr(self, "mensBorrar"):
                        self.mensBorrar(a1h8)
                    siEvent = False
            else:
                if siDer:
                    if hasattr(self, "mensCrear") and self.mensCrear:
                        self.mensCrear(a1h8)
                    siEvent = False
                if siIzq:
                    if hasattr(self, "mensRepetir") and self.mensRepetir:
                        self.mensRepetir(a1h8)
                    siEvent = False
        else:
            Board.mousePressEvent(self, event)
            return
        if siEvent:
            QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def ponDispatchDrop(self, dispatch):
        self.dispatchDrop = dispatch

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat("image/x-lc-dato"):
            dato = mimeData.data("image/x-lc-dato").data().decode()
            p = event.pos()
            x = p.x()
            y = p.y()
            cx = self.punto2columna(x)
            cy = self.punto2fila(y)
            if cx in range(1, 9) and cy in range(1, 9):
                a1h8 = self.num2alg(cy, cx)
                self.dispatchDrop(a1h8, dato)
            event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()


class BoardEstatico(Board):
    def mousePressEvent(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.width_square * 8)
        if not ((minimo < x < maximo) and (minimo < y < maximo)):
            if self.atajosRaton:
                self.atajosRaton(self.last_position, None)
            Board.mousePressEvent(self, event)
            return
        xc = 1 + int(float(x - self.margenCentro) / self.width_square)
        yc = 1 + int(float(y - self.margenCentro) / self.width_square)

        if self.is_white_bottom:
            yc = 9 - yc
        else:
            xc = 9 - xc

        f = chr(48 + yc)
        c = chr(96 + xc)

        self.main_window.pulsada_celda(c + f)

        Board.mousePressEvent(self, event)


class BoardEstaticoMensaje(BoardEstatico):
    def __init__(self, parent, config_board, color_mens, size_factor=None):
        self.color_mens = Code.dic_colors["BOARD_STATIC"] if color_mens is None else color_mens
        self.size_factor = 1.0 if size_factor is None else size_factor
        BoardEstatico.__init__(self, parent, config_board)

    def rehaz(self):
        Board.rehaz(self)
        self.mens = BoardTypes.Texto()
        self.mens.tipoLetra = BoardTypes.TipoLetra(puntos=self.width_square * 2 * self.size_factor, peso=750)
        self.mens.physical_pos.ancho = self.width_square * 8
        self.mens.physical_pos.alto = self.width_square * 8
        self.mens.physical_pos.orden = 99
        self.mens.colorTexto = self.color_mens
        self.mens.valor = ""
        self.mens.alineacion = "c"
        self.mens.physical_pos.x = (self.ancho - self.mens.physical_pos.ancho) / 2
        self.mens.physical_pos.y = (self.ancho - self.mens.physical_pos.ancho) / 2
        self.mensSC = BoardElements.TextoSC(self.escena, self.mens)

        self.mens2 = BoardTypes.Texto()
        self.mens2.tipoLetra = BoardTypes.TipoLetra(puntos=self.width_square * self.size_factor, peso=750)
        self.mens2.physical_pos.ancho = self.width_square * 8
        self.mens2.physical_pos.alto = self.width_square * 8
        self.mens2.physical_pos.orden = 99
        self.mens2.colorTexto = self.color_mens
        self.mens2.valor = ""
        self.mens2.alineacion = "c"
        self.mens2.physical_pos.x = self.mens.physical_pos.x + self.width_square * 2
        self.mens2.physical_pos.y = self.mens.physical_pos.y
        self.mensSC2 = BoardElements.TextoSC(self.escena, self.mens2)

    def pon_texto(self, texto, opacity):
        self.mens.valor = texto
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.escena.update()

    def pon_textos(self, texto1, texto2, opacity):
        self.mens.valor = texto1
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.mens2.valor = texto2
        self.mensSC2.setOpacity(opacity)
        self.mensSC2.show()
        self.escena.update()

    def remove_pieces(self, st):
        for a1h8 in st:
            self.borraPieza(a1h8)
