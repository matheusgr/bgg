import pickle
from pprint import pprint


def match(group1, group2):
	return len(set(group1).intersection(set(group2)))


def best(games, selection):
	results = []
	for g in games:
		append = True
		append = append and g.get('minplayers', selection["n_players"]) <= selection["n_players"]
		append = append and g.get('maxplayers', selection["n_players"]) >= selection["n_players"]
		append = append and g.get('minplaytime', selection["playingtime"]) <= selection["playingtime"]
		append = append and g.get('maxplaytime', selection["playingtime"]) >= selection["playingtime"]
		if append:
			results.append((g,
								match(selection["mechanics"], g.get('boardgamemechanic', []) + g.get('boardgamecategory', [])),
								abs(selection["n_players"] - int(g.get('best_nplayers', 0))),
								abs(selection["playingtime"] - int(g.get('playingtime')))
							)
						  )
		
	return [(x[0].get('name').text, x[1], x[2], x[3]) for x in sorted(results, key=lambda x: -x[1] * 10000 + x[2] * 100 + x[3])]


def submenu(allopt, selection):
	select = "-"
	allopt_sorted = sorted(list(allopt))
	while select not in "B":
		pprint(selection["mechanics"])
		print " [R] - remove one"
		print " [A] - add one"
		print " [C] - clear"
		print " [B/Enter] - back"
		print
		select = raw_input("option? ").upper()
		if select == "R":
			pprint([x for x in enumerate(selection["mechanics"])])
			option = int(raw_input("option? ") or -1)
			if option != -1:
				selection["mechanics"].pop(option)
		elif select == "A":
			pprint([x for x in enumerate(allopt_sorted)])
			option = int(raw_input("option? ") or -1)
			if option != -1:
				choose = allopt_sorted[option]
				if choose not in selection["mechanics"]:
					selection["mechanics"].append(choose)
		elif select == "C":
			del selection["mechanics"][:]


def menu(games, mechanics, selection):
	select = "-"
	while select != "Q":
		print "[N] - n players [" + str(selection["n_players"]) + "]"
		print "[P] - playing time (+- 30 min) [" + str(selection["playingtime"]) + "]"
		print "[M] - mechanics/categories [" + str(selection["mechanics"]) + "]"
		print
		print "Games.... "
		pprint(best(games, selection)[:10])
		print "[Q] - quit"
		print

		select = raw_input("I? ").upper()
		if select == 'N':
			selection["n_players"] = int(raw_input("n_players? ") or 2)
		elif select == "P":
			selection["playingtime"] = int(raw_input("playingtime? ") or 30)
		elif select == "M":
			submenu(mechanics, selection)

games = pickle.load(open('games.dat'))

mechanics = set()

for category in ['boardgamemechanic', 'boardgamecategory']:
	for game in games:
		mechanics.update(set(game.get(category, [])))


selection = { "n_players": 2,
			  "playingtime": 30,
			  "mechanics": []
			  }

menu(games, mechanics, selection)
