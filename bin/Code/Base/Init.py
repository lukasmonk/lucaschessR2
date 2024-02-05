import os
import sys

import Code
from Code import Procesador
from Code import Util
from Code.Base.Constantes import OUT_REINIT
from Code.MainWindow import LucasChessGui
from Code.Sound import Sound


def init():
    if not Code.DEBUG:
        sys.stderr = Util.Log("bug.log")

    main_procesador = Procesador.Procesador()
    main_procesador.set_version(Code.VERSION)
    run_sound = Sound.RunSound()
    resp = LucasChessGui.run_gui(main_procesador)
    run_sound.close()

    main_procesador.stop_engines()
    main_procesador.kibitzers_manager.close()

    if resp == OUT_REINIT:
        if sys.argv[0].endswith(".py"):
            exe = os.path.abspath(sys.argv[0])
        else:
            exe = "LucasR.exe" if Code.is_windows else "./LucasR"
        Code.startfile(exe)
