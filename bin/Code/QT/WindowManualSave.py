import encodings
import os

from PySide2 import QtWidgets, QtCore

from Code.Base import Game, Position
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.Voyager import Voyager


class WManualSave(LCDialog.LCDialog):
    def __init__(self, procesador):

        icono = Iconos.ManualSave()
        extparam = "manualsave"
        titulo = _("Edit and save positions to PGN or FNS")
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.position = Position.Position()
        self.position.set_pos_initial()

        self.manager_motor = None
        self.pgn = None
        self.fns = None

        self.li_labels = [
            ["Site", ""],
            ["Event", ""],
            ["Date", ""],
            ["White", ""],
            ["Black", ""],
            ["WhiteElo", ""],
            ["BlackElo", ""],
            ["Result", ""],
        ]
        self.li_labels.extend([["", ""] for x in range(10)])

        self.li_analysis = []
        self.analyzing = False

        self.game = None

        # Toolbar
        li_acciones = ((_("Close"), Iconos.MainMenu(), self.terminar), None)
        tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)

        # Board + botones + solucion + boton salvado
        ##
        bt_change_position = Controles.PB(self, "   " + _("Change position"), self.change_position, plano=False)
        bt_change_position.ponIcono(Iconos.Datos(), 24)
        ##
        conf_board = self.configuration.config_board("MANUALSAVE", 32)
        self.board = Board.Board(self, conf_board)
        self.board.crea()
        self.board.set_side_bottom(True)
        ##
        lybt, bt = QTVarios.ly_mini_buttons(self, "", siLibre=False, icon_size=24, siTiempo=False)
        ##
        self.em_solucion = Controles.EM(self, siHTML=False).altoMinimo(40).capturaCambios(self.reset_game)
        ##
        self.bt_solucion = Controles.PB(self, "   " + _("Save solution"), self.savesolucion, plano=False).ponIcono(
            Iconos.Grabar(), 24
        )
        self.bt_edit = Controles.PB(self, "   " + _("Edit"), self.edit_solucion, plano=False).ponIcono(
            Iconos.PlayGame()
        )
        ly = Colocacion.V().control(self.em_solucion).control(self.bt_edit)
        gb = Controles.GB(self, _("Solution"), ly)
        ###
        lybtp = Colocacion.H().control(bt_change_position).espacio(20).control(self.bt_solucion)
        lyT = Colocacion.V().otro(lybtp).control(self.board).otro(lybt).control(gb)
        gb_left = Controles.GB(self, "", lyT)

        # Ficheros PGN + FNS
        lb_pgn = Controles.LB(self, _("PGN") + ": ")
        self.bt_pgn = Controles.PB(self, "", self.pgn_select, plano=False).anchoMinimo(300)
        bt_no_pgn = Controles.PB(self, "", self.pgn_unselect).ponIcono(Iconos.Delete()).anchoFijo(16)
        lb_fns = Controles.LB(self, _("FNS") + ": ")
        self.bt_fns = Controles.PB(self, "", self.fns_select, plano=False).anchoMinimo(300)
        bt_no_fns = Controles.PB(self, "", self.fns_unselect).ponIcono(Iconos.Delete()).anchoFijo(16)

        # #Codec
        lb_codec = Controles.LB(self, _("Encoding") + ": ")
        liCodecs = [k for k in set(v for k, v in encodings.aliases.aliases.items())]
        liCodecs.sort()
        liCodecs = [(k, k) for k in liCodecs]
        liCodecs.insert(0, ("%s: %s" % (_("By default"), _("UTF-8")), "default"))
        self.codec = "default"
        self.cb_codecs = Controles.CB(self, liCodecs, self.codec)
        ###
        ly0 = Colocacion.G().control(lb_pgn, 0, 0).control(self.bt_pgn, 0, 1).control(bt_no_pgn, 0, 2)
        ly0.control(lb_fns, 1, 0).control(self.bt_fns, 1, 1).control(bt_no_fns, 1, 2)
        ly1 = Colocacion.H().control(lb_codec).control(self.cb_codecs).relleno(1)
        ly = Colocacion.V().otro(ly0).otro(ly1)
        gb_files = Controles.GB(self, _("File to save"), ly)

        # Labels + correlativo
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("LABEL", _("Label"), 80, edicion=Delegados.LineaTextoUTF8(), align_center=True)
        o_columns.nueva("VALUE", _("Value"), 280, edicion=Delegados.LineaTextoUTF8())
        self.grid_labels = Grid.Grid(self, o_columns, is_editable=True, xid=1)
        n = self.grid_labels.anchoColumnas()
        self.grid_labels.setFixedWidth(n + 20)
        self.register_grid(self.grid_labels)

        ##
        lb_number = Controles.LB(self, _("Correlative number") + ": ")
        self.sb_number = Controles.SB(self, 0, 0, 99999999).tamMaximo(50)
        lb_number_help = Controles.LB(self, _("Replace symbol # in Value column (#=3, ###=003)"))
        lb_number_help.setWordWrap(True)

        ly_number = Colocacion.H().control(lb_number).control(self.sb_number).control(lb_number_help, 4)

        ly = Colocacion.V().control(self.grid_labels).otro(ly_number)
        gb_labels = Controles.GB(self, _("PGN labels"), ly)

        # Analysis + grid + start/stop + multiPV
        self.bt_start = Controles.PB(self, "", self.start).ponIcono(Iconos.Pelicula_Seguir(), 32)
        self.bt_stop = Controles.PB(self, "", self.stop).ponIcono(Iconos.Pelicula_Pausa(), 32)
        self.bt_stop.hide()

        lb_engine = Controles.LB(self, _("Engine") + ":")
        list_engines = self.configuration.combo_engines()
        self.cb_engine = Controles.CB(self, list_engines, self.configuration.x_tutor_clave).capture_changes(
            self.reset_motor
        )

        lb_multipv = Controles.LB(self, _("Multi PV") + ": ")
        self.sb_multipv = Controles.SB(self, 1, 1, 500).tamMaximo(50)
        ##
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("PDT", _("Evaluation"), 100, align_center=True)
        o_columns.nueva("PGN", _("Solution"), 360)
        self.grid_analysis = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.register_grid(self.grid_analysis)
        ##
        lb_analysis_help = Controles.LB(self, _("Double click to send analysis line to solution"))
        ###
        ly_lin1 = Colocacion.H().control(self.bt_start).control(self.bt_stop).control(lb_engine).control(self.cb_engine)
        ly_lin1.relleno(1).control(lb_multipv).control(self.sb_multipv)
        ly = Colocacion.V().otro(ly_lin1).control(self.grid_analysis).control(lb_analysis_help)
        gb_analysis = Controles.GB(self, _("Analysis"), ly)

        # ZONA
        splitter_right = QtWidgets.QSplitter(self)
        splitter_right.setOrientation(QtCore.Qt.Vertical)
        splitter_right.addWidget(gb_files)
        splitter_right.addWidget(gb_labels)
        splitter_right.addWidget(gb_analysis)

        self.register_splitter(splitter_right, "RIGHT")
        ##
        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(gb_left)
        splitter.addWidget(splitter_right)

        self.register_splitter(splitter, "ALL")

        layout = Colocacion.V().control(tb).control(splitter).margen(5)

        self.setLayout(layout)

        self.inicializa()

    def inicializa(self):
        self.restore_video(anchoDefecto=758, altoDefecto=596)

        dic_vars = self.configuration.read_variables("manual_save")
        if dic_vars:
            fen = dic_vars.get("FEN", self.position.fen())
            self.position.read_fen(fen)

            self.em_solucion.set_text(dic_vars.get("SOLUTION", ""))

            self.pgn = dic_vars.get("PGN", "")
            self.bt_pgn.set_text(self.pgn)

            self.fns = dic_vars.get("FNS", "")
            self.bt_fns.set_text(self.fns)

            self.cb_codecs.set_value(dic_vars.get("CODEC", ""))

            self.li_labels = dic_vars.get("LI_LABELS", [])

            self.sb_number.set_value(dic_vars.get("NUMBER", 0))

            self.cb_engine.set_value(dic_vars.get("ENGINE", self.configuration.tutor_default))

            self.sb_multipv.set_value(dic_vars.get("MULTIPV", 1))

        self.board.set_position(self.position)
        self.reset_motor()
        self.test_save_solucion()

    def test_save_solucion(self):
        self.bt_solucion.setDisabled((not self.pgn) and (not self.fns))

    def finaliza(self):
        self.analyzing = False
        self.manager_motor.terminar()
        self.save_video()

        dic_vars = {
            "FEN": self.position.fen(),
            "SOLUTION": self.em_solucion.texto(),
            "PGN": self.pgn,
            "FNS": self.fns,
            "CODEC": self.cb_codecs.valor(),
            "LI_LABELS": self.li_labels,
            "NUMBER": self.sb_number.valor(),
            "ENGINE": self.cb_engine.valor(),
            "MULTIPV": self.sb_multipv.valor(),
        }

        self.configuration.write_variables("manual_save", dic_vars)

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def grid_num_datos(self, grid):
        return len(self.li_labels if grid.id == 1 else self.li_analysis)

    def grid_setvalue(self, grid, row, o_column, valor):
        n = 0 if o_column.key == "LABEL" else 1
        self.li_labels[row][n] = valor

    def grid_dato(self, grid, row, o_column):
        if grid.id == 1:
            n = 0 if o_column.key == "LABEL" else 1
            return self.li_labels[row][n]
        else:
            if o_column.key == "PDT":
                return self.li_analysis[row].ms_pdt
            else:
                return self.li_analysis[row].ms_pgn

    def grid_doble_click(self, grid, row, o_column):
        if grid == self.grid_analysis:
            self.em_solucion.set_text(self.li_analysis[row].ms_pgn)
            self.reset_game()
        self.grid_analysis.goto(row, 0)

    def start(self):
        self.sb_multipv.setDisabled(True)
        self.cb_engine.setDisabled(True)
        self.analyzing = True
        self.sb_multipv.setDisabled(True)
        self.show_stop()
        multipv = self.sb_multipv.valor()
        self.manager_motor.update_multipv(multipv)
        game = Game.Game(self.position)
        self.manager_motor.ac_inicio(game)
        QtCore.QTimer.singleShot(1000, self.lee_analisis)

    def lee_analisis(self):
        if self.analyzing:
            mrm = self.manager_motor.ac_estado()
            li = []
            for rm in mrm.li_rm:
                game = Game.Game(self.position)
                game.read_pv(rm.pv)
                game.ms_pgn = game.pgnBaseRAW()
                game.ms_pdt = rm.abbrev_text_pdt()
                li.append(game)
            self.li_analysis = li
            self.grid_analysis.refresh()

            QtCore.QTimer.singleShot(2000, self.lee_analisis)

    def stop(self):
        self.sb_multipv.setDisabled(False)
        self.cb_engine.setDisabled(False)
        self.analyzing = False
        self.show_start()
        if self.manager_motor:
            self.manager_motor.ac_final(0)

    def pgn_select(self):
        dirSalvados = self.configuration.save_folder()
        path = SelectFiles.salvaFichero(self, _("File to save"), dirSalvados, "pgn", False)
        if path:
            carpeta, file = os.path.split(path)
            if carpeta != self.configuration.save_folder():
                self.configuration.set_save_folder(carpeta)
            self.pgn = path
            self.bt_pgn.set_text(path)
        self.test_save_solucion()

    def pgn_unselect(self):
        self.pgn = None
        self.bt_pgn.set_text("")
        self.test_save_solucion()

    def fns_select(self):
        dir_inicial = self.configuration.personal_training_folder if self.fns is None else os.path.dirname(self.fns)
        path = SelectFiles.salvaFichero(self, _("File to save"), dir_inicial, "fns", False)
        if path:
            self.fns = path
            self.bt_fns.set_text(path)
        self.test_save_solucion()

    def fns_unselect(self):
        self.fns = None
        self.bt_fns.set_text("")
        self.test_save_solucion()

    def edit_solucion(self):
        self.reset_motor()
        pc = self.crea_game()
        pc = self.procesador.manager_game(self, pc, False, False, self.board)
        if pc:
            self.position = pc.first_position
            self.em_solucion.set_text(pc.pgnBaseRAW())

    def savesolucion(self):
        def open_file(fich):
            codec = self.cb_codecs.valor()
            if codec == "default":
                codec = "UTF-8"
            try:
                f = open(fich, "at", encoding=codec, errors="ignore")
            except:
                QTUtil2.message_error(self, _("Error opening file %s") % fich)
                f = None
            return f

        def write_file(fich, f, txt, quien):
            time = 0.5 if (self.pgn and self.fns) else 1.0
            try:
                f.write(txt)
                QTUtil2.temporary_message(self, "%s: %s" % (quien, _("Saved")), time)
            except:
                QTUtil2.message_error(self, _("Error writing to file %s") % fich)
            f.close()

        pc = self.crea_game()

        if self.pgn:
            f = open_file(self.pgn)
            if not f:
                return
            txt = pc.pgn() + "\n\n"
            write_file(self.pgn, f, txt, _("PGN"))

        if self.fns:
            f = open_file(self.fns)
            if not f:
                return
            fen = self.position.fen()
            li = ["%s: %s" % (k, v) for k, v in pc.li_tags if k != "FEN"]
            labels = ",".join(li)
            solucion = self.em_solucion.texto()
            linea = "%s|%s|%s\n" % (fen, labels, solucion)
            write_file(self.fns, f, linea, _("FNS"))

    def change_position(self):
        prev = self.analyzing
        self.stop()

        position, is_white_bottom = Voyager.voyager_position(self, self.position,
                                                             wownerowner=self.procesador.main_window)
        if position is not None:
            self.em_solucion.set_text("")
            self.position = position
            self.board.set_position(self.position)

            self.sb_number.set_value(self.sb_number.valor() + 1)

        if prev:
            self.start()

    def reset_motor(self):
        key = self.cb_engine.valor()
        if not key:
            return
        self.analyzing = False
        if self.manager_motor:
            self.manager_motor.terminar()
        self.stop()
        conf_engine = self.configuration.buscaRival(key)

        multipv = self.sb_multipv.valor()
        self.manager_motor = self.procesador.creaManagerMotor(conf_engine, 0, 0, has_multipv=multipv > 1)

    def ext_engines(self):
        if self.analyzing:
            return
        self.procesador.motoresExternos()
        valor = self.cb_engine.valor()
        list_engines = self.configuration.combo_engines()
        engine = self.configuration.x_tutor_clave
        for label, key in list_engines:
            if key == valor:
                engine = valor
                break
        self.cb_engine.rehacer(list_engines, engine)
        self.reset_motor()
        self.show_start()

    def show_start(self):
        self.bt_stop.hide()
        self.bt_start.show()

    def show_stop(self):
        self.bt_start.hide()
        self.bt_stop.show()

    def terminar(self):
        self.finaliza()
        self.accept()

    def closeEvent(self, event):
        self.finaliza()

    def crea_game(self):
        li_tags = []
        number = self.sb_number.valor()
        for key, value in self.li_labels:
            if key and value:
                if "#" in value:
                    n = value.count("#")
                    if n > 1:
                        t = "#" * n
                        if t in value:
                            value = value.replace(t, "%0" + "%d" % n + "d")
                            value = value % number
                        else:
                            value = value.replace("#", str(number), 1)
                    else:
                        value = value.replace("#", str(number))
            li_tags.append((key, value))
        li_tags.append(("FEN", self.position.fen()))
        li = ['[%s "%s"]\n' % (k, v) for k, v in li_tags]
        txt = "".join(li)
        pc = Game.Game(self.position)
        txt += "\n%s" % self.em_solucion.texto()
        pc.read_pgn(txt)
        return pc

    def reset_game(self):
        if self.game is not None:
            self.game = None
            self.board.set_position(self.position)

    def test_game(self):
        if not self.game:
            self.game = self.crea_game()
            self.board.set_position(self.position)
            self.game.mover_jugada = -1

    def MoverInicio(self):
        self.test_game()
        self.game.mover_jugada = -1
        self.board.set_position(self.position)

    def MoverAtras(self):
        self.test_game()
        if self.game.mover_jugada >= 0:
            self.game.mover_jugada -= 1
            if self.game.mover_jugada == -1:
                self.board.set_position(self.position)
            else:
                move = self.game.move(self.game.mover_jugada)
                self.board.set_position(move.position)
                self.board.put_arrow_sc(move.from_sq, move.to_sq)

    def MoverAdelante(self):
        self.test_game()
        if self.game.mover_jugada < (len(self.game) - 1):
            self.game.mover_jugada += 1
            move = self.game.move(self.game.mover_jugada)
            self.board.set_position(move.position)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)
            return True
        return False

    def MoverFinal(self):
        self.test_game()
        if len(self.game):
            self.game.mover_jugada = len(self.game) - 1
            move = self.game.move(self.game.mover_jugada)
            self.board.set_position(move.position)
            self.board.put_arrow_sc(move.from_sq, move.to_sq)


def manual_save(procesador):
    w = WManualSave(procesador)
    w.exec_()
