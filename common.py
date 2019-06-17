#!/usr/bin/python
import os
import re
import json
import requests
from collections import namedtuple, OrderedDict
from bs4 import BeautifulSoup as bSoup

pos_regex = re.compile('([A-Z]{2,3})[0-9]{1,3}')

class encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, simpleClass):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)

def build_players(refresh=True):

    cache = os.path.isfile('reponse.cache')
    
    if refresh or not cache:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'}
        response = requests.get('http://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php', headers=headers)
        soup = bSoup(response.text)

        with open('response.cache','w') as f:
            f.write(str(response.text))

    else:
        soup = bSoup(''.join(open('response.cache').readlines()))


    base_div = soup.find('div', attrs={'id':'rankings-table-wrapper'})
    base_body = base_div.find('table').find('tbody')


    players_dct = OrderedDict()

    for row in base_body.findAll('tr'):
        try:
            cls = row.get('class')[0]
        except IndexError:
            continue

        if cls.count('tier-row'):
            tier = str(row.find('td').text.split(' ',1)[1])

        elif cls.startswith('mpb-player'):
            cells = row.findAll('td')

            pos_rank = str(cells[3].text)
            name = str(cells[2].find('a').find('span', attrs={'class':'full-name'}).text)
            key_name = name.lower().replace(' ','_')

            players_dct[key_name] = {
                'name': name,
                'pos_rank': pos_rank,
                'rank': str(cells[0].text),
                'pos': re.search(pos_regex, pos_rank).group(1),
            }

        #### REMOVE THIS ####
        if len(players_dct) > 20:
            break
        #####################

    return players_dct


def pick_to_team(num_teams, pick):
    rnd = (pick-1) / num_teams
    team_id = pick - (rnd * num_teams)
    if rnd % 2:
        team_id = (num_teams - team_id + 1) % num_teams
        if not team_id:
            team_id = num_teams
    return team_id


if __name__ == '__main__':
    players_dct = build_players(refresh=False)
    import json
    with open('pl.py','w') as f:
        f.write( 'players = %s\n' % json.dumps(players_dct, indent=2) )

