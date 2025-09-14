import subprocess
import sys

import Code


def run_lucas(*args):
    li = []
    if sys.argv[0].endswith(".py"):
        li.append("python" if Code.is_windows else "python3")
        li.append("./LucasR.py")
    else:
        li.append("LucasR.exe" if Code.is_windows else "./LucasR")
    li.extend(args)

    return subprocess.Popen(li)
