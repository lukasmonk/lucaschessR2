import sys

import Code
from Code import Procesador
from Code import Util, XRun
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

    main_procesador.close_engines()
    main_procesador.kibitzers_manager.close()

    if resp == OUT_REINIT:
        XRun.run_lucas()
