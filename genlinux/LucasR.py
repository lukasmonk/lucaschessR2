from stat import *
import sys
import operator
import atexit
import subprocess
import ctypes
import glob
import urllib.request
import pickle
import os
import traceback
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
from typing import List, Tuple
import webbrowser
import struct
import dataclasses
from io import BytesIO

from PIL import Image
import sortedcontainers
import audioop
import psutil
import polib
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg, QtMultimedia
import chardet.universaldetector
import chess
from chess import gaviota, engine, pgn, svg
import deep_translator,requests,urllib3,idna,certifi,bs4

import uuid
import runpy
import sys
from pathlib import Path


def run_pyc(filepath: str) -> None:
    """Ejecuta un archivo .pyc como si fuese el script principal."""
    pyc_path = Path(filepath)

    sys.argv = [str(filepath)] + sys.argv[1:]  # pasa los parámetros recibidos
    runpy.run_path(str(pyc_path), run_name="__main__")


if __name__ == "__main__":
    run_pyc("LucasR.pyc")
