import collections
import time

from PySide2 import QtCore, QtWidgets

from Code.MainWindow import Tareas


class CPU:
    def __init__(self, main_window):
        self.main_window = main_window
        self.board = main_window.board
        self.ms_step = 10
        self.ultimaID = 0
        self.timer = None
        self.dicTareas = collections.OrderedDict()

    def reset(self):
        self.ultimaID = 0
        self.timer = None
        self.dicTareas = collections.OrderedDict()

    def new_id(self):
        self.ultimaID += 1
        return self.ultimaID

    def add_tarea(self, tarea, padre, is_exclusive):
        tid = tarea.id
        self.dicTareas[tid] = tarea
        tarea.padre = padre
        tarea.is_exclusive = is_exclusive
        return tid

    def duerme(self, seconds, padre=0, is_exclusive=False):
        tarea = Tareas.TareaDuerme(seconds)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, is_exclusive)

    def tooltip(self, texto, padre=0, is_exclusive=False):
        tarea = Tareas.TareaToolTip(texto)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, is_exclusive)

    def move_piece(self, from_a1h8, to_a1h8, seconds=1.0, padre=0, is_exclusive=False):
        tarea = Tareas.Tareamove_piece(from_a1h8, to_a1h8, seconds)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, is_exclusive)

    def remove_piece(self, a1h8, padre=0, is_exclusive=False, tipo=None):
        tarea = Tareas.TareaBorraPieza(a1h8, tipo)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, is_exclusive)

    def remove_piece_insecs(self, a1h8, seconds):
        tarea = Tareas.TareaBorraPiezaSecs(a1h8, seconds)
        tarea.enlaza(self)
        return self.add_tarea(tarea, 0, False)

    def change_piece(self, a1h8, pieza, padre=0, is_exclusive=False):
        tarea = Tareas.TareaCambiaPieza(a1h8, pieza)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, is_exclusive)

    def set_position(self, position, padre=0):
        tarea = Tareas.TareaPonPosicion(position)
        tarea.enlaza(self)
        return self.add_tarea(tarea, padre, True)

    def start(self):
        if self.timer:
            self.timer.stop()
            del self.timer
        self.timer = QtCore.QTimer(self.main_window)
        self.timer.timeout.connect(self.run)
        self.timer.start(self.ms_step)

    def stop(self):
        if self.timer:
            self.timer.stop()
            del self.timer
            self.timer = None
        self.reset()

    def run_lineal(self):
        self.start()
        while self.dicTareas:
            time.sleep(self.ms_step / 1000.0)
            QtWidgets.QApplication.processEvents()

    def run(self):
        li = sorted(self.dicTareas.keys())
        n_pasos = 0
        for tid in li:
            tarea = self.dicTareas[tid]

            if tarea.padre and tarea.padre in self.dicTareas:
                continue  # no ha terminado

            is_exclusive = tarea.is_exclusive
            if is_exclusive:
                if n_pasos:
                    continue  # Hay que esperar a que terminen todos los anteriores

            is_the_last = tarea.unPaso()
            n_pasos += 1
            if is_the_last:
                del self.dicTareas[tid]

            if is_exclusive:
                break

        if len(self.dicTareas) == 0:
            self.stop()
        QtWidgets.QApplication.processEvents()
