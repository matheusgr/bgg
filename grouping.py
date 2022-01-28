import pickle
from pprint import pprint

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def extract_terms(g):
	gv = [
		# *[x for x in g['name'].text.split() if len(x) > 3],
		*[x for x in g['description'].split() if len(x) > 3],
			   "minp" + str(g['minplayers']),
			   "maxp" + str(g['maxplayers']),
			   "ptime" + str(g['playingtime']),
			   "bplay" + str(g.get('best_nplayers', g['minplayers'])),
			   "bage" + str(g.get('best_age', 10)),
			   *["bcategory" + x for x in g.get('boardgamecategory', [])],
			   *["bmechanic" + x for x in g.get('boardgamemechanic', [])],
			   #*["bfamily" + x for x in g.get('boardgamefamily', [])]
			]
	return gv

def extract_documents(games):
	documents_names = []
	docs = []
	for g in games:
		if 'Expansion for Base-game' in g.get('boardgamecategory', 'Expansion for Base-game'):
			continue
		documents_names.append(g['name'])
		docs.append(extract_terms(g))
	return documents_names, docs

games = pickle.load(open('games.dat', 'rb'))

names, docs = extract_documents(games)

vectorizer = TfidfVectorizer(
	#token_pattern="\@\@\@",
	#preprocessor=lambda x: x,
	analyzer="word")

tfidf = vectorizer.fit_transform(["@@@".join(doc) for doc in docs])
km = KMeans(n_clusters=50)
km.fit(tfidf)
labels = km.predict(tfidf)

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