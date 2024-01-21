package main

import (
	"fmt"

	pb "github.com/woogles-io/open-protocols/gen/cgh"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/encoding/prototext"
)

func buildGame() *pb.CrosswordGameHistory {

	cgh := &pb.CrosswordGameHistory{
		Players: []*pb.PlayerInfo{
			{Nickname: "cesar", RealName: "César Del Solar"},
			{Nickname: "josh", RealName: "Joshua Sokol-Rubenstein"},
		},
		Lexicon:                      "NWL20",
		Description:                  "Game 8 of MERRY 2023, played on Dec 28, 2023 in Montclair, NJ",
		LetterDistribution:           "english",
		ChallengeRule:                pb.ChallengeRule_DOUBLE,
		NumberOfZeroptTurnsToEndGame: 6,
	}
	cgh.Events = append(cgh.Events, []*pb.CrosswordGameEvent{
		{
			Nickname:   "cesar",
			Rack:       "DIJNNR?",
			TotalScore: 30,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "8D",
					Play:        "DJINN",
					Score:       30,
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "HITWY",
			TotalScore: 33,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "I7",
					Play:        "WITHY",
					Score:       33,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "?CEEIRV",
			TotalScore: 110,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "J1",
					Play:        "sCRIEVE",
					Score:       80,
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "?CEEIRV",
			TotalScore: 164,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "1H",
					Play:        "MAsTERLy",
					Score:       131,
				},
			},
			Comment: `Josh said: "I never get to triple triple..." and laid this down. "I don't think I had a triple-triple if you'd made it an R ..."

A few seconds later, oh no, "you had VERJUICE!"`,
		},
		{
			Nickname:   "cesar",
			Rack:       "AEIMPZY",
			TotalScore: 177,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "H11",
					Play:        "MAZEY",
					Score:       67,
				},
			},
			Comment: `I spent around 10 minutes trying to calm down the murderous voices, then I laid this down (I did see MAIZE). I talked myself out of AZYME# but not MAZEY# apparently.`,
		},
		{
			Nickname:   "josh",
			Rack:       "",
			TotalScore: 164,
			Event: &pb.CrosswordGameEvent_ChallengeEvent{
				ChallengeEvent: &pb.ChallengeEvent{
					WordsChallenged: []string{"MAZEY"},
					PlayValid:       false,
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "AAEGL",
			TotalScore: 190,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "H11",
					Play:        "ALGAE",
					Score:       26,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "AEIMPYZ",
			TotalScore: 142,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "N1",
					Play:        "LAZY",
					Score:       32,
				},
			},
			Comment: `Obviously a big mistake, I can do something like PYAEMIA keeping the Z, etc, but my focus was long gone and I had too little time left now.`,
		},
		{
			Nickname:   "josh",
			Rack:       "EOO",
			TotalScore: 216,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "3L",
					Play:        "OOZE",
					Score:       26,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "DEIMOPR",
			TotalScore: 190,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "5E",
					Play:        "DEMIREP",
					Score:       48,
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "ACEKT",
			TotalScore: 254,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "E8",
					Play:        "JACKET",
					Score:       38,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "AAIIOOS",
			TotalScore: 190,
			Event: &pb.CrosswordGameEvent_ExchangeEvent{
				ExchangeEvent: &pb.ExchangeEvent{
					Exchanged: &pb.ExchangeEvent_ExchangedRack{
						ExchangedRack: "AIIOO",
					},
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "BERW",
			TotalScore: 287,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "6C",
					Play:        "BREW",
					Score:       33,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "AAISSST",
			TotalScore: 260,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "14H",
					Play:        "ASTASIAS",
					Score:       70,
				},
			},
			Comment: `I did my best to look dejected here, whilst staying within the rules, obviously.`,
		},
		{
			Nickname:   "josh",
			Rack:       "",
			TotalScore: 287,
			Event: &pb.CrosswordGameEvent_ChallengeEvent{
				ChallengeEvent: &pb.ChallengeEvent{
					WordsChallenged: []string{"ASTASIAS"},
					PlayValid:       true,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "AADEEFO",
			TotalScore: 292,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "D12",
					Play:        "DEAF",
					Score:       32,
				},
			},
		},
		{
			Nickname:   "josh",
			Rack:       "GORUU",
			TotalScore: 301,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "L9",
					Play:        "RUGOUS",
					Score:       14,
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "AEEFINO",
			TotalScore: 319,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "O11",
					Play:        "FEASE",
					Score:       27,
				},
			},
			Comment: `Too scared to leave that S open for another turn. IDK, I need to give myself better win chances.

FIE(F) looks a lot better.`,
		},
		{
			Nickname:   "josh",
			Rack:       "OOTUX",
			TotalScore: 349,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "15A",
					Play:        "OUTFOX",
					Score:       48,
				},
			},
			Comment: `ur_outfoxed`,
		},
		{
			Nickname:   "cesar",
			Rack:       "EGHIINO",
			TotalScore: 346,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "4F",
					Play:        "HOG",
					Score:       27,
				},
			},
			Comment: `I'm just trying to catch up. Quackondo likes OH keeping the ugly EGIIN. I don't know.`,
		},
		{
			Nickname:   "josh",
			Rack:       "",
			TotalScore: 349,
			Event: &pb.CrosswordGameEvent_ExchangeEvent{
				ExchangeEvent: &pb.ExchangeEvent{
					Exchanged: &pb.ExchangeEvent_NumExchanged{NumExchanged: 4},
				},
			},
		},
		{
			Nickname:   "cesar",
			Rack:       "EIIINOU",
			TotalScore: 359,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "G7",
					Play:        "INION",
					Score:       13,
				},
			},
			Comment: `Geez. I almost played UNION but wanted to undouble the I's plus I thought he might have thrown the Q in. I certainly have no real hopes of bingoing here, right - just wanted to get a big Q score in.`,
		},
		{
			Nickname:   "josh",
			Rack:       "DINQR",
			TotalScore: 397,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "N10",
					Play:        "QINDAR",
					Score:       48,
				},
			},
			Comment: `He kept the Q on the exchange!`,
		},
		{
			Nickname:   "cesar",
			Rack:       "EILNPUV",
			TotalScore: 441,
			Event: &pb.CrosswordGameEvent_TilePlayEvent{
				TilePlayEvent: &pb.TilePlayEvent{
					Coordinates: "2B",
					Play:        "VULPINE",
					Score:       82,
				},
			},
			Comment: `Miracle draw.`,
		},
		{
			Nickname:   "cesar",
			Rack:       "BLNOST",
			TotalScore: 457,
			Event: &pb.CrosswordGameEvent_GameEndEvent{
				GameEndEvent: &pb.GameEndEvent{
					EndgameRackBonus: 16,
				},
			},
		},
	}...)

	return cgh
}

func main() {
	history := buildGame()
	o := prototext.MarshalOptions{
		Multiline: true,
		Indent:    "  ",
	}
	t, err := o.Marshal(history)
	if err != nil {
		panic(err)
	}
	fmt.Println(string(t))

	// json
	json, err := protojson.Marshal(history)
	if err != nil {
		panic(err)
	}
	fmt.Println(string(json))
}
