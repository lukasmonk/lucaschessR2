import Code
from Code import Util
from Code.CompetitionWithTutor import CompetitionWithTutor
from Code.QT import WindowMemoria, QTUtil2


class Memoria:
    def __init__(self, procesador):

        self.procesador = procesador
        self.file = procesador.configuration.file_memory

        self.dic_data = Util.restore_pickle(self.file)
        if self.dic_data is None:
            self.dic_data = {}
            for x in range(6):
                self.dic_data[x] = [0] * 25

        self.categorias = CompetitionWithTutor.Categorias()
        self.main_window = procesador.main_window

    def nivel(self, numcategoria):
        li = self.dic_data[numcategoria]
        for n, t in enumerate(li):
            if t == 0:
                return n - 1
        return 24

    def maxnivel(self, numcategoria):
        nm = self.nivel(numcategoria) + 1
        if nm > 24:
            nm = 24
        if numcategoria:
            nma = self.nivel(numcategoria - 1)
            nm = min(nm, nma)
        return nm

    def record(self, numcategoria, nivel):
        li = self.dic_data[numcategoria]
        return li[nivel]

    def is_active(self, numcategoria):
        if numcategoria == 0:
            return True
        return self.nivel(numcategoria - 1) > 0

    def lanza(self, numcategoria):

        # pedimos el nivel
        while True:
            cat = self.categorias.number(numcategoria)
            maxnivel = self.maxnivel(numcategoria)
            nivel_mas1 = WindowMemoria.paramMemoria(self.procesador.main_window, cat.name(), maxnivel + 1)
            if nivel_mas1 is None:
                return
            nivel = nivel_mas1 - 1
            if nivel < 0:
                return
            else:
                if self.launch_level(numcategoria, nivel):
                    if nivel == 24 and numcategoria < 5:
                        numcategoria += 1
                else:
                    return

    def launch_level(self, numcategoria, nivel):

        piezas = nivel + 3
        seconds = (6 - numcategoria) * piezas

        li_fen = self.get_list_fens(piezas)
        if not li_fen:
            return

        cat = self.categorias.number(numcategoria)

        record = self.record(numcategoria, nivel)
        vtime = WindowMemoria.lanzaMemoria(self.procesador, cat.name(), nivel, seconds, li_fen, record)
        if vtime:
            if record == 0 or vtime < record:
                li = self.dic_data[numcategoria]
                li[nivel] = vtime
                Util.save_pickle(self.file, self.dic_data)

            return True
        return False

    def get_list_fens(self, num_piezas):
        with QTUtil2.OneMomentPlease(self.procesador.main_window):

            li = []

            fedu = Util.listfiles(Code.path_resource("Trainings", "Checkmates by Eduardo Sadier"), "*.fns")[0]
            with open(fedu, "rb") as f:
                for lst in f:
                    if lst:
                        pz = 0
                        lst = lst.split(b"|")[0]
                        for c in lst:
                            if c == " ":
                                break
                            if c in b"prnbqkPRNBQK":
                                pz += 1
                        if pz == num_piezas:
                            li.append(lst.decode("utf-8"))

        return li
