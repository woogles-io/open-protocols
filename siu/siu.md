# SIU protocol - draft 0.2

SIU lets a front end drive any crossword-game analysis engine over a
line-based text protocol. SIU is not an acronym; it is just SIU.

## 0. Lineage

SIU is a fresh start on **UCGI**, the Universal Crossword Game Interface
César Del Solar drafted in 2023-24
([`ucgi/` in this repo](../ucgi/ucgi.md)),
itself a close translation of chess's UCI. A Macondo implementation was
started on its `ucgi` branch (2024, unmerged) and MAGPIE adopted UCGI's move
notation, but the two engines have since diverged. SIU keeps what UCGI got
right, drops what only made sense for chess, and adds what crossword-game analysis
needs. Section 13 lists every difference.

SIU is the engine-protocol member of a family of open formats:

| Format | Answers | Chess analogue |
| --- | --- | --- |
| CGP | What is the position? | FEN |
| CGH | What happened in the game? (GCG successor, draft) | PGN |
| SIU | How does a front end talk to an engine? | UCI |

## 1. Transport

- The front end starts the engine as a child process and talks over
  stdin/stdout. Other transports carry the same lines unchanged: `postMessage`
  to a WASM engine in a web worker, or a WebSocket through the local bridge
  (section 11).
- One command per line, UTF-8, terminated by `\n` (engines also accept
  `\r\n`). Arbitrary whitespace between tokens is allowed.
- The engine must read input at all times, including while searching.
- **Forced mode:** the engine never searches without a `go`, and every `go`
  follows a `position`.
- Unknown tokens are ignored and the rest of the line parsed. A command that
  is not expected (e.g. `stop` while idle) is ignored.

## 2. Formats

### Positions: CGP

Positions are CGP strings as specified in
[`cgp/` in this repo](../cgp).
SIU references CGP and never redefines it. The four core fields (board,
racks, scores, consecutive zero-score turns) are required; opcodes such as
`lex` are optional, and when an opcode conflicts with a `setoption`, the
opcode wins for that position. An empty rack field means unknown; a partially
known opponent rack goes in the opponent's field.

### Moves

UCGI move notation: fields joined by `.`, no spaces, so no quoting is ever
needed.

```
<coord>.<tiles>[.<rack>[.<challpts>[.<turnloss>]]]   tile play
ex.<tiles>[.<rack>]                                  exchange of known tiles
ex.<n>                                               exchange of n unknown tiles
pass                                                 pass, or a failed challenge
phony.<coord>.<tiles>                                a play challenged off (from CGP)
rack.<tiles>                                         not a move: the on-turn rack,
                                                     only as the last token of a moves list
```

- **Coordinates are CGP's,** as its `lm` (last move) opcode defines them:
  rows are numbered 1-15, columns lettered A-O (Excel-style `AA`, `AB`, ...
  past 26 columns). Row first = horizontal (`8D.DJINN`), column first =
  vertical (`H11.MAZEY`). Engines emit uppercase column letters, as CGP
  does, and accept either case (MAGPIE emits lowercase today). The same
  convention is used by GCG and CGH; the UCGI draft's prose, which lettered
  the rows, is superseded.
- Tiles played through are written as the actual letter: no `.`, no `(A)`.
- Blanks are lowercase. Multi-character tiles are bracketed: `[CH]`.
- Examples: `8D.DJINN.DIJNNR?`, `J1.sCRIEVE`, `ex.ABC.ABCDEFG`, `ex.4`,
  `pass`, `phony.H11.MAZEY`.
- The tile-play and exchange forms are CGP's `lm` notation; SIU adds only
  the optional rack and challenge fields from UCGI, and `rack.`.

### Games: CGH

Where a whole game is needed (see open question 3), it is a CGH document, the
draft GCG successor in
[`cgh/` in this repo](../cgh).

## 3. Handshake

```
> siu
< id name <engine> <version>
< id author <names>
< capability <cap> [<cap> ...]
< option name <Name> type <check|spin|combo|button|string> [default <v>] [min <n>] [max <n>] [var <v> ...]
< ...
< siuok
```

The engine boots fast and does no heavy initialisation before `siuok`; a
front end may send `quit` right after it, just to learn the engine's options.

Capabilities: `gen`, `sim`, `infer`, `endgame`, `peg`, `auto`. A front end
must not send a `go` mode the engine did not declare. Two more describe
behaviour: `stream` (sends `info` during a search) and `stop` (honours `stop`
mid-search). An engine without them, such as a batch shim, sends only the
final result.

## 4. Options

```
> setoption name <Name> [value <v>]
> isready
< readyok
```

Names and values are case-insensitive and may contain spaces, but not the
words `name` or `value`. A `button` option takes no value. `setoption` is
sent only while the engine is idle. `isready` is answered with `readyok` once
all earlier input is processed, immediately and without stopping when a
search is running. It is required once before the first `go`.

### Reserved options

| Option | Type | Meaning |
| --- | --- | --- |
| `DataPath` | string | Directories with lexica, leave files and other strategy data; `;`-separated (from UCGI) |
| `EndgameHash` | spin | MB for endgame and pre-endgame hash tables; engines start small (from UCGI) |
| `Lexicon` | string | Short code, e.g. `CSW24` |
| `LetterDistribution` | string | e.g. `english` |
| `Leaves` | string | Leave file identifier |
| `WinPctTable` | string | Win % table identifier |
| `ChallengeRule` | combo | `void`, `single`, `double`, `triple`, `five_point`, `ten_point` |
| `Variant` | combo | `classic`, `wordsmog`, ... |
| `Threads` | spin | Default thread count for `go` |

Engines may add their own options. Names starting `SIU_` are reserved for
this spec.

## 5. Setting the position

```
position cgp <cgp> [moves <move> ... [rack.<tiles>]]
siunewgame
```

- `moves` plays the listed moves from the CGP. Inference needs this form: the
  engine must see the position before the opponent's move, and the move.
- Each `position` replaces the previous one. Engines may cache work across
  positions, keyed by position, but must not depend on it.
- `siunewgame` says the next position comes from a different game. It is
  optional; front ends follow it with `isready`.

## 6. Searching

```
go [<mode>] [searchmoves <m> ...] [alsosearchmoves <m> ...] [depth <n>]
   [iterations <n>] [movetime <ms>] [stopcondition 95|98|99] [firstwin]
   [useinference] [threads <n>] [infinite]
stop
quit
```

Modes: `gen`, `sim`, `infer`, `endgame`, `peg`, `auto`. With no mode, `auto`
is assumed: the engine picks the phase, as BestBot and MAGPIE's PlayChooser
do.

| Parameter | Meaning |
| --- | --- |
| `searchmoves` | Analyse only these moves |
| `alsosearchmoves` | Add these to the engine's own candidates; for annotation, the move actually played |
| `depth` | Plies: sim look-ahead, or endgame search depth |
| `iterations` | Sim iterations |
| `movetime` | Search exactly this many ms |
| `stopcondition` | Sim stops when the leader is this % certain |
| `firstwin` | Endgame and pre-endgame: return as soon as any win is found |
| `useinference` | Sim draws opponent racks from the last `infer` result |
| `infinite` | Search until `stop` |

- Limits combine; the search ends at the first one reached.
- An engine that cannot honour a parameter (e.g. Quackle has no
  `stopcondition`) answers `info string ignored <parameter>` and continues. It
  never ignores one silently.
- On `stop`, or when a limit is reached, the engine sends its final `info`
  lines, then `bestmove`. Every `go` ends with exactly one `bestmove`.
  (`go infer` ends with `bestmove none`.)

## 7. Output

### Provenance

Before the first result of every search, the engine says what produced it,
so numbers from different engines or leave generations are never compared by
accident:

```
info string provenance engine=<name>/<version> leaves=<id> winpct=<id> lexicon=<code>
```

### General info (from UCGI)

`depth`, `time` (ms), `nodes`, `nps`, `hashfull` (permill), `currmove`,
`currmovenumber`, `pv <m> ...`, `score wp <x>` / `score eq <x>` (optionally
`lowerbound` / `upperbound`), and `string <rest of line>`.

### Per-mode results

```
info gen move <m> score <n> eq <x> leave <tiles>
info sim move <m> wp <x> wpse <x> eq <x> eqse <x> iters <n>
info infer leave <tiles> prob <p>
info endgame depth <n> score spread <+n> pv <m> ...
info peg move <m> w:<draws> d:<draws> l:<draws> [spread <+n>]
bestmove <m>
```

- Sim lines repeat as estimates converge. `wpse` and `eqse` are the standard
  errors; MAGPIE already reports them in UCGI mode.
- The `peg` draws are `|`-separated, from UCGI: `info peg 8D.QI w:AB|AC|DE d:BB l:AH`.
- Win % and equity are not defined identically across engines (win % tables,
  MAGPIE's spread projection). SIU reports which definition was used, through
  provenance, rather than forcing one.

### Errors

```
info string error <code> <free text>
```

Codes: `unknown-command`, `bad-position`, `bad-move`, `unsupported-mode`,
`no-position`.

## 8. Example session

```
> siu
< id name MAGPIE 0.x
< id author MAGPIE authors
< capability gen sim infer endgame peg auto stream stop
< option name Lexicon type string default CSW24
< option name Threads type spin default 8 min 1 max 256
< siuok
> setoption name Lexicon value CSW21
> isready
< readyok
> position cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AEINRST/ 0/0 0
> go sim depth 2 movetime 30000 stopcondition 99 alsosearchmoves 8H.NASTIER
< info string provenance engine=MAGPIE/0.x leaves=CSW21 winpct=winpct_english lexicon=CSW21
< info sim move 8D.RETAINS wp 61.2 wpse 0.9 eq 74.1 eqse 1.1 iters 400
< info sim move 8H.NASTIER wp 60.8 wpse 0.9 eq 73.6 eqse 1.2 iters 400
< ...
> stop
< bestmove 8D.RETAINS
```

## 9. What SIU leaves out

Front-end concerns stay with the front end: no clocks (`1time`, `2inc`),
playing strength (`UCGI_LimitStrength`, `UCGI_Elo`), opponent identity
(`UCGI_Opponent`), registration or copy protection. These came from UCI's
engine-versus-human play and do not serve analysis.

## 10. Conformance

A shared test corpus (`conformance/`) of CGP positions and a harness that
drives any SIU engine and checks protocol behaviour: the handshake,
capabilities matching behaviour, `isready` while searching, `stop` answered
promptly, exactly one `bestmove` per `go`, legal moves, and exact endgame
results where a position has a known answer.

## 11. Local bridge

A browser cannot start a child process, so a web front end reaches engines
on the user's own machine through **`siu-bridge`**: a small local program
that launches configured engines and relays SIU lines over a WebSocket.
Compute and data files stay on the user's machine.

### Configuration

The bridge launches only the engines in its config, never anything else.

```toml
[[engine]]
id      = "macondo"
command = ["/usr/local/bin/macondo-siu"]

[[engine]]
id      = "magpie"
command = ["/opt/magpie/bin/magpie", "-mode", "siu"]
```

(The commands are placeholders: neither engine has an SIU mode yet.)

### Connection

- Listens on `127.0.0.1` only *(open: pick a default port)*.
- **Origin allowlist:** a WebSocket upgrade is accepted only from origins in
  the config (e.g. `https://woogles.io`). Any page can try to reach
  localhost, so this check is mandatory.
- **Pairing:** on first use the bridge shows a one-time code; the front end
  asks the user for it and receives a revocable token for later connections.
- *(Open: Chrome and Firefox allow an https page to open `ws://localhost`;
  Chrome is adding local-network-access prompts and Safari has been
  stricter. Test all three.)*

### Bridge messages

Bridge-level lines start with `bridge`, so they never collide with engine
commands.

```
> bridge hello token <token>
< bridge ok 0.2
> bridge engines
< bridge engine macondo
< bridge engine magpie
< bridge enginesok
> bridge open magpie
< bridge opened magpie
```

After `bridge open`, every other line is relayed verbatim, starting with the
`siu` handshake. `bridge close` ends the engine process. One connection
drives one engine; a front end comparing engines opens several.

Results from a local engine stay local unless the user saves them, for
example into the game's annotation. The bridge sends nothing anywhere on its
own.

## 12. Engine survey (2026-10)

| | Macondo | MAGPIE | Quackle | Elise |
| --- | --- | --- | --- | --- |
| Interface today | Interactive shell; unmerged `ucgi` branch (2024) with `cgp`, `gen`, `sim` | Shell with async `stop`/`status`, `libmagpie`, WASM worker; UCGI move notation and output mode | C++ library + bindings | Batch CLI over a GCG |
| CGP | Yes | Yes | No (adapter) | No (adapter) |
| Gen / sim | Yes | Yes, BAI stopping | Yes, fixed iterations | Yes |
| Inference | Yes | Yes | No | Yes |
| Endgame | Yes | Yes | Yes | Yes |
| Pre-endgame | Yes | Yes | Up to 2 in bag | Static evaluation only |
| License | GPL-3.0 | GPL-3.0 | GPL-3.0 | Unclear; ask the author |

## 13. Changes from UCGI

| Area | UCGI draft | SIU |
| --- | --- | --- |
| Handshake | `ucgi` / `ucgiok` | `siu` / `siuok`, plus `capability` |
| Coordinates | Rows lettered, letter first = horizontal | CGP's: rows numbered, number first = horizontal (also GCG, CGH, MAGPIE) |
| Challenged-off plays | Not covered | `phony.<coord>.<tiles>` (from CGP) |
| Search kinds | One `go` | `go <mode>`: gen, sim, infer, endgame, peg, auto |
| Sim depth | `depth` | `depth`, plus `iterations` |
| Sim results | `score wp`, `score eq` | Per-candidate `info sim` with standard errors |
| Inference | Not covered | `go infer`, `info infer`, `useinference` |
| Provenance | None | Mandatory line naming engine, leaves, win % table |
| Unsupported parameters | Unspecified | `info string ignored <param>` |
| Clocks, strength, opponent, registration, copy protection | Present | Removed |
| `ucginewgame` | Present | Renamed `siunewgame` |
| Kept as is | | Transport rules, forced mode, `isready`, `setoption`, option types, `searchmoves`, `alsosearchmoves`, `stopcondition`, `firstwin`, `info peg`, `DataPath`, `EndgameHash`, `bestmove` |

## 14. Open questions

1. *(Settled 2026-10-07: the name is SIU, and it lives here beside CGP and
   CGH.)*
2. *(Settled 2026-10-07: coordinates are CGP's.)*
3. **Whole-game analysis** (what the BestBot worker does): a `go` over a CGH
   game, or left to the front end looping over positions?
4. **Analysis in CGH.** CGH events have a free-text comment but no field for
   structured engine results; "save to annotation" needs one. CGH's
   `ChallengeRule` enum also lacks `VOID`.
5. **Native modes.** A `macondo siu` command, or an adapter over the shell?
   MAGPIE's UCGI output mode may already be most of the way there.
6. **Versioning.** Report the protocol version in the handshake
   (`id protocol siu 0.2`)?
