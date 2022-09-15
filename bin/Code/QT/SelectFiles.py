import os

from PySide2 import QtWidgets
import Code
from Code.QT import SelectFilesLC


def select_pgn(wowner):
    configuration = Code.configuration
    path = leeFichero(wowner, configuration.pgn_folder(), "pgn")
    if path:
        carpeta, file = os.path.split(path)
        configuration.save_pgn_folder(carpeta)
    return path


def select_pgns(wowner):
    configuration = Code.configuration
    files = leeFicheros(wowner, configuration.pgn_folder(), "pgn")
    if files:
        path = files[0]
        carpeta, file = os.path.split(path)
        configuration.save_pgn_folder(carpeta)
    return files


def get_existing_directory(owner, carpeta, titulo=None):
    if titulo is None:
        titulo = _("Open Directory")
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getExistingDirectory(owner, titulo, carpeta)
    return QtWidgets.QFileDialog.getExistingDirectory(
        owner,
        titulo,
        carpeta,
        QtWidgets.QFileDialog.ShowDirsOnly
        | QtWidgets.QFileDialog.DontResolveSymlinks,  # | QtWidgets.QFileDialog.DontUseNativeDialog
    )


def _lfTituloFiltro(extension, titulo):
    if titulo is None:
        titulo = _("File")
    if " " in extension:
        filtro = extension
    else:
        pathext = "*.%s" % extension
        if extension == "*" and Code.is_linux:
            pathext = "*"
        filtro = _("File") + " %s (%s)" % (extension, pathext)
    return titulo, filtro


def leeFichero(owner, carpeta, extension, titulo=None):
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getOpenFileName(owner, titulo, carpeta, extension)
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getOpenFileName(owner, titulo, carpeta, filtro)
    return resp[0] if resp else None


def leeFicheros(owner, carpeta, extension, titulo=None):
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getOpenFileNames(owner, titulo, carpeta, extension)
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getOpenFileNames(owner, titulo, carpeta, filtro)
    return resp[0] if resp else None


def creaFichero(owner, carpeta, extension, titulo=None):
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getSaveFileName(owner, titulo, carpeta, extension, True)
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getSaveFileName(owner, titulo, carpeta, filtro)
    return resp[0] if resp else None


def leeCreaFichero(owner, carpeta, extension, titulo=None):
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getSaveFileName(owner, titulo, carpeta, extension, False)
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getSaveFileName(
        owner, titulo, carpeta, filtro, options=QtWidgets.QFileDialog.DontConfirmOverwrite
    )
    return resp[0] if resp else None


def salvaFichero(main_window, titulo, carpeta, extension, confirm_overwrite=True):
    if Code.configuration.x_mode_select_lc:
        return SelectFilesLC.getSaveFileName(main_window, titulo, carpeta, extension, confirm_overwrite)
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    if confirm_overwrite:
        resp = QtWidgets.QFileDialog.getSaveFileName(main_window, titulo, dir=carpeta, filter=filtro)
    else:
        resp = QtWidgets.QFileDialog.getSaveFileName(
            main_window, titulo, dir=carpeta, filter=filtro, options=QtWidgets.QFileDialog.DontConfirmOverwrite
        )
    return resp[0] if resp else resp
