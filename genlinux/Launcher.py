"""
Launcher.py - Módulo de inicio para Lucas Chess.
"""

# --- Importaciones de Sistema y Utilidades ---
import os
import sys
import marshal
import traceback
import pathlib
from io import BytesIO

# --- Importaciones para empaquetado (aseguran que las dependencias estén presentes) ---
# Se agrupan para mejorar la legibilidad, manteniendo todas para compatibilidad con congeladores (PyInstaller, etc.)
try:
    from stat import *
    import operator
    import atexit
    import subprocess
    import ctypes
    import glob
    import urllib.request
    import pickle
    import time
    import gc
    import encodings
    import signal
    import hashlib
    import random
    import sqlite3
    import datetime
    import zlib
    import inspect
    import collections
    import copy
    import threading
    import zipfile
    import builtins
    import math
    import gettext
    import wave
    import base64
    import shutil
    import webbrowser
    import struct
    import dataclasses
    from typing import List, Tuple

    # --- Librerías de Terceros ---
    from PIL import Image
    import sortedcontainers
    import audioop
    import psutil
    import polib
    from PySide2 import QtCore, QtGui, QtWidgets, QtSvg, QtMultimedia
    import chardet.universaldetector
    import chess
    from chess import gaviota, engine, pgn, svg
    import deep_translator, requests, urllib3, idna, certifi, bs4
except ImportError as e:
    print(f"Error: Faltan dependencias críticas: {e}")
    sys.exit(1)


def launch():
    """Localiza y ejecuta el núcleo de la aplicación (LucasR.pyc)."""
    try:
        # Resolución robusta del path
        base_dir = pathlib.Path(__file__).parent.resolve()
        pyc_filename = "LucasR.pyc"
        pyc_path = base_dir / pyc_filename

        if not pyc_path.exists():
            print(f"Error: No se encuentra el archivo crítico: {pyc_filename}")
            print(f"Buscado en: {base_dir}")
            return

        with open(pyc_path, "rb") as f:
            # Los primeros 16 bytes suelen ser el header del .pyc (magic, timestamp, size o hash)
            # Ver PEP 552 para más detalles sobre el formato actual.
            f.seek(16)
            try:
                code_obj = marshal.load(f)
            except Exception as e:
                print(f"Error al deserializar {pyc_filename}: {e}")
                return

        # Ajustamos sys.argv si es necesario para que el script hijo lo vea correctamente
        # sys.argv[0] suele ser el Launcher.py, lo dejamos o lo cambiamos a LucasR.py

        # Ejecución del objeto de código
        exec(code_obj, globals())

    except Exception:
        print("Se ha producido un error inesperado al iniciar la aplicación:")
        traceback.print_exc()


if __name__ == "__main__":
    launch()
