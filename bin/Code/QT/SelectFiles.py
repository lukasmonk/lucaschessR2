import os

from PySide2 import QtWidgets

import Code


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
    options = QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
    if Code.configuration.x_mode_select_lc:
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
    return QtWidgets.QFileDialog.getExistingDirectory(
        owner,
        titulo,
        carpeta,
        options=options
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
    options = QtWidgets.QFileDialog.DontUseNativeDialog if Code.configuration.x_mode_select_lc else QtWidgets.QFileDialog.Options()

    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getOpenFileName(owner, titulo, carpeta, filtro, options=options)
    return resp[0] if resp else None


def leeFicheros(owner, carpeta, extension, titulo=None):
    options = QtWidgets.QFileDialog.DontUseNativeDialog if Code.configuration.x_mode_select_lc else QtWidgets.QFileDialog.Options()

    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getOpenFileNames(owner, titulo, carpeta, filtro, options=options)
    return resp[0] if resp else None


def creaFichero(owner, carpeta, extension, titulo=None):
    options = QtWidgets.QFileDialog.DontUseNativeDialog if Code.configuration.x_mode_select_lc else QtWidgets.QFileDialog.Options()

    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getSaveFileName(owner, titulo, carpeta, filtro, options=options)
    return resp[0] if resp else None


def leeCreaFichero(owner, carpeta, extension, titulo=None):
    options = QtWidgets.QFileDialog.DontConfirmOverwrite
    if Code.configuration.x_mode_select_lc:
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    resp = QtWidgets.QFileDialog.getSaveFileName(
        owner, titulo, carpeta, filtro, options=options
    )
    return resp[0] if resp else None


def salvaFichero(main_window, titulo, carpeta, extension, confirm_overwrite=True):
    titulo, filtro = _lfTituloFiltro(extension, titulo)
    if confirm_overwrite:
        options = QtWidgets.QFileDialog.DontUseNativeDialog if Code.configuration.x_mode_select_lc else QtWidgets.QFileDialog.Options()
        resp = QtWidgets.QFileDialog.getSaveFileName(main_window, titulo, dir=carpeta, filter=filtro, options=options)
    else:
        options = QtWidgets.QFileDialog.DontConfirmOverwrite
        if Code.configuration.x_mode_select_lc:
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
        resp = QtWidgets.QFileDialog.getSaveFileName(
            main_window, titulo, dir=carpeta, filter=filtro, options=options
        )
    return resp[0] if resp else resp
