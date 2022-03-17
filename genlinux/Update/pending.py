import shutil
import os
import time

origen = os.path.join(folder_root, "bin", "FasterCode.cpython-38-x86_64-linux-gnu.so")
destino = os.path.join(folder_OS, "FasterCode.cpython-38-x86_64-linux-gnu.so")
time.sleep(3.0) # que de tiempo a cerrar run previa
os.remove(destino)
shutil.move(origen, destino)
