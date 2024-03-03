import os
import shutil
import py_compile


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


class Processor:
    def __init__(self):
        self.destino = os.path.realpath("./LucasChessR")
        self.origen = os.path.realpath("..")

    def read_version(self):
        with open(os.path.join(self.origen, "bin", "Code", "__init__.py")) as f:
            ok = True
            for linea in f:
                if "VERSION" in linea:
                    version = linea.strip().split("=")[1].split('"')[1].strip()
                elif "DEBUG" in linea:
                    if "True" in linea:
                        input("Debug está a True")
                        ok = False
        if not ok:
            import sys

            sys.exit()
        self.version = version
        print("Reading versión", version)

    def remove_old(self):
        print("Removing old")
        shutil.rmtree(self.destino, ignore_errors=True)
        os.mkdir(self.destino)

    def copy_folder(self, carpeta):
        print("Copying folder", carpeta)
        origen = os.path.join(self.origen, carpeta)
        destino = os.path.join(self.destino, carpeta)
        shutil.copytree(origen, destino)

    def remove_fastercode(self):
        print("Removing _fastercode")
        fastercode = os.path.join(self.destino, "bin", "_fastercode")
        shutil.rmtree(fastercode)

    def remove_genicons(self):
        print("Removing _genicons")
        genicons = os.path.join(self.destino, "bin", "_genicons")
        shutil.rmtree(genicons)

    def remove_win32(self):
        print("Removing win32")
        folder = os.path.join(self.destino, "bin", "OS", "win32")
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    @staticmethod
    def extension(fich):
        p = fich.rfind(".")
        return "" if p < 0 else fich[p + 1 :]

    def clean_bin(self):
        print("Cleaning bin")

        def haz(carpeta):
            for fich in os.listdir(carpeta):
                path = os.path.join(carpeta, fich)
                if os.path.isdir(path):
                    haz(path)
                    if fich == "__pycache__":
                        os.rmdir(path)
                else:
                    extension = self.extension(fich)
                    if extension == "pyc":
                        os.remove(path)

        bin = os.path.join(self.destino, "bin")
        haz(bin)

        li_entry = [entry for entry in os.scandir(bin)]
        for entry in li_entry:
            if entry.is_file() and self.extension(entry.name) != "py":
                os.remove(entry.path)

    def copy_template(self):
        print("Copying template")
        py = os.path.join("Files", "bin")
        copytree(py, os.path.join(self.destino, "bin"))

    def set_bug(self):
        with open(os.path.join(self.destino, "bin", "bug.log"), "wt") as f:
            f.write("Version %s\n" % self.version)

    def copy_root(self):
        for entry in os.scandir("Files"):
            if entry.is_file():
                shutil.copy(entry.path, self.destino)

    def compile_file(self, path):
        pyc = path + "c"
        py_compile.compile(path, pyc)
        os.remove(path)

    def compila(self, folder):
        for fich in os.listdir(folder):
            path = os.path.join(folder, fich)
            if os.path.isdir(path):
                self.compila(path)
            elif path.endswith(".py"):
                self.compile_file(path)

    def compile_bin(self):
        print("Compiling")
        bin = os.path.join(self.destino, "bin", "Code")
        self.compila(bin)
        bin = os.path.join(self.destino, "bin", "OS")
        self.compila(bin)

    def lucasr(self):
        destino = os.path.join(self.destino, "bin", "LucasR.py")
        self.compile_file(destino)

    def move_libs_eboards(self):
        destino = os.path.join(self.destino, "bin")
        origen = os.path.join(self.destino, "bin", "OS", "linux", "DigitalBoards")
        for entry in os.scandir(origen):
            if entry.name.startswith("libQt5"):
                shutil.move(entry.path, destino)

    def crea_pendiente_stockfish(self):
        folder = os.path.join(self.destino, "bin", "OS", "linux", "Engines", "stockfish")

        try:
            # Es mejor que existan, por si hay una tecleada rápida
            path64 = os.path.join(folder, "stockfish-16.1-64")
            if os.path.isfile(path64):
                os.remove(path64)
            path64_other = os.path.join(folder, "stockfish-16.1-x86-64")

            shutil.copy(path64_other, path64)

        except OSError:
            input("Comprobar version de Stockfish")

    def calc_files_dic(self):
        dic_files = {}

        def check_folder(folder):
            entry: os.DirEntry
            for entry in os.scandir(folder):
                if entry.is_file():
                    path = os.path.relpath(entry.path, self.destino)
                    dic_files[path] = entry.stat().st_size
                elif entry.is_dir():
                    check_folder(entry.path)

        check_folder(self.destino)
        with open(os.path.join(self.destino, "dic_files.txt"), "wt") as q:
            q.write(str(dic_files))

    def create_shs(self):
        with open(os.path.join(self.destino, "setup_linux.sh"), "wt") as q:
            q.write(
                """QT_LOGGING_RULES='*=falrose'
export QT_LOGGING_RULES
if [ $(id -u) -eq 0 ]
then
    echo
    echo "PROBLEM: INSTALLING AS ROOT"
    echo
    echo "It is advisable that you install LucasChess as a normal user and not as root."
    read -e -p "Do you wish to continue installing? (yn) " yn
    if [[ "$yn" != "y" ]]
    then
        echo
        echo "....exiting...."
        echo
        exit
    fi
fi
cd bin
./setup_linux
"""
            )
        with open(os.path.join(self.destino, "LucasR.sh"), "wt") as q:
            q.write(
                """QT_LOGGING_RULES='*=false'
export QT_LOGGING_RULES
cd bin
./LucasR
"""
            )

    def set_permissions(self):
        perms = 0o755
        os.chmod(os.path.join(self.destino, "LucasR.sh"), perms)
        os.chmod(os.path.join(self.destino, "bin", "LucasR"), perms)
        os.chmod(os.path.join(self.destino, "setup_linux.sh"), perms)
        os.chmod(os.path.join(self.destino, "bin", "setup_linux"), perms)

    def write_version(self):
        with open(os.path.join(self.destino, "version.txt"), "wt") as q:
            q.write(self.version)


def gen_installer():
    xf = Processor()
    xf.read_version()
    xf.remove_old()
    xf.copy_folder("bin")
    xf.copy_folder("Resources")
    xf.remove_fastercode()
    xf.remove_genicons()
    xf.remove_win32()
    xf.clean_bin()
    xf.compile_bin()
    xf.set_bug()
    xf.copy_root()
    xf.lucasr()
    xf.move_libs_eboards()

    xf.copy_template()

    xf.crea_pendiente_stockfish()

    xf.calc_files_dic()

    xf.create_shs()
    xf.set_permissions()

    xf.write_version()


gen_installer()
