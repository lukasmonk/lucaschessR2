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

import marshal

code = open('LucasR.pyc', 'rb')
code.seek(16)  # To pass the first sixteen bytes
LucasR = marshal.load(code)
exec(LucasR)
