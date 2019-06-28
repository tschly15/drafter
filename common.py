#!/usr/bin/python
def pick_to_team(num_teams, pick):
    rnd = (pick-1) / num_teams
    team_id = pick - (rnd * num_teams)
    if rnd % 2:
        team_id = (num_teams - team_id + 1) % num_teams
        if not team_id:
            team_id = num_teams
    return team_id
