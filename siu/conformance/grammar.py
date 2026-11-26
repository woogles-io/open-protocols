"""Parsers for the text SIU puts on the wire: moves, CGP positions, info lines.

Stdlib only, so the harness runs anywhere Python 3.9+ does.
"""

import re
from dataclasses import dataclass, field

BOARD_SIZE = 15
STANDARD_TILE_COUNT = 100  # English distribution; enough for the bundled positions

_TILE = r"(?:[A-Za-z]|\[[A-Za-z]+\])"
_RACK_TILE = r"(?:[A-Za-z?]|\[[A-Za-z]+\])"
_TILES = rf"{_TILE}+"
_RACK = rf"{_RACK_TILE}+"
_COORD = r"(?:\d+[A-Za-z]+|[A-Za-z]+\d+)"

_TILE_PLAY = re.compile(rf"^(?P<coord>{_COORD})\.(?P<tiles>{_TILES})(?:\.{_RACK}(?:\.\d+(?:\.\d+)?)?)?$")
_EXCHANGE = re.compile(rf"^ex\.(?:\d+|{_TILES}(?:\.{_RACK})?)$")
_PHONY = re.compile(rf"^phony\.(?P<coord>{_COORD})\.(?P<tiles>{_TILES})$")


def _column_index(letters: str) -> int:
    """Excel-style column letters to a 0-based index: A=0, Z=25, AA=26."""
    index = 0
    for ch in letters.upper():
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return index - 1


def coord_on_board(coord: str, size: int = BOARD_SIZE) -> bool:
    """True when a CGP coordinate (8D horizontal, D8 vertical) lies on the board."""
    match = re.fullmatch(r"(\d+)([A-Za-z]+)|([A-Za-z]+)(\d+)", coord)
    if not match:
        return False
    row = int(match.group(1) or match.group(4))
    col = _column_index(match.group(2) or match.group(3))
    return 1 <= row <= size and 0 <= col < size


def is_valid_move(move: str) -> bool:
    """Syntax check for an SIU move token (spec section 2). Not a legality check."""
    if move == "pass" or _EXCHANGE.match(move):
        return True
    for pattern in (_TILE_PLAY, _PHONY):
        match = pattern.match(move)
        if match:
            return coord_on_board(match.group("coord"))
    return False


@dataclass
class Cgp:
    rows: list
    racks: list
    scores: list
    zeros: int
    opcodes: dict = field(default_factory=dict)

    def tiles_on_board(self) -> int:
        return sum(1 for row in self.rows for tok in _row_tokens(row) if not tok.isdigit())

    def tiles_on_racks(self) -> int:
        return sum(len(re.findall(_RACK_TILE, rack)) for rack in self.racks)


def _row_tokens(row: str) -> list:
    return re.findall(r"\d+|\[[^\]]+\]|.", row)


def parse_cgp(text: str, size: int = BOARD_SIZE) -> Cgp:
    """Parse the four required CGP fields plus opcodes. Raises ValueError."""
    fields = text.split(" ", 4)
    if len(fields) < 4:
        raise ValueError("CGP needs at least 4 space-separated fields")
    rows = fields[0].split("/")
    if len(rows) != size:
        raise ValueError(f"board has {len(rows)} rows, expected {size}")
    for i, row in enumerate(rows, start=1):
        width = sum(int(tok) if tok.isdigit() else 1 for tok in _row_tokens(row))
        if width != size:
            raise ValueError(f"row {i} is {width} squares wide, expected {size}")
    racks = fields[1].split("/")
    scores = fields[2].split("/")
    if len(racks) != len(scores):
        raise ValueError("racks and scores have different player counts")
    opcodes = {}
    if len(fields) == 5:
        for op in fields[4].split(";"):
            op = op.strip()
            if op:
                name, _, value = op.partition(" ")
                opcodes[name] = value.strip()
    return Cgp(rows, racks, [int(s) for s in scores], int(fields[3]), opcodes)


@dataclass
class Option:
    name: str
    type: str
    rest: str


def parse_option(line: str):
    """Parse 'option name <Name> type <t> ...'. Returns None if malformed."""
    match = re.fullmatch(r"option\s+name\s+(.+?)\s+type\s+(check|spin|combo|button|string)(\s+.*)?", line.strip())
    if not match:
        return None
    return Option(match.group(1), match.group(2), (match.group(3) or "").strip())


def info_kind(line: str):
    """The second token of an info line ('sim', 'string', 'depth', ...), or None."""
    tokens = line.split()
    if len(tokens) < 2 or tokens[0] != "info":
        return None
    return tokens[1]


def is_provenance(line: str) -> bool:
    return line.split()[:3] == ["info", "string", "provenance"]


def is_error(line: str, code=None) -> bool:
    tokens = line.split()
    if tokens[:3] != ["info", "string", "error"]:
        return False
    return code is None or (len(tokens) > 3 and tokens[3] == code)


RESULT_KINDS = {"gen", "sim", "infer", "endgame", "peg"}
