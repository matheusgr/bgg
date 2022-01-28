import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AffinityPropagation


def compare_games(g1, g2, descr_sim):
	if g1 == g2:
		return 1
	get_bestnplayers = lambda g: float(str(g.get('best_nplayers', (g['minplayers'] + g['maxplayers']) / 2)).replace('+', ''))
	get_bestage = lambda g: max(6, min(18, int(str(g.get('best_age', '10')).replace('+', ''))))
	#set_diff = lambda b, o, c: len(set(b.get(c, [])).intersection(o.get(c, []))) / (len(set(b.get(c, [])).union(o.get(c, []))) if b.get(c, []) and o.get(c, []) else 1)
	set_diff = lambda b, o, c: len(set(b.get(c, [])).intersection(o.get(c, [])))
	vector = [
				2 * descr_sim,
				abs(get_bestnplayers(g1) - get_bestnplayers(g2)),
				1 * 1 / (1 + abs(g1['playingtime'] + g2['playingtime'])),
				4 * 1 / (1 + abs(get_bestage(g1) - get_bestage(g2))),
				4 * set_diff(g1, g2, 'boardgamemechanics'),
				4 * set_diff(g1, g2, 'boardgamecategory'),
				2 * set_diff(g1, g2, 'boardgamefamily')
	]
	return sum(vector)

def extract_documents(games):
	documents_names = []
	docs = []
	for g in games:
		if 'Expansion for Base-game' in g.get('boardgamecategory', 'Expansion for Base-game'):
			continue
		documents_names.append(g['name'])
		docs.append(g)
	return documents_names, docs

games = pickle.load(open('games.dat', 'rb'))

names, docs = extract_documents(games)

vectorizer = TfidfVectorizer()

tfidf = vectorizer.fit_transform([doc['description'] for doc in docs])
descr_sim_matrix = (tfidf * tfidf.T).A


sim_matrix = []

for g1 in range(len(names)):
	sim_matrix.append([])
	for g2 in range(len(names)):
		sim_matrix[-1].append(compare_games(docs[g1], docs[g2], descr_sim_matrix[g1][g2]))

clustering = AffinityPropagation(random_state=5).fit(sim_matrix)
labels = clustering.labels_

clusters = {}
n = 0
for item in labels:
	if item in clusters:
		clusters[item].append(names[n])
	else:
		clusters[item] = [names[n]]
	n +=1

for item in clusters:
    for i in clusters[item]:
        print(item, i)