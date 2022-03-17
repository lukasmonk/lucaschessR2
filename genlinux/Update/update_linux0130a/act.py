import os
import Code
import Code.QT.QTUtil2 as QTUtil2
import zipfile

zip = zipfile.ZipFile("actual/0130a.zip")

zip.extractall(path=os.path.abspath(os.path.join(os.curdir, "..")))

QTUtil2.message(None, "Version R 1.30a")

