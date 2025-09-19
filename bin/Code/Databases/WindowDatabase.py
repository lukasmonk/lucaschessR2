from PySide2 import QtWidgets, QtCore

from Code.Databases import WDB_Games, WDB_Summary, WDB_Players, WDB_InfoMove, DBgames, WDB_GUtils, WDB_Perfomance
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTVarios


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

        self.db_games = DBgames.DBgames(file_database)

        self.game = None

        self.dicvideo = self.restore_dicvideo()
        dic_video = self.dicvideo

        si_summary = not si_select and self.db_games.allows_complete_games

        self.wplayer = None
        self.wsummary = None
        if si_summary:
            self.wplayer = WDB_Players.WPlayer(procesador, self, self.db_games)
            self.wplayer_active = False
            self.register_grid(self.wplayer.gridMovesBlack)
            self.register_grid(self.wplayer.gridMovesWhite)
            self.register_grid(self.wplayer.gridOpeningWhite)
            self.register_grid(self.wplayer.gridOpeningBlack)
            self.wsummary = WDB_Summary.WSummary(procesador, self, self.db_games, siMoves=False)
            self.register_grid(self.wsummary.grid)

        self.wgames = WDB_Games.WGames(self, self.db_games, self.wsummary, si_select)

        if si_summary:
            self.wperfomance = WDB_Perfomance.WPerfomance(self, self.wgames, self.db_games)
            self.register_grid(self.wperfomance.grid)

        self.ultFocus = None

        self.tab = Controles.Tab()
        self.tab.new_tab(self.wgames, _("Games"))
        if si_summary:
            self.tab.new_tab(self.wsummary, _("Opening explorer"))
            self.tab.dispatchChange(self.tab_changed)
            # if not si_select:
            self.tab.new_tab(self.wplayer, _("Players"))
            self.tab.new_tab(self.wperfomance, _("Perfomance Rating"))
        self.tab.set_font_type(puntos=procesador.configuration.x_tb_fontpoints)

        if self.owner and not self.is_temporary:
            li_acciones_work = [(_("Select another database"), Iconos.Database(), self.tw_select_other)]
            self.tbWork = QTVarios.LCTB(self, li_acciones_work, icon_size=20)
            self.tbWork.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.tab.setCornerWidget(self.tbWork)

        w = QtWidgets.QWidget(self)
        layoutv = Colocacion.V().control(self.tab).margen(4)
        w.setLayout(layoutv)

        self.infoMove = WDB_InfoMove.WInfomove(self)

        self.splitter = splitter = QtWidgets.QSplitter()
        splitter.addWidget(w)
        splitter.addWidget(self.infoMove)
        # self.splitter.splitterMoved.connect(self.handle_splitter_resize)

        layout = Colocacion.H().control(splitter).margen(0)
        self.setLayout(layout)

        self.restore_video(default_width=1200, default_height=600)
        if not dic_video:
            dic_video = {"SPLITTER": [800, 380], "TREE_1": 25, "TREE_2": 25, "TREE_3": 50, "TREE_4": 661}

        if "SPLITTER" not in dic_video:
            ancho = self.width()
            ancho_board = self.infoMove.board.width()
            sz = [ancho - ancho_board, ancho_board]
        else:
            sz = dic_video["SPLITTER"]
        self.splitter.setSizes(sz)

        dic_grid = self.db_games.read_config("dic_grid")
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
        self.db_games.close()
        if self.game is not None:
            self.accept()
        else:
            self.reject()

    def tw_cancelar(self):
        self.db_games.close()
        self.game = None
        self.reject()

    def tw_select_other(self):
        resp = QTVarios.select_db(self, self.configuration, False, True)
        if resp:
            if resp == ":n":
                dbpath = WDB_GUtils.new_database(self, self.configuration)
                if dbpath is not None:
                    self.configuration.set_last_database(dbpath)
                    self.reinit()
            else:
                self.configuration.set_last_database(resp)
                self.reinit()

    # def listaGamesSelected(self, no1=False):
    #     return self.wgames.listaSelected(no1)

    def tab_changed(self, ntab):
        QtWidgets.QApplication.processEvents()
        board = self.infoMove.board
        board.disable_all()

        if ntab == 0:  # in (0, 2):
            self.wgames.actualiza()
        elif ntab == 1:
            self.wsummary.gridActualiza()
        elif ntab == 2:
            self.wplayer.actualiza()
        elif ntab == 3:
            self.wperfomance.actualiza()
        self.infoMove.setVisible(ntab != 3)

    def inicializa(self):
        self.setWindowTitle(self.db_games.label())
        self.wgames.setdbGames(self.db_games)
        self.wgames.setInfoMove(self.infoMove)
        if self.wplayer is not None:
            self.wplayer.setInfoMove(self.infoMove)
            self.wplayer.setdbGames(self.db_games)
        if self.wsummary is not None:
            self.wsummary.setInfoMove(self.infoMove)
            self.wsummary.setdbGames(self.db_games)
            self.wsummary.actualizaPV("")
        self.wgames.actualiza(True)
        if self.is_temporary:
            self.wgames.adjustSize()

    def salvar(self):
        dic_extended = {"SPLITTER": self.splitter.sizes()}

        self.save_video(dic_extended)

        dic = {}
        self.wgames.grid.save_video(dic)
        self.db_games.save_config("dic_grid", dic)

    def reinit(self):
        self.salvar()
        self.db_games.close()
        self.reiniciar = True
        self.accept()

    def reinit_sinsalvar(self, must_close=True):
        if must_close:
            self.db_games.close()
        self.reiniciar = True
        self.accept()
