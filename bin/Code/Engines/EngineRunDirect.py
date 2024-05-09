import os
import subprocess
import sys
import time

import psutil

import Code
from Code import Util
from Code.Engines import EngineResponse, Priorities


class DirectEngine(object):
    def __init__(self, name, exe, li_options_uci=None, num_multipv=0, priority=None, args=None, log=None):

        self.log = None
        if log:
            self.log_open(log)

        self.name = name

        self.is_white = True

        self.gui_dispatch = None
        self.minDispatch = 1.0
        self.ultDispatch = 0

        self.who_dispatch = name
        self.uci_ok = False
        self.pid = None

        self.uci_lines = []

        if not os.path.isfile(exe):
            return

        self.exe = exe = os.path.abspath(exe)
        direxe = os.path.dirname(exe)
        xargs = ["./%s" % os.path.basename(exe)]
        if args:
            xargs.extend(args)

        if Code.is_windows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            startupinfo = None
            ld_library = os.environ.get("LD_LIBRARY_PATH", "")
            if ld_library:
                ld_library += ":"
            ld_library += direxe
            os.environ["LD_LIBRARY_PATH"] = ld_library

        curdir = os.path.abspath(os.curdir)
        os.chdir(direxe)
        self.process = subprocess.Popen(xargs, stdout=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo)

        os.chdir(curdir)

        self.pid = self.process.pid
        if priority is not None:
            p = psutil.Process(self.pid)
            p.nice(Priorities.priorities.value(priority))

        self.stdout = self.process.stdout
        self.stdin = self.process.stdin

        self.orden_uci()

        setoptions = False
        if li_options_uci:
            for opcion, valor in li_options_uci:
                if type(valor) == bool:
                    valor = str(valor).lower()
                self.set_option(opcion, valor)
                setoptions = True

        if setoptions:
            self.pwait_list("isready", "readyok", 1000)
        self.ucinewgame()

    def set_gui_dispatch(self, gui_dispatch, who_dispatch=None):
        self.gui_dispatch = gui_dispatch

    def put_line(self, line):
        self.stdin.write(line.encode("utf-8") + b"\n")
        self.stdin.flush()
        if self.log:
            self.log_write(">>> %s" % line)

    def log_open(self, file):
        self.log = open(file, "a")
        self.log.write("%s %s\n\n" % (str(Util.today()), "-" * 70))

    def log_close(self):
        if self.log:
            self.log.close()
            self.log = None

    def log_write(self, line):
        self.log.write(line)

    def pwait_list(self, orden, txt_busca, ms_maxtime):
        self.put_line(orden)
        ini = time.time()
        li = []
        while (time.time() - ini) * 1000 < ms_maxtime:
            line = self.stdout.readline().decode("utf-8", errors="ignore")
            if self.log:
                self.log_write(line.strip())
            li.append(line.strip())
            if line.startswith(txt_busca):
                return li, True
        return li, False

    def pwait_list_dispatch(self, orden, txt_busca, ms_maxtime):
        self.put_line(orden)
        ini = time.time()
        tm_dispatch = ini
        li = []
        mrm = EngineResponse.MultiEngineResponse(self.name, self.is_white)
        while (time.time() - ini) * 1000 < ms_maxtime:
            if (time.time() - tm_dispatch) >= 1.0:
                mrm.ordena()
                rm = mrm.best_rm_ordered()
                if not self.gui_dispatch(rm):
                    return li, False
                tm_dispatch = time.time()
            line = self.stdout.readline().strip().decode("utf-8", errors="ignore")
            if self.log:
                self.log_write(line)
            li.append(line)
            mrm.dispatch(line)
            if line.startswith(txt_busca):
                return li, True
        return li, False

    def orden_uci(self):
        li, self.uci_ok = self.pwait_list("uci", "uciok", 10000)
        self.uci_lines = [x for x in li if x.startswith("id ") or x.startswith("option name")] if self.uci_ok else []

    def ready_ok(self):
        li, readyok = self.pwait_list("isready", "readyok", 10000)
        return readyok

    def work_ok(self, orden):
        self.put_line(orden)
        return self.ready_ok()

    def ucinewgame(self):
        self.put_line("ucinewgame")

    def set_option(self, name, value):
        if value:
            self.put_line("setoption name %s value %s" % (name, value))
        else:
            self.put_line("setoption name %s" % name)

    def bestmove_fen(self, fen, max_time, max_depth):
        self.work_ok("position fen %s" % fen)
        self.is_white = is_white = "w" in fen
        return self._mejorMov(max_time, max_depth, is_white)

    def _mejorMov(self, max_time, max_depth, is_white):
        env = "go"
        if max_depth:
            env += " depth %d" % max_depth
        elif max_time:
            env += " movetime %d" % max_time

        ms_tiempo = 10000
        if max_time:
            ms_tiempo = max_time
        elif max_depth:
            ms_tiempo = int(max_depth * ms_tiempo / 3.0)

        if self.gui_dispatch:
            li_resp, result = self.pwait_list_dispatch(env, "bestmove", ms_tiempo)
        else:
            li_resp, result = self.pwait_list(env, "bestmove", ms_tiempo)

        if not result:
            return None

        mrm = EngineResponse.MultiEngineResponse(self.name, is_white)
        for linea in li_resp:
            mrm.dispatch(linea)
        mrm.max_time = max_time
        mrm.max_depth = max_depth
        mrm.ordena()
        return mrm

    def close(self):
        if self.pid:
            if self.process.poll() is None:
                self.put_line("quit")
                wtime = 40  # wait for it, wait for it...
                while self.process.poll() is None and wtime > 0:
                    time.sleep(0.05)
                    wtime -= 1

                if self.process.poll() is None:  # nope, no luck
                    sys.stderr.write("INFO X CLOSE525: the engine %s won't close properly.\n" % self.exe)
                    self.process.kill()
                    self.process.terminate()

            self.pid = None
        if self.log:
            self.log_close()
