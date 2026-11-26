"""A minimal engine that speaks SIU correctly but knows nothing about the game.

It exists to test the conformance harness itself, and as a readable sketch of
the protocol's control flow (reader thread, interruptible search, one
bestmove per go). Every move it reports is a fixed placeholder.

    python3 mock_engine.py            # conformant
    python3 mock_engine.py --broken   # declares everything, then breaks search rules, so the
                                      # harness's failure paths can be checked
"""

import sys
import threading

ENGINE_NAME = "siu-mock"
VERSION = "0.2"
MODES = ("gen", "sim", "infer", "endgame", "peg", "auto")
FAKE_MOVES = ("8D.ZA", "8H.QI", "ex.ABC", "pass")

out_lock = threading.Lock()


def say(line: str) -> None:
    with out_lock:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


class Engine:
    def __init__(self, broken: bool):
        self.broken = broken
        self.position = None
        self.lexicon = "CSW24"
        self.search = None
        self.stop_event = threading.Event()

    def handshake(self) -> None:
        say(f"id name {ENGINE_NAME} {VERSION}")
        say("id author SIU conformance suite")
        say("capability " + " ".join(MODES) + " stream stop")
        say("option name Lexicon type string default CSW24")
        say("option name Threads type spin default 1 min 1 max 64")
        say("option name EndgameHash type spin default 16 min 1 max 8000")
        say("siuok")

    def go(self, args: list) -> None:
        if self.search and self.search.is_alive():
            return
        if self.position is None:
            say("info string error no-position go sent before position")
            return
        mode = args[0] if args and args[0] in MODES else "auto"
        infinite = "infinite" in args
        movetime = 200
        if "movetime" in args:
            movetime = int(args[args.index("movetime") + 1])
        self.stop_event.clear()
        self.search = threading.Thread(target=self.run_search, args=(mode, infinite, movetime), daemon=True)
        self.search.start()

    def run_search(self, mode: str, infinite: bool, movetime_ms: int) -> None:
        if not self.broken:
            say(f"info string provenance engine={ENGINE_NAME}/{VERSION} leaves=none winpct=none lexicon={self.lexicon}")
        ticks = 0
        while True:
            if self.stop_event.wait(0.05):
                break
            ticks += 1
            if mode == "sim":
                say(f"info sim move 8D.ZA wp 55.0 wpse 1.0 eq 20.0 eqse 1.0 iters {ticks * 10}")
            elif mode == "infer":
                say("info infer leave AEN prob 0.12")
            if not infinite and ticks * 50 >= movetime_ms:
                break
        if mode == "infer":
            say("bestmove none")
        else:
            say("bestmove " + ("8d ZA" if self.broken else FAKE_MOVES[0]))
            if self.broken:
                say("bestmove " + FAKE_MOVES[1])

    def handle(self, line: str) -> bool:
        tokens = line.split()
        if not tokens:
            return True
        cmd, args = tokens[0], tokens[1:]
        if cmd == "siu":
            self.handshake()
        elif cmd == "isready":
            say("readyok")
        elif cmd == "setoption":
            if "name" in args and "value" in args and args[args.index("name") + 1].lower() == "lexicon":
                self.lexicon = args[args.index("value") + 1]
        elif cmd == "position":
            if len(args) >= 4 and args[0] == "cgp":
                self.position = " ".join(args[1:])
            else:
                say("info string error bad-position expected 'position cgp <cgp>'")
        elif cmd == "siunewgame":
            self.position = None
        elif cmd == "go":
            self.go(args)
        elif cmd == "stop":
            self.stop_event.set()
        elif cmd == "quit":
            self.stop_event.set()
            return False
        elif not self.broken:
            say(f"info string error unknown-command {cmd}")
        return True


def main() -> None:
    engine = Engine(broken="--broken" in sys.argv)
    for raw in sys.stdin:
        if not engine.handle(raw.strip()):
            break


if __name__ == "__main__":
    main()
