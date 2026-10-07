# SIU conformance suite

Checks that an engine speaks SIU correctly. It tests the protocol, not
playing strength. Python 3.9+, standard library only.

```
python3 siu_conformance.py -- <engine command ...>
python3 siu_conformance.py -- python3 mock_engine.py          # reference: all pass
python3 siu_conformance.py -- python3 mock_engine.py --broken  # violations caught
python3 -m unittest -v                                         # grammar + position tests
```

Options: `--timeout` (seconds per response, default 10), `--movetime` (ms per
timed search, default 1000), `--positions` (another positions file).

## What it checks

| Check | Spec |
| --- | --- |
| Handshake: `siuok`, `id name`, `id author`, a `capability` line, well-formed `option` lines | 3, 4 |
| `isready` answered; unknown commands ignored; `stop` while idle ignored | 1, 4 |
| `go` before `position` reports `no-position` and does not search | 7 |
| Every declared mode: exactly one `bestmove`, valid move syntax (`bestmove none` for infer), provenance before the first result, `info` streamed when `stream` is declared | 6, 7 |
| `isready` answered mid-search without ending it | 4 |
| `stop` ends `go infinite` with exactly one `bestmove` | 6 |
| `quit` exits | 6 |

Undeclared modes are skipped, not failed. Each check runs in a fresh engine
process, so one failure cannot cascade.

## Files

- `siu_conformance.py` - the harness
- `grammar.py` - parsers for moves, CGP, `option` and `info` lines
- `positions.json` - test positions, one or more per mode
- `mock_engine.py` - a minimal engine that speaks SIU but knows no Scrabble
- `test_grammar.py` - unit tests, including a tile-count check on every position

## Positions

None were made up: the endgame is the CGP spec's own example (bag empty), the
pre-endgame is MAGPIE's README `peg` example (1 in the bag), and the opening
and inference positions are an empty board. The endgame and pre-endgame use
the lexicons their sources used (OSPD1, NWL20); an engine without those will
need substitute positions.

## Not yet covered

- **Move legality.** Moves are checked for syntax only; legality needs a
  lexicon and board engine.
- **Known answers.** Exact endgame results and pre-endgame outcomes, once
  verified independently by at least two engines.
- `ignored <param>` notices, `searchmoves` / `alsosearchmoves`,
  `useinference`, and the error codes beyond `no-position`.
