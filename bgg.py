import urllib2
import time
import lxml.objectify


def callBgg(url):
	time.sleep(5)
	response = urllib2.urlopen(url)
	xml = response.read()
	data = lxml.objectify.fromstring(xml)
	retry = 5
	while data.tag == 'message' and retry > 0:
		time.sleep(5)
		retry -= 1
		response = urllib2.urlopen(url)
		xml = response.read()
		data = lxml.objectify.fromstring(xml)	
	return data

class Bgg:
	SITE = "https://www.boardgamegeek.com/xmlapi2/"
	def __init__(self, base, params):
		self.url = self.SITE + base + "?" + '&'.join([str(x) + '=' + str(y) for (x, y) in params.items()])
		self.data = callBgg(self.url)
			
	def __getattr__(self, attr):
		return self.data[attr]

def evaluate(d, data, attr, process=int):
	if hasattr(data, attr):
		d[attr] = process(data[attr].get('value'))

class Game:
	def __init__(self, name, data):
		self.name = name
		self.data = {'name': name}
		for attr in ['minplayers', 'maxplayers', 'playingtime', 'maxplaytime', 'minplaytime']:
			evaluate(self.data, data, attr)
		if hasattr(data, 'poll'):
			for poll in data.poll:
				if poll.get('name') == 'suggested_numplayers':
					best_nplayers = 0
					best_nplayers_value = 0
					if hasattr(poll, 'results'):
						for result in poll.results:
							if hasattr(result, 'result'):
								for r_result in result.result:
									if r_result.get('value') == 'Best':
										count = int(r_result.get('numvotes') or 0)
										if count > best_nplayers_value:
											best_nplayers = result.get('numplayers')
											best_nplayers_value = count
						if best_nplayers != 0:
							self.data['best_nplayers'] = best_nplayers
				if poll.get('name') == 'suggested_playerage':
					best_age = 0
					best_age_value = 0
					if hasattr(poll, 'results') and hasattr(poll.results, 'result'):
						for result in poll.results.result:
							value = result.get('value')
							votes = int(result.get('numvotes') or 0)
							if votes > best_age_value:
								best_age = value
								best_age_value = votes
						if best_age != 0:
							self.data['best_age'] = best_age
		if hasattr(data, 'link'):
			for link in data.link:
				i_type = link.get('type')
				i_value = link.get('value')
				c = self.data.get(i_type, [])
				c.append(i_value)
				self.data[i_type] = c
			
o = Bgg('collection', {'username': 'matheusgr'})

games = []

for item in o.item:
	oid = dict(item.items())['objectid']
	name = item.name
	gamedata = Bgg('thing', {'id': oid})
	g = Game(name, gamedata.item)
	games.append(g.data)
	
import pickle
pickle.dump(games, open('games.dat','wb'))
