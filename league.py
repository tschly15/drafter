#MAYBE TRY JSONPICKLE
import os
import re
import json
import requests
from collections import OrderedDict
try:
    from bs4 import BeautifulSoup as b4
except ImportError:
    from BeautifulSoup import BeautifulSoup as b4


class custom_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (league_cls,team_cls,player_cls)):
            return {'__{0}__'.format(obj.__class__.__name__): obj.__dict__}
        else:
            return json.JSONEncoder.default(self, obj)

class league_cls(object):

    url = 'http://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'}

    def __init__(self, session):

        self.num_teams = session.pop('num_teams')
        self.rounds = session.pop('num_rounds')

        self.keepers = []
        self.current_pick = 1

        #TODO: define the full path
        self.cache = 'response.cache'

        #list containing team objects
        self.teams = [ team_cls(str(idx))
                       for idx in range(1, int(self.num_teams)+1)]

        #ordered dict containing player objects
        self.players = OrderedDict()
        self.identify_players()

        self.positions = self.define_positions(session)
        print(self.positions)

    def to_json(self):
        key = '__{0}__'.format(self.__class__.__name__)
        val = json.dumps(self.__dict__, cls=custom_encoder)
        return '{"%s":%s}' % (key, val)

    @staticmethod
    def from_json(serialized):
        return json.loads(serialized, object_hook=deserialize)

    def define_positions(self, session):
        positions = []
        for fld in list(session.keys()):
            if fld.startswith('num_'):
                val = session.pop(fld)
                for idx in range(int(val)):
                    positions.append(fld[4:].upper())
        return positions

    def identify_players(self):
        soup = self.get_html(refresh=False)

        base_div = soup.find('div', attrs={'id':'rankings-table-wrapper'})
        base_body = base_div.find('table').find('tbody')

        for row in base_body.findAll('tr'):
            try:
                cls = row.get('class')[0]
            except IndexError:
                continue

            if cls.count('tier-row'):
                tier = str(row.find('td').text.split(' ',1)[1])

            elif cls.startswith('mpb-player'):
                cell = row.findAll('td')
                player_obj = player_cls(cell=cell, tier=tier)

                key_name = player_obj.player_name.lower().replace(' ','_')
                self.players[key_name] = player_obj

                if len(self.players) == 20:
                    return

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, cls=custom_encoder)

    def get_html(self, refresh=True):

        if refresh or not os.path.isfile(self.cache):
            response = requests.get(self.url, headers=self.headers)
            try:
                soup = b4(response.text, "lxml")
            except AttributeError:
                soup = b4(response.text)

            with open(self.cache,'w') as f:
                f.write(str(response.text))

        else: #this is merely to aid in testing
            try:
                soup = b4(''.join(open(self.cache).readlines()), "lxml")
            except AttributeError:
                soup = b4(''.join(open(self.cache).readlines()))

        return soup


class team_cls(object):
    def __init__(self, tid, name=""):
        self.team_id = tid
        self.team_name = name or "Team{0}".format(tid)


class player_cls(object):
    pos_regex = re.compile('([A-Z]{1,3})[0-9]{1,3}')

    def __init__(self, cell=None, tier=None, reinit=None):
        if reinit:
            self.__dict__.update(reinit)
        else:
            self.position_rank = str(cell[3].text)

            self.position = re.search(self.pos_regex, self.position_rank).group(1)
            self.player_name = str(cell[2].find('a').find('span', attrs={'class':'full-name'}).text)
            self.overall_rank = str(cell[0].text)

            self.tier = tier
            self.pick = None #update html to use this value as a toggle


def deserialize(o):
    #TODO: either a mixin or method with identical signature for each class
    if '__league_cls__' in o:
        dct = o['__league_cls__']
        lea = league_cls(dct['num_teams'])
        vars(lea).update(dct)
        return lea
    elif '__team_cls__' in o:
        dct = o['__team_cls__']
        return team_cls(dct['team_id'], dct['team_name'])
    elif '__player_cls__' in o:
        dct = o['__player_cls__']
        return player_cls(reinit=dct)

    return o
    #{u'__team_cls__': {u'team_id': 1, u'team_name': u'Team1'}}
    #{u'__player_cls__': {u'overall_rank': u'1', u'position': u'RB', u'position_rank': u'RB1', u'player_name': u'Saquon Barkley', u'tier': u'1'}}

#ll = league_cls(num_teams=12)
#serialized = ll.to_json()

#nl = league_cls.from_json(serialized)
#print nl