import os
import platform
import shutil
import subprocess
import time

import psutil

import Code
from Code import Util
from Code.QT import QTUtil2

STOCKFISH_KEY = "STOCKFISH17"


def process_running(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False


def check_engine(path: str) -> bool:
    if not os.path.isfile(path):
        return False

    path = os.path.abspath(path)
    xargs = ["./%s" % os.path.basename(path)]

    if Code.is_windows:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        startupinfo = None

    curdir = os.path.abspath(os.curdir)
    ok = False
    process = None
    try:
        os.chdir(os.path.dirname(path))
        process = subprocess.Popen(xargs, stdout=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo)
        os.chdir(curdir)
        pid = process.pid
        time.sleep(0.2)
        if not process_running(pid):
            return False

        stdout = process.stdout
        stdin = process.stdin

        stdin.write(b"go depth 1\n")
        stdin.flush()

        ini = time.time()
        while (time.time() - ini) < 3:
            x = stdout.readline()
            if b"bestmove" in x:
                ok = True
                break
            time.sleep(0.1)

        if not process_running(pid):
            return False

    except:
        os.chdir(curdir)

    try:
        if process:
            process.kill()
            process.terminate()
    except:
        pass

    return ok


def check_stockfish(window, check_again):
    conf_stockfish = Code.configuration.dic_engines["stockfish"]
    folder = os.path.dirname(conf_stockfish.path_exe)

    dic = Code.configuration.read_variables(STOCKFISH_KEY)
    if "NAME" in dic:
        conf_stockfish.name = dic["NAME"]
        if not check_again:
            return True

    seek = "64" if platform.machine().endswith("64") else "32"
    Code.procesador.close_engines()

    path_versions = Util.opj(folder, "versions.txt")
    lista = []
    with open(path_versions, "rt") as f:
        for linea in f:
            linea = linea.strip()
            if seek in linea:
                lista.append(linea)

    # Se guarda el primero, por si el resto no son validos, y no se muestra el mensaje mas veces
    conf_stockfish.name = lista[0].replace(".exe", "")
    Code.configuration.write_variables(STOCKFISH_KEY, {"NAME": conf_stockfish.name})

    mensaje = _("Selecting the best stockfish version for your CPU")
    um = QTUtil2.one_moment_please(window, mensaje)
    for file_engine in lista[1:]:  # el primero no lo miramos
        path_engine = Util.opj(folder, file_engine)
        if check_engine(path_engine):
            correct = file_engine
            um.label(mensaje + "\n" + file_engine)
            path_engine = conf_stockfish.path_exe
            Util.remove_file(path_engine)
            path_correct = Util.opj(folder, correct)
            shutil.copy(path_correct, path_engine)

            conf_stockfish.name = correct.replace(".exe", "")
            Code.configuration.write_variables(STOCKFISH_KEY, {"NAME": conf_stockfish.name})
        else:
            break

    um.final()
    return True


def check_engines(window):
    return check_stockfish(window, False)


def current_stockfish():
    dic = Code.configuration.read_variables(STOCKFISH_KEY)
    return dic.get("NAME", "stockfish")
