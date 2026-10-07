# SIU - Scrabble Interface, Universal

A text protocol between crossword-game front ends (Woogles, desktop GUIs,
scripts, AI agents) and analysis engines (Macondo, MAGPIE, Quackle, Elise),
in the spirit of chess's UCI: write the UI once, plug in any engine.

SIU is a fresh start on [UCGI](../ucgi/ucgi.md) and uses this repo's other
formats: [CGP](../cgp) for positions and [CGH](../cgh) for games.

- [`siu.md`](siu.md) - the protocol (draft 0.2)
- [`conformance/`](conformance) - a harness that checks any engine against
  the spec, with test positions and a mock engine

## Non-goals

- SIU requires no changes to any front end or engine; adoption is opt-in.
- It does not move analysis to the cloud. The main target is engines on the
  user's own machine (in the browser as WASM, or native through a local
  bridge), selected from a front end's UI. Server-side analysis such as
  Woogles' BestBot queue is untouched.
- It does not define what results mean across engines. It reports which
  engine, leave file and win % table produced each result, so they are
  never compared by accident.
