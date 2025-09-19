import copy
import os
import sys
import time
from queue import Queue
from typing import Optional, Any

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util
from Code.Analysis import AnalysisIndexes
from Code.Analysis import RunAnalysisControl
from Code.Base import Game
from Code.Base.Constantes import (
    INACCURACY, MISTAKE, BLUNDER,
    INACCURACY_MISTAKE, INACCURACY_MISTAKE_BLUNDER, MISTAKE_BLUNDER,
    RUNA_GAME, RUNA_HALT, RUNA_CONFIGURATION, RUNA_TERMINATE
)
from Code.BestMoveTraining import BMT
from Code.Config import Configuration
from Code.Engines import EngineManager
from Code.MainWindow import InitApp
from Code.Nags.Nags import NAG_3
from Code.Openings import OpeningsStd
from Code.QT import LCDialog, Controles, Colocacion, Iconos, QTUtil
from Code.SQL import UtilSQL
from Code.Themes import AssignThemes


class CPU:
    """Clase principal que maneja el análisis en segundo plano"""

    def __init__(self, filebase: str):
        # Configuración de IPC
        self.ipc_send = UtilSQL.IPC(filebase + "_receive.sqlite", False)
        self.ipc_receive = UtilSQL.IPC(filebase + "_send.sqlite", False)

        # Estado del análisis
        self.configuration: Optional[Configuration.Configuration] = None
        self.window: Optional[WAnalysis] = None
        self.engine: Optional[EngineManager.EngineManager] = None
        self.queue_orders = Queue()
        self.timer: Optional[QtCore.QTimer] = None

        # Flags de estado
        self.is_closed = False
        self.is_analyzing = False

        # Datos de análisis
        self.alm: Optional[Any] = None
        self.ag: Optional[AnalyzeGame] = None
        self.num_worker: Optional[int] = None

    def xreceive(self) -> None:
        """Recibe órdenes del proceso principal"""
        if self.is_closed:
            return

        if self.window:
            QTUtil.refresh_gui()

        dv = self.ipc_receive.pop()
        if not dv:
            return

        orden = RunAnalysisControl.Orden()
        orden.key = dv["__CLAVE__"]
        orden.dv = dv

        if orden.key == RUNA_HALT:
            self.close()

        self.queue_orders.put(orden)
        self.xreceive()

    def send(self, orden: RunAnalysisControl.Orden) -> None:
        """Envía resultados al proceso principal"""
        self.ipc_send.push(orden)

    def procesa(self) -> None:
        """Procesa las órdenes recibidas"""
        if self.is_closed or self.queue_orders.empty():
            return

        orden = self.queue_orders.get()
        key = orden.key

        if key == RUNA_CONFIGURATION:
            self._process_configuration(orden)
        elif key == RUNA_GAME:
            self._process_game(orden)
        elif key == RUNA_TERMINATE:
            self.close()

    def _process_configuration(self, orden: RunAnalysisControl.Orden) -> None:
        """Procesa la configuración inicial"""
        user = orden.dv["USER"]
        self.configuration = Configuration.Configuration(user)
        self.configuration.lee()
        Code.list_engine_managers = EngineManager.ListEngineManagers()
        self.configuration.relee_engines()
        Code.configuration = self.configuration
        Code.procesador = self
        OpeningsStd.ap.reset()

        self.alm = orden.dv["ALM"]
        self.num_worker = orden.dv["NUM_WORKER"]

        self.xreceive()
        self.lanzawindow()

    def _process_game(self, orden: RunAnalysisControl.Orden) -> None:
        """Procesa un juego para análisis"""
        game = orden.dv["GAME"]
        recno = orden.dv["RECNO"]
        self.analyze(game, recno)

    def lanzawindow(self) -> int:
        """Inicia la ventana de análisis"""
        app = QtWidgets.QApplication([])
        InitApp.init_app_style(app, self.configuration)
        self.configuration.load_translation()

        self.window = WAnalysis(self)
        self.ag = AnalyzeGame(self, self.alm)
        self.ag.cached_begin()

        self.window.show()
        self.procesa()

        return app.exec_()

    def close(self) -> None:
        """Cierra el proceso de análisis"""
        if not self.is_closed:
            self.is_closed = True
            if self.window:
                self.window.finalizar()
            QTUtil.refresh_gui()

            if self.ag:
                self.ag.cached_end()

            orden = RunAnalysisControl.Orden()
            orden.key = RUNA_TERMINATE
            self.send(orden)

            self.ipc_send.close()
            self.ipc_receive.close()

            if hasattr(Code, 'list_engine_managers'):
                Code.list_engine_managers.close_all()

            sys.exit()

    def analyzer_clone(self, mstime: int, depth: int, multipv: int) -> EngineManager.EngineManager:
        """Crea un clon del motor de análisis"""
        xclone = EngineManager.EngineManager(self.configuration.engine_analyzer())
        xclone.options(mstime, depth, True)
        if multipv == 0:
            xclone.maximize_multipv()
        else:
            xclone.set_multipv(multipv)
        return xclone

    def analyzer_engine(self, conf_motor: Any, vtime: int, depth: int) -> EngineManager.EngineManager:
        """Configura un motor de análisis específico"""
        xmanager = EngineManager.EngineManager(conf_motor)
        xmanager.options(vtime, depth, True)
        xmanager.set_priority(self.alm.priority)
        return xmanager

    def analyze(self, game: Game.Game, recno: int) -> None:
        """Inicia el análisis de un juego"""
        if self.is_closed:
            return

        self.window.init_game(recno, len(game))
        self.is_analyzing = True
        self.ag.xprocesa(game)
        self.is_analyzing = False

        orden = RunAnalysisControl.Orden()
        orden.key = RUNA_GAME
        orden.set("GAME", game)
        orden.set("RECNO", recno)

        li_save_extra = self.ag.xsave_extra_get()
        if li_save_extra:
            orden.set("EXTRA", li_save_extra)

        self.send(orden)
        self.procesa()

    def progress(self, npos: int, n_moves: int) -> bool:
        """Actualiza la barra de progreso"""
        self.window.progress(npos, n_moves)
        QTUtil.refresh_gui()
        return not self.is_closed


def run(filebase: str) -> None:
    """Función principal para iniciar el análisis"""
    if not Code.DEBUG:
        sys.stderr = Util.Log("./bug.analysis")

    cpu = CPU(filebase)
    cpu.xreceive()
    cpu.procesa()


class WAnalysis(LCDialog.LCDialog):
    """Ventana de progreso del análisis"""

    def __init__(self, cpu: CPU):
        self.cpu: CPU = cpu
        self.game: Optional[Game.Game] = None

        self.is_paused: bool = False

        title = f"{_('Mass analysis')} - {_('Worker')} {cpu.num_worker + 1}"
        LCDialog.LCDialog.__init__(self, None, title, Iconos.Analizar(), f"worker_analyisis_{self.cpu.num_worker}")
        flags = self.windowFlags()
        flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # UI Elements
        self.lb_game = Controles.LB(self)
        self.pb_moves = QtWidgets.QProgressBar()
        self.pb_moves.setFormat(_("Move") + " %v/%m")

        self.bt_pause = Controles.PB(self, "", self.pause_continue, plano=True)
        self.icon_pause_continue()

        # Layout
        layout = Colocacion.H().control(self.lb_game).control(self.pb_moves).control(self.bt_pause)
        self.setLayout(layout)
        self.restore_video(default_width=400, default_height=40)

        # Timer setup
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.xreceive)
        self.timer.start(200)
        self.is_closed = False

    def xreceive(self) -> None:
        """Maneja las actualizaciones periódicas"""
        self.cpu.xreceive()
        if not self.cpu.is_analyzing:
            self.cpu.procesa()

    def init_game(self, num_game: int, num_moves: int) -> None:
        """Inicializa la visualización para un nuevo juego"""
        self.lb_game.set_text(f"{_('Game')} {num_game + 1}")
        QTUtil.refresh_gui()

    def closeEvent(self, event) -> None:
        """Maneja el cierre de la ventana"""
        self.finalizar()

    def finalizar(self) -> None:
        """Finaliza el análisis"""
        if not self.is_closed:
            self.is_closed = True
            self.cpu.is_closed = True
            self.timer.stop()
            self.accept()

    def progress(self, npos: int, nmoves: int) -> None:
        """Actualiza la barra de progreso"""
        self.pb_moves.setRange(0, nmoves)
        self.pb_moves.setValue(npos)

    def pause_continue(self):
        if self.is_paused:
            self.is_paused = False
            self.icon_pause_continue()
        else:
            self.is_paused = True
            self.icon_pause_continue()
            while self.is_paused and not self.is_closed:
                time.sleep(0.05)
                QTUtil.refresh_gui()

    def icon_pause_continue(self):
        # self.bt_pause.ponIcono(Iconos.Kibitzer_Play() if self.is_paused else Iconos.Kibitzer_Pause())
        self.bt_pause.ponIcono(Iconos.ContinueColor() if self.is_paused else Iconos.PauseColor())


class AnalyzeGame:
    """Clase que maneja el análisis de un juego de ajedrez"""

    def __init__(self, cpu: CPU, alm: Any):
        self.cpu = cpu
        self.alm = alm
        self.configuration = Code.configuration

        # Configuración del motor de análisis
        self._setup_engine()

        # Configuración de blunders
        self._setup_blunders()

        # Configuración de brilliancies
        self._setup_brilliancies()

        # Configuración general
        self._setup_general()

        # Listas para resultados
        self.li_save_extra = []

    def _setup_engine(self) -> None:
        """Configura el motor de análisis"""
        if self.alm.engine == "default":
            self.xmanager = self.cpu.analyzer_clone(self.alm.vtime, self.alm.depth, self.alm.multiPV)
            self.xmanager.set_priority(self.alm.priority)
        else:
            conf_engine = copy.deepcopy(self.configuration.buscaRival(self.alm.engine))
            if self.alm.multiPV:
                conf_engine.update_multipv(self.alm.multiPV)
            self.xmanager = self.cpu.analyzer_engine(conf_engine, self.alm.vtime, self.alm.depth)

        if self.alm.nodes:
            self.xmanager.set_nodes(self.alm.nodes)

        self.vtime = self.alm.vtime
        self.depth = self.alm.depth
        self.nodes = self.alm.nodes
        self.with_variations = self.alm.include_variations
        self.accuracy_tags = self.alm.accuracy_tags
        self.skip_standard_moves = self.alm.standard_openings

    def _setup_blunders(self) -> None:
        """Configura la detección de blunders"""
        blunder_conditions = {
            INACCURACY: {INACCURACY},
            MISTAKE: {MISTAKE},
            BLUNDER: {BLUNDER},
            INACCURACY_MISTAKE_BLUNDER: {INACCURACY, BLUNDER, MISTAKE},
            INACCURACY_MISTAKE: {INACCURACY, MISTAKE},
            MISTAKE_BLUNDER: {BLUNDER, MISTAKE}
        }
        self.kblunders_condition_list = blunder_conditions.get(self.alm.kblunders_condition, {BLUNDER, MISTAKE})

        self.tacticblunders = (
            Util.opj(self.configuration.personal_training_folder, "../Tactics", self.alm.tacticblunders)
            if self.alm.tacticblunders else None
        )
        self.pgnblunders = self.alm.pgnblunders
        self.oriblunders = self.alm.oriblunders
        self.bmtblunders = self.alm.bmtblunders
        self.bmt_listaBlunders = None
        self.siTacticBlunders = False
        self.delete_previous = True

    def _setup_brilliancies(self) -> None:
        """Configura la detección de brilliancies"""
        self.fnsbrilliancies = self.alm.fnsbrilliancies
        self.pgnbrilliancies = self.alm.pgnbrilliancies
        self.oribrilliancies = self.alm.oribrilliancies
        self.bmtbrilliancies = self.alm.bmtbrilliancies
        self.bmt_listaBrilliancies = None

    def _setup_general(self) -> None:
        """Configura parámetros generales de análisis"""
        self.white = self.alm.white
        self.black = self.alm.black
        self.li_players = self.alm.li_players
        self.book = self.alm.book
        if self.book is not None:
            self.book.polyglot()

        self.li_selected = None
        self.from_last_move = self.alm.from_last_move
        self.delete_previous = self.alm.delete_previous
        self.themes_assign = AssignThemes.AssignThemes() if self.alm.themes_assign else None
        self.with_themes_tags = self.alm.themes_tags
        self.reset_themes = self.alm.themes_reset

    def xsave_extra(self, tip, par1, par2, par3=None):
        self.li_save_extra.append((tip, par1, par2, par3))

    def xsave_extra_get(self):
        li = self.li_save_extra
        self.li_save_extra = []
        return li

    def cached_begin(self):
        self.xmanager.analysis_cached_begin()

    def cached_end(self):
        self.xmanager.analysis_cached_end()

    def terminar_bmt(self, bmt_lista, name):
        """
        Si se estan creando registros para el entrenamiento BMT (Best move Training), al final hay que grabarlos
        @param bmt_lista: lista a grabar
        @param name: name del entrenamiento
        """
        if bmt_lista and len(bmt_lista) > 0:
            bmt = BMT.BMT(self.configuration.ficheroBMT)
            dbf = bmt.read_dbf(False)

            reg = dbf.baseRegistro()
            reg.ESTADO = "0"
            reg.NOMBRE = name
            reg.EXTRA = ""
            reg.TOTAL = len(bmt_lista)
            reg.HECHOS = 0
            reg.PUNTOS = 0
            reg.MAXPUNTOS = bmt_lista.max_puntos()
            reg.FINICIAL = Util.dtos(Util.today())
            reg.FFINAL = ""
            reg.SEGUNDOS = 0
            reg.BMT_LISTA = Util.var2zip(bmt_lista)
            reg.HISTORIAL = Util.var2zip([])
            reg.REPE = 0
            reg.ORDEN = 0

            dbf.insertarReg(reg, siReleer=False)

            bmt.cerrar()

    def terminar(self, si_bmt):
        """
        Proceso final, para cerrar el engine que hemos usado
        @param si_bmt: si hay que grabar el registro de BMT
        """
        self.xmanager.terminar()
        if si_bmt:
            self.terminar_bmt(self.bmt_listaBlunders, self.bmtblunders)
            self.terminar_bmt(self.bmt_listaBrilliancies, self.bmtbrilliancies)

    def save_brilliancies_fns(self, file, fen, mrm, game: Game.Game, njg):
        """
        Graba cada fen encontrado en el file "file"
        """
        if not file:
            return

        cab = ""
        for k, v in game.dic_tags().items():
            ku = k.upper()
            if ku not in ("RESULT", "FEN"):
                cab += '[%s "%s"]' % (k, v)

        game_raw = Game.game_without_variations(game)
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[0]
        p.read_pv(rm.pv)
        self.xsave_extra("file", file, f"{fen}||{p.pgn_base_raw()}|{cab} {game_raw.pgn_base_raw_copy(None, njg - 1)}")

    def graba_tactic(self, game, njg, mrm, pos_act):
        if not self.tacticblunders:
            return

        # Esta creado el folder
        before = "%s.fns" % _("Avoid the blunder")
        after = "%s.fns" % _("Take advantage of blunder")

        try:
            if not os.path.isdir(self.tacticblunders):
                dtactics = Util.opj(self.configuration.personal_training_folder, "../Tactics")
                if not os.path.isdir(dtactics):
                    Util.create_folder(dtactics)
                Util.create_folder(self.tacticblunders)
                with open(Util.opj(self.tacticblunders, "Config.ini"), "wt", encoding="utf-8",
                          errors="ignore") as f:
                    f.write(
                        """[COMMON]
    ed_reference=20
    REPEAT=0
    SHOWTEXT=1
    [TACTIC1]
    MENU=%s
    FILESW=%s:100
    [TACTIC2]
    MENU=%s
    FILESW=%s:100
    """
                        % (_("Avoid the blunder"), before, _("Take advantage of blunder"), after)
                    )
        except:
            pass

        cab = ""
        for k, v in game.dic_tags().items():
            ku = k.upper()
            if ku not in ("RESULT", "FEN"):
                cab += '[%s "%s"]' % (k, v)
        move = game.move(njg)

        fen = move.position_before.fen()
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[0]
        p.read_pv(rm.pv)

        path = Util.opj(self.tacticblunders, before)
        texto = "%s||%s|%s%s\n" % (fen, p.pgn_base_raw(), cab, game.pgn_base_raw_copy(None, njg - 1))
        self.xsave_extra("file", path, texto)

        fen = move.position.fen()
        p = Game.Game(fen=fen)
        rm = mrm.li_rm[pos_act]
        li = rm.pv.split(" ")
        p.read_pv(" ".join(li[1:]))

        path = Util.opj(self.tacticblunders, after)
        texto = "%s||%s|%s%s\n" % (fen, p.pgn_base_raw(), cab, game.pgn_base_raw_copy(None, njg))
        self.xsave_extra("file", path, texto)

        self.siTacticBlunders = True

    def save_pgn(self, file, name, dic_cab, fen, move, rm, mj):
        """
        Graba un game en un pgn

        @param file: pgn donde grabar
        @param name: name del engine que hace el analysis
        @param dic_cab: etiquetas de head del PGN
        @param fen: fen de la position
        @param move: move analizada
        @param rm: respuesta engine
        @param mj: respuesta engine con la mejor move, usado en caso de blunders, para incluirla
        """
        if not file:
            return False

        if mj:  # blunder
            game_blunder = Game.Game()
            game_blunder.set_position(move.position_before)
            game_blunder.read_pv(rm.pv)
            jg0 = game_blunder.move(0)
            jg0.set_comment(rm.texto())

        p = Game.Game()
        p.set_position(move.position_before)
        if mj:  # blunder
            rm = mj
        p.read_pv(rm.pv)
        if p.is_finished():
            result = p.resultado()
            mas = ""  # ya lo anade en la ultima move
        else:
            mas = " *"
            result = "*"

        jg0 = p.move(0)
        t = "%0.2f" % (float(self.vtime) / 1000.0,)
        t = t.rstrip("0")
        if t[-1] == ".":
            t = t[:-1]
        eti_t = "%s %s" % (t, _("Second(s)"))

        jg0.set_comment("%s %s: %s\n" % (name, eti_t, rm.texto()))
        if mj:
            jg0.add_variation(game_blunder)

        cab = ""
        for k, v in dic_cab.items():
            ku = k.upper()
            if ku not in ("RESULT", "FEN"):
                cab += '[%s "%s"]\n' % (k, v)
        # Nos protegemos de que se hayan escrito en el pgn original de otra forma
        cab += '[FEN "%s"]\n' % fen
        cab += '[Result "%s"]\n' % result

        texto = cab + "\n" + p.pgn_base() + mas + "\n\n"
        self.xsave_extra("file", file, texto)

        return True

    def save_bmt(self, si_blunder, fen, mrm, pos_act, cl_game, txt_game):
        """
        Se graba una position en un entrenamiento BMT
        @param si_blunder: si es blunder o brilliancie
        @param fen: position
        @param mrm: multirespuesta del engine
        @param pos_act: position de la position elegida en mrm
        @param cl_game: key de la game
        @param txt_game: la game completa en texto
        """

        previa = 999999999
        nprevia = -1
        tniv = 0
        game_bmt = Game.Game()
        cp = game_bmt.first_position
        cp.read_fen(fen)

        if len(mrm.li_rm) > 16:
            mrm_bmt = copy.deepcopy(mrm)
            if pos_act > 15:
                mrm_bmt.li_rm[15] = mrm_bmt.li_rm[pos_act]
                pos_act = 15
            mrm_bmt.li_rm = mrm_bmt.li_rm[:16]
        else:
            mrm_bmt = mrm

        for n, rm in enumerate(mrm_bmt.li_rm):
            pts = rm.centipawns_abs()
            if pts != previa:
                previa = pts
                nprevia += 1
            tniv += nprevia
            rm.nivelBMT = nprevia
            rm.siElegida = False
            rm.siPrimero = n == pos_act
            game_bmt.set_position(cp)
            game_bmt.read_pv(rm.pv)
            rm.txtPartida = game_bmt.save()

        bmt_uno = BMT.BMTUno(fen, mrm_bmt, tniv, cl_game)

        tipo = "bmt_blunders" if si_blunder else "bmt_brilliancies"
        self.xsave_extra(tipo, bmt_uno, cl_game, txt_game)

    def xprocesa(self, game):
        self.si_bmt_blunders = False
        self.si_bmt_brilliancies = False

        if self.alm.num_moves:
            li_moves = []
            lni = Util.ListaNumerosImpresion(self.alm.num_moves)
            num_move = int(game.primeraJugada())
            is_white = not game.starts_with_black
            for nRaw in range(game.num_moves()):
                must_save = lni.siEsta(num_move)
                if must_save:
                    if is_white:
                        if not self.alm.white:
                            must_save = False
                    elif not self.alm.black:
                        must_save = False
                if must_save:
                    li_moves.append(nRaw)
                is_white = not is_white
                if is_white:
                    num_move += 1

            self.li_selected = li_moves
        else:
            self.li_selected = None

        def gui_dispatch(xrm):
            return not self.cpu.is_closed

        self.xmanager.set_gui_dispatch(gui_dispatch)  # Dispatch del engine, si esta puesto a 4 minutos por ejemplo que
        # compruebe si se ha indicado que se cancele.

        si_blunders = self.pgnblunders or self.oriblunders or self.bmtblunders or self.tacticblunders
        si_brilliancies = self.fnsbrilliancies or self.pgnbrilliancies or self.bmtbrilliancies

        if self.bmtblunders and self.bmt_listaBlunders is None:
            self.bmt_listaBlunders = BMT.BMTLista()

        if self.bmtbrilliancies and self.bmt_listaBrilliancies is None:
            self.bmt_listaBrilliancies = BMT.BMTLista()

        xlibro_aperturas = self.book

        is_white = self.white
        is_black = self.black

        if self.li_players:
            for x in ["BLACK", "WHITE"]:
                player = game.get_tag(x)
                if player:
                    player = player.upper()
                    si = False
                    for uno in self.li_players:
                        si_z = uno.endswith("*")
                        si_a = uno.startswith("*")
                        uno = uno.replace("*", "").strip().upper()
                        if si_a:
                            if player.endswith(uno):
                                si = True
                            if si_z:  # form para poner si_a y si_z
                                si = uno in player
                        elif si_z:
                            if player.startswith(uno):
                                si = True
                        elif uno == player:
                            si = True
                        if si:
                            break
                    if not si:
                        if x == "BLACK":
                            is_black = False
                        else:
                            is_white = False

        if not (is_white or is_black):
            return

        cl_game = Util.huella()
        # txt_game = game.save()
        si_poner_pgn_original_blunders = False
        si_poner_pgn_original_brilliancies = False

        n_mov = len(game)
        if self.li_selected is None:
            li_pos_moves = list(range(n_mov))
        else:
            li_pos_moves = self.li_selected[:]

        st_borrar = set()
        if xlibro_aperturas is not None:
            for mov in li_pos_moves:
                if self.cpu.is_closed:
                    return

                move = game.move(mov)
                if xlibro_aperturas.get_list_moves(move.position.fen()):
                    st_borrar.add(mov)
                    continue
                else:
                    break

        if self.from_last_move:
            li_pos_moves.reverse()

        n_moves = len(li_pos_moves)

        for npos, pos_move in enumerate(li_pos_moves, 1):
            if not self.cpu.progress(npos, n_moves):
                return

            if pos_move in st_borrar:
                continue

            if self.cpu.is_closed:
                return

            move = game.move(pos_move)

            if self.cpu.is_closed:
                return

            li_moves_games = move.list_all_moves() if self.alm.analyze_variations else [(move, game, pos_move)]

            for move, game_move, pos_current_move in li_moves_games:

                # # white y black
                white_move = move.position_before.is_white
                if white_move:
                    if not is_white:
                        continue
                else:
                    if not is_black:
                        continue

                # -# previos
                allow_add_variations = True
                if self.delete_previous:
                    move.analysis = None

                # si no se borran los análisis previos y existe un análisis no se tocan las variantes
                elif move.analysis:
                    if self.with_variations and move.variations:
                        allow_add_variations = False

                # -# Procesamos
                if move.analysis is None:
                    resp = self.xmanager.analyzes_move_game(
                        game_move,
                        pos_current_move,
                        self.vtime,
                        depth=self.depth,
                    )
                    if not resp:
                        return

                    if self.cpu.is_closed:
                        return

                    move.analysis = resp

                cp = move.position_before
                mrm, pos_act = move.analysis
                move.complexity = AnalysisIndexes.calc_complexity(cp, mrm)
                move.winprobability = AnalysisIndexes.calc_winprobability(cp, mrm)
                move.narrowness = AnalysisIndexes.calc_narrowness(cp, mrm)
                move.efficientmobility = AnalysisIndexes.calc_efficientmobility(cp, mrm)
                move.piecesactivity = AnalysisIndexes.calc_piecesactivity(cp, mrm)
                move.exchangetendency = AnalysisIndexes.calc_exchangetendency(cp, mrm)

                rm = mrm.li_rm[pos_act]
                nag, color = mrm.set_nag_color(rm)
                move.add_nag(nag)

                if si_blunders or si_brilliancies or self.with_variations:

                    mj = mrm.li_rm[0]

                    fen = move.position_before.fen()

                    if self.with_variations and allow_add_variations:
                        if not move.analisis2variantes(self.alm, self.delete_previous):
                            move.remove_all_variations()

                    ok_blunder = nag in self.kblunders_condition_list
                    if ok_blunder:
                        self.graba_tactic(game, pos_move, mrm, pos_act)

                        if self.save_pgn(self.pgnblunders, mrm.name, game.dic_tags(), fen, move, rm, mj):
                            si_poner_pgn_original_blunders = True

                        if self.bmtblunders:
                            txt_game = Game.game_without_variations(game).save()
                            self.save_bmt(True, fen, mrm, pos_act, cl_game, txt_game)
                            self.si_bmt_blunders = True

                    if move.is_brilliant():
                        move.add_nag(NAG_3)
                        self.save_brilliancies_fns(self.fnsbrilliancies, fen, mrm, game, pos_current_move)

                        if self.save_pgn(self.pgnbrilliancies, mrm.name, game.dic_tags(), fen, move, rm, None):
                            si_poner_pgn_original_brilliancies = True

                        if self.bmtbrilliancies:
                            txt_game = Game.game_without_variations(game).save()
                            self.save_bmt(False, fen, mrm, pos_act, cl_game, txt_game)
                            self.si_bmt_brilliancies = True

        # Ponemos el texto original en la ultima
        if si_poner_pgn_original_blunders and self.oriblunders:
            self.xsave_extra("file", self.pgnblunders, "\n%s\n\n" % game.pgn())

        if si_poner_pgn_original_brilliancies and self.oribrilliancies:
            self.xsave_extra("file", self.pgnbrilliancies, "\n%s\n\n" % game.pgn())

        if self.themes_assign:
            self.themes_assign.assign_game(game, self.with_themes_tags, self.reset_themes)

        self.xmanager.remove_gui_dispatch()
