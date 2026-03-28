import os
from shutil import which

from Code import Util
from Code.Engines import Engines


def _wrapper_path(folder_engines: str) -> str:
    return Util.opj(folder_engines, "stockfish", "stockfish")


def _stockfish_path(folder_engines: str) -> str:
    env_path = os.environ.get("LUCASCHESS_STOCKFISH")
    if env_path and os.path.isfile(env_path):
        return env_path

    wrapper = _wrapper_path(folder_engines)
    if os.path.isfile(wrapper):
        return wrapper

    resolved = which("stockfish")
    if resolved:
        return resolved

    for candidate in ("/opt/homebrew/bin/stockfish", "/usr/local/bin/stockfish"):
        if os.path.isfile(candidate):
            return candidate

    return wrapper


def read_engines(folder_engines):
    dic_engines = {}
    stockfish_path = _stockfish_path(folder_engines)

    def add_stockfish_clone(key, name, elo):
        engine = Engines.Engine(
            key,
            "Lucas Chess macOS runtime",
            "stockfish",
            "https://stockfishchess.org/",
            stockfish_path,
        )
        engine._name = name
        engine.elo = elo
        engine.alias = "stockfish"
        engine.set_uci_option("Ponder", "false")
        engine.set_uci_option("Hash", "64")
        engine.set_uci_option("Threads", "2")
        engine.set_multipv(10, 256)
        if key != "stockfish":
            engine.set_uci_option("UCI_LimitStrength", "true")
            engine.set_uci_option("UCI_Elo", str(elo))
        dic_engines[key] = engine
        return engine

    add_stockfish_clone("stockfish", "Stockfish", 3700)
    add_stockfish_clone("irina", "Irina (Stockfish)", 1500)
    add_stockfish_clone("rocinante", "Rocinante (Stockfish)", 1800)
    add_stockfish_clone("fox", "Fox (Stockfish)", 1500)
    add_stockfish_clone("foxcub", "FoxCub (Stockfish)", 1000)

    return dic_engines


def dict_engines_fixed_elo(folder_engines):
    fixed = {}
    for elo in range(800, 3001, 100):
        engine = read_engines(folder_engines)["stockfish"].clona()
        engine.set_uci_option("UCI_LimitStrength", "true")
        engine.set_uci_option("UCI_Elo", str(elo))
        engine._name = f"Stockfish ({elo})"
        engine.key = f"stockfish ({elo})"
        engine.alias = "stockfish"
        engine.elo = elo
        fixed[elo] = [engine]
    return fixed
