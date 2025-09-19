from PySide2 import QtCore, QtWidgets

import Code
from Code import Util, XRun
from Code.Base import Game
from Code.Base.Constantes import RUNA_GAME, RUNA_HALT, RUNA_CONFIGURATION, RUNA_TERMINATE
from Code.BestMoveTraining import BMT
from Code.QT import QTUtil, LCDialog, Iconos, Controles, Colocacion
from Code.SQL import UtilSQL


class Orden:
    def __init__(self):
        self.key = ""
        self.dv = {}

    def set(self, name, valor):
        self.dv[name] = valor

    def block(self):
        self.dv["__CLAVE__"] = self.key
        return self.dv

    def get(self, name):
        return self.dv.get(name)


class IPCAnalysis:
    def __init__(self, alm, huella, num_worker):
        self.closed = False
        configuration = Code.configuration

        folder_tmp = Code.configuration.temporary_folder()
        filebase = Util.opj(folder_tmp, huella + f"_{num_worker}")
        file_send = filebase + "_send.sqlite"
        file_receive = filebase + "_receive.sqlite"

        self.ipc_send = UtilSQL.IPC(file_send, True)
        self.ipc_receive = UtilSQL.IPC(file_receive, True)

        orden = Orden()
        orden.key = RUNA_CONFIGURATION
        orden.set("USER", configuration.user)
        orden.set("ALM", alm)
        orden.set("NUM_WORKER", num_worker)

        self.send(orden)

        self.popen = XRun.run_lucas("-analysis", filebase)

    def send(self, orden):
        if not self.closed:
            self.ipc_send.push(orden.block())

    def receive(self):
        return self.ipc_receive.pop()

    def working(self):
        if self.popen is None or self.closed:
            return False
        return self.popen.poll() is None

    def send_game(self, game, recno):
        orden = Orden()
        orden.key = RUNA_GAME
        orden.dv["GAME"] = game
        orden.dv["RECNO"] = recno
        self.send(orden)

    def send_halt(self):
        orden = Orden()
        orden.key = RUNA_HALT
        self.send(orden)

    def send_terminate(self):
        orden = Orden()
        orden.key = RUNA_TERMINATE
        self.send(orden)

    def close(self):
        if not self.closed:
            self.ipc_send.close()
            self.ipc_receive.close()
            if self.popen:
                try:
                    self.popen.terminate()
                    self.popen = None
                except:
                    pass
            self.closed = True


class AnalysisMassiveWithWorkers:
    def __init__(self, wowner, alm, nregs, li_seleccionadas):
        self.db_games = wowner.db_games
        self.grid = wowner.grid
        self.wowner = wowner
        self.li_seleccionadas = li_seleccionadas
        self.nregs = nregs
        self.pos_reg = -1
        self.num_games_analyzed = 0

        self.bmt_blunders = None
        self.bmt_brillancies = None

        if alm.num_moves:
            alm.lni = Util.ListaNumerosImpresion(alm.num_moves)
        else:
            alm.lni = None
        self.alm = alm

        self.li_workers = []

        self.window = None

    def gen_workers(self):
        huella = Util.huella()
        num_workers = min(self.alm.workers, self.nregs)
        for num_worker in range(num_workers):
            worker = IPCAnalysis(self.alm, huella, num_worker)
            self.li_workers.append(worker)
            if not self.send_game_worker(num_worker):
                break

    def send_game_worker(self, num_worker):
        self.pos_reg += 1
        if self.pos_reg >= self.nregs:
            for worker in self.li_workers:
                worker.send_terminate()
            return False
        if self.alm.multiple_selected:
            recno = self.li_seleccionadas[self.pos_reg]
        else:
            recno = self.pos_reg

        game = self.db_games.read_game_recno(recno)
        self.li_workers[num_worker].send_game(game, recno)
        return True

    def close(self):
        worker: IPCAnalysis
        for worker in self.li_workers:
            if not worker.closed:
                worker.send_halt()
                worker.close()
        self.window.xclose()

    def processing(self):
        QTUtil.refresh_gui()
        if self.window.is_canceled():
            return self.close()

        if self.window.is_paused():
            return

        actives = 0

        worker: IPCAnalysis
        for num_worker, worker in enumerate(self.li_workers):
            if worker.closed:
                continue
            if not worker.working():
                worker.close()
                continue

            actives += 1

            order: Orden = worker.receive()
            if order is None:
                pass
            elif order.key == RUNA_GAME:
                self.send_game_worker(num_worker)

                game: Game.Game = order.get("GAME")
                if self.alm.accuracy_tags:
                    game.add_accuracy_tags()
                recno = order.get("RECNO")
                self.db_games.save_game_recno(recno, game)
                self.num_games_analyzed += 1
                self.window.set_pos(self.num_games_analyzed)

                li_extra = order.get("EXTRA")
                if li_extra:
                    for tipo, par1, par2, par3 in li_extra:
                        if tipo == "file":
                            with open(par1, "at", encoding="utf-8", errors="ignore") as f:
                                f.write(par2)
                        elif tipo == "bmt_blunders":
                            if self.bmt_blunders is None:
                                self.bmt_blunders = BMT.BMTLista()
                            self.bmt_blunders.nuevo(par1)
                            self.bmt_blunders.check_game(par2, par3)
                        elif tipo == "bmt_brilliancies":
                            if self.bmt_brillancies is None:
                                self.bmt_brillancies = BMT.BMTLista()
                            self.bmt_brillancies.nuevo(par1)
                            self.bmt_brillancies.check_game(par2, par3)

            elif order.key == RUNA_TERMINATE:
                worker.close()
                actives -= 1
                continue

        if actives == 0:
            self.close()

    def save_bmt(self, bmt):
        if bmt is None:
            return

    def run(self):
        self.window = WProgress(self.wowner, self, self.nregs)

        self.gen_workers()
        self.processing()
        self.window.exec_()
        for bmt_lista, name in ((self.bmt_blunders, self.alm.bmtblunders),
                                (self.bmt_brillancies, self.alm.bmtbrilliancies)):
            if bmt_lista and len(bmt_lista) > 0:
                bmt = BMT.BMT(Code.configuration.ficheroBMT)
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


class WProgress(LCDialog.LCDialog):
    def __init__(self, w_parent, amww: AnalysisMassiveWithWorkers, nregs: int):
        LCDialog.LCDialog.__init__(self, w_parent, _("Analyzing"), Iconos.Analizar(), "massive_progress")

        self.lb_game = Controles.LB(self)

        self.pb_moves = QtWidgets.QProgressBar(self)
        self.pb_moves.setFormat(_("Game") + " %v/%m")
        self.pb_moves.setRange(0, nregs)

        self._is_paused = False
        self.bt_pause = Controles.PB(self, "", self.pause_continue, plano=True)
        self.icon_pause_continue()
        pb_cancel = Controles.PB(self, _("Cancel"), self.xcancel, plano=False).ponIcono(Iconos.Delete())

        lay = Colocacion.H().control(self.lb_game).control(self.pb_moves).control(self.bt_pause)
        lay2 = Colocacion.H().relleno().control(pb_cancel)
        layout = Colocacion.V().otro(lay).espacio(20).otro(lay2)
        self.setLayout(layout)

        self.amww: AnalysisMassiveWithWorkers = amww
        self._is_canceled = False
        self._is_closed = False

        self.restore_video(default_width=400, default_height=40)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.xreceive)
        self.timer.start(200)

        self.restore_video()
        self.working = False

    def xreceive(self):
        QTUtil.refresh_gui()
        if self.working:
            return
        self.working = True
        self.amww.processing()
        self.working = False

    def xcancel(self):
        self._is_canceled = True
        self.amww.close()

    def pause_continue(self):
        if self._is_paused:
            self._is_paused = False
            self.icon_pause_continue()
        else:
            self._is_paused = True
            self.icon_pause_continue()

    def icon_pause_continue(self):
        # self.bt_pause.ponIcono(Iconos.Kibitzer_Play() if self._is_paused else Iconos.Kibitzer_Pause())
        self.bt_pause.ponIcono(Iconos.ContinueColor() if self._is_paused else Iconos.PauseColor())

    def is_canceled(self):
        return self._is_canceled

    def is_paused(self):
        return self._is_paused

    def set_pos(self, pos):
        if not self._is_canceled:
            self.pb_moves.setValue(pos)

    def xclose(self):
        if not self._is_closed:
            self._is_closed = True
            self.timer.stop()
            self.timer = None
            self.accept()
