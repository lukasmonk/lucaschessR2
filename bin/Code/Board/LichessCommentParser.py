import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

# --- Data structures -------------------------------------------------------

Color = str  # One of "G" (green), "R" (red), "Y" (yellow), "B" (blue)
Square = str  # "a1".."h8"


@dataclass(frozen=True)
class ColoredSquare:
    color: Color
    square: Square


@dataclass(frozen=True)
class Arrow:
    color: Color
    origin: Square
    target: Square


# --- Regexes ---------------------------------------------------------------

# Matches a single LiChess square
RE_SQ = r"[a-h][1-8]"
# Matches color letter
RE_COLOR = r"[GRYB]"

# %csl items like: Gd4, Re5, Bb7
RE_CSL_ITEM = re.compile(fr"\b({RE_COLOR})({RE_SQ})\b", re.IGNORECASE)
# %cal items like: Gd4e6, Rh1h8
RE_CAL_ITEM = re.compile(fr"\b({RE_COLOR})({RE_SQ})({RE_SQ})\b", re.IGNORECASE)

# Extract groups after a marker until next %marker or end of string
RE_BLOCK = re.compile(r"%(?P<tag>[a-z]{3,4})\s*(?P<body>[^%]*)", re.IGNORECASE)


# --- Utilities -------------------------------------------------------------

def _split_items(body: str) -> Iterable[str]:
    """Split a %csl/%cal body into tokens (comma/space separated)."""
    # normalize separators to spaces
    body = body.replace(",", " ")
    for token in body.split():
        yield token.strip()


def _parse_csl(body: str) -> List[ColoredSquare]:
    out: List[ColoredSquare] = []
    for token in _split_items(body):
        m = RE_CSL_ITEM.fullmatch(token)
        if not m:
            continue
        color, sq = m.group(1).upper(), m.group(2).lower()
        out.append(ColoredSquare(color=color, square=sq))
    return out


def _parse_cal(body: str) -> List[Arrow]:
    out: List[Arrow] = []
    for token in _split_items(body):
        m = RE_CAL_ITEM.fullmatch(token)
        if not m:
            continue
        color = m.group(1).upper()
        origin = m.group(2).lower()
        target = m.group(3).lower()
        out.append(Arrow(color=color, origin=origin, target=target))
    return out


def parse_lichess_graphics(text: Optional[str]):
    squares: List[ColoredSquare] = []
    arrows: List[Arrow] = []
    text = text.replace("[", " ").replace("]", " ")

    for m in RE_BLOCK.finditer(text):
        tag = m.group("tag").lower()
        body = (m.group("body") or "").strip()
        if not body and tag in {"csl", "cal"}:
            # tolerate bodies that spill until next %TAG via RE_BLOCK
            pass
        if tag == "csl":
            squares.extend(_parse_csl(body))
        elif tag == "cal":
            arrows.extend(_parse_cal(body))

    return squares, arrows
