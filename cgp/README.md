cgp stands for Crossword Game Position, and it is a file format to use when a position in a game is available, but not the full history that got us there. This can be used for puzzles and other analyses.

It is intended to only support the UTF-8 encoding.

## Description

Influenced by the FEN and EPD formats in Chess, a CGP record consists of several fields, separated by spaces, all on one line. It is meant to be concise and easily shareable for import into analysis programs.

The fields are as follows:

### 1. Tile placement

Tiles on the board are represented as the uppercase UTF-8 codepoint that represents them. Blanks on the board can be represented by the corresponding lowercase UTF-8 codepoint.

Each row of the board can then be represented by any number of letter characters, and each row should be separated by the `/` character.

In order to represent an unused space on the board, we use a number -- `1` means 1 empty space, `8` means 8 empty spaces in a row, etc.

Then, an empty 15x15 board looks like this:

`15/15/15/15/15/15/15/15/15/15/15/15/15/15/15`

A row with a D in the middle of it (the 8th position) would look like:

`7D7`

Note: for tiles that consist of multiple codepoints, such as CH in Spanish, these must be specified as `[CH]` (or `[ch]` lowercase), for example, ONLY IF there would be ambiguity. See the cgh folder for what constitutes ambiguity.

### 2. Racks for all involved players, in the order that they will next play.

Each rack is represented by its tiles, and racks are separated by a `/` symbol. A blank is represented by a `?`.

e.g.

`AB/AA?` means the player to play next has a rack of AB and the other player has a rack of AA? (? being the blank).

If one of the players' racks is only partially known, specify as many tiles as are known. If no tiles are known, leave that player's rack blank.

e.g.

`/ABCDEF` or `ABCDEF/`

Note that this supports any number of players.

**Note** It is recommended that the other player racks not be specified unless they are known for sure to be that value. It is up to the implementer to decide what to do
with a full or partial rack value for the opponent. For example, the implementer
can use this full or partial value for Monte Carlo sims, or pre-endgame solving. See
also the `oru` opcode.

For tiles that consist of multiple codepoints, these must be specified as `[CH]`, for example, again only if there is ambiguity.

### 3. Scores for both players

These are represented as regular numbers, separated by a `/` symbol. The order should be in the order of the racks.

e.g.

`357/289`

Note that this supports any number of players. Racks and scores would both have n-1 slashes for n-player games, starting with the next-to-move player and ending with the player who last moved.

These scores are before any time-penalty adjustments.

### 4. Number of consecutive zero-point turns

This number is the number of consecutive zero-point turns immediately prior to the position being shown. This should be a single number. We use this because in some implementations of crossword games, the game is over after six consecutive zero turns, for example.

e.g.

`5`

### 5. Any number of optional operations

An operation is composed of an opcode followed by zero or more operands and is concluded by a semicolon.

Multiple operations are separated by a single space character. If there is at least one operation present in a line, it is separated from the last (fourth) data field by a single space character.

## Opcodes

### bb (bingo bonus)

The number of bonus points a bingo is worth. Default to 50.

### bdn (board name)

The bdn opcode should be followed by the name of the board. For example:

`bdn CrosswordGame;`

If not specified, the implementer decides what its default board is. _The format attaches no special meaning to the board names that are provided in this opcode_. A future opcode might describe the actual board configuration square by square.

### cr (challenge rule)

The cr opcode should be followed by the name of the challenge rule. These are:

single double triple void 5pt 10pt

The implementer decides what the default challenge rule is.

### etl (exchange tile limit)

The etl opcode should be followed by the minimum number of tiles that must be in the bag to allow an exchange. Defaults to 7.

### gid (game id)

The gid opcode should be followed by a game id. The game id must not contain any spaces.

### ld (letter distribution)

The ld opcode should be followed by the name of the letter distribution. For example:

`ld english;`

If not specified, the implementer decides what its default letter distribution is. It is recommended that the letter distribution also contain the number of points for each tile.

### lex (lexicon)

The lex opcode should be followed by the name of the lexicon. For example:

`lex CSW21;`

If not specified, the implementer decides what its default lexicon is. It is recommended that this always be specified, as lexica change relatively quickly.

### lm (last move)

The move that led to this position, made by the player who moved last (the
last one in the order of the racks and scores). The board in the first field
already shows it. The lm opcode is followed by the move and, optionally, the
number of points it scored:

`lm n8.TILES;` or `lm n8.TILES SCORE;`

where n8 is the coordinate - rows are numbered 1 to 15 and columns are lettered from A to O for a 15x15 board. Horizontal plays start with the numbered row, vertical plays start with the lettered column. For boards that are bigger than 26 columns, use "Excel column notation", i.e. Z, AA, AB, ..., AAA, AAB, ...

TILES spells the whole main word, in order. Tiles the move placed are
written as their letters, a blank as the lowercase letter it stands for.
"Through" tiles, i.e., tiles that were already on the board before the move,
must be written in parentheses, as the letters they are. Consecutive through
tiles may share one pair of parentheses. For example, with CAT already on the
board,

`lm 8G.S(CAT)TER 10;`

says the move placed S, T, E and R around CAT, and scored 10. Marking the
through tiles is what lets a reader recover the move's own tiles, which the
board can't tell it: taking the tiles outside the parentheses off the board,
and the score away from the player who moved, gives the position before the
move. (Inferring what the player kept is one use.) A move written without
parentheses had no through tiles. Records written before this rule may have
left through tiles unmarked; a reader can't tell those from placed tiles.

If the move is an exchange, represent as `ex.TILES` if the tiles are known, or replace the tiles with a number of exchanged tiles (e.g. `ex.2`).

If the move is a pass or a failed challenge, represent it as `pass`.

If the move is a successful challenge, represent it as `phony.n8.TILES`, with
through tiles in parentheses as above. This represents a move that was
challenged off; the board doesn't show it.

The score, when given, is the move's score alone, without any end-of-game
adjustment (0 for an exchange, a pass or a phony).

Note: The lm opcode can only be specified once. If you want to specify multiple last moves, you should use a GCG file. This is more meant for immediate state and immediately highlighting the last play.

### mcnz (max number of consecutive zeroes)

Maximum number of consecutive zeroes until the game ends, for the given rule set. This should default to 6 if not specified.

### oru (opponent rack unknown)

The opponent rack, if provided, should be ignored for purposes of doing Monte
Carlo sims, etc.

e.g.

`oru;`

### ti (timer increment)

The timer increment in milliseconds, if one exists.

e.g.

`ti 3000;` means that 3 seconds are added to player clocks after they move

### tmr (timer)

Timers can be specified with slashes between players. They must be specified as integer milliseconds remaining on each player's clock.

e.g.

`tmr 10000/-2500;`

means the player to move has 10 seconds on their clock, and the other player has gone overtime by 2.5 seconds.

### to (timer max overtime setting)

The amount of overtime before the game ends, in milliseconds.

e.g.

`to 60000;` means the game is over after 1 minute of overtime (in typical play, the person who went over loses 10 points for every minute of overtime).

### var (variant)

The variant to use.

e.g.

`var WordSmog;`

## Example CGPs

1. From the 2018 US Nationals, game 30. Joel's opening rack was AENSTUU and he exchanged UU. Nigel's opening rack was AELNOQT. From his perspective:

`15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AELNOQT/ 0/0 0 lex NWL18; lm ex.2;`

Note: he exchanged QO instead of playing QAT!

2. Endgame from Maven paper (score is unknown, but it doesn't matter)

`5BERGS5/4PA3U5/2QAID3R5/3BEE3F2S2/1P1ET2VIATIC2/MA1TAW3c2H2/ES3IS2E2A2/AT1FOLIA4V2/LI1L1EX1E6/1N1O1D2N2Y3/1GNU2C1JETE3/2ER2OHO2N3/2O3GOY6/1INDOW1U7/4DORR7 IKLMTZ/AEINRU? 0/0 0 lex OSPD1;`

3. A play through tiles already on the board. CAT was played first, on H8
to J8 for 10 points; the player to move then exchanged, and the other player
made SCATTER around it, placing S, T, E and R for 10 more. The player to move
holds AEINRST:

`15/15/15/15/15/15/15/6SCATTER2/15/15/15/15/15/15/15 AEINRST/ 0/20 0 lex NWL23; lm 8G.S(CAT)TER 10;`
