import os
import time

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Util
from Code.Board import BoardElements, BoardTypes
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles
from Code.SQL import UtilSQL
from Code.Sound import Sound


class MesaSonido(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QGraphicsView.__init__(self)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.NoAnchor)
        self.escena = QtWidgets.QGraphicsScene(self)
        self.escena.setItemIndexMethod(self.escena.NoIndex)
        self.setScene(self.escena)

        self.main_window = parent
        self.crea()

    def crea(self):
        # base
        cajon = BoardTypes.Caja()
        cajon.physical_pos.orden = 1
        cajon.colorRelleno = 4294243572
        ancho, alto = 544, 100
        cajon.physical_pos.ancho, cajon.physical_pos.alto = ancho, alto
        cajon.physical_pos.x, cajon.physical_pos.y = 0, 0
        cajon.tipo = QtCore.Qt.NoPen

        self.cajonSC = BoardElements.CajaSC(self.escena, cajon)

        def tiempoSC(x, y, linea, minim, maxim, rutina, color):
            tt = BoardTypes.Texto()
            tt.font_type = BoardTypes.FontType(Code.font_mono, 10)
            tt.physical_pos.ancho = 68
            tt.physical_pos.alto = 12
            tt.physical_pos.orden = 5
            tt.colorFondo = color
            tt.valor = "00:00:00"
            tt.physical_pos.x = x
            tt.physical_pos.y = y
            tt.linea = linea
            tt.min = x + minim
            tt.max = x + maxim
            tt.rutina = rutina
            sc = BoardElements.TiempoSC(self.escena, tt)
            sc.ponCentesimas(0)
            return sc

        self.txtInicio = tiempoSC(2, 40, "d", 0, 400, self.mv_inicio, 4294242784)
        self.txtFinal = tiempoSC(ancho - 6 - 68, 40, "i", -400, 0, self.mv_final, 4294242784)
        self.txtActual = tiempoSC(68 + 2, 10, "a", 0, 400, None, 4294242784)
        self.txtDuracion = tiempoSC(236, 78, None, 0, 0, None, 4289509046)

        tf = BoardTypes.Caja()
        tf.physical_pos.orden = 2
        tf.physical_pos.x = 70
        tf.physical_pos.y = 44
        tf.physical_pos.ancho = 400
        tf.physical_pos.alto = 4
        tf.grosor = 0
        tf.colorRelleno = 4281413888
        self.linMain = BoardElements.CajaSC(self.escena, tf)

        tf = BoardTypes.Caja()
        tf.physical_pos.orden = 2
        tf.physical_pos.x = 70
        tf.physical_pos.y = 32
        tf.physical_pos.ancho = 0
        tf.physical_pos.alto = 26
        tf.colorRelleno = 4281413888
        BoardElements.CajaSC(self.escena, tf)

        tf = BoardTypes.Caja()
        tf.physical_pos.orden = 2
        tf.physical_pos.x = 470
        tf.physical_pos.y = 32
        tf.physical_pos.ancho = 0
        tf.physical_pos.alto = 26
        tf.colorRelleno = 4281413888
        BoardElements.CajaSC(self.escena, tf)

        self.setFixedSize(ancho, alto)

    def mv_inicio(self, posx):
        self.txtFinal.minimo = self.txtFinal.inicialx - 400 + posx
        self.txtActual.minimo = self.txtActual.inicialx + posx
        self.txtActual.compruebaPos()

        self.txtDuracion.ponCentesimas(self.txtFinal.calcCentesimas() - self.txtInicio.calcCentesimas())

    def mv_final(self, posx):
        self.txtInicio.maximo = self.txtInicio.inicialx + 400 + posx
        self.txtActual.maximo = self.txtActual.inicialx + 400 + posx
        self.txtActual.compruebaPos()

        self.txtDuracion.ponCentesimas(self.txtFinal.calcCentesimas() - self.txtInicio.calcCentesimas())

    def ponCentesimas(self, centesimas):
        for x in (self.txtActual, self.txtDuracion, self.txtFinal, self.txtInicio):
            x.ponCentesimas(centesimas)
            if centesimas == 0:
                x.posInicial()
        self.escena.update()

    def ponCentesimasActual(self, centesimas):
        self.txtActual.setphysical_pos(centesimas)
        self.escena.update()

    def limites(self):
        to_sq = self.txtFinal.calcCentesimas()
        from_sq = self.txtActual.calcCentesimas()
        return from_sq, to_sq

    def siHayQueRecortar(self):
        return self.txtInicio.siMovido() or self.txtFinal.siMovido()

    def activaEdicion(self, siActivar):
        for x in (self.txtActual, self.txtFinal, self.txtInicio):
            x.activa(siActivar)


class WEdicionSonido(LCDialog.LCDialog):
    (
        ks_aceptar,
        ks_cancelar,
        ks_microfono,
        ks_wav,
        ks_play,
        ks_stopplay,
        ks_stopmic,
        ks_record,
        ks_cancelmic,
        ks_limpiar,
        ks_grabar,
    ) = range(11)

    def __init__(self, owner, titulo, wav=None, maxTime=None, name=None):

        # titulo = _("Sound edition" )
        icono = Iconos.S_Play()
        extparam = "sound"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.confich = Code.configuration.ficheroDirSound

        # toolbar
        self.tb = QtWidgets.QToolBar("BASIC", self)
        self.tb.setIconSize(QtCore.QSize(32, 32))
        self.tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.prepare_toolbar()

        # Nombre
        siNombre = name is not None
        if siNombre:
            lbNom = Controles.LB(self, _("Name") + ":")
            self.edNom = Controles.ED(self, name).anchoMinimo(180)
            lyNom = Colocacion.H().control(lbNom).control(self.edNom).relleno()

        # MesaSonido
        self.mesa = MesaSonido(self)
        self.taller = Sound.TallerSonido(self, wav)

        self.mesa.ponCentesimas(self.taller.centesimas)

        self.siGrabando = False
        self.is_canceled = False

        self.maxTime = maxTime if maxTime else 300.0  # seconds=5 minutos

        layout = Colocacion.V().control(self.tb)
        if siNombre:
            layout.otro(lyNom)
        layout.control(self.mesa).margen(3)

        self.setLayout(layout)

        self.ponBaseTB()

        self.restore_video(siTam=False)

    def name(self):  # Para los guiones
        return self.edNom.texto()

    def closeEvent(self, event):  # Cierre con X
        self.siGrabando = False
        self.is_canceled = True
        self.save_video()

    def ponBaseTB(self):
        li = [self.ks_aceptar, self.ks_cancelar, None]
        if self.taller.with_data():
            li.extend([self.ks_limpiar, None, self.ks_play, None, self.ks_grabar])
            self.mesa.activaEdicion(True)
        else:
            li.extend([self.ks_microfono, None, self.ks_wav])
            self.mesa.activaEdicion(False)
        self.pon_toolbar(li)

    def prepare_toolbar(self):
        self.dic_toolbar = {}

        li_options = (
            (_("Accept"), Iconos.S_Aceptar(), self.ks_aceptar),
            (_("Cancel"), Iconos.S_Cancelar(), self.ks_cancelar),
            (_("Recording Mic"), Iconos.S_Microfono(), self.ks_microfono),
            (_("Read wav"), Iconos.S_LeerWav(), self.ks_wav),
            (_("Listen"), Iconos.S_Play(), self.ks_play),
            (_("End"), Iconos.S_StopPlay(), self.ks_stopplay),
            (_("End"), Iconos.S_StopMicrofono(), self.ks_stopmic),
            (_("Begin"), Iconos.S_Record(), self.ks_record),
            (_("Cancel"), Iconos.S_Cancelar(), self.ks_cancelmic),
            (_("Remove"), Iconos.S_Limpiar(), self.ks_limpiar),
            (_("Save wav"), Iconos.Grabar(), self.ks_grabar),
        )

        for titulo, icono, key in li_options:
            accion = QtWidgets.QAction(titulo, None)
            accion.setIcon(icono)
            accion.setIconText(titulo)
            accion.triggered.connect(self.procesaTB)
            accion.key = key
            self.dic_toolbar[key] = accion

    def pon_toolbar(self, li_acciones):

        self.tb.clear()
        for k in li_acciones:
            if k is None:
                self.tb.addSeparator()
            else:
                self.dic_toolbar[k].setVisible(True)
                self.dic_toolbar[k].setEnabled(True)
                self.tb.addAction(self.dic_toolbar[k])

        self.tb.li_acciones = li_acciones
        self.tb.update()

    def habilitaTB(self, kopcion, siHabilitar):
        self.dic_toolbar[kopcion].setEnabled(siHabilitar)

    def procesaTB(self):
        accion = self.sender().key
        if accion == self.ks_aceptar:
            self.is_canceled = True
            if self.mesa.siHayQueRecortar():
                from_sq, to_sq = self.mesa.limites()
                self.taller.recorta(from_sq, to_sq)
            self.wav = self.taller.wav
            self.centesimas = self.taller.centesimas
            self.accept()
            self.save_video()
            return
        elif accion == self.ks_cancelar:
            self.reject()
            return

        elif accion == self.ks_limpiar:
            self.reset_to_0()

        elif accion == self.ks_microfono:
            self.microfono()
        elif accion == self.ks_cancelmic:
            self.siGrabando = False
            self.is_canceled = True
            self.ponBaseTB()

        elif accion == self.ks_record:
            self.micRecord()
        elif accion == self.ks_stopmic:
            self.siGrabando = False
        elif accion == self.ks_wav:
            self.wav()
        elif accion == self.ks_grabar:
            self.grabar()
        elif accion == self.ks_play:
            self.play()
        elif accion == self.ks_stopplay:
            self.siPlay = False

    def microfono(self):
        self.pon_toolbar((self.ks_cancelmic, None, self.ks_record))

    def micRecord(self):
        self.pon_toolbar((self.ks_cancelmic, None, self.ks_stopmic))
        self.siGrabando = True
        self.is_canceled = False

        self.mesa.ponCentesimas(0)

        self.taller.mic_start(self)

        iniTime = time.time()

        while self.siGrabando:
            self.taller.mic_record()
            QTUtil.refresh_gui()
            t = time.time() - iniTime
            self.mesa.ponCentesimas(t * 100)
            if t > self.maxTime:
                break

        self.siGrabando = False
        self.taller.mic_end()
        if self.is_canceled:
            self.taller.reset_to_0()
            self.mesa.ponCentesimas(0)
        else:
            self.mesa.ponCentesimas(self.taller.centesimas)

        self.ponBaseTB()

    def reset_to_0(self):
        self.taller.reset_to_0()
        self.mesa.ponCentesimas(0)
        self.ponBaseTB()

    def wav(self):
        carpeta = Util.restore_pickle(self.confich)
        file = SelectFiles.leeFichero(self, carpeta, "wav")
        if file:
            carpeta = os.path.dirname(file)
            Util.save_pickle(self.confich, carpeta)
            if self.taller.read_wav_from_disk(file):
                self.mesa.ponCentesimas(self.taller.centesimas)
            else:
                QTUtil2.message_error(self, _("It is impossible to read this file, it is not compatible."))
            self.ponBaseTB()

    def grabar(self):
        carpeta = Util.restore_pickle(self.confich)
        file = SelectFiles.salvaFichero(self, _("Save wav"), carpeta, "wav", True)
        if file:
            if not file.lower().endswith(".wav"):
                file = file + ".wav"
            carpeta = os.path.dirname(file)
            Util.save_pickle(self.confich, carpeta)
            with open(file, "wb") as q:
                q.write(self.taller.wav)
            self.ponBaseTB()

    def play(self):
        self.mesa.activaEdicion(False)
        self.pon_toolbar((self.ks_stopplay,))

        centDesde, centHasta = self.mesa.limites()
        self.siPlay = True
        self.taller.play(centDesde, centHasta)

        QTUtil.refresh_gui()

        self.ponBaseTB()


def editSonido(owner, titulo, wav):
    w = WEdicionSonido(owner, titulo, wav)
    if w.exec_():
        return w.wav, w.centesimas
    else:
        return None


def db_sounds_coherent():
    rs = Code.runSound
    with UtilSQL.DictSQL(Code.configuration.file_sounds(), "general") as db:
        for key in db.keys():
            path_wav = rs.path_wav(key)
            if not Util.exist_file(path_wav):
                Code.runSound.save_wav(key, db[key])


class WSonidos(LCDialog.LCDialog):
    def __init__(self, procesador):

        self.procesador = procesador
        db_sounds_coherent()

        self.db = UtilSQL.DictSQL(procesador.configuration.file_sounds(), "general")
        self.li_sounds = self.create_soundslist()

        titulo = _("Custom sounds")
        icono = Iconos.S_Play()
        extparam = "sounds"
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        # Toolbar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Listen"), Iconos.S_Play(), self.play),
        )
        tb = QTVarios.LCTB(self, li_acciones)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SONIDO", _("Sound"), 300, align_center=True)
        o_columns.nueva("DURACION", _("Duration"), 80, align_center=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=Code.configuration.x_pgn_rowheight)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.grid.gotop()
        self.grid.setFocus()

        self.siPlay = False

        self.register_grid(self.grid)

        if not self.restore_video():
            self.resize(self.grid.anchoColumnas() + 30, 600)

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()
        self.db.close()

    def modificar(self):
        self.grid_doble_click(None, self.grid.recno(), None)

    def grid_num_datos(self, grid):
        return len(self.li_sounds)

    def grid_doble_click(self, grid, row, o_column):
        self.siPlay = False

        cl = self.li_sounds[row][0]
        if cl is None:
            return

        wav = self.db[cl]

        resp = editSonido(self, self.li_sounds[row][1], wav)
        if resp is not None:
            wav, cent = resp
            if wav is None:
                self.li_sounds[row][2] = None
                del self.db[cl]
                Code.runSound.remove_wav(cl)
            else:
                self.db[cl] = wav
                self.li_sounds[row][2] = cent
                Code.runSound.save_wav(cl, wav)
            self.grid.refresh()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        li = self.li_sounds[row]
        if key == "DURACION":
            if li[0] is None:
                return ""
            else:
                t = li[2]
                if t is None:

                    wav = self.db[li[0]]
                    if wav is None:
                        t = 0
                    else:
                        ts = Sound.TallerSonido(self, wav)
                        t = ts.centesimas
                return "%02d:%02d:%02d" % Sound.msc(t)

        else:
            return li[1]

    def play(self):
        li = self.li_sounds[self.grid.recno()]
        if li[0]:
            Code.runSound.play_key(li[0])

    def grid_color_fondo(self, grid, row, o_column):
        li = self.li_sounds[row]
        if li[0] is None:
            return QTUtil.qtColor(4294836181)
        else:
            return None

    def create_soundslist(self):
        dic_relations = Code.runSound.relations
        li_sounds = []

        def xadd(key):
            li_sounds.append([key, dic_relations[key]["NAME"], None])

        def xapart(txt):
            li_sounds.append([None, "- " + txt + " -", None])

        xadd("MC")
        xadd("ERROR")
        xadd("ZEITNOT")

        xapart(_("Results"))
        xadd("GANAMOS")
        xadd("GANARIVAL")
        xadd("TABLAS")
        xadd("TABLASREPETICION")
        xadd("TABLAS50")
        xadd("TABLASFALTAMATERIAL")
        xadd("GANAMOSTIEMPO")
        xadd("GANARIVALTIEMPO")

        xapart(_("Coordinates"))
        for c in "abcdefgh12345678":
            xadd(c)

        xapart(_("Pieces"))
        for c in "KQRBNP":
            xadd(c)

        xapart(_("Operations"))
        for c in ("O-O", "O-O-O", "=", "x", "#", "+"):
            xadd(c)

        return li_sounds
