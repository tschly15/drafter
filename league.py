import os
import json
import requests
from collections import defaultdict
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

    def __init__(self, session=None, reinit=None):
        if reinit:
            self.__dict__.update(reinit)

        else:
            self.num_teams = session.pop('num_teams')
            self.rounds = session.pop('num_rounds')

            #a list of ranks (ie. pointers to player objs)
            self.keepers = []
            self.include_keepers = session.pop('include_keepers')

            #TODO: define the full path
            self.cache = 'response.cache'

            #list containing team objects
            self.teams = [ team_cls(tid=idx)
                           for idx in range(int(self.num_teams)) ]

            #dict containing rank as key and value of player object
            self.players = {}
            self.identify_players()

            #link to player objs in order they were drafted
            self.drafted = [] 
            self.positions = self.define_positions(session)

    def to_json(self):
        key = '__{0}__'.format(self.__class__.__name__)
        val = json.dumps(self.__dict__, cls=custom_encoder)
        return '{"%s":%s}' % (key, val)

    @staticmethod
    def from_json(serialized):
        return json.loads(serialized, object_hook=deserialize)

    def pick_to_team(self):
        current_pick = len(self.drafted)
        num_teams = int(self.num_teams)

        pos = current_pick % num_teams
        rnd = int((current_pick-1) / num_teams) + 1

        if rnd % 2:
            return pos-1 if pos else num_teams-1
        
        mod = pos % num_teams
        return num_teams - mod if mod else 0

    def pick_from_team(self, session):
        num_teams = int(self.num_teams)
        rnd = int(session['keeper_player_round'])
        team_id = int(session['keeper_team_id']) + 1

        pick_before_round = (rnd-1) * num_teams 
        if rnd % 2:
            return pick_before_round + team_id

        inv_team_id = (num_teams+1) - team_id
        return pick_before_round + inv_team_id

    def define_positions(self, session):
        positions = []
        for fld in list(session):
            if fld.startswith('num_'):
                val = session.pop(fld)
                for idx in range(int(val)):
                    positions.append((idx,fld[4:].upper()))
        return positions

    def identify_players(self):
        soup = self.get_html(refresh=False)

        base_div = soup.find('div', attrs={'id':'rankings-table-wrapper'})
        base_body = base_div.find('table').find('tbody')

        for row in base_body.findAll('tr'):
            cls = row.get('class')
            if not cls:
                continue
            elif not isinstance(cls, (list,tuple)):
                cls = cls.split()
            cls = cls[0]
                
            if cls.count('tier-row'):
                tier = str(row.find('td').text.split(' ',1)[1])

            elif cls.startswith('mpb-player'):
                cell = row.findAll('td')
                player_obj = player_cls(cell=cell, tier=tier)

                self.players[player_obj.overall_rank] = player_obj

            if len(self.players) > 15:
                break


    def __str__(self):
        return json.dumps(self.__dict__, indent=2, cls=custom_encoder)

    def get_html(self, refresh=True):

        if refresh or not (os.path.isfile(self.cache) and os.path.getsize(self.cache)):
            response = requests.get(self.url, headers=self.headers)
            try:
                soup = b4(response.text, "lxml")
            except AttributeError:
                soup = b4(response.text)

            with open(self.cache,'w') as f:
                f.write(response.text.encode('utf8'))

        else: #this is merely to aid in testing
            try:
                soup = b4(''.join(open(self.cache).readlines()), "lxml")
            except AttributeError:
                soup = b4(''.join(open(self.cache).readlines()))

        return soup

    def draft_player_with_rank(self, session, rank):
            self.drafted.append(rank)

            team_id = self.pick_to_team()
            team = self.teams[team_id]

            player_obj = self.players[rank] #obj of player_cls
            player_obj.pick = str(len(self.drafted))
            player_obj.team_id = team_id #handy for UNDO

            position = team.determine_position(session, player_obj)
            self.teams[team_id].team_players[position].append(rank)


class team_cls(object):
    def __init__(self, tid=None, name="", reinit=None):
        if reinit:
            self.__dict__.update(reinit)
        else:
            self.team_id = str(tid)
            self.team_name = name or "Team{0}".format(int(tid+1))
            self.team_players = defaultdict(list)

    def drop_player(self, rank):
        for lst in self.team_players.values():
            if lst.count(rank):
                lst.remove(rank)
                break

    def get_player(self, league, pos, idx):
        try:
            rank = self.team_players[pos][idx]
            return league.players[rank].player_name
        except (KeyError,IndexError):
            return '-'

    def determine_position(self, session, player_obj):
        #1. attempt to assign as player's given position
        #2. attempt to assign to a flex position
        #3. attempt to assign to the bench

        pos = player_obj.position
        applicable_positions = [ fld
                                 for fld in session
                                 if fld.count(pos)
                                    and int(session[fld][1]) > 0 ]

        #move to the front of the line
        key = 'settings_num_{0}'.format(pos)
        if key in applicable_positions:
            applicable_positions.remove(key)
            applicable_positions.insert(0, key)

        for position in applicable_positions:
            pos_key = position.rsplit('_',1)[1].upper()
            if len(self.team_players[pos_key]) < int(session[position][1]):
                return pos_key

        #TODO: remove placeholder, finish logic
        return 'BN'

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, cls=custom_encoder)


class player_cls(object):

    def __init__(self, cell=None, tier=None, reinit=None):
        if reinit:
            self.__dict__.update(reinit)
        else:
            self.position_rank = str(cell[3].text)
            
            inp = cell[1].find('input')
            self.position = inp.get('data-position')
            self.nfl_team = inp.get('data-team')

            self.overall_rank = int(cell[0].text)
            self.player_name = str(cell[2].find('a').find('span', attrs={'class':'full-name'}).text)

            self.tier = tier
            self.pick = None
            self.team_id = None

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, cls=custom_encoder)
            

def deserialize(o):
    #TODO: either a mixin or method with identical signature for each class
    if '__league_cls__' in o:
        dct = o['__league_cls__']
        for key in list(dct['players']):
            player_obj = dct['players'].pop(key)
            dct['players'][int(key)] = player_obj
        return league_cls(reinit=dct)
    elif '__team_cls__' in o:
        dct = o['__team_cls__']
        dct['team_players'] = defaultdict(list, dct.pop('team_players'))
        return team_cls(reinit=dct)
    elif '__player_cls__' in o:
        dct = o['__player_cls__']
        return player_cls(reinit=dct)

    return o
