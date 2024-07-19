
Description of the universal crossword game interface (UCGI)    June 2023
=================================================================

Note: this description is heavily based on UCI (Universal Chess Interface).


* The specification is independent of the operating system. For Windows,
  the engine is a normal exe file, either a console or "real" windows application.

* all communication is done via standard input and output with text commands,

* The engine should boot and wait for input from the GUI,
  the engine should wait for the "isready" or "setoption" command to set up its internal parameters
  as the boot process should be as quick as possible.

* the engine must always be able to process input from stdin, even while thinking.

* all command strings the engine receives will end with '\n',
  also all commands the GUI receives should end with '\n',
  Note: '\n' can be 0x0d or 0x0a0d or any combination depending on your OS.
  If you use Engine and GUI in the same OS this should be no problem if you communicate in text mode,
  but be aware of this when for example running a Linux engine in a Windows GUI.

* arbitrary white space between tokens is allowed
  Example: "debug on\n" and  "   debug     on  \n" and "\t  debug \t  \t\ton\t  \n"
  all set the debug mode of the engine on.

* The engine will always be in forced mode which means it should never start calculating
  or pondering without receiving a "go" command first.

* Before the engine is asked to search on a position, there will always be a position command
  to tell the engine about the current position.

* if the engine or the GUI receives an unknown command or token it should just ignore it and try to
  parse the rest of the string in this line.
  Examples: "joho debug on\n" should switch the debug mode on given that joho is not defined,
            "debug joho on\n" will be undefined however.

* if the engine receives a command which is not supposed to come, for example "stop" when the engine is
  not calculating, it should also just ignore it.


Move format:
------------

The move format is described below.

```
pos.word.rack.challpts.challturnloss             # for a tile play
pass                                             # for a pass
ex.letters.rack | ex.number      # an exchange
rack.AEIRSTX                     # not a move, just a rack for the player on turn.
                                 # This should only be the last command in a list.
```

The tile play move does not need to have either of the final 3 fields. At its simplest it can just be pos.word

The format of the coordinate looks like RowColumn or ColumnRow. RowColumn is used if the play is horizontal,
ColumnRow is used if the play is vertical.

Rows are labeled from A through O (or more for bigger boards)
Columns are labeled from 1 through 15 (or more for bigger boards)

The row is a letter, the column is a number. If the letter is specified first, the play is horizontal.
If the column is specified first, the play is vertical.

For example:

```
h4.HADJI.ADHIJ.0.0          # horizontal, full rack unknown. No challenge pts,
                            # no challenge turn loss
h4.HADJI                    # same as above
11d.FIREFANG.AEFGINR.0.1    # vertical play, through a letter; letter will need to
                            # be determined by the history.
			                # firefang was wrongly challenged and so the opponent loses their turn

3m.CHTHoNIC.CCHIN?T.5.0     # chthonic was played with a blank O, through some letter.
                            # It gets an extra 5-pt bonus.
ex.ABC.ABCDEFG             # exchange ABC from a rack of ABCDEFG
ex.4                       # exchange 4 unknown tiles.
ex.ABC                     # exchange ABC from a rack of ABC (these are all the known
                           # letters)
pass                       # a pass (change of turn) without any play.
```


If playing THROUGH a letter or letters, you must use the actual letter being played through.
Don't use parentheses or a period.

Multi-character letters must be bracketed like such: [CH] for spanish, for example.

GUI to engine:
--------------

These are all the command the engine gets from the interface.

* ucgi

	tell engine to use the ucgi (universal crossword game interface),
	this will be sent once as a first command after program boot
	to tell the engine to switch to ucgi mode.
	After receiving the ucgi command the engine must identify itself with the "id" command
	and send the "option" commands to tell the GUI which engine settings the engine supports if any.
	After that the engine should send "ucgiok" to acknowledge the ucgi mode.
	If no ucgiok is sent within a certain time period, the engine task will be killed by the GUI.

* debug [ on | off ]

	switch the debug mode of the engine on and off.
	In debug mode the engine should send additional infos to the GUI, e.g. with the "info string" command,
	to help debugging, e.g. the commands that the engine has received etc.
	This mode should be switched off by default and this command can be sent
	any time, also when the engine is thinking.

* isready

	this is used to synchronize the engine with the GUI. When the GUI has sent a command or
	multiple commands that can take some time to complete,
	this command can be used to wait for the engine to be ready again or
	to ping the engine to find out if it is still alive.
	This command is also required once before the engine is asked to do any search
	to wait for the engine to finish initializing.
	This command must always be answered with "readyok" and can be sent also when the engine is calculating
	in which case the engine should also immediately answer with "readyok" without stopping the search.

* setoption name <id> [value <x>]

	this is sent to the engine when the user wants to change the internal parameters
	of the engine. For the "button" type no value is needed.
	One string will be sent for each parameter and this will only be sent when the engine is waiting.
	The name and value of the option in <id> should not be case sensitive and can include spaces.
	The substrings "value" and "name" should be avoided in <id> and <x> to allow unambiguous parsing,
	for example do not use <name> = "draw value".
	Here are some strings for the example below:
    ```
        "setoption name Selectivity value 3\n"
	    "setoption name Style value Risky\n"
	    "setoption name Clear Hash\n"
	    "setoption name DataPath value c:\cwgame\data"
    ```
* register

	this is the command to try to register an engine or to tell the engine that registration
	will be done later. This command should always be sent if the engine	has sent "registration error"
	at program startup.
	The following tokens are allowed:
	* later
	   the user doesn't want to register the engine now.
	* name <x>
	   the engine should be registered with the name <x>
	* code <y>
	   the engine should be registered with the code <y>
	Example:
    ```
	   "register later"
	   "register name Stefan MK code 4359874324"
    ```

* ucginewgame

   this is sent to the engine when the next search (started with "position" and "go") will be from
   a different game. This can be a new game the engine should play or a new game it should analyse but
   also the next position from a testsuite with positions only.
   If the GUI hasn't sent a "ucginewgame" before the first "position" command, the engine shouldn't
   expect any further ucginewgame commands as the GUI is probably not supporting the ucginewgame command.
   So the engine should not rely on this command even though all new GUIs should support it.
   As the engine's reaction to "ucginewgame" can take some time the GUI should always send "isready"
   after "ucginewgame" to wait for the engine to finish its operation.

* position [cgp <cgpstring>]  moves <move1> .... <movei>

	set up the position described in cgpstring on the internal board and
	play the moves on the internal crossword game board.

	See https://github.com/domino14/macondo/tree/master/cgp#readme for cgp format

	Note: no "new" command is needed. However, if this position is from a different game than
	the last position sent to the engine, the GUI should have sent a "ucginewgame" inbetween.

* go

	start calculating on the current position set up with the "position" command.
	There are a number of commands that can follow this command, all will be sent in the same string.
	If one command is not sent its value should be interpreted as it would not influence the search.
	* searchmoves {move1} .... {movei}
		restrict search to this moves only

		Example: After "position startpos" and "go infinite searchmoves h4.HADJI h6.HAJ ex.J"
		the engine should only search the three moves H4 HADJI, H6 HAJ, and exchange J.
		Note that the engine would already know the rack for this player, as it is specified in the
		Cgpstring.

    * alsosearchmoves {move1} ... {movei}

		Like searchmoves, but this searches moves in addition to the moves it would normally have searched. Can be used for sims where the player’s move was not in the top moves chosen by the engine.
	* 1time {x}

		player 1 has x msec left on the clock
	* 2time {x}

		player 2 has x msec left on the clock
	* 1inc {x}

		player 1 increment per move in mseconds if x > 0
	* 2inc {x}

		player 2 increment per move in mseconds if x > 0
	* depth {x}

		search x plies only.
	* firstwin

		return after finding a win, any win. Only usable in the endgame.
	* movetime {x}

		search exactly x mseconds
	* infinite

		search until the "stop" command. Do not exit the search without being told so in this mode!
	* stopcondition {x}

		Valid values are 95, 98, 99 (for percent sure). This is only used for montecarlo sims.
	* threads {x}

		Use this many threads. If not specified, should use as many threads as are available, but this isn’t a requirement.

* stop

	stop calculating as soon as possible,
	don't forget the "bestmove" when finishing the search

* quit

	quit the program as soon as possible


Engine to GUI:
--------------

* id
	* name <x>

		this must be sent after receiving the "ucgi" command to identify the engine,
		e.g. "id name Macondo X.Y\n"
	* author <x>

		this must be sent after receiving the "ucgi" command to identify the engine,
		e.g. "id author Aureliano Buendía\n"

* ucgiok

	Must be sent after the id and optional options to tell the GUI that the engine
	has sent all infos and is ready in ucgi mode.

* readyok

	This must be sent when the engine has received an "isready" command and has
	processed all input and is ready to accept new commands now.
	It is usually sent after a command that can take some time to be able to wait for the engine,
	but it can be used anytime, even when the engine is searching,
	and must always be answered with "isready".

* bestmove {move1}

	the engine has stopped searching and found the move {move1} best in this position.
	this command must always be sent if the engine stops searching, so for every "go" command a "bestmove" command is needed!
	Directly before that the engine should send a final "info" command with the final search information,
	so the GUI has the complete statistics about the last search.

* copyprotection

	this is needed for copyprotected engines. After the ucgiok command the engine can tell the GUI,
	that it will check the copy protection now. This is done by "copyprotection checking".
	If the check is ok the engine should send "copyprotection ok", otherwise "copyprotection error".
	If there is an error the engine should not function properly but should not quit alone.
	If the engine reports "copyprotection error" the GUI should not use this engine
	and display an error message instead!
	The code in the engine can look like this

    ```
      TellGUI("copyprotection checking\n");
	   // ... check the copy protection here ...
	   if(ok)
	      TellGUI("copyprotection ok\n");
      else
         TellGUI("copyprotection error\n");
    ```

* info

	the engine wants to send information to the GUI. This should be done whenever one of the info has changed.

	The engine can send only selected infos or multiple infos with one info command,
	e.g. "info currmove h4.HADJI.ADHIJRS currmovenumber 2" or
	     "info depth 12 nodes 123456 nps 100000".

	Also all infos belonging to the pv should be sent together
	e.g. "info depth 2 score wp 33.81 time 1242 nodes 2124 nps 34928 pv n3.VIG a2.FOO"
	I suggest to start sending "currmove", "currmovenumber", "currline" only after one second
	to avoid too much traffic.
	Additional info:

	* depth {x}

		search depth in plies
	* time {x}

		the time searched in ms, this should be sent together with the pv.
	* nodes {x}

		x nodes searched, the engine should send this info regularly
	* pv {move1} ... {movei}

		the best line found
	* score

		* wp {x}

			the score from the engine's point of view in win %.

		* eq {x}

			the score from the engine's point of view in equity.

		* lowerbound

	        the score is just a lower bound.

		* upperbound

		   	the score is just an upper bound.
	* currmove {move}

		currently searching this move

    * currmovenumber {x}

		currently searching move number x, for the first move x should be 1 not 0.

    * hashfull {x}

		the hash is x permill full, the engine should send this info regularly

	* nps {x}
		x nodes per second searched, the engine should send this info regularly

	* cpuload {x}

		the cpu usage of the engine is x permill.

	* string {str}
		any string str which will be displayed be the engine,
		if there is a string command the rest of the line will be interpreted as {str}

	* currline {cpunr} {move1} ... {movei}

	   this is the current line the engine is calculating. {cpunr} is the number of the cpu if
	   the engine is running on more than one cpu. {cpunr} = 1,2,3....
	   if the engine is just using one cpu, {cpunr} can be omitted.
	   If {cpunr} is greater than 1, always send all k lines in k strings together.
		The engine should only send this if the option "UCGI_ShowCurrLine" is set to true.

	* peg {move1} {w:AB|AC|DE} {d:BB} {l:AH}

        2-in-the-bag pre-endgame move wins with draws of AB, AC, and DE, ties with a draw of BB, loses with a draw of AH

* option

	This command tells the GUI which parameters can be changed in the engine.

	This should be sent once at engine startup after the "ucgi" and the "id" commands
	if any parameter can be changed in the engine.

	The GUI should parse this and build a dialog for the user to change the settings.

	Note that not every option needs to appear in this dialog as some options like
	"UCGI_AnalyseMode", etc. are better handled elsewhere or are set automatically.

	If the user wants to change some settings, the GUI will send a "setoption" command to the engine.

	Note that the GUI need not send the setoption command when starting the engine for every option if it doesn't want to change the default value.

	For all allowed combinations see the examples below,
	as some combinations of this tokens don't make sense.
	One string will be sent for each parameter.

    * name {id}

		The option has the name id.
		Certain options have a fixed value for {id} which means that the semantics of this option is fixed.
		Usually those options should not be displayed in the normal engine options window of the GUI but
		get a special treatment. "Pondering" for example should be set automatically when pondering is
		enabled or disabled in the GUI options. The same for "UCGI_AnalyseMode" which should also be set
		automatically by the GUI. All those certain options have the prefix "UCGI_" except for the
		first 6 options below. If the GUI gets an unknown Option with the prefix "UCGI_", it should just
		ignore it and not display it in the engine's options dialog.

		* {id}= EndgameHash, type is spin

			the value in MB for memory for endgame and pre-endgame hash tables can be changed,
			this should be answered with the first "setoptions" command at program boot
			if the engine has sent the appropriate "option name EndgameHash" command,
			which should be supported by all engines!
			So the engine should use a very small hash first as default.

		* {id} = DataPath, type string
			this is the path on the hard disk to the Data path. The data path should contain
			the gaddags, leave files, and other strategy files within subdirectories.
			Multiple directories can be concatenated with ";"

		* {id} = UCGI_ShowCurrLine, type check, should be false by default,
			the engine can show the current line it is calculating. see "info currline" above.

		* {id} = UCGI_LimitStrength, type check, should be false by default,
			The engine is able to limit its strength to a specific Elo number,
		   This should always be implemented together with "UCGI_Elo".

		* {id} = UCGI_Elo, type spin
			The engine can limit its strength in Elo within this interval.
			If UCGI_LimitStrength is set to false, this value should be ignored.
			If UCGI_LimitStrength is set to true, the engine should play with this specific strength.
		   This should always be implemented together with "UCGI_LimitStrength".

		* {id} = UCGI_AnalyseMode, type check
		   The engine wants to behave differently when analysing or playing a game.
		   For example when playing it can use some kind of learning.
		   This is set to false if the engine is playing a game, otherwise it is true.

		 * {id} = UCGI_Opponent, type string
		   With this command the GUI can send the name, title, elo and if the engine is playing a human
		   or computer to the engine.

		   The format of the string has to be [GM|IM|FM|WGM|WIM|none] [<elo>|none] [computer|human] <name>

		   Examples:
		   ```
           "setoption name UCGI_Opponent value GM 2300 human Nigel Richards"
		   "setoption name UCGI_Opponent value none none computer Macondo"
           ```

	* type {t}

		The option has type t.
		There are 5 different types of options the engine can send
		* check

			a checkbox that can either be true or false
		* spin

			a spin wheel that can be an integer in a certain range
		* combo

			a combo box that can have different predefined strings as a value
		* button

			a button that can be pressed to send a command to the engine
		* string

			a text field that has a string as a value,
			an empty string has the value "<empty>"

	* default {x}

		the default value of this parameter is x

	* min {x}

		the minimum value of this parameter is x

	* max {x}

		the maximum value of this parameter is x

	* var {x}

		a predefined value of this parameter is x
	Examples:
    Here are 5 strings for each of the 5 possible types of options

    ```
	   "option name Nullmove type check default true\n"
       "option name Selectivity type spin default 2 min 0 max 4\n"
	   "option name Style type combo default Normal var Solid var Normal var Risky\n"
	   "option name DataPath type string default c:\data\n"
	   "option name Clear Hash type button\n"
    ```


Examples:
---------

This is how the communication when the engine boots can look like:

```
GUI     engine

// tell the engine to switch to UCI mode
ucgi

// engine identify
    id name Macondo
	id author Cesar Del Solar

// engine sends the options it can change
// the engine can change the hash size from 16 to 8000 MB
	option name EndgameHash type spin default 16 min 16 max 8000
    option name DataPath type string default ./data

// the engine can set the playing style
  	option name Style type combo default Normal var Solid var Normal var Risky

// the engine has sent all parameters and is ready
	ucgiok

// Note: here the GUI can already send a "quit" command if it just wants to find out
//       details about the engine, so the engine should not initialize its internal
//       parameters before here.
// now the GUI sets some values in the engine
// set hash to 32 MB
setoption name EndgameHash value 32

// init tbs
setoption name DataPath value d:\tb;c\tb

// waiting for the engine to finish initializing
// this command and the answer is required here!
isready

// engine has finished setting up the internal values
	readyok

// now we are ready to go

// if the GUI is supporting it, tell the engine that is is
// searching on a game that it hasn't searched on before
ucginewgame

// if the engine supports the "UCGI_AnalyseMode" option and the next search is supposed to
// be an analysis, the GUI should set "UCGI_AnalyseMode" to true if it is currently
// set to false with this engine
setoption name UCGI_AnalyseMode value true

// tell the engine to search infinite from the start position after h4.HADJI, player on turn is holding AEIRSTX
position startpos moves h4.HADJI rack.AEIRSTX
go infinite

// the engine starts sending infos about the search to the GUI
// (only some examples are given)


info depth 3
info nps 26437
info score wp 73.8 eq 100 currmove 8a.SEXTARII currmovenumber 1
info score wp 70.1 eq 80 currmove 8b.SEXTARII currmovenumber 2
info nps 41562
....


// here the user has seen enough and asks to stop the searching
stop

// the engine has finished searching and is sending the bestmove command
// which is needed for every "go" command sent to tell the GUI
// that the engine is ready again
bestmove 8a.SEXTARII
```