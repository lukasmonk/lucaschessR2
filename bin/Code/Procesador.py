import os
import random
import stat
import sys
import webbrowser

import Code
from Code import Adjournments
from Code import CPU
from Code import ManagerEntPos
from Code import ManagerGame
from Code import ManagerSolo
from Code import Update
from Code import Util
from Code.About import About
from Code.Base import Position
from Code.Base.Constantes import (
    ST_PLAYING,
    TB_ADJOURNMENTS,
    TB_COMPETE,
    TB_INFORMATION,
    TB_OPTIONS,
    TB_PLAY,
    TB_QUIT,
    TB_TOOLS,
    TB_TRAIN,
    TB_REPLAY,
    GT_AGAINST_GM,
    GT_BOOK,
    GT_ELO,
    GT_MICELO,
    GT_WICKER,
    GT_AGAINST_ENGINE_LEAGUE,
    GT_AGAINST_CHILD_ENGINE,
    GT_AGAINST_ENGINE,
    GT_ALBUM,
    GT_COMPETITION_WITH_TUTOR,
    GT_FICS,
    GT_FIDE,
    GT_LICHESS,
    GT_HUMAN,
    OUT_REINIT,
    ENG_WICKER,
    TOP_RIGHT,
)
from Code.BestMoveTraining import WindowBMT
from Code.Board import WBoardColors, Eboard
from Code.Books import WFactory, WPolyglot, WBooksTrain, ManagerTrainBooks, WBooks, WBooksTrainOL, ManagerTrainBooksOL
from Code.CompetitionWithTutor import WCompetitionWithTutor, ManagerCompeticion
from Code.Competitions import ManagerElo, ManagerFideFics, ManagerMicElo, ManagerWicker
from Code.Config import Configuration, WindowConfig, WindowUsuarios
from Code.Databases import WindowDatabase, WDB_Games, DBgames
from Code.Endings import WEndingsGTB
from Code.Engines import EngineManager, WEngines, WConfEngines, WindowSTS, EnginesWicker, CheckEngines
from Code.Expeditions import WindowEverest, ManagerEverest
from Code.GM import ManagerGM
from Code.Kibitzers import KibitzersManager
from Code.Leagues import ManagerLeague, WLeagues
from Code.LearnGame import WindowPlayGame, ManagerPlayGame, WindowLearnGame
from Code.MainWindow import MainWindow, Presentacion, LucasChessGui
from Code.Maps import WindowWorkMap, ManagerMateMap
from Code.Menus import MenuTrainings, BasicMenus
from Code.Openings import ManagerOPLPositions, ManagerOPLEngines, ManagerOPLSequential, ManagerOPLStatic
from Code.Openings import WindowOpenings, WindowOpeningLine, WindowOpeningLines, OpeningLines, OpeningsStd
from Code.PlayAgainstEngine import ManagerPerson, Albums, ManagerAlbum, WindowAlbumes
from Code.PlayAgainstEngine import ManagerPlayAgainstEngine, WPlayAgainstEngine
from Code.PlayHuman import ManagerPlayHuman, WPlayHuman
from Code.QT import Delegados
from Code.QT import Iconos
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.QT import WColors
from Code.QT import WindowManualSave
from Code.Routes import Routes, WindowRoutes, ManagerRoutes
from Code.SQL import UtilSQL
from Code.SingularMoves import WindowSingularM, ManagerSingularM
from Code.Sound import WindowSonido
from Code.Swiss import WSwisses, ManagerSwiss
from Code.Tournaments import WTournaments
from Code.Washing import ManagerWashing, WindowWashing
from Code.WritingDown import WritingDown, ManagerWritingDown
from Code import RemoveResults


class Procesador:
    user = None
    li_opciones_inicio = None
    configuration = None
    manager = None
    version = None
    entrenamientos = None
    board = None
    is_first_time = None

    def __init__(self):

        if Code.list_engine_managers is None:
            Code.list_engine_managers = EngineManager.ListEngineManagers()

        self.web = "https://lucaschess.pythonanywhere.com"
        self.blog = "https://lucaschess.blogspot.com"
        self.github = "https://github.com/lukasmonk/lucaschessR2"
        self.wiki = "https://chessionate.com/lucaswiki"

        self.main_window = None
        self.kibitzers_manager = KibitzersManager.Manager(self)

    def start_with_user(self, user):
        self.user = user

        self.li_opciones_inicio = [
            TB_QUIT,
            TB_PLAY,
            TB_TRAIN,
            TB_COMPETE,
            TB_TOOLS,
            TB_OPTIONS,
            TB_INFORMATION,
        ]  # Lo incluimos aqui porque sino no lo lee, en caso de aplazada

        self.configuration = Configuration.Configuration(user)
        self.configuration.start()
        Code.procesador = self
        Code.runSound.read_sounds()
        OpeningsStd.ap.reset()

        if Code.configuration.x_digital_board:
            Code.eboard = Eboard.Eboard()

        if len(sys.argv) == 1:  # si no no funcionan los kibitzers en linux
            self.configuration.clean_tmp_folder()

        # Tras crear configuración miramos si hay Adjournments
        self.test_opcion_Adjournments()

        Code.all_pieces = Piezas.AllPieces()

        self.manager = None

        self.is_first_time = True
        self.siPresentacion = False  # si esta funcionando la presentacion

        self.posicionInicial = Position.Position()
        self.posicionInicial.set_pos_initial()

        self.xrival = None
        self.xtutor = None  # creaTutor lo usa asi que hay que definirlo antes
        self.xanalyzer = None  # cuando se juega ManagerEntMaq y el tutor danzando a toda maquina,
        # se necesita otro diferente
        self.replay = None
        self.replayBeep = None

    def test_opcion_Adjournments(self):
        must_adjourn = len(Adjournments.Adjournments()) > 0
        if TB_ADJOURNMENTS in self.li_opciones_inicio:
            if not must_adjourn:
                pos = self.li_opciones_inicio.index(TB_ADJOURNMENTS)
                del self.li_opciones_inicio[pos]
        else:
            if must_adjourn:
                self.li_opciones_inicio.insert(1, TB_ADJOURNMENTS)

    def set_version(self, version):
        self.version = version

    def iniciar_gui(self):
        if len(sys.argv) > 1:
            comando = sys.argv[1]
            if comando.lower().endswith(".pgn"):
                self.main_window = None
                self.read_pgn(comando)
                return

        self.entrenamientos = MenuTrainings.MenuTrainings(self)
        if self.configuration.x_translation_mode:
            self.entrenamientos.verify()

        self.main_window = MainWindow.MainWindow(self)
        self.main_window.set_manager_active(self)  # antes que muestra
        self.main_window.muestra()
        self.main_window.check_translated_help_mode()
        self.kibitzers_manager = KibitzersManager.Manager(self)

        self.board = self.main_window.board

        self.cpu = CPU.CPU(self.main_window)

        if self.configuration.x_check_for_update:
            Update.test_update(self)

        if len(sys.argv) > 1:
            comando = sys.argv[1]
            comandoL = comando.lower()
            if comandoL.endswith(".lcsb"):
                self.jugarSoloExtern(comando)
                return
            elif comandoL.endswith(".lcdb"):
                self.externDatabase(comando)
                return
            elif comandoL.endswith(".bmt"):
                self.start()
                self.externBMT(comando)
                return
            elif comando == "-play":
                fich_tmp = sys.argv[2]
                self.juegaExterno(fich_tmp)
                return

            elif comando == "-playagainst":
                recplay = sys.argv[2]
                self.juegaExternoAgainst(recplay)

        else:
            self.start()

    def reset(self):
        self.main_window.deactivate_eboard(0)
        self.main_window.activate_analysis_bar(False)
        self.main_window.activaCapturas(False)
        self.main_window.activaInformacionPGN(False)
        if self.manager:
            self.manager.end_manager()
            self.manager = None
        self.main_window.set_manager_active(self)  # Necesario, no borrar
        self.board.side_indicator_sc.setVisible(False)
        self.board.blindfoldQuitar()
        self.test_opcion_Adjournments()
        self.main_window.pon_toolbar(self.li_opciones_inicio, shortcuts=True)
        self.main_window.active_game(False, False)
        self.main_window.thinking(False)
        self.board.do_pressed_number = None
        self.board.set_position(self.posicionInicial)
        self.board.borraMovibles()
        self.board.remove_arrows()
        self.main_window.adjust_size()
        self.main_window.set_title()
        self.close_engines()

        self.main_window.current_height = self.main_window.height()

    def start(self):
        Code.runSound.close()
        if self.manager:
            self.manager.end_manager()
            del self.manager
            self.manager = None
        self.reset()
        if self.configuration.is_first_time:
            self.cambiaconfigurationPrimeraVez()
            self.configuration.is_first_time = False
            self.main_window.set_title()
        if self.is_first_time:
            self.is_first_time = False
            self.presentacion()
        self.kibitzers_manager.stop()
        self.close_engines()

    def presentacion(self, siEmpezar=True):
        self.siPresentacion = siEmpezar
        if not siEmpezar:
            self.cpu.stop()
            self.board.set_side_bottom(True)
            self.board.activa_menu_visual(True)
            self.board.set_position(self.posicionInicial)
            self.board.setToolTip("")
            self.board.bloqueaRotacion(False)

        else:
            self.board.bloqueaRotacion(True)
            self.board.setToolTip("")
            self.board.activa_menu_visual(True)
            Presentacion.ManagerChallenge101(self)

    def XTutor(self):
        if self.xtutor is None or not self.xtutor.activo:
            self.creaXTutor()
        return self.xtutor

    def creaXTutor(self):
        xtutor = EngineManager.EngineManager(self.configuration.engine_tutor())
        xtutor.function = _("Tutor")
        xtutor.options(self.configuration.x_tutor_mstime, self.configuration.x_tutor_depth, True)
        xtutor.set_priority(self.configuration.x_tutor_priority)
        if self.configuration.x_tutor_multipv == 0:
            xtutor.maximize_multipv()
        else:
            xtutor.set_multipv(self.configuration.x_tutor_multipv)

        self.xtutor = xtutor

    def cambiaXTutor(self):
        if self.xtutor:
            self.xtutor.terminar()
        self.creaXTutor()

    def super_tutor(self):
        if self.xtutor:
            self.xtutor.terminar()
        xtutor = EngineManager.EngineManager(self.configuration.engine_supertutor())
        xtutor.function = _("Tutor")
        xtutor.set_priority(self.configuration.x_tutor_priority)
        xtutor.maximize_multipv()
        xtutor.options(self.configuration.x_tutor_mstime, self.configuration.x_tutor_depth, True)
        self.xtutor = xtutor
        return xtutor

    def XAnalyzer(self):
        if self.xanalyzer is None or not self.xanalyzer.activo:
            self.creaXAnalyzer()
        return self.xanalyzer

    def creaXAnalyzer(self):
        xanalyzer = EngineManager.EngineManager(self.configuration.engine_analyzer())
        xanalyzer.function = _("Analyzer")
        xanalyzer.options(self.configuration.x_analyzer_mstime, self.configuration.x_analyzer_depth, True)
        if self.configuration.x_analyzer_multipv == 0:
            xanalyzer.maximize_multipv()
        else:
            xanalyzer.set_multipv(min(self.configuration.x_analyzer_multipv, xanalyzer.confMotor.maxMultiPV))

        self.xanalyzer = xanalyzer
        Code.xanalyzer = xanalyzer

    def analyzer_clone(self, mstime, depth, multipv):
        xclone = EngineManager.EngineManager(self.configuration.engine_analyzer())
        xclone.options(mstime, depth, True)
        if multipv == 0:
            xclone.maximize_multipv()
        else:
            xclone.set_multipv(multipv)
        return xclone

    def cambiaXAnalyzer(self):
        if self.xanalyzer:
            self.xanalyzer.terminar()
        self.creaXAnalyzer()

    def creaManagerMotor(self, conf_motor, vtime, depth, has_multipv=False, priority=None):
        if conf_motor.type == ENG_WICKER:
            xmanager = EnginesWicker.EngineManagerWicker(conf_motor)
        else:
            xmanager = EngineManager.EngineManager(conf_motor)
        xmanager.options(vtime, depth, has_multipv)
        xmanager.set_priority(priority)
        return xmanager

    @staticmethod
    def close_engines():
        Code.list_engine_managers.close_all()

    def menuplay(self):
        resp = BasicMenus.menuplay(self)
        if resp:
            self.menuPlay_run(resp)

    def menuPlay_run(self, resp):
        tipo, rival = resp
        if tipo == "free":
            config = rival
            self.libre(config)

        elif tipo == "person":
            self.playPerson(rival)

        elif tipo == "animales":
            self.albumAnimales(rival)

        elif tipo == "vehicles":
            self.albumVehicles(rival)

        elif tipo == "human":
            self.human()

    def playPerson(self, rival):
        uno = QTVarios.blancasNegrasTiempo(self.main_window)
        if not uno:
            return
        is_white, siTiempo, minutos, seconds, fastmoves = uno
        if is_white is None:
            return

        dic = {
            "ISWHITE": is_white,
            "RIVAL": rival,
            "SITIEMPO": siTiempo and minutos > 0,
            "MINUTOS": minutos,
            "SEGUNDOS": seconds,
            "FASTMOVES": fastmoves,
        }

        self.manager = ManagerPerson.ManagerPerson(self)
        self.manager.start(dic)

    def reabrirAlbum(self, album):
        tipo, name = album.claveDB.split("_")
        if tipo == "animales":
            self.albumAnimales(name)
        elif tipo == "vehicles":
            self.albumVehicles(name)

    def albumAnimales(self, animal):
        albumes = Albums.AlbumAnimales()
        album = albumes.get_album(animal)
        album.event = _("Album of animals")
        album.test_finished()
        cromo, siRebuild = WindowAlbumes.eligeCromo(self.main_window, self, album)
        if cromo is None:
            if siRebuild:
                albumes.reset(animal)
                self.albumAnimales(animal)
            return

        self.manager = ManagerAlbum.ManagerAlbum(self)
        self.manager.start(album, cromo)

    def albumVehicles(self, character):
        albumes = Albums.AlbumVehicles()
        album = albumes.get_album(character)
        album.event = _("Album of vehicles")
        album.test_finished()
        cromo, siRebuild = WindowAlbumes.eligeCromo(self.main_window, self, album)
        if cromo is None:
            if siRebuild:
                albumes.reset(character)
                self.albumVehicles(character)
            return

        self.manager = ManagerAlbum.ManagerAlbum(self)
        self.manager.start(album, cromo)

    def menu_compete(self):
        resp = BasicMenus.menu_compete(self)
        if resp:
            self.menucompete_run(resp)

    def menucompete_run(self, resp):
        tipo, rival = resp
        if tipo == "competition":
            self.competicion()

        elif tipo == "lucaselo":
            self.lucaselo()

        elif tipo == "micelo":
            self.micelo()

        elif tipo == "wicker":
            self.wicker()

        elif tipo == "fics":
            self.ficselo(rival)

        elif tipo == "fide":
            self.fideelo(rival)

        elif tipo == "lichess":
            self.lichesselo(rival)

        elif tipo == "challenge101":
            Presentacion.ManagerChallenge101(self)

        elif tipo == "strenght101":
            self.strenght101()

        elif tipo == "leagues":
            WLeagues.leagues(self.main_window)

        elif tipo == "swiss":
            WSwisses.swisses(self.main_window)

    def strenght101(self):
        w = WindowSingularM.WSingularM(self.main_window, self.configuration)
        if w.exec_():
            self.manager = ManagerSingularM.ManagerSingularM(self)
            self.manager.start(w.sm)

    def lucaselo(self):
        self.manager = ManagerElo.ManagerElo(self)
        resp = WEngines.select_engine_elo(self.manager, self.configuration.eloActivo())
        if resp:
            self.manager.start(resp)

    def micelo(self):
        self.manager = ManagerMicElo.ManagerMicElo(self)
        resp = WEngines.select_engine_micelo(self.manager, self.configuration.miceloActivo())
        if resp:
            key = "MICELO_TIME"
            dic = self.configuration.read_variables(key)
            default_minutes = dic.get("MINUTES", 10)
            default_seconds = dic.get("SECONDS", 0)
            respT = QTVarios.vtime(
                self.main_window,
                minMinutos=0,
                minSegundos=0,
                maxMinutos=999,
                max_seconds=999,
                default_minutes=default_minutes,
                default_seconds=default_seconds,
            )
            if respT:
                minutos, seconds = respT
                dic = {"MINUTES": minutos, "SECONDS": seconds}
                self.configuration.write_variables(key, dic)
                self.manager.start(resp, minutos, seconds)

    def wicker(self):
        self.manager = ManagerWicker.ManagerWicker(self)
        resp = WEngines.select_engine_wicker(self.manager, self.configuration.wicker_elo())
        if resp:
            key = "WICKER_TIME"
            dic = self.configuration.read_variables(key)
            default_minutes = dic.get("MINUTES", 10)
            default_seconds = dic.get("SECONDS", 0)
            respT = QTVarios.vtime(
                self.main_window,
                minMinutos=0,
                minSegundos=0,
                maxMinutos=999,
                max_seconds=999,
                default_minutes=default_minutes,
                default_seconds=default_seconds,
            )
            if respT:
                minutos, seconds = respT
                dic = {"MINUTES": minutos, "SECONDS": seconds}
                self.configuration.write_variables(key, dic)
                self.manager.start(resp, minutos, seconds)

    def ficselo(self, nivel):
        self.manager = ManagerFideFics.ManagerFideFics(self)
        self.manager.selecciona(GT_FICS)
        xid = self.manager.elige_juego(nivel)
        self.manager.start(xid)

    def fideelo(self, nivel):
        self.manager = ManagerFideFics.ManagerFideFics(self)
        self.manager.selecciona(GT_FIDE)
        xid = self.manager.elige_juego(nivel)
        self.manager.start(xid)

    def lichesselo(self, nivel):
        self.manager = ManagerFideFics.ManagerFideFics(self)
        self.manager.selecciona(GT_LICHESS)
        xid = self.manager.elige_juego(nivel)
        self.manager.start(xid)

    def run_action(self, key):
        self.close_engines()
        self.main_window.deactivate_eboard(0)

        if self.siPresentacion:
            self.presentacion(False)

        if key == TB_QUIT:
            if hasattr(self, "cpu"):
                self.cpu.stop()
            self.main_window.final_processes()
            self.main_window.accept()

        elif key == TB_PLAY:
            self.check_engines()
            self.menuplay()

        elif key == TB_COMPETE:
            self.check_engines()
            self.menu_compete()

        elif key == TB_TRAIN:
            self.check_engines()
            self.entrenamientos.lanza()

        elif key == TB_OPTIONS:
            self.check_engines()
            self.options()

        elif key == TB_TOOLS:
            self.check_engines()
            self.menu_tools()

        elif key == TB_INFORMATION:
            self.informacion()

        elif key == TB_ADJOURNMENTS:
            self.adjournments()

        elif key == TB_REPLAY:
            self.manager.replay_direct()

    def adjournments(self):
        menu = QTVarios.LCMenu(self.main_window)
        li_adjournments = Adjournments.Adjournments().list_menu()
        for key, label, tp in li_adjournments:
            menu.opcion((True, key, tp), label, Iconos.PuntoMagenta())
            menu.addSeparator()
        menu.addSeparator()
        mr = menu.submenu(_("Remove"), Iconos.Borrar())
        for key, label, tp in li_adjournments:
            mr.opcion((False, key, tp), label, Iconos.Delete())

        resp = menu.lanza()
        if resp:
            si_run, key, tp = resp
            if si_run:
                dic = Adjournments.Adjournments().get(key)

                Adjournments.Adjournments().remove(key)
                if tp == GT_AGAINST_ENGINE:
                    self.manager = ManagerPlayAgainstEngine.ManagerPlayAgainstEngine(self)
                elif tp == GT_ALBUM:
                    self.manager = ManagerAlbum.ManagerAlbum(self)
                elif tp == GT_AGAINST_CHILD_ENGINE:
                    self.manager = ManagerPerson.ManagerPerson(self)
                elif tp == GT_MICELO:
                    self.manager = ManagerMicElo.ManagerMicElo(self)
                elif tp == GT_WICKER:
                    self.manager = ManagerWicker.ManagerWicker(self)
                elif tp == GT_COMPETITION_WITH_TUTOR:
                    self.manager = ManagerCompeticion.ManagerCompeticion(self)
                elif tp == GT_ELO:
                    self.manager = ManagerElo.ManagerElo(self)
                elif tp == GT_AGAINST_GM:
                    self.manager = ManagerGM.ManagerGM(self)
                elif tp in (GT_FIDE, GT_FICS, GT_LICHESS):
                    self.manager = ManagerFideFics.ManagerFideFics(self)
                    self.manager.selecciona(tp)
                elif tp == GT_AGAINST_ENGINE_LEAGUE:
                    self.manager = ManagerLeague.ManagerLeague(self)
                elif tp == GT_HUMAN:
                    self.manager = ManagerPlayHuman.ManagerPlayHuman(self)
                else:
                    return
                self.manager.run_adjourn(dic)
                return

            else:
                Adjournments.Adjournments().remove(key)

            self.test_opcion_Adjournments()
            self.main_window.pon_toolbar(self.li_opciones_inicio, shortcuts=True)

    def launch_shortcuts(self):
        BasicMenus.shortcuts(self)

    def launch_shortcut_with_alt(self, key):
        BasicMenus.atajos_alt(self, key)

    def atajos_edit(self):
        BasicMenus.atajos_edit(self)

    def options(self):
        menu = QTVarios.LCMenu(self.main_window)

        menu.opcion(self.cambiaconfiguration, _("General configuration"), Iconos.Opciones())
        menu.separador()

        txt = _("Language")
        if txt != "Language":
            txt += " (Language)"
        menu.opcion(self.select_language, txt, Iconos.Language())
        menu.separador()

        menu.opcion(self.engines, _("Engines configuration"), Iconos.ConfEngines())
        menu.separador()

        # Logs of engines
        is_engines_log_active = Code.list_engine_managers.is_logs_active()
        label = _("Save engines log")
        if is_engines_log_active:
            icono = Iconos.LogActive()
            label += " ...%s" % _("Working...")
            key = self.log_close
        else:
            icono = Iconos.LogInactive()
            key = self.log_open
        menu.opcion(key, label, icono)
        menu.separador()

        menu1 = menu.submenu(_("Colors"), Iconos.Colores())
        menu1.opcion(self.edit_board_colors, _("Main board"), Iconos.EditarColores())
        menu1.separador()
        menu1.opcion(self.cambiaColores, _("General"), Iconos.Vista())
        menu.separador()

        menu.opcion(self.sonidos, _("Custom sounds"), Iconos.SoundTool())
        menu.separador()
        menu.opcion(self.atajos_edit, _("Shortcuts"), Iconos.Atajos())
        menu.separador()

        menu.opcion(self.remove_results, _("Remove results"), Iconos.Delete())
        menu.separador()

        menu.opcion(self.set_password, _("Set password"), Iconos.Password())
        menu.separador()

        if self.configuration.is_main:
            menu.opcion(self.usuarios, _("Users"), Iconos.Usuarios())
            menu.separador()

            menu1 = menu.submenu(_("User data folder"), Iconos.Carpeta())
            menu1.opcion(self.folder_change, _("Change the folder"), Iconos.FolderChange())
            if not Configuration.is_default_folder():
                menu1.separador()
                menu1.opcion(self.folder_default, _("Reset to default"), Iconos.Defecto())

        resp = menu.lanza()
        if resp:
            if isinstance(resp, tuple):
                resp[0](resp[1])
            else:
                resp()

    def remove_results(self):
        rem = RemoveResults.RemoveResults(self.main_window)
        rem.menu()

    def select_language(self):
        if LucasChessGui.select_language(self.main_window, False):
            self.reiniciar()

    def log_open(self):
        Code.list_engine_managers.active_logs(True)

    def log_close(self):
        Code.list_engine_managers.active_logs(False)

    def cambiaconfiguration(self):
        if WindowConfig.options(self.main_window, self.configuration):
            self.configuration.graba()
            self.reiniciar()

    def edit_board_colors(self):
        w = WBoardColors.WBoardColors(self.board)
        w.exec_()

    def cambiaColores(self):
        w = WColors.WColors(self)
        if w.exec_():
            self.reiniciar()

    def sonidos(self):
        w = WindowSonido.WSonidos(self)
        w.exec_()

    def folder_change(self):
        carpeta = SelectFiles.get_existing_directory(
            self.main_window,
            self.configuration.carpeta,
            _("Change the folder where all data is saved") + ". " + _("Be careful please"),
        )
        if carpeta and os.path.isdir(carpeta):
            self.configuration.changeActiveFolder(carpeta)
            self.reiniciar()

    def folder_default(self):
        self.configuration.changeActiveFolder(None)
        self.reiniciar()

    def reiniciar(self):
        self.main_window.final_processes()
        self.main_window.accept()
        QTUtil.exit_application(OUT_REINIT)

    def cambiaconfigurationPrimeraVez(self):
        if WindowConfig.options_first_time(self.main_window, self.configuration):
            self.configuration.graba()

    def motoresExternos(self):
        w = WConfEngines.WConfEngines(self.main_window)
        w.exec_()
        self.cambiaXTutor()
        self.cambiaXAnalyzer()

    def engines(self):
        w = WConfEngines.WConfEngines(self.main_window)
        w.exec_()
        self.cambiaXAnalyzer()
        self.cambiaXTutor()

    def aperturaspers(self):
        w = WindowOpenings.OpeningsPersonales(self)
        w.exec_()

    def usuarios(self):
        WindowUsuarios.edit_users(self)

    def set_password(self):
        WindowUsuarios.set_password(self)

    def trainingMap(self, mapa):
        resp = WindowWorkMap.train_map(self, mapa)
        if resp:
            self.manager = ManagerMateMap.ManagerMateMap(self)
            self.manager.start(resp)

    def train_book(self):
        w = WBooksTrain.WBooksTrain(self)
        if w.exec_() and w.book_player:
            self.type_play = GT_BOOK
            self.estado = ST_PLAYING
            self.manager = ManagerTrainBooks.ManagerTrainBooks(self)
            self.manager.start(w.book_player, w.player_highest, w.book_rival, w.rival_resp, w.is_white, w.show_menu)

    def train_book_ol(self):
        dbli_books_train = UtilSQL.ListObjSQL(Code.configuration.file_train_books_ol(), WBooksTrainOL.BooksTrainOL,
                                              tabla="data", reverted=True)
        # No es posible con with porque self.manager termina y deja el control en main_window
        w = WBooksTrainOL.WBooksTrainOL(self.main_window, dbli_books_train)
        if w.exec_():
            if w.train_rowid is None:
                dbli_books_train.close()
                return
            self.manager = ManagerTrainBooksOL.ManagerTrainBooksOL(self)
            self.manager.start(dbli_books_train, w.train_rowid)
        else:
            dbli_books_train.close()

    def menu_tools(self):
        resp = BasicMenus.menu_tools(self)
        if resp:
            self.menuTools_run(resp)

    def menuTools_run(self, resp):
        if resp == "pgn":
            self.visorPGN()

        elif resp == "miniatura":
            self.miniatura()

        elif resp == "polyglot":
            self.polyglot_factory()

        elif resp == "polyglot_install":
            self.polyglot_install()

        elif resp == "pgn_paste":
            self.pgn_paste()

        elif resp == "juega_solo":
            self.jugarSolo()

        elif resp == "torneos":
            self.torneos()
        elif resp == "sts":
            self.sts()
        elif resp == "kibitzers":
            self.kibitzers_manager.edit()
        elif resp == "conf_engines":
            self.engines()

        elif resp == "manual_save":
            self.manual_save()

        elif resp.startswith("dbase_"):
            comando = resp[6:]
            accion = comando[0]  # R = read database,  N = create new, D = delete
            valor = comando[2:]
            self.database(accion, valor)

        elif resp == "aperturaspers":
            self.aperturaspers()
        elif resp == "openings":
            self.openings()

    def openings(self):
        dicline = WindowOpeningLines.openingLines(self)
        if dicline:
            if "TRAIN" in dicline:
                resp = "tr_%s" % dicline["TRAIN"]
            else:
                resp = WindowOpeningLine.study(dicline["file"])
            if resp is None:
                self.openings()
            else:
                pathFichero = Util.opj(self.configuration.folder_openings(), dicline["file"])
                if resp == "tr_sequential":
                    self.openings_training_sequential(pathFichero)
                elif resp == "tr_static":
                    self.openings_training_static(pathFichero)
                elif resp == "tr_positions":
                    self.openings_training_positions(pathFichero)
                elif resp == "tr_engines":
                    self.openings_training_engines(pathFichero)

    def openings_training_sequential(self, pathFichero):
        self.manager = ManagerOPLSequential.ManagerOpeningLinesSequential(self)
        self.manager.start(pathFichero)

    def openings_training_engines(self, pathFichero):
        self.manager = ManagerOPLEngines.ManagerOpeningEngines(self)
        self.manager.start(pathFichero)

    def openings_training_static(self, pathFichero):
        dbop = OpeningLines.Opening(pathFichero)
        num_linea = WindowOpeningLines.select_static_line(self, dbop)
        dbop.close()
        if num_linea is not None:
            self.manager = ManagerOPLStatic.ManagerOpeningLinesStatic(self)
            self.manager.start(pathFichero, "static", num_linea)
        else:
            self.openings()

    def openings_training_positions(self, pathFichero):
        self.manager = ManagerOPLPositions.ManagerOpeningLinesPositions(self)
        self.manager.start(pathFichero)

    def externBMT(self, file):
        self.configuration.ficheroBMT = file
        WindowBMT.windowBMT(self)

    def anotar(self, game, siblancasabajo):
        self.manager = ManagerWritingDown.ManagerWritingDown(self)
        self.manager.start(game, siblancasabajo)

    def show_anotar(self):
        w = WritingDown.WritingDown(self)
        if w.exec_():
            pc, siblancasabajo = w.resultado
            if pc is None:
                pc = DBgames.get_random_game()
            self.anotar(pc, siblancasabajo)

    def externDatabase(self, file):
        # self.configuration.ficheroDBgames = file
        self.database("R", file)
        self.run_action(TB_QUIT)

    def database(self, accion, dbpath, is_temporary=False):
        if accion == "M":
            Code.startfile(self.configuration.folder_databases())
            return

        path_pgn = None
        if accion == "N":
            dbpath, path_pgn = WDB_Games.new_database(self.main_window, self.configuration, with_import_pgn=True)
            if dbpath is None:
                return
            accion = "R"

        if accion == "D":
            resp = QTVarios.select_db(self.main_window, self.configuration, True, False)
            if resp:
                if QTUtil2.pregunta(self.main_window, "%s\n%s" % (_("Do you want to remove?"), resp)):
                    Util.remove_file(resp)
                    Util.remove_file(resp + ".st1")
                    Util.remove_file(resp[:-5] + ".lcmv")
            return

        if accion == "R":
            self.configuration.set_last_database(Util.relative_path(dbpath))
            w = WindowDatabase.WBDatabase(self.main_window, self, dbpath, is_temporary, False)
            if self.main_window:
                with QTUtil.EscondeWindow(self.main_window):
                    if path_pgn:
                        w.show()
                        w.wgames.tw_importar_pgn(path_pgn)
                    if w.exec_():
                        if w.reiniciar:
                            self.database("R", self.configuration.get_last_database())
            else:
                Delegados.genera_pm(w.infoMove.board.piezas)
                w.show()

    def manual_save(self):
        WindowManualSave.manual_save(self)

    def torneos(self):
        WTournaments.tournaments(self.main_window)

    def sts(self):
        WindowSTS.sts(self, self.main_window)

    def libre(self, conf):
        dic = None
        if conf:
            with UtilSQL.DictSQL(self.configuration.ficheroEntMaquinaConf) as dbc:
                dic = dbc[conf]
        if dic is None:
            dic = WPlayAgainstEngine.play_against_engine(self, _("Play against an engine"))
        if dic:
            self.entrenaMaquina(dic)

    def human(self):
        w = WPlayHuman.WPlayHuman()
        if not w.exec_():
            return

        self.manager = ManagerPlayHuman.ManagerPlayHuman(self)
        self.manager.start(w.dic)

    def entrenaMaquina(self, dic):
        self.manager = ManagerPlayAgainstEngine.ManagerPlayAgainstEngine(self)
        side = dic["SIDE"]
        if side == "R":
            side = "B" if random.randint(1, 2) == 1 else "N"
        dic["ISWHITE"] = side == "B"
        self.manager.start(dic)

    def read_pgn(self, fichero_pgn):
        fichero_pgn = os.path.abspath(fichero_pgn)
        cfecha_pgn = str(os.path.getmtime(fichero_pgn))
        path_temp_pgns = self.configuration.folder_databases_pgn()

        li = list(os.scandir(path_temp_pgns))
        li_ant = []
        for entry in li:
            if entry.name.endswith(".lcdb"):
                li_ant.append(entry)
            else:
                Util.remove_file(entry.path)
        if len(li_ant) > 10:
            li_ant.sort(key=lambda x: x.stat()[stat.ST_ATIME], reverse=True)
            for x in li_ant[10:]:
                Util.remove_file(x.path)

        file_db = Util.opj(path_temp_pgns, os.path.basename(fichero_pgn)[:-3] + "lcdb")

        if Util.exist_file(file_db):
            create = False
            db = DBgames.DBgames(file_db)
            cfecha_pgn_ant = db.read_config("PGN_DATE")
            fichero_pgn_ant = db.read_config("PGN_FILE")
            db.close()
            if cfecha_pgn != cfecha_pgn_ant or fichero_pgn_ant != fichero_pgn:
                create = True
                Util.remove_file(file_db)
        else:
            create = True

        if create:
            db = DBgames.DBgames(file_db)
            dl_tmp = QTVarios.ImportarFicheroPGN(self.main_window)
            dl_tmp.show()
            db.import_pgns([fichero_pgn], dl_tmp=dl_tmp)
            db.save_config("PGN_DATE", cfecha_pgn)
            db.save_config("PGN_FILE", fichero_pgn)
            db.close()
            dl_tmp.close()

        self.database("R", file_db, is_temporary=True)

    def visorPGN(self):
        path = SelectFiles.select_pgn(self.main_window)
        if path:
            self.read_pgn(path)

    def select_1_pgn(self, wparent=None):
        wparent = self.main_window if wparent is None else wparent
        path = SelectFiles.select_pgn(wparent)
        if path:
            fichero_pgn = os.path.abspath(path)
            cfecha_pgn = str(os.path.getmtime(fichero_pgn))
            cdir = self.configuration.folder_databases_pgn()

            file_db = Util.opj(cdir, os.path.basename(fichero_pgn)[:-4] + ".lcdb")

            if Util.exist_file(file_db):
                create = False
                db = DBgames.DBgames(file_db)
                cfecha_pgn_ant = db.read_config("PGN_DATE")
                fichero_pgn_ant = db.read_config("PGN_FILE")
                db.close()
                if cfecha_pgn != cfecha_pgn_ant or fichero_pgn_ant != fichero_pgn:
                    create = True
                    Util.remove_file(file_db)
            else:
                create = True

            if create:
                db = DBgames.DBgames(file_db)
                dl_tmp = QTVarios.ImportarFicheroPGN(wparent)
                dl_tmp.show()
                db.import_pgns([fichero_pgn], dl_tmp=dl_tmp)
                db.save_config("PGN_DATE", cfecha_pgn)
                db.save_config("PGN_FILE", fichero_pgn)
                db.close()
                dl_tmp.close()

            db = DBgames.DBgames(file_db)
            if db.all_reccount() == 1:
                game = db.read_game_recno(0)
                db.close()
                return game
            db.close()

            w = WindowDatabase.WBDatabase(self.main_window, self, file_db, True, True)
            if w.exec_():
                return w.game

        return None

    def pgn_paste(self):
        path = self.configuration.ficheroTemporal("pgn")
        texto = QTUtil.get_txt_clipboard()
        if texto:
            texto = texto.strip()
            if not texto.startswith("["):
                texto = '[Event "%s"]\n\n %s' % (_("Paste PGN"), texto)
            with open(path, "wt", encoding="utf-8", errors="ignore") as q:
                q.write(texto)
            self.read_pgn(path)

    def miniatura(self):
        file_miniatures = Code.path_resource("IntFiles", "Miniatures.lcdb")
        db = DBgames.DBgames(file_miniatures)
        db.all_reccount()
        num_game = random.randint(0, db.reccount() - 1)
        game = db.read_game_recno(num_game)
        db.close()
        dic = {"GAME": game.save()}
        manager = ManagerSolo.ManagerSolo(self)
        self.manager = manager
        manager.start(dic)

    def polyglot_factory(self):
        resp = WFactory.polyglots_factory(self)
        if resp:
            w = WPolyglot.WPolyglot(self.main_window, self.configuration, resp)
            w.exec_()
            self.polyglot_factory()

    def polyglot_install(self):
        WBooks.registered_books(self.main_window)

    def juegaExterno(self, fich_tmp):
        dic_sended = Util.restore_pickle(fich_tmp)
        dic = WPlayAgainstEngine.play_position(self, _("Play a position"), dic_sended["ISWHITE"])
        if dic is None:
            self.run_action(TB_QUIT)
        else:
            side = dic["SIDE"]
            if side == "R":
                side = "B" if random.randint(1, 2) == 1 else "N"
            dic["ISWHITE"] = side == "B"
            self.manager = ManagerPlayAgainstEngine.ManagerPlayAgainstEngine(self)
            self.manager.play_position(dic, dic_sended["GAME"])

    def jugarSolo(self):
        self.manager = ManagerSolo.ManagerSolo(self)
        self.manager.start()

    def jugarSoloExtern(self, file_lcsb):
        self.manager = ManagerSolo.ManagerSolo(self)
        self.manager.leeFichero(file_lcsb)

    def juegaExternoAgainst(self, recplay):
        recplay = int(recplay)
        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        w = WindowPlayGame.WPlay1(self.main_window, self.configuration, db, recplay)
        if w.exec_():
            db.close()
            if w.recno is not None:
                is_white = w.is_white
                is_black = w.is_black
                if is_white or is_black:
                    self.manager = ManagerPlayGame.ManagerPlayGame(self)
                    self.manager.start(w.recno, is_white, is_black, close_on_exit=True)
        else:
            db.close()
        return

    def train_position(self, position, n_posiciones, titentreno, li_entrenamientos, entreno, with_tutor, jump,
                       remove_solutions, show_comments, advanced):
        self.manager = ManagerEntPos.ManagerEntPos(self)
        self.manager.set_training(entreno)
        self.manager.start(position, n_posiciones, titentreno, li_entrenamientos, with_tutor, jump,
                           remove_solutions, show_comments, advanced)

    def playRoute(self, route):
        if route.state == Routes.BETWEEN:
            self.manager = ManagerRoutes.ManagerRoutesTactics(self)
            self.manager.start(route)
        elif route.state == Routes.ENDING:
            self.manager = ManagerRoutes.ManagerRoutesEndings(self)
            self.manager.start(route)
        elif route.state == Routes.PLAYING:
            self.manager = ManagerRoutes.ManagerRoutesPlay(self)
            self.manager.start(route)

    def show_route(self):
        WindowRoutes.train_train(self)

    def playEverest(self, recno):
        self.manager = ManagerEverest.ManagerEverest(self)
        self.manager.start(recno)

    def showEverest(self, recno):
        if WindowEverest.show_expedition(self.main_window, self.configuration, recno):
            self.playEverest(recno)

    def play_game(self):
        w = WindowPlayGame.WPlayGameBase(self)
        if w.exec_():
            recno = w.recno
            if recno is not None:
                is_white = w.is_white
                is_black = w.is_black
                if is_white or is_black:
                    self.manager = ManagerPlayGame.ManagerPlayGame(self)
                    self.manager.start(recno, is_white, is_black)

    def play_game_show(self, recno):
        db = WindowPlayGame.DBPlayGame(self.configuration.file_play_game())
        w = WindowPlayGame.WPlay1(self.main_window, self.configuration, db, recno)
        if w.exec_():
            db.close()
            if w.recno is not None:
                is_white = w.is_white
                is_black = w.is_black
                if is_white or is_black:
                    self.manager = ManagerPlayGame.ManagerPlayGame(self)
                    self.manager.start(w.recno, is_white, is_black)
        else:
            db.close()

    def learn_game(self, game=None):
        if game:
            with WindowLearnGame.DBLearnGame() as db:
                db.append_game(game)

        w = WindowLearnGame.WLearnBase(self.main_window)
        w.exec_()

    def showTurnOnLigths(self, name):
        self.entrenamientos.turn_on_lights(name)

    def playWashing(self):
        ManagerWashing.manager_washing(self)

    def showWashing(self):
        if WindowWashing.windowWashing(self):
            self.playWashing()

    # def forest_creator(self, level):
    #     pass

    def informacion(self):
        resp = BasicMenus.menu_information(self)
        if resp:
            self.informacion_run(resp)

    def informacion_run(self, resp):
        if resp == "acercade":
            self.acercade()
        elif resp == "docs":
            webbrowser.open("%s/docs" % self.web)
        elif resp == "blog":
            webbrowser.open(self.blog)
        elif resp.startswith("http"):
            webbrowser.open(resp)
        elif resp == "web":
            webbrowser.open("%s/index?lang=%s" % (self.web, self.configuration.translator()))
        elif resp == "wiki":
            webbrowser.open(self.wiki)
        elif resp == "mail":
            webbrowser.open("mailto:lukasmonk@gmail.com")

        elif resp == "actualiza":
            self.actualiza()

        elif resp == "actualiza_manual":
            self.actualiza_manual()

    def adTitulo(self):
        return "<b>" + Code.lucas_chess + "</b><br>" + _X(_("version %1"), self.version)

    def adPie(self):
        return (
                "<hr><br><b>%s</b>" % _("Author")
                + ': <a href="mailto:lukasmonk@gmail.com">Lucas Monge</a> -'
                + ' <a href="%s">%s</a></a>' % (self.web, self.web)
                + '(%s <a href="http://www.gnu.org/copyleft/gpl.html"> GPL</a>).<br>' % _("License")
        )

    def acercade(self):
        w = About.WAbout()
        w.exec_()

    def actualiza(self):
        if Update.update(self.main_window):
            self.reiniciar()

    def actualiza_manual(self):
        if Update.update_manual(self.main_window):
            self.reiniciar()

    def one_moment_please(self, mensaje=None):
        return QTUtil2.waiting_message.start(
            self.main_window, mensaje if mensaje else _("One moment please..."), physical_pos=TOP_RIGHT
        )

    def num_rows(self):
        return 0

    def competicion(self):
        options = WCompetitionWithTutor.datos(self.main_window, self.configuration, self)
        if options:
            # self.game_type = GT_COMPETITION_WITH_TUTOR
            categorias, categoria, nivel, is_white, puntos = options

            self.manager = ManagerCompeticion.ManagerCompeticion(self)
            self.manager.start(categorias, categoria, nivel, is_white, puntos)

    def final_x(self):
        return True

    def final_x0(self):
        return True

    def clonVariations(self, window, xtutor=None, is_competitive=False):
        return ProcesadorVariations(
            window, xtutor, is_competitive=is_competitive, kibitzers_manager=self.kibitzers_manager
        )

    def manager_game(
            self, window, game, is_complete, only_consult, father_board, with_previous_next=None, save_routine=None
    ):
        clon_procesador = ProcesadorVariations(
            window, self.xtutor, is_competitive=False, kibitzers_manager=self.kibitzers_manager
        )
        clon_procesador.manager = ManagerGame.ManagerGame(clon_procesador)
        clon_procesador.manager.start(game, is_complete, only_consult, with_previous_next, save_routine)

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

    def select_one_fns(self, owner=None):
        if owner is None:
            owner = self.main_window
        return MenuTrainings.select_one_fns(owner, self)

    def gaviota_endings(self):
        WEndingsGTB.train_gtb(self)

    def play_league_human(self, league, xmatch, division):
        self.manager = ManagerLeague.ManagerLeague(self)
        adj = Adjournments.Adjournments()
        key_dic = adj.key_match_league(xmatch)
        if key_dic:
            key, dic_adjourn = key_dic
            adj.remove(key)
            self.manager.run_adjourn(dic_adjourn)
        else:
            self.manager.start(league, xmatch, division)

    def play_swiss_human(self, league, xmatch):
        self.manager = ManagerSwiss.ManagerSwiss(self)
        adj = Adjournments.Adjournments()
        key_dic = adj.key_match_swiss(xmatch)
        if key_dic:
            key, dic_adjourn = key_dic
            adj.remove(key)
            self.manager.run_adjourn(dic_adjourn)
        else:
            self.manager.start(league, xmatch)

    def check_engines(self):
        return CheckEngines.check_engines(self.main_window)


class ProcesadorVariations(Procesador):
    def __init__(self, window, xtutor, is_competitive=False, kibitzers_manager=None):
        self.kibitzers_manager = kibitzers_manager
        self.is_competitive = is_competitive

        self.configuration = Code.configuration

        self.li_opciones_inicio = [
            TB_QUIT,
            TB_PLAY,
            TB_TRAIN,
            TB_COMPETE,
            TB_TOOLS,
            TB_OPTIONS,
            TB_INFORMATION,
        ]  # Lo incluimos aqui porque sino no lo lee, en caso de aplazada

        self.siPresentacion = False

        self.main_window = MainWindow.MainWindow(self, window, extparam="mainv")
        self.main_window.set_manager_active(self)
        self.main_window.xrestore_video()

        self.board = self.main_window.board

        self.xtutor = xtutor
        self.xrival = None
        self.xanalyzer = None

        self.replayBeep = None

        self.posicionInicial = None

        self.entrenamientos = Code.procesador.entrenamientos

        self.cpu = CPU.CPU(self.main_window)
