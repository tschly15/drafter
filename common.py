#!/usr/bin/python
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


