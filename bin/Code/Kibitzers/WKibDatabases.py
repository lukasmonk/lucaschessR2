from PySide2 import QtCore, QtWidgets

import Code
from Code import Procesador
from Code.Databases import WDB_Games, DBgames
from Code.Engines import EngineManager
from Code.Kibitzers import WKibCommon
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import Piezas


class InfoMoveReplace:
    board = None

    def modoPartida(self, x, y):
        return True


class WKibDatabases(WKibCommon.WKibCommon):
    def __init__(self, cpu):
        WKibCommon.WKibCommon.__init__(self, cpu, Iconos.Database())

        self.db = DBgames.DBgames(self.kibitzer.path_exe)
        Code.procesador = self
        Code.procesador.entrenamientos = self

        configuration = Code.configuration = self.cpu.configuration
        Code.list_engine_managers = EngineManager.ListEngineManagers()
        Code.all_pieces = Piezas.AllPieces()

        xtutor = EngineManager.EngineManager(configuration.engine_tutor())
        xtutor.function = _("Tutor")
        xtutor.options(configuration.x_tutor_mstime, configuration.x_tutor_depth, True)
        xtutor.set_priority(configuration.x_tutor_priority)
        if configuration.x_tutor_multipv == 0:
            xtutor.maximize_multipv()
        else:
            xtutor.set_multipv(configuration.x_tutor_multipv)

        self.xtutor = xtutor

        dic_video = self.cpu.dic_video
        if not dic_video:
            dic_video = {'_SIZE_': '886,581'}

        self.siTop = dic_video.get("SITOP", True)

        self.is_temporary = False
        self.wgames = WDB_Games.WGames(self, self.db, None, False)
        self.wgames.infoMove = InfoMoveReplace()
        self.wgames.wsummary = self

        self.wgames.edit = self.edit_game

        self.wgames.tbWork.hide()
        self.wgames.status.hide()

        self.grid = self.wgames.grid

        self.status = QtWidgets.QStatusBar(self)
        self.status.setFixedHeight(22)

        self.setWindowTitle(cpu.titulo)
        self.setWindowIcon(Iconos.Database())

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        li_acciones = (
            (_("Quit"), Iconos.Kibitzer_Close(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Kibitzer_Up(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Kibitzer_Down(), self.windowBottom),
            (_("Takeback"), Iconos.Kibitzer_Back(), self.takeback),
            (_("Show/hide board"), Iconos.Kibitzer_Board(), self.config_board),
            (_("Configure the columns"), Iconos.EditColumns(), self.edit_columns),
        )
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        lydata = Colocacion.V().control(self.wgames).control(self.status)

        ly_h = Colocacion.H().control(self.board).otro(lydata)
        layout = Colocacion.V().control(self.tb).espacio(-8).otro(ly_h).margen(3)
        self.setLayout(layout)

        self.setLayout(lydata)

        self.siPlay = True

        self.restore_video(dic_video)
        self.ponFlags()

        self.db.filter_pv("")
        self.wgames.grid.refresh()
        self.wgames.grid.gotop()
        self.pv = ""
        self.previous_stable = False
        self.show_num_games()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_input)
        self.timer.start(200)

        if not self.show_board:
            self.board.hide()

    def edit_columns(self):
        self.wgames.tw_edit_columns()

    def check_input(self):
        self.show_num_games()
        self.cpu.check_input()

    def tw_terminar(self):
        pass

    def ponFlags(self):
        flags = self.windowFlags()
        if self.siTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.tb.set_action_visible(self.windowTop, not self.siTop)
        self.tb.set_action_visible(self.windowBottom, self.siTop)
        self.show()

    def windowTop(self):
        self.siTop = True
        self.ponFlags()

    def windowBottom(self):
        self.siTop = False
        self.ponFlags()

    def terminar(self):
        self.finalizar()
        self.accept()

    def pause(self):
        self.siPlay = False
        self.tb.set_action_visible(self.pause, False)
        self.tb.set_action_visible(self.play, True)
        self.stop()

    def play(self):
        self.siPlay = True
        self.tb.set_action_visible(self.pause, True)
        self.tb.set_action_visible(self.play, False)
        self.reset()

    def stop(self):
        self.siPlay = False

    def closeEvent(self, event):
        self.finalizar()

    def finalizar(self):
        self.save_video()
        if self.db:
            self.db.close()
            self.db = None
            self.siPlay = False

    def orden_game(self, game):
        if self.siPlay:
            self.game = game
            position = game.last_position
            self.siW = position.is_white
            self.board.set_position(position)
            self.pv = game.pv()
            self.db.filter_pv(self.pv)
            self.wgames.grid.refresh()
            self.wgames.grid.gotop()
            self.board.activate_side(self.siW)
            self.siPlay = True
            self.show_num_games()
            self.previous_stable = False

    def show_num_games(self):
        if not self.previous_stable:
            reccount, stable = self.db.reccount_stable()
            message = _("Games") + f": {reccount}"
            self.previous_stable = stable
            if stable:
                li_moves = self.db.get_summary(self.pv, {}, False)
                if li_moves and reccount:
                    dicmove = li_moves[-1]
                    # win y lost es al revés
                    message += (f'  ||   {_("Wins")}: {dicmove["lost"]}  '
                                f'{_("Losses")}: {dicmove["win"]}  '
                                f'{_("Draws")}: {dicmove["draw"]}')
            self.status.showMessage(message, 0)

    def reset(self):
        self.orden_game(self.game)

    def manager_game(
            self, window, game, is_complete, only_consult, father_board, with_previous_next=None, save_routine=None
    ):

        clon_procesador = Procesador.ProcesadorVariations(
            window, self.xtutor, is_competitive=False,
        )
        manager = clon_procesador.manager = Procesador.ManagerGame.ManagerGame(clon_procesador)
        manager.si_check_kibitzers = self.si_check_kibitzers
        manager.kibitzers_manager = self
        manager.main_window.base.analysis_bar.game = game
        manager.with_eboard = False
        manager.start(game, is_complete, only_consult, with_previous_next, save_routine)

        board = clon_procesador.main_window.board
        if father_board:
            board.dbvisual_set_file(father_board.dbVisual.file)
            board.dbvisual_set_show_always(father_board.dbVisual.show_always())

        resp = clon_procesador.main_window.show_variations(game.window_title())
        if father_board:
            father_board.dbvisual_set_file(father_board.dbVisual.file)
            father_board.dbvisual_set_show_always(father_board.dbVisual.show_always())

        if resp:
            return clon_procesador.manager.game
        else:
            return None

    def edit_game(self, recno, game):
        if recno is None:
            with_previous_next = None
        else:
            with_previous_next = self.wgames.edit_previous_next
        game.recno = recno
        game = self.manager_game(
            self,
            game,
            not self.wgames.db_games.allows_positions,
            False,
            self.wgames.infoMove.board,
            with_previous_next=with_previous_next,
            save_routine=self.wgames.edit_save,
        )
        if game:
            self.wgames.changes = True
            self.wgames.edit_save(game.recno, game)

    def some_working(self):
        return False

    def analyzer_clone(self, a, b, c):
        return self.xtutor

    def creaManagerMotor(self, conf_motor, vtime, depth, has_multipv=False, priority=None):
        xmanager = EngineManager.EngineManager(conf_motor)
        xmanager.options(vtime, depth, has_multipv)
        xmanager.set_priority(priority)
        return xmanager

    def rehazActual(self):
        pass

    def put_game(self, a, b):
        pass

    def si_check_kibitzers(self):
        return False
