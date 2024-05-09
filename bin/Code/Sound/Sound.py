import audioop
import os
import time
import wave
import queue
from io import BytesIO

from PySide2 import QtCore, QtMultimedia
from PySide2.QtMultimedia import QAudioDeviceInfo, QAudioFormat, QAudioInput, QSound
import Code
from Code import Util
from Code.QT import QTUtil
from Code.SQL import UtilSQL
from Code.Translations import TrListas

DATABASE = "D"
PLAY_ESPERA = "P"
PLAY_SINESPERA = "N"
STOP = "S"
TERMINAR = "T"


class RunSound:
    def __init__(self):
        Code.runSound = self
        self.replay = None
        self.replayBeep = None
        self.replayError = None
        self.dic_sounds = {}

        self.queue = queue.Queue()
        self.current = None

        self.working = False

    def siguiente(self):
        if not self.queue.empty():
            if self.current and not self.current.isFinished():
                QtCore.QTimer.singleShot(100, self.siguiente)
                return
            key = self.queue.get()
            self.current, mseconds = self.dic_sounds[key]
            self.current.play()
            if not self.queue.empty():
                QtCore.QTimer.singleShot(mseconds, self.siguiente)
                return

    def play_key(self, key, start=True):
        played = False
        if key not in self.dic_sounds:
            name_wav = self.relations[key]["WAV_KEY"] + ".wav"
            path_wav = Util.opj(Code.configuration.folder_sounds(), name_wav)
            if os.path.isfile(path_wav):
                wf = wave.open(path_wav)
                seconds = 1000.0 * wf.getnframes() / wf.getframerate()
                wf.close()
                qsound = QtMultimedia.QSound(path_wav)
                self.dic_sounds[key] = (qsound, seconds)
                played = True
            else:
                self.dic_sounds[key] = (None, 0)
                return False
        else:
            seconds = self.dic_sounds[key][1]

        if seconds > 0:
            self.queue.put(key)
            if start:
                self.siguiente()
        return played

    def write_sounds(self):
        configuration = Code.configuration
        folder_sounds = configuration.folder_sounds()

        if not Util.create_folder(folder_sounds):
            for key in self.relations:
                wav = self.relations[key]["WAV_KEY"] + ".wav"
                path_wav = Util.opj(folder_sounds, wav)
                if os.path.isfile(path_wav):
                    os.remove(path_wav)

        db = UtilSQL.DictSQL(configuration.file_sounds(), "general")
        for key in db.keys():
            wav = self.relations[key]["WAV_KEY"] + ".wav"
            path_wav = Util.opj(folder_sounds, wav)
            with open(path_wav, "wb") as q:
                q.write(db[key])
        db.close()

    def save_wav(self, key, wav):
        folder_sounds = Code.configuration.folder_sounds()
        path_wav = Util.opj(folder_sounds, self.relations[key]["WAV_KEY"] + ".wav")
        with open(path_wav, "wb") as q:
            q.write(wav)

    def remove_wav(self, key):
        folder_sounds = Code.configuration.folder_sounds()
        path_wav = Util.opj(folder_sounds, self.relations[key]["WAV_KEY"] + ".wav")
        Util.remove_file(path_wav)

    def path_wav(self, key):
        folder_sounds = Code.configuration.folder_sounds()
        return Util.opj(folder_sounds, self.relations[key]["WAV_KEY"] + ".wav")

    def read_sounds(self):
        configuration = Code.configuration
        folder_sounds = configuration.folder_sounds()

        if not os.path.isdir(folder_sounds):
            self.write_sounds()

    def close(self):
        self.working = False
        if self.current:
            self.current.stop()
        self.queue = queue.Queue()

    def play_list(self, li):
        for key in li:
            self.play_key(key, False)
        if self.queue:
            self.working = True
            self.siguiente()
            return True
        return False

    def playZeitnot(self):
        self.play_key("ZEITNOT")

    def playError(self):
        self.play_key("ERROR")
        if self.dic_sounds["ERROR"][0] is None:
            QTUtil.beep()

    def playBeep(self):
        self.play_key("MC")
        if self.dic_sounds["MC"][0] is None:
            QTUtil.beep()

    @property
    def relations(self):
        dic = {}

        def add(key, txt, wav_key):
            dic[key] = {"NAME": txt, "WAV_KEY": key if wav_key is None else wav_key}

        add("MC", _("Beep after move"), "BEEP")
        add("ERROR", _("Error"), "ERROR")
        add("ZEITNOT", _("Zeitnot"), "ZEITNOT")

        add("GANAMOS", _("You win"), "WIN")
        add("GANARIVAL", _("Opponent wins"), "LOST")
        add("TABLAS", _("Stalemate"), "STALEMATE")
        add("TABLASREPETICION", _("Draw by threefold repetition"), "DRAW_THREEFOLD")
        add("TABLAS50", _("Draw by fifty-move rule"), "DRAW_FIFTYRULE")
        add("TABLASFALTAMATERIAL", _("Draw by insufficient material"), "DRAW_MATERIAL")
        add("GANAMOSTIEMPO", _("You win on time"), "WIN_TIME")
        add("GANARIVALTIEMPO", _("Opponent has won on time"), "LOST_TIME")

        for c in "abcdefgh12345678":
            add(c, c, "COORD_" + c)

        d = TrListas.dic_nom_pieces()
        for c in "KQRBNP":
            add(c, d[c], "PIECE_" + c)

        add("O-O", _("Short castling"), "SHORT_CASTLING")
        add("O-O-O", _("Long castling"), "LONG_CASTLING")
        add("=", _("Promote to"), "PROMOTE_TO")
        add("x", _("Capture"), "CAPTURE")
        add("+", _("Check"), "CHECK")
        add("#", _("Checkmate"), "CHECKMATE")

        return dic


def msc(centesimas):
    t = centesimas
    cent = t % 100
    t //= 100
    mins = t // 60
    t -= mins * 60
    seg = t
    return mins, seg, cent


class TallerSonido:
    FORMAT = 16
    CHANNELS = 2
    SAMPLE_RATE = 22500

    def __init__(self, owner, wav):
        self.wav = wav

        self.owner = owner

        if not wav:
            self.centesimas = 0
        else:
            f = BytesIO(self.wav)

            wf = wave.open(f)
            self.centesimas = int(round(100.0 * wf.getnframes() / wf.getframerate(), 0))
            wf.close()

    def with_data(self):
        return self.wav is not None

    def reset_to_0(self):
        self.wav = None
        self.centesimas = 0

    def mic_start(self, owner):
        device = QAudioDeviceInfo.defaultInputDevice()
        if device.isNull():
            return False

        format_audio = QAudioFormat()
        format_audio.setSampleRate(self.SAMPLE_RATE)
        format_audio.setChannelCount(self.CHANNELS)
        format_audio.setSampleSize(self.FORMAT)
        format_audio.setCodec("audio/pcm")
        format_audio.setByteOrder(QAudioFormat.LittleEndian)
        format_audio.setSampleType(QAudioFormat.UnSignedInt)

        self.datos = []
        self.audio_input = QAudioInput(device, format_audio, owner)
        self.ioDevice = self.audio_input.start()
        self.ioDevice.readyRead.connect(self.mic_record)

    def mic_record(self):
        self.datos.append(self.ioDevice.readAll())

    def mic_end(self):
        self.audio_input.stop()

        resp = b"".join(self.datos)
        tx = audioop.lin2alaw(resp, 2)
        frames = audioop.alaw2lin(tx, 2)
        io = BytesIO()
        wf = wave.open(io, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.FORMAT // 8)
        wf.setframerate(self.SAMPLE_RATE)
        wf.writeframes(frames)
        self.wav = io.getvalue()
        self.centesimas = round(100.0 * wf.getnframes() / wf.getframerate(), 0)
        wf.close()

    def read_wav_from_disk(self, file):
        try:
            wf = wave.open(file, "rb")
            self.centesimas = round(100.0 * wf.getnframes() / wf.getframerate(), 0)
            wf.close()
            f = open(file, "rb")
            self.wav = f.read()
            f.close()
            return True
        except:
            self.wav = None
            self.centesimas = 0
            return False

    def play(self, cent_desde, cent_hasta):
        io_wav = self.io_wav(cent_desde, cent_hasta)
        path_wav = Code.configuration.ficheroTemporal("wav")
        with open(path_wav, "wb") as q:
            q.write(io_wav)
        self.qsound = QSound(path_wav)
        self.qsound.play()

        self.cent_desde = cent_desde
        self.cent_hasta = cent_hasta
        self.ini_time = time.time()
        self.playing()

    def playing(self):
        if self.owner.is_canceled:
            return
        t1 = time.time()
        centesimas = (t1 - self.ini_time) * 100 + self.cent_desde
        try:
            if centesimas >= self.cent_hasta:
                centesimas = self.cent_desde
            self.owner.mesa.ponCentesimasActual(centesimas)
            QTUtil.refresh_gui()
            if not self.owner.siPlay:
                self.qsound.stop()
            elif not self.qsound.isFinished():
                QtCore.QTimer.singleShot(100, self.playing)
        except RuntimeError:
            self.qsound.stop()

    def io_wav(self, centDesde, centHasta):
        f = BytesIO(self.wav)

        wf = wave.open(f, "rb")
        nchannels, sampwidth, framerate, nframes, comptype, compname = wf.getparams()

        kfc = 1.0 * wf.getframerate() / 100.0  # n. de frames por cada centesima
        minFrame = int(kfc * centDesde)
        maxFrame = int(kfc * centHasta)

        wf.setpos(minFrame)
        frames = wf.readframes(maxFrame - minFrame)
        wf.close()

        io = BytesIO()
        wf = wave.open(io, "wb")
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(frames)
        data = io.getvalue()
        wf.close()

        return data

    def recorta(self, centDesde, centHasta):
        self.wav = self.io_wav(centDesde, centHasta)
        self.centesimas = centHasta - centDesde
