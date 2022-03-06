import collections
import time

from PySide2 import QtCore, QtWidgets

from Code.MainWindow import Tareas


class CPU:
    def __init__(self, main_window):
        self.main_window = main_window
        self.board = main_window.board
        self.ms_step = 10
        self.reset()

    def reset(self):
        self.ultimaID = 0
        self.timer = None
        self.dicTareas = collections.OrderedDict()

    def nuevaID(self):
        self.ultimaID += 1
        return self.ultimaID

    def masTarea(self, tarea, padre, siExclusiva):
        tid = tarea.id
        self.dicTareas[tid] = tarea
        tarea.padre = padre
        tarea.siExclusiva = siExclusiva
        return tid

    def duerme(self, seconds, padre=0, siExclusiva=False):
        tarea = Tareas.TareaDuerme(seconds)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, siExclusiva)

    def toolTip(self, texto, padre=0, siExclusiva=False):
        tarea = Tareas.TareaToolTip(texto)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, siExclusiva)

    def muevePieza(self, from_a1h8, to_a1h8, seconds=1.0, padre=0, siExclusiva=False):
        tarea = Tareas.TareaMuevePieza(from_a1h8, to_a1h8, seconds)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, siExclusiva)

    def borraPieza(self, a1h8, padre=0, siExclusiva=False, tipo=None):
        tarea = Tareas.TareaBorraPieza(a1h8, tipo)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, siExclusiva)

    def borraPiezaSecs(self, a1h8, seconds):
        tarea = Tareas.TareaBorraPiezaSecs(a1h8, seconds)
        tarea.enlaza(self)
        return self.masTarea(tarea, 0, False)

    def cambiaPieza(self, a1h8, pieza, padre=0, siExclusiva=False):
        tarea = Tareas.TareaCambiaPieza(a1h8, pieza)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, siExclusiva)

    def set_position(self, position, padre=0):
        tarea = Tareas.TareaPonPosicion(position)
        tarea.enlaza(self)
        return self.masTarea(tarea, padre, True)

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

    def runLineal(self):
        self.start()
        while self.dicTareas:
             time.sleep(self.ms_step/1000.0)
             QtWidgets.QApplication.processEvents()

    def run(self):
        li = sorted(self.dicTareas.keys())
        nPasos = 0
        for tid in li:
            tarea = self.dicTareas[tid]

            if tarea.padre and tarea.padre in self.dicTareas:
                continue  # no ha terminado

            siExclusiva = tarea.siExclusiva
            if siExclusiva:
                if nPasos:
                    continue  # Hay que esperar a que terminen todos los anteriores

            siUltimo = tarea.unPaso()
            nPasos += 1
            if siUltimo:
                del self.dicTareas[tid]

            if siExclusiva:
                break

        if len(self.dicTareas) == 0:
            self.stop()
        QtWidgets.QApplication.processEvents()

