import collections
import datetime
import glob
import hashlib
import inspect
import os
import pickle
import random
import shutil
import time
import urllib.request
import zlib

import chardet.universaldetector
import psutil


def md5_lc(x: str) -> int:
    return int.from_bytes(hashlib.md5(x.encode()).digest(), "big") & 0xFFFFFFFFFFFFFFF


class Log:
    def __init__(self, logname):
        self.logname = logname

    def write(self, buf):
        if buf.startswith("Traceback"):
            buf = f"{today()}\n{buf}"
        with open(self.logname, "at") as ferr:
            ferr.write(buf)

    def writeln(self, buf):
        with open(self.logname, "at") as ferr:
            ferr.write(buf + "\n")

    def flush(self):
        pass  # To remove error 120 at exit


def remove_file(file: str) -> bool:
    try:
        os.remove(file)
    except:
        pass
    return not os.path.isfile(file)


def remove_folder_files(folder: str) -> bool:
    entry: os.DirEntry
    for entry in os.scandir(folder):
        if entry.is_file():
            if not remove_file(entry.path):
                return False
    try:
        os.rmdir(folder)
    except:
        pass
    return not os.path.isdir(folder)


def create_folder(carpeta: str):
    try:
        os.mkdir(carpeta)
        return True
    except:
        return False


def same_path(path1: str, path2: str) -> bool:
    return os.path.abspath(path1) == os.path.abspath(path2)


def norm_path(path):
    return os.path.abspath(path)


def filesize(file: str) -> int:
    return os.path.getsize(file) if os.path.isfile(file) else -1


def exist_file(file: str) -> bool:
    return filesize(file) >= 0 if file else False


def exist_folder(folder: str) -> bool:
    return os.path.isdir(folder) if folder else False


def file_copy(origin: str, destino: str) -> bool:
    if exist_file(origin):
        if remove_file(destino):
            shutil.copy2(origin, destino)
            return True
    return False


def file_next(folder: str, base: str, ext: str) -> str:
    n = 1
    path_ = opj(folder, "%s%s.%s" % (base, "%d", ext))
    while exist_file(path_ % n):
        n += 1
    return path_ % n


def rename_file(origin: str, destination: str) -> bool:
    if not exist_file(origin):
        return False
    origin = os.path.abspath(origin)
    destination = os.path.abspath(destination)
    if origin == destination:
        return True
    if origin.lower() == destination.lower():
        os.rename(origin, destination)
        return True
    if remove_file(destination):
        shutil.move(origin, destination)
        return True
    return False


def temporary_file(path_temp: str, ext: str) -> str:
    create_folder(path_temp)
    while True:
        fich = opj(path_temp, "%d.%s" % (random.randint(1, 999999999), ext))
        if not exist_file(fich):
            return fich


def list_vars_values(obj, li_exclude: [list, None] = None):
    if li_exclude is None:
        li_exclude = []
    li = []
    for name, value in inspect.getmembers(obj):
        if not ("__" in name) and name not in li_exclude:
            if not inspect.ismethod(value):
                li.append((name, value))
    return li


def restore_list_vars_values(obj, li_vars_values):
    for name, value in li_vars_values:
        if hasattr(obj, name):
            setattr(obj, name, value)


def save_obj_pickle(obj, li_exclude: [list, None] = None):
    li_vars_values = list_vars_values(obj, li_exclude)
    dic = {var: value for var, value in li_vars_values}
    return pickle.dumps(dic)


def restore_obj_pickle(obj, js_txt):
    dic = pickle.loads(js_txt)
    for k, v in dic.items():
        if hasattr(obj, k):
            setattr(obj, k, v)


def ini_dic(file: str) -> dict:
    dic = {}
    if os.path.isfile(file):
        with open(file, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line:
                    n = line.find("=")
                    if n:
                        key = line[:n].strip()
                        value = line[n + 1:].strip()
                        dic[key] = value
    return dic


def today():
    return datetime.datetime.now()


ORDERED_NUMBER = [random.randint(0, 99)]


def huella_num() -> str:
    ns = time.time_ns()
    if ns % 100 == 0:
        ns //= 100
    ORDERED_NUMBER[0] += 1
    txt = "%d%d" % (ns, ORDERED_NUMBER[0])
    return txt


def huella() -> str:
    def conv(num100: int) -> str:
        if num100 < 9:
            return chr(49 + num100)
        if num100 < 35:
            return chr(65 - 9 + num100)
        if num100 < 61:
            return chr(97 - 35 + num100)
        return chr(122) + conv(num100 - 61)

    txt = huella_num()
    if len(txt) % 2 == 1:
        txt += str(random.randint(0, 9))
    li = []
    for n in range(len(txt) // 2):
        num = int(txt[n * 2: n * 2 + 2])
        li.append(conv(num))
    return "".join(li)


def save_pickle(fich: str, obj) -> bool:
    with open(fich, "wb") as q:
        q.write(pickle.dumps(obj))
    return True


def restore_pickle(fich: str, default=None):
    if exist_file(fich):
        try:
            with open(fich, "rb") as f:
                return pickle.loads(f.read())
        except:
            pass
    return default


def urlretrieve(url: str, fich: str) -> bool:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
            if the_page:
                with open(fich, "wb") as q:
                    q.write(the_page)
                    return True
            return False
    except:
        return False


def var2zip(var):
    varp = pickle.dumps(var)
    return zlib.compress(varp, 5)


def zip2var(blob):
    if blob is None:
        return None
    try:
        varp = zlib.decompress(blob)
        return pickle.loads(varp)
    except:
        return None


def zip2var_change_import(blob, li_replace):
    if blob is None:
        return None
    try:
        varp = zlib.decompress(blob)
    except:
        return None
    try:
        return pickle.loads(varp)
    except:
        try:
            for replace_from, replace_to in li_replace:
                varp = varp.replace(replace_from, replace_to)
            return pickle.loads(varp)
        except:
            return None


class Record:
    pass


def var2txt(var):
    return pickle.dumps(var)


def txt2var(txt):
    return pickle.loads(txt)


def dtos(f):
    return "%04d%02d%02d" % (f.year, f.month, f.day)


def stod(txt):
    if txt and len(txt) == 8 and txt.isdigit():
        return datetime.date(int(txt[:4]), int(txt[4:6]), int(txt[6:]))
    return None


def dtosext(f):
    return "%04d%02d%02d%02d%02d%02d" % (f.year, f.month, f.day, f.hour, f.minute, f.second)


def dtostr_hm(f):
    return "%04d.%02d.%02d %02d:%02d" % (f.year, f.month, f.day, f.hour, f.minute)


def stodext(txt):
    if txt and len(txt) == 14 and txt.isdigit():
        return datetime.datetime(
            int(txt[:4]), int(txt[4:6]), int(txt[6:8]), int(txt[8:10]), int(txt[10:12]), int(txt[12:])
        )
    return None


def primera_mayuscula(txt):
    return txt[0].upper() + txt[1:].lower() if len(txt) > 0 else ""


def primeras_mayusculas(txt):
    return " ".join([primera_mayuscula(x) for x in txt.split(" ")])


def ini2dic(file):
    dic_base = collections.OrderedDict()

    if os.path.isfile(file):

        with open(file, "rt", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#"):
                    if linea.startswith("["):
                        key = linea[1:-1]
                        dic = collections.OrderedDict()
                        dic_base[key] = dic
                    else:
                        n = linea.find("=")
                        if n > 0:
                            clave1 = linea[:n].strip()
                            valor = linea[n + 1:].strip()
                            dic[clave1] = valor

    return dic_base


def dic2ini(file, dic):
    with open(file, "wt", encoding="utf-8", errors="ignore") as f:
        for k in dic:
            f.write("[%s]\n" % k)
            for key in dic[k]:
                f.write("%s=%s\n" % (key, dic[k][key]))


def ini_base2dic(file, rfind_equal=False):
    dic = {}

    if os.path.isfile(file):

        with open(file, "rt", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                linea = linea.strip()
                if linea.startswith("#"):
                    continue
                if linea:
                    n = linea.rfind("=") if rfind_equal else linea.find("=")
                    if n:
                        key = linea[:n].strip()
                        valor = linea[n + 1:].strip()
                        dic[key] = valor

    return dic


def dic2ini_base(file, dic):
    with open(file, "wt", encoding="utf-8", errors="ignore") as f:
        for k, v in dic.items():
            f.write("%s=%s\n" % (k, v))


def secs2str(s):
    m = s / 60
    s = s % 60
    h = m / 60
    m = m % 60
    return "%02d:%02d:%02d" % (h, m, s)


class ListaNumerosImpresion:
    def __init__(self, txt):
        # Formas
        # 1. <num>            1, <num>, 0
        #   2. <num>-           2, <num>, 0
        #   3. <num>-<num>      3, <num>,<num>
        #   4. -<num>           4, <num>, 0
        self.lista = []
        if txt:
            txt = txt.replace("--", "-").replace(",,", ",").replace(" ", "")

            for bloque in txt.split(","):

                if bloque.startswith("-"):
                    num = bloque[1:]
                    if num.isdigit():
                        self.lista.append((4, int(num)))

                elif bloque.endswith("-"):
                    num = bloque[:-1]
                    if num.isdigit():
                        self.lista.append((2, int(num)))

                elif "-" in bloque:
                    li = bloque.split("-")
                    if len(li) == 2:
                        num1, num2 = li
                        if num1.isdigit() and num2.isdigit():
                            i1 = int(num1)
                            i2 = int(num2)
                            if i1 <= i2:
                                self.lista.append((3, i1, i2))

                elif bloque.isdigit():
                    self.lista.append((1, int(bloque)))

    def siEsta(self, pos):
        if not self.lista:
            return True

        for patron in self.lista:
            modo = patron[0]
            i1 = patron[1]
            if modo == 1:
                if pos == i1:
                    return True
            elif modo == 2:
                if pos >= i1:
                    return True
            elif modo == 3:
                i2 = patron[2]
                if i1 <= pos <= i2:
                    return True
            elif modo == 4:
                if pos <= i1:
                    return True

        return False

    def selected(self, lista):
        return [x for x in lista if self.siEsta(x)]


class SymbolDict:
    def __init__(self, dic=None):
        self._dic = {}
        self._keys = []
        if dic:
            for k, v in dic.items():
                self.__setitem__(k, v)

    def __contains__(self, key):
        return key.upper() in self._dic

    def __len__(self):
        return len(self._keys)

    def __getitem__(self, key):
        if type(key) == int:
            return self._keys[key]
        return self._dic[key.upper()]

    def __setitem__(self, key, valor):
        clu = key.upper()
        if not (clu in self._dic):
            self._keys.append(key)
        self._dic[clu] = valor

    def get(self, key, default=None):
        clu = key.upper()
        if not (clu in self._dic):
            return default
        return self.__getitem__(key)

    def items(self):
        for k in self._keys:
            yield k, self.__getitem__(k)

    def keys(self):
        return self._keys[:]

    def __str__(self):
        x = ""
        for t in self._keys:
            x += "[%s]=[%s]\n" % (t, str(self.__getitem__(t)))
        return x.strip()


class Rondo:
    def __init__(self, *lista):
        self.pos = -1
        self.lista = lista
        self.tope = len(self.lista)

    def shuffle(self):
        li = list(self.lista)
        random.shuffle(li)
        self.lista = li

    def otro(self):
        self.pos += 1
        if self.pos == self.tope:
            self.pos = 0
        return self.lista[self.pos]

    def reset(self):
        self.pos = -1


def valid_filename(name):
    name = name.strip()
    nom = []
    for x in name:
        if x in '\\:/|?*^%><(),;"' or ord(x) < 32:
            x = "_"
        nom.append(x)
    name = "".join(nom)
    li_invalid = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]
    if name.upper() in li_invalid:
        name = "__%s__" % name
    if "." in name:
        if name[: name.find(".")].upper() in li_invalid:
            name = "__%s__" % name
    return name


def asciiNomFichero(name):
    name = valid_filename(name)
    li = []
    for x in name:
        if not (31 < ord(x) < 127):
            li.append("_")
        else:
            li.append(x)
    name = "".join(li)
    while "__" in name:
        name = name.replace("__", "_")
    return name


def datefile(pathfile):
    try:
        mtime = os.path.getmtime(pathfile)
        return datetime.datetime.fromtimestamp(mtime)
    except:
        return None


def fideELO(eloJugador, eloRival, resultado):
    if resultado == +1:
        resultado = 1.0
    elif resultado == 0:
        resultado = 0.5
    else:
        resultado = 0.0
    if eloJugador <= 1200:
        k = 40.0
    elif eloJugador <= 2100:
        k = 32.0
    elif eloRival < 2400:
        k = 24.0
    else:
        k = 16.0
    probabilidad = 1.0 / (1.0 + (10.0 ** ((eloRival - eloJugador) / 400.0)))
    return int(k * (resultado - probabilidad))


date_format = ["%Y.%m.%d"]


def localDate(date):
    return date.strftime(date_format[0])


def localDateT(date):
    return "%s %02d:%02d" % (date.strftime(date_format[0]), date.hour, date.minute)


def listfiles(*lista):
    f = lista[0]
    if len(lista) > 1:
        for x in lista[1:]:
            f = opj(f, x)
    return glob.glob(f)


def listdir(txt):
    return os.scandir(txt)


class OpenCodec:
    def __init__(self, path, modo=None):
        with open(path, "rb") as f:
            u = chardet.universaldetector.UniversalDetector()
            u.feed(f.read(1024))
            u.close()
            encoding = u.result.get("encoding", "utf-8")
        if modo is None:
            modo = "rt"
        self.f = open(path, modo, encoding=encoding, errors="ignore")

    def __enter__(self):
        return self.f

    def __exit__(self, xtype, value, traceback):
        self.f.close()


def txt_encoding(btxt):
    u = chardet.universaldetector.UniversalDetector()
    u.feed(btxt)
    u.close()
    return u.result.get("encoding", "utf-8")


def bytes_str_codec(btxt):
    u = chardet.universaldetector.UniversalDetector()
    u.feed(btxt)
    u.close()
    codec = u.result.get("encoding", "utf-8")
    return btxt.decode(codec), codec


def file_encoding(fich, chunk=30000):
    with open(fich, "rb") as f:
        bt = f.read(chunk)
        if 195 in bt:
            return "utf-8"
        u = chardet.universaldetector.UniversalDetector()
        u.feed(bt)
        u.close()
        codec = u.result.get("encoding", "utf-8")
        if codec == "ascii":
            codec = "latin-1"
        return codec


class Decode:
    def __init__(self, codec=None):
        self.codec = "utf-8" if codec is None else codec

    def read_file(self, file):
        self.codec = file_encoding(file)

    def decode(self, xbytes):
        try:
            resp = xbytes.decode(self.codec, "ignore")
        except:
            u = chardet.universaldetector.UniversalDetector()
            u.feed(xbytes)
            u.close()
            codec = u.result.get("encoding", "utf-8")
            resp = xbytes.decode(codec, "ignore")
        return resp


def path_split(path):
    path = os.path.realpath(path)
    return path.split(os.sep)


def relative_path(*args):
    n_args = len(args)
    if n_args == 1:
        path = args[0]
    else:
        path = opj(args[0], args[1])
        if n_args > 2:
            for x in range(2, n_args):
                path = opj(path, args[x])
    try:
        path = os.path.abspath(path)
        rel = os.path.relpath(path)
        if not rel.startswith(".."):
            path = rel
    except ValueError:
        pass

    return path


def filename_unique(destination: str):
    if os.path.isfile(destination):
        n = destination.rfind(".")
        if n == -1:
            ext = ""
        else:
            ext = destination[n:]
            destination = destination[:n]
        n = 1
        if destination.endswith("-1"):
            destination = destination[:-2]
            n = 2
        while True:
            fich = destination + "-%d%s" % (n, ext)
            n += 1
            if not os.path.isfile(fich):
                return fich
    return destination


def memory_python():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def unique_list(lista):
    st = set()
    li = []
    for x in lista:
        if x not in st:
            li.append(x)
            st.add(x)
    return li


def div_list(xlist, max_group):
    nlist = len(xlist)
    xfrom = 0
    li_groups = []
    while xfrom < nlist:
        li_groups.append(xlist[xfrom: xfrom + max_group])
        xfrom += max_group
    return li_groups


def cpu_count():
    return psutil.cpu_count()


def opj(*elem) -> str:
    return str(os.path.join(*elem))


def fen_fen64(fen):
    fen = fen.split(" ")[0]
    li = []
    for line in fen.split("/"):
        ln = []
        for c in line:
            if c.isdigit():
                ln.append(" " * int(c))
            else:
                ln.append(c)
        li.append("".join(ln))
    return "".join(li)
