"""SIU conformance harness: drives any engine and checks protocol behaviour.

    python3 siu_conformance.py -- <engine command ...>
    python3 siu_conformance.py -- python3 mock_engine.py

It checks the protocol, not playing strength: the handshake, isready, stop,
exactly one bestmove per go, move syntax, provenance, and that declared
capabilities match behaviour. Exits non-zero if any check fails.
"""

import argparse
import json
import queue
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

import grammar

HERE = Path(__file__).resolve().parent


class EngineProcess:
    """An engine subprocess with a background reader, so reads never block."""

    def __init__(self, command: list):
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1,
        )
        self.lines = queue.Queue()
        self.transcript = []
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self) -> None:
        for raw in self.proc.stdout:
            self.lines.put(raw.rstrip("\r\n"))
        self.lines.put(None)  # EOF

    def send(self, line: str) -> None:
        self.transcript.append("> " + line)
        try:
            self.proc.stdin.write(line + "\n")
            self.proc.stdin.flush()
        except BrokenPipeError:
            pass

    def read_until(self, done, timeout: float) -> tuple:
        """Collect lines until done(line) is true. Returns (lines, finished)."""
        got = []
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return got, False
            try:
                line = self.lines.get(timeout=remaining)
            except queue.Empty:
                return got, False
            if line is None:
                return got, False
            self.transcript.append("< " + line)
            got.append(line)
            if done(line):
                return got, True

    def drain(self, quiet: float = 0.3) -> list:
        """Lines that arrive until the engine has been quiet for `quiet` seconds."""
        got, _ = self.read_until(lambda _line: False, quiet)
        return got

    def close(self) -> None:
        self.send("quit")
        try:
            self.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.proc.kill()


class Results:
    def __init__(self):
        self.rows = []

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.rows.append((name, status, detail))
        print(f"{status:<5} {name}" + (f"  - {detail}" if detail else ""), flush=True)

    @property
    def failed(self) -> int:
        return sum(1 for _, status, _ in self.rows if status == "FAIL")


class Suite:
    def __init__(self, command: list, timeout: float, movetime: int, positions: list):
        self.command = command
        self.timeout = timeout
        self.movetime = movetime
        self.positions = positions
        self.results = Results()
        self.capabilities = set()

    def start(self) -> EngineProcess:
        """A fresh engine, handshaken and ready. Each check gets its own process."""
        engine = EngineProcess(self.command)
        engine.send("siu")
        engine.read_until(lambda line: line.strip() == "siuok", self.timeout)
        engine.send("isready")
        engine.read_until(lambda line: line.strip() == "readyok", self.timeout)
        return engine

    def position_for(self, mode: str):
        return next((p for p in self.positions if mode in p["modes"]), None)

    def set_position(self, engine: EngineProcess, position: dict) -> None:
        engine.send(f"setoption name Lexicon value {position['lexicon']}")
        moves = position.get("moves")
        engine.send(f"position cgp {position['cgp']}" + (" moves " + " ".join(moves) if moves else ""))
        engine.send("isready")
        engine.read_until(lambda line: line.strip() == "readyok", self.timeout)

    # -- checks -----------------------------------------------------------

    def check_handshake(self) -> None:
        engine = EngineProcess(self.command)
        try:
            engine.send("siu")
            lines, ok = engine.read_until(lambda line: line.strip() == "siuok", self.timeout)
            if not ok:
                self.results.add("handshake: siuok", "FAIL", f"no siuok within {self.timeout}s")
                return
            self.results.add("handshake: siuok", "PASS")
            ids = [l for l in lines if l.startswith("id ")]
            has_name = any(l.startswith("id name ") for l in ids)
            has_author = any(l.startswith("id author ") for l in ids)
            self.results.add("handshake: id name and author", "PASS" if has_name and has_author else "FAIL",
                             "" if has_name and has_author else "missing id name or id author")
            caps = [l for l in lines if l.startswith("capability ")]
            if caps:
                self.capabilities = set(caps[-1].split()[1:])
                self.results.add("handshake: capability", "PASS", " ".join(sorted(self.capabilities)))
            else:
                self.results.add("handshake: capability", "FAIL", "no capability line")
            bad = [l for l in lines if l.startswith("option") and grammar.parse_option(l) is None]
            self.results.add("handshake: option lines well-formed", "FAIL" if bad else "PASS",
                             f"malformed: {bad[0]}" if bad else "")
        finally:
            engine.close()

    def check_isready(self) -> None:
        engine = self.start()
        try:
            engine.send("isready")
            _, ok = engine.read_until(lambda line: line.strip() == "readyok", self.timeout)
            self.results.add("isready answered", "PASS" if ok else "FAIL")
        finally:
            engine.close()

    def check_unknown_command(self) -> None:
        engine = self.start()
        try:
            engine.send("joho frobnicate")
            engine.send("isready")
            _, ok = engine.read_until(lambda line: line.strip() == "readyok", self.timeout)
            self.results.add("unknown command ignored", "PASS" if ok else "FAIL",
                             "" if ok else "engine stopped answering after an unknown command")
        finally:
            engine.close()

    def check_stop_when_idle(self) -> None:
        engine = self.start()
        try:
            engine.send("stop")
            stray = [l for l in engine.drain() if l.startswith("bestmove")]
            engine.send("isready")
            _, ok = engine.read_until(lambda line: line.strip() == "readyok", self.timeout)
            passed = ok and not stray
            self.results.add("stop while idle is ignored", "PASS" if passed else "FAIL",
                             "sent bestmove with no search running" if stray else "")
        finally:
            engine.close()

    def check_go_without_position(self) -> None:
        engine = self.start()
        try:
            engine.send("go gen")
            lines = engine.drain(1.0)
            errored = any(grammar.is_error(l, "no-position") for l in lines)
            searched = any(l.startswith("bestmove") for l in lines)
            if errored and not searched:
                self.results.add("go without position reports no-position", "PASS")
            else:
                self.results.add("go without position reports no-position", "FAIL",
                                 "searched anyway" if searched else "no 'info string error no-position'")
        finally:
            engine.close()

    def check_mode(self, mode: str) -> None:
        name = f"go {mode}"
        position = self.position_for(mode)
        if mode not in self.capabilities:
            self.results.add(name, "SKIP", "not declared")
            return
        if position is None:
            self.results.add(name, "SKIP", "no test position for this mode")
            return
        engine = self.start()
        try:
            self.set_position(engine, position)
            engine.send(f"go {mode} movetime {self.movetime}")
            lines, ok = engine.read_until(lambda line: line.startswith("bestmove"), self.timeout + self.movetime / 1000)
            if not ok:
                self.results.add(name, "FAIL", f"no bestmove (position {position['id']})")
                return
            lines += engine.drain()
            problems = []
            bestmoves = [l for l in lines if l.startswith("bestmove")]
            if len(bestmoves) != 1:
                problems.append(f"{len(bestmoves)} bestmove lines, expected 1")
            move = bestmoves[0].split()[1] if len(bestmoves[0].split()) > 1 else ""
            if mode == "infer":
                if move != "none":
                    problems.append(f"infer should end 'bestmove none', got '{move}'")
            elif not grammar.is_valid_move(move):
                problems.append(f"bestmove '{move}' is not a valid SIU move")
            results = [i for i, l in enumerate(lines) if grammar.info_kind(l) in grammar.RESULT_KINDS]
            provenance = [i for i, l in enumerate(lines) if grammar.is_provenance(l)]
            if not provenance:
                problems.append("no provenance line")
            elif results and provenance[0] > results[0]:
                problems.append("provenance came after the first result")
            if mode in ("sim", "infer") and "stream" in self.capabilities and not results:
                problems.append(f"declared stream but sent no 'info {mode}' lines")
            self.results.add(name, "FAIL" if problems else "PASS",
                             "; ".join(problems) or f"bestmove {move} (position {position['id']})")
        finally:
            engine.close()

    def check_isready_while_searching(self) -> None:
        name = "isready answered during a search"
        if "stop" not in self.capabilities:
            self.results.add(name, "SKIP", "engine does not declare stop")
            return
        position = self.position_for("sim") or self.position_for("auto")
        engine = self.start()
        try:
            self.set_position(engine, position)
            engine.send("go infinite")
            time.sleep(0.3)
            engine.send("isready")
            lines, ok = engine.read_until(lambda line: line.strip() == "readyok", self.timeout)
            ended = any(l.startswith("bestmove") for l in lines)
            if ok and not ended:
                self.results.add(name, "PASS")
            else:
                self.results.add(name, "FAIL", "isready stopped the search" if ended else "no readyok")
            engine.send("stop")
            engine.read_until(lambda line: line.startswith("bestmove"), self.timeout)
        finally:
            engine.close()

    def check_stop(self) -> None:
        name = "stop ends an infinite search with one bestmove"
        if "stop" not in self.capabilities:
            self.results.add(name, "SKIP", "engine does not declare stop")
            return
        position = self.position_for("sim") or self.position_for("auto")
        engine = self.start()
        try:
            self.set_position(engine, position)
            engine.send("go infinite")
            early = engine.drain(0.5)
            if any(l.startswith("bestmove") for l in early):
                self.results.add(name, "FAIL", "infinite search ended without stop")
                return
            sent = time.monotonic()
            engine.send("stop")
            lines, ok = engine.read_until(lambda line: line.startswith("bestmove"), self.timeout)
            elapsed_ms = (time.monotonic() - sent) * 1000
            lines += engine.drain()
            count = sum(1 for l in lines if l.startswith("bestmove"))
            if ok and count == 1:
                self.results.add(name, "PASS", f"bestmove {elapsed_ms:.0f} ms after stop")
            else:
                self.results.add(name, "FAIL", f"{count} bestmove lines after stop")
        finally:
            engine.close()

    def check_quit(self) -> None:
        engine = self.start()
        engine.send("quit")
        try:
            engine.proc.wait(timeout=self.timeout)
            self.results.add("quit exits", "PASS")
        except subprocess.TimeoutExpired:
            engine.proc.kill()
            self.results.add("quit exits", "FAIL", f"still running {self.timeout}s after quit")

    def run(self) -> int:
        self.check_handshake()
        if not any(name.startswith("handshake: siuok") and status == "PASS" for name, status, _ in self.results.rows):
            print("handshake failed; skipping the remaining checks")
            return 1
        self.check_isready()
        self.check_unknown_command()
        self.check_stop_when_idle()
        self.check_go_without_position()
        for mode in ("gen", "sim", "infer", "endgame", "peg", "auto"):
            self.check_mode(mode)
        self.check_isready_while_searching()
        self.check_stop()
        self.check_quit()
        rows = self.results.rows
        print(f"\n{sum(s == 'PASS' for _, s, _ in rows)} passed, {self.results.failed} failed, "
              f"{sum(s == 'SKIP' for _, s, _ in rows)} skipped")
        return 1 if self.results.failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeout", type=float, default=10.0, help="seconds to wait for each response")
    parser.add_argument("--movetime", type=int, default=1000, help="ms per timed search")
    parser.add_argument("--positions", type=Path, default=HERE / "positions.json")
    parser.add_argument("engine", nargs=argparse.REMAINDER, help="engine command, after --")
    args = parser.parse_args()
    command = [a for a in args.engine if a != "--"] if args.engine else []
    if not command:
        parser.error("give the engine command after --")
    if len(command) == 1 and " " in command[0]:
        command = shlex.split(command[0])
    positions = json.loads(args.positions.read_text())["positions"]
    return Suite(command, args.timeout, args.movetime, positions).run()


if __name__ == "__main__":
    sys.exit(main())
