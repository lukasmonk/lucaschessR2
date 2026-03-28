from __future__ import annotations

import importlib
import subprocess
import sys
import types
from pathlib import Path


def install() -> None:
    try:
        import PySide2  # noqa: F401
    except ModuleNotFoundError:
        _install_pyqt5_compat()


def ensure_fastercode() -> None:
    if sys.platform != "darwin":
        return

    platform_dir = Path(__file__).resolve().parent / "OS" / "darwin"
    if _can_import_fastercode(platform_dir):
        return

    build_script = Path(__file__).resolve().parent / "_fastercode" / "build_macos.sh"
    if not build_script.is_file():
        raise RuntimeError("Lucas Chess macOS runtime is incomplete: FasterCode build script is missing.")

    try:
        subprocess.run(
            [str(build_script), sys.executable],
            check=True,
            cwd=str(build_script.parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Lucas Chess could not build FasterCode for this macOS runtime. Run setup_macos.command first."
        ) from exc

    if not _can_import_fastercode(platform_dir):
        raise RuntimeError(
            "Lucas Chess could not load FasterCode for this macOS runtime. Run setup_macos.command first."
        )


def _can_import_fastercode(platform_dir: Path) -> bool:
    if not platform_dir.is_dir():
        return False

    platform_path = str(platform_dir)
    sys.path.insert(0, platform_path)
    try:
        importlib.import_module("FasterCode")
        return True
    except (ImportError, OSError):
        sys.modules.pop("FasterCode", None)
        return False
    finally:
        try:
            sys.path.remove(platform_path)
        except ValueError:
            pass


def _install_pyqt5_compat() -> None:
    try:
        from PyQt5 import QtCore, QtGui, QtMultimedia, QtSvg, QtWidgets, sip
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Lucas Chess requires PySide2 or PyQt5. Run setup_macos.command to install the runtime."
        ) from exc

    if not hasattr(QtCore, "Signal"):
        QtCore.Signal = QtCore.pyqtSignal
    if not hasattr(QtCore, "Slot"):
        QtCore.Slot = QtCore.pyqtSlot
    if not hasattr(QtCore, "Property"):
        QtCore.Property = QtCore.pyqtProperty

    package = types.ModuleType("PySide2")
    package.__path__ = []
    package.QtCore = QtCore
    package.QtGui = QtGui
    package.QtWidgets = QtWidgets
    package.QtSvg = QtSvg
    package.QtMultimedia = QtMultimedia

    shiboken2 = types.ModuleType("shiboken2")

    def is_valid(obj) -> bool:
        return not sip.isdeleted(obj)

    shiboken2.isValid = is_valid

    sys.modules["PySide2"] = package
    sys.modules["PySide2.QtCore"] = QtCore
    sys.modules["PySide2.QtGui"] = QtGui
    sys.modules["PySide2.QtWidgets"] = QtWidgets
    sys.modules["PySide2.QtSvg"] = QtSvg
    sys.modules["PySide2.QtMultimedia"] = QtMultimedia
    sys.modules["shiboken2"] = shiboken2
