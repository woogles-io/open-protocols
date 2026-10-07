"""Unit tests for grammar.py and the bundled positions. Run: python3 -m unittest -v"""

import json
import unittest
from pathlib import Path

import grammar

HERE = Path(__file__).resolve().parent


class MoveSyntax(unittest.TestCase):
    def test_valid(self):
        for move in ("8D.DJINN", "8D.DJINN.DIJNNR?", "J1.sCRIEVE", "11D.FIREFANG.AEFGINR.0.1",
                     "3M.CHTHoNIC.CCHIN?T.5.0", "13L.ONYX", "8d.ZA", "ex.ABC", "ex.ABC.ABCDEFG", "ex.4",
                     "pass", "phony.H11.MAZEY", "8D.[CH]E"):
            with self.subTest(move=move):
                self.assertTrue(grammar.is_valid_move(move))

    def test_invalid(self):
        for move in ("8D ZA", "\"8D ZA\"", "16A.ZA", "8P.ZA", "8D.", "ex.", "-AEI", "-", "8D.Z(A)", "none"):
            with self.subTest(move=move):
                self.assertFalse(grammar.is_valid_move(move))

    def test_coordinates(self):
        self.assertTrue(grammar.coord_on_board("8D"))
        self.assertTrue(grammar.coord_on_board("H11"))
        self.assertTrue(grammar.coord_on_board("o15"))
        self.assertFalse(grammar.coord_on_board("0A"))
        self.assertFalse(grammar.coord_on_board("AA1"))


class Positions(unittest.TestCase):
    def test_bundled_positions_are_consistent(self):
        """Every position parses, and its tile count matches its declared bag size."""
        positions = json.loads((HERE / "positions.json").read_text())["positions"]
        for p in positions:
            with self.subTest(position=p["id"]):
                cgp = grammar.parse_cgp(p["cgp"])
                unseen = grammar.STANDARD_TILE_COUNT - cgp.tiles_on_board() - cgp.tiles_on_racks()
                unknown_rack_slots = 0
                if p["bag"] > 0:
                    unknown_rack_slots = sum(7 - len(rack) for rack in cgp.racks)
                self.assertEqual(unseen, p["bag"] + unknown_rack_slots)

    def test_rejects_bad_rows(self):
        with self.assertRaises(ValueError):
            grammar.parse_cgp("15/15 AEINRST/ 0/0 0")
        with self.assertRaises(ValueError):
            grammar.parse_cgp("14/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AEINRST/ 0/0 0")


class InfoLines(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(grammar.info_kind("info sim move 8D.ZA wp 55"), "sim")
        self.assertTrue(grammar.is_provenance("info string provenance engine=x/1"))
        self.assertTrue(grammar.is_error("info string error no-position", "no-position"))
        self.assertFalse(grammar.is_error("info string error bad-move", "no-position"))

    def test_options(self):
        opt = grammar.parse_option("option name Endgame Hash type spin default 16 min 1 max 8000")
        self.assertEqual((opt.name, opt.type), ("Endgame Hash", "spin"))
        self.assertIsNone(grammar.parse_option("option name Foo type slider"))


if __name__ == "__main__":
    unittest.main()
