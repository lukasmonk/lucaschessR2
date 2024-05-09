import io
import os
import time

from PIL import Image
from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Util
from Code.Base import Game, Move, Position
from Code.Base.Constantes import BLACK
from Code.Board import Board, Board2
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Voyager import Scanner

MODO_POSICION, MODO_PARTIDA = range(2)


def hamming_distance(string, other_string):
    # Adaptation from https://github.com/bunchesofdonald/photohash, MIT license
    """Computes the hamming distance between two strings."""
    return sum(map(lambda x: 0 if x[0] == x[1] else 1, zip(string, other_string)))


def average_hash(img, hash_size=8):
    # Adaptation from https://github.com/bunchesofdonald/photohash, MIT license
    """Computes the average hash of the given image."""
    # Open the image, resize it and convert it to black & white.
    image = img.resize((hash_size, hash_size), Image.ANTIALIAS).convert("L")
    pixels = list(image.getdata())

    avg = sum(pixels) // len(pixels)

    # Compute the hash based on each pixels value compared to the average.
    bits = "".join(map(lambda pixel: "1" if pixel > avg else "0", pixels))
    hashformat = "0{hashlength}x".format(hashlength=hash_size ** 2 // 4)
    return int(bits, 2).__format__(hashformat)


class WPosicion(QtWidgets.QWidget):
    def __init__(self, wparent, is_game, game, is_white_bottom):
        self.game = game
        self.position = game.first_position
        self.configuration = configuration = Code.configuration

        self.is_game = is_game

        self.wparent = wparent

        factor_big_fonts = Code.factor_big_fonts

        QtWidgets.QWidget.__init__(self, wparent)

        config_board = configuration.config_board("VOYAGERPOS", 24)
        self.board = Board2.PosBoard(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.mueve)
        self.board.mensBorrar = self.borraCasilla
        self.board.mensCrear = self.creaCasilla
        self.board.mensRepetir = self.repitePieza
        self.board.set_dispatch_drop(self.dispatchDrop)
        self.board.baseCasillasSC.setAcceptDrops(True)
        self.board.set_side_bottom(is_white_bottom)

        li_acciones = [
            (_("Save"), Iconos.GrabarComo(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Basic position"), Iconos.Inicio(), self.inicial),
            None,
            (_("Clear board"), Iconos.Borrar(), self.clear_board),
            None,
            (_("Paste FEN position"), Iconos.Pegar(), self.pegar),
            None,
            (_("Copy FEN position"), Iconos.Copiar(), self.copiar),
            None,
            (_("Scanner"), Iconos.Scanner(), self.scanner),
            None,
        ]
        if Code.eboard:
            li_acciones.append((_("Enable"), Code.eboard.icon_eboard(), self.eboard_activate))
            li_acciones.append(None)

        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)

        drag_drop_wb = QTVarios.ListaPiezas(self, "P,N,B,R,Q,K", self.board, margen=0)
        drag_drop_ba = QTVarios.ListaPiezas(self, "k,q,r,b,n,p", self.board, margen=0)

        self.rbWhite = Controles.RB(self, _("White"), rutina=self.change_side)
        self.rbBlack = Controles.RB(self, _("Black"), rutina=self.change_side)

        self.cbWoo = Controles.CHB(self, _("White") + " O-O", True)
        self.cbWooo = Controles.CHB(self, _("White") + " O-O-O", True)
        self.cbBoo = Controles.CHB(self, _("Black") + " O-O", True)
        self.cbBooo = Controles.CHB(self, _("Black") + " O-O-O", True)

        lb_en_passant = Controles.LB(self, _("En passant") + ":")
        self.edEnPassant = Controles.ED(self).controlrx("(-|[a-h][36])").anchoFijo(30*factor_big_fonts)

        self.edMovesPawn, lbMovesPawn = QTUtil2.spinbox_lb(self, 0, 0, 999, etiqueta=_("Halfmove clock"), max_width=50*factor_big_fonts)

        self.edFullMoves, lbFullMoves = QTUtil2.spinbox_lb(self, 1, 1, 999, etiqueta=_("Fullmove number"), max_width=50*factor_big_fonts)

        self.vars_scanner = Scanner.ScannerVars(self.configuration.carpetaScanners)

        self.lb_scanner = Controles.LB(self)

        pb_scanner_deduce = Controles.PB(self, _("Deduce"), self.scanner_deduce, plano=False)
        self.chb_scanner_flip = Controles.CHB(self, _("Flip the board"), False).capture_changes(self, self.scanner_flip)
        self.pb_scanner_learn = Controles.PB(self, _("Learn"), self.scanner_learn, plano=False)
        self.pb_scanner_learn_quit = Controles.PB(self, "", self.scanner_learn_quit).ponIcono(
            Iconos.Menos(), icon_size=24
        )
        self.pb_scanner_learn_quit.ponToolTip(_("Remove last learned")).anchoFijo(24*factor_big_fonts)

        self.sb_scanner_tolerance, lb_scanner_tolerance = QTUtil2.spinbox_lb(
            self, self.vars_scanner.tolerance, 3, 20, etiqueta=_("Deduction tolerance"), max_width=50*factor_big_fonts
        )
        self.sb_scanner_tolerance_learns, lb_scanner_tolerance_learns = QTUtil2.spinbox_lb(
            self, self.vars_scanner.tolerance_learns, 1, 6, etiqueta=_("Learning tolerance"), max_width=50*factor_big_fonts
        )

        self.chb_rem_ghost_deductions = Controles.CHB(self, _("Remove ghost deductions"), self.vars_scanner.rem_ghost)

        self.cb_scanner_select, lb_scanner_select = QTUtil2.combobox_lb(self, [], None, _("OPR"))
        self.cb_scanner_select.capture_changes(self.scanner_change)
        pb_scanner_more = Controles.PB(self, "", self.scanner_more).ponIcono(Iconos.Mas())

        self.chb_scanner_ask = Controles.CHB(self, _("Ask before new capture"), self.vars_scanner.ask)

        self.li_scan_pch = []
        self.is_scan_init = False
        self.im_scanner = None
        self.pixmap = None

        # LAYOUT -------------------------------------------------------------------------------------------
        hbox = Colocacion.H().control(self.rbWhite).espacio(15).control(self.rbBlack)
        gb_color = Controles.GB(self, _("Side to play"), hbox)

        ly = Colocacion.G().control(self.cbWoo, 0, 0).control(self.cbBoo, 0, 1)
        ly.control(self.cbWooo, 1, 0).control(self.cbBooo, 1, 1)
        gb_enroques = Controles.GB(self, _("Castling moves possible"), ly)

        ly = Colocacion.G()
        ly.controld(lbMovesPawn, 0, 0, 1, 3).control(self.edMovesPawn, 0, 3)
        ly.controld(lb_en_passant, 1, 0).control(self.edEnPassant, 1, 1)
        ly.controld(lbFullMoves, 1, 2).control(self.edFullMoves, 1, 3)
        gb_otros = Controles.GB(self, "", ly)

        ly_t = (
            Colocacion.H()
            .relleno()
            .control(lb_scanner_tolerance)
            .espacio(5)
            .control(self.sb_scanner_tolerance)
            .relleno()
        )
        ly_tl = (
            Colocacion.H()
            .relleno()
            .control(lb_scanner_tolerance_learns)
            .espacio(5)
            .control(self.sb_scanner_tolerance_learns)
            .relleno()
        )
        ly_l = Colocacion.H().control(self.pb_scanner_learn).control(self.pb_scanner_learn_quit)
        ly_s = Colocacion.H().control(lb_scanner_select).control(self.cb_scanner_select).control(pb_scanner_more)
        ly = Colocacion.V().control(self.chb_scanner_flip).control(pb_scanner_deduce).otro(ly_l).otro(ly_t).otro(ly_tl)
        ly.control(self.chb_rem_ghost_deductions).otro(ly_s)
        ly.control(self.chb_scanner_ask)
        self.gb_scanner = Controles.GB(self, _("Scanner"), ly)

        ly_g = Colocacion.G()
        ly_g.controlc(drag_drop_ba, 0, 0)
        ly_g.control(self.board, 1, 0).control(self.lb_scanner, 1, 1)
        ly_g.controlc(drag_drop_wb, 2, 0).controlc(self.gb_scanner, 2, 1, numFilas=4)
        ly_g.controlc(gb_color, 3, 0)
        ly_g.controlc(gb_enroques, 4, 0)
        ly_g.controlc(gb_otros, 5, 0)

        layout = Colocacion.V()
        layout.controlc(self.tb)
        layout.otro(ly_g)
        layout.margen(1)
        self.setLayout(layout)

        self.ultimaPieza = "P"
        self.piezas = self.board.piezas
        self.reset_position()
        self.ponCursor()

        self.lb_scanner.hide()
        self.pb_scanner_learn_quit.hide()
        self.gb_scanner.hide()

    def eboard_activate(self):
        if Code.eboard.driver:
            Code.eboard.deactivate()
        else:
            Code.eboard.activate(self.eboard_dispatch)

    def eboard_dispatch(self, quien, fen):
        self.position.read_fen(fen)
        self.actPosicion()
        self.reset_position(False)
        if fen.count("K") == 1 and fen.count("k") == 1:
            self.save()
        elif fen.count("k") == 1:
            self.rbWhite.activa(True)
        elif fen.count("K") == 1:
            self.rbBlack.activa(True)

    def closeEvent(self, event):
        self.scanner_write()

    def change_side(self):
        self.board.set_side_indicator(self.rbWhite.isChecked())
        self.actPosicion()
        self.reset_position()

    def save(self):
        self.actPosicion()
        si_kw = False
        si_kb = False
        si_p1 = False
        for a1h8, pz in self.squares.items():
            if pz and a1h8:
                if pz == "K":
                    si_kw = True
                elif pz == "k":
                    si_kb = True
                elif pz in "pP" and a1h8[1] in "18":
                    si_p1 = True
        if not si_kw:
            QTUtil2.message_error(self, _("King") + "-" + _("White") + "???")
            return
        if not si_kb:
            QTUtil2.message_error(self, _("King") + "-" + _("Black") + "???")
            return
        if si_p1:
            QTUtil2.message_error(self, _("Pawns in the first or last row"))
            return

        self.position.is_white = not self.position.is_white
        if self.position.is_check():
            self.position.is_white = not self.position.is_white
            QTUtil2.message_error(self, _("The king is in check"))
            return
        self.position.is_white = not self.position.is_white
        self.wparent.setPosicion(self.position)
        self.scanner_write()
        if self.is_game:
            self.wparent.ponModo(MODO_PARTIDA)
        else:
            self.wparent.save()

    def cancelar(self):
        if Code.eboard:
            Code.eboard.deactivate()
        self.scanner_write()
        if self.is_game:
            self.wparent.ponModo(MODO_PARTIDA)
        else:
            self.wparent.cancelar()

    def ponCursor(self):
        cursor = self.piezas.cursor(self.ultimaPieza)
        for item in self.board.escena.items():
            item.setCursor(cursor)
        self.board.setCursor(cursor)

    def cambiaPiezaSegun(self, pieza):
        ant = self.ultimaPieza
        if ant.upper() == pieza:
            if ant == pieza:
                pieza = pieza.lower()
        self.ultimaPieza = pieza
        self.ponCursor()

    def mueve(self, from_sq, to_sq):
        if from_sq == to_sq:
            return
        if self.squares.get(to_sq):
            self.board.borraPieza(to_sq)
        self.squares[to_sq] = self.squares.get(from_sq)
        self.squares.pop(from_sq, None)
        self.board.muevePieza(from_sq, to_sq)

        self.ponCursor()

    def dispatchDrop(self, from_sq, qbpieza):
        pieza = qbpieza[0]
        if self.squares.get(from_sq):
            self.borraCasilla(from_sq)
        self.ponPieza(from_sq, pieza)

    def borraCasilla(self, from_sq):
        self.squares[from_sq] = None
        self.board.borraPieza(from_sq)

    def creaCasilla(self, from_sq):
        menu = QtWidgets.QMenu(self)

        si_kw = False
        si_kb = False
        for p in self.squares.values():
            if p == "K":
                si_kw = True
            elif p == "k":
                si_kb = True

        li_options = []
        if not si_kw:
            li_options.append((_("King"), "K"))
        li_options.extend(
            [(_("Queen"), "Q"), (_("Rook"), "R"), (_("Bishop"), "B"), (_("Knight"), "N"), (_("Pawn"), "P")]
        )
        if not si_kb:
            li_options.append((_("King"), "k"))
        li_options.extend(
            [(_("Queen"), "q"), (_("Rook"), "r"), (_("Bishop"), "b"), (_("Knight"), "n"), (_("Pawn"), "p")]
        )

        for txt, pieza in li_options:
            icono = self.board.piezas.icono(pieza)

            accion = QtWidgets.QAction(icono, txt, menu)
            accion.key = pieza
            menu.addAction(accion)

        resp = menu.exec_(QtGui.QCursor.pos())
        if resp:
            pieza = resp.key
            self.ponPieza(from_sq, pieza)

    def ponPieza(self, from_sq, pieza):
        antultimo = self.ultimaPieza
        self.ultimaPieza = pieza
        self.repitePieza(from_sq)
        if pieza == "K":
            self.ultimaPieza = antultimo
        if pieza == "k":
            self.ultimaPieza = antultimo

        self.ponCursor()

    def repitePieza(self, from_sq):
        pieza = self.ultimaPieza
        if pieza in "kK":
            for pos, pz in self.squares.items():
                if pz == pieza:
                    self.borraCasilla(pos)
                    break
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            if pieza.islower():
                pieza = pieza.upper()
            else:
                pieza = pieza.lower()
        self.squares[from_sq] = pieza
        pieza = self.board.creaPieza(pieza, from_sq)
        pieza.activa(True)

        self.ponCursor()

    def leeDatos(self):
        is_white = self.rbWhite.isChecked()
        en_passant = self.edEnPassant.texto().strip()
        if not en_passant:
            en_passant = "-"
        num_moves = self.edFullMoves.value()
        mov_pawn_capt = self.edMovesPawn.value()

        castles = ""
        for cont, pieza in ((self.cbWoo, "K"), (self.cbWooo, "Q"), (self.cbBoo, "k"), (self.cbBooo, "q")):
            if cont.isChecked():
                castles += pieza
        if not castles:
            castles = "-"
        return is_white, en_passant, num_moves, mov_pawn_capt, castles

    def actPosicion(self):
        (
            self.position.is_white,
            self.position.en_passant,
            self.position.num_moves,
            self.position.mov_pawn_capt,
            self.position.castles,
        ) = self.leeDatos()
        castles = self.position.castles
        self.cbWoo.set_value("K" in castles)
        self.cbWooo.set_value("Q" in castles)
        self.cbBoo.set_value("k" in castles)
        self.cbBooo.set_value("q" in castles)

    def setPosicion(self, position):
        self.position = position.copia()
        self.reset_position()

    def pegar(self):
        tp, data = QTUtil.get_clipboard()
        if tp:
            if tp == "t":
                try:
                    self.position.read_fen(str(data))
                    self.reset_position()
                except:
                    pass
            elif tp == "h":
                try:
                    self.position.read_fen(QTUtil.get_txt_clipboard())
                    self.reset_position()
                except:
                    pass
            elif tp == "p":
                if not self.is_scan_init:
                    self.scanner_init()
                    self.is_scan_init = True
                img: QtGui.QImage = data
                path_png = Code.configuration.ficheroTemporal("png")
                img.save(path_png)
                self.im_scanner = Image.open(path_png)
                self.scanner_process()
                tc = self.board.width_square * 8
                self.pixmap = QtGui.QPixmap(path_png)
                pm = self.pixmap.scaled(tc, tc)
                self.lb_scanner.ponImagen(pm)
                self.lb_scanner.show()
                self.gb_scanner.show()
                self.scanner_deduce()

                self.setFocus()

    def copiar(self):
        self.actPosicion()
        QTUtil.ponPortapapeles(self.position.fen())
        QTVarios.fen_is_in_clipboard(self)

    def clear_board(self):
        self.position.read_fen("8/8/8/8/8/8/8/8 w - - 0 1")
        self.reset_position()

    def inicial(self):
        self.position.set_pos_initial()
        self.reset_position()

    def reset_position(self, reset_all=True):
        self.board.set_position(self.position)
        self.squares = self.position.squares
        self.board.squares = self.squares
        self.board.enable_all()

        if reset_all:
            if self.position.is_white:
                self.rbWhite.activa(True)
            else:
                self.rbBlack.activa(True)

            # Enroques permitidos
            castles = self.position.castles
            self.cbWoo.setChecked("K" in castles)
            self.cbWooo.setChecked("Q" in castles)
            self.cbBoo.setChecked("k" in castles)
            self.cbBooo.setChecked("q" in castles)

            # Otros
            self.edEnPassant.set_text(self.position.en_passant)
            self.edFullMoves.setValue(self.position.num_moves)
            self.edMovesPawn.setValue(self.position.mov_pawn_capt)

    def scanner(self):
        self.wparent.showMinimized()
        QTUtil.refresh_gui()

        if self.chb_scanner_ask.valor() and not QTUtil2.pregunta(
                None, _("Bring the window to scan to front"), label_yes=_("Accept"), label_no=_("Cancel"), si_top=True,
        ):
            self.wparent.showNormal()
            return

        time.sleep(0.2)
        QTUtil.refresh_gui()
        time.sleep(0.2)
        QTUtil.refresh_gui()

        screen = QtWidgets.QApplication.primaryScreen()
        desktop = screen.grabWindow(0, 0, 0, QTUtil.desktop_width(), QTUtil.desktop_height())

        self.wparent.showNormal()

        if not self.is_scan_init:
            self.scanner_init()
            self.is_scan_init = True

        if Code.configuration.x_enable_highdpiscaling:
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)

        sc = Scanner.Scanner(self, self.configuration.carpetaScanners, desktop)
        if not sc.exec_():
            if Code.configuration.x_enable_highdpiscaling:
                QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
            return

        if Code.configuration.x_enable_highdpiscaling:
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        self.vars_scanner.read()
        self.vars_scanner.tolerance = self.sb_scanner_tolerance.valor()  # releemos la variable
        self.vars_scanner.tolerance_learns = min(
            self.sb_scanner_tolerance_learns.valor(), self.vars_scanner.tolerance
        )

        self.chb_scanner_flip.set_value(sc.side == BLACK)

        self.pixmap = sc.selected_pixmap
        img = self.pixmap.toImage()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        self.im_scanner = Image.open(io.BytesIO(buffer.data()))
        self.scanner_process()
        tc = self.board.width_square * 8
        pm = self.pixmap.scaled(tc, tc)
        self.lb_scanner.ponImagen(pm)
        self.lb_scanner.show()
        self.gb_scanner.show()
        self.scanner_deduce()

        self.setFocus()

    def scanner_process(self):
        im = self.im_scanner
        flipped = self.chb_scanner_flip.isChecked()
        w, h = im.size
        tam = w // 8
        dic = {}
        dic_color = {}
        for f in range(8):
            for c in range(8):
                if flipped:
                    fil = chr(49 + f)
                    col = chr(97 + 7 - c)
                else:
                    fil = chr(49 + 7 - f)
                    col = chr(97 + c)
                x = c * tam + 2
                y = f * tam + 2
                x1 = x + tam - 4
                y1 = y + tam - 4
                im_t = im.crop((x, y, x1, y1))
                pos = "%s%s" % (col, fil)
                dic[pos] = average_hash(im_t, hash_size=8)
                dic_color[pos] = (f + c) % 2 == 0
        self.dicscan_pos_hash = dic
        self.dic_pos_color = dic_color
        is_white_bottom = self.board.is_white_bottom
        if (is_white_bottom and flipped) or ((not is_white_bottom) and (not flipped)):
            self.board.rotaBoard()

    def scanner_flip(self):
        self.scanner_process()
        self.scanner_deduce()

    def scanner_deduce_base(self, extended):
        tolerance = self.sb_scanner_tolerance.valor()
        dic = {}
        for pos, hs in self.dicscan_pos_hash.items():
            pz = None
            dt = 99999999
            reg = None
            cl = self.dic_pos_color[pos]
            for piece, color, hsp in self.li_scan_pch:
                if cl == color:
                    dtp = hamming_distance(hs, hsp)
                    if dtp <= dt:
                        pz = piece
                        dt = dtp
                        reg = piece, color, hsp
            if pz and dt <= tolerance:
                if extended:
                    dic[pos] = pz, reg, dt
                else:
                    dic[pos] = pz
        return dic

    def scanner_deduce(self):
        self.actPosicion()
        fen = "8/8/8/8/8/8/8/8 w KQkq - 0 1"
        if not self.position.is_white:
            fen = fen.replace("w", "b")
        self.position.read_fen(fen)
        self.actPosicion()
        self.reset_position()
        dic = self.scanner_deduce_base(False)
        for pos, pz in dic.items():
            self.ponPieza(pos, pz)

    def scanner_learn(self):
        cp = Position.Position()
        cp.read_fen(self.board.fen_active())
        tolerance = self.sb_scanner_tolerance.valor()
        tolerance_learn = min(self.sb_scanner_tolerance_learns.valor(), tolerance)

        self.n_scan_last_added = len(self.li_scan_pch)
        dic_deduced_extended = self.scanner_deduce_base(True)

        for pos, pz_real in cp.squares.items():
            if pz_real:
                resp = dic_deduced_extended.get(pos)
                if resp is None:
                    pz_deduced = None
                    dt = 99
                else:
                    pz_deduced, reg_scan, dt = resp
                if (not pz_deduced) or (pz_real != pz_deduced) or dt > tolerance_learn:
                    color_celda = self.dic_pos_color[pos]
                    hs = self.dicscan_pos_hash[pos]
                    key = (pz_real, color_celda, hs)
                    self.li_scan_pch.append(key)

        if self.chb_rem_ghost_deductions.valor():
            for pos_a1h8, (pz_deduced, reg_scan, dt) in dic_deduced_extended.items():
                if cp.get_pz(pos_a1h8) is None:  # ghost
                    pz, color, hs = reg_scan
                    for pos_li, (xpz, xcolor, xhs) in enumerate(self.li_scan_pch):
                        if pz == xpz and color == xcolor and hs == xhs:
                            del self.li_scan_pch[pos_li]
                            break

        self.scanner_show_learned()

    def scanner_learn_quit(self):
        self.li_scan_pch = self.li_scan_pch[: self.n_scan_last_added]
        self.scanner_show_learned()

    def scanner_more(self):
        name = ""
        while True:
            li_gen = []

            config = FormLayout.Editbox(_("Name"), ancho=120)
            li_gen.append((config, name))

            resultado = FormLayout.fedit(
                li_gen, title=_("New scanner"), parent=self, anchoMinimo=200, icon=Iconos.Scanner()
            )
            if resultado:
                accion, li_gen = resultado
                name = li_gen[0].strip()
                if name:
                    fich = Util.opj(self.configuration.carpetaScanners, "%s.scn" % name)
                    if Util.exist_file(fich):
                        QTUtil2.message_error(self, _("This scanner already exists."))
                        continue
                    try:
                        with open(fich, "w") as f:
                            f.write("")
                        self.scanner_reread(name)
                        return
                    except:
                        QTUtil2.message_error(self, _("This name is not valid to create a scanner file."))
                        continue
            return

    def scanner_init(self):
        scanner = self.vars_scanner.scanner
        self.scanner_reread(scanner)

    def scanner_change(self):
        fich_scanner = self.cb_scanner_select.valor()
        self.vars_scanner.scanner = os.path.basename(fich_scanner)[:-4]
        self.scanner_read()

    def scanner_reread(self, label_default):
        dsc = self.configuration.carpetaScanners
        lista = [fich for fich in os.listdir(dsc) if fich.endswith(".scn")]
        li = [(fich[:-4], Util.opj(dsc, fich)) for fich in lista]
        fich_default = None
        if not label_default:
            if li:
                label_default, fich_default = li[0]

        for label, fich in li:
            if label == label_default:
                fich_default = fich

        self.cb_scanner_select.rehacer(li, fich_default)
        self.cb_scanner_select.show()
        self.scanner_read()

    def scanner_read(self):
        self.li_scan_pch = []
        self.n_scan_last_save = 0
        self.n_scan_last_added = 0
        fich = self.cb_scanner_select.valor()
        if not fich:
            return
        if Util.filesize(fich):
            with open(fich) as f:
                for linea in f:
                    self.li_scan_pch.append(eval(linea.strip()))
        self.n_scan_last_save = len(self.li_scan_pch)
        self.n_scan_last_added = self.n_scan_last_save

        self.scanner_show_learned()

    def scanner_show_learned(self):
        self.pb_scanner_learn.set_text("%s (%d)" % (_("Learn"), len(self.li_scan_pch)))
        self.pb_scanner_learn_quit.setVisible(self.n_scan_last_added < len(self.li_scan_pch))

    def scanner_write(self):
        fich_scanner = self.cb_scanner_select.valor()
        if not fich_scanner:
            return

        tam = len(self.li_scan_pch)
        if tam > self.n_scan_last_save:
            with open(fich_scanner, "a") as q:
                for x in range(self.n_scan_last_save, tam):
                    q.write(str(self.li_scan_pch[x]).replace(" ", ""))
                    q.write("\n")
            self.n_scan_last_save = tam
            self.n_scan_last_added = tam

        self.vars_scanner.scanner = os.path.basename(fich_scanner)[:-4]
        self.vars_scanner.tolerance = self.sb_scanner_tolerance.valor()
        self.vars_scanner.tolerance_learns = self.sb_scanner_tolerance_learns.valor()
        self.vars_scanner.ask = self.chb_scanner_ask.valor()
        self.vars_scanner.rem_ghost = self.chb_rem_ghost_deductions.valor()
        self.vars_scanner.write()

    def keyPressEvent(self, event):
        k = event.key()

        if k == QtCore.Qt.Key_V:
            self.pegar()

        event.ignore()


class WPGN(QtWidgets.QWidget):
    def __init__(self, wparent, game):
        self.game = game

        self.wparent = wparent
        self.configuration = configuration = Code.configuration
        QtWidgets.QWidget.__init__(self, wparent)

        li_acciones = (
            (_("Save"), Iconos.Grabar(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.wparent.cancelar),
            None,
            (_("Start position"), Iconos.NuevaPartida(), self.inicial),
            None,
            (_("Remove all moves"), Iconos.Borrar(), self.limpia),
            None,
            (_("Takeback"), Iconos.Atras(), self.atras),
            None,
        )

        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)

        config_board = configuration.config_board("VOYAGERPGN", 24)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.player_has_moved)
        Delegados.genera_pm(self.board.piezas)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 35, align_center=True)
        self.with_figurines = configuration.x_pgn_withfigurines
        nAnchoColor = (self.board.ancho - 35 - 20) // 2
        o_columns.nueva(
            "WHITE", _("White"), nAnchoColor, edicion=Delegados.EtiquetaPGN(True if self.with_figurines else None)
        )
        o_columns.nueva(
            "BLACK", _("Black"), nAnchoColor, edicion=Delegados.EtiquetaPGN(False if self.with_figurines else None)
        )
        self.pgn = Grid.Grid(self, o_columns, siCabeceraMovible=False, siSelecFilas=True)
        self.pgn.setMinimumWidth(self.board.ancho)

        ly = Colocacion.V().control(self.tb).control(self.board)
        ly.control(self.pgn)
        ly.margen(1)
        self.setLayout(ly)

        self.board.set_position(self.game.last_position)
        self.play_next_move()

    def save(self):
        self.wparent.save()

    def limpia(self):
        self.game.li_moves = []
        self.board.set_position(self.game.first_position)
        self.play_next_move()

    def atras(self):
        n = len(self.game)
        if n:
            self.game.li_moves = self.game.li_moves[:-1]
            move = self.game.move(n - 2)
            if move:
                self.board.set_position(move.position)
                self.board.put_arrow_sc(move.from_sq, move.to_sq)
            else:
                self.board.set_position(self.game.first_position)
            self.play_next_move()

    def inicial(self):
        self.wparent.ponModo(MODO_POSICION)

    def play_next_move(self):
        self.tb.set_action_visible(self.inicial, len(self.game) == 0)
        if self.game.is_finished():
            self.board.disable_all()
            return
        self.pgn.refresh()
        self.pgn.gobottom()
        self.board.activate_side(self.game.last_position.is_white)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        if not promotion and self.game.last_position.pawn_can_promote(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.game.last_position.is_white)

        ok, mens, move = Move.get_game_move(self.game, self.game.last_position, from_sq, to_sq, promotion)

        if ok:
            self.game.add_move(move)
            self.board.set_position(move.position)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)

            self.play_next_move()
            return True
        else:
            return False

    def grid_num_datos(self, grid):
        n = len(self.game)
        if not n:
            return 0
        if self.game.starts_with_black:
            n += 1
        if n % 2:
            n += 1
        return n // 2

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "NUMBER":
            return str(self.game.first_position.num_moves + row)

        si_ini_black = self.game.starts_with_black
        n_jug = len(self.game)
        if row == 0:
            w = None if si_ini_black else 0
            b = 0 if si_ini_black else 1
        else:
            n = row * 2
            w = n - 1 if si_ini_black else n
            b = w + 1
        if b >= n_jug:
            b = None

        def xjug(xn):
            if xn is None:
                return ""
            move = self.game.move(xn)
            if self.with_figurines:
                return move.pgn_figurines()
            else:
                return move.pgn_translated()

        if col == "WHITE":
            return xjug(w)
        else:
            return xjug(b)


class Voyager(LCDialog.LCDialog):
    def __init__(self, owner, is_game, game):
        titulo = _("Voyager 2") if is_game else _("Start position")
        icono = Iconos.Voyager() if is_game else Iconos.Datos()
        LCDialog.LCDialog.__init__(self, None, titulo, icono, "voyager")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.is_game = is_game
        self.game = game.copia()
        self.resultado = None

        is_white_bottom = True
        if hasattr(owner, "board"):
            is_white_bottom = owner.board.is_white_bottom
        self.wPos = WPosicion(self, is_game, self.game, is_white_bottom)
        self.wPGN = WPGN(self, self.game)

        ly = Colocacion.V().control(self.wPos).control(self.wPGN).margen(0)
        self.setLayout(ly)

        self.ponModo(MODO_PARTIDA if self.is_game else MODO_POSICION)

        self.restore_video(siTam=False)

    def is_white_bottom(self):
        return self.wPos.board.is_white_bottom

    def ponModo(self, modo):
        self.modo = modo
        if modo == MODO_POSICION:
            self.wPos.setPosicion(self.game.first_position)
            self.wPGN.setVisible(False)
            self.wPos.setVisible(True)
        else:
            self.wPos.setVisible(False)
            self.wPGN.setVisible(True)

    def setPosicion(self, position):
        self.game.first_position = position
        self.wPGN.limpia()

    def save(self):
        self.resultado = self.game.save() if self.is_game else self.game.first_position
        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def closeEvent(self, event):
        self.cancelar()


def voyager_position(wowner, position, wownerowner=None):
    wownerowner_maximized = None
    if wownerowner:
        wownerowner_maximized = wownerowner.isMaximized()
        wownerowner.showMinimized()
    wowner_maximized = wowner.isMaximized()
    wowner.showMinimized()

    game = Game.Game(first_position=position)
    dlg = Voyager(wowner, False, game)
    resp = dlg.resultado if dlg.exec_() else None

    if wowner_maximized:
        wowner.showMaximized()
    else:
        wowner.showNormal()
    if wownerowner:
        if wownerowner_maximized:
            wownerowner.showMaximized()
        else:
            wownerowner.showNormal()
    QTUtil.refresh_gui()

    return resp, dlg.is_white_bottom()


def voyager_game(wowner, game):
    wowner_maximized = wowner.isMaximized()
    wowner.showMinimized()
    dlg = Voyager(wowner, True, game)
    resp = dlg.resultado if dlg.exec_() else None
    if wowner_maximized:
        wowner.showMaximized()
    else:
        wowner.showNormal()
    QTUtil.refresh_gui()
    return resp
