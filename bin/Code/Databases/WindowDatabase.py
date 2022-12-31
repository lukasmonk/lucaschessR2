import gettext
_ = gettext.gettext
from PySide2 import QtWidgets, QtCore

from Code.Databases import WDB_Games, WDB_Summary, WDB_Players, WDB_InfoMove, DBgames
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import LCDialog


class WBDatabase(LCDialog.LCDialog):
    def __init__(self, w_parent, procesador, file_database, is_temporary, si_select):
        self.is_temporary = is_temporary
        icono = Iconos.Database()
        extparam = "databases"
        titulo = _("Temporary database") if self.is_temporary else _("Database")
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)
        self.owner = w_parent

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.reiniciar = False  # lo usamos para cambiar de database

        self.dbGames = DBgames.DBgames(file_database)

        self.dicvideo = self.restore_dicvideo()
        dicVideo = self.dicvideo

        siSummary = not si_select

        self.wplayer = WDB_Players.WPlayer(procesador, self, self.dbGames)
        self.wplayer_active = False

        if siSummary:
            self.wsummary = WDB_Summary.WSummary(procesador, self, self.dbGames, siMoves=False)
            self.register_grid(self.wsummary.grid)

        else:
            self.wsummary = None

        self.wgames = WDB_Games.WGames(procesador, self, self.dbGames, self.wsummary, si_select)

        self.ultFocus = None

        self.tab = Controles.Tab()
        self.tab.new_tab(self.wgames, _("Games"))
        if siSummary:
            self.tab.new_tab(self.wsummary, _("Opening explorer"))
            self.tab.dispatchChange(self.tabChanged)
        if not si_select:
            self.tab.new_tab(self.wplayer, _("Players"))
        self.tab.ponTipoLetra(puntos=procesador.configuration.x_tb_fontpoints)

        if self.owner and not self.is_temporary:
            liAccionesWork = [(_("Select another database"), Iconos.Database(), self.tw_select_other)]
            self.tbWork = QTVarios.LCTB(self, liAccionesWork, icon_size=20)
            self.tbWork.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.tab.setCornerWidget(self.tbWork)

        w = QtWidgets.QWidget(self)
        layoutv = Colocacion.V().control(self.tab).margen(4)
        w.setLayout(layoutv)

        self.infoMove = WDB_InfoMove.WInfomove(self)

        self.splitter = splitter = QtWidgets.QSplitter()
        splitter.addWidget(w)
        splitter.addWidget(self.infoMove)

        layout = Colocacion.H().control(splitter).margen(0)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=1200, altoDefecto=600)
        if not dicVideo:
            dicVideo = {"SPLITTER": [800, 380], "TREE_1": 25, "TREE_2": 25, "TREE_3": 50, "TREE_4": 661}

        if not ("SPLITTER" in dicVideo):
            ancho = self.width()
            ancho_board = self.infoMove.board.width()
            sz = [ancho - ancho_board, ancho_board]
        else:
            sz = dicVideo["SPLITTER"]
        self.splitter.setSizes(sz)

        dic_grid = self.dbGames.read_config("dic_grid")
        if not dic_grid:
            key = "databases_columns_default"
            dic_grid = self.configuration.read_variables(key)
        if dic_grid:
            self.wgames.grid.restore_video(dic_grid)
            self.wgames.grid.releerColumnas()

        self.inicializa()

    def closeEvent(self, event):
        self.tw_terminar()

    def tw_terminar(self):
        self.wgames.tw_terminar()
        if self.wsummary:
            self.wsummary.close_db()
            self.wsummary = None
        self.salvar()
        self.accept()

    def tw_aceptar(self):
        self.game, recno = self.wgames.current_game()
        self.dbGames.close()
        if self.game is not None:
            self.accept()
        else:
            self.reject()

    def tw_cancelar(self):
        self.dbGames.close()
        self.game = None
        self.reject()

    def tw_select_other(self):
        resp = QTVarios.select_db(self, self.configuration, False, True)
        if resp:
            if resp == ":n":
                dbpath = WDB_Games.new_database(self, self.configuration)
                if dbpath is not None:
                    self.configuration.set_last_database(dbpath)
                    self.reinit()
            else:
                self.configuration.set_last_database(resp)
                self.reinit()

    def listaGamesSelected(self, no1=False):
        return self.wgames.listaSelected(no1)

    def tabChanged(self, ntab):
        QtWidgets.QApplication.processEvents()
        board = self.infoMove.board
        board.disable_all()
        if ntab == 0:
            self.wgames.actualiza()
        else:
            self.wsummary.gridActualiza()

    def inicializa(self):
        self.setWindowTitle(self.dbGames.label())
        self.wgames.setdbGames(self.dbGames)
        self.wgames.setInfoMove(self.infoMove)
        self.wplayer.setInfoMove(self.infoMove)
        self.wplayer.setdbGames(self.dbGames)
        if self.wsummary:
            self.wsummary.setInfoMove(self.infoMove)
            self.wsummary.setdbGames(self.dbGames)
            self.wsummary.actualizaPV("")
        self.wgames.actualiza(True)
        if self.is_temporary:
            self.wgames.adjustSize()

    def salvar(self):
        dic_extended = {"SPLITTER": self.splitter.sizes()}

        self.save_video(dic_extended)

        dic = {}
        self.wgames.grid.save_video(dic)
        self.dbGames.save_config("dic_grid", dic)

    def reinit(self):
        self.salvar()
        self.dbGames.close()
        self.reiniciar = True
        self.accept()

    def reinit_sinsalvar(self, must_close=True):
        if must_close:
            self.dbGames.close()
        self.reiniciar = True
        self.accept()
